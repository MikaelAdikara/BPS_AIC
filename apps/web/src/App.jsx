/** InsightUlasan - alur linear empat layar (blueprint bagian 13.1, 14).
 *
 * Tidak ada router dan tidak ada nav global: seluruh interaksi berada dalam satu alur
 * Landing → Processing → Result → Evidence, sesuai batas MVP satu input → satu output AI.
 *
 * Halaman landing membawa lapisan pemasaran (hero, fitur, CTA) DI ATAS panel unggah yang
 * sesungguhnya. Tautan "Mulai" hanya menggulir ke panel itu - bukan berpindah halaman -
 * supaya alur satu-arah tersebut tetap utuh.
 *
 * Setiap layar aplikasi duduk di dalam `.page-frame`: bingkai membulat yang mengapung di
 * atas kanvas, persis seperti layar S1–S4 pada desain referensi.
 */

import { useEffect, useRef, useState } from "react";
import { api, guessMapping, parseFile, parsePastedText, rowsToReviews } from "./api/client";
import {
  ActionCard,
  AspectChart,
  BenchmarkCard,
  ColumnMapper,
  DataQualityCard,
  EvidenceDrawer,
  Narrative,
  OpportunitySection,
  PreviewTable,
  QnABox,
  VisualFindings,
} from "./components";
import {
  Brand,
  Features,
  FootCta,
  Hero,
  HowItWorks,
  MarketplaceBand,
  SiteNav,
} from "./components/landing";
import "./styles/app.css";

const STAGES = [
  "Membaca teks ulasan",
  "Mengambil bukti pendukung",
  "Mengelompokkan masalah",
  "Menyusun rekomendasi",
];

const WARNING_TEXT = {
  data_kecil:
    "Data Anda kurang dari 15 ulasan. Anggap hasil ini sebagai indikasi awal, bukan kesimpulan pasti.",
  baris_dilewati: "Sebagian baris dilewati karena kosong atau terduplikasi.",
  pii_diredaksi:
    "Nomor telepon dan data pribadi yang ditemukan sudah disamarkan sebelum dianalisis.",
  mode_sederhana:
    "Mode sederhana aktif. Sebagian penjelasan memakai teks standar, tetapi seluruh angka dan bukti tetap lengkap.",
  data_kosong: "Tidak ada ulasan yang dapat dianalisis dari data ini.",
};

const CATEGORIES = [
  ["other", "Lainnya / campuran"],
  ["fashion", "Fashion"],
  ["electronics", "Elektronik"],
  ["food_beverage", "Makanan & minuman"],
  ["beauty", "Kecantikan"],
  ["home_living", "Rumah tangga"],
];

