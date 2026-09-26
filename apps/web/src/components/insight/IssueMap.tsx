import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
} from "react";
import {
  ArrowRight,
  Eye,
  EyeOff,
  Maximize,
  Minus,
  Network,
  Plus,
  Search,
  X,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
import { issueLink } from "@/lib/workspace-model.js";
import {
  BUCKETS,
  URGENCY,
  bounds,
  buildGroups,
  channelColor,
  channelLabel,
  layout,
  pickLabels,
  sharedLinks,
  sortChannels,
  urgencyColor,
  type Bucket,
  type Group,
  type GroupBy,
  type Landscape,
  type MapFinding,
} from "@/lib/insight-model";
import { Table } from "@/components/ui";

const typeKeys: Record<string, string> = {
  missing_fact: "typeMissingFact",
  unclear_fact: "typeUnclearWording",
  unclear_wording: "typeUnclearWording",
  conflicting_fact: "typeListingConflict",
  listing_conflict: "typeListingConflict",
  expectation_mismatch: "typeExpectationGap",
  expectation_gap: "typeExpectationGap",
  product_quality: "typeQuality",
  operational: "typeOperations",
  operations: "typeOperations",
};

function clip(text: string, max = 22) {
  return text.length > max ? text.slice(0, max - 1).trimEnd() + "…" : text;
}

export function ChannelDot({ channel, size = 8 }: { channel: string; size?: number }) {
  return (
    <i
      className="channel-swatch"
      style={{ background: channelColor(channel), width: size, height: size }}
      aria-hidden
    />
  );
}

export function UrgencyLegend({ counts }: { counts?: Record<Bucket, number> }) {
  const { t } = useI18n();
  return (
    <ul className="urgency-legend" aria-label={t("insights.urgencyLegend")}>
      {BUCKETS.map((bucket) => (
        <li key={bucket}>
          <i style={{ background: URGENCY[bucket].color }} aria-hidden />
          <span>{t("insights." + URGENCY[bucket].key)}</span>
          {counts && <strong className="count">{counts[bucket]}</strong>}
        </li>
      ))}
    </ul>
  );
}

export function IssueMap({
  data,
  channel,
  onChannel,
}: {
  data: Landscape;
  channel: string;
  onChannel: (value: string) => void;
}) {
  const { t, language } = useI18n();
  const [groupBy, setGroupBy] = useState<GroupBy>("product");
  const [colorBy, setColorBy] = useState<"urgency" | "channel">("urgency");
  const [query, setQuery] = useState("");
  const [hidden, setHidden] = useState<Set<Bucket>>(() => new Set());
  const [selected, setSelected] = useState<string | null>(null);
  const [hover, setHover] = useState<{ finding?: MapFinding; group?: Group; x: number; y: number } | null>(null);
  const [labels, setLabels] = useState(true);
  const [view, setView] = useState({ k: 1, x: 0, y: 0 });
  const [stage, setStage] = useState({ w: 0, h: 0 });
  const frame = useRef<HTMLDivElement>(null);
  const drag = useRef<{ x: number; y: number; vx: number; vy: number; moved: boolean } | null>(null);

  const attr = (f: MapFinding) => (language === "id" ? f.attribute_local : f.attribute) || f.attribute;
  const groupLabel = (kind: GroupBy, key: string) =>
    kind === "aspect" ? t("insights.aspect_" + key)
      : kind === "type" ? t("workspace." + (typeKeys[key] ?? "typeOperations"))
      : kind === "channel" ? channelLabel(key)
      : key;

  const needle = query.trim().toLowerCase();
  const scoped = useMemo(
    () => data.map.findings.filter((f) => !channel || f.channel === channel),
    [data, channel],
  );
  const filtered = useMemo(
    () =>
      scoped.filter(
        (f) =>
          !hidden.has(f.bucket as Bucket) &&
          (!needle || (f.product_title + " " + f.attribute + " " + f.attribute_local).toLowerCase().includes(needle)),
      ),
    [scoped, hidden, needle],
  );
  const products = useMemo(
    () =>
      data.map.products.filter(
        (p) => (!channel || p.channel === channel) && (!needle || p.title.toLowerCase().includes(needle)),
      ),
    [data, channel, needle],
  );
  const counts = useMemo(() => {
    const out: Record<Bucket, number> = { recurrence: 0, needs_fact: 0, to_do: 0, monitoring: 0 };
    for (const f of scoped) if (f.bucket in out) out[f.bucket as Bucket] += 1;
    return out;
  }, [scoped]);
  const groups = useMemo(
    () => buildGroups(filtered, products, groupBy, groupLabel, hidden.size === 0),
    // label bergantung bahasa
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [filtered, products, groupBy, language],
  );
  const links = useMemo(() => sharedLinks(groups, groupBy), [groups, groupBy]);
  const placed = useMemo(() => layout(groups, links), [groups, links]);
  const box = useMemo(() => bounds(placed), [placed]);
  const healthy = groupBy === "product" ? groups.filter((g) => g.findings.length === 0).length : 0;
  const active = groups.find((g) => g.key === selected) ?? null;
  const labelled = pickLabels(
    placed,
    new Set(labels ? groups.filter((g) => g.findings.length > 0).slice(0, 16).map((g) => g.key) : []),
  );
  if (active) labelled.add(active.key);
  const pad = 30;
  // Satu unit tata letak tidak pernah lebih dari ~1px: peta kecil tetap berukuran wajar,
  // peta besar diperkecil agar muat.
  const vw = Math.max(box.w + pad * 2, stage.w / 1.35);
  const vh = Math.max(box.h + pad * 2, stage.h / 1.35);
  const viewBox = `${box.x + box.w / 2 - vw / 2} ${box.y + box.h / 2 - vh / 2} ${vw} ${vh}`;

  useEffect(() => {
    setView({ k: 1, x: 0, y: 0 });
  }, [groupBy, channel, needle, hidden]);
  useEffect(() => {
    if (selected && !groups.some((g) => g.key === selected)) setSelected(null);
  }, [groups, selected]);

  useEffect(() => {
    const el = frame.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(([entry]) =>
      setStage({ w: entry.contentRect.width, h: entry.contentRect.height }),
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Zoom roda hanya dengan Ctrl/⌘ (atau cubit trackpad) supaya scroll halaman tidak tertahan.
  useEffect(() => {
    const el = frame.current;
    if (!el) return;
    const wheel = (event: WheelEvent) => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault();
      setView((v) => ({ ...v, k: Math.min(4, Math.max(0.5, v.k * Math.exp(-event.deltaY * 0.0025))) }));
    };
    el.addEventListener("wheel", wheel, { passive: false });
    return () => el.removeEventListener("wheel", wheel);
  }, []);

  function scale() {
    const el = frame.current;
    if (!el) return 1;
    const rect = el.getBoundingClientRect();
    return Math.max(vw / rect.width, vh / rect.height);
  }
  function down(event: ReactPointerEvent<SVGSVGElement>) {
    if (event.button !== 0) return;
    drag.current = { x: event.clientX, y: event.clientY, vx: view.x, vy: view.y, moved: false };
  }
  function move(event: ReactPointerEvent<SVGSVGElement>) {
    const d = drag.current;
    if (!d) return;
    const dx = event.clientX - d.x;
    const dy = event.clientY - d.y;
    if (!d.moved && Math.hypot(dx, dy) < 4) return;
    if (!d.moved) event.currentTarget.setPointerCapture(event.pointerId);
    d.moved = true;
    setHover(null);
    const s = scale();
    setView((v) => ({ ...v, x: d.vx + (dx * s) / v.k, y: d.vy + (dy * s) / v.k }));
  }
  function up() {
    setTimeout(() => (drag.current = null), 0);
  }
  function tip(event: { clientX: number; clientY: number }, payload: { finding?: MapFinding; group?: Group }) {
    if (drag.current?.moved) return;
    const rect = frame.current?.getBoundingClientRect();
    if (!rect) return;
    setHover({ ...payload, x: event.clientX - rect.left, y: event.clientY - rect.top });
  }
  function focus(key: string) {
    setSelected(key);
    const target = placed.find((p) => p.group.key === key);
    if (!target) return;
    const cx = box.x + box.w / 2;
    const cy = box.y + box.h / 2;
    const k = Math.max(1.6, view.k);
    setView({ k, x: cx - target.x, y: cy - target.y });
  }
  function toggleBucket(bucket: Bucket) {
    setHidden((current) => {
      const next = new Set(current);
      if (next.has(bucket)) next.delete(bucket);
      else next.add(bucket);
      return next.size === BUCKETS.length ? new Set() : next;
    });
  }
  const leafColor = (f: MapFinding) => (colorBy === "urgency" ? urgencyColor(f.bucket) : channelColor(f.channel));
  const hubColor = (g: Group) =>
    g.kind === "product"
      ? colorBy === "channel" && g.channel
        ? channelColor(g.channel)
        : g.worst
          ? urgencyColor(g.worst)
          : "var(--map-healthy)"
      : g.kind === "channel"
        ? channelColor(g.key)
        : "var(--map-hub)";
  const dimmed = (g: Group) => active != null && active.key !== g.key;
  const cx = box.x + box.w / 2;
  const cy = box.y + box.h / 2;
  const transform = `translate(${cx} ${cy}) scale(${view.k}) translate(${-cx + view.x} ${-cy + view.y})`;
  const channels = sortChannels(data.channels);

  return (
    <section className="card issue-map" aria-labelledby="issue-map-title">
      <header className="issue-map__head">
        <div>
          <h2 className="card__title" id="issue-map-title">
            <Network size={18} aria-hidden />
            {t("insights.mapTitle")}
          </h2>
          <p className="muted">{t("insights.mapLead")}</p>
        </div>
        <div className="issue-map__switches">
          <div className="segmented segmented--sm" role="group" aria-label={t("insights.groupBy")}>
            {(["product", "aspect", "type", "channel"] as GroupBy[]).map((value) => (
              <button key={value} type="button" aria-pressed={groupBy === value} onClick={() => setGroupBy(value)}>
                {t("insights.group" + value[0].toUpperCase() + value.slice(1))}
              </button>
            ))}
          </div>
        </div>
      </header>
      <div className="issue-map__body">
        <div className="issue-map__stage" ref={frame}>
          <div className="map-tools" role="toolbar" aria-label={t("insights.mapTitle")}>
            <button type="button" onClick={() => setView((v) => ({ ...v, k: Math.min(4, v.k * 1.3) }))} aria-label={t("insights.zoomIn")} title={t("insights.zoomIn")}>
              <Plus size={16} aria-hidden />
            </button>
            <button type="button" onClick={() => setView((v) => ({ ...v, k: Math.max(0.5, v.k / 1.3) }))} aria-label={t("insights.zoomOut")} title={t("insights.zoomOut")}>
              <Minus size={16} aria-hidden />
            </button>
            <button type="button" onClick={() => { setView({ k: 1, x: 0, y: 0 }); setSelected(null); }} aria-label={t("insights.fit")} title={t("insights.fit")}>
              <Maximize size={15} aria-hidden />
            </button>
            <button type="button" aria-pressed={labels} onClick={() => setLabels((v) => !v)} aria-label={t("insights.labels")} title={t("insights.labels")}>
              {labels ? <Eye size={16} aria-hidden /> : <EyeOff size={16} aria-hidden />}
            </button>
          </div>
          {placed.length === 0 ? (
            <div className="issue-map__empty">
              <p>{t("insights.noMatch")}</p>
              <button type="button" className="btn btn--outline btn--sm" onClick={() => { setQuery(""); setHidden(new Set()); onChannel(""); }}>
                {t("insights.clearFilters")}
              </button>
            </div>
          ) : (
            <svg
              className={cn("issue-map__svg", drag.current?.moved && "is-dragging")}
              viewBox={viewBox}
              preserveAspectRatio="xMidYMid meet"
              role="img"
              aria-label={t("insights.mapTitle")}
              onPointerDown={down}
              onPointerMove={move}
              onPointerUp={up}
              onPointerCancel={up}
              onPointerLeave={() => setHover(null)}
              onClick={(event) => {
                if (event.target === event.currentTarget && !drag.current?.moved) setSelected(null);
              }}
            >
              <g transform={transform}>
                <g className="map-links">
                  {links.map(([a, b]) => {
                    const pa = placed[a];
                    const pb = placed[b];
                    const lit = active && (active.key === pa.group.key || active.key === pb.group.key);
                    return (
                      <line key={a + "-" + b} x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y} className={cn(lit && "is-lit")} />
                    );
                  })}
                </g>
                {placed.map((p, index) => {
                  const dim = dimmed(p.group);
                  return (
                    <g
                      key={p.group.key}
                      className={cn("map-cluster", dim && "is-dim", active?.key === p.group.key && "is-active")}
                      style={{ "--i": Math.min(index, 30) } as CSSProperties}
                    >
                      {p.leaves.map((leaf) => (
                        <line key={"s" + leaf.finding.id} className="map-spoke" x1={p.x} y1={p.y} x2={p.x + leaf.x} y2={p.y + leaf.y} />
                      ))}
                      {p.leaves.map((leaf) => (
                        <circle
                          key={leaf.finding.id}
                          className={cn("map-leaf", leaf.finding.bucket === "recurrence" && "is-urgent")}
                          cx={p.x + leaf.x}
                          cy={p.y + leaf.y}
                          r={leaf.r}
                          fill={leafColor(leaf.finding)}
                          onPointerEnter={(event) => tip(event, { finding: leaf.finding })}
                          onPointerMove={(event) => tip(event, { finding: leaf.finding })}
                          onPointerLeave={() => setHover(null)}
                          onClick={(event) => {
                            event.stopPropagation();
                            if (!drag.current?.moved) window.location.hash = issueLink(leaf.finding).slice(1);
                          }}
                        />
                      ))}
                      <circle
                        className="map-hub"
                        cx={p.x}
                        cy={p.y}
                        r={p.r}
                        fill={hubColor(p.group)}
                        onPointerEnter={(event) => tip(event, { group: p.group })}
                        onPointerMove={(event) => tip(event, { group: p.group })}
                        onPointerLeave={() => setHover(null)}
                        onClick={(event) => {
                          event.stopPropagation();
                          if (!drag.current?.moved) setSelected((s) => (s === p.group.key ? null : p.group.key));
                        }}
                      />
                      {labelled.has(p.group.key) && (
                        <text className="map-label" x={p.x} y={p.y - p.ring + 2} textAnchor="middle">
                          {clip(p.group.label)}
                        </text>
                      )}
                    </g>
                  );
                })}
              </g>
            </svg>
          )}
          <div className="map-legend">
            {colorBy === "urgency" ? (
              <UrgencyLegend />
            ) : (
              <ul className="urgency-legend">
                {channels.map((c) => (
                  <li key={c}>
                    <i style={{ background: channelColor(c) }} aria-hidden />
                    <span>{channelLabel(c)}</span>
                  </li>
                ))}
              </ul>
            )}
            {healthy > 0 && (
              <span className="map-legend__healthy">
                <i aria-hidden />
                {t("insights.healthyProducts", { count: healthy })}
              </span>
            )}
          </div>
          <p className="map-hint muted">{t("insights.mapKeys")}</p>
          {hover && (
            <div
              className="map-tip"
              role="status"
              style={{ left: Math.min(hover.x + 14, (frame.current?.clientWidth ?? 400) - 250), top: hover.y + 14 }}
            >
              {hover.finding ? (
                <>
                  <span className="map-tip__badge" style={{ "--tone": urgencyColor(hover.finding.bucket) } as CSSProperties}>
                    {t("insights." + (URGENCY[hover.finding.bucket as Bucket]?.key ?? "ready"))}
                  </span>
                  <strong>{attr(hover.finding)}</strong>
                  <span className="muted">
                    <ChannelDot channel={hover.finding.channel} /> {hover.finding.product_title}
                  </span>
                  <span className="count">{t("insights.reviewsCount", { count: hover.finding.support })}</span>
                </>
              ) : hover.group ? (
                <>
                  <strong>{hover.group.label}</strong>
                  <span className="muted">
                    {hover.group.findings.length
                      ? t("insights.issuesCount", { count: hover.group.findings.length })
                      : t("insights.healthy")}
                    {hover.group.product && " · " + t("insights.reviewsCount", { count: hover.group.product.reviews })}
                  </span>
                </>
              ) : null}
            </div>
          )}
        </div>
        <aside className="issue-map__side" aria-label={t("insights.topGroups")}>
          <div className="map-side__head">
            <h3>{active ? t("insights.selected") : t("insights.topGroups")}</h3>
            {active ? (
              <button type="button" className="map-side__close" onClick={() => setSelected(null)} aria-label={t("insights.close")}>
                <X size={16} aria-hidden />
              </button>
            ) : (
              <span className="muted">{t("insights.sortedUrgency")}</span>
            )}
          </div>
          <label className="map-search">
            <Search size={15} aria-hidden />
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={t("insights.search")}
              aria-label={t("insights.search")}
            />
          </label>
          <div className="filter-chips" role="group" aria-label={t("insights.filterTitle")}>
            <button type="button" aria-pressed={!channel} onClick={() => onChannel("")}>
              {t("insights.allChannels")}
            </button>
            {channels.map((c) => (
              <button key={c} type="button" aria-pressed={channel === c} onClick={() => onChannel(channel === c ? "" : c)}>
                <ChannelDot channel={c} />
                {channelLabel(c)}
              </button>
            ))}
          </div>
          <div className="map-side__row">
            <span className="map-side__label">{t("insights.urgencyFilter")}</span>
            <div className="filter-chips filter-chips--urgency" role="group" aria-label={t("insights.urgencyFilter")}>
              {BUCKETS.map((bucket) => (
                <button
                  key={bucket}
                  type="button"
                  aria-pressed={!hidden.has(bucket)}
                  onClick={() => toggleBucket(bucket)}
                  style={{ "--tone": URGENCY[bucket].color } as CSSProperties}
                  title={t("insights." + URGENCY[bucket].hint)}
                >
                  <i aria-hidden />
                  {t("insights." + URGENCY[bucket].key)}
                  <span className="count">{counts[bucket]}</span>
                </button>
              ))}
            </div>
          </div>
          <div className="map-side__row">
            <span className="map-side__label">{t("insights.colorBy")}</span>
            <div className="segmented segmented--sm" role="group" aria-label={t("insights.colorBy")}>
              <button type="button" aria-pressed={colorBy === "urgency"} onClick={() => setColorBy("urgency")}>
                {t("insights.colorUrgency")}
              </button>
              <button type="button" aria-pressed={colorBy === "channel"} onClick={() => setColorBy("channel")}>
                {t("insights.colorChannel")}
              </button>
            </div>
          </div>
          {active ? (
            <div className="map-detail">
              <p className="map-detail__title">
                {active.channel && <ChannelDot channel={active.channel} size={10} />}
                <strong>{active.label}</strong>
              </p>
              <UrgencyLegend counts={active.counts} />
              {active.findings.length === 0 ? (
                <p className="muted">{t("insights.healthy")}</p>
              ) : (
                <ul className="map-detail__list">
                  {active.findings.map((f) => (
                    <li key={f.id}>
                      <a href={issueLink(f)}>
                        <i style={{ background: urgencyColor(f.bucket) }} aria-hidden />
                        <span>
                          <strong>{attr(f)}</strong>
                          <small className="muted">
                            {groupBy === "product" ? channelLabel(f.channel) : f.product_title} ·{" "}
                            {t("insights.reviewsCount", { count: f.support })}
                          </small>
                        </span>
                        <ArrowRight size={14} aria-hidden />
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <ol className="map-rank">
              {groups
                .filter((g) => g.findings.length > 0)
                .slice(0, 8)
                .map((g) => (
                  <li key={g.key}>
                    <button type="button" onClick={() => focus(g.key)} title={t("insights.focus")}>
                      <span className="map-rank__top">
                        {g.channel && <ChannelDot channel={g.channel} />}
                        <strong>{g.label}</strong>
                        <span className="count muted">{t("insights.issuesCount", { count: g.findings.length })}</span>
                      </span>
                      <span className="map-rank__bar" aria-hidden>
                        {BUCKETS.map((b) =>
                          g.counts[b] ? (
                            <span key={b} style={{ flexGrow: g.counts[b], background: URGENCY[b].color }} />
                          ) : null,
                        )}
                      </span>
                      {g.worst && (
                        <span className="map-rank__meta">
                          <span className="map-tip__badge" style={{ "--tone": URGENCY[g.worst].color } as CSSProperties}>
                            {t("insights." + URGENCY[g.worst].key)}
                          </span>
                          <span className="muted">{attr(g.findings[0])}</span>
                        </span>
                      )}
                    </button>
                  </li>
                ))}
            </ol>
          )}
        </aside>
      </div>
      <details className="issue-map__table">
        <summary>{t("insights.mapTable")}</summary>
        <Table>
          <thead>
            <tr>
              <th scope="col">{t("insights.group")}</th>
              {BUCKETS.map((b) => (
                <th scope="col" key={b}>{t("insights." + URGENCY[b].key)}</th>
              ))}
              <th scope="col">{t("insights.worst")}</th>
            </tr>
          </thead>
          <tbody>
            {groups.filter((g) => g.findings.length).map((g) => (
              <tr key={g.key}>
                <td>{g.label}</td>
                {BUCKETS.map((b) => (
                  <td className="count" key={b}>{g.counts[b]}</td>
                ))}
                <td>{attr(g.findings[0])}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      </details>
    </section>
  );
}
