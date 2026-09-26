import { useId, useState } from "react";
import { Camera, FileText, ScanSearch } from "lucide-react";
import { request, ApiError } from "@/api/http.js";
import type { ProductView } from "@/api/product";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { pollJob } from "@/lib/jobs.js";
import { Button, Notice } from "@/components/ui";
import type { Mutation } from "./FindingCard";
import { skipReasonKey } from "./actions";

interface VisionRun {
  ocr?: { status: string; reason?: string | null; images_read?: number; images_total?: number; changed?: boolean } | null;
  photos?: { status: string; reason?: string | null; planned?: number; checked?: number; cached?: number; checked_at?: string } | null;
}

const STAGES = ["triage", "discovery", "membership", "verifier", "gate"];

export function ListingEditor({
  productId,
  listing,
  setListing,
  mutate,
  id,
}: {
  productId: string;
  listing: string;
  setListing: (value: string) => void;
  mutate: Mutation;
  id?: string;
}) {
  const { t } = useI18n();
  const { busy } = useWorkspace();
  const generated = useId();
  const fieldId = id ?? generated;
  return (
    <form
      className="stack"
      onSubmit={(event) => {
        event.preventDefault();
        void mutate(
          () =>
            request("/deciqo/products/" + encodeURIComponent(productId) + "/listing", {
              method: "PUT",
              body: { listing },
            }),
          "product.listingSaved",
          "workspace.jobAnalysing",
        );
      }}
    >
      <div className="field">
        <label htmlFor={fieldId}>{t("product.listingField")}</label>
        <textarea
          id={fieldId}
          rows={5}
          required
          value={listing}
          onChange={(event) => setListing(event.target.value)}
          aria-describedby={fieldId + "-hint"}
        />
        <p id={fieldId + "-hint"} className="field__hint">
          {t("product.editDescriptionHint")}
        </p>
      </div>
      <Button type="submit" busy={busy}>
        {t("product.saveListing")}
      </Button>
    </form>
  );
}

export function InvestigateButton({
  productId,
  view,
  mutate,
}: {
  productId: string;
  view: ProductView;
  mutate: Mutation;
}) {
  const { t } = useI18n();
  const { busy } = useWorkspace();
  const done = Boolean(view.analysis?.created_at) || (view.analysis?.trace?.length ?? 0) > 0;
  return (
    <Button
      busy={busy}
      onClick={() =>
        void mutate(
          () =>
            request("/deciqo/products/" + encodeURIComponent(productId) + "/analyse", {
              method: "POST",
              body: { force: true },
            }),
          "product.analyseSaved",
          "workspace.jobAnalysing",
        )
      }
    >
      <ScanSearch size={16} aria-hidden />
      {t(done ? "product.rerun" : "product.investigate")}
    </Button>
  );
}

