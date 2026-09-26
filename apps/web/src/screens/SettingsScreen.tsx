import { useEffect, useId, useState, type FormEvent } from "react";
import { useAuth } from "@/api/auth";
import { useWorkspace } from "@/api/workspace";
import { request, ApiError } from "@/api/http.js";
import { useI18n, type Language } from "@/lib/i18n";
import { useTheme } from "@/lib/theme";
import { TelegramSettings } from "@/components/TelegramSettings";
import { Meter } from "@/components/visual/charts";
import {
  Bot,
  Cpu,
  GitCommit,
  Globe,
  Monitor,
  Moon,
  RefreshCw,
  Server as ServerIcon,
  Sun,
  UserRound,
  Wallet,
} from "lucide-react";
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
        <Card title={t("settings.profile")} icon={<UserRound size={18} aria-hidden />}>
          <form className="stack" onSubmit={(event) => void save(event)}>
            <div className="profile-head">
              <span className="profile-head__avatar" aria-hidden>
                {(name || user?.email || "?")
                  .split(/\s+/)
                  .slice(0, 2)
                  .map((part) => part[0]?.toUpperCase())
                  .join("")}
              </span>
              <div>
                <strong>{name || user?.name}</strong>
                <p>
                  <span className="muted">{t("settings.email")}: </span>
                  {user?.email}
                </p>
              </div>
            </div>
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
        <Card title={t("settings.display")} icon={<Monitor size={18} aria-hidden />}>
          <div className="display-grid">
            <div className="field">
              <span className="field__label" id={id + "-lang"}>
                {t("settings.language")}
              </span>
              <div className="segmented" role="group" aria-labelledby={id + "-lang"}>
                {(
                  [
                    ["en", "English"],
                    ["id", "Bahasa Indonesia"],
                  ] as const
                ).map(([value, label]) => (
                  <button
                    key={value}
                    type="button"
                    aria-pressed={language === value}
                    onClick={() => setLanguage(value as Language)}
                  >
                    <Globe size={14} aria-hidden />
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div className="field">
              <span className="field__label" id={id + "-theme"}>
                {t("settings.theme")}
              </span>
              <div className="segmented" role="group" aria-labelledby={id + "-theme"}>
                {(["light", "dark"] as const).map((value) => (
                  <button
                    key={value}
                    type="button"
                    aria-pressed={theme === value}
                    onClick={() => {
                      if (theme !== value) toggleTheme();
                    }}
                  >
                    {value === "light" ? <Sun size={14} aria-hidden /> : <Moon size={14} aria-hidden />}
                    {t("settings." + value)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Card>
        <TelegramSettings />
        <Card
          title={t("settings.server")}
          icon={<ServerIcon size={18} aria-hidden />}
          action={
            <Button
              variant="outline"
              size="sm"
              disabled={loading}
              onClick={() => setRevision((value) => value + 1)}
            >
              <RefreshCw size={14} aria-hidden className={loading ? "spinner" : undefined} />
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
              <dl className="spec-grid">
                <div>
                  <dt>
                    <Cpu size={14} aria-hidden />
                    {t("settings.engine")}
                  </dt>
                  <dd>
                    <Chip tone={server.engine === "ai" ? "good" : "muted"}>
                      <i className="status-dot" aria-hidden />
                      {t("settings." + (server.engine === "ai" ? "ai" : "rules"))}
                    </Chip>
                  </dd>
                </div>
                <div>
                  <dt>
                    <Bot size={14} aria-hidden />
                    {t("settings.model")}
                  </dt>
                  <dd className="count">{server.llm?.model ?? "—"}</dd>
                </div>
                <div>
                  <dt>
                    <Globe size={14} aria-hidden />
                    {t("settings.fetch")}
                  </dt>
                  <dd>
                    <Chip tone={server.fetch?.configured ? "good" : "warn"}>
                      <i className="status-dot" aria-hidden />
                      {t(
                        "settings." +
                          (server.fetch?.configured
                            ? "configured"
                            : "unavailable"),
                      )}
                    </Chip>
                  </dd>
                </div>
                <div className="spec-grid__wide">
                  <dt>
                    <Wallet size={14} aria-hidden />
                    {t("settings.spent")} / {t("settings.limit")}
                  </dt>
                  <dd>
                    <span className="count spec-grid__money">
                      {number(server.llm?.spent_usd)} / {number(server.llm?.budget_usd)}
                    </span>
                    <Meter
                      value={server.llm?.spent_usd ?? 0}
                      max={server.llm?.budget_usd || 1}
                      label={t("settings.spent")}
                      warn
                    />
                  </dd>
                </div>
              </dl>
            )
          )}
        </Card>
        <Card title={t("settings.version")} icon={<GitCommit size={18} aria-hidden />}>
          {loading ? (
            <LoadingState />
          ) : version ? (
            <dl className="spec-grid">
              <div>
                <dt>{version.app}</dt>
                <dd className="count">{version.version}</dd>
              </div>
              {(["pipeline", "verifier", "commit"] as const).map((key) => (
                <div key={key}>
                  <dt>{t("settings." + key)}</dt>
                  <dd className="break-word count">{version[key] || "—"}</dd>
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
