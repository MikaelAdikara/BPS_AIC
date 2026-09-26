import { useEffect, useId, useState } from "react";
import { request, ApiError } from "@/api/http.js";
import { useWorkspace, type Issue } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { issueLink } from "@/lib/workspace-model.js";
import { AlertRows, type AlertEvent } from "@/screens/AlertsScreen";
import {
  Button,
  Card,
  Chip,
  EmptyState,
  LoadingState,
  Metric,
  Notice,
  Table,
} from "./ui";
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
function Ranking({
  rows,
  types = false,
}: {
  rows: { key: string; count: number }[];
  types?: boolean;
}) {
  const { t } = useI18n();
  const max = Math.max(1, ...rows.map((row) => row.count));
  return (
    <ul className="ranking-list">
      {rows.map((row) => (
        <li key={row.key}>
          <div>
            <span>
              {types
                ? t("workspace." + (typeKeys[row.key] ?? "typeOperations"))
                : row.key}
            </span>
            <strong className="count">{row.count}</strong>
          </div>
          <svg viewBox="0 0 100 6" aria-hidden="true">
            <rect width="100" height="6" fill="var(--line)" />
            <rect
              width={(row.count / max) * 100}
              height="6"
              fill="var(--blue)"
            />
          </svg>
        </li>
      ))}
    </ul>
  );
}
function EvidenceChart({ data }: { data: Insights }) {
  const { t, language } = useI18n();
  const id = useId();
  const max = Math.max(1, ...data.series.map((row) => row.count));
  const x = (index: number) =>
    20 + (index / Math.max(1, data.series.length - 1)) * 560;
  const y = (count: number) => 130 - (count / max) * 110;
  const line = data.series
    .map((row, index) => `${x(index)},${y(row.count)}`)
    .join(" ");
  return (
    <>
      <p className="muted">{t("overview.scope")}</p>
      {data.total === 0 ? (
        <Notice tone="muted">{t("overview.noEvidence")}</Notice>
      ) : (
        <svg
          className="evidence-chart"
          viewBox="0 0 600 160"
          role="img"
          aria-labelledby={id}
        >
          <title id={id}>{t("overview.evidence")}</title>
          <path
            d={`M20,130 L${line.replaceAll(" ", " L")} L580,130 Z`}
            fill="var(--blue-tint)"
          />
          <polyline
            points={line}
            fill="none"
            stroke="var(--blue)"
            strokeWidth="3"
          />
          {data.series.map((row, index) => (
            <circle
              key={row.date}
              cx={x(index)}
              cy={y(row.count)}
              r="4"
              fill="var(--blue)"
              tabIndex={0}
            >
              <title>
                {row.date}: {row.count}
              </title>
            </circle>
          ))}
          <text x="20" y="155" fill="var(--muted)" fontSize="12">
            {data.series[0]?.date}
          </text>
          <text
            x="580"
            y="155"
            textAnchor="end"
            fill="var(--muted)"
            fontSize="12"
          >
            {data.series.at(-1)?.date}
          </text>
        </svg>
      )}
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
  const id = useId();
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
  return (
    <div className="stack">
      <div className="field">
        <label htmlFor={id}>{t("overview.days")}</label>
        <select
          id={id}
          value={days}
          onChange={(event) => setDays(Number(event.target.value))}
        >
          {[7, 30, 90].map((value) => (
            <option key={value} value={value}>
              {t("overview.dayOption", { count: value })}
            </option>
          ))}
        </select>
      </div>
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
          <>
            <Card
              title={t("overview.plan")}
              lead={t("overview.planLead", { count: data.open })}
            >
              {data.plan.length === 0 ? (
                <EmptyState
                  title={t("overview.none")}
                  description={t("overview.noneHint")}
                />
              ) : (
                <ol className="decision-list">
                  {data.plan.map((item) => (
                    <li key={item.id}>
                      <div>
                        <strong>
                          {language === "id"
                            ? item.attribute_local
                            : item.attribute}
                        </strong>
                        <p>{t("overview."+item.next_step)}</p>
                        <p className="muted">{t("overview.score",{score:item.score})}</p>
                        <p className="muted">
                          {item.product_title} · {item.channel}
                        </p>
                        <div className="finding-picker">
                          <Chip>
                            {t("overview.reach", { count: item.support })}
                          </Chip>
                          {item.drivers.filter(driver=>["rising","falling","single_report","units"].includes(driver.key)).map(driver=><Chip key={driver.key}>{driver.key==="single_report"?t("overview.single"):driver.key==="units"?t("overview.units",{buyers:driver.illustrative_buyers??0,sold:driver.units_sold??0}):t("overview."+driver.key,{recent:percent(driver.recent??0),before:percent(driver.before??0)})}</Chip>)}
                          <Chip>
                            {t("overview.share", {
                              share: percent(item.share),
                              low: percent(item.confidence_low),
                            })}
                          </Chip>
                          {item.hidden_high_star > 0 && (
                            <Chip>
                              {t("overview.hidden", {
                                count: item.hidden_high_star,
                              })}
                            </Chip>
                          )}
                          <Chip>
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
                      </div>
                      <a className="btn btn--outline" href={issueLink(item)}>
                        {t("overview.open")}
                      </a>
                    </li>
                  ))}
                </ol>
              )}
              <details>
                <summary>{t("overview.heuristic")}</summary>
                <p>{t("overview.heuristicHint")}</p>
              </details>
            </Card>
            <div className="insights-grid">
              <Card title={t("overview.evidence")}>
                <EvidenceChart data={data} />
                <div className="evidence-metrics">
                  <Metric value={data.total} label={t("overview.total")} />
                  <Metric value={data.delta} label={t("overview.delta")} />
                  <Metric
                    value={data.affected_products}
                    label={t("overview.affected")}
                  />
                  <Metric
                    value={data.average_rating ?? "—"}
                    label={t("overview.rating")}
                  />
                </div>
                <p className="muted">
                  {t("overview.undated", { count: data.undated })}
                </p>
              </Card>
              <Card title={t("overview.brief")}>
                <p>{t("overview.briefText", { count: data.open })}</p>
                {data.plan[0] && (
                  <>
                    <p>
                      {t("overview.next", {
                        product: data.plan[0].product_title,
                      })}
                    </p>
                    <a
                      className="btn btn--primary"
                      href={issueLink(data.plan[0])}
                    >
                      {t("overview.open")}
                    </a>
                  </>
                )}
                <p className="muted">{t("overview.rules")}</p>
              </Card>
            </div>
            <div className="insights-grid">
              <Card title={t("overview.channel")}>
                <Ranking rows={data.ranking_channels} />
              </Card>
              <Card title={t("overview.type")}>
                <Ranking rows={data.ranking_types} types />
              </Card>
            </div>
            {(["one_fix_candidates", "same_product_candidates"] as const).map(
              (key) =>
                data[key].length > 0 && (
                  <Card
                    key={key}
                    title={t(
                      "overview." +
                        (key === "one_fix_candidates" ? "candidates" : "same"),
                    )}
                    lead={t("overview.candidateHint")}
                  >
                    <ul>
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
          </>
        )
      )}
      <Card
        title={t("overview.alerts")}
        action={<a href="#/app/alerts">{t("overview.allAlerts")}</a>}
      >
        {loading ? (
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
