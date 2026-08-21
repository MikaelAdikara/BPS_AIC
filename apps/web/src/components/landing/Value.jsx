/** Bagian nilai bisnis: besaran masalahnya, celah harga di pasar, dan kenapa gratisnya bertahan.
 *
 * Bentuknya sengaja BUKAN kisi kartu statistik. Empat angka besar berjajar dengan label kecil
 * di bawahnya adalah bentuk yang dipakai setiap halaman SaaS, dan ia menyampaikan angkanya
 * tanpa menyampaikan artinya - pembaca melihat empat fakta terpisah, bukan satu argumen.
 *
 * Argumennya di sini adalah sebuah JARAK: yang gratis berhenti di rating rata-rata, yang mampu
 * berharga jutaan per bulan, dan di antara keduanya tidak ada apa pun. Jarak paling jujur
 * digambar sebagai jarak. Karena itu bagian tengahnya satu penggaris harga utuh, bukan lima
 * kartu berdampingan, dan celahnya benar-benar terlihat sebagai ruang kosong yang lebar.
 *
 * Seluruh angka di berkas ini punya sumber di docs/BUSINESS_VALUE.md. Yang belum tervalidasi
 * ditandai di layar, bukan hanya di dokumen - halaman pemasaran adalah tempat paling menggoda
 * untuk membulatkan angka, dan produk ini tidak melakukannya.
 */

// Skala penggaris: logaritmik, karena rentangnya empat kali lipat sepuluh (Rp10 ribu sampai
// Rp32 juta) dan skala linear akan menumpuk seluruh ujung bawahnya jadi satu titik.
//
// Ujung kirinya dipatok Rp10.000, bukan Rp0. Log dari nol tidak terdefinisi, dan yang lebih
// penting: menaruh nol di ujung kiri membuat jarak Rp0→Rp39.000 memakan 61% penggaris - ujung
// termurahnya justru tampak paling lebar, kebalikan dari yang sebenarnya terjadi.
const MIN = 10_000;
const MAX = 32_000_000;
const RENTANG = Math.log10(MAX) - Math.log10(MIN);

const posisi = (rupiah) => ((Math.log10(rupiah) - Math.log10(MIN)) / RENTANG) * 100;

const DEKADE = [10_000, 100_000, 1_000_000, 10_000_000];

const rupiahSingkat = (n) =>
  n >= 1_000_000 ? `Rp${n / 1_000_000} jt` : `Rp${n / 1_000} rb`;

// Harga masuk termurah tiap produk, per bulan, kurs Rp16.000/USD. Sumbernya halaman harga
// publik masing-masing vendor, 2026 - lihat docs/BUSINESS_VALUE.md bagian 3.
const PESAING = [
  {
    nama: "Yotpo",
    rupiah: 1_264_000,
    usd: "USD 79/bln",
    batas: "Alat mengumpulkan ulasan, bukan menganalisis keluhan. Tanpa prioritisasi.",
  },
  {
    nama: "Birdeye",
    rupiah: 4_784_000,
    usd: "USD 299/bln per lokasi",
    batas: "Kontrak 12 bulan, onboarding terpisah USD 500-1.500. Untuk bisnis multi-cabang.",
  },
  {
    nama: "Thematic",
    rupiah: 32_000_000,
    usd: "USD 2.000/bln",
    batas: "Benar-benar mengekstrak tema, tetapi kelas perusahaan dan bukan untuk ragam informal.",
    // Birdeye dan Thematic hanya berjarak 23% penggaris, sementara labelnya selebar 172px -
    // terukur bertabrakan 72px pada 1280px. Yang satu diturunkan satu tingkat, dan garis
    // penghubung tipis menjaga hubungannya ke titik di penggaris tetap terbaca.
    tingkat: 1,
  },
];

// Batas kanan wilayah Ulasin. Rp39.000 adalah rencana tingkat berlangganan, dan statusnya
// sebagai hipotesis disebut di layar - bukan disembunyikan di catatan kaki.
const ATAP_ULASIN = 39_000;

