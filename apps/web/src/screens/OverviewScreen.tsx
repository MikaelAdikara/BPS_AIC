import {
  ArrowRight,
  ArrowUpRight,
  Eye,
  ListTodo,
  MessageSquareQuote,
  Package,
  Plug,
  RotateCcw,
  Ruler,
  Zap,
  type LucideIcon,
} from "lucide-react";
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
  Notice,
  type Tone,
} from "@/components/ui";
import { IssuesTable, StateGate, buckets } from "@/components/workspace";
import { OverviewInsights } from "@/components/OverviewInsights";
import { CountUp } from "@/components/visual/motion";
import { Donut, Meter } from "@/components/visual/charts";
export const bucketIcons: Record<string, LucideIcon> = {
  recurrence: RotateCcw,
  needs_fact: Ruler,
  to_do: Zap,
  monitoring: Eye,
};
const statusColors: Record<string, string> = {
  recurrence: "var(--status-critical)",
  needs_fact: "var(--status-warning)",
  to_do: "var(--status-info)",
  monitoring: "var(--status-good)",
};
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
function Kpi({
  icon: Icon,
  label,
  value,
  hint,
  tone,
}: {
  icon: LucideIcon;
  label: string;
  value: number | null | undefined;
  hint?: string;
  tone: string;
}) {
  return (
    <div className="kpi">
      <div className="kpi__top">
        <span>{label}</span>
        <span
          className="kpi__icon"
          style={{ color: tone, background: `color-mix(in srgb, ${tone} 13%, transparent)` }}
        >
          <Icon size={18} aria-hidden />
        </span>
      </div>
      <div className="kpi__value">
        <CountUp value={value} />
      </div>
      {hint && <p className="kpi__hint">{hint}</p>}
    </div>
  );
}
export function OverviewScreen() {
  const { user } = useAuth();
  const { t, language } = useI18n();
  const { summary, inbox, channels, status, run, busy } = useWorkspace();
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
  const today = new Date().toLocaleDateString(language === "id" ? "id-ID" : "en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
  const counts = overviewBuckets.map(({ bucket }) => summary?.buckets[bucket] ?? 0);
  const openTotal = counts.reduce((sum, value) => sum + value, 0);
  const connected = channels.filter((channel) => channel.status === "connected").length;
  const maxReviews = Math.max(1, ...channels.map((channel) => channel.reviews ?? 0));
  return (
    <>
      <header className="page-header">
        <div>
          <span className="page-eyebrow">
            <span className="pulse-dot" aria-hidden />
            {today}
          </span>
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
            <Chip style={{ marginTop: 10 }}>{t("workspace.includesSynthetic")}</Chip>
          )}
        </div>
        <div className="utility-bar">
          <a className="btn btn--outline" href="#/app/sources">
            <Plug size={16} aria-hidden />
            {t("workspace.addChannel")}
          </a>
          {summary?.top?.[0] && (
            <a className="btn btn--primary" href={issueLink(summary.top[0])}>
              {t("workspace.openNext")}
              <ArrowRight size={16} aria-hidden />
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
            <div className="kpi-grid">
              <Kpi
                icon={ListTodo}
                label={t("workspace.kpiOpen")}
                value={summary?.findings_open}
                tone="var(--blue)"
              />
              <Kpi
                icon={Package}
                label={t("workspace.kpiProducts")}
                value={summary?.products}
                tone="var(--status-good)"
              />
              <Kpi
                icon={MessageSquareQuote}
                label={t("workspace.kpiReviews")}
                value={summary?.reviews}
                tone="#8b5cf6"
              />
              <Kpi
                icon={Plug}
                label={t("workspace.kpiChannels")}
                value={connected}
                hint={t("workspace.kpiChannelsHint", { total: channels.length })}
                tone="var(--status-warning)"
              />
            </div>
            <div className="status-board">
              <div className="bucket-grid">
                {overviewBuckets.map(({ bucket, hint, tab }, index) => {
                  const Icon = bucketIcons[bucket];
                  const value = counts[index];
                  return (
                    <a
                      className={"bucket-card tone-" + buckets[bucket].tone}
                      key={bucket}
                      href={"#/app/issues?tab=" + tab}
                    >
                      <span className="bucket-card__top">
                        <span className="bucket-card__icon">
                          <Icon size={18} aria-hidden />
                        </span>
                        <ArrowUpRight size={18} className="bucket-card__arrow" aria-hidden />
                      </span>
                      <span className="bucket-card__value">
                        <CountUp value={value} />
                      </span>
                      <span>
                        <span className="bucket-card__label">
                          {t("workspace." + buckets[bucket].key)}
                        </span>
                        <span className="bucket-card__hint" style={{ display: "block" }}>
                          {t("workspace." + hint)}
                        </span>
                      </span>
                      <Meter
                        value={value}
                        max={Math.max(1, openTotal)}
                        label={t("workspace." + buckets[bucket].key)}
                      />
                    </a>
                  );
                })}
              </div>
              <Card title={t("workspace.statusTitle")} lead={t("workspace.statusLead")}>
                <Donut
                  centerLabel={t("workspace.statusTotal")}
                  slices={overviewBuckets.map(({ bucket, tab }, index) => {
                    const Icon = bucketIcons[bucket];
                    return {
                      key: bucket,
                      label: t("workspace." + buckets[bucket].key),
                      value: counts[index],
                      color: statusColors[bucket],
                      href: "#/app/issues?tab=" + tab,
                      icon: <Icon size={15} aria-hidden />,
                    };
                  })}
                />
              </Card>
            </div>
            <OverviewInsights />
            <Card
              title={t("workspace.whatFirst")}
              icon={<ListTodo size={18} aria-hidden />}
              action={
                <a className="card-link" href="#/app/issues">
                  {t("workspace.viewAll")}
                  <ArrowRight size={14} aria-hidden />
                </a>
              }
            >
              <IssuesTable items={inbox.slice(0, 6)} />
            </Card>
            <Card
              title={t("workspace.channels")}
              icon={<Plug size={18} aria-hidden />}
              action={
                <a className="card-link" href="#/app/sources">
                  {t("workspace.manage")}
                  <ArrowRight size={14} aria-hidden />
                </a>
              }
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
                        <span
                          className={"channel-dot tone-" + state.tone}
                          aria-hidden
                        >
                          <Plug size={16} />
                        </span>
                        <div className="channel-list__body">
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
                          {channel.reviews != null && (
                            <div className="channel-list__share">
                              <Meter
                                value={channel.reviews}
                                max={maxReviews}
                                label={channel.label}
                              />
                              <span className="count muted">
                                {t("workspace.counts", {
                                  products: channel.products ?? 0,
                                  reviews: channel.reviews,
                                })}
                              </span>
                            </div>
                          )}
                        </div>
                        <div className="utility-bar">
                          {channel.synthetic && <Chip synthetic />}
                          <Chip tone={state.tone}>
                            {state.tone === "good" && (
                              <span className="pulse-dot" aria-hidden />
                            )}
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
