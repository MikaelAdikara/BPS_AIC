import { useEffect, useState } from "react";
import { request, ApiError } from "@/api/http.js";
import { useWorkspace } from "@/api/workspace";
import {
  ArrowRight,
  Bell,
  CircleAlert,
  CircleCheck,
  CircleX,
  Clock3,
  Newspaper,
  Plug,
  RefreshCw,
  RotateCcw,
  Send,
  type LucideIcon,
} from "lucide-react";
import { useI18n } from "@/lib/i18n";
import {
  Button,
  Card,
  Chip,
  EmptyState,
  LoadingState,
  Notice,
  type Tone,
} from "@/components/ui";
export interface AlertEvent {
  id: number;
  kind: string;
  status: string;
  finding_id: string | null;
  synthetic: boolean;
  message: string;
  attempts: number;
  created_at: string;
  payload: { product?: string; attribute_local?: string };
}
interface AlertsView {
  events: AlertEvent[];
  telegram: { linked: boolean; bot_configured: boolean; demo_sink: boolean };
  rules: {
    new_issue: Record<string, number>;
    reopened: Record<string, number>;
    source_problem: Record<string, number>;
    delivery: Record<string, number>;
  };
}
const kinds = [
  "new_issue",
  "reopened",
  "source_problem",
  "job_done",
  "job_failed",
  "digest",
];
const statuses: Record<string, Tone> = {
  sent: "good",
  simulated: "info",
  unconfigured: "warn",
  pending: "muted",
  permanent_failure: "alert",
  digested: "muted",
};
const kindIcons: Record<string, LucideIcon> = {
  new_issue: CircleAlert,
  reopened: RotateCcw,
  source_problem: Plug,
  job_done: CircleCheck,
  job_failed: CircleX,
  digest: Newspaper,
};
const kindTones: Record<string, Tone> = {
  new_issue: "info",
  reopened: "alert",
  source_problem: "warn",
  job_done: "good",
  job_failed: "alert",
  digest: "muted",
};
/** Ringkasan satu-dua baris: tanpa awalan demo (sudah ada chip sintetis) dan tanpa baris tautan. */
function summarize(message: string) {
  return message
    .replace(/^\[DEMO[^\]]*\]\s*/, "")
    .split("\n")
    .filter((line) => line.trim() && !line.includes("://"))
    .join(" ");
}
const failures = new Set(["permanent_failure"]);
/** Linimasa alert: tiap event satu kartu yang menempel ke garis, ikon tepat di atas garis. */
export function AlertRows({ events }: { events: AlertEvent[] }) {
  const { t, language } = useI18n();
  return (
    <ol className="alert-tl">
      {events.map((event, index) => {
        const Icon = kindIcons[event.kind] ?? Bell;
        const tone = kindTones[event.kind] ?? "muted";
        const created = new Date(event.created_at);
        const newDay =
          index === 0 ||
          new Date(events[index - 1].created_at).toDateString() !== created.toDateString();
        const summary = summarize(event.message);
        const showAttempts = event.attempts > 1 || failures.has(event.status);
        return (
          <li key={event.id} className="alert-tl__item">
            {newDay && (
              <h3 className="alert-tl__date">
                <time dateTime={event.created_at}>
                  {created.toLocaleDateString(language, {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                  })}
                </time>
              </h3>
            )}
            <article className="alert-tl__event">
              <span className={"alert-tl__icon tone-" + tone} aria-hidden>
                <Icon size={16} />
              </span>
              <div className="alert-tl__card">
                <div className="alert-tl__head">
                  <div className="alert-tl__chips">
                    <Chip tone={tone}>
                      {t("alerts." + (kinds.includes(event.kind) ? event.kind : "unknown"))}
                    </Chip>
                    <Chip tone={statuses[event.status] ?? "muted"}>
                      <i className="status-dot" aria-hidden />
                      {t("alerts." + (event.status in statuses ? event.status : "unknown"))}
                    </Chip>
                    {event.synthetic && <Chip synthetic />}
                  </div>
                  <time
                    className="alert-tl__time count"
                    dateTime={event.created_at}
                    title={created.toLocaleString(language)}
                  >
                    {created.toLocaleTimeString(language, { hour: "2-digit", minute: "2-digit" })}
                  </time>
                </div>
                <p className="alert-tl__summary">{summary || event.message}</p>
                {showAttempts && (
                  <p className={"alert-tl__attempts" + (failures.has(event.status) ? " is-failed" : "")}>
                    {t("alerts.attempts", { count: event.attempts })}
                  </p>
                )}
                <div className="alert-tl__foot">
                  <details className="alert-tl__more">
                    <summary>{t("alerts.message")}</summary>
                    <p className="alert-tl__full">{event.message}</p>
                  </details>
                  {event.finding_id && (
                    <a
                      className="card-link alert-tl__open"
                      href={"#/app/issues?f=" + encodeURIComponent(event.finding_id)}
                    >
                      {t("alerts.open")}
                      <ArrowRight size={14} aria-hidden />
                    </a>
                  )}
                </div>
              </div>
            </article>
          </li>
        );
      })}
    </ol>
  );
}
export function AlertsScreen() {
  const { t, language, localizeError } = useI18n();
  const { summary } = useWorkspace();
  const [data, setData] = useState<AlertsView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const [kind, setKind] = useState("all");
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    request("/deciqo/alerts?lang=" + language, { signal: controller.signal })
      .then((result) => {
        if (!controller.signal.aborted) setData(result);
      })
      .catch((e: ApiError) => {
        if (!controller.signal.aborted) setError(e.code);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [revision, language, summary]);
  const events =
    data?.events.filter((event) => kind === "all" || event.kind === kind) ?? [];
  return (
    <>
      <header className="page-header">
        <div>
          <h1>{t("alerts.title")}</h1>
          <p className="muted">{t("alerts.lead")}</p>
        </div>
        <Button
          variant="outline"
          disabled={loading}
          onClick={() => setRevision((value) => value + 1)}
        >
          <RefreshCw size={16} aria-hidden className={loading ? "spinner" : undefined} />
          {t("alerts.refresh")}
        </Button>
      </header>
      {loading ? (
        <LoadingState />
      ) : error ? (
        <Notice
          tone="alert"
          action={
            <Button onClick={() => setRevision((value) => value + 1)}>
              {t("common.retry")}
            </Button>
          }
        >
          {localizeError(error)}
        </Notice>
      ) : (
        data && (
          <div className="stack">
            <Notice tone={data.telegram.linked ? "good" : "muted"}>
              <div>
                <p>
                  {t(
                    "alerts." + (data.telegram.linked ? "linked" : "unlinked"),
                  )}
                </p>
                <a href="#/app/settings">{t("alerts.manage")}</a>
              </div>
            </Notice>
            <Card title={t("alerts.rules")} icon={<Bell size={18} aria-hidden />}>
              <ul className="rule-tiles">
                {(
                  [
                    [CircleAlert, "info", t("alerts.newRule", data.rules.new_issue)],
                    [RotateCcw, "alert", t("alerts.reopenRule", data.rules.reopened)],
                    [Plug, "warn", t("alerts.sourceRule", data.rules.source_problem)],
                    [Send, "good", t("alerts.deliveryRule", data.rules.delivery)],
                  ] as const
                ).map(([Icon, tone, text]) => (
                  <li key={text}>
                    <span className={"rule-tiles__icon tone-" + tone} aria-hidden>
                      <Icon size={16} />
                    </span>
                    {text}
                  </li>
                ))}
              </ul>
            </Card>
            <div className="segmented alert-kinds" role="group" aria-label={t("alerts.all")}>
              {["all", ...kinds].map((value) => {
                const count =
                  value === "all"
                    ? data.events.length
                    : data.events.filter((event) => event.kind === value).length;
                if (value !== "all" && count === 0) return null;
                return (
                  <button
                    key={value}
                    type="button"
                    aria-pressed={kind === value}
                    onClick={() => setKind(value)}
                  >
                    {t("alerts." + value)}
                    <span className="tab-count">{count}</span>
                  </button>
                );
              })}
            </div>
            <Card title={t("alerts.history")} icon={<Clock3 size={18} aria-hidden />}>
              {events.length ? (
                <AlertRows events={events} />
              ) : (
                <EmptyState
                  title={t("alerts.empty")}
                  description={t("alerts.emptyHint")}
                />
              )}
            </Card>
          </div>
        )
      )}
    </>
  );
}
