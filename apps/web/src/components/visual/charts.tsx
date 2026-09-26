import {
  useEffect,
  useId,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent,
  type ReactNode,
} from "react";
import { cn } from "@/lib/cn";
import { useInView } from "./motion";

/* Grafik SVG ringan yang memakai token tema. Semua nilai yang tampil di tooltip juga tersedia
 * lewat label langsung atau tabel data di pemanggilnya; tooltip hanya mempercepat. */

function useWidth<T extends HTMLElement>() {
  const ref = useRef<T>(null);
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

/** Kurva monoton (Fritsch–Carlson): tidak pernah melewati titik data, jadi tidak turun di bawah nol. */
function monotonePath(points: [number, number][]) {
  const n = points.length;
  if (n === 0) return "";
  if (n === 1) return `M${points[0][0]},${points[0][1]}`;
  const dx: number[] = [];
  const slope: number[] = [];
  for (let i = 0; i < n - 1; i++) {
    dx.push(points[i + 1][0] - points[i][0]);
    slope.push((points[i + 1][1] - points[i][1]) / (dx[i] || 1));
  }
  const tangent = [slope[0]];
  for (let i = 1; i < n - 1; i++) {
    tangent.push(slope[i - 1] * slope[i] <= 0 ? 0 : (slope[i - 1] + slope[i]) / 2);
  }
  tangent.push(slope[n - 2]);
  for (let i = 0; i < n - 1; i++) {
    if (slope[i] === 0) {
      tangent[i] = 0;
      tangent[i + 1] = 0;
      continue;
    }
    const a = tangent[i] / slope[i];
    const b = tangent[i + 1] / slope[i];
    const h = a * a + b * b;
    if (h > 9) {
      const t = 3 / Math.sqrt(h);
      tangent[i] = t * a * slope[i];
      tangent[i + 1] = t * b * slope[i];
    }
  }
  let d = `M${points[0][0]},${points[0][1]}`;
  for (let i = 0; i < n - 1; i++) {
    const [x0, y0] = points[i];
    const [x1, y1] = points[i + 1];
    const h = dx[i] / 3;
    d += ` C${x0 + h},${y0 + tangent[i] * h} ${x1 - h},${y1 - tangent[i + 1] * h} ${x1},${y1}`;
  }
  return d;
}

function niceMax(value: number) {
  if (value <= 4) return Math.max(1, Math.ceil(value));
  const power = Math.pow(10, Math.floor(Math.log10(value)));
  const step = [1, 2, 2.5, 5, 10].find((s) => s * power >= value / 1) ?? 10;
  return step * power;
}

export interface Point {
  label: string;
  value: number;
}

/** Deret waktu tunggal dengan area bergradien, crosshair, dan navigasi keyboard (←/→). */
export function AreaChart({
  data,
  height = 220,
  title,
  valueLabel,
  formatLabel = (label) => label,
  className,
}: {
  data: Point[];
  height?: number;
  title: string;
  valueLabel: string;
  formatLabel?: (label: string) => string;
  className?: string;
}) {
  const { ref, width } = useWidth<HTMLDivElement>();
  const view = useInView<HTMLDivElement>(0.25);
  const id = useId().replace(/:/g, "");
  const [active, setActive] = useState<number | null>(null);
  const pad = { top: 16, right: 12, bottom: 28, left: 32 };
  const w = Math.max(0, width - pad.left - pad.right);
  const h = height - pad.top - pad.bottom;
  const max = niceMax(Math.max(0, ...data.map((d) => d.value)));
  const x = (i: number) => pad.left + (data.length < 2 ? w / 2 : (i / (data.length - 1)) * w);
  const y = (v: number) => pad.top + h - (v / max) * h;
  const points = data.map((d, i) => [x(i), y(d.value)] as [number, number]);
  const line = monotonePath(points);
  const area = points.length
    ? `${line} L${points.at(-1)![0]},${pad.top + h} L${points[0][0]},${pad.top + h} Z`
    : "";
  const ticks = [0, max / 2, max].map((v) => Math.round(v * 10) / 10);
  const labelIdx = data.length > 2 ? [0, Math.floor((data.length - 1) / 2), data.length - 1] : data.map((_, i) => i);

  function pick(clientX: number, rect: DOMRect) {
    if (!data.length || w <= 0) return;
    const rel = (clientX - rect.left - pad.left) / w;
    setActive(Math.max(0, Math.min(data.length - 1, Math.round(rel * (data.length - 1)))));
  }
  function key(event: KeyboardEvent) {
    if (!data.length) return;
    if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
      event.preventDefault();
      const step = event.key === "ArrowRight" ? 1 : -1;
      setActive((current) =>
        Math.max(0, Math.min(data.length - 1, (current ?? (step > 0 ? -1 : data.length)) + step)),
      );
    } else if (event.key === "Escape") setActive(null);
  }
  const point = active == null ? null : data[active];

  return (
    <div
      ref={(node) => {
        (ref as { current: HTMLDivElement | null }).current = node;
        (view.ref as { current: HTMLDivElement | null }).current = node;
      }}
      className={cn("chart chart--area", view.inView && "is-drawn", className)}
      style={{ height }}
    >
      {width > 0 && (
        <svg
          width={width}
          height={height}
          role="img"
          aria-labelledby={id + "t"}
          tabIndex={0}
          onKeyDown={key}
          onBlur={() => setActive(null)}
          onPointerMove={(event) => pick(event.clientX, event.currentTarget.getBoundingClientRect())}
          onPointerLeave={() => setActive(null)}
        >
          <title id={id + "t"}>{title}</title>
          <defs>
            <linearGradient id={id + "g"} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="var(--chart-accent)" stopOpacity="0.28" />
              <stop offset="100%" stopColor="var(--chart-accent)" stopOpacity="0" />
            </linearGradient>
          </defs>
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
              textAnchor={i === 0 ? "start" : i === data.length - 1 ? "end" : "middle"}
            >
              {formatLabel(data[i].label)}
            </text>
          ))}
          <path className="chart__area" d={area} fill={`url(#${id}g)`} />
          <path className="chart__line" d={line} pathLength={1} />
          {point && active != null && (
            <g className="chart__cross">
              <line x1={x(active)} x2={x(active)} y1={pad.top} y2={pad.top + h} />
              <circle cx={x(active)} cy={y(point.value)} r={5} />
            </g>
          )}
        </svg>
      )}
      {point && active != null && (
        <div
          className="chart__tip"
          role="status"
          style={
            {
              left: Math.min(Math.max(x(active), 70), Math.max(70, width - 70)),
              top: Math.max(0, y(point.value) - 12),
            } as CSSProperties
          }
        >
          <strong>{point.value}</strong>
          <span>
            <i className="chart__key" /> {valueLabel}
          </span>
          <span className="chart__tip-date">{formatLabel(point.label)}</span>
        </div>
      )}
    </div>
  );
}

