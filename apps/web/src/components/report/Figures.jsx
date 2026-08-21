/** Kepala laporan: angka yang dibaca lebih dulu dari apa pun, dan kategori pembandingnya.
 *
 * Bentuknya deretan angka yang dipisah garis, BUKAN baris kartu statistik. Kartu statistik -
 * angka besar, label kecil, satu per kotak, berjajar empat - adalah bentuk baku dashboard mana
 * pun dan justru karena itu ia berhenti memberi tahu apa pun tentang laporan ini. Ia juga
 * memakan tinggi yang sama besarnya dengan bagian yang benar-benar perlu dibaca.
 *
 * Lima angka di sini dipilih karena masing-masing dipakai untuk menimbang angka SESUDAHNYA:
 * berapa ulasannya (seberapa jauh hasil ini layak dipercaya), rata-rata bintang (titik acuan
 * yang sudah dikenal pemilik toko dari dashboard marketplace), berapa yang memuat keluhan
 * (penyebut untuk seluruh persentase di bawah), rentang tanggalnya (apakah ini foto minggu
 * lalu atau setahun terakhir), dan kategori pembandingnya.
 *
 * Kategori ditampilkan sebagai ANGKA yang dibaca, bukan sebagai kontrol yang bisa diubah.
 * Versi sebelumnya menaruh `<select>` di sini supaya tebakan sistem dapat dikoreksi tanpa
 * analisis ulang. Secara teknis itu berjalan, tetapi salah tempat: pembaca laporan sedang
 * membaca, bukan menyiapkan, dan satu-satunya kontrol di tengah deretan angka - yang justru
 * MENGUBAH angka di bawahnya - terbaca sebagai rancu. Kategori adalah keterangan penyiapan,
 * jadi ia dipilih di layar unggah dan di sini cuma dilaporkan kembali.
 */

import { CATEGORY_LABEL, desimal, pct, rentangTanggal } from "../../lib/format.js";
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

export function SummaryHead({ result, category }) {
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
        <Angka
          nilai={CATEGORY_LABEL[category] ?? category}
          nama="kategori pembanding"
          sub="dipilih di layar unggah"
        />
      </div>

      <Narrative text={summary.executive_summary_text} className="ringkas__narasi" />
    </div>
  );
}
