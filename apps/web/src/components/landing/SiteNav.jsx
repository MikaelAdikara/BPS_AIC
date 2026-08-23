import { Brand, ThemeToggle } from "../Brand.jsx";

export function SiteNav({ onStart, theme, onToggleTheme }) {
  return (
    <nav className="nav">
      <Brand onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} />

      <div className="nav__links">
        <a href="#bukti">Bukti</a>
        <a href="#cara-kerja">Cara kerja</a>
        <a href="#studi-kasus">Studi kasus</a>
        <a href="#nilai">Nilai</a>
      </div>

      <div className="nav__right">
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />
        <button className="btn btn--primary" onClick={onStart}>
          Mulai Analisis ›
        </button>
      </div>
    </nav>
  );
}
