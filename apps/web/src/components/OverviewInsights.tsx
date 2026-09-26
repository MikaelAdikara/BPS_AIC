import { useEffect, useState } from "react";
import {
  ArrowRight,
  Bell,
  CalendarDays,
  ChartSpline,
  Clock,
  EyeOff,
  Layers,
  ListOrdered,
  MessageSquareWarning,
  Package,
  Percent,
  Plug,
  Sparkles,
  Star,
  Tag,
  TrendingDown,
  TrendingUp,
  Users,
} from "lucide-react";
import { request, ApiError } from "@/api/http.js";
import { useWorkspace, type Issue } from "@/api/workspace";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
import { issueLink } from "@/lib/workspace-model.js";
import { AlertRows, type AlertEvent } from "@/screens/AlertsScreen";
import {
  Button,
  Card,
  Chip,
  EmptyState,
  LoadingState,
  Notice,
  Table,
} from "./ui";
import { AreaChart, BarList, Meter } from "./visual/charts";
import { CountUp } from "./visual/motion";
interface Plan extends Issue {
  share: number;
  confidence_low: number;
  hidden_high_star: number;
  estimated_minutes: number;
  next_step: string;
  score: number;
  drivers: {key: string; recent?: number; before?: number; units_sold?: number; illustrative_buyers?: number; support?: number; share?: number; confident_share?: number; n?: number; minutes?: number}[];
}
interface Decision {
  finding_id: string;
  product_id: string;
  product_title: string;
  channel: string;
  attribute_local: string;
  bucket: string;
  next_step: string;
  score: number;
  drivers: Plan["drivers"];
}
interface Insights {
  days: number;
  series: { date: string; count: number }[];
  total: number;
  previous: number;
  delta: number;
  undated: number;
  affected_products: number;
  average_rating: number | null;
  open: number;
  plan: Plan[];
  ranking_channels: { key: string; count: number }[];
  ranking_types: { key: string; count: number }[];
  one_fix_candidates: { label: string; items: Issue[] }[];
  same_product_candidates: { label: string; items: Issue[] }[];
}
const typeKeys: Record<string, string> = {
  missing_fact: "typeMissingFact",
  unclear_fact: "typeUnclearWording",
  conflicting_fact: "typeListingConflict",
  expectation_mismatch: "typeExpectationGap",
  product_quality: "typeQuality",
  operational: "typeOperations",
};
function EvidenceChart({ data }: { data: Insights }) {
  const { t, language } = useI18n();
  const locale = language === "id" ? "id-ID" : "en-GB";
  const short = (date: string) =>
    new Date(date + "T00:00:00").toLocaleDateString(locale, {
      day: "numeric",
      month: "short",
    });
  const direction = data.delta > 0 ? "up" : data.delta < 0 ? "down" : "flat";
  const Trend = data.delta < 0 ? TrendingDown : TrendingUp;
  return (
    <>
      <p className="muted chart-scope">{t("overview.scope")}</p>
      {data.total === 0 ? (
        <Notice tone="muted">{t("overview.noEvidence")}</Notice>
      ) : (
        <AreaChart
          title={t("overview.evidence")}
          valueLabel={t("overview.count")}
          formatLabel={short}
          data={data.series.map((row) => ({ label: row.date, value: row.count }))}
        />
      )}
      <div className="metric-tiles">
        <div className="metric-tile">
          <span className="metric-tile__label">
            <MessageSquareWarning size={14} aria-hidden />
            {t("overview.total")}
          </span>
          <span className="metric-tile__value">
            <CountUp value={data.total} />
            <span className={"delta delta--" + direction}>
              <Trend size={12} aria-hidden />
              {data.delta > 0 ? "+" : ""}
              {data.delta}
            </span>
          </span>
        </div>
        <div className="metric-tile">
          <span className="metric-tile__label">
            <Trend size={14} aria-hidden />
            {t("overview.delta")}
          </span>
          <span className="metric-tile__value">
            <CountUp value={data.delta} format={(value) => (value > 0 ? "+" : "") + value} />
          </span>
        </div>
        <div className="metric-tile">
          <span className="metric-tile__label">
            <Package size={14} aria-hidden />
            {t("overview.affected")}
          </span>
          <span className="metric-tile__value">
            <CountUp value={data.affected_products} />
          </span>
        </div>
        <div className="metric-tile">
          <span className="metric-tile__label">
            <Star size={14} aria-hidden />
            {t("overview.rating")}
          </span>
          <span className="metric-tile__value">
            <CountUp value={data.average_rating} decimals={data.average_rating == null ? 0 : 2} />
            {data.average_rating != null && <Star size={16} className="star-icon" aria-hidden />}
          </span>
        </div>
      </div>
      <p className="muted chart-note">
        <CalendarDays size={14} aria-hidden />
        {t("overview.undated", { count: data.undated })}
      </p>
      <details>
        <summary>{t("overview.table")}</summary>
        <Table>
          <thead>
            <tr>
              <th>{t("overview.date")}</th>
              <th>{t("overview.count")}</th>
            </tr>
          </thead>
          <tbody>
            {data.series.map((row) => (
              <tr key={row.date}>
                <td>
                  {new Date(row.date + "T00:00:00").toLocaleDateString(
                    language,
                  )}
                </td>
                <td className="count">{row.count}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      </details>
    </>
  );
}
export function OverviewInsights() {
  const { summary } = useWorkspace();
  const { t, language, localizeError } = useI18n();
  const [days, setDays] = useState(30);
  const [data, setData] = useState<Insights | null>(null);
  const [alerts, setAlerts] = useState<AlertEvent[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const [expanded, setExpanded] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    Promise.allSettled([
      request("/deciqo/overview?days=" + days, { signal: controller.signal }),
      request("/deciqo/alerts?lang=" + language, { signal: controller.signal }),
      request("/deciqo/decisions", { signal: controller.signal }),
    ]).then(([insights, events, decisions]) => {
      if (controller.signal.aborted) return;
      if (insights.status === "fulfilled" && decisions.status === "fulfilled") {
        const response: { decisions: Decision[] } = decisions.value;
        const plan = response.decisions.map(row => {
          const source = (insights.value.plan as Plan[]).find(item => item.id === row.finding_id);
          const reach = row.drivers.find(driver => driver.key === "reach")!;
          const effort = row.drivers.find(driver => driver.key === "effort")!;
          return { ...source, ...row, id: row.finding_id, attribute: source?.attribute ?? row.attribute_local,
            support: reach.support!, share: reach.share!, confidence_low: reach.confident_share!,
            hidden_high_star: row.drivers.find(driver => driver.key === "hidden")?.n ?? 0,
            estimated_minutes: effort.minutes! } as Plan;
        });
        setData({ ...insights.value, plan });
      }
      else {
        setData(null);
        const failure = insights.status === "rejected" ? insights.reason : decisions.status === "rejected" ? decisions.reason : null;
        setError((failure as ApiError)?.code ?? "request_failed");
      }
      setAlerts(events.status === "fulfilled" ? events.value.events : null);
      setLoading(false);
    });
    return () => controller.abort();
  }, [days, summary, language, revision]);
  const percent = (value: number) =>
    new Intl.NumberFormat(language, {
      style: "percent",
      maximumFractionDigits: 1,
    }).format(value);
  const maxScore = Math.max(0.0001, ...(data?.plan.map((item) => item.score) ?? [0]));
  return (
    <div className="stack">
      <div className="section-bar">
        <div>
          <h2>{t("overview.insights")}</h2>
          <p className="muted">{t("overview.insightsLead")}</p>
        </div>
        <div className="segmented" role="group" aria-label={t("overview.days")}>
          {[7, 30, 90].map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={days === value}
              onClick={() => setDays(value)}
            >
              {t("overview.dayOption", { count: value })}
            </button>
          ))}
        </div>
      </div>
      {loading && !data ? (
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
          <div className={cn("stack", loading && "is-refreshing")} aria-busy={loading || undefined}>
            <div className="insights-grid">
              <Card title={t("overview.evidence")} icon={<ChartSpline size={18} aria-hidden />}>
                <EvidenceChart data={data} />
              </Card>
              <section className="brief-card" aria-labelledby="brief-title">
                <span className="brief-card__rings" aria-hidden />
                <h2 id="brief-title">
                  <Sparkles size={16} aria-hidden />
                  {t("overview.brief")}
                </h2>
                <p className="brief-card__big">{t("overview.briefText", { count: data.open })}</p>
                {data.plan[0] && (
                  <>
                    <p>
                      {t("overview.next", {
                        product: data.plan[0].product_title,
                      })}
                    </p>
                    <a
                      className="btn"
                      href={issueLink(data.plan[0])}
                    >
                      {t("overview.open")}
                      <ArrowRight size={16} aria-hidden />
                    </a>
                    {data.plan.length > 1 && (
                      <ol className="brief-card__queue" start={2}>
                        {data.plan.slice(1, 4).map((item) => (
                          <li key={item.id}>
                            <a href={issueLink(item)}>
                              <span>{language === "id" ? item.attribute_local : item.attribute}</span>
                              <small>{item.product_title}</small>
                            </a>
                          </li>
                        ))}
                      </ol>
                    )}
                  </>
                )}
                <p className="muted">{t("overview.rules")}</p>
              </section>
            </div>
            <Card
              title={t("overview.plan")}
              lead={t("overview.planLead", { count: data.open })}
              icon={<ListOrdered size={18} aria-hidden />}
            >
              {data.plan.length === 0 ? (
                <EmptyState
                  title={t("overview.none")}
                  description={t("overview.noneHint")}
                />
              ) : (
                <ol className="decision-list">
                  {data.plan.slice(0, expanded ? undefined : 5).map((item, index) => (
                    <li key={item.id} className="decision-item">
                      <span className="decision-rank" aria-hidden>
                        {index + 1}
                      </span>
                      <div>
                        <h3>
                          {language === "id"
                            ? item.attribute_local
                            : item.attribute}
                        </h3>
                        <p className="decision-item__next">
                          <ArrowRight size={14} aria-hidden />
                          {t("overview."+item.next_step)}
                        </p>
                        <p className="muted decision-item__meta">
                          {item.product_title} · {item.channel}
                        </p>
                        <div className="decision-score">
                          <span>{t("overview.score",{score:item.score})}</span>
                          <Meter value={item.score} max={maxScore} label={t("overview.score",{score:item.score})} />
                        </div>
                        <div className="finding-picker">
                          <Chip tone="info">
                            <Users size={12} aria-hidden />
                            {item.support_is_minimum ? "≥ " : ""}{t("overview.reach", { count: item.support })}
                          </Chip>
                          {item.drivers.filter(driver=>["rising","falling","single_report","units"].includes(driver.key)).map(driver=><Chip key={driver.key} tone={driver.key==="rising"?"alert":driver.key==="falling"?"good":"muted"}>{driver.key==="rising"?<TrendingUp size={12} aria-hidden />:driver.key==="falling"?<TrendingDown size={12} aria-hidden />:null}{driver.key==="single_report"?t("overview.single"):driver.key==="units"?t("overview.units",{buyers:driver.illustrative_buyers??"—",sold:driver.units_sold??"—"}):t("overview."+driver.key,{recent:driver.recent == null ? "—" : percent(driver.recent),before:driver.before == null ? "—" : percent(driver.before)})}</Chip>)}
                          <Chip>
                            <Percent size={12} aria-hidden />
                            {t("overview.share", {
                              share: percent(item.share),
                              low: percent(item.confidence_low),
                            })}
                          </Chip>
                          {item.hidden_high_star > 0 && (
                            <Chip tone="warn">
                              <EyeOff size={12} aria-hidden />
                              {t("overview.hidden", {
                                count: item.hidden_high_star,
                              })}
                            </Chip>
                          )}
                          <Chip>
                            <Clock size={12} aria-hidden />
                            {t("overview.minutes", {
                              count: item.estimated_minutes,
                            })}
                          </Chip>
                          <Chip>
                            {t(
                              "workspace." +
                                ({
                                  recurrence: "bucketRecurrence",
                                  needs_fact: "bucketNeedsFact",
                                  to_do: "bucketTodo",
                                }[item.bucket] ?? "bucketTodo"),
                            )}
                          </Chip>
                        </div>
                        {item.support_is_minimum && <p className="muted">{t("product.minimum", {read:item.candidates_read, total:item.denominator})}</p>}
                      </div>
                      <a className="btn btn--outline btn--sm" href={issueLink(item)}>
                        {t("overview.open")}
                        <ArrowRight size={14} aria-hidden />
                      </a>
                    </li>
                  ))}
                </ol>
              )}
              <div className="plan-foot">
                <details>
                  <summary>{t("overview.heuristic")}</summary>
                  <p>{t("overview.heuristicHint")}</p>
                </details>
                {data.plan.length > 5 && <Button variant="text" onClick={() => setExpanded(value => !value)}>{t(expanded ? "overview.showFewer" : "overview.showAll")}</Button>}
              </div>
            </Card>
            <div className="insights-grid insights-grid--even">
              <Card title={t("overview.channel")} icon={<Plug size={18} aria-hidden />}>
                <BarList
                  rows={data.ranking_channels.map((row) => ({
                    key: row.key,
                    label: row.key,
                    value: row.count,
                  }))}
                />
              </Card>
              <Card title={t("overview.type")} icon={<Tag size={18} aria-hidden />}>
                <BarList
                  color="color-mix(in srgb, var(--blue) 55%, var(--sky-deep))"
                  rows={data.ranking_types.map((row) => ({
                    key: row.key,
                    label: t("workspace." + (typeKeys[row.key] ?? "typeOperations")),
                    value: row.count,
                  }))}
                />
              </Card>
            </div>
            {(["one_fix_candidates", "same_product_candidates"] as const).map(
              (key) =>
                data[key].length > 0 && (
                  <Card
                    key={key}
                    icon={<Layers size={18} aria-hidden />}
                    title={t(
                      "overview." +
                        (key === "one_fix_candidates" ? "candidates" : "same"),
                    )}
                    lead={t("overview.candidateHint")}
                  >
                    <ul className="candidate-list">
                      {data[key].map((group) => (
                        <li key={group.label}>
                          <strong>{group.label}</strong>
                          <ul>
                            {group.items.map((item) => (
                              <li key={item.id}>
                                <a href={issueLink(item)}>
                                  {item.product_title} · {item.channel}
                                </a>
                              </li>
                            ))}
                          </ul>
                        </li>
                      ))}
                    </ul>
                  </Card>
                ),
            )}
          </div>
        )
      )}
      <Card
        title={t("overview.alerts")}
        icon={<Bell size={18} aria-hidden />}
        action={
          <a className="card-link" href="#/app/alerts">
            {t("overview.allAlerts")}
            <ArrowRight size={14} aria-hidden />
          </a>
        }
      >
        {loading && !alerts ? (
          <LoadingState />
        ) : alerts === null ? (
          <Notice tone="warn">{t("common.unavailable")}</Notice>
        ) : alerts.length ? (
          <AlertRows events={alerts.slice(0, 4)} />
        ) : (
          <EmptyState
            title={t("alerts.empty")}
            description={t("alerts.emptyHint")}
          />
        )}
      </Card>
    </div>
  );
}
