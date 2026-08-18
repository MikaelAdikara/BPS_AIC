/** Lapisan pemasaran InsightUlasan — porting langsung dari halaman referensi Google Stitch.
 *
 * Struktur dan posisi elemen (termasuk koordinat absolut kartu mengambang) sengaja sama
 * persis dengan referensi. Yang diubah hanya ISI teks yang tidak benar untuk produk ini —
 * lihat komentar pada pita marketplace.
 */

const Logo = ({ size = 17 }) => (
  <svg width={size} height={size} viewBox="0 0 34 34" fill="none" aria-hidden="true">
    <path
      d="M4 6C4 4.34 5.34 3 7 3H27C28.66 3 30 4.34 30 6V20C30 21.66 28.66 23 27 23H16L10 28V23H7C5.34 23 4 21.66 4 20V6Z"
      fill="#fff"
    />
    <path
      d="M11 13L15 17L23 9"
      stroke="#1E4FCB"
      strokeWidth="2.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const Brand = ({ onClick }) => (
  <button className="brand" onClick={onClick}>
    <span className="brand__mark">
      <Logo />
    </span>
    <span className="brand__name">
      Insight<span>Ulasan</span>
    </span>
  </button>
);

export function SiteNav({ onStart, themeToggle }) {
  return (
    <nav className="nav">
      <Brand onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} />

      <div className="nav__links">
        <a href="#cara-kerja">Cara kerja</a>
        <a href="#fitur">Fitur</a>
        <a href="#mulai">Mulai analisis</a>
      </div>

      <div className="nav__right">
        {themeToggle}
        <button className="btn btn--primary" onClick={onStart}>
          Mulai Sekarang ›
        </button>
      </div>
    </nav>
  );
}

/** Kartu ulasan mengambang. Isinya contoh ulasan berbahasa sehari-hari — persis jenis
 *  kalimat yang harus dibaca sistem, lengkap dengan singkatan dan ejaan bebas. */
const REVIEWS = [
  {
    pos: "tl-1",
    ava: "RW",
    color: "#C97F6B",
    who: "Rina W.",
    meta: "Ulasan produk · 2 hari lalu",
    text: "Ukurannya beda jauh sama yang di foto, kekecilan banget. Padahal udah cek size chart dulu.",
    dot: "var(--red-base)",
    tag: "Ukuran tidak sesuai",
  },
  {
    pos: "tl-2",
    ava: "AS",
    color: "#7FA88B",
    who: "Ayu S.",
    meta: "Ulasan produk · 5 hari lalu",
    text: "Chat seller lama banget dibalesnya, udah 2 hari baru dibales. Padahal cuma nanya stok.",
    dot: "#4E9BE0",
    tag: "Respons lambat",
  },
  {
    pos: "tl-3",
    ava: "BT",
    color: "#C9A24A",
    who: "Bagus T.",
    meta: "Ulasan produk · 1 minggu lalu",
    text: "Bahannya bagus sih, cuma pengiriman lama 5 hari baru sampai padahal sekota aja.",
    dot: "var(--amber-base)",
    tag: "Pengiriman lambat",
  },
  {
    pos: "tr-1",
    ava: "DP",
    color: "#6B87C9",
    who: "Dimas P.",
    meta: "Ulasan produk · 4 hari lalu",
    text: "Paket datang dus penyok parah, isinya untung masih aman. Tolong packingnya dirapihin.",
    dot: "var(--amber-base)",
    tag: "Kemasan rusak",
  },
  {
    pos: "tr-2",
    ava: "SM",
    color: "#B08AC1",
    who: "Sekar M.",
    meta: "Ulasan produk · 1 minggu lalu",
    text: "Warnanya nggak sesuai gambar, aslinya jauh lebih pudar. Agak kecewa tapi bahannya oke.",
    dot: "#A98AC1",
    tag: "Deskripsi tidak akurat",
  },
  {
    pos: "tr-3",
    ava: "FN",
    color: "#5C9E85",
    who: "Fajar N.",
    meta: "Ulasan produk · 2 minggu lalu",
    text: "Barang ori, packing bubble wrap tebel, admin fast respon juga. Recommended seller!",
    dot: "var(--green-base)",
    tag: "Sentimen positif",
  },
];

const FloatingReview = (r) => (
  <article className={`fcard ${r.pos}`} key={r.who}>
    <div className="fc-head">
      <span className="fc-ava" style={{ background: r.color }}>
        {r.ava}
      </span>
      <div>
        <div className="fc-who">{r.who}</div>
        <div className="fc-meta">{r.meta}</div>
      </div>
    </div>
    <p>"{r.text}"</p>
    <span className="chip-tag">
      <i className="dot" style={{ background: r.dot }} />
      {r.tag}
    </span>
  </article>
);