export default function App() {
  const [screen, setScreen] = useState("landing");
  const [tab, setTab] = useState("paste"); // paste | file
  const [text, setText] = useState("");
  const [file, setFile] = useState(null); // { name, columns, rows, truncated }
  const [mapping, setMapping] = useState({});
  const [category, setCategory] = useState("other");
  const [stage, setStage] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [decisions, setDecisions] = useState({});
  const [openCard, setOpenCard] = useState(null);
  const [ready, setReady] = useState(false);
  // Desain ini bermode terang; gelap adalah varian, bukan sebaliknya. Karena itu preferensi
  // OS TIDAK dibaca saat muat - mesin yang kebetulan bertema gelap dulu membuka aplikasi
  // dalam tampilan yang bukan tampilan rancangannya. Yang dihormati hanya pilihan eksplisit
  // pengguna, dan pilihan itu diingat antar-kunjungan.
  const [theme, setTheme] = useState(() => {
    if (typeof window === "undefined") return "light";
    return window.localStorage?.getItem("insightulasan:theme") === "dark" ? "dark" : "light";
  });
  const fileInput = useRef(null);
  const startRef = useRef(null);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage?.setItem("insightulasan:theme", theme);
  }, [theme]);

  useEffect(() => {
    api.readiness().then(() => setReady(true)).catch(() => setReady(false));
  }, []);

  async function run(reviews) {
    if (!reviews.length) {
      setError({ message: "Belum ada ulasan untuk dianalisis." });
      return;
    }
    setError(null);
    setScreen("processing");
    setStage(0);
    window.scrollTo({ top: 0 });
    // Checklist maju bertahap agar pengguna tahu sistem benar-benar bekerja - ini satu-satunya
    // momen bergerak di seluruh aplikasi (BRAND_GUIDELINES §8).
    const ticker = setInterval(() => setStage((s) => Math.min(s + 1, STAGES.length - 1)), 900);
    try {
      const data = await api.analyze(reviews);
      setResult(data);
      setScreen("result");
      window.scrollTo({ top: 0 });
    } catch (err) {
      setError({ message: err.message, action: err.suggestedAction });
      setScreen("landing");
    } finally {
      clearInterval(ticker);
    }
  }

  async function runSample() {
    try {
      const sample = await api.sample();
      await run(
        sample.reviews.map((r) => ({
          review_id: r.review_id,
          text: r.text,
          rating: Number(r.rating) || null,
          timestamp: r.timestamp || null,
          category: r.category || "other",
          source: "sample_dataset",
        }))
      );
    } catch (err) {
      setError({ message: err.message });
    }
  }

  async function onPickFile(picked) {
    if (!picked) return;
    setError(null);
    try {
      const parsed = await parseFile(picked);
      setFile({ name: picked.name, ...parsed });
      setMapping(guessMapping(parsed.columns));
      setTab("file");
    } catch (err) {
      setFile(null);
      setError({ message: err.message });
    }
  }

  function reset() {
    setResult(null);
    setDecisions({});
    setOpenCard(null);
    setScreen("landing");
    window.scrollTo({ top: 0 });
  }

  function goToStart() {
    startRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  const themeToggle = (
    <button
      className="themebtn"
      onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
      aria-pressed={theme === "dark"}
    >
      {theme === "dark" ? "Mode terang" : "Mode gelap"}
    </button>
  );

  // Header ringkas untuk layar di dalam alur - tanpa tautan pemasaran yang mengganggu.
  const appHeader = (
    <nav className="nav">
      <Brand onClick={reset} />
      <div className="nav__right">
        {themeToggle}
        <button className="btn btn--outline" onClick={reset}>
          Mulai analisis baru
        </button>
      </div>
    </nav>
  );

  const avatar = <div className="app-ava">OU</div>;

  if (screen === "processing") {
    const percent = Math.round(((stage + 1) / STAGES.length) * 100);
    return (
      <>
        {appHeader}
        <main>
          <div className="tour-tag">
            <b>02</b> · Memproses otomatis
          </div>
          <div className="page-frame">
            <div className="app-l">
              <div className="app-top">
                <div className="app-hello">
                  Memproses ulasan Anda…<span>Mohon tunggu sebentar</span>
                </div>
                {avatar}
              </div>

              <div className="panel">
                <div className="panel-title">
                  Progres{" "}
                  <em>
                    <span className="stat">{percent}</span>%
                  </em>
                </div>
                <div
                  className="track"
                  role="progressbar"
                  aria-valuenow={percent}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <div
                    className="fill"
                    style={{
                      width: `${percent}%`,
                      background: "linear-gradient(90deg, var(--blue), var(--blue-light))",
                      transition: "width var(--motion-panel) var(--ease-out)",
                    }}
                  />
                </div>
                <p className="meta" style={{ marginTop: 9 }}>
                  {STAGES[stage]}…
                </p>
              </div>

              <div className="panel">
                <div className="panel-title">Tahapan</div>
                {STAGES.map((s, i) => {
                  const state = i < stage ? "done" : i === stage ? "active" : "pending";
                  return (
                    <div
                      key={s}
                      className={`check-row ${state}`}
                      style={{ animationDelay: `${i * 0.12}s` }}
                    >
                      <span className={`check-circle ${state}`}>
                        {state === "done" && (
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none">
                            <path
                              d="M5 12.5l4.5 4.5L19 7.5"
                              stroke="#fff"
                              strokeWidth="3"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        )}
                      </span>
                      <span className="lbl">{s}</span>
                    </div>
                  );
                })}
              </div>

              <p className="meta">Biasanya kurang dari satu menit untuk 100 ulasan.</p>
            </div>
          </div>
        </main>
      </>
    );
  }

  if (screen === "result" && result) {
    return (
      <>
        {appHeader}
        <main>
          <div className="tour-tag">
            <b>03</b> · Hasil analisis
          </div>
          <div className="page-frame">
            <div className="app-l">
              <div className="app-top">
                {/* Subjudul di sini metadata, bukan fakta terhitung, jadi tanpa `.stat`,
                    yang lagipula akan kalah spesifisitas dari `.app-hello span`. */}
                <div className="app-hello">
                  Hasil Analisis<span>Toko Anda · {result.summary.total_reviews} ulasan</span>
                </div>
                {avatar}
              </div>

              <div className="panel">
                <div className="panel-title">Ringkasan</div>
                <Narrative text={result.summary.executive_summary_text} className="body" />
                {result.warnings?.map((w) => (
                  <div key={w} className="banner-grey" style={{ margin: "10px 0 0" }}>
                    {WARNING_TEXT[w] ?? w}
                  </div>
                ))}
              </div>

              <DataQualityCard quality={result.data_quality} />

              {result.top_actions.length > 0 && (
                <>
                  <div className="panel-title" style={{ margin: "20px 2px 9px" }}>
                    Yang perlu dikerjakan lebih dulu
                  </div>
                  {result.top_actions.map((card, i) => (
                    <ActionCard
                      key={card.action_id}
                      index={i}
                      card={card}
                      decision={decisions[card.action_id]}
                      onDecide={(id, value) => setDecisions((d) => ({ ...d, [id]: value }))}
                      onOpenEvidence={setOpenCard}
                    />
                  ))}
                </>
              )}

              <OpportunitySection opportunities={result.opportunities} />
              <VisualFindings findings={result.visual_findings} />
              <BenchmarkCard rows={result.benchmark} />
              <AspectChart aggregates={result.aspect_aggregates} />

              <QnABox analysisId={result.analysis_id} onAsk={api.ask} />

              <p className="meta" style={{ marginTop: 20 }}>
                Model: {result.model_versions?.text} · mode {result.mode}
              </p>
              <button className="btn-cta" onClick={reset} style={{ marginTop: 12 }}>
                Mulai analisis baru
              </button>
            </div>
          </div>

          <EvidenceDrawer card={openCard} onClose={() => setOpenCard(null)} />
        </main>
      </>
    );
  }

  const mappedReviews = file ? rowsToReviews(file.rows, mapping, category) : [];

  return (
    <>
      <SiteNav onStart={goToStart} themeToggle={themeToggle} />

      <Hero onStart={goToStart} />
      <MarketplaceBand />
      <HowItWorks />
      <Features />

      <main id="mulai" ref={startRef}>
        <div className="tour-tag">
          <b>01</b> · Unggah data ulasan
        </div>
        <div className="page-frame">
          <div className="app-l">
            <div className="app-top">
              <div className="app-hello">
                Halo, Owner UMKM!<span>Masukkan ulasan untuk mulai</span>
              </div>
              {avatar}
            </div>

            {!ready && (
              <div className="banner-grey">
                Sistem sedang menyiapkan model. Tombol analisis akan aktif setelah siap.
              </div>
            )}
            {error && (
              <div className="banner-error">
                <b>{error.message}</b>
                {error.action && <div style={{ marginTop: 4 }}>{error.action}</div>}
              </div>
            )}

            <div className="tabs" role="tablist" style={{ marginBottom: 14 }}>
              {[
                ["paste", "Tempel teks"],
                ["file", "Unggah berkas"],
              ].map(([id, label]) => (
                <button
                  key={id}
                  role="tab"
                  aria-selected={tab === id}
                  className={`tab ${tab === id ? "tab--active" : ""}`}
                  onClick={() => setTab(id)}
                >
                  {label}
                </button>
              ))}
            </div>

            {tab === "paste" ? (
              <>
                <div className="panel">
                  <div className="panel-title">Tempel ulasan Anda, satu ulasan per baris</div>
                  <label className="sr-only" htmlFor="paste">
                    Ulasan Anda
                  </label>
                  <textarea
                    id="paste"
                    className="textarea"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder={
                      "ukurannya kekecilan padahal pesan L\npengiriman cepat, packing rapi\n…"
                    }
                  />
                </div>
                <button
                  className="btn-cta"
                  disabled={!ready}
                  onClick={() => run(parsePastedText(text))}
                >
                  Analisis {parsePastedText(text).length || ""} ulasan ›
                </button>
                <button
                  className="btn btn--outline"
                  disabled={!ready}
                  onClick={runSample}
                  style={{ width: "100%", marginTop: 10 }}
                >
                  Coba dengan data contoh
                </button>
              </>
            ) : (
              <>
                <div
                  className="dropzone"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    onPickFile(e.dataTransfer.files?.[0]);
                  }}
                >
                  <span className="dz-icon" aria-hidden="true">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path
                        d="M12 4v12m0-12l-4 4m4-4l4 4M5 18h14"
                        stroke="#fff"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>
                  <p>
                    <b>Tarik file CSV/JSON ke sini</b>
                    <br />
                    atau klik untuk memilih file
                  </p>
                  <button className="btn btn--outline" onClick={() => fileInput.current?.click()}>
                    Pilih berkas
                  </button>
                  <input
                    ref={fileInput}
                    type="file"
                    accept=".csv,.json,text/csv,application/json"
                    className="sr-only"
                    onChange={(e) => onPickFile(e.target.files?.[0])}
                  />
                  <p className="meta">Maksimal 5 MB · 1.000 baris pertama yang dipakai</p>
                </div>

                {file && (
                  <>
                    <div className="panel">
                      <p className="body">
                        <b>{file.name}</b> terbaca ·{" "}
                        <span className="stat">{file.columns.length}</span> kolom
                        {file.truncated && " · sisanya dipotong di 1.000 baris"}
                      </p>
                    </div>

                    <div className="panel">
                      <div className="panel-title">Pemetaan kolom</div>
                      <ColumnMapper
                        columns={file.columns}
                        mapping={mapping}
                        onChange={setMapping}
                      />
                      <div className="map-row">
                        <label className="src" htmlFor="cat">
                          Kategori produk
                        </label>
                        <span className="arrow" aria-hidden="true">
                          →
                        </span>
                        <select
                          id="cat"
                          value={category}
                          onChange={(e) => setCategory(e.target.value)}
                        >
                          {CATEGORIES.map(([v, l]) => (
                            <option key={v} value={v}>
                              {l}
                            </option>
                          ))}
                        </select>
                      </div>
                      <p className="meta" style={{ marginTop: 10 }}>
                        Tebakan otomatis dapat Anda ubah. Hanya kolom teks ulasan yang wajib.
                      </p>
                    </div>

                    <div className="panel">
                      <div className="panel-title">Pratinjau data</div>
                      <PreviewTable rows={file.rows} columns={file.columns} mapping={mapping} />
                    </div>

                    <button
                      className="btn-cta"
                      disabled={!ready || !mapping.text || !mappedReviews.length}
                      onClick={() => run(mappedReviews)}
                    >
                      Analisis {mappedReviews.length || ""} ulasan ›
                    </button>
                    {!mapping.text && (
                      <p className="meta" style={{ marginTop: 8 }}>
                        Pilih kolom teks ulasan lebih dulu untuk mulai menganalisis.
                      </p>
                    )}
                    <button
                      className="btn btn--text"
                      onClick={() => setFile(null)}
                      style={{ width: "100%", marginTop: 6 }}
                    >
                      Ganti berkas
                    </button>
                  </>
                )}
              </>
            )}

            <p className="meta" style={{ marginTop: 20 }}>
              Data Anda hanya diproses selama sesi ini dan tidak disimpan permanen. Nomor telepon
              dan data pribadi yang terdeteksi disamarkan sebelum dianalisis. Foto ulasan belum
              didukung pada versi ini.
            </p>
          </div>
        </div>
      </main>

      <FootCta onStart={goToStart} />
    </>
  );
}
