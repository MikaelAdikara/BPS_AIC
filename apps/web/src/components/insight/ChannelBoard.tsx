import type { CSSProperties, ReactNode } from "react";
import { Database, Download, Globe, Link2, Plug, Upload } from "lucide-react";
import type { Channel } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { channelColor, channelLabel } from "@/lib/insight-model";
import { Button } from "@/components/ui";

const MODE: Record<string, { key: string; icon: typeof Plug }> = {
  woocommerce: { key: "modeApi", icon: Plug },
  lazada: { key: "modeFetch", icon: Link2 },
};
const STATUS: Record<string, { key: string; tone: string }> = {
  connected: { key: "sourceConnected", tone: "var(--status-good)" },
  stale: { key: "sourceStale", tone: "var(--status-warning)" },
  unavailable: { key: "sourceUnavailable", tone: "var(--status-critical)" },
  disconnected: { key: "sourceDisconnected", tone: "var(--muted)" },
  no_data: { key: "sourceNoData", tone: "var(--muted)" },
  not_checked: { key: "sourceNotChecked", tone: "var(--muted)" },
};

export function SamplingBadge({ kind }: { kind: string }) {
  const { t } = useI18n();
  const known = ["complete", "random", "skewed", "unknown"].includes(kind) ? kind : "unknown";
  return (
    <span className={"sampling-badge sampling-badge--" + known} title={t("sources.samplingHint_" + known)}>
      {t("sources.sampling_" + known)}
    </span>
  );
}

function Stat({ label, value, alert, muted, title }: { label: string; value: ReactNode; alert?: boolean; muted?: boolean; title?: string }) {
  return (
    <span className={"channel-card__stat" + (alert ? " is-alert" : "") + (muted ? " is-muted" : "")} title={title}>
      <strong className="count">{value}</strong>
      <small>{label}</small>
    </span>
  );
}

/** Kartu per kanal yang juga berfungsi sebagai tab: status berwarna, volume, dan isu terbuka.
 * Setiap kartu punya empat slot angka yang sama (unit terjual "—" abu bila tidak dilaporkan)
 * dan footer tetap di bawah, sehingga kartu dalam satu baris sejajar. */
export function ChannelBoard({
  keys,
  channels,
  active,
  onSelect,
}: {
  keys: string[];
  channels: Channel[];
  active: string;
  onSelect: (key: string) => void;
}) {
  const { t, language } = useI18n();
  const number = (value: number) => new Intl.NumberFormat(language).format(value);
  return (
    <section className="channel-board" aria-labelledby="channel-board-title">
      <div className="channel-board__head">
        <h2 id="channel-board-title">{t("sources.boardTitle")}</h2>
        <p className="muted">{t("sources.boardLead")}</p>
      </div>
      <div className="channel-board__grid" role="group" aria-labelledby="channel-board-title">
        {keys.map((key) => {
          const channel = channels.find((c) => c.key === key);
          const mode = MODE[key] ?? { key: "modeImport", icon: Upload };
          const ModeIcon = mode.icon;
          const status = STATUS[channel?.status ?? "no_data"] ?? STATUS.not_checked;
          const hasData = (channel?.products ?? 0) > 0;
          const synced = channel?.last_success_at ? new Date(channel.last_success_at) : null;
          return (
            <button
              key={key}
              type="button"
              className="channel-card"
              aria-pressed={active === key}
              onClick={() => onSelect(key)}
              style={{ "--channel": channelColor(key), "--tone": status.tone } as CSSProperties}
            >
              <span className="channel-card__top">
                <i className="channel-card__mark" aria-hidden />
                <strong>{channelLabel(key)}</strong>
                <span className="channel-card__mode">
                  <ModeIcon size={12} aria-hidden />
                  {t("sources." + mode.key)}
                </span>
              </span>
              <span className="channel-card__status">
                <i aria-hidden />
                {t("workspace." + status.key)}
              </span>
              {hasData ? (
                <span className="channel-card__stats">
                  <Stat label={t("sources.statProducts")} value={number(channel!.products)} />
                  <Stat label={t("sources.statReviews")} value={number(channel!.reviews)} />
                  <Stat
                    label={t("sources.statOpen")}
                    value={number(channel!.active_findings ?? 0)}
                    alert={(channel!.active_findings ?? 0) > 0}
                  />
                  {channel!.units_sold != null ? (
                    <Stat label={t("sources.statUnits")} value={number(channel!.units_sold)} />
                  ) : (
                    <Stat label={t("sources.statUnits")} value="—" muted title={t("sources.unitsUnknown")} />
                  )}
                </span>
              ) : (
                <span className="channel-card__empty muted">{t("sources.noDataYet")}</span>
              )}
              <span className="channel-card__foot">
                {(channel?.samplings?.length || channel?.synthetic) && (
                  <span className="channel-card__badges">
                    {channel?.samplings?.map((kind) => <SamplingBadge key={kind} kind={kind} />)}
                    {channel?.synthetic && <span className="channel-card__origin">{t("sources.origin_synthetic")}</span>}
                  </span>
                )}
                <span className="muted channel-card__synced">
                  {synced && !Number.isNaN(synced.getTime())
                    ? t("sources.lastSync", { time: synced.toLocaleString(language === "id" ? "id-ID" : "en-GB") })
                    : t("sources.neverSynced")}
                </span>
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

export interface SamplePack {
  name: string;
  channel: string;
  data_origin: string;
  captured_at: string | null;
  label: string;
  products?: number;
  sampling_kind?: string;
}

const ORIGIN_ICON: Record<string, typeof Globe> = {
  synthetic: Database,
  public_dataset: Database,
  public_snapshot: Globe,
  public_live: Globe,
};

/** Kartu paket contoh: asal data, cara sampel diambil (dan artinya), jumlah produk, tombol muat. */
export function SamplePackCard({
  pack,
  busy,
  onLoad,
}: {
  pack: SamplePack;
  busy: boolean;
  onLoad: () => void;
}) {
  const { t, language } = useI18n();
  const Icon = ORIGIN_ICON[pack.data_origin] ?? Globe;
  const kind = pack.sampling_kind ?? "unknown";
  return (
    <article className="pack-card" style={{ "--channel": channelColor(pack.channel) } as CSSProperties}>
      <header className="pack-card__head">
        <span className="pack-card__icon" aria-hidden>
          <Icon size={16} />
        </span>
        <div>
          <h3>{pack.label}</h3>
          <p className="muted">
            {t("sources.origin_" + pack.data_origin)}
            {pack.products != null && " · " + t("sources.packProducts", { count: pack.products })}
            {pack.captured_at &&
              " · " + t("sources.captured", { time: new Date(pack.captured_at).toLocaleDateString(language === "id" ? "id-ID" : "en-GB") })}
          </p>
        </div>
      </header>
      <div className="pack-card__sampling">
        <SamplingBadge kind={kind} />
        <p className="muted">{t("sources.samplingHint_" + (["complete", "random", "skewed"].includes(kind) ? kind : "unknown"))}</p>
      </div>
      <div className="pack-card__foot">
        <Button variant="outline" busy={busy} onClick={onLoad}>
          <Download size={14} aria-hidden />
          {t("sources.sampleLoad")}
        </Button>
      </div>
    </article>
  );
}
