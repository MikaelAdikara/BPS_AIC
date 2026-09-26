import type { DraftSection, Finding, ProductView } from "@/api/product";

/** Satu aksi utama per temuan, dipakai kartu "Yang perlu kamu lakukan" dan kartu temuan. */
export type ActionKind = "listing" | "fact" | "copy" | "ops" | "review";

/** Bagian kartu temuan yang difokuskan setelah aksi dipilih. */
export type FocusStep = "listing" | "fact" | "draft" | "decision" | "evidence" | "card";

/** Pilihan cepat "Apa yang sudah Anda lakukan?" sesuai rute isu (kunci pesan `product.*`). */
export function decisionPresets(finding: Finding): string[] {
  if (finding.listing_fixable) return ["doneListing1", "doneListing2", "doneListing3"];
  if (finding.finding_type === "product_quality")
    return ["doneQuality1", "doneQuality2", "doneQuality3"];
  return ["doneOps1", "doneOps2", "doneOps3"];
}

type Translate = (key: string, values?: Record<string, string | number>) => string;

/** Ringkasan siap kirim untuk tim operasional/QC: isu, hitungan, dan kutipan verbatim. */
export function opsBrief(
  finding: Finding,
  view: ProductView,
  t: Translate,
  attribute: string,
  formatDate: (value: string) => string,
): string {
  const metrics = finding.metrics;
  const quality = finding.finding_type === "product_quality";
  const quotes = finding.evidence.slice(0, 5).map((item) => {
    const meta = [
      item.rating != null ? item.rating + "★" : "",
      item.variant ?? "",
      item.review_time ? formatDate(item.review_time) : "",
    ].filter(Boolean);
    return `- “${item.quote}”` + (meta.length ? ` (${meta.join(", ")})` : "");
  });
  return [
    `[Deciqo] ${view.product.title}`,
    t("product.briefIssue", {
      attribute,
      support: metrics.support,
      total: metrics.denominator,
    }),
    "",
    t("product.briefQuotes"),
    ...quotes,
    "",
    t(quality ? "product.briefAskQuality" : "product.briefAskOps"),
  ].join("\n");
}

const BUCKET_ORDER = [
  "recurrence",
  "needs_fact",
  "to_do",
  "monitoring",
  "dismissed",
  "not_detected",
];

export function sortByImpact(findings: Finding[]): Finding[] {
  const rank = (bucket: string) => {
    const index = BUCKET_ORDER.indexOf(bucket);
    return index === -1 ? BUCKET_ORDER.length : index;
  };
  return findings
    .map((finding, index) => ({ finding, index }))
    .sort(
      (a, b) =>
        rank(a.finding.bucket) - rank(b.finding.bucket) ||
        (b.finding.metrics?.support ?? b.finding.support ?? 0) -
          (a.finding.metrics?.support ?? a.finding.support ?? 0) ||
        a.index - b.index,
    )
    .map((item) => item.finding);
}

export function draftText(section?: DraftSection): string | null {
  return section?.text && ["ready", "needs_review"].includes(section.status)
    ? section.text
    : null;
}

export function actionFor(
  finding: Finding,
  section: DraftSection | undefined,
  listingProvided: boolean,
): { kind: ActionKind; focus: FocusStep } {
  if (!finding.listing_fixable) return { kind: "ops", focus: "decision" };
  if (finding.bucket === "needs_fact" || finding.next === "fact")
    return { kind: "fact", focus: "fact" };
  if (draftText(section)) return { kind: "copy", focus: "draft" };
  if (
    !listingProvided &&
    (finding.next === "paste_listing" || finding.needs_listing)
  )
    return { kind: "listing", focus: "listing" };
  if (finding.next === "draft" || finding.next === "apply")
    return { kind: "review", focus: "draft" };
  return { kind: "review", focus: "card" };
}

export function safeImageUrl(value: unknown): string | null {
  if (typeof value !== "string" || !value) return null;
  try {
    const url = new URL(value, window.location.href);
    return ["http:", "https:"].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

export function prefersReducedMotion() {
  return (
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
  );
}

const SKIP_REASONS: Record<string, string> = {
  no_images: "whyNoImages",
  no_api_key: "whyNoApiKey",
  key_rejected: "whyKeyRejected",
  budget: "whyBudget",
  disabled: "whyDisabled",
  error: "whyError",
  limit: "whyLimit",
  not_run: "whyNotRun",
};

/** Kunci pesan ramah untuk alasan OCR/vision dilewati (kode dari engine/vision.py). */
export function skipReasonKey(code?: string | null): string {
  return "product." + (SKIP_REASONS[code ?? ""] ?? "whyUnknown");
}
