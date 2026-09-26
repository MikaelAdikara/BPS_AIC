import type { ReactNode } from "react";
import {
  ChevronRight,
  ClipboardCopy,
  Eye,
  PenLine,
  Truck,
  FileText,
} from "lucide-react";
import type { DraftSection, Finding } from "@/api/product";
import { useI18n } from "@/lib/i18n";
import { Card, Chip, EmptyState, type Tone } from "@/components/ui";
import { buckets } from "@/components/workspace";
import { actionFor, type ActionKind, type FocusStep } from "./actions";

const typeKeys: Record<string, string> = {
  missing_fact: "typeMissingFact",
  unclear_wording: "typeUnclearWording",
  unclear_fact: "typeUnclearWording",
  listing_conflict: "typeListingConflict",
  conflicting_fact: "typeListingConflict",
  expectation_gap: "typeExpectationGap",
  expectation_mismatch: "typeExpectationGap",
  product_quality: "typeQuality",
  operations: "typeOperations",
  operational: "typeOperations",
};

const actionMeta: Record<ActionKind, { key: string; icon: ReactNode; primary: boolean }> = {
  fact: { key: "actFact", icon: <PenLine size={16} aria-hidden />, primary: true },
  copy: { key: "actCopy", icon: <ClipboardCopy size={16} aria-hidden />, primary: true },
  listing: { key: "actListing", icon: <FileText size={16} aria-hidden />, primary: true },
  ops: { key: "actOps", icon: <Truck size={16} aria-hidden />, primary: false },
  review: { key: "actReview", icon: <Eye size={16} aria-hidden />, primary: false },
};

export function ActionPlan({
  findings,
  sections,
  listingProvided,
  selectedId,
  onSelect,
  onCopy,
  emptyAction,
}: {
  findings: Finding[];
  sections: DraftSection[];
  listingProvided: boolean;
  selectedId: string | null;
  onSelect: (finding: Finding, focus: FocusStep) => void;
  onCopy: (finding: Finding, text: string) => void;
  emptyAction: ReactNode;
}) {
  const { t, language } = useI18n();
  const listing = findings.filter((item) => item.listing_fixable).length;
  const ops = findings.length - listing;
  return (
    <Card
      className="action-plan"
      title={t("product.planTitle")}
      lead={
        findings.length
          ? t("product.planSummary", { listing, ops })
          : undefined
      }
    >
      {findings.length === 0 ? (
        <EmptyState
          title={t("product.noFindings")}
          description={t("product.noFindingsHint")}
          action={emptyAction}
        />
      ) : (
        <ol className="action-plan__list">
          {findings.map((finding) => {
            const section = sections.find((item) => item.finding_id === finding.id);
            const action = actionFor(finding, section, listingProvided);
            const meta = actionMeta[action.kind];
            const bucket = buckets[finding.bucket];
            const tone: Tone = bucket?.tone ?? "muted";
            const metrics = finding.metrics;
            const support = metrics?.support ?? finding.support;
            const denominator = metrics?.denominator ?? finding.denominator;
            const minimum = metrics?.support_is_minimum ?? finding.support_is_minimum;
            const name = language === "id" ? finding.attribute_local : finding.attribute;
            const selected = finding.id === selectedId;
            return (
              <li
                key={finding.id}
                className={"action-row rail-" + tone + (selected ? " is-selected" : "")}
              >
                <button
                  type="button"
                  className="action-row__main"
                  aria-current={selected ? "true" : undefined}
                  onClick={() => onSelect(finding, "card")}
                >
                  <span className="action-row__name">{name}</span>
                  <span className="action-row__meta">
                    <span className="action-row__count">
                      {t("product.planAffected", {
                        support: (minimum ? "≥ " : "") + support,
                        total: denominator,
                      })}
                    </span>
                    <Chip tone={finding.listing_fixable ? "info" : "muted"}>
                      {t(
                        "workspace." +
                          (typeKeys[finding.finding_type] ??
                            (finding.listing_fixable ? "typeBuyerNeed" : "typeOperations")),
                      )}
                    </Chip>
                    {bucket && finding.bucket !== "to_do" && (
                      <Chip tone={bucket.tone}>{t("workspace." + bucket.key)}</Chip>
                    )}
                  </span>
                  <ChevronRight size={18} className="action-row__chevron" aria-hidden />
                </button>
                <button
                  type="button"
                  className={"btn btn--sm action-row__cta " + (meta.primary ? "btn--primary" : "btn--outline")}
                  aria-label={t("product." + meta.key) + " · " + name}
                  onClick={() => {
                    const text = action.kind === "copy" ? section?.text : null;
                    if (text) onCopy(finding, text);
                    onSelect(finding, action.focus);
                  }}
                >
                  {meta.icon}
                  {t("product." + meta.key)}
                </button>
              </li>
            );
          })}
        </ol>
      )}
    </Card>
  );
}
