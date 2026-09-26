import { useAuth } from "@/api/auth";
import { useWorkspace } from "@/api/workspace";
import { request } from "@/api/http.js";
import { useI18n } from "@/lib/i18n";
import { issueLink } from "@/lib/workspace-model.js";
import {
  Button,
  Card,
  Chip,
  EmptyState,
  Metric,
  Notice,
  type Tone,
} from "@/components/ui";
import { IssuesTable, StateGate, buckets } from "@/components/workspace";
const overviewBuckets = [
  { bucket: "recurrence", hint: "hintRecurrence", tab: "recurrence" },
  { bucket: "needs_fact", hint: "hintNeedsFact", tab: "needs_fact" },
  { bucket: "to_do", hint: "hintTodo", tab: "to_do" },
  { bucket: "monitoring", hint: "hintMonitoring", tab: "monitoring" },
];
const sourceStates: Record<string, { key: string; tone: Tone }> = {
  connected: { key: "sourceConnected", tone: "good" },
  no_data: { key: "sourceNoData", tone: "muted" },
  stale: { key: "sourceStale", tone: "warn" },
  unavailable: { key: "sourceUnavailable", tone: "warn" },
  disconnected: { key: "sourceDisconnected", tone: "muted" },
  not_checked: { key: "sourceNotChecked", tone: "muted" },
};
export function OverviewScreen() {
  const { user } = useAuth();
  const { t, language } = useI18n();
  const { summary, inbox, channels, status, run, busy } = useWorkspace();
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
  return (
    <>
      <header className="page-header">
        <div>
          <h1>{t("workspace." + greeting, { name: user?.name ?? "" })}</h1>
          {summary && (
            <p className="muted">
              {t("workspace.counts", {
                products: summary.products,
                reviews: summary.reviews,
              })}
            </p>
          )}
          {channels.some((channel) => channel.synthetic) && (
            <Chip>{t("workspace.includesSynthetic")}</Chip>
          )}
        </div>
        <div className="utility-bar">
          <a className="btn btn--outline" href="#/app/sources">
            {t("workspace.addChannel")}
          </a>
          {summary?.top?.[0] && (
            <a className="btn btn--primary" href={issueLink(summary.top[0])}>
              {t("workspace.openNext")}
            </a>
          )}
        </div>
      </header>
      <StateGate>
        {summary?.products === 0 ? (
          <Card>
            <EmptyState
              title={t("workspace.startTitle")}
              description={t("workspace.startHint")}
              action={
                <div className="stack">
                  <Button
                    busy={busy}
                    onClick={() =>
                      void run(
                        () =>
                          request("/deciqo/workspace/reset", {
                            method: "POST",
                          }),
                        "workspace.demoLoaded",
                        "workspace.jobSeeding",
                      )
                    }
                  >
                    {t("workspace.loadDemo")}
                  </Button>
                  <a className="btn btn--outline" href="#/app/sources">
                    {t("workspace.connect")}
                  </a>
                </div>
              }
            />
          </Card>
        ) : (
          <>
            {status?.engine === "rules" && (
              <Notice tone="muted">{t("workspace.rulesHint")}</Notice>
            )}
            <div className="bucket-grid">
              {overviewBuckets
                .filter(
                  ({ bucket }) =>
                    summary?.buckets[bucket] !== undefined &&
                    summary.buckets[bucket] > 0,
                )
                .map(({ bucket, hint, tab }) => (
                  <a
                    className={"bucket-card tone-" + buckets[bucket].tone}
                    key={bucket}
                    href={"#/app/issues?tab=" + tab}
                  >
                    <Metric
                      value={summary?.buckets[bucket]}
                      label={t("workspace." + buckets[bucket].key)}
                      hint={t("workspace." + hint)}
                    />
                  </a>
                ))}
            </div>
            <Card
              title={t("workspace.whatFirst")}
              action={<a href="#/app/issues">{t("workspace.viewAll")}</a>}
            >
              <IssuesTable items={inbox.slice(0, 6)} />
            </Card>
            <Card
              title={t("workspace.channels")}
              action={<a href="#/app/sources">{t("workspace.manage")}</a>}
            >
              {channels.length === 0 ? (
                <EmptyState
                  title={t("workspace.startTitle")}
                  description={t("workspace.startHint")}
                  action={
                    <a className="btn btn--primary" href="#/app/sources">
                      {t("workspace.addChannel")}
                    </a>
                  }
                />
              ) : (
                <ul className="channel-list">
                  {channels.map((channel) => {
                    const state =
                      sourceStates[channel.status] ?? sourceStates.not_checked;
                    const date = channel.last_success_at
                      ? new Date(channel.last_success_at)
                      : null;
                    return (
                      <li key={channel.key}>
                        <div>
                          <strong>{channel.label}</strong>
                          <p className="muted">
                            {date && !Number.isNaN(date.getTime())
                              ? t("workspace.sourceUpdated", {
                                  time: date.toLocaleString(
                                    language === "id" ? "id-ID" : "en-GB",
                                  ),
                                })
                              : t("workspace.sourceUnknown")}
                          </p>
                        </div>
                        <div className="utility-bar">
                          {channel.synthetic && <Chip synthetic />}
                          <Chip tone={state.tone}>
                            {t("workspace." + state.key)}
                          </Chip>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </Card>
          </>
        )}
      </StateGate>
    </>
  );
}
