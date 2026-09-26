import test from "node:test";
import assert from "node:assert/strict";
import { pollJob } from "./jobs.js";
import { issuesForTab, issueLink, loadWorkspace } from "./workspace-model.js";

test("polling stops after eight consecutive errors and reports loss of contact", async () => {
  let calls = 0;
  await assert.rejects(
    pollJob("j1", {
      read: async () => {
        calls++;
        throw new Error("offline");
      },
      wait: async () => {},
    }),
    (error) => error.code === "contact_lost",
  );
  assert.equal(calls, 8);
});
test("polling recovers after errors and stops on completion", async () => {
  let calls = 0;
  const states = [];
  const result = await pollJob("j1", {
    read: async () => {
      calls++;
      if (calls === 1) throw new Error("offline");
      return { id: "j1", status: calls === 2 ? "running" : "done" };
    },
    wait: async () => {},
    onUpdate: (job) => states.push(job.status),
  });
  assert.equal(result.status, "done");
  assert.deepEqual(states, ["running", "done"]);
  assert.equal(calls, 3);
});
test("polling does not retry a missing job or an expired session", async () => {
  for (const status of [401, 404]) {
    let calls = 0;
    await assert.rejects(
      pollJob("j1", {
        read: async () => {
          calls++;
          throw { status };
        },
        wait: async () => {},
      }),
    );
    assert.equal(calls, 1);
  }
});
test("aborted polling does not make another request", async () => {
  const controller = new AbortController();
  controller.abort();
  assert.equal(
    await pollJob("j1", {
      signal: controller.signal,
      read: async () => {
        throw new Error("must not call");
      },
    }),
    null,
  );
});
test("tabs preserve API order, bucket, support, and denominator", () => {
  const items = [
    {
      id: "f2",
      product_id: "p2",
      bucket: "monitoring",
      support: 7,
      denominator: 11,
    },
    { id: "f1", product_id: "p1", bucket: "to_do", support: 1, denominator: 8 },
    {
      id: "f3",
      product_id: "p3",
      bucket: "needs_fact",
      support: 3,
      denominator: 4,
    },
  ];
  assert.deepEqual(issuesForTab(items, "needs"), [items[1], items[2]]);
  assert.equal(issuesForTab(items, "all"), items);
  assert.equal(issueLink(items[2]), "#/app/listings/p3?f=f3");
});
test("workspace reads all four API resources and keeps errors visible", async () => {
  const original = globalThis.fetch;
  const paths = [];
  try {
    globalThis.fetch = async (url) => {
      paths.push(url);
      if (url.endsWith("/summary"))
        return new Response(JSON.stringify({ detail: { code: "not_found" } }), {
          status: 404,
        });
      return new Response(
        JSON.stringify(
          url.endsWith("/status") ? { engine: "rules", jobs: [] } : {},
        ),
      );
    };
    const result = await loadWorkspace();
    assert.equal(paths.length, 4);
    assert.equal(result.error.status, 404);
    assert.equal(result.summary, null);
    assert.equal(result.status.engine, "rules");
  } finally {
    globalThis.fetch = original;
  }
});
