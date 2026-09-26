import { ApiError, request } from "../api/http.js";
export const activeJob = (job) =>
  job?.status === "running" || job?.status === "queued";
/** @param {string} id @param {{signal?:AbortSignal,onUpdate?:(job:any)=>void,read?:typeof request,wait?:(ms:number,signal?:AbortSignal)=>Promise<void>,maxErrors?:number}} options */
export async function pollJob(
  id,
  {
    signal,
    onUpdate = () => {},
    read = request,
    wait = delay,
    maxErrors = 8,
  } = {},
) {
  let failures = 0;
  while (!signal?.aborted) {
    let job;
    try {
      job = await read("/deciqo/jobs/" + encodeURIComponent(id), { signal });
      failures = 0;
    } catch (error) {
      if (signal?.aborted) return null;
      if (error.status === 401 || error.status === 404) throw error;
      if (++failures >= maxErrors) throw new ApiError("contact_lost", "");
      await wait(1500, signal);
      continue;
    }
    onUpdate(job);
    if (!activeJob(job)) return job;
    await wait(1500, signal);
  }
  return null;
}
function delay(ms, signal) {
  return new Promise((resolve) => {
    if (signal?.aborted) {
      resolve();
      return;
    }
    const finish = () => {
      clearTimeout(timer);
      signal?.removeEventListener("abort", finish);
      resolve();
    };
    const timer = setTimeout(finish, ms);
    signal?.addEventListener("abort", finish, { once: true });
  });
}
