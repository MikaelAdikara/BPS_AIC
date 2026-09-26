import { useId, useState, type CSSProperties, type ReactNode } from "react";
import {
  Bell,
  Check,
  CircleHelp,
  Compass,
  FileSearch,
  Flag,
  FlaskConical,
  Info,
  Layers,
  Lock,
  PenLine,
  Plug,
  Plus,
  Quote,
  Ruler,
  ShieldCheck,
  Sparkles,
  Split,
  UserRound,
  X,
} from "lucide-react";
import { Brand, BrandMark } from "@/components/Brand.jsx";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
import { Marquee } from "@/components/visual/Marquee";
import { CountUp, Reveal, useInView } from "@/components/visual/motion";
import { Clouds } from "./Clouds";
import { DemoButton } from "./Hero";
import { useRevealOnce } from "./hooks";

type Start = { start: () => void; busy: boolean; error: string | null; signedIn: boolean };
const five = [1, 2, 3, 4, 5];

/** Label kecil berikon di atas judul bagian (gaya Billow). */
export function Eyebrow({ icon: Icon, children }: { icon: typeof Plug; children: ReactNode }) {
  return (
    <p className="lp-eyebrow">
      <span className="lp-eyebrow__icon" aria-hidden>
        <Icon size={13} />
      </span>
      {children}
    </p>
  );
}

const CHANNELS: { name: string; logo?: string }[] = [
  { name: "WooCommerce" },
  { name: "Lazada", logo: "/brand/logos/lazada.svg" },
  { name: "Tokopedia", logo: "/brand/logos/tokopedia.svg" },
  { name: "Shopee", logo: "/brand/logos/shopee.svg" },
  { name: "TikTok Shop" },
  { name: "Blibli" },
  { name: "CSV" },
];

/** Pita kanal sumber ulasan. Logo dipakai secara nominatif (lihat public/brand/logos/README.md). */
export function Channels() {
  const { t } = useI18n();
  return (
    <section className="lp-channels" aria-labelledby="lp-channels-title">
      <div className="lp-wrap lp-channels__inner">
        <p id="lp-channels-title" className="lp-channels__label">
          {t("landing.channels.label")}
        </p>
        <Marquee fade pauseOnHover duration={32} gap={56} repeat={3} className="lp-channels__marquee">
          {CHANNELS.map((channel) => (
            <span key={channel.name} className="lp-logo">
              {channel.logo ? (
                <img src={channel.logo} alt={channel.name} height={22} loading="lazy" decoding="async" />
              ) : (
                <span className="lp-logo__word">{channel.name}</span>
              )}
            </span>
          ))}
        </Marquee>
        <p className="lp-note">{t("landing.channels.note")}</p>
      </div>
    </section>
  );
}

const REVIEWS = [
  { n: 1, stars: 2 },
  { n: 2, stars: 3 },
  { n: 3, stars: 2 },
  { n: 4, stars: 3 },
  { n: 5, stars: 1 },
  { n: 6, stars: 4 },
  { n: 7, stars: 3 },
  { n: 8, stars: 2 },
];

function ReviewCard({ n, stars }: { n: number; stars: number }) {
  const { t } = useI18n();
  return (
    <figure className="vcard">
      <div className="vcard__top">
        <span className="vcard__stars" aria-label={stars + "★"}>
          {"★★★★★".slice(0, stars)}
          <i>{"★★★★★".slice(stars)}</i>
        </span>
        <span className="vcard__tag">{t("landing.reviews.t" + n)}</span>
      </div>
      <blockquote>“{t("landing.reviews.q" + n)}”</blockquote>
    </figure>
  );
}

/** Dinding ulasan sintetis yang miring (adaptasi marquee 3D): banyaknya keluhan yang harus dibaca. */
function ReviewWall() {
  const { t } = useI18n();
  const columns = [REVIEWS, [...REVIEWS].reverse(), [...REVIEWS.slice(4), ...REVIEWS.slice(0, 4)]];
  return (
    <div className="review-wall" aria-hidden>
      <div className="review-wall__plane">
        {columns.map((column, index) => (
          <Marquee key={index} vertical pauseOnHover reverse={index % 2 === 1} duration={34 + index * 6} gap={14} repeat={2}>
            {column.map((review) => (
              <ReviewCard key={review.n} {...review} />
            ))}
          </Marquee>
        ))}
      </div>
      <span className="review-wall__label">
        <FlaskConical size={12} />
        {t("landing.reviews.label")}
      </span>
    </div>
  );
}

