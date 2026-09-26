import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useAuth } from "./auth";
import { ApiError } from "./http.js";
import { useI18n } from "@/lib/i18n";
import { activeJob, pollJob } from "@/lib/jobs.js";
import { loadWorkspace } from "@/lib/workspace-model.js";
export interface Issue {
  id: string;
  product_id: string;
  product_title: string;
  channel: string;
  synthetic: boolean;
  attribute: string;
  attribute_local: string;
  finding_type: string;
  bucket: string;
  next: string | null;
  support: number;
  denominator: number;
  candidates_read: number;
  support_is_minimum: boolean;
  example: string;
  engine: string;
  updated_at: string;
  needs_listing: boolean;
}
export interface Channel {
  key: string;
  label: string;
  status: string;
  synthetic: boolean;
  last_success_at: string | null;
  last_error: string | null;
  products: number;
  reviews: number;
}
export interface Job {
  id: string;
  kind: string;
  status: string;
  detail: { index?: number; total?: number; stage?: string };
  error?: { code?: string } | null;
}
interface Summary {
  products: number;
  reviews: number;
  findings_open: number;
  buckets: Record<string, number>;
  top: Issue[];
  engine: string;
}
interface Status {
  engine: string;
  jobs: Job[];
  engine_ready: boolean;
  llm: { configured: boolean; key_rejected: boolean; budget_usd: number; spent_usd: number; model: string };
  fetch: { configured: boolean; budget_usd: number; spent_usd: number; max_urls: number; max_charge_per_run_usd: number; reviews_per_product: number };
  estimate: { products: number; changed: number; analyse_all_usd: number };
}
interface Data {
  channels: Channel[];
  summary: Summary | null;
  inbox: Issue[];
  status: Status | null;
}
interface ContextValue extends Data {
  loading: boolean;
  error: string | null;
  busy: boolean;
  job: Job | null;
  toast: string | null;
  refresh: () => Promise<unknown>;
  run: (
    task: () => Promise<unknown>,
    successKey?: string,
    jobLabel?: string,
  ) => Promise<void>;
  closeJob: () => void;
  closeToast: () => void;
  jobLabel: string;
}
const Context = createContext<ContextValue | null>(null);
export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { user, refresh: refreshAuth } = useAuth();
  const { t } = useI18n();
  const [data, setData] = useState<Data>({
    channels: [],
    summary: null,
    inbox: [],
    status: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [job, setJob] = useState<Job | null>(null);
  const [toastKey, setToastKey] = useState<string | null>(null);
  const [jobLabel, setJobLabel] = useState("workspace.jobRunning");
  const mounted = useRef(false);
  const controller = useRef<AbortController | null>(null);
  const active = useRef(false);
  const revision = useRef(0);
  const refresh = useCallback(async () => {
    const current = ++revision.current;
    setLoading(true);
    setError(null);
    const result = await loadWorkspace(controller.current?.signal);
    if (!mounted.current || current !== revision.current) return;
    setData(result);
    if (result.error) {
      setError(
        result.error.status === 404
          ? "read_model_unavailable"
          : (result.error.code ?? "request_failed"),
      );
      if (result.error.status === 401) void refreshAuth();
    }
    setLoading(false);
    return result;
  }, [refreshAuth]);
  const follow = useCallback(
    async (initial: Job) => {
      controller.current?.abort();
      const aborter = new AbortController();
      controller.current = aborter;
      setJob(initial);
      let completed;
      try {
        completed = await pollJob(initial.id, {
          signal: aborter.signal,
          onUpdate: (next: Job) => {
            if (mounted.current) setJob(next);
          },
        });
      } catch (error) {
        if (mounted.current)
          setJob((previous) =>
            previous ? { ...previous, status: "contact_lost" } : previous,
          );
        throw error;
      }
      if (!completed) return;
      if (completed.status === "failed")
        throw new ApiError(completed.error?.code ?? "job_failed", "");
      if (completed.status === "interrupted")
        throw new ApiError("job_interrupted", "");
      await refresh();
    },
    [refresh],
  );
  useEffect(() => {
    mounted.current = true;
    controller.current = new AbortController();
    void refresh().then(async (state) => {
      const initial = state?.status?.jobs?.find(activeJob);
      if (initial && mounted.current) {
        active.current = true;
        setBusy(true);
        try {
          await follow(initial);
        } catch (e) {
          if (mounted.current)
            setError((e as ApiError).code ?? "request_failed");
        } finally {
          active.current = false;
          if (mounted.current) setBusy(false);
        }
      }
    });
    return () => {
      mounted.current = false;
      revision.current++;
      controller.current?.abort();
    };
  }, [user?.id, refresh, follow]);
  const run = useCallback(
    async (
      task: () => Promise<unknown>,
      successKey = "workspace.saved",
      label = "workspace.jobRunning",
    ) => {
      if (active.current) return;
      active.current = true;
      setBusy(true);
      setError(null);
      setJobLabel(label);
      try {
        const result = (await task()) as { job_id?: string } | null;
        if (!mounted.current) return;
        if (result?.job_id)
          await follow({
            id: result.job_id,
            kind: label,
            status: "queued",
            detail: {},
          });
        else await refresh();
        if (mounted.current) setToastKey(successKey);
      } catch (e) {
        if (mounted.current) {
          setError((e as ApiError).code ?? "request_failed");
          if ((e as ApiError).status === 401) void refreshAuth();
        }
      } finally {
        active.current = false;
        if (mounted.current) setBusy(false);
      }
    },
    [follow, refresh, refreshAuth],
  );
  return (
    <Context.Provider
      value={{
        ...data,
        loading,
        error,
        busy,
        job,
        jobLabel,
        toast: toastKey ? t(toastKey) : null,
        refresh,
        run,
        closeJob: () => setJob(null),
        closeToast: useCallback(() => setToastKey(null), []),
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useWorkspace() {
  const value = useContext(Context);
  if (!value) throw new Error("WorkspaceProvider required");
  return value;
}
