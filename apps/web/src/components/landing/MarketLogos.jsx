/** Logo marketplace ASLI - satu sumber untuk pita, bagian urgensi, dan halaman panduan.
 *
 * Tiga wordmark (Shopee, Tokopedia, Lazada) adalah berkas SVG resmi dari Wikimedia Commons
 * berstatus public domain, disajikan lewat <img> dari /brand/logos. Tiga lainnya (TikTok,
 * Bukalapak, Google) adalah glif CC0 dari Simple Icons yang di-inline di sini supaya warnanya
 * dapat mengikuti tema - glif TikTok hitam di atas latar gelap tidak terlihat kalau dipasang
 * sebagai gambar. Glif disandingkan dengan nama merek sebagai teks, karena glifnya sendiri
 * bukan wordmark.
 *
 * Logo di sini menandai SUMBER ULASAN yang didukung, bukan kemitraan. Atribusi lengkap ada
 * di public/brand/logos/README.md.
 */

const TIKTOK =
  "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z";

const BUKALAPAK =
  "M10.976 23.845a3.158 3.158 0 1 1-1.95-6.008 3.158 3.158 0 0 1 1.95 6.008Zm6.554-2.883c4.047-1.315 7.315-5.981 5.689-10.984-1.626-5.003-7.012-6.856-11.058-5.541a1.89 1.89 0 0 0-1.252 2.249l.414 1.682a1.892 1.892 0 0 0 2.42 1.348l.162-.053c1.861-.606 3.592.504 4.071 2.019.505 1.507-.244 3.422-2.106 4.027l-.162.054a1.891 1.891 0 0 0-1.166 2.512l.653 1.604a1.89 1.89 0 0 0 2.335 1.083Zm-6.962-7.982L7.841 1.752A2.3 2.3 0 0 0 4.897.113l-2.952.959A2.3 2.3 0 0 0 .526 4.128L4.92 14.815a2.3 2.3 0 0 0 2.841 1.318l1.285-.417a2.298 2.298 0 0 0 1.522-2.736Z";

function TikTokGlyph({ size }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} aria-hidden="true">
      <path fill="currentColor" d={TIKTOK} />
    </svg>
  );
}

function BukalapakGlyph({ size }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} aria-hidden="true">
      <path fill="#E31E52" d={BUKALAPAK} />
    </svg>
  );
}

/** Huruf "G" empat warna Google - bentuk standar yang dipakai tombol masuk Google. */
function GoogleGlyph({ size }) {
  return (
    <svg viewBox="0 0 48 48" width={size} height={size} aria-hidden="true">
      <path
        fill="#EA4335"
        d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
      />
      <path
        fill="#4285F4"
        d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
      />
      <path
        fill="#FBBC05"
        d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
      />
      <path
        fill="#34A853"
        d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
      />
    </svg>
  );
}

export const LOGOS = {
  shopee: { nama: "Shopee", src: "/brand/logos/shopee.svg", rasio: 1000 / 320, warna: "#ee4d2d" },
  tokopedia: { nama: "Tokopedia", src: "/brand/logos/tokopedia.svg", rasio: 400 / 87, warna: "#42b549" },
  tiktokshop: { nama: "TikTok Shop", Glyph: TikTokGlyph, teks: "TikTok Shop", warna: "currentColor" },
  lazada: { nama: "Lazada", src: "/brand/logos/lazada.svg", rasio: 410.28 / 107.51, warna: "#000083" },
  bukalapak: { nama: "Bukalapak", Glyph: BukalapakGlyph, teks: "Bukalapak", warna: "#E31E52" },
  google: { nama: "Google Reviews", Glyph: GoogleGlyph, teks: "Google Reviews", warna: "#4285F4" },
};

export const LOGO_ORDER = ["shopee", "tokopedia", "tiktokshop", "lazada", "bukalapak", "google"];

/** Satu logo dengan tinggi seragam. Wordmark memakai rasio aslinya supaya tidak gepeng;
 *  glif+teks disejajarkan pada garis dasar yang sama. */
export function MarketLogo({ id, height = 22, className = "", hidden = false }) {
  const l = LOGOS[id];
  if (!l) return null;
  if (l.src) {
    return (
      <img
        className={`mlogo mlogo--img ${className}`}
        src={l.src}
        alt={hidden ? "" : l.nama}
        aria-hidden={hidden || undefined}
        height={height}
        width={Math.round(height * l.rasio)}
        style={{ height, width: "auto" }}
        decoding="async"
      />
    );
  }
  const Glyph = l.Glyph;
  return (
    <span
      className={`mlogo mlogo--glif ${className}`}
      aria-hidden={hidden || undefined}
      aria-label={hidden ? undefined : l.nama}
      style={{ "--mlogo-h": `${height}px` }}
    >
      <Glyph size={Math.round(height * 0.95)} />
      <b>{l.teks}</b>
    </span>
  );
}
