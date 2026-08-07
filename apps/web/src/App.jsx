/** InsightUlasan — alur linear empat layar (blueprint bagian 13.1, 14).
 *
 * Tidak ada router dan tidak ada nav global: seluruh interaksi berada dalam satu alur
 * Landing → Processing → Result → Evidence, sesuai batas MVP satu input → satu output AI.
 */

import { useEffect, useState } from "react";
import { api, parsePastedText } from "./api/client";
import { ActionCard, BenchmarkCard, EvidenceDrawer, Narrative, aspectLabel } from "./components";
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

export default function App() {
  const [screen, setScreen] = useState("landing");
  const [text, setText] = useState("");
  const [stage, setStage] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [decisions, setDecisions] = useState({});
  const [openCard, setOpenCard] = useState(null);
  const [ready, setReady] = useState(false);

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

      <p className="body-s" style={{ marginTop: "var(--space-6)" }}>
        Data Anda hanya diproses selama sesi ini dan tidak disimpan permanen. Nomor telepon dan
        data pribadi yang terdeteksi disamarkan sebelum dianalisis.
      </p>
    </main>
  );
}
