/** Ringkasan per produk, dari kolom produk yang sudah ada di berkas yang diunggah.
 *
 * Tabel betulan, bukan kartu. Yang dikerjakan pembaca di sini adalah membandingkan angka yang
 * sejenis antar baris - "produk mana yang paling banyak dikeluhkan" - dan itu persis tugas
 * yang diselesaikan kolom sejajar. Kartu memaksa mata melompat, dan pada dua puluh produk
 * pelompatan itu berhenti menjadi mungkin.
 *
 * Dua dataset contoh membentuk potongan ini karena bentuknya berlawanan, dan keduanya nyata:
 * ekspor Shopee asli memuat 2 produk atas 66 ulasan (perbandingan yang bermakna), sedangkan
 * berkas kurasi memuat 90 produk atas 120 ulasan - hampir semuanya satu ulasan masing-masing.
 * Produk bersampel tipis karena itu tidak dibuang, hanya dilipat di balik satu baris ringkasan:
 * membuangnya diam-diam akan menyembunyikan justru bentuk data yang perlu diketahui pengguna
 * sebelum ia menarik kesimpulan apa pun per produk.
 */

import { useState } from "react";

import { aspectLabel, desimal, pct } from "../../lib/format.js";
import { useOverflowX } from "../../lib/hooks.js";

const KOLOM = [
  ["produk", "Produk", "kiri"],
  ["ulasan", "Ulasan", "kanan"],
  ["bintang", "Rata-rata", "kanan"],
  ["keluhan", "Berkeluhan", "kanan"],
  ["sebaran", "Sebaran bintang", "kiri"],
];

const PENGURUT = {
  produk: (a, b) => a.product_name.localeCompare(b.product_name, "id"),
  ulasan: (a, b) => b.total_reviews - a.total_reviews,
  bintang: (a, b) => (b.avg_rating ?? -1) - (a.avg_rating ?? -1),
  keluhan: (a, b) => b.pct_negative - a.pct_negative,
  sebaran: (a, b) => b.total_reviews - a.total_reviews,
};

/** Sebaran bintang satu produk sebagai lima batang mini.
 *
 * Selalu lima keranjang, termasuk yang nol - batang yang jumlah keranjangnya berubah antar
 * baris tidak bisa dibandingkan sekilas, dan perbandingan sekilas adalah satu-satunya gunanya
 * pada ukuran sekecil ini.
 */
function MiniSebaran({ ratings, total }) {
  if (!ratings?.length || !total) return <span className="meta">—</span>;
  const max = Math.max(...ratings, 1);
  return (
    <span className="mini" aria-hidden="true">
      {ratings.map((n, i) => (
        <i
          key={i}
          className={`mini__bar mini__bar--${i + 1}`}
          style={{ height: `${Math.max((n / max) * 100, n ? 12 : 0)}%` }}
          title={`${i + 1} bintang: ${n} ulasan`}
        />
      ))}
    </span>
  );
}

function BarisProduk({ produk, terbuka, onToggle }) {
  const bisaDibuka = produk.complaints.length > 0 || produk.total_reviews > 0;

  return (
    <>
      <tr
        className={`ptabel__baris ${terbuka ? "ptabel__baris--buka" : ""} ${
          produk.sparse ? "ptabel__baris--tipis" : ""
        }`}
      >
        <th scope="row">
          <button
            className="ptabel__nama"
            onClick={onToggle}
            aria-expanded={bisaDibuka ? terbuka : undefined}
          >
            <span className="ptabel__panah" aria-hidden="true">
              ›
            </span>
            {produk.product_name}
          </button>
        </th>
        <td className="stat">{produk.total_reviews}</td>
        <td className="stat">{produk.avg_rating != null ? desimal(produk.avg_rating, 2) : "—"}</td>
        <td>
          <span className="stat">{pct(produk.pct_negative)}</span>
          <em className="ptabel__dari"> ({produk.negative_reviews})</em>
        </td>
        <td>
          <MiniSebaran ratings={produk.ratings} total={produk.total_reviews} />
        </td>
      </tr>

      {terbuka && (
        <tr className="ptabel__laci">
          <td colSpan={KOLOM.length}>
            {produk.complaints.length > 0 ? (
              <>
                <p className="meta">Keluhan terbanyak pada produk ini:</p>
                <ul className="ptabel__keluhan">
                  {produk.complaints.map((c) => (
                    <li key={c.aspect}>
                      {aspectLabel(c.aspect)} <span className="stat">{c.count}</span>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p className="meta">
                Tidak ada keluhan yang terdeteksi pada produk ini dari{" "}
                <span className="stat">{produk.total_reviews}</span> ulasannya.
              </p>
            )}
            {produk.sparse && (
              <p className="meta">
                Ulasannya kurang dari tiga. Persentase di baris ini bergerak liar oleh satu
                ulasan saja, jadi bacalah sebagai catatan, bukan sebagai ukuran.
              </p>
            )}
          </td>
        </tr>
      )}
    </>
  );
}

export function ProductTable({ products }) {
  const [urut, setUrut] = useState("ulasan");
  const [buka, setBuka] = useState(null);
  const [lipat, setLipat] = useState(true);
  const [scroll, fits] = useOverflowX();

  if (!products?.length) return null;

  const utama = products.filter((p) => !p.sparse);
  const tipis = products.filter((p) => p.sparse);

  // Kalau SELURUH produk bersampel tipis, melipat semuanya akan menyisakan tabel kosong.
  // Dalam keadaan itu yang dilipat tidak ada, dan catatannya yang bicara.
  const semuanyaTipis = utama.length === 0;
  const tampil = [...utama, ...(lipat && !semuanyaTipis ? [] : tipis)].sort(PENGURUT[urut]);

  return (
    <div className="ptabel">
      <div className={`mtable-scroll ${fits ? "mtable-scroll--fit" : ""}`} ref={scroll}>
        <table className="mtable ptabel__tabel">
          <caption className="sr-only">
            Ringkasan per produk. Tekan nama produk untuk melihat keluhan di dalamnya.
          </caption>
          <thead>
            <tr>
              {KOLOM.map(([id, label, sisi]) => (
                <th key={id} scope="col" className={`ptabel__kepala ptabel__kepala--${sisi}`}>
                  <button
                    onClick={() => setUrut(id)}
                    aria-pressed={urut === id}
                    className={urut === id ? "ptabel__urut ptabel__urut--on" : "ptabel__urut"}
                  >
                    {label}
                    {urut === id && (
                      <span aria-hidden="true" className="ptabel__tanda">
                        ↓
                      </span>
                    )}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tampil.map((p) => (
              <BarisProduk
                key={p.product_name}
                produk={p}
                terbuka={buka === p.product_name}
                onToggle={() => setBuka(buka === p.product_name ? null : p.product_name)}
              />
            ))}
          </tbody>
        </table>
      </div>

      {tipis.length > 0 && !semuanyaTipis && (
        <button className="link-more" onClick={() => setLipat(!lipat)}>
          {lipat
            ? `Tampilkan ${tipis.length} produk dengan kurang dari 3 ulasan →`
            : "Sembunyikan produk bersampel tipis ←"}
        </button>
      )}

      {semuanyaTipis && (
        <p className="meta">
          Seluruh <span className="stat">{products.length}</span> produk di berkas Anda punya
          kurang dari tiga ulasan masing-masing. Perbandingan antar produk belum bermakna pada
          data berbentuk seperti ini - angka per produk di atas terlalu mudah berubah oleh satu
          ulasan. Yang tetap dapat dipercaya adalah angka gabungan di bagian lain laporan.
        </p>
      )}
    </div>
  );
}
