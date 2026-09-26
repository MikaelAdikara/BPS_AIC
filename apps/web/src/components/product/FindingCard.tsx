import { useEffect, useId, useRef, useState, type FormEvent } from "react";
import { Copy, Ruler } from "lucide-react";
import { request, ApiError } from "@/api/http.js";
import type { DraftSection, Finding, ProductView } from "@/api/product";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { Button, Card, Chip, Field, Notice, type Tone } from "@/components/ui";
import { buckets } from "@/components/workspace";
import { EvidenceList } from "./EvidenceList";
import { draftText, prefersReducedMotion, skipReasonKey, type FocusStep } from "./actions";

const nextKeys: Record<string, string> = {
  recurrence: "nextRecurrence",
  fact: "nextFact",
  apply: "nextApply",
  draft: "nextDraft",
  route: "nextRoute",
  monitoring: "nextMonitoring",
  paste_listing: "nextPasteListing",
};
const checks: Record<string, { key: string; tone: Tone }> = {
  not_provided: { key: "checkNotProvided", tone: "warn" },
  pending: { key: "checkPending", tone: "muted" },
  evidence_found: { key: "checkFound", tone: "good" },
  not_found_in_checked_content: { key: "checkNotFound", tone: "warn" },
  verification_failed: { key: "checkFailed", tone: "muted" },
  incomplete_source: { key: "checkIncomplete", tone: "muted" },
  conflicting: { key: "checkConflict", tone: "warn" },
  not_applicable: { key: "checkNotApplicable", tone: "muted" },
};
const drafts: Record<string, { key: string; tone: Tone }> = {
  ready: { key: "ready", tone: "good" },
  needs_review: { key: "needsReview", tone: "warn" },
  needs_merchant_fact: { key: "needsFact", tone: "warn" },
  needs_listing: { key: "needsListing", tone: "warn" },
  blocked: { key: "blocked", tone: "alert" },
  nothing_to_draft: { key: "nothing", tone: "muted" },
};
const reasons: Record<string, string> = {
  missing_fact: "reasonMissing",
  listing_not_provided: "reasonListing",
  missing_listing: "reasonListing",
  unsupported_quantity: "reasonUnsupported",
  unsupported_claim: "reasonUnsupported",
  placeholder: "reasonPlaceholder",
  already_in_listing: "reasonAlreadyListing",
  nothing_rendered: "reasonNothingRendered",
};
const rejectedReasons: Record<string, string> = {
  quote_not_verbatim: "rejectedQuote",
  unknown_review_id: "rejectedUnknown",
  quote_too_short: "rejectedShort",
  labelled_both_ways: "rejectedConflict",
  wrong_item_routes_to_operations: "rejectedRoute",
  also_reports_wrong_variant: "rejectedRoute",
  complaint_not_about_this_attribute: "rejectedRelevance",
  not_about_this_attribute: "rejectedRelevance",
  complaint_without_attribute: "rejectedRelevance",
};

export type Mutation = (
  task: () => Promise<unknown>,
  success: string,
  label?: string,
) => Promise<void>;

