import { useEffect, useState } from "react";
import { useAuth } from "@/api/auth";
import { useWorkspace } from "@/api/workspace";
import { request, ApiError } from "@/api/http.js";
import { useI18n } from "@/lib/i18n";
import { Button, Card, Chip, Notice } from "./ui";
interface Link {
  code: string;
  deep_link: string | null;
  bot_configured: boolean;
  expires_at: string;
}
export function TelegramSettings() {
  const { user, refresh } = useAuth();
  const { run, busy } = useWorkspace();
  const { t, language, localizeError } = useI18n();
  const [link, setLink] = useState<Link | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [expired, setExpired] = useState(false);
  useEffect(() => {
    if (!link) return;
    const expiry = Date.parse(link.expires_at);
    const check = () => {
      if (Date.now() >= expiry) {
        setExpired(true);
        return;
      }
      void refresh(true);
    };
    const interval = setInterval(check, 10000);
    window.addEventListener("focus", check);
    return () => {
      clearInterval(interval);
      window.removeEventListener("focus", check);
    };
  }, [link, refresh]);
  useEffect(() => {
    if (user?.telegram_linked) setLink(null);
  }, [user?.telegram_linked]);
  async function action(path: string, method: string) {
    setError(null);
    setResult(null);
    await run(
      async () => {
        try {
          const data = await request(path, { method });
          if (path.endsWith("/test"))
            setResult(
              data.status === "sent"
                ? "sent"
                : data.status === "failed"
                  ? "failed"
                  : "waiting",
            );
          else if (method === "POST") {
            setLink(data);
            setExpired(false);
          } else setLink(null);
          await refresh(true);
        } catch (e) {
          setError((e as ApiError).code);
          throw e;
        }
      },
      path.endsWith("/test") ? "settings.telegram" : "telegram.saved",
    );
  }
  const safeLink =
    link?.deep_link &&
    /^https:\/\/t\.me\/[A-Za-z0-9_]+\?start=[A-Z2-9]{6}$/.test(link.deep_link)
      ? link.deep_link
      : null;
  return (
    <Card title={t("settings.telegram")}>
      <div className="stack">
        <div>
          <Chip tone={user?.telegram_linked ? "good" : "muted"}>
            {t("settings." + (user?.telegram_linked ? "linked" : "notLinked"))}
          </Chip>
        </div>
        <p className="muted">{t("settings.telegramHint")}</p>
        {error && <Notice tone="alert">{localizeError(error)}</Notice>}
        {result && (
          <Notice
            tone={
              result === "sent"
                ? "good"
                : result === "failed"
                  ? "alert"
                  : "warn"
            }
          >
            {t("telegram." + result)}
          </Notice>
        )}
        {user?.telegram_linked ? (
          <div className="finding-picker">
            <Button
              variant="outline"
              busy={busy}
              onClick={() => void action("/deciqo/telegram/link", "DELETE")}
            >
              {t("telegram.unlink")}
            </Button>
            <Button
              busy={busy}
              onClick={() => void action("/deciqo/telegram/test", "POST")}
            >
              {t("telegram.test")}
            </Button>
          </div>
        ) : (
          <Button
            busy={busy}
            onClick={() => void action("/deciqo/telegram/link", "POST")}
          >
            {t("telegram.create")}
          </Button>
        )}
        {link && (
          <Notice tone={link.bot_configured && !expired ? "info" : "warn"}>
            <div className="stack">
              {!link.bot_configured ? (
                <p>{t("telegram.unconfigured")}</p>
              ) : expired ? (
                <p>{t("telegram.expired")}</p>
              ) : (
                <>
                  <p>{t("telegram.hint")}</p>
                  <p>
                    {t("telegram.code")}:{" "}
                    <strong className="count">{link.code}</strong>
                  </p>
                  <p>
                    {t("telegram.expires", {
                      time: new Date(link.expires_at).toLocaleString(language),
                    })}
                  </p>
                  <div className="finding-picker">
                    {safeLink && (
                      <a
                        className="btn btn--primary"
                        href={safeLink}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {t("telegram.open")}
                      </a>
                    )}
                    <Button
                      variant="outline"
                      onClick={async () => {
                        try {
                          await navigator.clipboard.writeText(link.code);
                          setResult("copied");
                        } catch {
                          setResult("copyFailed");
                        }
                      }}
                    >
                      {t("telegram.copy")}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => void refresh(true)}
                    >
                      {t("telegram.refresh")}
                    </Button>
                  </div>
                </>
              )}
            </div>
          </Notice>
        )}
      </div>
    </Card>
  );
}
