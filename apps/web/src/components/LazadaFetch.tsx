import { useId, useState } from "react";
import { request, ApiError } from "@/api/http.js";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { Button, Card, Notice } from "@/components/ui";

export function LazadaFetch() {
  const { status, run, busy } = useWorkspace();
  const { t, localizeError } = useI18n();
  const [urls, setUrls] = useState("");
  const [error, setError] = useState<string | null>(null);
  const id = useId();
  const capability = status?.fetch;
  return <Card title={t("sources.fetch")}>
    <form className="stack" onSubmit={event => {
      event.preventDefault();
      setError(null);
      void run(async () => {
        try { return await request("/deciqo/lazada/fetch", { method: "POST", body: { urls: urls.split(/\r?\n/).map(url => url.trim()).filter(Boolean) } }); }
        catch(e) { setError((e as ApiError).code ?? "request_failed"); throw e; }
      }, "sources.importedDone", "sources.importing");
    }}>
      <label htmlFor={id}>{t("sources.fetchUrls")}</label>
      <textarea id={id} rows={4} required value={urls} onChange={event=>setUrls(event.target.value)} maxLength={12000} />
      {capability && <p className="muted">{t("sources.fetchLimits", { urls: capability.max_urls, reviews: capability.reviews_per_product, charge: capability.max_charge_per_run_usd })}</p>}
      {!capability?.configured && <Notice tone="info">{t("sources.fetchUnavailable")}</Notice>}
      {error && <Notice tone="alert">{localizeError(error)}</Notice>}
      <Button type="submit" busy={busy} disabled={!capability?.configured || !urls.trim()}>{t("sources.fetchRun")}</Button>
    </form>
  </Card>;
}
