import {
  Component,
  Suspense,
  forwardRef,
  lazy,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type ErrorInfo,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
} from "react";
import {
  ArrowRight,
  Eye,
  EyeOff,
  LocateFixed,
  Minus,
  Network,
  Plus,
  Search,
  X,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
import { readPreference, writePreference } from "@/lib/storage.js";
import { issueLink } from "@/lib/workspace-model.js";
import {
  BUCKETS,
  URGENCY,
  bounds,
  buildGroups,
  channelColor,
  channelLabel,
  clipLabel,
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
import {
  hubColor,
  leafColor,
  openIssue,
  type ColorBy,
  type MapCanvasHandle,
  type MapCanvasProps,
  type MapHover,
} from "./map-shared";

const IssueMap3D = lazy(() => import("./IssueMap3D"));

const VIEW_KEY = "deciqo-issue-map-view";

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

/* --- kemampuan perangkat -------------------------------------------------------------------- */

let webglCache: boolean | null = null;
function hasWebGL() {
  if (webglCache != null) return webglCache;
  try {
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl2") ?? canvas.getContext("webgl");
    webglCache = !!gl;
    (gl as WebGLRenderingContext | null)?.getExtension("WEBGL_lose_context")?.loseContext();
  } catch {
    webglCache = false;
  }
  return webglCache;
}

function useMedia(query: string) {
  const [match, setMatch] = useState(() =>
    typeof window !== "undefined" && typeof window.matchMedia === "function" ? window.matchMedia(query).matches : false,
  );
  useEffect(() => {
    if (typeof window.matchMedia !== "function") return;
    const list = window.matchMedia(query);
    const update = () => setMatch(list.matches);
    update();
    list.addEventListener?.("change", update);
    return () => list.removeEventListener?.("change", update);
  }, [query]);
  return match;
}

/** Bila modul 3D atau konteks WebGL gagal, kembali ke peta datar tanpa merusak halaman. */
class Fallback3D extends Component<{ onError(): void; children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: unknown, info: ErrorInfo) {
    console.warn("IssueMap3D failed, falling back to 2D", error, info.componentStack);
    this.props.onError();
  }
  render() {
    return this.state.failed ? null : this.props.children;
  }
}

/* --- pembungkus ----------------------------------------------------------------------------- */

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
  const [colorBy, setColorBy] = useState<ColorBy>("urgency");
  const [query, setQuery] = useState("");
  const [hidden, setHidden] = useState<Set<Bucket>>(() => new Set());
  const [selected, setSelected] = useState<string | null>(null);
  const [focusSeq, setFocusSeq] = useState(0);
  const [hover, setHover] = useState<MapHover | null>(null);
  const [labels, setLabels] = useState(true);
  const [pref, setPref] = useState(() => readPreference(VIEW_KEY, ""));
  const [failed3D, setFailed3D] = useState(false);
  const [webgl] = useState(() => (typeof document !== "undefined" ? hasWebGL() : false));
  const wide = useMedia("(min-width: 768px)");
  const reducedMotion = useMedia("(prefers-reduced-motion: reduce)");
  const stage = useRef<HTMLDivElement>(null);
  const canvas = useRef<MapCanvasHandle>(null);
  const list = useRef<HTMLOListElement>(null);

  const can3D = webgl && wide && !failed3D;
  const use3D = can3D && (pref ? pref === "3d" : !reducedMotion);
  function chooseView(value: "3d" | "2d") {
    setPref(value);
    writePreference(VIEW_KEY, value);
    setHover(null);
  }

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
  const withIssues = useMemo(() => groups.filter((g) => g.findings.length > 0), [groups]);
  const healthy = groupBy === "product" ? groups.length - withIssues.length : 0;
  const active = groups.find((g) => g.key === selected) ?? null;
  const channels = sortChannels(data.channels);
  const channelCounts = useMemo(() => {
    const out: Record<string, number> = {};
    for (const f of filtered) out[f.channel] = (out[f.channel] ?? 0) + 1;
    return out;
  }, [filtered]);
  const rows = active && !withIssues.includes(active) ? [active, ...withIssues] : withIssues;

  useEffect(() => {
    if (selected && !groups.some((g) => g.key === selected)) setSelected(null);
  }, [groups, selected]);
  useEffect(() => setHover(null), [groupBy, channel, needle, hidden, use3D]);

  // Pilihan dari kanvas: gulir daftar (bukan halaman) supaya baris terpilih terlihat.
  useEffect(() => {
    const box = list.current;
    if (!box || !selected) return;
    const row = box.querySelector<HTMLElement>(`[data-key="${CSS.escape(selected)}"]`);
    if (!row) return;
    const top = row.offsetTop - box.offsetTop;
    if (top < box.scrollTop || top + 64 > box.scrollTop + box.clientHeight)
      box.scrollTo({ top: Math.max(0, top - 8), behavior: reducedMotion ? "auto" : "smooth" });
  }, [selected, reducedMotion]);

  const select = useCallback((key: string | null) => setSelected(key), []);
  function selectFromList(key: string) {
    if (selected === key) {
      setSelected(null);
      return;
    }
    setSelected(key);
    setFocusSeq((n) => n + 1);
  }
  function toggleBucket(bucket: Bucket) {
    setHidden((current) => {
      const next = new Set(current);
      if (next.has(bucket)) next.delete(bucket);
      else next.add(bucket);
      return next.size === BUCKETS.length ? new Set() : next;
    });
  }
  function clearFilters() {
    setQuery("");
    setHidden(new Set());
    onChannel("");
  }

  const totalIssues = filtered.length;
  const urgentIssues = filtered.filter((f) => f.bucket === "recurrence").length;
  const summary = t("map3d.summary", { groups: withIssues.length, issues: totalIssues, urgent: urgentIssues });
  const grouping = t("map3d.grouping" + groupBy[0].toUpperCase() + groupBy.slice(1));
  const canvasProps: MapCanvasProps = {
    groups,
    links,
    groupBy,
    colorBy,
    labels,
    selected,
    focusSeq,
    summary,
    reducedMotion,
    onSelect: select,
    onHover: setHover,
  };
  const stageWidth = stage.current?.clientWidth ?? 600;
  const stageHeight = stage.current?.clientHeight ?? 520;

  return (
    <section className="card issue-map map3d" aria-labelledby="issue-map-title">
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
      <div className="issue-map__body map3d-body">
        <div className="map3d-main">
          <p className="map3d-guide">{t(use3D ? "map3d.guide3d" : "map3d.guide2d", { grouping })}</p>
          {failed3D && <p className="map3d-notice" role="status">{t("map3d.failed")}</p>}
          <div className={cn("issue-map__stage map3d-stage", use3D && "is-3d")} ref={stage}>
            {groups.length === 0 ? (
              <div className="issue-map__empty">
                <p>{t("insights.noMatch")}</p>
                <button type="button" className="btn btn--outline btn--sm" onClick={clearFilters}>
                  {t("insights.clearFilters")}
                </button>
              </div>
            ) : use3D ? (
              <Fallback3D onError={() => setFailed3D(true)}>
                <Suspense fallback={<div className="map3d-loading" role="status">{t("map3d.loading")}</div>}>
                  <IssueMap3D ref={canvas} {...canvasProps} />
                </Suspense>
              </Fallback3D>
            ) : (
              <IssueMap2D ref={canvas} {...canvasProps} />
            )}

            <div className="map3d-legend" role="group" aria-labelledby="map3d-legend-title">
              <div className="map3d-legend__head">
                <span className="map3d-legend__title" id="map3d-legend-title">{t("map3d.legendTitle")}</span>
                <div className="map3d-legend__switch" role="group" aria-label={t("insights.colorBy")}>
                  <button type="button" aria-pressed={colorBy === "urgency"} onClick={() => setColorBy("urgency")}>
                    {t("insights.colorUrgency")}
                  </button>
                  <button type="button" aria-pressed={colorBy === "channel"} onClick={() => setColorBy("channel")}>
                    {t("insights.colorChannel")}
                  </button>
                </div>
              </div>
              <ul>
                {colorBy === "urgency"
                  ? BUCKETS.map((bucket) => (
                      <li key={bucket} className={cn(hidden.has(bucket) && "is-off")}>
                        <i style={{ background: URGENCY[bucket].color }} aria-hidden />
                        <span>{t("insights." + URGENCY[bucket].key)}</span>
                        <strong>{counts[bucket]}</strong>
                      </li>
                    ))
                  : channels.map((c) => (
                      <li key={c}>
                        <i style={{ background: channelColor(c) }} aria-hidden />
                        <span>{channelLabel(c)}</span>
                        <strong>{channelCounts[c] ?? 0}</strong>
                      </li>
                    ))}
              </ul>
              {healthy > 0 && (
                <span className="map3d-legend__healthy">
                  <i aria-hidden />
                  {t("insights.healthyProducts", { count: healthy })}
                </span>
              )}
            </div>

            <div className="map3d-tools" role="toolbar" aria-label={t("insights.mapTitle")}>
              {can3D && (
                <div className="map3d-view" role="group" aria-label={t("map3d.viewToggle")}>
                  <button type="button" aria-pressed={use3D} onClick={() => chooseView("3d")} aria-label={t("map3d.show3d")} title={t("map3d.show3d")}>
                    {t("map3d.view3d")}
                  </button>
                  <button type="button" aria-pressed={!use3D} onClick={() => chooseView("2d")} aria-label={t("map3d.show2d")} title={t("map3d.show2d")}>
                    {t("map3d.view2d")}
                  </button>
                </div>
              )}
              <button type="button" onClick={() => canvas.current?.zoomIn()} aria-label={t("insights.zoomIn")} title={t("insights.zoomIn")}>
                <Plus size={17} aria-hidden />
              </button>
              <button type="button" onClick={() => canvas.current?.zoomOut()} aria-label={t("insights.zoomOut")} title={t("insights.zoomOut")}>
                <Minus size={17} aria-hidden />
              </button>
              <button
                type="button"
                onClick={() => {
                  setSelected(null);
                  canvas.current?.fit();
                }}
                aria-label={t("map3d.resetCamera")}
                title={t("map3d.resetCamera")}
              >
                <LocateFixed size={17} aria-hidden />
              </button>
              <button
                type="button"
                aria-pressed={labels}
                onClick={() => setLabels((v) => !v)}
                aria-label={t(labels ? "map3d.labelsOn" : "map3d.labelsOff")}
                title={t(labels ? "map3d.labelsOn" : "map3d.labelsOff")}
              >
                {labels ? <Eye size={17} aria-hidden /> : <EyeOff size={17} aria-hidden />}
              </button>
            </div>

            {hover && (
              <div
                className="map-tip map3d-tip"
                role="status"
                style={{
                  left: Math.max(8, Math.min(hover.x + 16, stageWidth - 256)),
                  top: Math.max(8, Math.min(hover.y + 16, stageHeight - 130)),
                }}
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
                    {hover.group.worst && (
                      <span className="map-tip__badge" style={{ "--tone": urgencyColor(hover.group.worst) } as CSSProperties}>
                        {t("insights." + URGENCY[hover.group.worst].key)}
                      </span>
                    )}
                    <strong>{hover.group.label}</strong>
                    <span className="muted">
                      {hover.group.channel && <ChannelDot channel={hover.group.channel} />}
                      {hover.group.findings.length
                        ? t("insights.issuesCount", { count: hover.group.findings.length })
                        : t("insights.healthy")}
                    </span>
                    {hover.group.product && (
                      <span className="count">{t("insights.reviewsCount", { count: hover.group.product.reviews })}</span>
                    )}
                  </>
                ) : null}
              </div>
            )}
          </div>
        </div>

        <aside className="issue-map__side map3d-side" aria-label={t("insights.topGroups")}>
          <section className="map3d-filters" aria-labelledby="map3d-filters-title">
            <h3 className="map3d-heading" id="map3d-filters-title">{t("map3d.filtersTitle")}</h3>
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
            <div className="map3d-field">
              <span className="map3d-label" id="map3d-urgency-label">{t("insights.urgencyFilter")}</span>
              <div className="filter-chips filter-chips--urgency map3d-urgency" role="group" aria-labelledby="map3d-urgency-label">
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
          </section>

          <section className="map3d-list" aria-labelledby="map3d-list-title">
            <div className="map3d-list__head">
              <h3 className="map3d-heading" id="map3d-list-title">
                {t("map3d.listTitle")}
                {!active && <span className="map3d-list__count">{withIssues.length}</span>}
              </h3>
              {active && (
                <button type="button" className="map3d-clear" onClick={() => setSelected(null)}>
                  <X size={14} aria-hidden />
                  {t("map3d.clearSelection")}
                </button>
              )}
            </div>
            {rows.length === 0 ? (
              <p className="map3d-list__empty muted">{t("map3d.noIssues")}</p>
            ) : (
              <ol className="map3d-rows" ref={list}>
                {rows.map((g) => {
                  const isSelected = g.key === selected;
                  return (
                    <li key={g.key} data-key={g.key} className={cn(isSelected && "is-selected")}>
                      <button
                        type="button"
                        className="map3d-row"
                        aria-expanded={isSelected}
                        aria-controls={isSelected ? "map3d-detail" : undefined}
                        onClick={() => selectFromList(g.key)}
                        title={g.label}
                      >
                        <span className="map3d-row__top">
                          {g.channel ? <ChannelDot channel={g.channel} size={9} /> : <i className="map3d-row__nodot" aria-hidden />}
                          <strong>{g.label}</strong>
                          <span className="map3d-row__count">{g.findings.length}</span>
                        </span>
                        <span className="map3d-row__bar" aria-hidden>
                          {g.findings.length === 0 ? (
                            <span style={{ flexGrow: 1, background: "var(--map-healthy)" }} />
                          ) : (
                            BUCKETS.map((b) =>
                              g.counts[b] ? (
                                <span key={b} style={{ flexGrow: g.counts[b], background: URGENCY[b].color }} />
                              ) : null,
                            )
                          )}
                        </span>
                        {g.worst ? (
                          <span className="map3d-row__meta">
                            <span className="map-tip__badge" style={{ "--tone": URGENCY[g.worst].color } as CSSProperties}>
                              {t("insights." + URGENCY[g.worst].key)}
                            </span>
                            <span className="map3d-row__issue" title={attr(g.findings[0])}>{attr(g.findings[0])}</span>
                          </span>
                        ) : (
                          <span className="map3d-row__meta muted">{t("insights.healthy")}</span>
                        )}
                      </button>
                      {isSelected && g.findings.length > 0 && (
                        <ul className="map-detail__list map3d-detail" id="map3d-detail" aria-label={t("map3d.issuesOf")}>
                          {g.findings.map((f) => (
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
                    </li>
                  );
                })}
              </ol>
            )}
          </section>
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
            {withIssues.map((g) => (
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

/* --- kanvas 2D (SVG) ------------------------------------------------------------------------ */

export const IssueMap2D = forwardRef<MapCanvasHandle, MapCanvasProps>(function IssueMap2D(
  { groups, links, colorBy, labels, selected, focusSeq, summary, onSelect, onHover },
  ref,
) {
  const [view, setView] = useState({ k: 1, x: 0, y: 0 });
  const [stage, setStage] = useState({ w: 0, h: 0 });
  const frame = useRef<HTMLDivElement>(null);
  const drag = useRef<{ x: number; y: number; vx: number; vy: number; moved: boolean } | null>(null);

  const placed = useMemo(() => layout(groups, links), [groups, links]);
  const box = useMemo(() => bounds(placed), [placed]);
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
  // Ruang ekstra di atas untuk legenda dan tombol yang melayang di pojok kanvas.
  const top = 72;
  const vh = Math.max(box.h + pad * 2 + top, stage.h / 1.35);
  const viewBox = `${box.x + box.w / 2 - vw / 2} ${box.y + box.h / 2 - vh / 2 - top / 2} ${vw} ${vh}`;

  useEffect(() => {
    setView({ k: 1, x: 0, y: 0 });
  }, [groups]);

  useImperativeHandle(
    ref,
    () => ({
      zoomIn: () => setView((v) => ({ ...v, k: Math.min(4, v.k * 1.3) })),
      zoomOut: () => setView((v) => ({ ...v, k: Math.max(0.5, v.k / 1.3) })),
      fit: () => setView({ k: 1, x: 0, y: 0 }),
    }),
    [],
  );

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

  // Pilihan dari daftar samping: geser peta ke hub itu.
  useEffect(() => {
    if (!focusSeq || !selected) return;
    const target = placed.find((p) => p.group.key === selected);
    if (!target) return;
    const cx = box.x + box.w / 2;
    const cy = box.y + box.h / 2;
    setView((v) => ({ k: Math.max(1.6, v.k), x: cx - target.x, y: cy - target.y }));
    // hanya saat permintaan fokus baru
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusSeq]);

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
    onHover(null);
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
    onHover({ ...payload, x: event.clientX - rect.left, y: event.clientY - rect.top });
  }
  const dimmed = (g: Group) => active != null && active.key !== g.key;
  const cx = box.x + box.w / 2;
  const cy = box.y + box.h / 2;
  const transform = `translate(${cx} ${cy}) scale(${view.k}) translate(${-cx + view.x} ${-cy + view.y})`;

  return (
    <div className="map3d-canvas" ref={frame}>
      <svg
        className={cn("issue-map__svg", drag.current?.moved && "is-dragging")}
        viewBox={viewBox}
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label={summary}
        onPointerDown={down}
        onPointerMove={move}
        onPointerUp={up}
        onPointerCancel={up}
        onPointerLeave={() => onHover(null)}
        onClick={(event) => {
          if (event.target === event.currentTarget && !drag.current?.moved) onSelect(null);
        }}
      >
        <g transform={transform}>
          <g className={cn("map-links", active && "has-active")}>
            {links.map(([a, b]) => {
              const pa = placed[a];
              const pb = placed[b];
              if (!pa || !pb) return null;
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
                    fill={leafColor(leaf.finding, colorBy)}
                    onPointerEnter={(event) => tip(event, { finding: leaf.finding })}
                    onPointerMove={(event) => tip(event, { finding: leaf.finding })}
                    onPointerLeave={() => onHover(null)}
                    onClick={(event) => {
                      event.stopPropagation();
                      if (!drag.current?.moved) openIssue(leaf.finding);
                    }}
                  />
                ))}
                <circle
                  className="map-hub"
                  cx={p.x}
                  cy={p.y}
                  r={p.r}
                  fill={hubColor(p.group, colorBy)}
                  onPointerEnter={(event) => tip(event, { group: p.group })}
                  onPointerMove={(event) => tip(event, { group: p.group })}
                  onPointerLeave={() => onHover(null)}
                  onClick={(event) => {
                    event.stopPropagation();
                    if (!drag.current?.moved) onSelect(selected === p.group.key ? null : p.group.key);
                  }}
                />
                {labelled.has(p.group.key) && (
                  <text className="map-label map3d-label2d" x={p.x} y={p.y - p.ring + 2} textAnchor="middle">
                    {clipLabel(p.group.label)}
                    <title>{p.group.label}</title>
                  </text>
                )}
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
});
