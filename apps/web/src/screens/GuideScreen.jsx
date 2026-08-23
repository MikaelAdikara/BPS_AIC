/** Halaman Panduan (#/panduan) - "dari mana saya mengambil ulasan, dan bagaimana memasukkannya".
 *
 * Ditujukan untuk pemilik toko yang belum pernah memakai alat seperti ini. Tiga keputusan
 * rancangan yang membentuk halaman ini:
 *
 *  1. Pertanyaannya dibalik. Bukan "fitur apa yang kami punya", melainkan "di mana ulasan
 *     ANDA berada" - pengguna memilih tempatnya (Shopee, Tokopedia, Google Maps, WhatsApp...)
 *     dan halaman menunjukkan letak menunya dengan gambar ponsel, bukan paragraf.
 *  2. Satu jalur ditonjolkan di semua platform: buka halaman ulasan, tangkap layar. Jalur itu
 *     tidak butuh berkas, tidak butuh laptop, dan tidak bergantung pada fitur penjual yang
 *     letaknya berpindah antar-versi aplikasi. Jalur lain (tempel teks, berkas) tetap ada.
 *  3. Setiap jalur berakhir di tombol yang membuka layar kerja LANGSUNG pada tab yang tepat
 *     (#/analisis?masukan=shot|paste|file), supaya tidak ada langkah "sekarang cari tabnya".
 *
 * Isinya di src/content/panduan.js. Gambar ponselnya mock generik (CSS), bukan tangkapan layar
 * aplikasi pihak ketiga - nama menu bisa bergeser antar-versi, dan mock yang jelas-jelas mock
 * tidak berbohong soal itu. Logo marketplace-nya asli (MarketLogos.jsx).
 */

import { useEffect, useMemo, useState } from "react";
import { Brand, ThemeToggle } from "../components/Brand.jsx";
import { MarketLogo } from "../components/landing/MarketLogos.jsx";
import { CARA, JALUR, PLATFORM, SEBELUM_MULAI, TANYA } from "../content/panduan.js";
import { goTo } from "../lib/hooks.js";

/** Mengubah **teks** menjadi <b>teks</b>. Cukup untuk kebutuhan di sini; bukan Markdown. */
function Tebal({ teks }) {
  const bagian = String(teks).split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {bagian.map((b, i) =>
        b.startsWith("**") && b.endsWith("**") ? <b key={i}>{b.slice(2, -2)}</b> : <span key={i}>{b}</span>
      )}
    </>
  );
}

