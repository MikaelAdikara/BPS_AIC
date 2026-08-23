/** Bagian atas halaman pemasaran - porting langsung dari halaman referensi Google Stitch.
 *
 * Koordinat absolut kartu mengambang sengaja dipertahankan persis: tata letak yang sedikit
 * berserak dan miring 2-5 derajat itulah yang membuat halaman terasa hidup.
 */

import { useEffect, useRef } from "react";

/** Kartu ulasan mengambang. Isinya contoh ulasan berbahasa sehari-hari - persis jenis
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
  // Tilt 3D yang mengikuti kursor. Hanya di perangkat berkursor halus dan bila pengguna tidak
  // meminta gerak dikurangi; selain itu variabel --tx/--ty tetap 0 dan semuanya statis.
  const stage = useRef(null);
  useEffect(() => {
    const el = stage.current;
    if (!el || typeof window.matchMedia !== "function") return undefined;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return undefined;
    if (!window.matchMedia("(pointer: fine)").matches) return undefined;
    let raf = 0;
    const onMove = (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        el.style.setProperty("--tx", x.toFixed(3));
        el.style.setProperty("--ty", y.toFixed(3));
      });
    };
    const onLeave = () => {
      cancelAnimationFrame(raf);
      el.style.setProperty("--tx", "0");
      el.style.setProperty("--ty", "0");
    };
    el.addEventListener("pointermove", onMove);
    el.addEventListener("pointerleave", onLeave);
    return () => {
      cancelAnimationFrame(raf);
      el.removeEventListener("pointermove", onMove);
      el.removeEventListener("pointerleave", onLeave);
    };
  }, []);

  return (
    <section className="hero-section">
      <div className="hero">
        <div className="eyebrow">
          <span className="pulse" />
          Tanpa akun · berjalan lokal · data tidak disimpan
        </div>
        <h1>
          <span className="line">
            Sulap Ulasan jadi <span className="highlight">Keputusan</span>
          </span>
        </h1>
        <p className="sub">
          Ratusan ulasan pelanggan menjadi <b>tiga hal yang harus dikerjakan minggu ini</b> - setiap
          angka membawa kutipan aslinya, dan bisa Anda hitung ulang sendiri.
        </p>
        <div className="cta-row">
          <button className="btn btn--primary btn--lg" onClick={onStart}>
            Mulai Analisis ›
          </button>
          <a className="btn btn--outline btn--lg" href="#bukti">
            Lihat Cara Menghitungnya
          </a>
        </div>
      </div>

      <div className="stage" ref={stage}>
        <span className="spill spill--blue">✦ Insight baru</span>
        <span className="spill spill--dark">Prioritas #1 · Ukuran</span>
        <span className="spill spill--glass">Diperbarui tiap hari</span>

        <PhoneMockup />

        <div className="fcards">{REVIEWS.map(FloatingReview)}</div>
      </div>
    </section>
  );
}
