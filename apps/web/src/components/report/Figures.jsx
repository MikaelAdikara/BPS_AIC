/** Kepala laporan: angka yang dibaca lebih dulu dari apa pun, dan kategori pembandingnya.
 *
 * Bentuknya deretan angka yang dipisah garis, BUKAN baris kartu statistik. Kartu statistik -
 * angka besar, label kecil, satu per kotak, berjajar empat - adalah bentuk baku dashboard mana
 * pun dan justru karena itu ia berhenti memberi tahu apa pun tentang laporan ini. Ia juga
 * memakan tinggi yang sama besarnya dengan bagian yang benar-benar perlu dibaca.
 *
 * Empat angka di sini dipilih karena masing-masing dipakai untuk menimbang angka SESUDAHNYA:
 * berapa ulasannya (seberapa jauh hasil ini layak dipercaya), rata-rata bintang (titik acuan
 * yang sudah dikenal pemilik toko dari dashboard marketplace), berapa yang memuat keluhan
 * (penyebut untuk seluruh persentase di bawah), dan rentang tanggalnya (apakah ini foto
 * minggu lalu atau setahun terakhir).
 */

import { CATEGORIES, desimal, pct, rentangTanggal } from "../../lib/format.js";
import { Narrative } from "../insight.jsx";

/** Satu angka beserta namanya. `sub` untuk keterangan yang menimbang angkanya. */
function Angka({ nilai, nama, sub }) {
  return (
    <div className="angka">
      <span className="angka__nilai">{nilai}</span>
      <span className="angka__nama">{nama}</span>
      {sub && <span className="angka__sub">{sub}</span>}
    </div>
  );
}

/** Chip kategori - tebakan sistem yang bisa diganti pengguna.
 *
 * `<select>` bawaan, bukan menu buatan sendiri. Ini persis tugas yang sudah diselesaikan
 * elemen bawaan (papan ketik, pembaca layar, pemilih ala ponsel), dan laporan analitik bukan
 * tempat menciptakan afordans baru untuk pekerjaan yang sudah baku.
 *
 * Kenapa tebakannya ditampilkan alih-alih dipakai diam-diam: kategori memilih baseline
 * pembanding, dan baseline itu muncul beberapa baris di bawah sebagai selisih persen yang
 * terbaca seperti fakta. Tebakan yang keliru akan menaruh angka keliru di tempat yang paling
 * dipercaya, jadi ia diletakkan di sini - terlihat, dan bisa dikoreksi dalam satu klik tanpa
 * mengulang analisis.
 */
function KategoriChip({ guess, category, onChange }) {
  const ragu = !guess || guess.confidence === "rendah" || guess.basis === "bawaan";
  const diubah = guess && category !== guess.category;

  const dasar = !guess
    ? null
    : diubah
      ? `Anda ganti dari tebakan sistem (${guess.category})`
      : guess.basis === "bawaan"
        ? "Sistem tidak menemukan petunjuk kategori - pilih sendiri agar pembandingnya tepat"
        : `Ditebak dari ${guess.basis} · cocok pada ${guess.matched_reviews} dari ${guess.total_reviews} ulasan`;

  return (
    <div className={`kchip ${ragu && !diubah ? "kchip--ragu" : ""}`}>
      <label className="kchip__label" htmlFor="kategori-banding">
        Dibandingkan terhadap
      </label>
      <select
        id="kategori-banding"
        className="kchip__pilih"
        value={category}
        onChange={(e) => onChange(e.target.value)}
      >
        {CATEGORIES.map(([id, label]) => (
          <option key={id} value={id}>
            {label}
          </option>
        ))}
      </select>
      {dasar && <p className="kchip__dasar">{dasar}</p>}
    </div>
  );
}

export function SummaryHead({ result, category, onCategory }) {
  const { summary, ratings } = result;
  const rentang = rentangTanggal(summary.period_start, summary.period_end);
  const porsiKeluhan = summary.total_reviews
    ? summary.reviews_with_complaint / summary.total_reviews
    : 0;

  return (
    <div className="ringkas">
      <div className="ringkas__angka">
        <Angka nilai={summary.total_reviews} nama="ulasan dianalisis" />
        <Angka
          nilai={ratings?.average != null ? desimal(ratings.average, 2) : "—"}
          nama="rata-rata bintang"
          sub={
            ratings?.without_rating
              ? `${ratings.without_rating} tanpa rating`
              : ratings
                ? null
                : "tidak ada kolom rating"
          }
        />
        <Angka
          nilai={pct(porsiKeluhan)}
          nama="ulasan memuat keluhan"
          sub={`${summary.reviews_with_complaint} dari ${summary.total_reviews}`}
        />
        <Angka nilai={rentang ?? "—"} nama="rentang tanggal" sub={rentang ? null : "tanpa tanggal"} />
      </div>

      <KategoriChip guess={result.category_guess} category={category} onChange={onCategory} />

      <Narrative text={summary.executive_summary_text} className="ringkas__narasi" />
    </div>
  );
}
