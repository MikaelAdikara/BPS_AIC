/** Bagian "Kenapa sekarang": fakta dan berita bisnis yang membuat masalah ini mendesak.
 *
 * Polanya meminjam tata letak cerita pelanggan WIZ.AI - satu kartu utama lebar, lalu tiga kartu
 * ringkas - tetapi isinya fakta bersumber, bukan testimoni. Versi pertama bagian ini terlalu
 * banyak teks; versi ini memindahkan beban ceritanya ke VISUAL: tiap kartu membawa satu grafik
 * yang digambar dari angka sumbernya sendiri (bukan ilustrasi dekoratif), plus logo marketplace
 * asli di kartu biaya. Teksnya tinggal judul satu kalimat dan sumber.
 *
 * Tidak ada satu angka pun yang dikarang di sini. Sumber lengkap beserta tautannya ada di
 * docs/BUSINESS_VALUE.md dan README bagian 3. Aturan keras yang tetap berlaku: kartu TIDAK
 * menyimpulkan "karena itu pakai Ulasin" - faktanya dibiarkan bicara.
 */

import { MarketLogo } from "./MarketLogos.jsx";

/* Kartu utama - ke mana harga jual pergi setelah struktur biaya 2026.
 * Lebar segmen adalah ILUSTRASI proporsi di tengah rentang sumber (15-20% total); labelnya
 * menyebut rentang aslinya, dan keterangan di bawah grafik mengatakan itu terus terang. */
const BIAYA = [
  { id: "komisi", label: "Komisi", rentang: "2,5-10%", lebar: 8 },
  { id: "ongkir", label: "Gratis ongkir", rentang: "4-4,5%", lebar: 4.5 },
  { id: "promosi", label: "Promosi", rentang: "1-2%", lebar: 1.5 },
  { id: "iklan", label: "Iklan", rentang: "3-5%", lebar: 4 },
];
const BIAYA_TOTAL = BIAYA.reduce((a, b) => a + b.lebar, 0); // 18 dari 100

const SKALA = [
  { n: "65,5 jt", ket: "unit UMKM di Indonesia · 61,9% PDB", sumber: "Kemenkop UKM 2025" },
  { n: "25 jt", ket: "UMKM sudah onboarding di platform digital", sumber: "Kemenkop UKM 2025" },
  { n: "≈ US$100 M", ket: "GMV ekonomi digital Indonesia 2025, +14%", sumber: "e-Conomy SEA 2025" },
  { n: "800 rb", ket: "penjual video commerce, +75% setahun", sumber: "e-Conomy SEA 2025" },
];

/* ---------- Visual kartu kecil: digambar dari angkanya, bukan gambar tempel ---------- */

/** BPKN: dua batang, 926 → 1.733. Tinggi relatif terhadap 1.733. */
function GrafikPengaduan() {
  return (
    <div className="uviz uviz--batang" aria-hidden="true">
      <div className="uviz__kolom">
        <b style={{ "--h": `${(926 / 1733) * 100}%` }}>
          <span>926</span>
        </b>
        <small>2023</small>
      </div>
      <div className="uviz__kolom uviz__kolom--naik">
        <b style={{ "--h": "100%" }}>
          <span>1.733</span>
        </b>
        <small>2024</small>
      </div>
      <div className="uviz__panah">+200%</div>
    </div>
  );
}

/** Perilaku pembeli: 10 orang, 8 terisi. */
function GrafikPembeli() {
  return (
    <div className="uviz uviz--orang" aria-hidden="true">
      {Array.from({ length: 10 }, (_, i) => (
        <svg
          key={i}
          viewBox="0 0 24 32"
          className={i < 8 ? "is-isi" : ""}
          style={{ "--i": i }}
        >
          <circle cx="12" cy="6" r="5" />
          <path d="M4 31v-9a8 8 0 0 1 16 0v9z" />
        </svg>
      ))}
      <span className="uviz__ket">8 dari 10 membaca ulasan dulu</span>
    </div>
  );
}

/** Efek membalas: volume ulasan 100 → 112, dan bintang +0,12. */
function GrafikMembalas() {
  return (
    <div className="uviz uviz--balas" aria-hidden="true">
      <div className="uviz__baris">
        <span>Tanpa balasan</span>
        <i style={{ "--w": "72%" }} />
        <b>100</b>
      </div>
      <div className="uviz__baris uviz__baris--naik">
        <span>Rutin membalas</span>
        <i style={{ "--w": "80.6%" }} />
        <b>112</b>
      </div>
      <div className="uviz__bintang">
        {Array.from({ length: 5 }, (_, i) => (
          <svg key={i} viewBox="0 0 24 24" style={{ "--i": i }}>
            <path d="M12 2.5l2.9 6.1 6.7.8-4.9 4.6 1.3 6.6L12 17.3 6 20.6l1.3-6.6-4.9-4.6 6.7-.8z" />
          </svg>
        ))}
        <span>+0,12 ★ rata-rata</span>
      </div>
    </div>
  );
}