export function Value() {
  const ujungUlasin = posisi(ATAP_ULASIN);
  const awalPesaing = posisi(PESAING[0].rupiah);

  return (
    <section className="value" id="nilai">
      <div className="value__intro">
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

      {/* Penggaris harga. Satu benda utuh, bukan lima kartu - karena yang harus terbaca adalah
          jarak antar-titiknya, dan jarak tidak bisa dibaca dari kartu yang berdampingan. */}
      <figure className="rail">
        <figcaption className="rail__cap">
          Harga masuk termurah perkakas analisis ulasan, per bulan.{" "}
          <span>Skala logaritmik · kurs Rp16.000/USD</span>
        </figcaption>

        <div className="rail__plot">
          <div className="rail__line" aria-hidden="true">
            {DEKADE.map((n) => (
              <span key={n} className="rail__tick" style={{ "--pos": `${posisi(n)}%` }}>
                <i />
                <em>{rupiahSingkat(n)}</em>
              </span>
            ))}

            <span
              className="rail__zone rail__zone--kami"
              style={{ "--pos": "0%", "--span": `${ujungUlasin}%` }}
            />
            <span
              className="rail__zone rail__zone--celah"
              style={{ "--pos": `${ujungUlasin}%`, "--span": `${awalPesaing - ujungUlasin}%` }}
            />
          </div>

          <p className="rail__label rail__label--kami" style={{ "--pos": "0%" }}>
            <b>Ulasin</b>
            <span>Gratis hari ini</span>
            <small>Rencana berlangganan Rp39.000 - belum divalidasi</small>
          </p>

          <p className="rail__label rail__label--celah" style={{ "--pos": `${ujungUlasin}%` }}>
            <b>Tidak ada apa pun di sini</b>
            <span>
              Tidak ada perkakas yang membaca “bahannya oke sih cuma kekecilan bgt, sizechartnya
              ngaco” pada anggaran penjual mikro.
            </span>
          </p>

          {PESAING.map((p) => (
            <p
              key={p.nama}
              className="rail__label rail__label--lawan"
              // Tingkatnya ditulis DUA kali dengan sengaja: sebagai custom property untuk
              // hitungan posisi, dan sebagai atribut data untuk pemilih CSS. Memilih lewat
              // `[style*="--tier: 1"]` sempat dipakai dan rapuh - cara React merangkai atribut
              // style tidak dijamin memuat spasi yang sama.
              data-tier={p.tingkat ?? 0}
              style={{ "--pos": `${posisi(p.rupiah)}%`, "--tier": p.tingkat ?? 0 }}
            >
              <b>{p.nama}</b>
              <span>{p.usd}</span>
              <small>{p.batas}</small>
            </p>
          ))}
        </div>
      </figure>

      {/* Pertanyaan yang selalu muncul setelah kata "gratis" adalah "lalu apa tangkapannya".
          Menjawabnya dengan hitungan terbuka lebih meyakinkan daripada menjanjikan selamanya. */}
      <div className="value__biaya">
        <h3>Kenapa gratisnya bisa bertahan</h3>
        <p>
          Bukan karena dibiayai investor. Seluruh model berjalan di mesin yang menjalankan
          aplikasi ini, bukan lewat API berbayar per ulasan, jadi ongkosnya tidak naik bersama
          jumlah pemakaian.
        </p>
        <p className="value__hitung">
          <span>66 ulasan selesai dalam 88 detik pada CPU dua inti</span>
          <i aria-hidden="true">↓</i>
          <span>satu mesin sanggup melayani ratusan penjual sebulan</span>
          <i aria-hidden="true">↓</i>
          <b>ongkos melayani satu penjual ≈ Rp1.330 per bulan</b>
        </p>
        <p className="value__nota">
          Angka 88 detik itu terukur. Sisanya turunan dengan asumsi yang ditulis terbuka -
          hitungan lengkapnya, termasuk apa yang belum divalidasi, ada di berkas BUSINESS_VALUE
          di repositori.
        </p>
      </div>
    </section>
  );
}
