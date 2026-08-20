/** Identitas yang dipakai kedua cangkang: halaman pemasaran dan dashboard. */

const Logo = ({ size = 17 }) => (
  <svg width={size} height={size} viewBox="0 0 34 34" fill="none" aria-hidden="true">
    <path
      d="M4 6C4 4.34 5.34 3 7 3H27C28.66 3 30 4.34 30 6V20C30 21.66 28.66 23 27 23H16L10 28V23H7C5.34 23 4 21.66 4 20V6Z"
      fill="#fff"
    />
    <path
      d="M11 13L15 17L23 9"
      stroke="#1E4FCB"
      strokeWidth="2.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export function Brand({ onClick }) {
  return (
    <button className="brand" onClick={onClick} aria-label="InsightUlasan, kembali ke beranda">
      <span className="brand__mark">
        <Logo />
      </span>
      <span className="brand__name">
        Insight<span>Ulasan</span>
      </span>
    </button>
  );
}

export function ThemeToggle({ theme, onToggle }) {
  return (
    <button className="themebtn" onClick={onToggle} aria-pressed={theme === "dark"}>
      {theme === "dark" ? "Mode terang" : "Mode gelap"}
    </button>
  );
}
