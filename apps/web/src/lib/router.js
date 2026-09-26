const paths = new Set([
  "/",
  "/login",
  "/register",
  "/app",
  "/app/issues",
  "/app/listings",
  "/app/sources",
  "/app/alerts",
  "/app/settings",
]);
export function parseRoute(hash) {
  if (!hash.startsWith("#/")) return null;
  const [path, query = ""] = hash.slice(1).split("?");
  const product = /^\/app\/listings\/([^/]+)$/.exec(path);
  return {
    path,
    query: new URLSearchParams(query),
    productId: product?.[1] ?? null,
    known: paths.has(path) || Boolean(product),
    protected: path === "/app" || path.startsWith("/app/"),
  };
}
export function resolveRoute(hash, previous = parseRoute("#/")) {
  return (
    parseRoute(hash) ??
    previous ?? {
      path: "/",
      query: new URLSearchParams(),
      productId: null,
      known: true,
      protected: false,
    }
  );
}
export function navigate(path) {
  window.location.hash = "#" + path;
}
