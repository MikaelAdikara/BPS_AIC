import { useEffect, useState } from "react";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { issuesForTab, issueLink } from "@/lib/workspace-model.js";
import { Card, EmptyState } from "@/components/ui";
import { IssuesTable, StateGate } from "@/components/workspace";
const tabs = [
  { value: "needs", key: "tabNeeds" },
  { value: "monitoring", key: "tabMonitoring" },
  { value: "dismissed", key: "tabDismissed" },
  { value: "not_detected", key: "tabNotDetected" },
  { value: "all", key: "tabAll" },
];
const validTabs = [
  "needs",
  "monitoring",
  "dismissed",
  "not_detected",
  "all",
  "recurrence",
  "needs_fact",
  "to_do",
];
function storedTab() {
  try {
    return sessionStorage.getItem("deciqo-issues-tab") ?? "needs";
  } catch {
    return "needs";
  }
}
export function IssuesScreen({ query }: { query: URLSearchParams }) {
  const { inbox, loading, error } = useWorkspace();
  const { t } = useI18n();
  const [tab, setTab] = useState(() => query.get("tab") ?? storedTab());
  useEffect(() => {
    const requested = query.get("tab");
    if (requested && validTabs.includes(requested)) setTab(requested);
  }, [query]);
  useEffect(() => {
    if (!loading && !error && query.has("f")) {
      const item = inbox.find((issue) => issue.id === query.get("f"));
      if (item) window.location.hash = issueLink(item).slice(1);
    }
  }, [query, inbox, loading, error]);
  const effective = validTabs.includes(tab) ? tab : "needs";
  const items = issuesForTab(inbox, effective);
  function select(value: string) {
    setTab(value);
    try {
      sessionStorage.setItem("deciqo-issues-tab", value);
    } catch {}
    window.location.hash = "#/app/issues?tab=" + value;
  }
  return (
    <>
      <header className="page-header">
        <div>
          <h1>{t("common.issues")}</h1>
          <p className="muted">{t("workspace.issuesLead")}</p>
        </div>
      </header>
      <StateGate>
        <div
          className="issue-tabs"
          role="group"
          aria-label={t("workspace.filters")}
        >
          {tabs.map((item) => (
            <button
              key={item.value}
              className="btn btn--text"
              aria-pressed={
                item.value === effective ||
                (item.value === "needs" &&
                  ["recurrence", "needs_fact", "to_do"].includes(effective))
              }
              onClick={() => select(item.value)}
            >
              {t("workspace." + item.key)}
            </button>
          ))}
        </div>
        <Card>
          {items.length > 0 || inbox.length === 0 ? (
            <IssuesTable items={items} />
          ) : (
            <EmptyState
              title={t(
                effective === "needs"
                  ? "workspace.noNeeds"
                  : "workspace.noMatches",
              )}
              description={t(
                effective === "needs"
                  ? "workspace.noNeedsHint"
                  : "workspace.noMatchesHint",
              )}
              action={
                <button
                  className="btn btn--outline"
                  onClick={() => select("all")}
                >
                  {t("workspace.viewAll")}
                </button>
              }
            />
          )}
        </Card>
      </StateGate>
    </>
  );
}