export function Compare() {
  const { t } = useI18n();
  return (
    <section className="lp-section lp-compare" aria-labelledby="lp-why-title">
      <div className="lp-wrap lp-compare__grid">
        <Reveal className="lp-compare__copy">
          <Eyebrow icon={Split}>{t("landing.eyebrow.why")}</Eyebrow>
          <h2 id="lp-why-title" className="lp-h2">
            {t("landing.why.title")}
          </h2>
          <p className="lp-lead">{t("landing.why.lead")}</p>
          <ReviewWall />
        </Reveal>
        <Reveal className="ledger" delay={120}>
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
                <li key={n} style={{ "--i": n } as CSSProperties}>
                  <Check size={16} aria-hidden className="ledger__check" />
                  {t("landing.why.with" + n)}
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
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
        <Reveal className="lp-steps__head">
          <Eyebrow icon={Compass}>{t("landing.eyebrow.how")}</Eyebrow>
          <h2 id="lp-how-title" className="lp-h2">
            {t("landing.how.title")}
          </h2>
          <p className="lp-lead">{t("landing.how.lead")}</p>
        </Reveal>
        <ol ref={ref} className={cn("steps", shown && "is-shown")}>
          {five.map((n, i) => {
            const Icon = STEP_ICONS[i];
            return (
              <li key={n} className="step" style={{ "--i": i } as CSSProperties}>
                <span className="step__dot">
                  <Icon size={20} aria-hidden />
                </span>
                <span className="step__num">0{n}</span>
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

function EvidenceArt() {
  const { t } = useI18n();
  return (
    <div className="art-count">
      <span className="art-count__num">
        <CountUp value={3} duration={1200} /> / 4
      </span>
      <span className="art-count__of">{t("landing.features.evidenceOf", { total: 4 })}</span>
    </div>
  );
}

export function Bento() {
  const { t } = useI18n();
  const { ref, inView } = useInView<HTMLDivElement>(0.2);
  return (
    <section id="features" className="lp-section lp-bento" aria-labelledby="lp-features-title">
      <div className="lp-wrap">
        <Reveal className="lp-bento__head">
          <Eyebrow icon={Layers}>{t("landing.eyebrow.features")}</Eyebrow>
          <h2 id="lp-features-title" className="lp-h2">
            {t("landing.features.title")}
          </h2>
          <p className="lp-lead">{t("landing.features.lead")}</p>
        </Reveal>
        <div ref={ref} className={cn("bento", inView && "is-shown")}>
          <BentoCell
            index={0}
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
                    <span key={i} style={{ height: h + "%", "--i": i } as CSSProperties} />
                  ))}
                </div>
              </div>
            }
          />
          <BentoCell
            index={1}
            icon={ShieldCheck}
            title={t("landing.features.evidenceTitle")}
            text={t("landing.features.evidence")}
            pill={t("landing.features.evidencePill")}
            art={<EvidenceArt />}
          />
          <BentoCell
            index={2}
            icon={Ruler}
            title={t("landing.features.factTitle")}
            text={t("landing.features.fact")}
            pill={t("landing.features.factPill")}
            art={
              <div className="art-chips">
                {[1, 2, 3].map((n) => (
                  <span key={n} className="chip tone-warn" style={{ "--i": n } as CSSProperties}>
                    <Lock size={12} aria-hidden />
                    {t("landing.features.factChip" + n)}
                  </span>
                ))}
              </div>
            }
          />
          <BentoCell
            index={3}
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
                    <i style={{ width: [82, 56, 34][n - 1] + "%", "--i": n } as CSSProperties} />
                  </div>
                ))}
              </div>
            }
          />
          <BentoCell
            index={4}
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
            index={5}
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
  index,
  span = 1,
  icon: Icon,
  title,
  text,
  pill,
  art,
  className,
}: {
  index: number;
  span?: 1 | 2;
  icon: typeof Plug;
  title: string;
  text: string;
  pill: string;
  art: React.ReactNode;
  className?: string;
}) {
  return (
    <article
      className={cn("bento__cell", span === 2 && "bento__cell--wide", className)}
      style={{ "--cell": index } as CSSProperties}
    >
      <div className="bento__art" aria-hidden>
        {art}
      </div>
      <div className="bento__body">
        <span className="bento__icon" aria-hidden>
          <Icon size={18} />
        </span>
        <h3 className="bento__title">{title}</h3>
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
        <Reveal>
          <Eyebrow icon={ShieldCheck}>{t("landing.eyebrow.honest")}</Eyebrow>
          <h2 id="lp-honest-title" className="lp-h2">
            {t("landing.honest.title")}
          </h2>
        </Reveal>
        <div className="honest">
          <Reveal className="honest__col">
            <h3 className="honest__label">{t("landing.honest.workingLabel")}</h3>
            <ul>
              {[1, 2, 3].map((n) => (
                <li key={n}>
                  <Check size={18} aria-hidden className="honest__ok" />
                  {t("landing.honest.working" + n)}
                </li>
              ))}
            </ul>
          </Reveal>
          <Reveal className="honest__col honest__col--not" delay={120}>
            <h3 className="honest__label">{t("landing.honest.notYetLabel")}</h3>
            <ul>
              {[1, 2, 3, 4].map((n) => (
                <li key={n}>
                  <Info size={18} aria-hidden className="honest__info" />
                  {t("landing.honest.notYet" + n)}
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

export function Faq() {
  const { t } = useI18n();
  const id = useId();
  const [open, setOpen] = useState<number | null>(1);
  return (
    <section id="faq" className="lp-section lp-faq" aria-labelledby="lp-faq-title">
      <div className="lp-wrap lp-faq__inner">
        <Reveal className="lp-faq__head">
          <Eyebrow icon={CircleHelp}>{t("landing.eyebrow.faq")}</Eyebrow>
          <h2 id="lp-faq-title" className="lp-h2">
            {t("landing.faq.title")}
          </h2>
          <p className="lp-lead">{t("landing.faq.lead")}</p>
        </Reveal>
        <Reveal className="faq" delay={100}>
          {[1, 2, 3, 4, 5, 6].map((n) => {
            const expanded = open === n;
            return (
              <div key={n} className={cn("faq__item", expanded && "is-open")}>
                <h3>
                  <button
                    type="button"
                    className="faq__q"
                    aria-expanded={expanded}
                    aria-controls={id + n}
                    onClick={() => setOpen(expanded ? null : n)}
                  >
                    {t("landing.faq.q" + n)}
                    <span className="faq__icon" aria-hidden>
                      <Plus size={16} />
                    </span>
                  </button>
                </h3>
                <div id={id + n} className="faq__a" role="region" aria-label={t("landing.faq.q" + n)}>
                  <div>
                    <p>{t("landing.faq.a" + n)}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </Reveal>
      </div>
    </section>
  );
}

export function Close({ demo }: { demo: Start }) {
  const { t } = useI18n();
  return (
    <section className="lp-close" aria-labelledby="lp-close-title">
      <Reveal className="lp-wrap lp-close__card" scale>
        <div className="lp-close__clouds" aria-hidden>
          <Clouds />
        </div>
        <div className="lp-close__inner">
          <span className="lp-close__mark">
            <BrandMark size={44} />
          </span>
          <h2 id="lp-close-title" className="lp-h2">
            {t("landing.close.title")}
          </h2>
          <p className="lp-lead">{t("landing.close.lead")}</p>
          <DemoButton demo={demo} label={t("landing.hero.demo")} />
          <p className="lp-note">{t("landing.close.note")}</p>
        </div>
      </Reveal>
    </section>
  );
}

export function Footer() {
  const { t } = useI18n();
  return (
    <footer className="lp-footer">
      <div className="lp-wrap lp-footer__grid">
        <div className="lp-footer__brand">
          <Brand />
          <p>{t("landing.footer.line")}</p>
        </div>
        <nav aria-label={t("landing.footer.product")}>
          <h2>{t("landing.footer.product")}</h2>
          <a href="#how">{t("landing.nav.how")}</a>
          <a href="#gate">{t("landing.nav.gate")}</a>
          <a href="#features">{t("landing.nav.features")}</a>
          <a href="#honest">{t("landing.nav.honest")}</a>
          <a href="#faq">{t("landing.nav.faq")}</a>
        </nav>
        <nav aria-label={t("landing.footer.app")}>
          <h2>{t("landing.footer.app")}</h2>
          <a href="#/login">{t("landing.nav.signIn")}</a>
          <a href="#/register">{t("landing.login.titleRegister")}</a>
          <a href="#/login">{t("landing.footer.demo")}</a>
        </nav>
      </div>
    </footer>
  );
}
