import { useState } from "react";
import { request, ApiError } from "@/api/http.js";
import type { ProductView } from "@/api/product";
import { useI18n } from "@/lib/i18n";
import { Button, Chip, EmptyState, Notice } from "@/components/ui";

/** Pembanding chatbot umum; dilipat di paling bawah halaman produk. */
export function GenericComparison({ productId, result, refresh }: { productId: string; result: ProductView["generic_draft"]; refresh: () => Promise<void> }) {
  const { t, localizeError } = useI18n();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function compare() {
    setBusy(true);
    setError(null);
    try {
      await request("/deciqo/products/" + encodeURIComponent(productId) + "/generic", { method: "POST" });
      await refresh();
    } catch (e) {
      setError((e as ApiError).code ?? "request_failed");
    } finally {
      setBusy(false);
    }
  }
  return <details className="card disclosure-card generic-compare">
    <summary>
      <span className="disclosure-card__title">{t("product.genericTitle")}</span>
      <span className="disclosure-card__hint muted">
        {result ? t("product.genericCounts", result.counts) : t("product.genericWhy")}
      </span>
    </summary>
    <div className="disclosure-card__body stack">
      <p>{t("product.genericWhy")}</p>
      <p className="muted">{t("product.genericHint")}</p>
      <div><Button variant="outline" busy={busy} onClick={() => void compare()}>{t("product.genericRun")}</Button></div>
      {error && <Notice tone="alert">{error === "generic_unavailable" ? t("product.genericUnavailable") : localizeError(error)}</Notice>}
      {!result && !busy && <EmptyState title={t("product.genericEmpty")} description={t("product.genericEmptyHint")} />}
      {result && <details>
        <summary>{t("product.genericCounts", result.counts)}</summary>
        <p className="muted">{result.model} · {result.gate_version}</p>
        {result.problems.map((item, index) => <details key={index}><summary>{item.problem}</summary><p>{item.suggestion}</p></details>)}
        {result.sentences.map((sentence, index) => <div key={index} className="quote">
          <Chip tone={sentence.status === "passed" ? "good" : "alert"}>{t(sentence.status === "passed" ? "product.genericPassed" : "product.blocked")}</Chip>
          <p>{sentence.text}</p>
          {sentence.reasons.length > 0 && <p className="muted">{t("product.reasonUnsupported")}</p>}
          {sentence.unsupported.length > 0 && <p>{t("product.genericUnsupported")}: {sentence.unsupported.join(" · ")}</p>}
        </div>)}
      </details>}
    </div>
  </details>;
}
