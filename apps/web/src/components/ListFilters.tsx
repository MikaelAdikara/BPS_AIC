import { useEffect, useId, useState } from "react";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { Button, Field } from "./ui";
export interface Filters {
  q: string;
  channel: string;
  kind: string;
  severity: string;
  status: string;
  order: string;
}
const empty: Filters = {
  q: "",
  channel: "",
  kind: "",
  severity: "",
  status: "",
  order: "priority",
};
export function useListFilters(key: string) {
  const [filters, setFilters] = useState<Filters>(() => {
    try {
      const saved = JSON.parse(sessionStorage.getItem(key) ?? "null");
      return { ...empty, ...saved };
    } catch {
      return { ...empty };
    }
  });
  useEffect(() => {
    try {
      sessionStorage.setItem(key, JSON.stringify(filters));
    } catch {}
  }, [filters, key]);
  return { filters, setFilters, clear: () => setFilters({ ...empty }) };
}
export function filterQuery(filters: Filters) {
  return new URLSearchParams(
    Object.entries(filters).filter(([, value]) => Boolean(value)),
  ).toString();
}
const types: Record<string, string> = {
  missing_fact: "typeMissingFact",
  unclear_fact: "typeUnclearWording",
  conflicting_fact: "typeListingConflict",
  expectation_mismatch: "typeExpectationGap",
  product_quality: "typeQuality",
  operational: "typeOperations",
};
export function ListFilters({
  filters,
  onChange,
  onClear,
  products = false,
}: {
  filters: Filters;
  onChange: (value: Filters) => void;
  onClear: () => void;
  products?: boolean;
}) {
  const { channels } = useWorkspace();
  const { t } = useI18n();
  const id = useId();
  const select = (
    key: keyof Filters,
    values: { value: string; label: string }[],
  ) => (
    <div className="field">
      <label htmlFor={id + key}>
          {t("filters." + ({ kind: "type", severity: "impact", q: "search", channel: "channel", order: "order", status: "status" }[key]))}
      </label>
      <select
        id={id + key}
        value={filters[key]}
        onChange={(event) =>
          onChange({ ...filters, [key]: event.target.value })
        }
      >
        {key !== "order" && <option value="">{t("filters.all")}</option>}
        {values.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
  return (
    <div className="list-filters">
      <Field
        label={t("filters.search")}
        type="search"
        value={filters.q}
        maxLength={300}
        onChange={(event) => onChange({ ...filters, q: event.target.value })}
      />
      {select(
        "channel",
        channels.map((channel) => ({
          value: channel.key,
          label: channel.label,
        })),
      )}
      {products ? (
        select(
          "status",
          ["ready", "pending", "failed", "stale"].map((value) => ({
            value,
            label: t("catalog." + value),
          })),
        )
      ) : (
        <>
          {select(
            "kind",
            Object.entries(types).map(([value, key]) => ({
              value,
              label: t("workspace." + key),
            })),
          )}
          {select(
            "severity",
            ["high", "medium", "low"].map((value) => ({
              value,
              label: t("filters." + value),
            })),
          )}
        </>
      )}
      {select(
        "order",
        (products
          ? ["priority", "reviews", "recent", "product"]
          : ["priority", "reviews", "share", "recent", "product"]
        ).map((value) => ({ value, label: t("filters." + value) })),
      )}
      <Button variant="text" onClick={onClear}>
        {t("filters.clear")}
      </Button>
    </div>
  );
}
