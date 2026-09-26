import { useEffect, useId, useState } from "react";
import { request, ApiError } from "@/api/http.js";
import { useWorkspace } from "@/api/workspace";
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
export function AlertRows({ events }: { events: AlertEvent[] }) {
  const { t, language } = useI18n();
  return (
    <ol className="alert-list">
      {events.map((event) => (
        <li key={event.id}>
          <div className="finding-picker">
            <Chip>
              {t(
                "alerts." +
                  (kinds.includes(event.kind) ? event.kind : "unknown"),
              )}
            </Chip>
            <Chip tone={statuses[event.status] ?? "muted"}>
              {t(
                "alerts." +
                  (event.status in statuses ? event.status : "unknown"),
              )}
            </Chip>
            {event.synthetic && <Chip synthetic />}
          </div>
          <p>
            <strong>
              {event.payload.product ?? event.payload.attribute_local ?? ""}
            </strong>
          </p>
          <p className="muted">
            <time dateTime={event.created_at}>
              {new Date(event.created_at).toLocaleString(language)}
            </time>{" "}
            · {t("alerts.attempts", { count: event.attempts })}
          </p>
          <details>
            <summary>{t("alerts.message")}</summary>
            <p className="draft-text">{event.message}</p>
          </details>
          {event.finding_id && (
            <a href={"#/app/issues?f=" + encodeURIComponent(event.finding_id)}>
              {t("alerts.open")}
            </a>
          )}
        </li>
      ))}
    </ol>
  );
}
export function AlertsScreen() {
  const { t, language, localizeError } = useI18n();
  const { summary } = useWorkspace();
  const id = useId();
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
            <Card title={t("alerts.rules")}>
              <ul className="rules-list">
                <li>{t("alerts.newRule", data.rules.new_issue)}</li>
                <li>{t("alerts.reopenRule", data.rules.reopened)}</li>
                <li>{t("alerts.sourceRule", data.rules.source_problem)}</li>
                <li>{t("alerts.deliveryRule", data.rules.delivery)}</li>
              </ul>
            </Card>
            <div className="field">
              <label className="visually-hidden" htmlFor={id}>
                {t("alerts.all")}
              </label>
              <select
                id={id}
                value={kind}
                onChange={(event) => setKind(event.target.value)}
              >
                <option value="all">{t("alerts.all")}</option>
                {kinds.map((value) => (
                  <option key={value} value={value}>
                    {t("alerts." + value)}
                  </option>
                ))}
              </select>
            </div>
            <Card>
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