/** Mockup ponsel. Strukturnya sengaja sama dengan layar hasil sungguhan: masalah teratas
 *  berperingkat, satu rekomendasi utama, lalu kutipan yang mendasarinya. */
function PhoneMockup() {
  return (
    <div className="phone" aria-hidden="true">
      <div className="screen">
        <div className="island" />
        <div className="statusbar">
          <span>9:41</span>
          <span>●●● ▾</span>
        </div>

        <div className="app">
          <div className="app-top">
            <div className="app-hello">
              Halo, Owner UMKM!<span>Ringkasan ulasan minggu ini</span>
            </div>
            <div className="app-ava">OU</div>
          </div>

          <div className="panel">
            <div className="panel-title">
              Masalah teratas <em>7 hari</em>
            </div>
            {[
              ["Ukuran tidak sesuai", "tinggi", "f1"],
              ["Kemasan rusak", "sedang", "f2"],
              ["Respons lambat", "rendah", "f3"],
            ].map(([name, level, fill]) => (
              <div className="bar-row" key={name}>
                <div className="bar-label">
                  <b>{name}</b>
                  <span>{level}</span>
                </div>
                <div className="track">
                  <div className={`fill ${fill}`} />
                </div>
              </div>
            ))}
          </div>

          <div className="rec">
            <span className="rec-tag">Rekomendasi utama</span>
            <p>Perbarui size chart &amp; tambahkan foto ukuran asli di halaman produk.</p>
            <small>Didukung kutipan ulasan pelanggan ↗</small>
          </div>

          <div className="mini">
            <span className="md" style={{ background: "var(--red-base)" }} />
            <p>"Ukurannya beda jauh sama yang di foto…"</p>
          </div>
          <div className="mini">
            <span className="md" style={{ background: "var(--amber-base)" }} />
            <p>"Paket datang dus penyok parah…"</p>
          </div>
        </div>

        <div className="tabbar">
          <i className="on" />
          <i />
          <i />
          <i />
        </div>
      </div>
    </div>
  );
}

export function Hero({ onStart }) {
  return (
    <section className="hero-section">
      <div className="hero">
        <div className="eyebrow">
          <span className="pulse" />
          Asisten ulasan cerdas untuk pelaku usaha
        </div>
        <h1>
          <span className="line">
            Sulap Ulasan jadi <span className="highlight">Keputusan</span>
          </span>
        </h1>
        <p className="sub">
          Ubah kumpulan ulasan dari pelanggan Anda menjadi <b>rekomendasi bisnis konkret</b> kurang
          dari 1 menit.
        </p>
        <div className="cta-row">
          <button className="btn btn--primary btn--lg" onClick={onStart}>
            Mulai Sekarang ›
          </button>
          <a className="btn btn--outline btn--lg" href="#cara-kerja">
            Lihat Cara Kerjanya
          </a>
        </div>
      </div>

      <div className="stage">
        <span className="spill spill--blue">✦ Insight baru</span>
        <span className="spill spill--dark">Prioritas #1 · Ukuran</span>
        <span className="spill spill--glass">Diperbarui tiap hari</span>

        <PhoneMockup />

        <div className="fcards">{REVIEWS.map(FloatingReview)}</div>
      </div>
    </section>
  );
}

/** Pita marketplace. Teks referensi berbunyi "Terhubung dengan ulasan dari semua marketplace
 *  besar" — itu menjanjikan integrasi langsung yang TIDAK dimiliki versi ini, jadi kalimatnya
 *  diganti menjadi jalur yang benar-benar didukung: berkas ekspor. */
export function MarketplaceBand() {
  return (
    <div className="band">
      <div className="band-inner">
        <span className="lbl">Bekerja dengan berkas ekspor ulasan dari semua marketplace besar</span>
        <div className="band-logos">
          <b>Tokopedia</b>
          <b>Shopee</b>
          <b>TikTok Shop</b>
          <b>Lazada</b>
          <b>Bukalapak</b>
          <b>Google Reviews</b>
        </div>
      </div>
    </div>
  );
}