export interface Slice {
  key: string;
  label: string;
  value: number;
  color: string;
  href?: string;
  icon?: ReactNode;
}

/** Donat komposisi dengan celah 2px antar-segmen, angka total di tengah, dan legenda berlabel. */
export function Donut({
  slices,
  total,
  centerLabel,
  size = 176,
  thickness = 18,
}: {
  slices: Slice[];
  total?: number;
  centerLabel: string;
  size?: number;
  thickness?: number;
}) {
  const view = useInView<HTMLDivElement>(0.3);
  const [hover, setHover] = useState<string | null>(null);
  const sum = slices.reduce((s, x) => s + x.value, 0);
  const r = (size - thickness) / 2;
  const c = 2 * Math.PI * r;
  const gap = slices.filter((s) => s.value > 0).length > 1 ? 3 : 0;
  let offset = 0;
  const shown = hover ? slices.find((s) => s.key === hover) : null;
  return (
    <div ref={view.ref} className={cn("donut", view.inView && "is-drawn")}>
      <div className="donut__ring" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden>
          <circle className="donut__track" cx={size / 2} cy={size / 2} r={r} strokeWidth={thickness} />
          {slices.map((slice, index) => {
            if (slice.value <= 0 || sum === 0) return null;
            const length = (slice.value / sum) * c;
            const dash = Math.max(0.5, length - gap);
            const el = (
              <circle
                key={slice.key}
                className={cn("donut__seg", hover && hover !== slice.key && "is-dim")}
                cx={size / 2}
                cy={size / 2}
                r={r}
                stroke={slice.color}
                strokeWidth={thickness}
                strokeDashoffset={-offset}
                style={{ "--i": index, strokeDasharray: `${dash} ${c}` } as CSSProperties}
                onPointerEnter={() => setHover(slice.key)}
                onPointerLeave={() => setHover(null)}
              />
            );
            offset += length;
            return el;
          })}
        </svg>
        <div className="donut__center">
          <strong className="donut__value">{shown ? shown.value : (total ?? sum)}</strong>
          <span className="donut__label">{shown ? shown.label : centerLabel}</span>
        </div>
      </div>
      <ul className="donut__legend">
        {slices.map((slice) => {
          const body = (
            <>
              <i className="donut__swatch" style={{ background: slice.color }} />
              {slice.icon}
              <span className="donut__name">{slice.label}</span>
              <strong className="count">{slice.value}</strong>
              <span className="donut__pct count">
                {sum ? Math.round((slice.value / sum) * 100) : 0}%
              </span>
            </>
          );
          return (
            <li
              key={slice.key}
              className={cn(hover === slice.key && "is-active")}
              onPointerEnter={() => setHover(slice.key)}
              onPointerLeave={() => setHover(null)}
            >
              {slice.href ? (
                <a href={slice.href} onFocus={() => setHover(slice.key)} onBlur={() => setHover(null)}>
                  {body}
                </a>
              ) : (
                <div>{body}</div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

/** Peringkat horizontal: label dan nilai tertulis langsung, batang tumbuh saat terlihat. */
export function BarList({
  rows,
  color = "var(--chart-accent)",
}: {
  rows: { key: string; label: ReactNode; value: number; color?: string; icon?: ReactNode }[];
  color?: string;
}) {
  const view = useInView<HTMLUListElement>(0.3);
  const max = Math.max(1, ...rows.map((row) => row.value));
  return (
    <ul ref={view.ref} className={cn("bar-list", view.inView && "is-drawn")}>
      {rows.map((row, index) => (
        <li key={row.key} style={{ "--i": index } as CSSProperties}>
          <div className="bar-list__head">
            <span className="bar-list__label">
              {row.icon}
              {row.label}
            </span>
            <strong className="count">{row.value}</strong>
          </div>
          <div className="bar-list__track" aria-hidden>
            <span
              className="bar-list__bar"
              style={{ width: (row.value / max) * 100 + "%", background: row.color ?? color }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}

/** Garis kecil tanpa sumbu untuk kartu statistik. Dekoratif; nilainya ada di kartu. */
export function Sparkline({
  values,
  width = 96,
  height = 32,
  color = "var(--chart-accent)",
}: {
  values: number[];
  width?: number;
  height?: number;
  color?: string;
}) {
  const id = useId().replace(/:/g, "");
  if (values.length < 2) return null;
  const max = Math.max(1, ...values);
  const pts = values.map(
    (v, i) => [(i / (values.length - 1)) * width, height - 2 - (v / max) * (height - 4)] as [number, number],
  );
  const line = monotonePath(pts);
  return (
    <svg className="sparkline" width={width} height={height} viewBox={`0 0 ${width} ${height}`} aria-hidden>
      <defs>
        <linearGradient id={id} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={`${line} L${width},${height} L0,${height} Z`} fill={`url(#${id})`} />
      <path d={line} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" />
    </svg>
  );
}

/** Batang kemajuan bernada: biru normal, kuning ≥ 70%, merah ≥ 90% bila `warn` aktif. */
export function Meter({
  value,
  max,
  label,
  warn = false,
  tone,
}: {
  value: number;
  max: number;
  label: string;
  warn?: boolean;
  tone?: "info" | "good" | "warn" | "alert";
}) {
  const view = useInView<HTMLDivElement>(0.3);
  const ratio = max > 0 ? Math.min(1, Math.max(0, value / max)) : 0;
  const level = tone ?? (warn && ratio >= 0.9 ? "alert" : warn && ratio >= 0.7 ? "warn" : "info");
  return (
    <div
      ref={view.ref}
      className={cn("meter", "meter--" + level, view.inView && "is-drawn")}
      role="meter"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={value}
    >
      <span className="meter__fill" style={{ width: Math.max(ratio * 100, value > 0 ? 1.5 : 0) + "%" }} />
    </div>
  );
}
