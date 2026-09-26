import { useEffect, useId, useState, type FormEvent } from "react";
import { useAuth } from "@/api/auth";
import { useWorkspace } from "@/api/workspace";
import { request, ApiError } from "@/api/http.js";
import { useI18n, type Language } from "@/lib/i18n";
import { useTheme } from "@/lib/theme";
import { TelegramSettings } from "@/components/TelegramSettings";
import {
  Button,
  Card,
  Chip,
  Field,
  LoadingState,
  Notice,
} from "@/components/ui";
interface Server {
  engine: string;
  llm: { model?: string; spent_usd?: number; budget_usd?: number };
  fetch: { configured: boolean };
}
interface Version {
  app: string;
  version: string;
  commit: string;
  pipeline: string;
  verifier: string;
}
export function SettingsScreen() {
  const { user, refresh: refreshAuth } = useAuth();
  const { run, busy } = useWorkspace();
  const { t, language, setLanguage, localizeError } = useI18n();
  const { theme, toggleTheme } = useTheme();
  const [name, setName] = useState(user?.name ?? "");
  const [phone, setPhone] = useState(user?.phone ?? "");
  const [profileError, setProfileError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [server, setServer] = useState<Server | null>(null);
  const [version, setVersion] = useState<Version | null>(null);
  const [revision, setRevision] = useState(0);
  const id = useId();
  useEffect(() => {
    setName(user?.name ?? "");
    setPhone(user?.phone ?? "");
  }, [user?.name, user?.phone]);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    Promise.allSettled([
      request("/deciqo/status", { signal: controller.signal }),
      request("/version", { signal: controller.signal }),
    ]).then(([statusResult, versionResult]) => {
      if (controller.signal.aborted) return;
      if (statusResult.status === "fulfilled") setServer(statusResult.value);
      else {
        setServer(null);
        setError((statusResult.reason as ApiError).code);
      }
      setVersion(
        versionResult.status === "fulfilled" ? versionResult.value : null,
      );
      setLoading(false);
    });
    return () => controller.abort();
  }, [revision]);
  async function save(event: FormEvent) {
    event.preventDefault();
    setProfileError(null);
    await run(async () => {
      try {
        await request("/auth/me", {
          method: "PATCH",
          body: { name, phone, lang: language },
        });
        await refreshAuth(true);
      } catch (e) {
        setProfileError((e as ApiError).code);
        throw e;
      }
    }, "settings.saved");
  }
  const number = (value?: number) =>
    value == null
      ? "—"
      : new Intl.NumberFormat(language, { maximumFractionDigits: 4 }).format(
          value,
        );
  return (
    <>
      <header className="page-header">
        <div>
          <h1>{t("settings.title")}</h1>
          <p className="muted">{t("settings.lead")}</p>
        </div>
      </header>
      <div className="stack">
        <Card title={t("settings.profile")}>
          <form className="stack" onSubmit={(event) => void save(event)}>
            <p>
              <span className="muted">{t("settings.email")}: </span>
              {user?.email}
            </p>
            <Field
              label={t("settings.name")}
              value={name}
              maxLength={120}
              onChange={(event) => setName(event.target.value)}
            />
            <Field
              label={t("settings.phone")}
              type="tel"
              value={phone}
              maxLength={32}
              hint={t("settings.phoneHint")}
              onChange={(event) => setPhone(event.target.value)}
            />
            {profileError && (
              <Notice tone="alert">{localizeError(profileError)}</Notice>
            )}
            <div>
              <Button type="submit" busy={busy}>
                {t("settings.save")}
              </Button>
            </div>
          </form>
        </Card>
        <Card title={t("settings.display")}>
          <div className="stack">
            <div className="field">
              <label htmlFor={id + "-lang"}>{t("settings.language")}</label>
              <select
                id={id + "-lang"}
                value={language}
                onChange={(event) =>
                  setLanguage(event.target.value as Language)
                }
              >
                <option value="en">English</option>
                <option value="id">Bahasa Indonesia</option>
              </select>
            </div>
            <div>
              <p className="muted">{t("settings.theme")}</p>
              <Button
                variant="outline"
                aria-pressed={theme === "dark"}
                onClick={toggleTheme}
              >
                {t("settings." + theme)}
              </Button>
            </div>
          </div>
        </Card>
        <TelegramSettings />
        <Card
          title={t("settings.server")}
          action={
            <Button
              variant="outline"
              disabled={loading}
              onClick={() => setRevision((value) => value + 1)}
            >
              {t("settings.refresh")}
            </Button>
          }
        >
          {loading ? (
            <LoadingState />
          ) : error ? (
            <Notice tone="alert">{localizeError(error)}</Notice>
          ) : (
            server && (
              <dl className="stack">
                <div>
                  <dt className="muted">{t("settings.engine")}</dt>
                  <dd>
                    {t("settings." + (server.engine === "ai" ? "ai" : "rules"))}
                  </dd>
                </div>
                <div>
                  <dt className="muted">{t("settings.model")}</dt>
                  <dd>{server.llm?.model ?? "—"}</dd>
                </div>
                <div>
                  <dt className="muted">{t("settings.fetch")}</dt>
                  <dd>
                    {t(
                      "settings." +
                        (server.fetch?.configured
                          ? "configured"
                          : "unavailable"),
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="muted">{t("settings.spent")}</dt>
                  <dd className="count">{number(server.llm?.spent_usd)}</dd>
                </div>
                <div>
                  <dt className="muted">{t("settings.limit")}</dt>
                  <dd className="count">{number(server.llm?.budget_usd)}</dd>
                </div>
              </dl>
            )
          )}
        </Card>
        <Card title={t("settings.version")}>
          {loading ? (
            <LoadingState />
          ) : version ? (
            <dl className="stack">
              <div>
                <dt>{version.app}</dt>
                <dd>{version.version}</dd>
              </div>
              {(["pipeline", "verifier", "commit"] as const).map((key) => (
                <div key={key}>
                  <dt className="muted">{t("settings." + key)}</dt>
                  <dd className="break-word">{version[key] || "—"}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <Notice tone="muted">{t("settings.missingVersion")}</Notice>
          )}
        </Card>
      </div>
    </>
  );
}