export function Features() {
  return (
    <section className="features" id="fitur">
      <div className="tabs" role="tablist" aria-label="Alur kerja">
        <button className="tab tab--active" role="tab" aria-selected="true">
          Baca
        </button>
        <button className="tab" role="tab" aria-selected="false">
          Prioritaskan
        </button>
        <button className="tab" role="tab" aria-selected="false">
          Tindak Lanjuti
        </button>
      </div>

      <h2>
        Setiap ulasan, <span className="soft">jadi langkah nyata</span>
      </h2>
      <p>
        Teks dan rating dari semua kanal terkumpul di satu tempat, lalu dikelompokkan per
        masalah, diurutkan berdasarkan dampaknya, dan dilengkapi rekomendasi yang harus dibenahi
        lebih dulu.
      </p>

      <div className="fgrid">
        <article className="fitem">
          <div className="fasset" aria-hidden="true">
            <div className="fa1-back">
              <div className="ln" />
              <div className="ln" />
              <div className="ln" />
            </div>
            <div className="fa1-front">
              <div className="fa1-photo" />
              <div className="fa1-text">
                <div className="ln" />
                <div className="ln" />
                <span className="mini-tag">
                  <i />
                  Ukuran
                </span>
              </div>
            </div>
          </div>
          <h3>Mengerti Bahasa Pelanggan Sehari-hari</h3>
          <p>
            Bahasa gaul, singkatan, sampai ejaan bebas, semuanya tetap terbaca. Tidak ada ulasan
            yang terlewat hanya karena sulit dipahami.
          </p>
        </article>

        <article className="fitem">
          <div className="fasset" aria-hidden="true">
            <div className="fa2-panel">
              {[
                ["1", "Ukuran tidak sesuai", "82%"],
                ["2", "Kemasan rusak", "56%"],
                ["3", "Respons lambat", "33%"],
              ].map(([n, label, w]) => (
                <div className="fa2-row" key={n}>
                  <span className="fa2-badge">{n}</span>
                  <div className="fa2-body">
                    <div className="fa2-label">{label}</div>
                    <div className="fa2-track">
                      <div className="fa2-fill" style={{ width: w }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <h3>Mengurutkan yang Paling Penting</h3>
          <p>
            Masalah diurutkan berdasarkan seberapa sering muncul, seberapa besar dampaknya, dan
            seberapa baru terjadinya, jadi urutan kerjanya bukan tebak-tebakan.
          </p>
        </article>

        <article className="fitem">
          <div className="fasset" aria-hidden="true">
            <div className="fa3-rec">
              <span className="fa3-check">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M5 12.5l4.5 4.5L19 7.5"
                    stroke="#1E4FCB"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              Perbarui size chart &amp; foto ukuran asli
            </div>
            <div className="fa3-connector" />
            <div className="fa3-quote">
              <span className="qm">”</span>
              <p>"Ukurannya beda jauh sama yang di foto, kekecilan banget…"</p>
              <span className="mini-tag" style={{ marginTop: 7 }}>
                <i />
                Ukuran tidak sesuai
              </span>
            </div>
          </div>
          <h3>Menyertakan Buktinya</h3>
          <p>
            Setiap rekomendasi datang lengkap dengan kutipan asli pelanggan di baliknya, jadi Anda
            bisa ambil tindakan dengan yakin atau menolaknya dengan alasan yang jelas.
          </p>
        </article>
      </div>
    </section>
  );
}

export function HowItWorks() {
  const STEPS = [
    [
      "01",
      "Masukkan ulasan Anda",
      "Tempel langsung satu ulasan per baris, atau unggah berkas CSV/JSON hasil ekspor marketplace. Kolomnya Anda cocokkan sendiri.",
    ],
    [
      "02",
      "Sistem membacanya",
      "Setiap ulasan dipecah per aspek (ukuran, kemasan, pengiriman, pelayanan), lalu dinilai sentimen dan tingkat keluhannya.",
    ],
    [
      "03",
      "Anda dapat daftar prioritas",
      "Hal yang paling perlu dikerjakan lebih dulu, masing-masing dengan kutipan asli pelanggan sebagai buktinya.",
    ],
  ];

  return (
    <section className="features" id="cara-kerja">
      <div className="section-head">
        <h2>
          Tiga langkah, <span className="soft">satu sore</span>
        </h2>
        <p>
          Tidak ada pemasangan dan tidak ada akun yang perlu dihubungkan. Data Anda hanya diproses
          selama sesi ini dan tidak disimpan permanen.
        </p>
      </div>
      <div className="fgrid">
        {STEPS.map(([n, title, body]) => (
          <article className="fitem" key={n}>
            <span className="step-no">Langkah {n}</span>
            <h3>{title}</h3>
            <p>{body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export function FootCta({ onStart }) {
  return (
    <div className="foot">
      <div className="foot-card">
        <div className="glow" />
        <h2>
          Berhenti Menggulir Ulasan.{" "}
          <span className="accent">Mulai Perbaiki Bisnis Anda.</span>
        </h2>
        <p>
          Masukkan ulasan toko Anda, dan lihat daftar prioritas pertama dari apa yang pelanggan Anda
          minta untuk diperbaiki.
        </p>
        <div className="cta-row">
          <button className="btn btn--primary btn--lg" onClick={onStart}>
            Mulai Sekarang ›
          </button>
          <a className="btn btn--ondark btn--lg" href="#cara-kerja">
            Lihat Cara Kerjanya
          </a>
        </div>
      </div>
      <div className="foot-note">
        © 2026 InsightUlasan · Dibuat untuk pelaku usaha yang peduli setiap ulasan
      </div>
    </div>
  );
}
