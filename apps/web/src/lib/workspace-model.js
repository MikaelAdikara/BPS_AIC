import { request } from "../api/http.js";
export async function loadWorkspace(signal) {
  const paths = [
    "/deciqo/channels",
    "/deciqo/summary",
    "/deciqo/inbox",
    "/deciqo/status",
  ];
  const results = await Promise.allSettled(
    paths.map((path) => request(path, { signal })),
  );
  const value = (index) =>
    results[index].status === "fulfilled" ? results[index].value : null;
  return {
    channels: value(0)?.channels ?? [],
    summary: value(1),
    inbox: value(2)?.items ?? [],
    status: value(3),
    error:
      results.find((result) => result.status === "rejected")?.reason ?? null,
  };
}
export function issueLink(item) {
  return (
    "#/app/listings/" +
    encodeURIComponent(item.product_id) +
    "?f=" +
    encodeURIComponent(item.id)
  );
}
export function issuesForTab(items, tab) {
  const buckets = {
    needs: ["recurrence", "needs_fact", "to_do"],
    monitoring: ["monitoring"],
    dismissed: ["dismissed"],
    not_detected: ["not_detected"],
  };
  if (tab === "all") return items;
  return items.filter((item) => (buckets[tab] ?? [tab]).includes(item.bucket));
}
