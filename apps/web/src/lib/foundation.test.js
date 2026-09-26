import test from "node:test";
import assert from "node:assert/strict";
import { messages, translate, localizeError, plural } from "./messages.js";
import { parseRoute, resolveRoute } from "./router.js";
import { readPreference, writePreference } from "./storage.js";
import { ApiError, request } from "../api/http.js";

test("all namespaces have matching EN/ID keys and interpolation values", () => {
  for (const namespace of Object.keys(messages.en)) {
    assert.deepEqual(
      Object.keys(messages.en[namespace]).sort(),
      Object.keys(messages.id[namespace]).sort(),
    );
    for (const key of Object.keys(messages.en[namespace])) {
      assert.deepEqual(
        messages.en[namespace][key].match(/\{\w+\}/g),
        messages.id[namespace][key].match(/\{\w+\}/g),
      );
    }
  }
  assert.equal(plural("en", 1), "1 review");
  assert.equal(plural("en", 2), "2 reviews");
  assert.equal(translate("id", "common.pluralOther", { count: 3 }), "3 ulasan");
  assert.equal(localizeError("unknown", "en"), messages.en.common.unknownError);
});
test("landing anchors preserve route and query identifies a finding", () => {
  const initial = parseRoute("#/app/issues?tab=needs_you&f=f_123");
  assert.equal(initial.query.get("f"), "f_123");
  assert.equal(initial.protected, true);
  assert.equal(resolveRoute("#how", initial), initial);
  assert.equal(resolveRoute("#gate").path, "/");
  assert.equal(parseRoute("#/app/listings/p_123?f=f_1").productId, "p_123");
  assert.equal(parseRoute("#/analisis").known, false);
  assert.equal(parseRoute("#/app/settings").known, true);
});
test("storage refusal keeps preferences usable", () => {
  const storage = {
    getItem() {
      throw new Error("denied");
    },
  };
  assert.equal(readPreference("language", "en", storage), "en");
  const original = Object.getOwnPropertyDescriptor(globalThis, "localStorage");
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    get() {
      throw new Error("denied");
    },
  });
  try {
    assert.equal(readPreference("theme", "light"), "light");
    assert.doesNotThrow(() => writePreference("theme", "dark"));
  } finally {
    if (original) Object.defineProperty(globalThis, "localStorage", original);
    else delete globalThis.localStorage;
  }
});
test("API uses cookies, preserves error codes, and handles empty and invalid responses", async () => {
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async (url, options) => {
      assert.equal(url, "/api/v1/auth/login");
      assert.equal(options.credentials, "include");
      assert.equal(JSON.parse(options.body).email, "a@example.test");
      return new Response(
        JSON.stringify({ detail: { code: "bad_credentials", message: "No" } }),
        { status: 401 },
      );
    };
    await assert.rejects(
      request("/auth/login", {
        method: "POST",
        body: { email: "a@example.test" },
      }),
      (e) =>
        e instanceof ApiError &&
        e.code === "bad_credentials" &&
        e.status === 401,
    );
    globalThis.fetch = async () => new Response(null, { status: 204 });
    assert.equal(await request("/auth/logout", { method: "POST" }), null);
    globalThis.fetch = async () =>
      new Response("<html>error</html>", { status: 502 });
    await assert.rejects(
      request("/auth/me"),
      (e) => e.code === "invalid_response",
    );
    globalThis.fetch = async () => {
      throw new TypeError("network");
    };
    await assert.rejects(
      request("/auth/me"),
      (e) => e.code === "network_error",
    );
  } finally {
    globalThis.fetch = original;
  }
});
