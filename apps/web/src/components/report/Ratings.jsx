/** Sebaran bintang, dan keluhan apa yang menghuni tiap pita.
 *
 * Menyaring ulasan menurut bintang sudah dikerjakan setiap dashboard marketplace, dan
 * membangunnya ulang di sini cuma akan menjadi Shopee dengan logo lain. Yang tidak dikerjakan
 * satu pun dari mereka - dan yang jatuh gratis dari data yang sudah dihitung - adalah ISI tiap
 * pita: "dua belas ulasan bintang satu Anda, delapan di antaranya soal ukuran".
 *
 * Karena itu pita di sini bukan penyaring melainkan pertanyaan yang bisa dibuka. Menekan satu
 * pita membuka keluhan di dalamnya, bukan memfilter daftar di tempat lain.
 *
 * Lima pita selalu digambar, termasuk yang nol. Sebaran bintang dibaca dari BENTUKNYA - "huruf
 * J" atau "menumpuk di tengah" - dan bentuk itu rusak begitu pita kosong dihilangkan dan
 * tetangganya bergeser mengisi tempatnya.
 */

import { useState } from "react";

import { aspectLabel, pct } from "../../lib/format.js";

/** Bintang sebagai bentuk, bukan sebagai angka bertuliskan "1".
 *
 * Bentuk bintang terbaca tanpa dibaca - mata mengenali empat penuh dan satu kosong lebih cepat
 * daripada mengurai teks "4". Angkanya tetap ada untuk pembaca layar lewat `aria-label` di
 * barisnya, jadi bentuk tidak pernah menjadi satu-satunya pembawa arti.
 */
function Bintang({ nilai }) {
  return (
    <span className="bpita__bintang" aria-hidden="true">
      {[1, 2, 3, 4, 5].map((i) => (
        <svg key={i} viewBox="0 0 20 20" width="11" height="11" className={i <= nilai ? "on" : ""}>
          <path d="M10 1.6 12.6 7l5.9.9-4.3 4.1 1 5.9L10 15.1 4.8 17.9l1-5.9L1.5 7.9 7.4 7z" />
        </svg>
      ))}
    </span>
  );
}

function Pita({ band, maxCount, terbuka, onToggle }) {
  const adaKeluhan = band.complaints.length > 0;
  const lebar = maxCount ? (band.count / maxCount) * 100 : 0;

  return (
    <div className={`bpita ${terbuka ? "bpita--buka" : ""} ${band.count ? "" : "bpita--nol"}`}>
      <button
        className="bpita__kepala"
        onClick={onToggle}
        disabled={!adaKeluhan}
        aria-expanded={adaKeluhan ? terbuka : undefined}
        aria-label={`Bintang ${band.rating}: ${band.count} ulasan, ${pct(band.pct)} dari total${
          adaKeluhan ? `. ${band.complaints.length} jenis keluhan di dalamnya` : ""
        }`}
      >
        <Bintang nilai={band.rating} />
        <span className="bpita__track">
          <i className="bpita__isi" style={{ width: `${lebar}%` }} />
        </span>
        <span className="bpita__jml stat">{band.count}</span>
        <span className="bpita__pct">{pct(band.pct)}</span>
        {adaKeluhan && (
          <span className="bpita__panah" aria-hidden="true">
            ›
          </span>
        )}
      </button>

      {/* Grid 0fr → 1fr, bukan height auto: tinggi otomatis tidak dapat ditransisikan, dan
          `max-height` yang ditebak selalu salah untuk salah satu isi. */}
      <div className="bpita__laci" data-buka={terbuka ? "ya" : "tidak"}>
        <div className="bpita__laci-isi">
          <p className="meta">Keluhan yang muncul di ulasan bintang {band.rating}:</p>
          <ul className="bpita__keluhan">
            {band.complaints.map((c) => (
              <li key={c.aspect}>
                {aspectLabel(c.aspect)} <span className="stat">{c.count}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export function RatingBands({ ratings }) {
  const [buka, setBuka] = useState(null);
  if (!ratings) return null;

  const maxCount = Math.max(...ratings.bands.map((b) => b.count), 1);

  return (
    <div className="bpitas">
      {ratings.bands
        .slice()
        .reverse()
        .map((band) => (
          <Pita
            key={band.rating}
            band={band}
            maxCount={maxCount}
            terbuka={buka === band.rating}
            onToggle={() => setBuka(buka === band.rating ? null : band.rating)}
          />
        ))}

      <p className="meta bpitas__kaki">
        Tekan satu baris untuk melihat keluhan di dalamnya.{" "}
        {ratings.without_rating > 0 && (
          <>
            <span className="stat">{ratings.without_rating}</span> ulasan tidak membawa rating dan
            tidak masuk hitungan ini.
          </>
        )}
      </p>
    </div>
  );
}
