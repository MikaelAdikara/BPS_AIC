import { useI18n } from "@/lib/i18n";
import { useWorkspace, type Issue } from "@/api/workspace";
import { issueLink } from "@/lib/workspace-model.js";
import {
  Button,
  Chip,
  EmptyState,
  LoadingState,
  Notice,
  Table,
  type Tone,
} from "./ui";
export const buckets: Record<string, { key: string; tone: Tone }> = {
  recurrence: { key: "bucketRecurrence", tone: "alert" },
  needs_fact: { key: "bucketNeedsFact", tone: "warn" },
  to_do: { key: "bucketTodo", tone: "info" },
  monitoring: { key: "bucketMonitoring", tone: "good" },
  dismissed: { key: "bucketDismissed", tone: "muted" },
  not_detected: { key: "bucketNotDetected", tone: "muted" },
};
const nextKeys: Record<string, string> = {
  recurrence: "nextRecurrence",
  fact: "nextFact",
  apply: "nextApply",
  draft: "nextDraft",
  route: "nextRoute",
  monitoring: "nextMonitoring",
  paste_listing: "nextPasteListing",
};
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
export function StateGate({ children }: { children: React.ReactNode }) {
  const { loading, error, refresh } = useWorkspace();
  const { t, localizeError } = useI18n();
  if (loading) return <LoadingState />;
  if (error)
    return (
      <Notice
        tone="alert"
        action={
          <Button variant="outline" onClick={() => void refresh()}>
            {t("common.retry")}
          </Button>
        }
      >
        <p>{t("workspace.loadError")}</p>
        <p>
          {error === "read_model_unavailable"
            ? t("workspace.apiUnavailable")
            : error === "contact_lost"
              ? t("workspace.jobLost")
              : error === "job_interrupted"
                ? t("workspace.jobInterrupted")
                : localizeError(error)}
        </p>
      </Notice>
    );
  return <>{children}</>;
}
export function IssuesTable({ items }: { items: Issue[] }) {
  const { t, language } = useI18n();
  if (items.length === 0)
    return (
      <EmptyState
        title={t("workspace.noIssues")}
        description={t("workspace.noIssuesHint")}
        action={
          <a className="btn btn--primary" href="#/app/sources">
            {t("workspace.addChannel")}
          </a>
        }
      />
    );
  return (
    <Table>
      <thead>
        <tr>
          <th scope="col">{t("workspace.issue")}</th>
          <th scope="col">{t("workspace.type")}</th>
          <th scope="col">{t("workspace.reviews")}</th>
          <th scope="col">{t("workspace.status")}</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => {
          const bucket = buckets[item.bucket] ?? {
            key: "bucketNotDetected",
            tone: "muted" as Tone,
          };
          return (
            <tr key={item.id} className="issue-row">
              <td>
                <a className="issue-link" href={issueLink(item)}>
                  <strong>{item.product_title}</strong>
                </a>
                <p>
                  {language === "id" ? item.attribute_local : item.attribute}
                </p>
                {item.example && <q className="muted">{item.example}</q>}
                <div className="issue-meta">
                  <span>{item.channel}</span>
                  {item.synthetic && <Chip synthetic />}
                  {item.engine === "rules" && (
                    <Chip>{t("workspace.rules")}</Chip>
                  )}
                </div>
              </td>
              <td>
                <Chip>
                  {t(
                    "workspace." +
                      (item.needs_listing
                        ? "typeBuyerNeed"
                        : (typeKeys[item.finding_type] ?? "typeBuyerNeed")),
                  )}
                </Chip>
              </td>
              <td className="count">
                {item.support_is_minimum ? "≥ " : ""}
                {item.support} / {item.denominator}
              </td>
              <td>
                <Chip tone={bucket.tone}>{t("workspace." + bucket.key)}</Chip>
                {item.next && nextKeys[item.next] && (
                  <p>{t("workspace." + nextKeys[item.next])}</p>
                )}
              </td>
            </tr>
          );
        })}
      </tbody>
    </Table>
  );
}
