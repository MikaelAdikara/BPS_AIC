import { useEffect, useState } from "react";
import { useWorkspace, type Issue } from "@/api/workspace";
import { request, ApiError } from "@/api/http.js";
import {
  ListFilters,
  useListFilters,
  filterQuery,
} from "@/components/ListFilters";
import { useI18n } from "@/lib/i18n";
import { issuesForTab, issueLink } from "@/lib/workspace-model.js";
import {
  Button,
  Card,
  EmptyState,
  LoadingState,
  Notice,
} from "@/components/ui";
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
  const { filters, setFilters, clear } = useListFilters(
    "deciqo-issues-filters",
  );
  const params = filterQuery(filters);
  const [filtered, setFiltered] = useState<Issue[]>([]);
  const [filterLoading, setFilterLoading] = useState(true);
  const [filterError, setFilterError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const { inbox, loading, error } = useWorkspace();
  const { t, localizeError } = useI18n();
  useEffect(() => {
    const controller = new AbortController();
    setFilterLoading(true);
    setFilterError(null);
    const timer = setTimeout(() => {
      request("/deciqo/inbox?" + params, { signal: controller.signal })
        .then((data) => {
          if (!controller.signal.aborted) setFiltered(data.items);
        })
        .catch((e: ApiError) => {
          if (!controller.signal.aborted) setFilterError(e.code);
        })
        .finally(() => {
          if (!controller.signal.aborted) setFilterLoading(false);
        });
    }, 200);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [params, inbox, revision]);
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
  const items = issuesForTab(filtered, effective);
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
          className="segmented issue-tabs"
          role="group"
          aria-label={t("workspace.filters")}
        >
          {tabs.map((item) => (
            <button
              key={item.value}
              type="button"
              aria-pressed={
                item.value === effective ||
                (item.value === "needs" &&
                  ["recurrence", "needs_fact", "to_do"].includes(effective))
              }
              onClick={() => select(item.value)}
            >
              {t("workspace." + item.key)}
              {!filterLoading && (
                <span className="tab-count">
                  {issuesForTab(filtered, item.value).length}
                </span>
              )}
            </button>
          ))}
        </div>
        <div className="toolbar-card">
          <ListFilters filters={filters} onChange={setFilters} onClear={clear} />
        </div>
        <Card className={filterLoading && filtered.length ? "is-refreshing" : undefined}>
          {filterLoading && !filtered.length ? (
            <LoadingState />
          ) : filterError ? (
            <Notice
              tone="alert"
              action={
                <Button onClick={() => setRevision((value) => value + 1)}>
                  {t("common.retry")}
                </Button>
              }
            >
              {localizeError(filterError)}
            </Notice>
          ) : items.length > 0 || inbox.length === 0 ? (
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
                    onClick={() => { clear(); select("all"); }}
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
