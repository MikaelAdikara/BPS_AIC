import { useMemo, useState } from "react";
import { ExternalLink, Star } from "lucide-react";
import type { ProductView } from "@/api/product";
import { useI18n } from "@/lib/i18n";
import { Chip } from "@/components/ui";
import { ChannelDot } from "@/components/insight/IssueMap";
import { channelLabel } from "@/lib/insight-model";
import { ProductImage } from "./ProductImage";
import { safeImageUrl } from "./actions";

const PUBLIC_ORIGINS = [
  "public",
  "public_snapshot",
  "public_live",
  "public_dataset",
  "lazada_public",
  "research_dataset",
  "team_collected",
];

export function ProductHeader({
  view,
  link,
  formatDate,
}: {
  view: ProductView;
  link: string | null;
  formatDate: (value: string) => string;
}) {
  const { t, language } = useI18n();
  const product = view.product;
  const gallery = useMemo(() => {
    const all = [product.image_url, ...(product.images ?? [])]
      .map(safeImageUrl)
      .filter((url): url is string => Boolean(url));
    return [...new Set(all)];
  }, [product.image_url, product.images]);
  const [active, setActive] = useState(0);
  const main = gallery[active] ?? gallery[0] ?? null;
  const origin = product.synthetic
    ? "originSynthetic"
    : PUBLIC_ORIGINS.includes(product.data_origin)
      ? "originPublic"
      : "originChannel";
  const rating = view.stats.rating;
  return (
    <header className="product-head">
      <div className="product-head__media">
        <ProductImage src={main} alt={product.title} size={112} className="product-head__image" />
        {gallery.length > 1 && (
          <div className="product-head__strip" role="group" aria-label={t("product.gallery")}>
            {gallery.slice(0, 6).map((url, index) => (
              <button
                key={url}
                type="button"
                className="product-head__thumb"
                aria-pressed={index === active}
                aria-label={t("product.galleryImage", { index: index + 1, total: gallery.length })}
                onClick={() => setActive(index)}
              >
                <ProductImage src={url} size={32} />
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="product-head__body">
        <h1 className="product-head__title" title={product.title}>
          {product.title}
        </h1>
        <div className="product-head__meta">
          <span className="channel-tag">
            <ChannelDot channel={product.channel} />
            {channelLabel(product.channel)}
          </span>
          {product.synthetic && <Chip synthetic />}
          {view.analysis?.engine === "rules" && <Chip>{t("product.ruleMode")}</Chip>}
        </div>
        <p className="product-head__stats">
          {rating != null && (
            <span className="product-head__rating">
              <Star size={14} className="star-icon" aria-hidden />
              <span className="count">
                {new Intl.NumberFormat(language === "id" ? "id-ID" : "en-GB", {
                  maximumFractionDigits: 1,
                }).format(rating)}
              </span>
              <span className="visually-hidden"> / 5</span>
            </span>
          )}
          <span>
            {t("product.reviews", {
              reviews: view.stats.reviews,
              photos: view.stats.with_photos,
            })}
          </span>
        </p>
        <p className="product-head__origin muted">
          {t("product." + origin)}
          {product.captured_at
            ? " · " + t("product.captured", { time: formatDate(product.captured_at) })
            : ""}
        </p>
      </div>
      {link && (
        <a
          className="btn btn--outline product-head__live"
          href={link}
          target="_blank"
          rel="noopener noreferrer"
        >
          {t("product.live")}
          <ExternalLink size={16} aria-hidden />
        </a>
      )}
    </header>
  );
}
