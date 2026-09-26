import {
  ArrowRight,
  Bell,
  Database,
  FlaskConical,
  Inbox,
  LayoutGrid,
  Lock,
  Ruler,
} from "lucide-react";
import { Brand, LangToggle, ThemeToggle } from "@/components/Brand.jsx";
import { Button } from "@/components/ui";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
import { Clouds } from "./Clouds";
import { useScrollProgress, useScrolledPast } from "./hooks";

type Start = { start: () => void; busy: boolean; error: string | null; signedIn: boolean };

export function SiteNav({ demo }: { demo: Start }) {
  const { t } = useI18n();
  const scrolled = useScrolledPast(12);
  return (
    <header className={cn("lp-nav", scrolled && "is-scrolled")}>
      <div className="lp-nav__inner">
        <Brand />
        <nav className="lp-nav__links" aria-label={t("landing.nav.label")}>
          <a href="#how">{t("landing.nav.how")}</a>
          <a href="#gate">{t("landing.nav.gate")}</a>
          <a href="#features">{t("landing.nav.features")}</a>
          <a href="#honest">{t("landing.nav.honest")}</a>
        </nav>
        <div className="lp-nav__tools">
          <LangToggle />
          <ThemeToggle />
          {demo.signedIn ? (
            <a className="btn btn--outline btn--sm lp-nav__signin" href="#/app">
              {t("landing.nav.openApp")}
            </a>
          ) : (
            <a className="btn btn--outline btn--sm lp-nav__signin" href="#/login">
              {t("landing.nav.signIn")}
            </a>
          )}
        </div>
      </div>
    </header>
  );
}

export function DemoButton({ demo, label }: { demo: Start; label: string }) {
  const { localizeError, t } = useI18n();
  return (
    <div className="lp-demo">
      <Button size="lg" busy={demo.busy} onClick={() => void demo.start()}>
        {label}
        <ArrowRight size={18} aria-hidden />
      </Button>
      {demo.error && (
        <p className="lp-demo__error" role="alert">
          {t("landing.hero.demoError")} {localizeError(demo.error)}
        </p>
      )}
    </div>
  );
}

export function Hero({ demo }: { demo: Start }) {
  const { t } = useI18n();
  const stage = useScrollProgress<HTMLDivElement>();
  return (
    <section className="lp-hero" aria-labelledby="lp-hero-title">
      <div className="lp-wrap lp-hero__copy">
        <h1 id="lp-hero-title" className="lp-hero__title">
          <span>{t("landing.hero.titleA")}</span>
          <span className="lp-hero__accent">{t("landing.hero.titleB")}</span>
        </h1>
        <p className="lp-lead lp-hero__lead">{t("landing.hero.lead")}</p>
        <div className="lp-hero__actions">
          <DemoButton demo={demo} label={t("landing.hero.demo")} />
          <a className="btn btn--outline btn--lg" href={demo.signedIn ? "#/app" : "#/login"}>
            {demo.signedIn ? t("landing.nav.openApp") : t("landing.hero.signIn")}
          </a>
        </div>
        <p className="lp-note">{t("landing.hero.note")}</p>
      </div>
      <div className="lp-stage" ref={stage} aria-hidden>
        <div className="lp-stage__clouds">
          <Clouds />
        </div>
        <div className="lp-stage__window">
          <ProductWindow />
        </div>
        <div className="lp-stage__cards">
          <ReviewStack />
        </div>
      </div>
    </section>
  );
}

function ProductWindow() {
  const { t } = useI18n();
  return (
    <div className="mock">
      <div className="mock__bar">
        <span className="mock__dots">
          <i />
          <i />
          <i />
        </span>
        <span className="mock__url">{t("landing.mock.url")}</span>
      </div>
      <div className="mock__body">
        <aside className="mock__side">
          <span className="mock__brand">
            <img src="/brand/mark.png" width={18} height={18} alt="" />
            Deciqo
          </span>
          <span className="mock__nav">
            <LayoutGrid size={14} />
            {t("landing.mock.navOverview")}
          </span>
          <span className="mock__nav is-active">
            <Inbox size={14} />
            {t("landing.mock.navIssues")}
            <b className="mock__badge">3</b>
          </span>
          <span className="mock__nav">
            <Database size={14} />
            {t("landing.mock.navSources")}
          </span>
          <span className="mock__nav">
            <Bell size={14} />
            {t("landing.mock.navAlerts")}
          </span>
        </aside>
        <div className="mock__main">
          <div className="mock__chips">
            <span className="chip tone-warn">{t("landing.mock.chipFact")}</span>
            <span className="chip tone-muted">{t("landing.mock.chipSize")}</span>
            <span className="chip tone-muted">
              <FlaskConical size={12} />
              {t("landing.mock.chipSynthetic")}
            </span>
          </div>
          <p className="mock__title">{t("landing.mock.product")}</p>
          <p className="mock__next">{t("landing.mock.next")}</p>
          <div className="mock__panels">
            <div className="mock__panel">
              <p className="mock__count">{t("landing.mock.count")}</p>
              <p className="mock__quote">“{t("landing.mock.quote1")}”</p>
              <p className="mock__quote">“{t("landing.mock.quote2")}”</p>
            </div>
            <div className="mock__panel mock__panel--amber">
              <p className="mock__finding">{t("landing.mock.finding")}</p>
              <div className="mock__input">
                <Ruler size={14} />
                <span>{t("landing.mock.inputValue")}</span>
                <span className="mock__confirm">{t("landing.mock.confirm")}</span>
              </div>
              <p className="mock__held">
                <Lock size={12} />
                {t("landing.mock.held")}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ReviewStack() {
  const { t } = useI18n();
  const cards = [
    { id: 1042, stars: 2, quote: "landing.mock.quote1" },
    { id: 1057, stars: 5, quote: "landing.mock.quote3" },
    { id: 1063, stars: 3, quote: "landing.mock.quote2" },
  ];
  return (
    <div className="rstack">
      {cards.map((c, i) => (
        <div key={c.id} className={"rcard rcard--" + i}>
          <p className="rcard__meta">{t("landing.mock.review", { id: c.id, stars: c.stars })}</p>
          <p className="rcard__quote">“{t(c.quote)}”</p>
          <p className="rcard__label">
            <FlaskConical size={11} />
            {t("landing.mock.chipSynthetic")}
          </p>
        </div>
      ))}
    </div>
  );
}