const KARTU = [
  {
    kategori: "Perlindungan konsumen",
    angka: "+200%",
    angkaKet: "pengaduan ke BPKN, 2023→2024",
    judul: "E-commerce kini sektor pengaduan teratas setelah jasa keuangan",
    sumber: "BPKN, statistik pengaduan 2024-2025",
    Visual: GrafikPengaduan,
  },
  {
    kategori: "Perilaku pembeli",
    angka: "80%+",
    angkaKet: "membaca ulasan sebelum membeli",
    judul: "Dan 60% menyebut ulasan jujur sesama pengguna sebagai konten paling meyakinkan",
    sumber: "Survei perilaku konsumen Indonesia, 2025",
    Visual: GrafikPembeli,
  },
  {
    kategori: "Efek membalas",
    angka: "+12%",
    angkaKet: "ulasan masuk setelah rutin membalas",
    judul: "Penjual yang membalas ulasan menerima lebih banyak ulasan, dan ratingnya naik 0,12 bintang",
    sumber: "Proserpio & Zervas, Marketing Science, 2017",
    Visual: GrafikMembalas,
  },
];

export function Urgency() {
  return (
    <section className="urgensi" id="kenapa-sekarang" aria-labelledby="urgensi-judul">
      <div className="section-head urgensi__head">
        <h2 id="urgensi-judul">
          Kenapa sekarang, <span className="soft">bukan nanti</span>
        </h2>
        <p>
          Empat fakta bersumber - dan semuanya menunjuk ke tumpukan teks yang sama: ulasan yang
          belum pernah dibaca sistematis oleh penjual mikro mana pun.
        </p>
      </div>

      <article className="urgensi__utama">
        <div className="urgensi__utama-visual">
          <div className="rupiah" aria-hidden="true">
            <div className="rupiah__kepala">
              <span>Dari harga jual</span>
              <b>Rp100.000</b>
            </div>
            <div className="rupiah__kurung">
              <span style={{ "--w": `${BIAYA_TOTAL}%` }} />
              <b style={{ "--w": `${BIAYA_TOTAL}%` }}>biaya platform ≈ 15-20%</b>
            </div>
            <div className="rupiah__bar">
              {BIAYA.map((b, i) => (
                <i
                  key={b.id}
                  className={`rupiah__seg rupiah__seg--${b.id}`}
                  style={{ "--w": `${b.lebar}%`, "--i": i }}
                  title={`${b.label} ${b.rentang}`}
                />
              ))}
              <i
                className="rupiah__seg rupiah__seg--sisa"
                style={{ "--w": `${100 - BIAYA_TOTAL}%`, "--i": BIAYA.length }}
              >
                <span>untuk modal, ongkos, dan laba Anda</span>
              </i>
            </div>
            <ul className="rupiah__legenda">
              {BIAYA.map((b) => (
                <li key={b.id} className={`rupiah__leg rupiah__leg--${b.id}`}>
                  <i />
                  <span>{b.label}</span>
                  <b>{b.rentang}</b>
                </li>
              ))}
            </ul>
            <div className="rupiah__total">
              <span>Biaya platform</span>
              <b>15-20%</b>
              <span>dari harga jual</span>
            </div>
          </div>
          <div className="urgensi__logos">
            <span>Struktur biaya baru 2026 di</span>
            <MarketLogo id="shopee" height={16} />
            <MarketLogo id="tokopedia" height={15} />
            <MarketLogo id="tiktokshop" height={16} />
            <MarketLogo id="lazada" height={15} />
          </div>
        </div>
        <div className="urgensi__utama-teks">
          <span className="urgensi__chip">Biaya platform 2026</span>
          <h3>
            Sejak 1 Januari 2026, 15-20% harga jual habis untuk biaya platform - sebelum satu
            keluhan pun dibenahi.
          </h3>
          <p>
            Margin yang tergerus lebih dulu membuat setiap pembeli yang kecewa rugi dua kali: biaya
            iklannya terbakar, dan ulasannya menahan pembeli berikutnya.
          </p>
          <div className="urgensi__meta">
            <span>Rincian tarif Shopee, Tokopedia, TikTok Shop 2026 · laporan industri</span>
          </div>
        </div>
      </article>

      <div className="urgensi__grid">
        {KARTU.map((k) => (
          <article className="urgensi__kartu" key={k.kategori}>
            <div className="urgensi__kartu-visual">
              <k.Visual />
            </div>
            <span className="urgensi__chip">{k.kategori}</span>
            <div className="urgensi__angka">
              <b>{k.angka}</b>
              <span>{k.angkaKet}</span>
            </div>
            <h3>{k.judul}</h3>
            <div className="urgensi__meta">
              <span>{k.sumber}</span>
            </div>
          </article>
        ))}
      </div>

      <ul className="urgensi__skala" aria-label="Skala pasar">
        {SKALA.map((s) => (
          <li key={s.n}>
            <b>{s.n}</b>
            <span>{s.ket}</span>
            <small>{s.sumber}</small>
          </li>
        ))}
      </ul>

      <p className="urgensi__nota">
        Semua angka di bagian ini bersumber dari pihak lain. Yang kami ukur sendiri ada di bagian
        Bukti, lengkap dengan batasnya.
      </p>
    </section>
  );
}
