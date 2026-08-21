/** Identitas yang dipakai kedua cangkang: halaman pemasaran dan dashboard.
 *
 * Lambangnya gelembung percakapan yang bagian dalamnya sekaligus kaca pembesar - ulasan yang
 * dibaca, bukan sekadar dikumpulkan. Berkas sumbernya `Logo.png` di akar repositori;
 * `scripts/build_brand_assets.py` yang memotongnya menjadi lambang, lockup, dan favicon di
 * `public/brand/`.
 *
 * Lockupnya bertumpuk - lambang di atas, kata "Ulasin" di bawahnya. Bentuk itu dipilih supaya
 * nama produk terbaca sebagai nama, bukan sebagai label yang menempel di samping ikon.
 *
 * Kata "Ulasin" pada lockup nav sengaja tetap TEKS, bukan bagian dari gambar: warnanya harus
 * ikut berganti bersama tema, dan `--ink` bergerak jauh lebih lebar antar tema daripada biru
 * pada berkas lockup.
 */

/** Lambang yang berdiri sendiri - dipakai di tempat yang sudah menyebut nama produknya.
 *
 * Satu berkas 160px melayani seluruh pemakaian: ukuran terbesarnya di layar 32px, jadi 160px
 * masih tajam sampai kerapatan piksel 5x. Versi sebelumnya menyertakan `mark-512.png` lewat
 * `srcSet` dan itu 300 KB untuk ikon 30px. */
export function BrandMark({ size = 30, className = "" }) {
  return (
    <img
      className={`brand__mark ${className}`}
      src="/brand/mark.png"
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
 * Satu berkas untuk kedua tema. Kata "Ulasin" pada logo bergradien biru terang - piksel
 * paling gelapnya 3,1:1 di atas kanvas gelap, rata-ratanya 5,5:1 - jadi tidak ada lagi
 * varian gelap yang mewarnai ulang hurufnya seperti pada logo lama. */
export function BrandLockup({ height = 30 }) {
  return (
    <img
      className="brand__lockup"
      src="/brand/lockup.png"
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
