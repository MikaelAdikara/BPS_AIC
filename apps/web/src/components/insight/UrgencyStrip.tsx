import type { CSSProperties } from "react";
import { useI18n } from "@/lib/i18n";
import { BUCKETS, URGENCY, type Bucket } from "@/lib/insight-model";

/** Batang 100% komposisi urgensi; tiap segmen dan legendanya membuka tab isu yang sesuai. */
export function UrgencyStrip({
  items,
  active,
  onSelect,
}: {
  items: { bucket: string }[];
  active?: string;
  onSelect: (bucket: Bucket) => void;
}) {
  const { t } = useI18n();
  const counts = BUCKETS.map((b) => items.filter((i) => i.bucket === b).length);
  const total = counts.reduce((s, v) => s + v, 0);
  if (!total) return null;
  return (
    <div className="urgency-strip">
      <div className="urgency-strip__bar" role="img" aria-label={t("insights.urgencyLegend")}>
        {BUCKETS.map((b, i) =>
          counts[i] ? (
            <span
              key={b}
              style={{ flexGrow: counts[i], background: URGENCY[b].color } as CSSProperties}
              title={`${t("insights." + URGENCY[b].key)} · ${counts[i]}`}
            />
          ) : null,
        )}
      </div>
      <div className="urgency-strip__keys">
        {BUCKETS.map((b, i) => (
          <button
            key={b}
            type="button"
            aria-pressed={active === b}
            disabled={!counts[i]}
            onClick={() => onSelect(b)}
            style={{ "--tone": URGENCY[b].color } as CSSProperties}
          >
            <i aria-hidden />
            <span>
              <strong>{t("insights." + URGENCY[b].key)}</strong>
              <small>{t("insights." + URGENCY[b].hint)}</small>
            </span>
            <b className="count">{counts[i]}</b>
          </button>
        ))}
      </div>
    </div>
  );
}