export function FindingCard({
  finding,
  section,
  view,
  mutate,
  focus,
  copyNotice,
}: {
  finding: Finding;
  section?: DraftSection;
  view: ProductView;
  mutate: Mutation;
  /** Permintaan fokus dari kartu "Yang perlu kamu lakukan"; nonce memicu ulang untuk langkah yang sama. */
  focus: { step: FocusStep; nonce: number } | null;
  copyNotice?: string | null;
}) {
  const { t, language, localizeError } = useI18n();
  const { busy } = useWorkspace();
  const [value, setValue] = useState("");
  const [unit, setUnit] = useState("cm");
  const [variant, setVariant] = useState("");
  const [factError, setFactError] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [reason, setReason] = useState("");
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const [editFact, setEditFact] = useState(false);
  const formId = useId();
  const cardId = "finding-" + finding.id;
  const draftRef = useRef<HTMLElement>(null);
  const check = checks[finding.listing_check?.status] ?? checks.pending;
  const coverage = finding.listing_check?.coverage;
  const status =
    section?.status ??
    (finding.draft_status === "ready" ? null : finding.draft_status);
  const draft = status ? drafts[status] : null;
  const bucket = buckets[finding.bucket];
  const metrics = finding.metrics;
  const follow = finding.follow_up;
  const vision = finding.vision_summary;
  const text = draftText(section);
  const url = "/deciqo/findings/" + encodeURIComponent(finding.id);
  const attribute = language === "id" ? finding.attribute_local : finding.attribute;

  useEffect(() => {
    if (copyNotice) setCopyStatus(copyNotice);
  }, [copyNotice, focus?.nonce]);

  useEffect(() => {
    if (!focus) return;
    const behavior: ScrollBehavior = prefersReducedMotion() ? "auto" : "smooth";
    const byId = (id: string) => document.getElementById(id);
    if (focus.step === "fact") setEditFact(true);
    let inner = 0;
    const outer = requestAnimationFrame(() => {
      inner = requestAnimationFrame(() => {
        const card = byId(cardId);
        let scrollTarget: HTMLElement | null = card;
        let focusTarget: HTMLElement | null = card;
        const fact = byId(formId + "-fact");
        const note = byId(formId + "-note");
        if (focus.step === "fact" && fact) {
          scrollTarget = fact.closest(".finding-step");
          focusTarget = fact;
        } else if (focus.step === "draft" && draftRef.current) {
          scrollTarget = draftRef.current;
          focusTarget = byId(formId + "-copy") ?? draftRef.current;
        } else if (focus.step === "decision" && note) {
          focusTarget = note;
        }
        scrollTarget?.scrollIntoView({ behavior, block: "start" });
        focusTarget?.focus({ preventScroll: true });
      });
    });
    return () => {
      cancelAnimationFrame(outer);
      cancelAnimationFrame(inner);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focus?.nonce]);

  async function saveFact(event: FormEvent) {
    event.preventDefault();
    setFactError(null);
    await mutate(async () => {
      try {
        return await request(url + "/fact", {
          method: "POST",
          body: { value, unit, variant },
        });
      } catch (e) {
        setFactError((e as ApiError).code ?? "request_failed");
        throw e;
      }
    }, "product.factSaved");
  }
  async function decision(kind: string) {
    setDecisionError(null);
    await mutate(async () => {
      try {
        return await request(url + "/decision", {
          method: "POST",
          body: { decision: kind, note, reason },
        });
      } catch (e) {
        setDecisionError((e as ApiError).code ?? "request_failed");
        throw e;
      }
    }, "product.decisionSaved");
  }
  async function copy() {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus("copied");
    } catch {
      setCopyStatus("copyFailed");
    }
  }
  function date(value: string) {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime())
      ? value
      : parsed.toLocaleString(language === "id" ? "id-ID" : "en-GB");
  }
  const percent = new Intl.NumberFormat(language === "id" ? "id-ID" : "en-GB", {
    style: "percent",
    maximumFractionDigits: 1,
  }).format(metrics.share ?? 0);
  const showFactForm = !finding.fact || editFact;

  return (
    <Card
      id={cardId}
      tabIndex={-1}
      className="finding-card"
      title={attribute}
      lead={finding.buyer_expectation}
    >
      <div className="stack">
        <div className="utility-bar">
          {bucket && <Chip tone={bucket.tone}>{t("workspace." + bucket.key)}</Chip>}
          {finding.engine === "rules" && <Chip>{t("product.ruleMode")}</Chip>}
          {metrics.support === 1 && <Chip>{t("product.singleReport")}</Chip>}
        </div>
        {finding.next && nextKeys[finding.next] && (
          <div className="next-step" aria-live="polite">
            <strong>{t("product.next")}</strong>
            <p>{t("workspace." + nextKeys[finding.next])}</p>
          </div>
        )}
        <section className="finding-step">
          <h3>{t("product.stepEvidence")}</h3>
          <dl className="evidence-stats">
            <div>
              <dt>{t("product.support")}</dt>
              <dd className="count">
                {metrics.support_is_minimum ? "≥ " : ""}
                {metrics.support} / {metrics.denominator}
              </dd>
            </div>
            <div>
              <dt>{t("product.opposite")}</dt>
              <dd className="count">{metrics.contradicting}</dd>
            </div>
            <div>
              <dt>{t("product.hidden")}</dt>
              <dd className="count">{metrics.hidden_high_star}</dd>
            </div>
            <div>
              <dt>{t("product.photos")}</dt>
              <dd className="count">{metrics.with_photos}</dd>
            </div>
          </dl>
          <p className="muted finding-step__note">
            {t(metrics.support_is_minimum ? "product.shareCandidates" : "product.share", {
              share: percent,
            })}
            {" · "}
            {metrics.support_is_minimum
              ? t("product.minimum", {
                  read: metrics.candidates_read,
                  total: metrics.denominator,
                })
              : t("product.coverage", { count: metrics.denominator })}
          </p>
          {vision && (vision.checked > 0 || vision.skipped_reason) && (
            <p className="vision-summary">
              {vision.checked > 0
                ? t("product.visionSummary", {
                    checked: vision.checked,
                    supports: vision.supports,
                    contradicts: vision.contradicts,
                  })
                : t("product.visionSkipped", { reason: t(skipReasonKey(vision.skipped_reason)) })}
              {vision.checked > 0 && <span className="muted"> · {t("product.visionHint")}</span>}
            </p>
          )}
          <EvidenceList evidence={finding.evidence} formatDate={date} />
          {metrics.support > finding.evidence.length && (
            <p className="muted finding-step__note">{t("product.moreEvidence")}</p>
          )}
          {finding.uncertain > 0 && (
            <p className="muted finding-step__note">
              {t("product.uncertain", { count: finding.uncertain })}
            </p>
          )}
          <details>
            <summary>{t("product.moreMetrics")}</summary>
            <div className="evidence-stats evidence-stats--two">
              <div>
                <dt>{t("product.ratingNow")}</dt>
                <dd className="count">{metrics.rating_now ?? "—"}</dd>
              </div>
              <div>
                <dt>{t("product.ratingWithout")}</dt>
                <dd className="count">{metrics.rating_without ?? "—"}</dd>
              </div>
            </div>
            <p className="muted">{t("product.ratingHint")}</p>
            {(metrics.variants?.length ?? 0) > 0 && (
              <ul>
                {metrics.variants!.map((item) => (
                  <li key={item.variant}>
                    {item.variant} · {t("product.variantCount", { count: item.complaints })}
                    {item.exploratory && " · " + t("product.variantExploratory")}
                  </li>
                ))}
              </ul>
            )}
          </details>
          {finding.rejected.length > 0 && (
            <details>
              <summary>{t("product.rejected")}</summary>
              <ul>
                {finding.rejected.map((item, index) => (
                  <li key={item.review_id + index}>
                    {item.review_id} ·{" "}
                    {t("product." + (rejectedReasons[item.reason] ?? "rejectedGeneral"))}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </section>
        <section className="finding-step">
          <h3>{t("product.stepListing")}</h3>
          <Chip tone={check.tone}>{t("product." + check.key)}</Chip>
          {finding.listing_check?.quote && (
            <blockquote className="quote">
              <p>“{finding.listing_check.quote}”</p>
            </blockquote>
          )}
          {(finding.listing_check?.related?.length ?? 0) > 0 && (
            <details>
              <summary>{t("product.related")}</summary>
              {finding.listing_check.related.map((item, index) => (
                <blockquote className="quote" key={index}>
                  “{item}”
                </blockquote>
              ))}
            </details>
          )}
          {coverage && (
            <p className="muted finding-step__note">
              {t("product.checkCoverage", {
                checked: coverage.chars_checked,
                total: coverage.chars_total,
                images: coverage.images_read,
                imageTotal: coverage.images_total,
              })}
              {coverage.model_chars != null &&
                " " +
                  t("product.modelCoverage", {
                    count: coverage.model_chars,
                    total: coverage.chars_total,
                  })}
            </p>
          )}
        </section>
        {finding.listing_fixable ? (
          <>
            <section className="finding-step finding-step--fact">
              <h3>{t("product.stepFact")}</h3>
              {finding.fact && (
                <Notice tone="good">
                  <p className="count">
                    {finding.fact.value} {finding.fact.unit}
                    {finding.fact.variant ? " · " + finding.fact.variant : ""}
                  </p>
                  <p>{t("product.factTime", { time: date(finding.fact.confirmed_at) })}</p>
                </Notice>
              )}
              {finding.fact && !editFact && (
                <Button variant="text" size="sm" onClick={() => setEditFact(true)}>
                  {t("product.changeFact")}
                </Button>
              )}
              <form
                className="stack fact-form"
                hidden={!showFactForm}
                onSubmit={(event) => void saveFact(event)}
              >
                <p>{t("product.factQuestion", { attribute })}</p>
                {language === "id" && finding.merchant_question && (
                  <p className="muted">{finding.merchant_question}</p>
                )}
                <div className="fact-fields">
                  <Field
                    id={formId + "-fact"}
                    label={t("product.factValue")}
                    value={value}
                    required
                    maxLength={256}
                    onChange={(event) => setValue(event.target.value)}
                    hint={t("product.factHint")}
                    error={factError ? localizeError(factError) : undefined}
                  />
                  <div className="field">
                    <label htmlFor={formId + "-unit"}>{t("product.factUnit")}</label>
                    <select
                      id={formId + "-unit"}
                      value={unit}
                      onChange={(event) => setUnit(event.target.value)}
                    >
                      <option value="">{t("product.noUnit")}</option>
                      {["cm", "mm", "m", "inch", "g", "kg", "ml", "mAh", "W", "V"].map((item) => (
                        <option key={item}>{item}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <Field
                  label={t("product.factVariant")}
                  value={variant}
                  maxLength={100}
                  onChange={(event) => setVariant(event.target.value)}
                />
                <Button type="submit" busy={busy}>
                  <Ruler size={16} aria-hidden />
                  {t("product.confirm")}
                </Button>
              </form>
            </section>
            <section className="finding-step finding-step--draft" ref={draftRef} tabIndex={-1}>
              <h3>{t("product.stepDraft")}</h3>
              {draft && <Chip tone={draft.tone}>{t("product." + draft.key)}</Chip>}
              {text ? (
                <>
                  <div className="draft-text">{text}</div>
                  <div className="draft-actions">
                    <Button id={formId + "-copy"} onClick={() => void copy()}>
                      <Copy size={16} aria-hidden />
                      {t("product.copy")}
                    </Button>
                    {section?.rendered_from === "merchant_fact" && (
                      <span className="muted">{t("product.draftFromFact")}</span>
                    )}
                  </div>
                </>
              ) : (
                <p className="muted">
                  {t(
                    status === "needs_review"
                      ? "product.draftReview"
                      : status === "needs_merchant_fact" || status === "needs_listing"
                        ? "product.draftHeld"
                        : "product.draftPending",
                  )}
                </p>
              )}
              <p role="status" className="draft-status">
                {copyStatus ? t("product." + copyStatus) : ""}
              </p>
              {section && section.reasons.length > 0 && (
                <ul>
                  {section.reasons.map((item, index) => (
                    <li key={index}>{t("product." + (reasons[item] ?? "reasonUnsupported"))}</li>
                  ))}
                </ul>
              )}
              <p className="muted finding-step__note">{t("product.manualApply")}</p>
            </section>
          </>
        ) : (
          <Notice tone="info">{t("product.opsHint")}</Notice>
        )}
        <section className="finding-step">
          <h3>{t("product.stepDecision")}</h3>
          {["acted", "dismissed"].includes(finding.state) ? (
            <Button variant="outline" busy={busy} onClick={() => void decision("reopened")}>
              {t("product.reopen")}
            </Button>
          ) : (
            <div className="decision-grid">
              <div className="stack">
                <div className="field">
                  <label htmlFor={formId + "-note"}>{t("product.decisionNote")}</label>
                  <textarea
                    id={formId + "-note"}
                    rows={3}
                    maxLength={2000}
                    value={note}
                    onChange={(event) => setNote(event.target.value)}
                    aria-describedby={formId + "-note-hint"}
                  />
                  <p id={formId + "-note-hint"} className="field__hint">
                    {t("product.noteHint")}
                  </p>
                </div>
                <Button busy={busy} disabled={!note.trim()} onClick={() => void decision("acted")}>
                  {t("product.applied")}
                </Button>
              </div>
              <div className="stack">
                <div className="field">
                  <label htmlFor={formId + "-reason"}>{t("product.reason")}</label>
                  <select
                    id={formId + "-reason"}
                    value={reason}
                    onChange={(event) => setReason(event.target.value)}
                  >
                    <option value="">{t("product.chooseReason")}</option>
                    <option value="false_positive">{t("product.falsePositive")}</option>
                    <option value="not_relevant">{t("product.notRelevant")}</option>
                    <option value="wont_fix">{t("product.wontFix")}</option>
                  </select>
                </div>
                <Button
                  variant="outline"
                  disabled={!reason}
                  busy={busy}
                  onClick={() => void decision("dismissed")}
                >
                  {t("product.dismiss")}
                </Button>
              </div>
            </div>
          )}
          {decisionError && <Notice tone="alert">{localizeError(decisionError)}</Notice>}
          {follow && (
            <Notice
              tone={
                follow.state === "recurrence"
                  ? "alert"
                  : follow.state === "no_recurrence_observed"
                    ? "good"
                    : "muted"
              }
            >
              <strong>
                {t(
                  "product." +
                    (follow.state === "recurrence"
                      ? "followRecurrence"
                      : follow.state === "no_recurrence_observed"
                        ? "followQuiet"
                        : "followWaiting"),
                )}
              </strong>
              <p>
                {t("product.followCounts", {
                  time: date(follow.acted_at),
                  after: follow.after,
                  complaints: follow.complaints,
                })}
              </p>
              <p>{t("product.followUndated", { count: follow.undated })}</p>
            </Notice>
          )}
          <details>
            <summary>{t("product.history")}</summary>
            <ul>
              {view.decisions
                .filter((item) => item.finding_id === finding.id)
                .map((item, index) => (
                  <li key={index}>
                    <strong>
                      {t(
                        "product." +
                          (item.decision === "acted"
                            ? "applied"
                            : item.decision === "dismissed"
                              ? "dismiss"
                              : "reopen"),
                      )}
                    </strong>{" "}
                    · {date(item.created_at)}
                    <p>{item.note}</p>
                    {item.reason && (
                      <p>
                        {t(
                          "product." +
                            ({
                              false_positive: "falsePositive",
                              not_relevant: "notRelevant",
                              wont_fix: "wontFix",
                            }[item.reason] ?? "reason"),
                        )}
                      </p>
                    )}
                  </li>
                ))}
            </ul>
          </details>
        </section>
      </div>
    </Card>
  );
}
