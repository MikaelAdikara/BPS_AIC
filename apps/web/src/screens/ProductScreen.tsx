import { useCallback, useEffect, useRef, useState } from "react";
import { request, ApiError } from "@/api/http.js";
import type { ProductView, Finding } from "@/api/product";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { Button, Card, LoadingState, Notice } from "@/components/ui";
import { GenericComparison } from "@/components/GenericComparison";
import { ProductHeader } from "@/components/product/ProductHeader";
import { ActionPlan } from "@/components/product/ActionPlan";
import { FindingCard } from "@/components/product/FindingCard";
import {
  InvestigateButton,
  InvestigationDetails,
  ListingEditor,
} from "@/components/product/InvestigationDetails";
import {
  prefersReducedMotion,
  sortByImpact,
  type FocusStep,
} from "@/components/product/actions";

const LISTING_FIELD_ID = "product-listing-field";

function externalUrl(value: string) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

export function ProductScreen({
  productId,
  query,
}: {
  productId: string;
  query: URLSearchParams;
}) {
  const { t, language, localizeError } = useI18n();
  const workspace = useWorkspace();
  const [view, setView] = useState<ProductView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [listing, setListing] = useState("");
  const queryFinding = query.get("f");
  const [selectedId, setSelectedId] = useState<string | null>(queryFinding);
  const [focus, setFocus] = useState<{ step: FocusStep; nonce: number } | null>(null);
  const [copyNotice, setCopyNotice] = useState<{ id: string; status: string } | null>(null);
  const aborter = useRef<AbortController | null>(null);
  const version = useRef(0);
  const load = useCallback(async () => {
    const current = ++version.current;
    aborter.current?.abort();
    const controller = new AbortController();
    aborter.current = controller;
    setError(null);
    try {
      const result = (await request(
        "/deciqo/products/" + encodeURIComponent(productId),
        { signal: controller.signal },
      )) as ProductView;
      if (current !== version.current) return;
      setView(result);
      // listing_text bisa memuat blok OCR gambar; editor hanya memakai deskripsi yang bisa diubah.
      setListing(result.product.listing_edit_text ?? "");
    } catch (e) {
      if (current === version.current && !controller.signal.aborted)
        setError((e as ApiError).code ?? "request_failed");
    } finally {
      if (current === version.current) setLoading(false);
    }
  }, [productId]);
  useEffect(() => {
    setLoading(true);
    setView(null);
    void load();
    return () => {
      version.current++;
      aborter.current?.abort();
    };
  }, [load]);
  useEffect(() => {
    if (queryFinding) setSelectedId(queryFinding);
  }, [queryFinding]);
  async function mutate(
    task: () => Promise<unknown>,
    success: string,
    label?: string,
  ) {
    let succeeded = false;
    await workspace.run(
      async () => {
        const result = await task();
        succeeded = true;
        return result;
      },
      success,
      label,
    );
    if (succeeded) await load();
  }
  function date(value: string) {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime())
      ? value
      : parsed.toLocaleString(language === "id" ? "id-ID" : "en-GB");
  }
  function select(finding: Finding, step: FocusStep) {
    setSelectedId(finding.id);
    try {
      window.history.replaceState(
        null,
        "",
        "#/app/listings/" + encodeURIComponent(productId) + "?f=" + encodeURIComponent(finding.id),
      );
    } catch {
      /* URL tetap; pilihan tetap berlaku di state. */
    }
    if (step === "listing") {
      requestAnimationFrame(() => {
        const field = document.getElementById(LISTING_FIELD_ID);
        field?.closest(".card")?.scrollIntoView({
          behavior: prefersReducedMotion() ? "auto" : "smooth",
          block: "start",
        });
        field?.focus({ preventScroll: true });
      });
      return;
    }
    setFocus((current) => ({ step, nonce: (current?.nonce ?? 0) + 1 }));
  }
  async function copyFix(finding: Finding, text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopyNotice({ id: finding.id, status: "copied" });
    } catch {
      setCopyNotice({ id: finding.id, status: "copyFailed" });
    }
  }
  if (loading && !view)
    return (
      <>
        <h1>{t("common.products")}</h1>
        <LoadingState />
      </>
    );
  if (!view)
    return (
      <>
        <h1>{t("product.loadError")}</h1>
        <Notice tone="alert">{localizeError(error ?? "request_failed")}</Notice>
        <Button onClick={() => void load()}>{t("common.retry")}</Button>
      </>
    );
  const product = view.product;
  const link = externalUrl(product.url);
  const findings = sortByImpact(view.findings);
  const sections = view.draft?.sections ?? [];
  const finding = findings.find((item) => item.id === selectedId) ?? findings[0];
  return (
    <div className="product-page">
      <a className="product-back" href="#/app/listings">{t("product.back")}</a>
      <ProductHeader view={view} link={link} formatDate={date} />
      {error && (
        <Notice
          tone="alert"
          action={<Button variant="outline" onClick={() => void load()}>{t("common.retry")}</Button>}
        >
          {localizeError(error)}
        </Notice>
      )}
      {workspace.error && (
        <Notice tone="alert">{localizeError(workspace.error)}</Notice>
      )}
      {view.analysis?.status === "failed" && (
        <Notice tone="warn">{t("product.analysisFailed")}</Notice>
      )}
      {!product.listing_provided && (
        <Card
          className="listing-prompt"
          title={t("product.listingTitle")}
          lead={t("product.listingHint")}
        >
          <ListingEditor
            id={LISTING_FIELD_ID}
            productId={productId}
            listing={listing}
            setListing={setListing}
            mutate={mutate}
          />
        </Card>
      )}
      <ActionPlan
        findings={findings}
        sections={sections}
        listingProvided={product.listing_provided}
        selectedId={finding?.id ?? null}
        onSelect={select}
        onCopy={(item, text) => void copyFix(item, text)}
        emptyAction={<InvestigateButton productId={productId} view={view} mutate={mutate} />}
      />
      {finding && (
        <FindingCard
          key={finding.id}
          finding={finding}
          section={sections.find((section) => section.finding_id === finding.id)}
          view={view}
          mutate={mutate}
          focus={focus}
          copyNotice={copyNotice?.id === finding.id ? copyNotice.status : null}
        />
      )}
      <InvestigationDetails
        productId={productId}
        view={view}
        listing={listing}
        setListing={setListing}
        mutate={mutate}
        refresh={load}
        formatDate={date}
      />
      <GenericComparison productId={productId} result={view.generic_draft} refresh={load} />
    </div>
  );
}
