import type { CSSProperties } from "react";
import {
  Bell,
  Check,
  FileSearch,
  Flag,
  Info,
  Lock,
  PenLine,
  Plug,
  Quote,
  Ruler,
  ShieldCheck,
  Sparkles,
  UserRound,
  X,
} from "lucide-react";
import { Brand, BrandMark } from "@/components/Brand.jsx";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
import { Clouds } from "./Clouds";
import { DemoButton } from "./Hero";
import { useRevealOnce } from "./hooks";

type Start = { start: () => void; busy: boolean; error: string | null; signedIn: boolean };
const five = [1, 2, 3, 4, 5];

export function Compare() {
  const { t } = useI18n();
  return (
    <section className="lp-section lp-compare" aria-labelledby="lp-why-title">
      <div className="lp-wrap lp-compare__grid">
        <div className="lp-compare__copy">
          <h2 id="lp-why-title" className="lp-h2">
            {t("landing.why.title")}
          </h2>
          <p className="lp-lead">{t("landing.why.lead")}</p>
        </div>
        <div className="ledger">
          <div className="ledger__col ledger__col--today">
            <p className="ledger__label">{t("landing.why.todayLabel")}</p>
            <ul>
              {five.map((n) => (
                <li key={n}>
                  <X size={16} aria-hidden className="ledger__x" />
                  {t("landing.why.today" + n)}
                </li>
              ))}
            </ul>
          </div>
          <div className="ledger__col ledger__col--deciqo">
            <p className="ledger__label">{t("landing.why.deciqoLabel")}</p>
            <ul>
              {five.map((n) => (
                <li key={n}>
                  <Check size={16} aria-hidden className="ledger__check" />
                  {t("landing.why.with" + n)}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

const STEP_ICONS = [Quote, FileSearch, Ruler, PenLine, Flag];

export function Steps() {
  const { t } = useI18n();
  const { ref, shown } = useRevealOnce<HTMLOListElement>(0.4);
  return (
    <section id="how" className="lp-section lp-steps" aria-labelledby="lp-how-title">
      <div className="lp-wrap">
        <div className="lp-steps__head">
          <h2 id="lp-how-title" className="lp-h2">
            {t("landing.how.title")}
          </h2>
          <p className="lp-lead">{t("landing.how.lead")}</p>
        </div>
        <ol ref={ref} className={cn("steps", shown && "is-shown")}>
          {five.map((n, i) => {
            const Icon = STEP_ICONS[i];
            return (
              <li key={n} className="step" style={{ "--i": i } as CSSProperties}>
                <span className="step__dot">
                  <Icon size={20} aria-hidden />
                </span>
                <span className="step__num">{n}</span>
                <h3 className="step__title">{t(`landing.how.step${n}Title`)}</h3>
                <p className="step__text">{t(`landing.how.step${n}`)}</p>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}

export function Bento() {
  const { t } = useI18n();
  return (
    <section id="features" className="lp-section lp-bento" aria-labelledby="lp-features-title">
      <div className="lp-wrap">
        <div className="lp-bento__head">
          <h2 id="lp-features-title" className="lp-h2">
            {t("landing.features.title")}
          </h2>
          <p className="lp-lead">{t("landing.features.lead")}</p>
        </div>
        <div className="bento">
          <BentoCell
            span={2}
            className="bento__cell--lead"
            icon={Plug}
            title={t("landing.features.channelsTitle")}
            text={t("landing.features.channels")}
            pill={t("landing.features.channelsPill")}
            art={
              <div className="art-channels">
                <span className="art-channels__pill">
                  <i className="art-dot" />
                  {t("landing.features.channelsWoo")}
                </span>
                <div className="art-bars">
                  {[46, 70, 38, 88, 58, 74, 30, 64].map((h, i) => (
                    <span key={i} style={{ height: h + "%" }} />
                  ))}
                </div>
              </div>
            }
          />
          <BentoCell
            icon={ShieldCheck}
            title={t("landing.features.evidenceTitle")}
            text={t("landing.features.evidence")}
            pill={t("landing.features.evidencePill")}
            art={
              <div className="art-count">
                <span className="art-count__num">3 / 4</span>
                <span className="art-count__of">{t("landing.features.evidenceOf", { total: 4 })}</span>
              </div>
            }
          />
          <BentoCell
            icon={Ruler}
            title={t("landing.features.factTitle")}
            text={t("landing.features.fact")}
            pill={t("landing.features.factPill")}
            art={
              <div className="art-chips">
                {[1, 2, 3].map((n) => (
                  <span key={n} className="chip tone-warn">
                    <Lock size={12} aria-hidden />
                    {t("landing.features.factChip" + n)}
                  </span>
                ))}
              </div>
            }
          />
          <BentoCell
            span={2}
            icon={Sparkles}
            title={t("landing.features.planTitle")}
            text={t("landing.features.plan")}
            pill={t("landing.features.planPill")}
            art={
              <div className="art-plan">
                {[1, 2, 3].map((n) => (
                  <div key={n} className={cn("art-plan__col", n === 1 && "is-lit")}>
                    <span>{t("landing.features.planCol" + n)}</span>
                    <i style={{ width: [82, 56, 34][n - 1] + "%" }} />
                  </div>
                ))}
              </div>
            }
          />
          <BentoCell
            span={2}
            icon={Bell}
            title={t("landing.features.alertsTitle")}
            text={t("landing.features.alerts")}
            pill={t("landing.features.alertsPill")}
            art={
              <div className="art-toast">
                <BrandMark size={26} />
                <div>
                  <p className="art-toast__title">{t("landing.features.alertsToast")}</p>
                  <p className="art-toast__sub">{t("landing.features.alertsToastSub")}</p>
                </div>
              </div>
            }
          />
          <BentoCell
            icon={UserRound}
            title={t("landing.features.accountsTitle")}
            text={t("landing.features.accounts")}
            pill={t("landing.features.accountsPill")}
            art={
              <div className="art-avatars">
                {[0, 1, 2].map((i) => (
                  <span key={i} className={cn("art-avatar", i === 0 && "is-you")}>
                    <UserRound size={18} aria-hidden />
                  </span>
                ))}
              </div>
            }
          />
        </div>
      </div>
    </section>
  );
}

function BentoCell({
  span = 1,
  icon: Icon,
  title,
  text,
  pill,
  art,
  className,
}: {
  span?: 1 | 2;
  icon: typeof Plug;
  title: string;
  text: string;
  pill: string;
  art: React.ReactNode;
  className?: string;
}) {
  return (
    <article className={cn("bento__cell", span === 2 && "bento__cell--wide", className)}>
      <div className="bento__art" aria-hidden>
        {art}
      </div>
      <div className="bento__body">
        <h3 className="bento__title">
          <Icon size={18} aria-hidden className="bento__icon" />
          {title}
        </h3>
        <p className="bento__text">{text}</p>
        <span className="chip tone-info bento__pill">{pill}</span>
      </div>
    </article>
  );
}

export function Honest() {
  const { t } = useI18n();
  return (
    <section id="honest" className="lp-section lp-honest" aria-labelledby="lp-honest-title">
      <div className="lp-wrap">
        <h2 id="lp-honest-title" className="lp-h2">
          {t("landing.honest.title")}
        </h2>
        <div className="honest">
          <div className="honest__col">
            <h3 className="honest__label">{t("landing.honest.workingLabel")}</h3>
            <ul>
              {[1, 2, 3].map((n) => (
                <li key={n}>
                  <Check size={18} aria-hidden className="honest__ok" />
                  {t("landing.honest.working" + n)}
                </li>
              ))}
            </ul>
          </div>
          <div className="honest__col honest__col--not">
            <h3 className="honest__label">{t("landing.honest.notYetLabel")}</h3>
            <ul>
              {[1, 2, 3, 4].map((n) => (
                <li key={n}>
                  <Info size={18} aria-hidden className="honest__info" />
                  {t("landing.honest.notYet" + n)}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

export function Close({ demo }: { demo: Start }) {
  const { t } = useI18n();
  return (
    <section className="lp-close" aria-labelledby="lp-close-title">
      <div className="lp-close__clouds" aria-hidden>
        <Clouds />
      </div>
      <div className="lp-wrap lp-close__inner">
        <BrandMark size={56} />
        <h2 id="lp-close-title" className="lp-h2">
          {t("landing.close.title")}
        </h2>
        <p className="lp-lead">{t("landing.close.lead")}</p>
        <DemoButton demo={demo} label={t("landing.hero.demo")} />
        <p className="lp-note">{t("landing.close.note")}</p>
      </div>
    </section>
  );
}

export function Footer() {
  const { t } = useI18n();
  return (
    <footer className="lp-footer">
      <div className="lp-wrap lp-footer__inner">
        <Brand />
        <p>{t("landing.footer.line")}</p>
      </div>
    </footer>
  );
}
