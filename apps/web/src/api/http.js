export class ApiError extends Error {
  constructor(code, message, status = 0) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}
/** @param {string} path @param {{method?:string,body?:unknown,signal?:AbortSignal}} options */
export async function request(path, { method = "GET", body, signal } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);
  const abort = () => controller.abort();
  if (signal?.aborted) controller.abort();
  else signal?.addEventListener("abort", abort, { once: true });
  try {
    const response = await fetch("/api/v1" + path, {
      method,
      credentials: "include",
      signal: controller.signal,
      headers:
        body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (response.status === 204) return null;
    let data;
    try {
      data = await response.json();
    } catch {
      throw new ApiError("invalid_response", "", response.status);
    }
    if (!response.ok)
      throw new ApiError(
        data?.detail?.code ??
          (response.status === 401 ? "unauthorized" : "request_failed"),
        data?.detail?.message ?? "",
        response.status,
      );
    return data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      controller.signal.aborted ? "timeout" : "network_error",
      "",
    );
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", abort);
  }
}
