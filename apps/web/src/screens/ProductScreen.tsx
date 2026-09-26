import {
  useCallback,
  useEffect,
  useRef,
  useState,
  useId,
  type FormEvent,
} from "react";
import { Copy, ExternalLink, FileText, Ruler } from "lucide-react";
import { request, ApiError } from "@/api/http.js";
import type { ProductView, Finding, DraftSection } from "@/api/product";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import {
  Button,
  Card,
  Chip,
  EmptyState,
  Field,
  LoadingState,
  Metric,
  Notice,
  Quote,
  type Tone,
} from "@/components/ui";
import { buckets } from "@/components/workspace";
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
  const [filter, setFilter] = useState("all");
  const aborter = useRef<AbortController | null>(null);
  const version = useRef(0);
  const listingId = useId();
  const load = useCallback(async () => {
    const current = ++version.current;
    aborter.current?.abort();
    const controller = new AbortController();
    aborter.current = controller;
    setLoading(true);
    setError(null);
    try {
      const result = (await request(
        "/deciqo/products/" + encodeURIComponent(productId),
        { signal: controller.signal },
      )) as ProductView;
      if (current !== version.current) return;
      setView(result);
      setListing(result.product.listing_text ?? "");
    } catch (e) {
      if (current === version.current && !controller.signal.aborted)
        setError((e as ApiError).code ?? "request_failed");
    } finally {
      if (current === version.current) setLoading(false);
    }
  }, [productId]);
  useEffect(() => {
    void load();
    return () => {
      version.current++;
      aborter.current?.abort();
    };
  }, [load]);
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
  if (loading)
    return (
      <>
        <h1>{t("common.products")}</h1>
        <LoadingState />
      </>
    );
  if (error || !view)
    return (
      <>
        <h1>{t("product.loadError")}</h1>
        <Notice tone="alert">{localizeError(error ?? "request_failed")}</Notice>
        <Button onClick={() => void load()}>{t("common.retry")}</Button>
      </>
    );
  const product = view.product;
  const link = externalUrl(product.url);
  const origin = product.synthetic
    ? "originSynthetic"
    : [
          "public",
          "public_snapshot",
          "lazada_public",
          "research_dataset",
          "team_collected",
        ].includes(product.data_origin)
      ? "originPublic"
      : "originChannel";
  const visible = view.findings.filter(
    (finding) =>
      filter === "all" ||
      (filter === "listing"
        ? finding.listing_fixable
        : !finding.listing_fixable),
  );
  const finding =
    visible.find((item) => item.id === query.get("f")) ?? visible[0];
  return (
    <>
      <a href="#/app/listings">{t("product.back")}</a>
      <header className="page-header">
        <div className="stack">
          <h1>{product.title}</h1>
          <div className="utility-bar">
            <span>{product.channel}</span>
            {product.synthetic && <Chip synthetic />}
            {view.analysis?.engine === "rules" && (
              <Chip>{t("product.ruleMode")}</Chip>
            )}
          </div>
          <p className="muted">
            {t("product." + origin)}
            {product.captured_at
              ? " · " +
                t("product.captured", { time: date(product.captured_at) })
              : ""}
          </p>
          <p>
            {t("product.reviews", {
              reviews: view.stats.reviews,
              photos: view.stats.with_photos,
            })}
          </p>
        </div>
        {link && (
          <a
            className="btn btn--outline"
            href={link}
            target="_blank"
            rel="noopener noreferrer"
          >
            {t("product.live")}
            <ExternalLink size={16} aria-hidden />
          </a>
        )}
      </header>
      {workspace.error && (
        <Notice tone="alert">{localizeError(workspace.error)}</Notice>
      )}
      {view.analysis?.status === "failed" && (
        <Notice tone="warn">{t("product.analysisFailed")}</Notice>
      )}
      {!product.listing_provided && (
        <Card title={t("product.listingTitle")} lead={t("product.listingHint")}>
          <form
            className="stack"
            onSubmit={(event) => {
              event.preventDefault();
              void mutate(
                () =>
                  request(
                    "/deciqo/products/" +
                      encodeURIComponent(productId) +
                      "/listing",
                    { method: "PUT", body: { listing } },
                  ),
                "product.listingSaved",
                "workspace.jobAnalysing",
              );
            }}
          >
            <div className="field">
              <label htmlFor={listingId}>{t("product.listingField")}</label>
              <textarea
                id={listingId}
                rows={5}
                required
                value={listing}
                onChange={(event) => setListing(event.target.value)}
              />
            </div>
            <Button type="submit" busy={workspace.busy}>
              {t("product.saveListing")}
            </Button>
          </form>
        </Card>
      )}
      <Card
        title={t("product.pipeline")}
        lead={t("product.pipelineLead")}
        action={
          <Button
            busy={workspace.busy}
            onClick={() =>
              void mutate(
                () =>
                  request(
                    "/deciqo/products/" +
                      encodeURIComponent(productId) +
                      "/analyse",
                    { method: "POST", body: { force: true } },
                  ),
                "product.analyseSaved",
                "workspace.jobAnalysing",
              )
            }
          >
            {t(view.analysis ? "product.rerun" : "product.investigate")}
          </Button>
        }
      >
        {view.analysis ? (
          <ul className="pipeline-list">
            {view.analysis.trace.map((stage, index) => {
              const key = String(stage.stage);
              let detail = "";
              if (key === "triage")
                detail = t("product.stageKept", {
                  kept: stage.kept,
                  total: stage.of,
                });
              if (key === "discovery")
                detail = t("product.stageProposed", { count: stage.proposed });
              if (key === "membership")
                detail = t("product.stageLabelled", { count: stage.labelled });
              if (key === "verifier")
                detail = t("product.stageVerifier", {
                  kept: stage.kept,
                  dropped: stage.dropped,
                  quotes: stage.quotes_rejected,
                });
              if (key === "gate")
                detail = t("product.stageGate", {
                  blocked: stage.blocked ?? "—",
                  facts: stage.need_fact ?? "—",
                });
              return (
                <li key={index}>
                  <strong>
                    {t(
                      "product." +
                        ([
                          "triage",
                          "discovery",
                          "membership",
                          "verifier",
                          "gate",
                        ].includes(key)
                          ? key
                          : "pipeline"),
                    )}
                  </strong>
                  <span className="count">{detail}</span>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="muted">{t("product.notAnalysed")}</p>
        )}
      </Card>
      <div className="page-header">
        <div
          className="issue-tabs"
          role="group"
          aria-label={t("product.findings")}
        >
          {[
            ["all", "filterAll"],
            ["listing", "filterListing"],
            ["ops", "filterOps"],
          ].map(([value, key]) => (
            <button
              className="btn btn--text"
              aria-pressed={filter === value}
              key={value}
              onClick={() => setFilter(value)}
            >
              {t("product." + key)}
            </button>
          ))}
        </div>
        <Button
          busy={workspace.busy}
          onClick={() =>
            void mutate(
              () =>
                request(
                  "/deciqo/products/" +
                    encodeURIComponent(productId) +
                    "/draft",
                  { method: "POST" },
                ),
              "product.draftSaved",
              "workspace.jobDrafting",
            )
          }
        >
          <FileText size={16} aria-hidden />
          {t("product.draftAll")}
        </Button>
      </div>
      {view.findings.length === 0 ? (
        <Card>
          <EmptyState
            title={t("product.noFindings")}
            description={t("product.noFindingsHint")}
          />
        </Card>
      ) : (
        <>
          <nav className="finding-picker" aria-label={t("product.findings")}>
            {visible.map((item) => (
              <a
                key={item.id}
                className="btn btn--outline"
                href={
                  "#/app/listings/" +
                  encodeURIComponent(productId) +
                  "?f=" +
                  encodeURIComponent(item.id)
                }
                aria-current={finding?.id === item.id ? "true" : undefined}
              >
                {language === "id" ? item.attribute_local : item.attribute}
              </a>
            ))}
          </nav>
          {finding ? (
            <FindingCard
              key={finding.id}
              finding={finding}
              section={view.draft?.sections.find(
                (section) => section.finding_id === finding.id,
              )}
              view={view}
              mutate={mutate}
            />
          ) : (
            <EmptyState
              title={t("product.noSelected")}
              description={t("product.noFindingsHint")}
            />
          )}
        </>
      )}
      {view.not_detected.length > 0 && (
        <Card title={t("product.notDetected")}>
          <ul>
            {view.not_detected.map((item) => (
              <li key={item.id}>{item.attribute_local}</li>
            ))}
          </ul>
        </Card>
      )}
    </>
  );
}
type Mutation = (
  task: () => Promise<unknown>,
  success: string,
  label?: string,
) => Promise<void>;
function FindingCard({
  finding,
  section,
  view,
  mutate,
}: {
  finding: Finding;
  section?: DraftSection;
  view: ProductView;
  mutate: Mutation;
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
  const formId = useId();
  const check = checks[finding.listing_check.status] ?? checks.pending;
  const coverage = finding.listing_check.coverage;
  const status =
    section?.status ??
    (finding.draft_status === "ready" ? null : finding.draft_status);
  const draft = status ? drafts[status] : null;
  const bucket = buckets[finding.bucket];
  const metrics = finding.metrics;
  const follow = finding.follow_up;
  const url = "/deciqo/findings/" + encodeURIComponent(finding.id);
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
  function date(value: string) {
    return new Date(value).toLocaleString(
      language === "id" ? "id-ID" : "en-GB",
    );
  }
  return (
    <Card
      title={language === "id" ? finding.attribute_local : finding.attribute}
      lead={finding.buyer_expectation}
    >
      <div className="stack">
        <div className="utility-bar">
          {bucket && (
            <Chip tone={bucket.tone}>{t("workspace." + bucket.key)}</Chip>
          )}
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
          <div className="evidence-metrics">
            <Metric
              label={t("product.support")}
              value={
                <>
                  {metrics.support_is_minimum ? "≥ " : ""}
                  {metrics.support} / {metrics.denominator}
                </>
              }
            />
            <Metric
              label={t("product.opposite")}
              value={metrics.contradicting}
            />
            <Metric
              label={t("product.hidden")}
              value={metrics.hidden_high_star}
            />
            <Metric label={t("product.photos")} value={metrics.with_photos} />
          </div>
          <p className="muted">
            {metrics.support_is_minimum
              ? t("product.minimum", {
                  read: metrics.candidates_read,
                  total: metrics.denominator,
                })
              : t("product.coverage", { count: metrics.denominator })}
          </p>
          <p className="muted">
            {t("product.share", {
              share: new Intl.NumberFormat(
                language === "id" ? "id-ID" : "en-GB",
                { style: "percent", maximumFractionDigits: 1 },
              ).format(metrics.share),
            })}
          </p>
          <div className="stack">
            {finding.evidence.slice(0, 6).map((evidence, index) => (
              <Quote
                key={evidence.review_id + index}
                text={evidence.quote}
                reviewId={evidence.review_id}
                rating={evidence.rating}
                date={evidence.review_time ? date(evidence.review_time) : null}
                variant={evidence.variant}
              />
            ))}
          </div>
          {metrics.support > finding.evidence.slice(0, 6).length && (
            <p className="muted">{t("product.moreEvidence")}</p>
          )}
          {finding.uncertain > 0 && (
            <p className="muted">
              {t("product.uncertain", { count: finding.uncertain })}
            </p>
          )}
          {finding.rejected.length > 0 && (
            <details>
              <summary>{t("product.rejected")}</summary>
              <ul>
                {finding.rejected.map((item, index) => (
                  <li key={item.review_id + index}>
                    {item.review_id} ·{" "}
                    {t(
                      "product." +
                        (rejectedReasons[item.reason] ?? "rejectedGeneral"),
                    )}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </section>
        <section className="finding-step">
          <h3>{t("product.stepListing")}</h3>
          <Chip tone={check.tone}>{t("product." + check.key)}</Chip>
          {finding.listing_check.quote && (
            <blockquote className="quote">
              <p>“{finding.listing_check.quote}”</p>
            </blockquote>
          )}
          {finding.listing_check.related?.length > 0 && (
            <details>
              <summary>{t("product.related")}</summary>
              {finding.listing_check.related.map((text, index) => (
                <blockquote className="quote" key={index}>
                  “{text}”
                </blockquote>
              ))}
            </details>
          )}
          {coverage && (
            <p className="muted">
              {t("product.checkCoverage", {
                checked: coverage.chars_checked,
                total: coverage.chars_total,
                images: coverage.images_read,
                imageTotal: coverage.images_total,
              })}
            </p>
          )}
        </section>
        {finding.listing_fixable ? (
          <>
            <section className="finding-step">
              <h3>{t("product.stepFact")}</h3>
              {finding.fact && (
                <Notice tone="good">
                  <p className="count">
                    {finding.fact.value} {finding.fact.unit}
                    {finding.fact.variant ? " · " + finding.fact.variant : ""}
                  </p>
                  <p>
                    {t("product.factTime", {
                      time: date(finding.fact.confirmed_at),
                    })}
                  </p>
                  <p>{t("product.factSaved")}</p>
                </Notice>
              )}
              <form
                className="stack"
                onSubmit={(event) => void saveFact(event)}
              >
                <p>
                  {t("product.factQuestion", {
                    attribute:
                      language === "id"
                        ? finding.attribute_local
                        : finding.attribute,
                  })}
                </p>
                {language === "id" && finding.merchant_question && (
                  <p className="muted">{finding.merchant_question}</p>
                )}
                <Field
                  label={t("product.factValue")}
                  value={value}
                  required
                  maxLength={256}
                  onChange={(event) => setValue(event.target.value)}
                  hint={t("product.factHint")}
                  error={factError ? localizeError(factError) : undefined}
                />
                <div className="fact-fields">
                  <div className="field">
                    <label htmlFor={formId + "-unit"}>
                      {t("product.factUnit")}
                    </label>
                    <select
                      id={formId + "-unit"}
                      value={unit}
                      onChange={(event) => setUnit(event.target.value)}
                    >
                      <option value="">{t("product.noUnit")}</option>
                      {[
                        "cm",
                        "mm",
                        "m",
                        "inch",
                        "g",
                        "kg",
                        "ml",
                        "mAh",
                        "W",
                        "V",
                      ].map((item) => (
                        <option key={item}>{item}</option>
                      ))}
                    </select>
                  </div>
                  <Field
                    label={t("product.factVariant")}
                    value={variant}
                    maxLength={100}
                    onChange={(event) => setVariant(event.target.value)}
                  />
                </div>
                <Button type="submit" busy={busy}>
                  <Ruler size={16} aria-hidden />
                  {t("product.confirm")}
                </Button>
              </form>
            </section>
            <section className="finding-step">
              <h3>{t("product.stepDraft")}</h3>
              {draft && (
                <Chip tone={draft.tone}>{t("product." + draft.key)}</Chip>
              )}
              {section?.text &&
              ["ready", "needs_review"].includes(section.status) ? (
                <>
                  <div className="draft-text">{section.text}</div>
                  <Button
                    variant="outline"
                    onClick={async () => {
                      try {
                        await navigator.clipboard.writeText(section.text);
                        setCopyStatus("copied");
                      } catch {
                        setCopyStatus("copyFailed");
                      }
                    }}
                  >
                    <Copy size={16} aria-hidden />
                    {t("product.copy")}
                  </Button>
                  {section.rendered_from === "merchant_fact" && (
                    <p className="muted">{t("product.draftFromFact")}</p>
                  )}
                </>
              ) : (
                <p className="muted">
                  {t(
                    status === "needs_merchant_fact" ||
                      status === "needs_listing"
                      ? "product.draftHeld"
                      : "product.draftPending",
                  )}
                </p>
              )}
              {copyStatus && <p role="status">{t("product." + copyStatus)}</p>}
              {section && section.reasons.length > 0 && (
                <ul>
                  {section.reasons.map((reason, index) => (
                    <li key={index}>
                      {t("product." + (reasons[reason] ?? "reasonUnsupported"))}
                    </li>
                  ))}
                </ul>
              )}
              <p className="muted">{t("product.manualApply")}</p>
            </section>
          </>
        ) : (
          <Notice tone="info">{t("product.opsHint")}</Notice>
        )}
        <section className="finding-step">
          <h3>{t("product.stepDecision")}</h3>
          {["acted", "dismissed"].includes(finding.state) ? (
            <Button
              variant="outline"
              busy={busy}
              onClick={() => void decision("reopened")}
            >
              {t("product.reopen")}
            </Button>
          ) : (
            <>
              <div className="field">
                <label htmlFor={formId + "-note"}>
                  {t("product.decisionNote")}
                </label>
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
              <Button
                busy={busy}
                disabled={!note.trim()}
                onClick={() => void decision("acted")}
              >
                {t("product.applied")}
              </Button>
              <div className="field">
                <label htmlFor={formId + "-reason"}>
                  {t("product.reason")}
                </label>
                <select
                  id={formId + "-reason"}
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                >
                  <option value="">{t("product.chooseReason")}</option>
                  <option value="false_positive">
                    {t("product.falsePositive")}
                  </option>
                  <option value="not_relevant">
                    {t("product.notRelevant")}
                  </option>
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
            </>
          )}
          {decisionError && (
            <Notice tone="alert">{localizeError(decisionError)}</Notice>
          )}
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
