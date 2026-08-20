/** Identitas yang dipakai kedua cangkang: halaman pemasaran dan dashboard.
 *
 * Lockupnya bertumpuk - lambang di atas, kata "Ulasin" di bawahnya. Bentuk itu dipilih supaya
 * nama produk terbaca sebagai nama, bukan sebagai label yang menempel di samping ikon.
 *
 * Lambangnya tiga batang menaik: berapa banyak ulasan menyebut satu hal, disusun dari yang
 * paling jarang ke yang paling sering. Batang terpendek sengaja lebih pudar - itu bagian
 * yang belum jadi masalah. Sekali lihat, lambangnya menyebut isi produknya: menghitung
 * seberapa sering sesuatu disebut, lalu menaruhnya berurutan.
 */

const Logo = ({ size = 19 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <rect x="3.4" y="13.6" width="4" height="6.6" rx="2" fill="#fff" fillOpacity="0.5" />
    <rect x="10" y="9" width="4" height="11.2" rx="2" fill="#fff" fillOpacity="0.78" />
    <rect x="16.6" y="3.8" width="4" height="16.4" rx="2" fill="#fff" />
  </svg>
);

/** Lambang yang berdiri sendiri - dipakai di tempat yang sudah menyebut nama produknya. */
export function BrandMark({ size = 30 }) {
  return (
    <span className="brand__mark" style={{ width: size, height: size }}>
      <Logo size={Math.round(size * 0.63)} />
    </span>
  );
}

export function Brand({ onClick, layout = "stack" }) {
  return (
    <button
      className={`brand brand--${layout}`}
      onClick={onClick}
      aria-label="Ulasin, kembali ke beranda"
    >
      <BrandMark size={layout === "stack" ? 30 : 28} />
      <span className="brand__name">Ulasin</span>
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
