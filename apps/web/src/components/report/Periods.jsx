/** Riwayat antar periode, dan lintasan tiap aspek di sepanjangnya.
 *
 * Batasnya disebut di layar, bukan hanya di dokumen: ini BUKAN riwayat lintas sesi. Tidak ada
 * yang disimpan setelah halaman ditutup. Yang digambar di sini adalah berkas yang baru saja
 * diunggah, dibelah menurut kolom tanggalnya sendiri - dan itu ternyata cukup, karena ekspor
 * marketplace hampir selalu memuat berbulan-bulan sekaligus.
 *
 * Dua keadaan digambar berbeda dan keduanya penting:
 *
 *   KOSONG   periode tanpa satu pun ulasan. Digambar sebagai bingkai putus-putus, tetap
 *            memakan lebarnya sendiri. Menghilangkannya akan merapatkan sumbu waktu, dan
 *            kenaikan yang sebenarnya terpisah satu kuartal akan tampak seperti kenaikan
 *            bulan-ke-bulan.
 *   TIPIS    periode berisi kurang dari tiga ulasan. Digambar bergaris miring. Satu ulasan
 *            negatif adalah "100% negatif" secara aritmetika, dan batang penuh tanpa tanda
 *            adalah cara tercepat membuat pemilik toko panik atas satu orang.
 */

import { aspectLabel, desimal, pct } from "../../lib/format.js";

/** Lintasan satu aspek sebagai garis kecil, dipakai di dalam baris aspek.
 *
 * Tanpa sumbu, tanpa label, tanpa kisi - pada lebar 64px semuanya berubah jadi bercak. Yang
 * dibaca dari bentuk sekecil ini cuma satu hal, yaitu arahnya, dan untuk itu garis saja sudah
 * cukup. Angka pastinya ada di laci yang terbuka tepat di bawahnya.
 */
export function Sparkline({ counts, buckets, width = 64, height = 18 }) {
  if (!counts?.length || counts.length < 2) return null;

  const max = Math.max(...counts, 1);
  const dx = width / (counts.length - 1);
  const titik = counts.map((n, i) => [i * dx, height - (n / max) * (height - 2) - 1]);
  const d = titik.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");

  const akhir = titik[titik.length - 1];
  const naik = counts[counts.length - 1] > counts[0];

  const ringkas = buckets
    ? `${buckets[0]?.label} ${counts[0]} keluhan, ${buckets[buckets.length - 1]?.label} ${
        counts[counts.length - 1]
      } keluhan`
    : undefined;

  return (
    <svg
      className="spark"
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={ringkas}
    >
      <path d={d} fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <circle cx={akhir[0]} cy={akhir[1]} r="2" className={naik ? "spark__naik" : "spark__turun"} />
    </svg>
  );
}

function Batang({ bucket, max }) {
  const tinggi = max ? (bucket.total_reviews / max) * 100 : 0;
  const negatif = bucket.total_reviews
    ? (bucket.negative_reviews / bucket.total_reviews) * 100
    : 0;

  const keterangan = bucket.empty
    ? `${bucket.label}: tidak ada ulasan`
    : `${bucket.label}: ${bucket.total_reviews} ulasan, ${bucket.negative_reviews} berisi keluhan${
        bucket.avg_rating != null ? `, rata-rata ${desimal(bucket.avg_rating, 2)} bintang` : ""
      }${bucket.sparse ? " - terlalu sedikit untuk dipersentasekan" : ""}`;

  return (
    <li
      className={`rbar ${bucket.empty ? "rbar--kosong" : ""} ${bucket.sparse ? "rbar--tipis" : ""}`}
      title={keterangan}
    >
      <span className="rbar__kolom">
        <span className="rbar__track" aria-hidden="true">
          <i className="rbar__isi" style={{ height: `${tinggi}%` }}>
            <i className="rbar__neg" style={{ height: `${negatif}%` }} />
          </i>
        </span>
      </span>
      <span className="sr-only">{keterangan}</span>
      <span className="rbar__jml" aria-hidden="true">
        {bucket.empty ? "–" : bucket.total_reviews}
      </span>
      <span className="rbar__label" aria-hidden="true">
        {bucket.label}
      </span>
    </li>
  );
}

export function PeriodChart({ history }) {
  if (!history) return null;

  if (history.granularity === "tidak_cukup") {
    return (
      <div className="banner-grey">
        {history.note ?? "Riwayat antar periode belum bisa dihitung dari data ini."}
      </div>
    );
  }

  const max = Math.max(...history.buckets.map((b) => b.total_reviews), 1);
  const berisi = history.buckets.filter((b) => !b.empty);
  const pertama = berisi[0];
  const terakhir = berisi[berisi.length - 1];

  return (
    <div className="riwayat">
      <div className="legend">
        <span>
          <i style={{ background: "var(--blue)" }} />
          Seluruh ulasan
        </span>
        <span>
          <i style={{ background: "var(--red-base)" }} />
          Yang memuat keluhan
        </span>
      </div>

      <ul className={`rbars rbars--${history.granularity}`}>
        {history.buckets.map((b) => (
          <Batang key={b.period} bucket={b} max={max} />
        ))}
      </ul>

      {pertama && terakhir && pertama !== terakhir && (
        <p className="riwayat__banding">
          Dari <b>{pertama.label}</b> ke <b>{terakhir.label}</b>, porsi ulasan yang memuat keluhan
          bergerak dari <span className="stat">{pct(pertama.pct_negative)}</span> ke{" "}
          <span className="stat">{pct(terakhir.pct_negative)}</span>
          {pertama.avg_rating != null && terakhir.avg_rating != null && (
            <>
              {" "}
              dan rata-rata bintang dari{" "}
              <span className="stat">{desimal(pertama.avg_rating, 2)}</span> ke{" "}
              <span className="stat">{desimal(terakhir.avg_rating, 2)}</span>
            </>
          )}
          .
        </p>
      )}

      {history.series.length > 0 && (
        <div className="riwayat__seri">
          <p className="meta">Lintasan tiap aspek sepanjang periode yang sama:</p>
          <ul>
            {history.series.map((s) => (
              <li key={s.aspect}>
                <span className="riwayat__seri-nama">{aspectLabel(s.aspect)}</span>
                <Sparkline counts={s.counts} buckets={history.buckets} width={110} height={22} />
                <span className="riwayat__seri-angka">
                  <span className="stat">{s.total}</span> keluhan
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {history.note && <p className="meta riwayat__nota">{history.note}</p>}

      <p className="meta riwayat__batas">
        Grafik ini dihitung dari kolom tanggal di berkas yang baru saja Anda unggah, bukan dari
        riwayat yang tersimpan. Tidak ada data Anda yang disimpan setelah halaman ini ditutup.
      </p>
    </div>
  );
}
