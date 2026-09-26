import { useEffect, useId, useRef, useState } from "react";
import { CalendarDays, ChevronDown } from "lucide-react";
import { DayPicker, type DateRange } from "react-day-picker";
import { enGB, id as idLocale } from "react-day-picker/locale";
import "react-day-picker/style.css";
import { useI18n } from "@/lib/i18n";

/** Rentang aktif: preset hari (7/30/90), "all" dari ulasan tertua, atau tanggal pilihan (inklusif). */
export type RangeValue = { preset: 7 | 30 | 90 | "all" } | { start: string; end: string };
export interface ResolvedRange {
  start: string;
  end: string;
  days: number;
  all?: boolean;
}
export const MAX_RANGE_DAYS = 730;
const PRESETS = [7, 30, 90, "all"] as const;

function pad(value: number) {
  return String(value).padStart(2, "0");
}
export function isoDay(date: Date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}
function fromIso(value: string) {
  const [y, m, d] = value.split("-").map(Number);
  return new Date(y, m - 1, d);
}
function shift(value: Date, days: number) {
  const next = new Date(value);
  next.setDate(next.getDate() + days);
  return next;
}

/** Query string untuk GET /deciqo/overview. */
export function rangeQuery(value: RangeValue) {
  if ("start" in value) return `start=${value.start}&end=${value.end}`;
  return value.preset === "all" ? "all=true" : `days=${value.preset}`;
}

/** "28 Aug – 26 Sep 2026" / "28 Agu – 26 Sep 2026". Nama bulan dari messages agar tidak
 * bergantung pada versi ICU peramban (en-GB kini menulis "Sept"). */
export function formatRange(start: string, end: string, months: string[]) {
  const a = fromIso(start);
  const b = fromIso(end);
  const day = (d: Date) => `${d.getDate()} ${months[d.getMonth()]}`;
  const full = (d: Date) => `${day(d)} ${d.getFullYear()}`;
  if (start === end) return full(b);
  return a.getFullYear() === b.getFullYear() ? `${day(a)} – ${full(b)}` : `${full(a)} – ${full(b)}`;
}

function useWide(query = "(min-width: 720px)") {
  const [wide, setWide] = useState(() => typeof window !== "undefined" && window.matchMedia(query).matches);
  useEffect(() => {
    const media = window.matchMedia(query);
    const update = () => setWide(media.matches);
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, [query]);
  return wide;
}

/** Tanggal yang sedang berlaku. Server menang bila jawabannya cocok dengan pilihan; selama
 * memuat, tanggal dihitung di klien supaya label tidak menunjukkan rentang lama. */
export function activeRange(value: RangeValue, resolved?: ResolvedRange | null): { start: string; end: string } | null {
  if ("start" in value) return value;
  if (value.preset === "all") return resolved?.all ? resolved : null;
  if (resolved && !resolved.all && resolved.days === value.preset) return resolved;
  const today = new Date();
  return { start: isoDay(shift(today, 1 - value.preset)), end: isoDay(today) };
}

export function DateRangeControl({
  value,
  onChange,
  resolved,
}: {
  value: RangeValue;
  onChange: (value: RangeValue) => void;
  resolved?: ResolvedRange | null;
}) {
  const { t, language } = useI18n();
  const months = t("overview.monthsShort").split(",");
  const wide = useWide();
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<DateRange | undefined>();
  const root = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const dialogId = useId();
  const current = activeRange(value, resolved);
  const label = current ? formatRange(current.start, current.end, months) : t("overview.rangeAll");
  const today = new Date();

  function close(focus = true) {
    setOpen(false);
    if (focus) trigger.current?.focus();
  }
  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent) => {
      if (root.current && !root.current.contains(event.target as Node)) close(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        close();
      }
    };
    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  function toggle() {
    if (open) return close();
    const next = current ? { from: fromIso(current.start), to: fromIso(current.end) } : undefined;
    const anchor = next?.to ?? today;
    setDraft(next);
    setMonth(new Date(anchor.getFullYear(), anchor.getMonth() - (monthCount - 1), 1));
    setOpen(true);
  }
  /** Tanggal diketik langsung: batas bawah/atas ditukar bila terbalik, masa depan dipotong ke hari ini. */
  function typed(edge: "from" | "to", raw: string) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(raw)) return;
    let day = fromIso(raw);
    if (day > today) day = today;
    let from = edge === "from" ? day : draft?.from ?? day;
    let to = edge === "to" ? day : draft?.to ?? draft?.from ?? day;
    if (from > to) [from, to] = [to, from];
    const earliest = shift(to, 1 - MAX_RANGE_DAYS);
    if (from < earliest) from = earliest;
    setDraft({ from, to });
    setMonth(new Date(to.getFullYear(), to.getMonth() - (monthCount - 1), 1));
  }
  function apply() {
    if (!draft?.from) return;
    onChange({ start: isoDay(draft.from), end: isoDay(draft.to ?? draft.from) });
    close();
  }
  const monthCount = wide ? 2 : 1;
  const [month, setMonth] = useState<Date>(today);

  return (
    <div className="date-range" ref={root}>
      <div className="segmented" role="group" aria-label={t("overview.days")}>
        {PRESETS.map((preset) => (
          <button
            key={preset}
            type="button"
            aria-pressed={"preset" in value && value.preset === preset}
            onClick={() => onChange({ preset })}
          >
            {preset === "all" ? t("overview.rangeAll") : t("overview.dayOption", { count: preset })}
          </button>
        ))}
      </div>
      <button
        ref={trigger}
        type="button"
        className="date-range__trigger"
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls={open ? dialogId : undefined}
        aria-label={t("overview.rangePick", { range: label })}
        data-custom={"start" in value || undefined}
        onClick={toggle}
      >
        <CalendarDays size={16} aria-hidden />
        <span className="date-range__label">{label}</span>
        <ChevronDown size={14} aria-hidden className="date-range__chev" />
      </button>
      {open && (
        <div className="date-range__pop" id={dialogId} role="dialog" aria-label={t("overview.rangeDialog")}>
          <DayPicker
            mode="range"
            autoFocus
            locale={language === "id" ? idLocale : enGB}
            numberOfMonths={monthCount}
            month={month}
            onMonthChange={setMonth}
            endMonth={today}
            disabled={{ after: today }}
            excludeDisabled
            max={MAX_RANGE_DAYS - 1}
            selected={draft}
            onSelect={setDraft}
          />
          <div className="date-range__inputs">
            <label>
              <span>{t("overview.rangeFrom")}</span>
              <input
                type="date"
                value={draft?.from ? isoDay(draft.from) : ""}
                max={isoDay(today)}
                onChange={(event) => typed("from", event.target.value)}
              />
            </label>
            <label>
              <span>{t("overview.rangeTo")}</span>
              <input
                type="date"
                value={draft?.to ? isoDay(draft.to) : draft?.from ? isoDay(draft.from) : ""}
                max={isoDay(today)}
                onChange={(event) => typed("to", event.target.value)}
              />
            </label>
          </div>
          <div className="date-range__foot">
            <p className="muted">
              {draft?.from
                ? formatRange(isoDay(draft.from), isoDay(draft.to ?? draft.from), months)
                : t("overview.rangeHint", { count: MAX_RANGE_DAYS })}
            </p>
            <div className="date-range__actions">
              <button type="button" className="btn btn--text btn--sm" onClick={() => close()}>
                {t("overview.rangeCancel")}
              </button>
              <button type="button" className="btn btn--primary btn--sm" disabled={!draft?.from} onClick={apply}>
                {t("overview.rangeApply")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
