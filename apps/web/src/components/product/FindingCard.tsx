import { useEffect, useId, useRef, useState, type FormEvent } from "react";
import { ArrowRight, Camera, Check, Copy, FileText, Plus, Ruler, Send } from "lucide-react";
import { request, ApiError } from "@/api/http.js";
import type { DraftSection, Finding, ProductView } from "@/api/product";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { Button, Card, Chip, Field, Notice, type Tone } from "@/components/ui";
import { buckets } from "@/components/workspace";
import { EvidenceList } from "./EvidenceList";
import {
  decisionPresets,
  draftText,
  opsBrief,
  prefersReducedMotion,
  skipReasonKey,
  type FocusStep,
} from "./actions";

const nextKeys: Record<string, string> = {
  recurrence: "nextRecurrence",
  fact: "nextFact",
  apply: "nextApply",
  draft: "nextDraft",
  route: "nextRoute",
  monitoring: "nextMonitoring",
  paste_listing: "nextPasteListing",
};
/** Tombol "Langkah berikutnya": bagian kartu yang dituju untuk setiap `finding.next`. */
const nextTargets: Record<string, FocusStep> = {
  recurrence: "evidence",
  fact: "fact",
  apply: "draft",
  draft: "draft",
  route: "decision",
  monitoring: "decision",
  paste_listing: "listing",
};
const DISMISS_REASONS = [
  ["false_positive", "falsePositive"],
  ["not_relevant", "notRelevant"],
  ["wont_fix", "wontFix"],
] as const;
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
  onListing,
}: {
  finding: Finding;
  section?: DraftSection;
  view: ProductView;
  mutate: Mutation;
  /** Permintaan fokus dari kartu "Yang perlu kamu lakukan"; nonce memicu ulang untuk langkah yang sama. */
  focus: { step: FocusStep; nonce: number } | null;
  copyNotice?: string | null;
  /** Membuka editor listing di halaman (langkah "Tempel listing saat ini"). */
  onListing?: () => void;
}) {
  const { t, language, localizeError } = useI18n();
  const { busy } = useWorkspace();
  const [value, setValue] = useState("");
  const [unit, setUnit] = useState("cm");
  const [variant, setVariant] = useState("");
  const [factError, setFactError] = useState<string | null>(null);
  const [preset, setPreset] = useState(0);
  const [detail, setDetail] = useState("");
  const [showDetail, setShowDetail] = useState(false);
  const [nextStatus, setNextStatus] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
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
  const presets = decisionPresets(finding);
  const other = preset === presets.length;
  // Catatan keputusan dirakit dari pilihan cepat + detail opsional; server tetap menyimpan catatan.
  const note = [other ? "" : t("product." + presets[preset]), detail.trim()]
    .filter(Boolean)
    .join(" — ");

  useEffect(() => {
    if (copyNotice) setCopyStatus(copyNotice);
  }, [copyNotice, focus?.nonce]);

  /** Gulir ke bagian kartu dan pindahkan fokus keyboard ke kontrol pertamanya. */
  function focusStep(step: FocusStep) {
    const behavior: ScrollBehavior = prefersReducedMotion() ? "auto" : "smooth";
    const byId = (id: string) => document.getElementById(id);
    if (step === "fact") setEditFact(true);
    let inner = 0;
    const outer = requestAnimationFrame(() => {
      inner = requestAnimationFrame(() => {
        const card = byId(cardId);
        let scrollTarget: HTMLElement | null = card;
        let focusTarget: HTMLElement | null = card;
        const fact = byId(formId + "-fact");
        const decisionStep = byId(formId + "-decision");
        const evidence = byId(formId + "-evidence");
        if (step === "fact" && fact) {
          scrollTarget = fact.closest(".finding-step");
          focusTarget = fact;
        } else if (step === "draft" && draftRef.current) {
          scrollTarget = draftRef.current;
          focusTarget = byId(formId + "-copy") ?? draftRef.current;
        } else if (step === "decision" && decisionStep) {
          scrollTarget = decisionStep;
          focusTarget =
            decisionStep.querySelector<HTMLElement>("button:not([disabled])") ?? decisionStep;
        } else if (step === "evidence" && evidence) {
          scrollTarget = evidence;
          focusTarget = evidence;
        }
        scrollTarget?.scrollIntoView({ behavior, block: "start" });
        focusTarget?.focus({ preventScroll: true });
      });
    });
    return () => {
      cancelAnimationFrame(outer);
      cancelAnimationFrame(inner);
    };
  }

  useEffect(() => {
    if (!focus) return;
    return focusStep(focus.step);
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
  async function decision(kind: string, reason = "") {
    setDecisionError(null);
    await mutate(async () => {
      try {
        return await request(url + "/decision", {
          method: "POST",
          body: { decision: kind, note: kind === "acted" ? note : "", reason },
        });
      } catch (e) {
        setDecisionError((e as ApiError).code ?? "request_failed");
        throw e;
      }
    }, "product.decisionSaved");
  }
  function generateDraft() {
    return mutate(
      () =>
        request("/deciqo/products/" + encodeURIComponent(view.product.id) + "/draft", {
          method: "POST",
        }),
      "product.draftSaved",
      "workspace.jobDrafting",
    );
  }
  /** Tombol "Langkah berikutnya" menjalankan langkah itu, bukan sekadar menyebutnya. */
  async function runNext() {
    const next = finding.next ?? "";
    setNextStatus(null);
    if (next === "paste_listing" && onListing) return onListing();
    if (next === "route") {
      try {
        await navigator.clipboard.writeText(opsBrief(finding, view, t, attribute, day));
        setNextStatus("briefCopied");
      } catch {
        setNextStatus("briefFailed");
      }
    }
    if (next === "draft" && !text) await generateDraft();
    focusStep(nextTargets[next] ?? "card");
  }
  async function sendBrief() {
    setSending(true);
    try {
      const result = (await request("/deciqo/telegram/brief", {
        method: "POST",
        body: { text: opsBrief(finding, view, t, attribute, day) },
      })) as { status: string; reason?: string };
      setNextStatus(
        result.status === "sent"
          ? "briefSent"
          : result.status === "unconfigured"
            ? "briefNoTelegram"
            : "briefSendFailed",
      );
    } catch {
      setNextStatus("briefSendFailed");
    } finally {
      setSending(false);
    }
  }
  /** Tombol "Cek foto" ada di Detail investigasi (dengan polling job-nya); buka dan jalankan. */
  function checkPhotos() {
    const details = document.getElementById("investigation-details") as HTMLDetailsElement | null;
    if (details) details.open = true;
    const button = document.getElementById("investigation-check-photos");
    button?.scrollIntoView({
      behavior: prefersReducedMotion() ? "auto" : "smooth",
      block: "center",
    });
    button?.click();
    button?.focus({ preventScroll: true });
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
  function day(value: string) {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime())
      ? value
      : parsed.toLocaleDateString(language === "id" ? "id-ID" : "en-GB", { dateStyle: "medium" });
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
          <div className="next-step-wrap">
            <button
              type="button"
              className="next-step"
              disabled={busy}
              onClick={() => void runNext()}
            >
              <span className="next-step__icon" aria-hidden>
                <ArrowRight size={18} />
              </span>
              <span className="next-step__text">
                <span className="next-step__label">{t("product.next")}</span>
                <span className="next-step__title">{t("workspace." + nextKeys[finding.next])}</span>
                <span className="next-step__hint">{t("product.nextHint_" + finding.next)}</span>
              </span>
            </button>
            <div className="next-step__after">
              <p role="status" className="next-step__status">
                {nextStatus ? t("product." + nextStatus) : ""}
              </p>
              {finding.next === "route" && nextStatus && nextStatus !== "briefSent" && (
                <Button variant="outline" size="sm" busy={sending} onClick={() => void sendBrief()}>
                  <Send size={15} aria-hidden />
                  {t("product.briefTelegram")}
                </Button>
              )}
              {nextStatus === "briefNoTelegram" && (
                <a className="next-step__link" href="#/app/settings">
                  {t("product.briefConnect")}
                </a>
              )}
            </div>
          </div>
        )}
        <section className="finding-step" id={formId + "-evidence"} tabIndex={-1}>
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
            <div className="vision-summary">
              <p>
                {vision.checked > 0
                  ? t("product.visionSummary", {
                      checked: vision.checked,
                      supports: vision.supports,
                      contradicts: vision.contradicts,
                    })
                  : vision.skipped_reason === "not_run"
                    ? t("product.photosNotRun")
                    : t("product.visionSkipped", {
                        reason: t(skipReasonKey(vision.skipped_reason)),
                      })}
                {vision.checked > 0 && <span className="muted"> · {t("product.visionHint")}</span>}
              </p>
              {vision.checked === 0 &&
                vision.skipped_reason === "not_run" &&
                metrics.with_photos > 0 && (
                  <Button variant="outline" size="sm" onClick={checkPhotos}>
                    <Camera size={15} aria-hidden />
                    {t("product.checkPhotos")}
                  </Button>
                )}
            </div>
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
                <div className="draft-empty">
                  <p className="muted">
                    {t(
                      status === "needs_review"
                        ? "product.draftReview"
                        : status === "needs_merchant_fact" || status === "needs_listing"
                          ? "product.draftHeld"
                          : "product.draftPending",
                    )}
                  </p>
                  {status !== "needs_merchant_fact" && status !== "needs_listing" && (
                    <Button variant="outline" size="sm" busy={busy} onClick={() => void generateDraft()}>
                      <FileText size={15} aria-hidden />
                      {t("product.generateDraft")}
                    </Button>
                  )}
                </div>
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
        <section className="finding-step" id={formId + "-decision"} tabIndex={-1}>
          <h3>{t("product.stepDecision")}</h3>
          {["acted", "dismissed"].includes(finding.state) ? (
            <div className="decision-done">
              <Button variant="outline" busy={busy} onClick={() => void decision("reopened")}>
                {t("product.reopen")}
              </Button>
            </div>
          ) : (
            <div className="decision">
              <fieldset className="decision__picks">
                <legend>{t("product.decisionWhat")}</legend>
                <div className="pick-row">
                  {[...presets, "doneOther"].map((key, index) => (
                    <button
                      key={key}
                      type="button"
                      className="pick"
                      aria-pressed={preset === index}
                      onClick={() => {
                        setPreset(index);
                        if (index === presets.length) {
                          setShowDetail(true);
                          requestAnimationFrame(() =>
                            document.getElementById(formId + "-note")?.focus(),
                          );
                        }
                      }}
                    >
                      {preset === index && <Check size={14} aria-hidden />}
                      {t("product." + key)}
                    </button>
                  ))}
                </div>
              </fieldset>
              {showDetail || other ? (
                <div className="field decision__detail">
                  <label htmlFor={formId + "-note"}>
                    {t(other ? "product.detailRequired" : "product.detailOptional")}
                  </label>
                  <textarea
                    id={formId + "-note"}
                    rows={2}
                    maxLength={900}
                    value={detail}
                    placeholder={t("product.detailPlaceholder")}
                    onChange={(event) => setDetail(event.target.value)}
                  />
                </div>
              ) : (
                <button type="button" className="decision__add" onClick={() => setShowDetail(true)}>
                  <Plus size={14} aria-hidden />
                  {t("product.addDetail")}
                </button>
              )}
              <div className="decision__actions">
                <Button busy={busy} disabled={!note} onClick={() => void decision("acted")}>
                  <Check size={16} aria-hidden />
                  {t("product.markDone")}
                </Button>
                <p className="muted decision__follow">{t("product.decisionFollow")}</p>
              </div>
              <div className="decision__dismiss">
                <span className="muted">{t("product.dismissLead")}</span>
                {DISMISS_REASONS.map(([value, key]) => (
                  <Button
                    key={value}
                    variant="text"
                    size="sm"
                    busy={busy}
                    onClick={() => void decision("dismissed", value)}
                  >
                    {t("product." + key)}
                  </Button>
                ))}
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
