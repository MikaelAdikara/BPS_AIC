import { ExternalLink, Store } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { Button, Card, Chip } from "./ui";
export interface LocalStoreStatus {
  reachable: boolean;
  connected: boolean;
  storefront_url: string;
  admin_url: string;
}
/** Toko WordPress + WooCommerce asli (profile Compose `store`) untuk demo webhook live. */
export function LocalWooStore({
  status,
  busy,
  onConnect,
}: {
  status: LocalStoreStatus | null;
  busy: boolean;
  onConnect: () => void;
}) {
  const { t } = useI18n();
  if (!status) return null;
  return (
    <Card title={t("sources.localTitle")} lead={t("sources.localLead")}>
      <div className="local-store">
        {status.reachable ? (
          <>
            <div className="local-store__status">
              <Store size={16} aria-hidden />
              <Chip tone={status.connected ? "good" : "info"}>
                {t(status.connected ? "sources.localConnected" : "sources.localNotConnected")}
              </Chip>
            </div>
            <div className="local-store__links">
              {!status.connected && (
                <Button busy={busy} onClick={onConnect}>
                  {t("sources.localConnect")}
                </Button>
              )}
              <a
                className="btn btn--outline btn--sm"
                href={status.storefront_url}
                target="_blank"
                rel="noreferrer"
              >
                {t("sources.localOpen")}
                <ExternalLink size={14} aria-hidden />
              </a>
              <a
                className="btn btn--text btn--sm"
                href={status.admin_url}
                target="_blank"
                rel="noreferrer"
              >
                {t("sources.localAdmin")}
                <ExternalLink size={14} aria-hidden />
              </a>
            </div>
          </>
        ) : (
          <p className="muted">{t("sources.localOff")}</p>
        )}
      </div>
    </Card>
  );
}
