/** "Kenapa bukan ...?" - tiga pertanyaan yang pasti ada di kepala pembaca, dijawab lebih dulu.
 *
 * Ditulis sebagai perbandingan jujur, bukan serangan: tiap alternatif punya kelebihan yang
 * disebut apa adanya, lalu satu hal yang tidak bisa dilakukannya - dan itulah tempat Ulasin
 * berdiri. Kalau perbandingannya tidak adil, pembaca yang sudah memakai alternatif itu berhenti
 * percaya pada seluruh halaman.
 */

const BANDING = [
  {
    lawan: "ChatGPT / LLM API",
    kelebihan: "Cepat dicoba, pintar membaca bahasa apa pun, bisa diajak ngobrol.",
    tapi: [
      "Angkanya dikarang ulang tiap kali ditanya - \"berapa persen keluhan ukuran?\" bisa berbeda antar jawaban, dan tidak ada yang bisa dihitung ulang.",
      "Ulasan pelanggan Anda dikirim ke server pihak ketiga; biayanya naik bersama jumlah ulasan.",
      "Tidak tahu data kategori pembanding, tidak punya jejak perhitungan, tidak mengingat aturan bisnis Anda.",
    ],
    ulasin: "Angka dihitung deterministik di mesin lokal, tanpa API, dan setiap angka membawa kutipan + rumusnya.",
  },
  {
    lawan: "Dashboard Shopee / Tokopedia",
    kelebihan: "Gratis, bawaan, datanya lengkap dan langsung dari sumbernya.",
    tapi: [
      "Berhenti di rating rata-rata dan daftar ulasan - ia tidak mengelompokkan keluhan per aspek, tidak mengurutkan mana yang mendesak, dan tidak memberi langkah.",
      "Tiap kanal hanya melihat kanalnya sendiri; Shopee tidak tahu apa kata pembeli Tokopedia Anda.",
      "Tidak ada pembanding: 8% keluhan pengiriman itu bagus atau buruk? Dashboard tidak menjawab.",
    ],
    ulasin: "Semua kanal dalam satu layar, keluhan per aspek, prioritas terurut, dan pembanding kategori dari 9.000+ ulasan publik.",
  },
  {
    lawan: "Baca manual / Excel",
    kelebihan: "Paling akurat untuk yang sempat membacanya, dan konteksnya utuh.",
    tapi: [
      "Tidak proporsional di atas 50-100 ulasan per bulan - dan waktu pemilik toko adalah hal yang paling langka.",
      "Keluhan yang berulang pelan-pelan (\"agak kekecilan\" di 1 dari 10 ulasan) hampir mustahil terlihat tanpa dihitung.",
      "Tidak ada riwayat: bulan lalu lebih buruk atau lebih baik? Tidak ada yang mencatat.",
    ],
    ulasin: "Membaca 100% ulasan dalam hitungan detik, mengelompokkan, menghitung, dan menyimpan arsip yang bisa dibandingkan bulan depan.",
  },
];

export function WhyNot() {
  return (
    <section className="banding-sec" id="kenapa-bukan" aria-labelledby="banding-judul">
      <div className="section-head">
        <h2 id="banding-judul">
          Kenapa bukan <span className="soft">yang sudah ada?</span>
        </h2>
        <p>
          Tiga alternatif yang wajar, masing-masing dengan kelebihannya yang nyata - dan satu hal
          yang tidak bisa dilakukannya.
        </p>
      </div>
      <div className="banding-grid">
        {BANDING.map((b) => (
          <article className="banding-kartu" key={b.lawan}>
            <h3>{b.lawan}</h3>
            <p className="banding-kartu__plus">
              <b>Kelebihannya:</b> {b.kelebihan}
            </p>
            <ul className="banding-kartu__minus">
              {b.tapi.map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
            <p className="banding-kartu__ulasin">
              <b>Ulasin:</b> {b.ulasin}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
