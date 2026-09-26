import { useEffect, useRef, useState } from "react";
import { CircleCheck, CircleHelp, CircleX, X } from "lucide-react";
import type { Evidence, VisionCheck } from "@/api/product";
import { useI18n } from "@/lib/i18n";
import { Button } from "@/components/ui";
import { safeImageUrl } from "./actions";

const DEFAULT_VISIBLE = 3;

const verdicts = {
  supports: { key: "visionSupports", tone: "good", Icon: CircleCheck },
  contradicts: { key: "visionContradicts", tone: "warn", Icon: CircleX },
  inconclusive: { key: "visionUnclear", tone: "muted", Icon: CircleHelp },
} as const;

export function VisionBadge({ vision }: { vision?: VisionCheck | null }) {
  const { t } = useI18n();
  if (!vision) return null;
  const meta = verdicts[vision.verdict as keyof typeof verdicts] ?? verdicts.inconclusive;
  const { Icon } = meta;
  return (
    <span className={"chip vision-badge tone-" + meta.tone} title={vision.reason || undefined}>
      <Icon size={14} aria-hidden />
      {t("product." + meta.key)}
    </span>
  );
}

export function EvidenceList({
  evidence,
  formatDate,
}: {
  evidence: Evidence[];
  formatDate: (value: string) => string;
}) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(false);
  const [photo, setPhoto] = useState<{ url: string; alt: string } | null>(null);
  const shown = expanded ? evidence : evidence.slice(0, DEFAULT_VISIBLE);
  return (
    <>
      <ul className="evidence-list">
        {shown.map((item, index) => {
          const photos = (item.images ?? [])
            .map(safeImageUrl)
            .filter((url): url is string => Boolean(url))
            .slice(0, 4);
          const meta = [
            item.rating == null ? null : item.rating + " ★",
            item.variant,
            item.review_time ? formatDate(item.review_time) : null,
            item.review_id,
          ].filter(Boolean);
          return (
            <li key={item.review_id + index} className="evidence-item">
              <blockquote className="evidence-item__quote">
                <p>“{item.quote}”</p>
                <footer>{meta.join(" · ")}</footer>
              </blockquote>
              {(photos.length > 0 || item.vision) && (
                <div className="evidence-item__photos">
                  {photos.length > 0 && (
                    <div className="evidence-item__thumbs">
                      {photos.map((url, photoIndex) => (
                        <button
                          key={url}
                          type="button"
                          className="evidence-thumb"
                          aria-label={t("product.openPhoto", { index: photoIndex + 1, total: photos.length })}
                          onClick={() =>
                            setPhoto({ url, alt: t("product.buyerPhotoAlt", { quote: item.quote.slice(0, 80) }) })
                          }
                        >
                          <PhotoThumb url={url} />
                        </button>
                      ))}
                    </div>
                  )}
                  <VisionBadge vision={item.vision} />
                  {item.vision?.reason && (
                    <p className="evidence-item__reason muted">{item.vision.reason}</p>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
      {evidence.length > DEFAULT_VISIBLE && (
        <Button variant="text" size="sm" aria-expanded={expanded} onClick={() => setExpanded((value) => !value)}>
          {expanded
            ? t("product.showFewer")
            : t("product.showAllQuotes", { count: evidence.length })}
        </Button>
      )}
      <PhotoLightbox photo={photo} onClose={() => setPhoto(null)} />
    </>
  );
}

function PhotoThumb({ url }: { url: string }) {
  const [failed, setFailed] = useState(false);
  if (failed) return <span className="evidence-thumb__empty" aria-hidden />;
  return (
    <img
      src={url}
      alt=""
      width={72}
      height={72}
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
    />
  );
}

/** Lightbox sederhana memakai <dialog> bawaan: Esc, fokus terkunci, dan tombol tutup. */
function PhotoLightbox({
  photo,
  onClose,
}: {
  photo: { url: string; alt: string } | null;
  onClose: () => void;
}) {
  const { t } = useI18n();
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (photo && !dialog.open) {
      if (typeof dialog.showModal === "function") dialog.showModal();
      else window.open(photo.url, "_blank", "noopener,noreferrer");
    } else if (!photo && dialog.open) dialog.close();
  }, [photo]);
  return (
    <dialog
      ref={ref}
      className="photo-lightbox"
      aria-label={t("product.buyerPhoto")}
      onClose={onClose}
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      {photo && (
        <figure>
          <img src={photo.url} alt={photo.alt} referrerPolicy="no-referrer" />
          <figcaption>
            <a href={photo.url} target="_blank" rel="noopener noreferrer">
              {t("product.openPhotoTab")}
            </a>
            <Button variant="outline" size="sm" onClick={onClose} autoFocus>
              <X size={16} aria-hidden />
              {t("product.closePhoto")}
            </Button>
          </figcaption>
        </figure>
      )}
    </dialog>
  );
}
