import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { Card, Chip, Metric } from "@/components/ui";

export function RunPanel() {
  const { status } = useWorkspace();
  const { t, language } = useI18n();
  if (!status) return null;
  const usd = (value: number) => new Intl.NumberFormat(language, { style: "currency", currency: "USD", maximumFractionDigits: 4 }).format(value);
  return <Card title={t("catalog.runTitle")} lead={t("catalog.runHint")}>
    <div className="stack">
      <div className="utility-bar"><Chip tone={status.engine === "ai" ? "good" : "muted"}>{status.engine === "ai" ? status.llm.model : t("product.ruleMode")}</Chip><span>{t("catalog.changed", { count: status.estimate.changed, total: status.estimate.products })}</span></div>
      <div className="evidence-metrics">
        <Metric label={t("catalog.estimate")} value={usd(status.estimate.analyse_all_usd)} />
        <Metric label={t("catalog.aiBudget")} value={`${usd(status.llm.spent_usd)} / ${usd(status.llm.budget_usd)}`} />
        <Metric label={t("catalog.fetchBudget")} value={`${usd(status.fetch.spent_usd)} / ${usd(status.fetch.budget_usd)}`} />
      </div>
      <label className="stack">{t("catalog.aiBudget")}<progress max={status.llm.budget_usd || 1} value={status.llm.spent_usd} aria-label={t("catalog.aiBudget")} /></label>
      <label className="stack">{t("catalog.fetchBudget")}<progress max={status.fetch.budget_usd || 1} value={status.fetch.spent_usd} aria-label={t("catalog.fetchBudget")} /></label>
      <p className="muted">{t("catalog.budgetHint")}</p>
      <details><summary>{t("catalog.stages")}</summary><ol>{["triage", "evidence", "listing", "fact", "draft", "gate", "decision"].map(stage => <li key={stage}>{t("catalog.stage" + stage)}</li>)}</ol></details>
    </div>
  </Card>;
}
