/** Bagian nilai bisnis: besaran masalahnya, celah harga di pasar, dan kenapa gratisnya bertahan.
 *
 * Versi pertama bagian ini menggambar penggaris harga logaritmik - satu garis mendatar dengan
 * tiap produk dipatok pada posisi harganya. Idenya benar (celah paling jujur digambar sebagai
 * jarak), pelaksanaannya tidak: pada skala logaritmik ketiga produk berbayar menumpuk di 40%
 * kanan penggaris sementara 60% kirinya kosong, labelnya saling bertabrakan sampai perlu
 * diturunkan bertingkat, dan garis penghubung tingkat keduanya justru melintas menembus label
 * tetangganya. Bentuk itu memaksa tabrakan berapa pun angkanya digeser.
 *
 * Yang dipakai sekarang: baris, bukan sumbu. Isinya cuma lima butir dan satu celah - jumlah
 * yang tidak menuntut sumbu sama sekali. Barisnya tidak mungkin bertabrakan, muat di lebar
 * berapa pun, dan tiap butir punya ruang untuk menyebut BATASNYA, bukan cuma harganya - dan
 * batas itulah argumen sebenarnya, karena yang gratis pun sudah kalah sebelum bicara harga.
 *
 * Celahnya tetap digambar sebagai celah: satu pita bertanda di antara dua kelompok.
 *
 * Seluruh angka di berkas ini punya sumber di docs/BUSINESS_VALUE.md. Yang belum tervalidasi
 * ditandai di layar, bukan hanya di dokumen - halaman pemasaran adalah tempat paling menggoda
 * untuk membulatkan angka, dan produk ini tidak melakukannya.
 */

// Harga masuk termurah, per bulan. Sumbernya halaman harga publik tiap vendor, 2026, dengan
// kurs Rp16.000/USD - lihat docs/BUSINESS_VALUE.md bagian 3.
const TERJANGKAU = [
  {
    nama: "Ulasin",
    harga: "Gratis",
    catatan: "Rencana berlangganan Rp39.000 - masih hipotesis",
    batas: "Mengelompokkan keluhan per aspek, mengurutkan prioritasnya, dan menyertakan kutipan aslinya.",
    kami: true,
  },
  {
    nama: "Shopee & Tokopedia Seller Centre",
    harga: "Gratis",
    catatan: "Bawaan platform",
    batas: "Berhenti di rating rata-rata dan daftar ulasan. Tanpa pengelompokan aspek, tanpa urutan prioritas - dan tiap dashboard hanya melihat kanalnya sendiri.",
  },
];

const MAHAL = [
  {
    nama: "Yotpo",
    rupiah: 1_264_000,
    catatan: "USD 79/bln",
    batas: "Alat mengumpulkan ulasan, bukan menganalisis keluhan. Tanpa prioritisasi tindakan.",
  },
  {
    nama: "Birdeye",
    rupiah: 4_784_000,
    catatan: "USD 299/bln per lokasi",
    batas: "Kontrak 12 bulan plus onboarding USD 500-1.500. Dirancang untuk bisnis multi-cabang.",
  },
  {
    nama: "Thematic",
    rupiah: 32_000_000,
    catatan: "USD 2.000/bln, 3 pengguna",
    batas: "Benar-benar mengekstrak tema - tetapi kelas perusahaan, dan model temanya bukan untuk ragam informal Bahasa Indonesia.",
  },
];

const rupiahJuta = (n) =>
  `Rp${(n / 1_000_000).toLocaleString("id-ID", { maximumFractionDigits: 2 })} jt`;

const HITUNGAN = [
  { nilai: "66 ulasan / 88 detik", ket: "terukur pada CPU dua inti, tanpa kartu grafis" },
  { nilai: "648 penjual per mesin", ket: "kalau tiap penjual menganalisis 300 ulasan sebulan" },
  { nilai: "≈ Rp1.330", ket: "ongkos melayani satu penjual, per bulan", hasil: true },
];

const Baris = ({ b }) => (
  <li className={`banding__baris ${b.kami ? "banding__baris--kami" : ""}`}>
    <div className="banding__nama">
      {b.nama}
      {b.kami && <span className="banding__tanda">produk ini</span>}
    </div>
    <div className="banding__harga">
      <b>{b.harga ?? rupiahJuta(b.rupiah)}</b>
      <small>{b.catatan}</small>
    </div>
    <p className="banding__batas">{b.batas}</p>
  </li>
);

export function Value() {
  return (
    <section className="value" id="nilai">
      <div className="section-head value__head">
        <h2>
          Yang gratis berhenti di rating. Yang bisa lebih, harganya kelas perusahaan.
        </h2>
        <p>
          Di Indonesia ada <b>4,40 juta unit usaha e-commerce</b>, mayoritas mikro, dan margin
          mereka sudah tergerus <b>15-20%</b> biaya platform sebelum satu rupiah masuk kantong.
          Ketika keluhan yang sama berulang tanpa terdeteksi, kerugiannya dua kali: penjualan
          yang hilang, dan biaya iklan yang dibakar untuk mendatangkan pembeli ke masalah yang
          belum diperbaiki.
        </p>
      </div>

      <div className="banding">
        <p className="banding__cap">
          Harga masuk termurah perkakas analisis ulasan, per bulan
          <span> · kurs Rp16.000/USD</span>
        </p>

        <ul className="banding__grup">
          {TERJANGKAU.map((b) => (
            <Baris key={b.nama} b={b} />
          ))}
        </ul>

        {/* Celahnya diberi barisnya sendiri, bukan sekadar jarak kosong: ruang kosong terbaca
            sebagai jeda tata letak, sedangkan yang harus terbaca di sini adalah ketiadaan. */}
        <div className="banding__celah">
          <b>Di antara keduanya, tidak ada apa pun</b>
          <p>
            Tidak ada perkakas yang membaca “bahannya oke sih cuma kekecilan bgt, sizechartnya
            ngaco” pada anggaran penjual mikro. Yang berbayar semuanya dirancang untuk ulasan
            berbahasa Inggris.
          </p>
        </div>

        <ul className="banding__grup">
          {MAHAL.map((b) => (
            <Baris key={b.nama} b={b} />
          ))}
        </ul>
      </div>

      {/* Pertanyaan yang selalu muncul setelah kata "gratis" adalah "lalu apa tangkapannya".
          Menjawabnya dengan hitungan terbuka lebih meyakinkan daripada menjanjikan selamanya. */}
      <div className="ongkos">
        <h3>Kenapa gratisnya bisa bertahan</h3>
        <p className="ongkos__lead">
          Bukan karena dibiayai investor. Seluruh model berjalan di mesin yang menjalankan
          aplikasi ini, bukan lewat API berbayar per ulasan, jadi ongkosnya tidak naik bersama
          jumlah pemakaian.
        </p>

        <ol className="ongkos__hitung">
          {HITUNGAN.map((h) => (
            <li key={h.nilai} className={h.hasil ? "ongkos__hasil" : ""}>
              <b>{h.nilai}</b>
              <span>{h.ket}</span>
            </li>
          ))}
        </ol>

        <p className="ongkos__nota">
          Angka 88 detik itu terukur. Sisanya turunan dengan asumsi yang ditulis terbuka -
          hitungan lengkapnya, termasuk enam hal yang belum divalidasi, ada di berkas
          BUSINESS_VALUE di repositori.
        </p>
      </div>
    </section>
  );
}
