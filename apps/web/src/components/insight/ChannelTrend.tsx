import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { Activity } from "lucide-react";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
import { channelColor, channelLabel, sortChannels, spreadLabels } from "@/lib/insight-model";
import { Notice, Table } from "@/components/ui";
import { useInView } from "@/components/visual/motion";

function useWidth() {
  const ref = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    setWidth(el.clientWidth);
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width));
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  return { ref, width };
}

function niceMax(value: number) {
  if (value <= 4) return Math.max(1, Math.ceil(value));
  const power = Math.pow(10, Math.floor(Math.log10(value)));
  return ([1, 2, 2.5, 5, 10].find((s) => s * power >= value) ?? 10) * power;
}

/** Satu garis per kanal pada satu sumbu y. Label ujung garis dipisah agar tidak menumpuk,
 * legenda bisa menyembunyikan kanal, dan crosshair menampilkan angka semua kanal di hari itu. */
export function ChannelTrend({
  volume,
  evidence,
  channels: all,
  channel,
  height = 260,
}: {
  volume: Record<string, number | string>[];
  evidence: Record<string, number | string>[];
  channels: string[];
  channel: string;
  height?: number;
}) {
  const { t, language } = useI18n();
  const locale = language === "id" ? "id-ID" : "en-GB";
  const [mode, setMode] = useState<"all" | "evidence">("all");
  const [off, setOff] = useState<Set<string>>(() => new Set());
  const [active, setActive] = useState<number | null>(null);
  const { ref, width } = useWidth();
  const seen = useInView<HTMLDivElement>(0.25);
  const rows = mode === "all" ? volume : evidence;
  const channels = sortChannels(all).filter((c) => !channel || c === channel);
  const shown = channels.filter((c) => !off.has(c));
  const total = rows.reduce((sum, row) => sum + channels.reduce((s, c) => s + Number(row[c] ?? 0), 0), 0);
  const short = (date: string) =>
    new Date(date + "T00:00:00").toLocaleDateString(locale, { day: "numeric", month: "short" });

  const labelWidth = Math.min(110, Math.max(70, width * 0.14));
  const pad = { top: 14, right: labelWidth, bottom: 28, left: 34 };
  const w = Math.max(0, width - pad.left - pad.right);
  const h = height - pad.top - pad.bottom;
  const max = niceMax(Math.max(0, ...rows.flatMap((row) => shown.map((c) => Number(row[c] ?? 0)))));
  const x = (i: number) => pad.left + (rows.length < 2 ? w / 2 : (i / (rows.length - 1)) * w);
  const y = (v: number) => pad.top + h - (v / max) * h;
  const ticks = [...new Set([0, Math.round(max / 2), max])];
  const labelIdx = rows.length > 2 ? [0, Math.floor((rows.length - 1) / 2), rows.length - 1] : rows.map((_, i) => i);
  const ends = spreadLabels(
    shown.map((c) => ({ c, y: y(Number(rows.at(-1)?.[c] ?? 0)) })),
    14,
    pad.top,
    pad.top + h,
  );

  function pick(clientX: number, rect: DOMRect) {
    if (!rows.length || w <= 0) return;
    const rel = (clientX - rect.left - pad.left) / w;
    setActive(Math.max(0, Math.min(rows.length - 1, Math.round(rel * (rows.length - 1)))));
  }
  function key(event: KeyboardEvent) {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") {
      if (event.key === "Escape") setActive(null);
      return;
    }
    event.preventDefault();
    const step = event.key === "ArrowRight" ? 1 : -1;
    setActive((current) => Math.max(0, Math.min(rows.length - 1, (current ?? (step > 0 ? -1 : rows.length)) + step)));
  }
  const point = active == null ? null : rows[active];

  return (
    <section className="card trend-card" aria-labelledby="trend-title">
      <header className="card__header">
        <div>
          <h2 className="card__title" id="trend-title">
            <Activity size={18} aria-hidden />
            {t("insights.trendTitle")}
          </h2>
          <p className="muted">{t("insights.trendLead")}</p>
        </div>
        <div className="segmented segmented--sm" role="group" aria-label={t("insights.trendTitle")}>
          <button type="button" aria-pressed={mode === "all"} onClick={() => setMode("all")}>
            {t("insights.trendAll")}
          </button>
          <button type="button" aria-pressed={mode === "evidence"} onClick={() => setMode("evidence")}>
            {t("insights.trendEvidence")}
          </button>
        </div>
      </header>
      <div className="card__body">
        {total === 0 ? (
          <Notice tone="muted">{t("insights.trendEmpty")}</Notice>
        ) : (
          <div
            ref={(node) => {
              (ref as { current: HTMLDivElement | null }).current = node;
              (seen.ref as { current: HTMLDivElement | null }).current = node;
            }}
            className={cn("chart chart--multi", seen.inView && "is-drawn")}
            style={{ height }}
          >
            {width > 0 && (
              <svg
                width={width}
                height={height}
                role="img"
                aria-label={t("insights.trendTitle")}
                tabIndex={0}
                onKeyDown={key}
                onBlur={() => setActive(null)}
                onPointerMove={(event) => pick(event.clientX, event.currentTarget.getBoundingClientRect())}
                onPointerLeave={() => setActive(null)}
              >
                {ticks.map((tick) => (
                  <g key={tick} className="chart__grid">
                    <line x1={pad.left} x2={pad.left + w} y1={y(tick)} y2={y(tick)} />
                    <text x={pad.left - 8} y={y(tick)} dy="0.32em" textAnchor="end">
                      {tick}
                    </text>
                  </g>
                ))}
                {labelIdx.map((i) => (
                  <text
                    key={i}
                    className="chart__axis"
                    x={x(i)}
                    y={height - 8}
                    textAnchor={i === 0 ? "start" : i === rows.length - 1 ? "end" : "middle"}
                  >
                    {short(String(rows[i].date))}
                  </text>
                ))}
                {shown.map((c) => (
                  <polyline
                    key={c}
                    className="multi-line"
                    points={rows.map((row, i) => `${x(i)},${y(Number(row[c] ?? 0))}`).join(" ")}
                    stroke={channelColor(c)}
                    pathLength={1}
                  />
                ))}
                {ends.map((end) => (
                  <g key={end.c} className="multi-end">
                    <circle cx={pad.left + w} cy={end.y} r={3.5} fill={channelColor(end.c)} />
                    <text x={pad.left + w + 10} y={end.ly} dy="0.32em">
                      {channelLabel(end.c)}
                    </text>
                  </g>
                ))}
                {point && active != null && (
                  <g className="chart__cross">
                    <line x1={x(active)} x2={x(active)} y1={pad.top} y2={pad.top + h} />
                    {shown.map((c) => (
                      <circle key={c} cx={x(active)} cy={y(Number(point[c] ?? 0))} r={4} style={{ stroke: channelColor(c) }} />
                    ))}
                  </g>
                )}
              </svg>
            )}
            {point && active != null && (
              <div
                className="chart__tip chart__tip--multi"
                role="status"
                style={{ left: Math.min(Math.max(x(active), 80), Math.max(80, width - pad.right - 60)), top: pad.top }}
              >
                <span className="chart__tip-date">{short(String(point.date))}</span>
                {[...shown]
                  .sort((a, b) => Number(point[b] ?? 0) - Number(point[a] ?? 0))
                  .map((c) => (
                    <span key={c} className="chart__tip-row">
                      <i style={{ background: channelColor(c) }} aria-hidden />
                      {channelLabel(c)}
                      <strong className="count">{Number(point[c] ?? 0)}</strong>
                    </span>
                  ))}
              </div>
            )}
          </div>
        )}
        <div className="trend-legend" role="group" aria-label={t("insights.filterTitle")}>
          {channels.map((c) => (
            <button
              key={c}
              type="button"
              aria-pressed={!off.has(c)}
              onClick={() =>
                setOff((current) => {
                  const next = new Set(current);
                  if (next.has(c)) next.delete(c);
                  else if (channels.length - next.size > 1) next.add(c);
                  return next;
                })
              }
            >
              <i style={{ background: channelColor(c) }} aria-hidden />
              {channelLabel(c)}
              <span className="count muted">
                {rows.reduce((sum, row) => sum + Number(row[c] ?? 0), 0)}
              </span>
            </button>
          ))}
        </div>
        <details>
          <summary>{t("insights.trendTable")}</summary>
          <Table>
            <thead>
              <tr>
                <th scope="col">{t("insights.date")}</th>
                {channels.map((c) => (
                  <th scope="col" key={c}>{channelLabel(c)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={String(row.date)}>
                  <td>{short(String(row.date))}</td>
                  {channels.map((c) => (
                    <td className="count" key={c}>{Number(row[c] ?? 0)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </Table>
        </details>
      </div>
    </section>
  );
}