export function InvestigationDetails({
  productId,
  view,
  listing,
  setListing,
  mutate,
  refresh,
  formatDate,
}: {
  productId: string;
  view: ProductView;
  listing: string;
  setListing: (value: string) => void;
  mutate: Mutation;
  refresh: () => Promise<void>;
  formatDate: (value: string) => string;
}) {
  const { t, localizeError } = useI18n();
  const { busy } = useWorkspace();
  const [visionBusy, setVisionBusy] = useState(false);
  const [visionState, setVisionState] = useState<"idle" | "done" | "unavailable" | "slow">("idle");
  const [visionRun, setVisionRun] = useState<VisionRun | null>(null);
  const [visionError, setVisionError] = useState<string | null>(null);
  const uid = useId();
  const product = view.product;
  const analysis = view.analysis;
  const trace = analysis?.trace ?? [];
  const ocr = product.image_ocr;
  const hasPhotos = (view.stats.with_photos ?? 0) > 0;

  async function checkPhotos() {
    setVisionBusy(true);
    setVisionError(null);
    setVisionRun(null);
    setVisionState("idle");
    try {
      // Sinkron dan lambat (puluhan detik): tombol menampilkan status berjalan selama menunggu.
      const result = (await request("/deciqo/products/" + encodeURIComponent(productId) + "/vision", {
        method: "POST",
        timeout: 180000,
      })) as { job_id?: string | null; vision_run?: VisionRun | null } | null;
      setVisionRun(result?.vision_run ?? null);
      // OCR yang mengubah teks listing memicu analisis ulang; tunggu sampai cek listing ikut segar.
      if (result?.job_id) await pollJob(result.job_id);
      setVisionState("done");
      await refresh();
    } catch (e) {
      const error = e as ApiError;
      // Rute belum ada (404 tanpa kode API), metode tidak didukung, atau belum diimplementasi.
      if ([405, 501].includes(error.status) || (error.status === 404 && error.code === "request_failed"))
        setVisionState("unavailable");
      else if (error.code === "timeout") setVisionState("slow");
      else setVisionError(error.code ?? "request_failed");
    } finally {
      setVisionBusy(false);
    }
  }

  function visionRunText(run: VisionRun) {
    const parts: string[] = [];
    const photos = run.photos;
    if (photos) {
      parts.push(
        photos.status === "skipped"
          ? t("product.visionRunSkipped", { reason: t(skipReasonKey(photos.reason)) })
          : t("product.visionRunPhotos", { checked: photos.checked ?? 0, cached: photos.cached ?? 0 }),
      );
    }
    const ocrRun = run.ocr;
    if (ocrRun) {
      parts.push(
        ocrRun.status === "skipped"
          ? t("product.ocrSkipped", { reason: t(skipReasonKey(ocrRun.reason)) })
          : t("product.ocrDone", { read: ocrRun.images_read ?? 0, total: ocrRun.images_total ?? 0 }),
      );
    }
    return parts.join(" · ");
  }

  function stageDetail(stage: Record<string, string | number>) {
    switch (String(stage.stage)) {
      case "triage":
        return t("product.stageKept", { kept: stage.kept, total: stage.of });
      case "discovery":
        return t("product.stageProposed", { count: stage.proposed });
      case "membership":
        return t("product.stageLabelled", { count: stage.labelled });
      case "verifier":
        return t("product.stageVerifier", {
          kept: stage.kept,
          dropped: stage.dropped,
          quotes: stage.quotes_rejected,
        });
      case "gate":
        return t("product.stageGate", {
          blocked: stage.blocked ?? "—",
          facts: stage.need_fact ?? "—",
        });
      default:
        return "";
    }
  }

  return (
    <details className="card disclosure-card">
      <summary>
        <span className="disclosure-card__title">{t("product.detailsTitle")}</span>
        <span className="disclosure-card__hint muted">
          {analysis?.created_at
            ? t("product.detailsRan", { time: formatDate(analysis.created_at) })
            : t("product.notAnalysed")}
        </span>
      </summary>
      <div className="disclosure-card__body">
        <div className="details-actions">
          <InvestigateButton productId={productId} view={view} mutate={mutate} />
          <Button
            variant="outline"
            busy={busy}
            onClick={() =>
              void mutate(
                () =>
                  request("/deciqo/products/" + encodeURIComponent(productId) + "/draft", {
                    method: "POST",
                  }),
                "product.draftSaved",
                "workspace.jobDrafting",
              )
            }
          >
            <FileText size={16} aria-hidden />
            {t("product.draftAll")}
          </Button>
          {hasPhotos && (
            <Button
              variant="outline"
              busy={visionBusy}
              disabled={visionState === "unavailable"}
              onClick={() => void checkPhotos()}
            >
              <Camera size={16} aria-hidden />
              {t("product.checkPhotos")}
            </Button>
          )}
        </div>
        <p role="status" className="details-line details-status">
          {visionBusy
            ? t("product.checkPhotosRunning")
            : visionState === "unavailable"
              ? t("product.checkPhotosUnavailable")
              : visionState === "slow"
                ? t("product.checkPhotosSlow")
                : visionState === "done"
                  ? visionRun
                    ? visionRunText(visionRun)
                    : t("product.checkPhotosDone")
                  : ""}
        </p>
        {visionState === "slow" && (
          <div>
            <Button variant="outline" size="sm" onClick={() => void refresh()}>
              {t("product.reload")}
            </Button>
          </div>
        )}
        {visionError && <Notice tone="alert">{localizeError(visionError)}</Notice>}
        {ocr && (
          <p className="details-line">
            {ocr.status === "done"
              ? t("product.ocrDone", { read: ocr.images_read, total: ocr.images_total })
              : ocr.status === "pending"
                ? t("product.ocrPending")
                : t("product.ocrSkipped", { reason: t(skipReasonKey(ocr.reason)) })}
          </p>
        )}

        <section className="details-section" aria-labelledby={uid + "-pipeline"}>
          <h3 id={uid + "-pipeline"}>{t("product.pipeline")}</h3>
          <p className="muted">{t("product.pipelineLead")}</p>
          {trace.length > 0 ? (
            <ul className="pipeline-list">
              {trace.map((stage, index) => {
                const key = String(stage.stage);
                return (
                  <li key={index}>
                    <strong>{t("product." + (STAGES.includes(key) ? key : "pipeline"))}</strong>
                    <span className="count">{stageDetail(stage)}</span>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="muted">{t("product.notAnalysed")}</p>
          )}
        </section>

        {product.listing_provided && (
          <section className="details-section" aria-labelledby={uid + "-listing"}>
            <h3 id={uid + "-listing"}>{t("product.listingCurrent")}</h3>
            <p className="muted">{t("product.listingHint")}</p>
            <ListingEditor
              productId={productId}
              listing={listing}
              setListing={setListing}
              mutate={mutate}
            />
          </section>
        )}

        {view.not_detected.length > 0 && (
          <section className="details-section" aria-labelledby={uid + "-gone"}>
            <h3 id={uid + "-gone"}>{t("product.notDetected")}</h3>
            <ul>
              {view.not_detected.map((item) => (
                <li key={item.id}>{item.attribute_local}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </details>
  );
}
