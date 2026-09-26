import "@/styles/landing.css";
import { useEffect, useState, type FormEvent } from "react";
import { ArrowLeft, FlaskConical } from "lucide-react";
import { useAuth } from "@/api/auth";
import { Brand, LangToggle, ThemeToggle } from "@/components/Brand.jsx";
import { Button, Field, Notice } from "@/components/ui";
import { useI18n } from "@/lib/i18n";
import { navigate } from "@/lib/router.js";

type Mode = "login" | "register";

function modeFromHash(): Mode {
  return window.location.hash.startsWith("#/register") ? "register" : "login";
}

/** `#/login` dan `#/register`: form akun di kiri, akun demo di bawahnya, dan alur singkat di kanan.
 *  Pengguna yang sudah masuk dialihkan ke `#/app` oleh router aplikasi. */
export default function LoginScreen() {
  const { t, localizeError } = useI18n();
  const { login, register, demo } = useAuth();
  const [mode, setMode] = useState<Mode>(modeFromHash);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<{ code: string; from: "form" | "demo" } | null>(null);
  const [busy, setBusy] = useState<"form" | "demo" | null>(null);

  useEffect(() => {
    const update = () => setMode(modeFromHash());
    window.addEventListener("hashchange", update);
    return () => window.removeEventListener("hashchange", update);
  }, []);

  useEffect(() => {
    setFieldErrors({});
    setError(null);
  }, [mode]);

  function validate() {
    const next: Record<string, string> = {};
    if (mode === "register" && !name.trim()) next.name = t("landing.login.errorName");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) next.email = t("landing.login.errorEmail");
    if (password.length < 8) next.password = t("landing.login.errorPassword");
    setFieldErrors(next);
    return Object.keys(next).length === 0;
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!validate()) return;
    setBusy("form");
    try {
      if (mode === "register") await register(email.trim(), password, name.trim());
      else await login(email.trim(), password);
      navigate("/app");
    } catch (err) {
      setError({ code: (err as { code?: string }).code ?? "request_failed", from: "form" });
    } finally {
      setBusy(null);
    }
  }

  async function startDemo() {
    setError(null);
    setBusy("demo");
    try {
      await demo();
      navigate("/app");
    } catch (err) {
      setError({ code: (err as { code?: string }).code ?? "request_failed", from: "demo" });
    } finally {
      setBusy(null);
    }
  }

  const isRegister = mode === "register";
  return (
    <div className="lp login">
      <header className="login__top lp-wrap">
        <Brand />
        <div className="lp-nav__tools">
          <LangToggle />
          <ThemeToggle />
        </div>
      </header>
      <main className="lp-wrap login__grid">
        <div className="login__forms">
          <a className="login__back" href="#/">
            <ArrowLeft size={16} aria-hidden />
            {t("landing.login.back")}
          </a>
          <section className="login__card" aria-labelledby="login-title">
            <h1 id="login-title" className="login__title">
              {isRegister ? t("landing.login.titleRegister") : t("landing.login.titleSignIn")}
            </h1>
            <p className="login__subtitle">{t("landing.login.subtitle")}</p>
            <form className="login__form" onSubmit={submit} noValidate>
              {isRegister && (
                <Field
                  label={t("landing.login.name")}
                  autoComplete="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  error={fieldErrors.name}
                />
              )}
              <Field
                label={t("landing.login.email")}
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={fieldErrors.email}
              />
              <Field
                label={t("landing.login.password")}
                type="password"
                autoComplete={isRegister ? "new-password" : "current-password"}
                hint={t("landing.login.passwordHint")}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={fieldErrors.password}
              />
              {error?.from === "form" && <Notice tone="alert">{localizeError(error.code)}</Notice>}
              <Button type="submit" size="lg" busy={busy === "form"} disabled={busy === "demo"}>
                {isRegister ? t("landing.login.submitRegister") : t("landing.login.submitSignIn")}
              </Button>
            </form>
            <a className="login__switch" href={isRegister ? "#/login" : "#/register"}>
              {isRegister ? t("landing.login.toSignIn") : t("landing.login.toRegister")}
            </a>
          </section>
          <section className="login__demo" aria-labelledby="login-demo-title">
            <h2 id="login-demo-title" className="login__demo-title">
              <FlaskConical size={18} aria-hidden />
              {t("landing.login.demoTitle")}
            </h2>
            <p>{t("landing.login.demoText")}</p>
            <Button
              variant="outline"
              busy={busy === "demo"}
              disabled={busy === "form"}
              onClick={() => void startDemo()}
            >
              {t("landing.login.demoButton")}
            </Button>
            {error?.from === "demo" && <Notice tone="alert">{localizeError(error.code)}</Notice>}
          </section>
        </div>
        <aside className="login__panel" aria-labelledby="login-panel-title">
          <h2 id="login-panel-title" className="login__panel-title">
            {t("landing.login.panelTitle")}
          </h2>
          <ol className="login__steps">
            {[1, 2, 3].map((n) => (
              <li key={n}>
                <span className="login__num">{n}</span>
                <div>
                  <h3>{t(`landing.login.panel${n}Title`)}</h3>
                  <p>{t(`landing.login.panel${n}`)}</p>
                </div>
              </li>
            ))}
          </ol>
        </aside>
      </main>
    </div>
  );
}
