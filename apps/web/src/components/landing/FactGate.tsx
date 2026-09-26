import { useRef, useState, type FormEvent } from "react";
import { AlertCircle, Lock, LockOpen, RotateCcw, Ruler, ShieldHalf } from "lucide-react";
import { BrandMark } from "@/components/Brand.jsx";
import { Button } from "@/components/ui";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
import { BorderBeam } from "@/components/visual/BorderBeam";
import { Reveal } from "@/components/visual/motion";
import { Eyebrow } from "./Sections";

/** Demo konsep di sisi klien: draf tertahan sampai pengunjung (sebagai merchant) mengisi ukuran
 *  yang memuat angka. Tidak memanggil API dan tidak menyimpan apa pun. */
export function FactGate() {
  const { t } = useI18n();
  const [value, setValue] = useState("");
  const [released, setReleased] = useState<string | null>(null);
  const [error, setError] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  function submit(e: FormEvent) {
    e.preventDefault();
    const trimmed = value.trim();
    if (!/\d/.test(trimmed)) {
      setError(true);
      input.current?.focus();
      return;
    }
    setError(false);
    setReleased(trimmed);
  }

  function reset() {
    setReleased(null);
    setValue("");
    setError(false);
    requestAnimationFrame(() => input.current?.focus());
  }

  return (
    <section id="gate" className="lp-section lp-gate" aria-labelledby="lp-gate-title">
      <div className="lp-wrap">
        <Reveal className="lp-gate__head">
          <Eyebrow icon={ShieldHalf}>{t("landing.eyebrow.gate")}</Eyebrow>
          <h2 id="lp-gate-title" className="lp-h2">
            <span>{t("landing.gate.titleA")}</span>{" "}
            <span className="lp-accent">{t("landing.gate.titleB")}</span>
          </h2>
          <p className="lp-lead">{t("landing.gate.lead")}</p>
        </Reveal>
        <div className="lp-gate__grid">
          <article className="gate-generic" aria-label={t("landing.gate.genericLabel")}>
            <p className="gate-generic__label">{t("landing.gate.genericLabel")}</p>
            <p className="gate-generic__text">
              {t("landing.gate.genericBefore")}
              <mark className="gate-invented">{t("landing.gate.genericNum1")}</mark>
              {t("landing.gate.genericMid")}
              <mark className="gate-invented">{t("landing.gate.genericNum2")}</mark>
              {t("landing.gate.genericAfter")}
            </p>
            <p className="gate-generic__note">
              <AlertCircle size={16} aria-hidden />
              {t("landing.gate.genericNote")}
            </p>
          </article>

          <article className={cn("gate-deciqo", released && "is-released")} aria-label="Deciqo">
            {!released && <BorderBeam size={180} duration={8} from="var(--amber-base)" to="var(--blue)" />}
            <header className="gate-deciqo__head">
              <span className="gate-deciqo__brand">
                <BrandMark size={22} />
                Deciqo
              </span>
              <span
                className={cn("chip", released ? "tone-good" : "tone-warn", "gate-pill")}
                aria-live="polite"
              >
                {released ? <LockOpen size={14} aria-hidden /> : <Lock size={14} aria-hidden />}
                {released ? t("landing.gate.released") : t("landing.gate.held")}
              </span>
            </header>

            <div className="gate-draft">
              <div className="gate-draft__held" aria-hidden={Boolean(released)}>
                <p className="gate-draft__text">{t("landing.gate.heldText")}</p>
                <p className="gate-draft__sub">{t("landing.gate.heldSub")}</p>
              </div>
              {released && (
                <div className="gate-draft__released">
                  <p className="gate-draft__text">{t("landing.gate.draft", { value: released })}</p>
                  <p className="gate-draft__source">{t("landing.gate.source")}</p>
                </div>
              )}
            </div>

            {released ? (
              <Button variant="outline" onClick={reset} className="gate-reset">
                <RotateCcw size={16} aria-hidden />
                {t("landing.gate.reset")}
              </Button>
            ) : (
              <form className="gate-form" onSubmit={submit} noValidate>
                <label htmlFor="gate-input" className="gate-form__label">
                  <Ruler size={16} aria-hidden />
                  {t("landing.gate.label")}
                </label>
                <div className="gate-form__row">
                  <input
                    id="gate-input"
                    ref={input}
                    value={value}
                    maxLength={40}
                    autoComplete="off"
                    placeholder={t("landing.gate.placeholder")}
                    aria-invalid={error}
                    aria-describedby={error ? "gate-error" : undefined}
                    onChange={(e) => {
                      setValue(e.target.value);
                      if (error) setError(false);
                    }}
                  />
                  <Button type="submit">{t("landing.gate.button")}</Button>
                </div>
                {error && (
                  <p id="gate-error" className="field__error" role="alert">
                    {t("landing.gate.error")}
                  </p>
                )}
              </form>
            )}
            <p className="gate-deciqo__example">{t("landing.gate.example")}</p>
          </article>
        </div>
      </div>
    </section>
  );
}