const IkonCentang = () => (
  <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">
    <path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

/** Mock ponsel: layar aplikasi dengan satu baris menu yang harus diketuk. Ia sengaja generik -
 *  bingkai, kepala berwarna aksen platform, daftar menu - supaya jelas ini petunjuk letak,
 *  bukan tangkapan layar aplikasi aslinya. Jari yang mengetuk dan kilat "tangkapan layar"
 *  dianimasikan berulang; keduanya dimatikan pada prefers-reduced-motion lewat CSS. */
function PhoneMock({ p }) {
  const { layar } = p;
  const chat = layar.mode === "chat";
  return (
    <div className="gphone" style={{ "--aksen": p.aksen }} aria-hidden="true">
      <div className="gphone__notch" />
      <div className="gphone__kepala">
        {p.logo ? (
          <span className="gphone__logo">
            <MarketLogo id={p.logo} height={14} hidden />
          </span>
        ) : (
          <span className="gphone__logo gphone__logo--teks">{p.nama.split(" ")[0]}</span>
        )}
        <span className="gphone__judul">{layar.judul}</span>
      </div>
      {chat ? (
        <div className="gphone__chat">
          {layar.menu.map((m, i) => (
            <div key={m} className={`gphone__bubble ${i === 4 ? "gphone__bubble--kanan" : ""}`} style={{ "--i": i }}>
              {m}
            </div>
          ))}
          <div className="gphone__pilih">
            <span>4 pesan dipilih</span>
            <b>Salin</b>
          </div>
        </div>
      ) : (
        <ul className="gphone__menu">
          {layar.menu.map((m, i) => (
            <li key={m} className={i === layar.ketuk ? "is-ketuk" : ""}>
              <span>{m}</span>
              <i />
              {i === layar.ketuk && (
                <span className="gphone__jari">
                  <svg viewBox="0 0 24 24" width="26" height="26">
                    <path
                      d="M9 11V4.5a1.5 1.5 0 0 1 3 0V11m0-2.5a1.5 1.5 0 0 1 3 0V11m0-1.5a1.5 1.5 0 0 1 3 0V11m0-.5a1.5 1.5 0 0 1 3 0v5a6 6 0 0 1-6 6h-1.5a6 6 0 0 1-4.8-2.4L5.2 15.6a1.6 1.6 0 0 1 2.4-2.1L9 15V11"
                      fill="#fff"
                      stroke="#14150f"
                      strokeWidth="1.6"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
      {!chat && (
        <div className="gphone__hasil">
          <span className="gphone__hasil-judul">{layar.hasil}</span>
          {[0, 1, 2].map((i) => (
            <div className="gphone__ulasan" key={i} style={{ "--i": i }}>
              <i />
              <div>
                <span style={{ width: `${78 - i * 14}%` }} />
                <span style={{ width: `${56 + i * 9}%` }} />
              </div>
            </div>
          ))}
          <div className="gphone__kilat" />
        </div>
      )}
      <div className="gphone__bar" />
    </div>
  );
}

function PilihPlatform({ aktif, onPilih }) {
  // Di layar sempit pemilihnya bergulir menyamping; chip yang aktif digeser ke tengah supaya
  // pengguna yang datang lewat tautan ?tempat=... melihat pilihannya, bukan chip pertama.
  // Hanya geseran MENYAMPING di dalam relnya - scrollIntoView akan ikut menggulir halaman
  // secara vertikal saat halaman baru dibuka, dan itu melompati kepala halaman.
  useEffect(() => {
    const el = document.getElementById(`gtab-${aktif}`);
    const rel = el?.parentElement;
    if (!el || !rel || rel.scrollWidth <= rel.clientWidth) return;
    rel.scrollTo({ left: el.offsetLeft - (rel.clientWidth - el.offsetWidth) / 2, behavior: "smooth" });
  }, [aktif]);
  return (
    <div className="gpilih" role="tablist" aria-label="Tempat ulasan Anda">
      {PLATFORM.map((p) => (
        <button
          key={p.id}
          role="tab"
          id={`gtab-${p.id}`}
          aria-selected={aktif === p.id}
          aria-controls="gpanel"
          className={`gpilih__item ${aktif === p.id ? "gpilih__item--on" : ""}`}
          onClick={() => onPilih(p.id)}
          style={{ "--aksen": p.aksen }}
        >
          {p.logo ? (
            <MarketLogo id={p.logo} height={p.logo === "lazada" || p.logo === "tokopedia" ? 15 : 17} hidden />
          ) : (
            <span className="gpilih__wa" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="18" height="18">
                <path
                  fill="#25D366"
                  d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 2a8 8 0 1 1-4.1 14.9l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 0 1 12 4zm-3 4.3c-.2 0-.5 0-.7.3-.3.3-1 1-1 2.4s1 2.8 1.2 3c.1.2 2 3.1 4.9 4.2 2.4.9 2.9.8 3.4.7.5-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3l-2-1c-.3-.1-.5-.1-.7.2l-.9 1.1c-.2.2-.3.2-.6.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.3-.4.8-1.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.5-.4-.5-.6-.5H9z"
                />
              </svg>
            </span>
          )}
          <span className="gpilih__nama">{p.nama}</span>
        </button>
      ))}
    </div>
  );
}

function JalurTombol({ ids, utama }) {
  return (
    <div className="gjalur">
      {ids.map((id, i) => {
        const j = JALUR[id];
        const primer = i === 0 || id === utama;
        return (
          <a key={id} href={j.hash} className={`btn ${primer ? "btn--primary" : "btn--outline"}`}>
            {primer ? "Mulai: " : ""}
            {j.nama} ›
          </a>
        );
      })}
    </div>
  );
}

export function GuideScreen({ theme, onToggleTheme }) {
  const [aktif, setAktif] = useState(PLATFORM[0].id);
  const p = useMemo(() => PLATFORM.find((x) => x.id === aktif) ?? PLATFORM[0], [aktif]);

  // Pratinjau: #/panduan?tempat=google membuka langsung platform itu - dipakai tautan dari
  // FAQ dan dari layar kerja, supaya pengguna tidak perlu memilih dua kali.
  useEffect(() => {
    const q = window.location.hash.split("?")[1];
    const t = q ? new URLSearchParams(q).get("tempat") : null;
    if (t && PLATFORM.some((x) => x.id === t)) setAktif(t);
  }, []);

  return (
    <div className="guide">
      <header className="nav guide__nav">
        <Brand onClick={() => goTo("landing")} />
        <div className="nav__links">
          <a href="#/">‹ Beranda</a>
          <a href="#gtempat">Tempat ulasan</a>
          <a href="#gcara">Cara memasukkan</a>
          <a href="#gtanya">Tanya jawab</a>
        </div>
        <div className="nav__right">
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
          <button className="btn btn--primary" onClick={() => goTo("dashboard")}>
            Mulai Analisis ›
          </button>
        </div>
      </header>

      <main className="guide__main">
        <section className="guide__hero">
          <span className="eyebrow">Panduan · 3 menit · tanpa istilah teknis</span>
          <h1>
            Dari mana saya mengambil ulasan <span className="soft">untuk Ulasin?</span>
          </h1>
          <p>
            Pilih tempat ulasan toko Anda biasanya muncul. Kami tunjukkan letak menunya dengan
            gambar, langkah demi langkah. Cara paling mudah dari HP: buka halaman ulasannya, tangkap
            layar, kirim - tidak perlu mengunduh apa pun.
          </p>
          <ul className="guide__jalur-ringkas" aria-label="Tiga cara memasukkan ulasan">
            {Object.values(JALUR).map((j, i) => (
              <li key={j.id} className={i === 0 ? "is-utama" : ""}>
                <a href={`#gcara-${j.id}`}>
                  <b>{j.nama}</b>
                  <span>{j.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </section>

        <section className="guide__tempat" id="gtempat" aria-labelledby="gtempat-judul">
          <div className="section-head">
            <h2 id="gtempat-judul">
              Di mana ulasan Anda <span className="soft">biasanya muncul?</span>
            </h2>
            <p>Ketuk salah satu. Nama menu mengikuti aplikasi versi terbaru; kalau letaknya bergeser, kuncinya satu: cari kata <b>Ulasan</b> atau <b>Penilaian</b>.</p>
          </div>

          <PilihPlatform aktif={aktif} onPilih={setAktif} />

          <div className="gpanel" id="gpanel" role="tabpanel" aria-labelledby={`gtab-${p.id}`} key={p.id}>
            <div className="gpanel__visual">
              <PhoneMock p={p} />
            </div>
            <div className="gpanel__teks">
              <div className="gpanel__kepala">
                {p.logo ? <MarketLogo id={p.logo} height={22} /> : <h3>{p.nama}</h3>}
                <span className="gpanel__ringkas">{p.ringkas}</span>
              </div>
              <ol className="gpanel__langkah">
                {p.langkah.map((l, i) => (
                  <li key={i}>
                    <span className="gpanel__no" aria-hidden="true">
                      {i + 1}
                    </span>
                    <p>
                      <Tebal teks={l} />
                    </p>
                  </li>
                ))}
              </ol>
              {p.alternatif && (
                <p className="gpanel__alt">
                  <b>{p.altJudul ?? "Lewat laptop?"}</b> <Tebal teks={p.alternatif} />
                </p>
              )}
              {p.kalauTidakKetemu && (
                <p className="gpanel__alt gpanel__alt--cari">
                  <b>Kalau menunya tidak ketemu:</b> <Tebal teks={p.kalauTidakKetemu} />
                </p>
              )}
              <JalurTombol ids={p.jalur} />
            </div>
          </div>
        </section>

        <section className="guide__cara" id="gcara" aria-labelledby="gcara-judul">
          <div className="section-head">
            <h2 id="gcara-judul">
              Tiga cara memasukkannya <span className="soft">ke Ulasin</span>
            </h2>
            <p>Pilih yang paling dekat dengan kebiasaan Anda. Semuanya berakhir di laporan yang sama.</p>
          </div>
          <div className="gcara__grid">
            {CARA.map((c, i) => (
              <article className={`gcara__kartu ${i === 0 ? "gcara__kartu--utama" : ""}`} id={`gcara-${c.id}`} key={c.id}>
                <div className="gcara__kepala">
                  <span className="gcara__tag">{i === 0 ? "Paling mudah" : `Cara ${i + 1}`}</span>
                  <h3>{c.judul}</h3>
                  <p>{c.untuk}</p>
                </div>
                <ol>
                  {c.langkah.map((l, j) => (
                    <li key={j}>
                      <IkonCentang />
                      <span>
                        <Tebal teks={l} />
                      </span>
                    </li>
                  ))}
                </ol>
                <p className="gcara__catatan">{c.catatan}</p>
                <div className="gcara__aksi">
                  <a href={JALUR[c.id].hash} className={`btn ${i === 0 ? "btn--primary" : "btn--outline"}`}>
                    Buka tab {JALUR[c.id].nama.split(" /")[0]} ›
                  </a>
                  {c.unduh && (
                    <a href={c.unduh.href} download className="btn btn--text">
                      {c.unduh.label}
                    </a>
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="guide__sebelum" aria-labelledby="gsebelum-judul">
          <h2 id="gsebelum-judul" className="sr-only">
            Sebelum mulai
          </h2>
          <div className="gsebelum__grid">
            {SEBELUM_MULAI.map((s) => (
              <div className="gsebelum__item" key={s.judul}>
                <h3>{s.judul}</h3>
                <p>
                  <Tebal teks={s.isi} />
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="guide__tanya" id="gtanya" aria-labelledby="gtanya-judul">
          <div className="section-head">
            <h2 id="gtanya-judul">
              Yang sering <span className="soft">ditanyakan</span>
            </h2>
          </div>
          <div className="gtanya__list">
            {TANYA.map((t) => (
              <details className="gtanya__item" key={t.q}>
                <summary>{t.q}</summary>
                <p>{t.a}</p>
              </details>
            ))}
          </div>
        </section>

        <section className="guide__cta">
          <h2>Sudah punya tangkapan layarnya?</h2>
          <p>Satu menit dari sekarang Anda sudah membaca tiga hal yang paling perlu dikerjakan.</p>
          <div className="gjalur gjalur--tengah">
            <a href={JALUR.shot.hash} className="btn btn--primary btn--lg">
              Mulai dengan tangkapan layar ›
            </a>
            <button className="btn btn--outline btn--lg" onClick={() => goTo("dashboard")}>
              Coba data contoh dulu
            </button>
          </div>
          <p className="guide__cta-nota">Tanpa akun · data tidak disimpan · gratis</p>
        </section>
      </main>
    </div>
  );
}
