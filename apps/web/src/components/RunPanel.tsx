import { Bot, CircleDollarSign, Globe, Workflow } from "lucide-react";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { Card, Chip } from "@/components/ui";
import { Meter } from "@/components/visual/charts";

export function RunPanel() {
  const { status } = useWorkspace();
  const { t, language } = useI18n();
  if (!status) return null;
  const usd = (value: number) => new Intl.NumberFormat(language, { style: "currency", currency: "USD", maximumFractionDigits: 4 }).format(value);
  const pct = (spent: number, budget: number) => (budget > 0 ? Math.round((spent / budget) * 100) : 0) + "%";
  return <Card title={t("catalog.runTitle")} lead={t("catalog.runHint")} icon={<Workflow size={18} aria-hidden />}
    action={<Chip tone={status.engine === "ai" ? "good" : "muted"}>{status.engine === "ai" && <span className="pulse-dot" aria-hidden />}{status.engine === "ai" ? status.llm.model : t("product.ruleMode")}</Chip>}>
    <div className="stack">
      <div className="run-changed"><Meter value={status.estimate.changed} max={Math.max(1, status.estimate.products)} label={t("catalog.changed", { count: status.estimate.changed, total: status.estimate.products })} tone="info" /><span>{t("catalog.changed", { count: status.estimate.changed, total: status.estimate.products })}</span></div>
      <div className="budget-grid">
        <div className="budget-tile">
          <span className="budget-tile__label"><CircleDollarSign size={16} aria-hidden />{t("catalog.estimate")}</span>
          <strong className="budget-tile__value">{usd(status.estimate.analyse_all_usd)}</strong>
        </div>
        <div className="budget-tile">
          <span className="budget-tile__label"><Bot size={16} aria-hidden />{t("catalog.aiBudget")}</span>
          <strong className="budget-tile__value">{usd(status.llm.spent_usd)} <small>/ {usd(status.llm.budget_usd)}</small></strong>
          <Meter value={status.llm.spent_usd} max={status.llm.budget_usd || 1} label={t("catalog.aiBudget")} warn />
          <span className="budget-tile__pct count">{pct(status.llm.spent_usd, status.llm.budget_usd)}</span>
        </div>
        <div className="budget-tile">
          <span className="budget-tile__label"><Globe size={16} aria-hidden />{t("catalog.fetchBudget")}</span>
          <strong className="budget-tile__value">{usd(status.fetch.spent_usd)} <small>/ {usd(status.fetch.budget_usd)}</small></strong>
          <Meter value={status.fetch.spent_usd} max={status.fetch.budget_usd || 1} label={t("catalog.fetchBudget")} warn />
          <span className="budget-tile__pct count">{pct(status.fetch.spent_usd, status.fetch.budget_usd)}</span>
        </div>
      </div>
      <p className="muted">{t("catalog.budgetHint")}</p>
      <details><summary>{t("catalog.stages")}</summary><ol className="stage-chain">{["triage", "evidence", "listing", "fact", "draft", "gate", "decision"].map(stage => <li key={stage}>{t("catalog.stage" + stage)}</li>)}</ol></details>
    </div>
  </Card>;
}
