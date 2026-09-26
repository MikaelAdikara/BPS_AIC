import { useState, type CSSProperties } from "react";
import { Star } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import {
  STAR_COLORS,
  averageStars,
  channelLabel,
  sortChannels,
  sumStars,
} from "@/lib/insight-model";
import { Notice } from "@/components/ui";
import { Donut } from "@/components/visual/charts";
import { ChannelDot } from "./IssueMap";

/** Donat sebaran bintang untuk kanal terpilih, ditambah batang 100% per kanal untuk
 * membandingkan kanal satu sama lain dengan skala yang sama. */
export function RatingMix({
  allTime,
  window,
  channel,
}: {
  allTime: Record<string, number[]>;
  window: Record<string, number[]>;
  channel: string;
}) {
  const { t, language } = useI18n();
  const [scope, setScope] = useState<"all" | "window">("all");
  const source = scope === "all" ? allTime : window;
  const counts = sumStars(source, channel);
  const total = counts.reduce((s, v) => s + v, 0);
  const average = averageStars(counts);
  const percent = (value: number) =>
    new Intl.NumberFormat(language, { style: "percent", maximumFractionDigits: 0 }).format(value);
  const channels = sortChannels(Object.keys(source)).filter((c) => sumStars(source, c).some(Boolean));

  return (
    <section className="card rating-card" aria-labelledby="rating-title">
      <header className="card__header">
        <div>
          <h2 className="card__title" id="rating-title">
            <Star size={18} aria-hidden />
            {t("insights.ratingTitle")}
          </h2>
          <p className="muted">{t("insights.ratingLead")}</p>
        </div>
        <div className="segmented segmented--sm" role="group" aria-label={t("insights.ratingTitle")}>
          <button type="button" aria-pressed={scope === "all"} onClick={() => setScope("all")}>
            {t("insights.ratingAll")}
          </button>
          <button type="button" aria-pressed={scope === "window"} onClick={() => setScope("window")}>
            {t("insights.ratingWindow")}
          </button>
        </div>
      </header>
      <div className="card__body">
        {total === 0 ? (
          <Notice tone="muted">{t("insights.ratingEmpty")}</Notice>
        ) : (
          <>
            <Donut
              centerLabel={t("insights.ratingAverage") + " ★"}
              total={average == null ? 0 : Number(average.toFixed(2))}
              slices={[4, 3, 2, 1, 0].map((index) => ({
                key: String(index + 1),
                label: t("insights.star", { count: index + 1 }),
                value: counts[index],
                color: STAR_COLORS[index],
              }))}
            />
            <p className="rating-split">
              <span className="rating-split__low">
                <i style={{ background: STAR_COLORS[0] }} aria-hidden />
                {t("insights.ratingLow", { share: percent((counts[0] + counts[1]) / total) })}
              </span>
              <span>
                <i style={{ background: STAR_COLORS[4] }} aria-hidden />
                {t("insights.ratingHigh", { share: percent((counts[3] + counts[4]) / total) })}
              </span>
            </p>
            {!channel && channels.length > 1 && (
              <ul className="rating-rows">
                {channels.map((c) => {
                  const row = sumStars(source, c);
                  const sum = row.reduce((s, v) => s + v, 0);
                  const avg = averageStars(row);
                  return (
                    <li key={c}>
                      <span className="rating-rows__name">
                        <ChannelDot channel={c} />
                        {channelLabel(c)}
                      </span>
                      <span className="rating-rows__bar" role="img" aria-label={`${channelLabel(c)}: ${row.map((v, i) => `${i + 1}★ ${v}`).join(", ")}`}>
                        {row.map((value, index) =>
                          value ? (
                            <span
                              key={index}
                              title={`${index + 1}★ · ${value}`}
                              style={{ flexGrow: value, background: STAR_COLORS[index] } as CSSProperties}
                            />
                          ) : null,
                        )}
                      </span>
                      <strong className="count">{avg == null ? "—" : avg.toFixed(1)}★</strong>
                      <span className="count muted rating-rows__n">{sum}</span>
                    </li>
                  );
                })}
              </ul>
            )}
          </>
        )}
      </div>
    </section>
  );
}
