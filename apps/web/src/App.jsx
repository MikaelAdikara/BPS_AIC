/** InsightUlasan — alur linear empat layar (blueprint bagian 13.1, 14).
 *
 * Tidak ada router dan tidak ada nav global: seluruh interaksi berada dalam satu alur
 * Landing → Processing → Result → Evidence, sesuai batas MVP satu input → satu output AI.
 */

import { useEffect, useRef, useState } from "react";
import { api, guessMapping, parseFile, parsePastedText, rowsToReviews } from "./api/client";
import {
  ActionCard,
  BenchmarkCard,
  ColumnMapper,
  DataQualityCard,
  EvidenceDrawer,
  Narrative,
  OpportunitySection,
  PreviewTable,
  QnABox,
  VisualFindings,
  aspectLabel,
} from "./components";
import "./styles/app.css";

const STAGES = [
  "Memproses teks ulasan",
  "Mengambil bukti pendukung",
  "Menghitung prioritas",
  "Menyusun rekomendasi",
];

const WARNING_TEXT = {
  data_kecil:
    "Data Anda kurang dari 15 ulasan — anggap hasil ini sebagai indikasi awal, bukan kesimpulan pasti.",
  baris_dilewati: "Sebagian baris dilewati karena kosong atau terduplikasi.",
  pii_diredaksi:
    "Nomor telepon dan data pribadi yang ditemukan sudah disamarkan sebelum dianalisis.",
  mode_sederhana:
    "Mode sederhana aktif — sebagian penjelasan memakai teks standar. Seluruh angka dan bukti tetap lengkap.",
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
  const fileInput = useRef(null);

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
    // Checklist maju bertahap agar pengguna tahu sistem benar-benar bekerja — ini satu-satunya
    // momen bergerak di seluruh aplikasi (BRAND_GUIDELINES §8).
    const ticker = setInterval(() => setStage((s) => Math.min(s + 1, STAGES.length - 1)), 900);
    try {
      const data = await api.analyze(reviews);
      setResult(data);
      setScreen("result");
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
  }

  if (screen === "processing") {
    return (
      <main className="shell">
        <h1 className="display-m">Sedang menganalisis…</h1>
        <div
          className="progress"
          role="progressbar"
          aria-valuenow={Math.round(((stage + 1) / STAGES.length) * 100)}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <div className="progress__bar" style={{ width: `${((stage + 1) / STAGES.length) * 100}%` }} />
        </div>
        {STAGES.map((s, i) => (
          <div key={s} className={`stage ${i <= stage ? "stage--done" : ""}`} style={{ animationDelay: `${i * 0.12}s` }}>
            <span className="stage__mark">{i <= stage ? "✓" : ""}</span>
            {s}
          </div>
        ))}
        <p className="body-s" style={{ marginTop: "var(--space-6)" }}>
          Biasanya kurang dari satu menit untuk 100 ulasan.
        </p>
      </main>
    );
  }

  if (screen === "result" && result) {
    return (
      <main className="shell">
        <span className="label">Hasil analisis</span>
        <h1 className="display-m" style={{ marginTop: "var(--space-2)" }}>
          Ringkasan
        </h1>
        <Narrative text={result.summary.executive_summary_text} />

        {result.warnings?.map((w) => (
          <div key={w} className={`banner ${w === "mode_sederhana" ? "banner--muted" : "banner--warn"}`}>
            {WARNING_TEXT[w] ?? w}
          </div>
        ))}

        <DataQualityCard quality={result.data_quality} />

        {result.top_actions.length > 0 && (
          <>
            <h2 className="title" style={{ marginTop: "var(--space-8)" }}>
              Yang perlu dikerjakan lebih dulu
            </h2>
            {result.top_actions.map((card) => (
              <ActionCard
                key={card.action_id}
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

        <section className="card">
          <h3 className="title">Rincian per aspek</h3>
          <table className="bench">
            <thead>
              <tr>
                <th>Aspek</th>
                <th>Disebut</th>
                <th>Keluhan</th>
              </tr>
            </thead>
            <tbody>
              {result.aspect_aggregates.slice(0, 8).map((a) => (
                <tr key={a.aspect}>
                  <td>{aspectLabel(a.aspect)}</td>
                  <td>{a.total_mentions}</td>
                  <td style={{ color: a.negative_count ? "var(--urgency-high)" : "var(--ink-muted)" }}>
                    {a.negative_count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <QnABox analysisId={result.analysis_id} onAsk={api.ask} />

        <p className="body-s">
          Model: {result.model_versions?.text} · mode {result.mode}
        </p>
        <button className="btn btn--outline" onClick={reset} style={{ marginTop: "var(--space-4)" }}>
          Mulai analisis baru
        </button>

        <EvidenceDrawer card={openCard} onClose={() => setOpenCard(null)} />
      </main>
    );
  }

  const mappedReviews = file ? rowsToReviews(file.rows, mapping, category) : [];

  return (
    <main className="shell">
      <h1 className="display-l">InsightUlasan</h1>
      <p className="lead">
        Ubah ulasan pelanggan jadi langkah nyata — tiga masalah paling mendesak, bukti kutipan
        aslinya, dan apa yang bisa dikerjakan minggu ini.
      </p>

      {!ready && (
        <div className="banner banner--muted">
          Sistem sedang menyiapkan model. Tombol analisis akan aktif setelah siap.
        </div>
      )}
      {error && (
        <div className="banner banner--error">
          <strong>{error.message}</strong>
          {error.action && <div style={{ marginTop: "var(--space-1)" }}>{error.action}</div>}
        </div>
      )}

      <div className="tabs" role="tablist">
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
          <label className="label" htmlFor="paste">
            Tempel ulasan Anda — satu ulasan per baris
          </label>
          <textarea
            id="paste"
            className="textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={"ukurannya kekecilan padahal pesan L\npengiriman cepat, packing rapi\n…"}
            style={{ marginTop: "var(--space-2)" }}
          />
          <div className="actions">
            <button className="btn btn--primary" disabled={!ready} onClick={() => run(parsePastedText(text))}>
              Analisis sekarang
            </button>
            <button className="btn btn--outline" disabled={!ready} onClick={runSample}>
              Coba dengan data contoh
            </button>
          </div>
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
            <p style={{ margin: 0 }}>Tarik berkas CSV atau JSON ke sini</p>
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
            <p className="body-s" style={{ margin: 0 }}>
              Maksimal 5 MB · 1.000 baris pertama yang dipakai
            </p>
          </div>

          {file && (
            <>
              <p className="body-s" style={{ marginTop: "var(--space-4)" }}>
                <strong>{file.name}</strong> terbaca ·{" "}
                <span className="stat">{file.columns.length}</span> kolom
                {file.truncated && " · sisanya dipotong di 1.000 baris"}
              </p>

              <h2 className="title" style={{ marginTop: "var(--space-6)" }}>
                Cocokkan kolom
              </h2>
              <p className="body-s">
                Tebakan otomatis di bawah dapat Anda ubah. Hanya kolom teks ulasan yang wajib.
              </p>
              <ColumnMapper columns={file.columns} mapping={mapping} onChange={setMapping} />

              <label className="label" htmlFor="cat" style={{ marginTop: "var(--space-4)", display: "block" }}>
                Kategori produk (untuk pembanding)
              </label>
              <select
                id="cat"
                className="input"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {CATEGORIES.map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>

              <h2 className="title" style={{ marginTop: "var(--space-6)" }}>
                Pratinjau
              </h2>
              <PreviewTable rows={file.rows} columns={file.columns} mapping={mapping} />

              <div className="actions">
                <button
                  className="btn btn--primary"
                  disabled={!ready || !mapping.text || !mappedReviews.length}
                  onClick={() => run(mappedReviews)}
                >
                  Analisis {mappedReviews.length || ""} ulasan
                </button>
                <button className="btn btn--text" onClick={() => setFile(null)}>
                  Ganti berkas
                </button>
              </div>
              {!mapping.text && (
                <p className="body-s">Pilih kolom teks ulasan lebih dulu untuk mulai menganalisis.</p>
              )}
            </>
          )}
        </>
      )}

      <p className="body-s" style={{ marginTop: "var(--space-6)" }}>
        Data Anda hanya diproses selama sesi ini dan tidak disimpan permanen. Nomor telepon dan
        data pribadi yang terdeteksi disamarkan sebelum dianalisis. Foto ulasan belum didukung
        pada versi ini.
      </p>
    </main>
  );
}
