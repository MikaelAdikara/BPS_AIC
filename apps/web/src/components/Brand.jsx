/** Identitas yang dipakai kedua cangkang: halaman pemasaran dan dashboard.
 *
 * Lambangnya gelembung percakapan yang bagian dalamnya sekaligus kaca pembesar - ulasan yang
 * dibaca, bukan sekadar dikumpulkan. Berkas sumbernya dua render JPEG di akar repositori;
 * `scripts/build_brand_assets.py` yang mengubahnya menjadi PNG bertransparansi di
 * `public/brand/`, lengkap dengan alasan tiap langkahnya.
 *
 * Lockupnya bertumpuk - lambang di atas, kata "Ulasin" di bawahnya. Bentuk itu dipilih supaya
 * nama produk terbaca sebagai nama, bukan sebagai label yang menempel di samping ikon.
 *
 * Kata "Ulasin" pada lockup nav sengaja tetap TEKS, bukan bagian dari gambar: warnanya harus
 * ikut berganti bersama tema, dan biru tua pada berkas lockup hanya 2,6:1 di atas kanvas
 * gelap. Berkas lockup dipakai di tempat yang latarnya sudah pasti - lihat `BrandLockup`.
 */

/** Lambang yang berdiri sendiri - dipakai di tempat yang sudah menyebut nama produknya.
 *
 * `mark.png` berukuran 256px dan melayani seluruh pemakaian di bawah 128px; `mark-512.png`
 * hanya diminta oleh layar rapat-piksel lewat `srcSet`, jadi kunjungan biasa tidak menanggung
 * 300 KB hanya untuk ikon 30px. */
export function BrandMark({ size = 30, className = "" }) {
  return (
    <img
      className={`brand__mark ${className}`}
      src="/brand/mark.png"
      srcSet="/brand/mark.png 256w, /brand/mark-512.png 512w"
      sizes={`${size}px`}
      width={size}
      height={size}
      alt=""
      aria-hidden="true"
      decoding="async"
    />
  );
}

/** Lambang + kata sebagai satu gambar utuh.
 *
 * Dipakai HANYA di permukaan yang warnanya tidak ikut berganti bersama tema - kartu penutup
 * halaman pemasaran selalu gelap di kedua tema, jadi varian terangnya yang selalu benar di
 * sana. `variant` ada supaya pemanggil menyatakan latar tempat ia dipasang, bukan menebaknya.
 */
export function BrandLockup({ variant = "onLight", height = 30 }) {
  const src = variant === "onDark" ? "/brand/lockup-dark.png" : "/brand/lockup.png";
  return (
    <img
      className="brand__lockup"
      src={src}
      height={height}
      style={{ height }}
      alt="Ulasin"
      decoding="async"
    />
  );
}

export function Brand({ onClick, layout = "stack" }) {
  return (
    <button
      className={`brand brand--${layout}`}
      onClick={onClick}
      aria-label="Ulasin, kembali ke beranda"
    >
      <BrandMark size={layout === "stack" ? 32 : 30} />
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
