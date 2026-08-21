/** Dashboard - seluruh fitur analisis hidup di sini.
 *
 * Tiga fase berurutan: `upload` → `processing` → `result`. Baru pada fase terakhir muncul
 * navigasi, karena sebelum ada hasil tidak ada apa pun untuk dijelajahi. Fase disimpan sebagai
 * state, bukan rute tersendiri: menyegarkan halaman di tengah analisis tidak dapat melanjutkan
 * pekerjaan yang sudah berjalan, jadi alamat yang menjanjikan sebaliknya justru menyesatkan.
 *
 * Navigasi hasil menyusut dari empat tab menjadi TIGA, dan ketiganya kini mode, bukan bagian:
 * membaca laporan, bertanya kepadanya, dan melihat apa yang belum dibangun. Seluruh isi
 * laporan - yang dulu terbagi antara tab Hasil dan tab Detail, ditambah lima bagian baru -
 * pindah ke satu gulungan bersama rel bagian; alasannya di kepala `ReportPanel.jsx`.
 *
 * Yang juga hilang dari berkas ini: sapaan bernama toko dan avatar berinisial. Keduanya
 * bergantung pada isian "Nama toko" yang tidak pernah bisa dideteksi dari berkas ekspor
 * marketplace mana pun - ekspor ulasan tidak menyebutkan nama toko Anda, karena Anda sudah
 * tahu. Menanyakannya demi sebuah sapaan berarti menagih pekerjaan untuk hiasan, dan laporan
 * analitik tidak menyapa pembacanya dengan nama; ia menunjukkan angkanya.
 */

import { useEffect, useRef, useState } from "react";
import {
  api,
  guessMapping,
  parseFile,
  parsePastedText,
  rowsToReviews,
} from "../api/client.js";
import { Brand, ThemeToggle } from "../components/Brand.jsx";
import { EvidenceDialog } from "../components/insight.jsx";
import { ProcessingStep, estimateSeconds } from "../components/dashboard/ProcessingStep.jsx";
import { QnaPanel } from "../components/dashboard/QnaPanel.jsx";
import { ReportPanel } from "../components/dashboard/ReportPanel.jsx";
import { RoadmapPanel } from "../components/dashboard/RoadmapPanel.jsx";
import { UploadStep } from "../components/dashboard/UploadStep.jsx";
import { goTo } from "../lib/hooks.js";
import { rentangTanggal } from "../lib/format.js";

const TABS = [
  ["laporan", "Laporan"],
  ["tanya", "Tanya Jawab"],
  ["roadmap", "Roadmap"],
];

const HEADINGS = {
  upload: ["Masukkan ulasan untuk mulai", "Tempel, unggah berkas, atau kirim tangkapan layar"],
  processing: ["Memproses ulasan Anda…", "Mohon tunggu sebentar"],
  laporan: ["Laporan analisis", null],
  tanya: ["Tanya Jawab Ulasan", "Jawaban selalu disertai kutipan aslinya"],
  roadmap: ["Roadmap Selanjutnya", "Transparan soal apa yang belum ada"],
};

let draftSeq = 0;

export function DashboardScreen({ theme, onToggleTheme }) {
  const [phase, setPhase] = useState("upload");
  const [tab, setTab] = useState("laporan");
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(null);

  // --- masukan
  const [input, setInput] = useState("paste");
  const [paste, setPaste] = useState("");
  const [file, setFile] = useState(null); // { name, columns, rows, truncated }
  const [mapping, setMapping] = useState({});
  const [shots, setShots] = useState([]); // nama berkas gambar yang sudah dibaca
  const [drafts, setDrafts] = useState([]); // hasil OCR yang masih dapat disunting
  const [ocrBusy, setOcrBusy] = useState(false);

  // --- hasil
  // Jam analisis. `elapsed` diperbarui empat kali sedetik selama fase processing; `estimate`
  // dikunci saat analisis dimulai supaya angkanya tidak bergeser di tengah penantian.
  const [elapsed, setElapsed] = useState(0);
  const [estimate, setEstimate] = useState(20);
  const [batch, setBatch] = useState(0);
  const [result, setResult] = useState(null);
  const [decisions, setDecisions] = useState({});
  const [openCard, setOpenCard] = useState(null);

  // Kategori pembanding yang sedang ditampilkan. Dimulai dari tebakan backend dan dapat
  // diganti pengguna di kepala laporan - tanpa analisis ulang, karena backend mengirimkan
  // baseline SELURUH kategori sekaligus (lihat `_benchmarks_for_every_category`).
  const [category, setCategory] = useState("other");

  // --- tanya jawab
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [askError, setAskError] = useState(null);

  const top = useRef(null);

  useEffect(() => {
    api.readiness().then(() => setReady(true)).catch(() => setReady(false));
  }, []);

  function scrollUp() {
    window.scrollTo({ top: 0, behavior: "auto" });
  }

  // ----------------------------------------------------------------------------------
  // Analisis
  // ----------------------------------------------------------------------------------

  async function run(reviews) {
    if (!reviews.length) {
      setError({ message: "Belum ada ulasan untuk dianalisis." });
      return;
    }
    setError(null);
    setPhase("processing");
    setBatch(reviews.length);
    setEstimate(estimateSeconds(reviews.length));
    setElapsed(0);
    scrollUp();

    // Waktu diukur dari jam dinding, bukan dari jumlah tick yang sudah lewat. `setInterval`
    // tidak dijamin tepat waktu - tab latar belakang di-throttle sampai sekali per detik - dan
    // menghitung tick akan membuat jamnya tertinggal jauh persis pada pengguna yang berpindah
    // tab justru karena analisisnya lama.
    const mulai = Date.now();
    const ticker = setInterval(() => setElapsed((Date.now() - mulai) / 1000), 250);
    try {
      const data = await api.analyze(reviews);
      setResult(data);
      setCategory(data.category_guess?.category ?? "other");
      setMessages([]);
      setDecisions({});
      setTab("laporan");
      setPhase("result");
      scrollUp();
    } catch (err) {
      setError({ message: err.message, action: err.suggestedAction });
      setPhase("upload");
      scrollUp();
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
          // Data contoh membawa kolom produknya sendiri, dan tanpa meneruskannya bagian per
          // produk tidak akan pernah muncul pada jalur "coba data contoh" - persis jalur yang
          // dipakai orang untuk menilai apakah produk ini berguna.
          product_name: r.product_name || null,
          category: "other",
          source: "sample_dataset",
        }))
      );
    } catch (err) {
      setError({ message: err.message });
    }
  }

  // ----------------------------------------------------------------------------------
  // Masukan
  // ----------------------------------------------------------------------------------

  async function onPickFile(picked) {
    if (!picked) return;
    setError(null);
    try {
      const parsed = await parseFile(picked);
      setFile({ name: picked.name, ...parsed });
      setMapping(guessMapping(parsed.columns));
    } catch (err) {
      setFile(null);
      setError({ message: err.message });
    }
  }

  async function onPickShots(picked) {
    if (!picked?.length) return;
    setError(null);
    setOcrBusy(true);
    try {
      const read = await api.readScreenshots(picked);
      setShots((s) => [...s, ...read.images]);
      setDrafts((d) => [
        ...d,
        ...read.reviews.map((r) => ({ ...r, review_id: `ocr_${(draftSeq += 1)}` })),
      ]);
      if (read.reviews.length === 0) {
        setError({
          message: "Tidak ada teks ulasan yang terbaca dari gambar itu.",
          action: "Coba tangkapan layar yang lebih tajam, atau tempel teksnya langsung.",
        });
      }
    } catch (err) {
      setError({ message: err.message, action: err.suggestedAction });
    } finally {
      setOcrBusy(false);
    }
  }

  const mappedReviews = file ? rowsToReviews(file.rows, mapping) : [];
  const pastedReviews = parsePastedText(paste);
  const draftReviews = drafts
    .filter((d) => d.text.trim().length >= 3)
    .map((d) => ({
      review_id: d.review_id,
      text: d.text.trim(),
      rating: d.rating ?? null,
      timestamp: null,
      category: "other",
      source: "manual_upload",
    }));

  const pending =
    input === "paste" ? pastedReviews : input === "file" ? mappedReviews : draftReviews;
  const canAnalyze =
    ready && pending.length > 0 && (input !== "file" || Boolean(mapping.text)) && !ocrBusy;

  // ----------------------------------------------------------------------------------
  // Tanya jawab
  // ----------------------------------------------------------------------------------

  async function ask(question) {
    setTab("tanya");
    setAskError(null);
    setAsking(true);
    setMessages((m) => [...m, { id: `q${m.length}`, role: "user", text: question }]);
    try {
      const answer = await api.ask(result.analysis_id, question);
      setMessages((m) => [...m, { id: `a${m.length}`, role: "system", answer }]);
    } catch (err) {
      setAskError(err.message);
    } finally {
      setAsking(false);
    }
  }

  // ----------------------------------------------------------------------------------
  // Ulang
  // ----------------------------------------------------------------------------------

  function restart() {
    setPhase("upload");
    setResult(null);
    setDecisions({});
    setMessages([]);
    setOpenCard(null);
    setError(null);
    scrollUp();
  }

  const key = phase === "result" ? tab : phase;
  const [title, subtitle] = HEADINGS[key];

  // Sub-judul laporan menyebut cakupan datanya, bukan menyapa pembacanya. Inilah keterangan
  // yang benar-benar dibutuhkan sebelum membaca angka apa pun di bawahnya: berapa banyak, dan
  // dari rentang waktu kapan.
  const rentang = result && rentangTanggal(result.summary.period_start, result.summary.period_end);

  return (
    <div className="dash">
      <header className="dash__bar">
        <Brand onClick={() => goTo("landing")} />
        <div className="nav__right">
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
          {phase === "result" && (
            <button className="btn btn--outline" onClick={restart}>
              Analisis baru
            </button>
          )}
        </div>
      </header>

      <main className={`dash__main ${phase === "result" ? "dash__main--wide" : ""}`} ref={top}>
        <div className="dash__head">
          <div>
            <h1>{title}</h1>
            {subtitle ? (
              <p>{subtitle}</p>
            ) : (
              result && (
                <p>
                  <span className="stat">{result.summary.total_reviews}</span> ulasan
                  {rentang && <> · {rentang}</>}
                  {result.products?.length > 1 && (
                    <>
                      {" "}
                      · <span className="stat">{result.products.length}</span> produk
                    </>
                  )}
                </p>
              )
            )}
          </div>
        </div>

        {phase === "result" && (
          <nav className="segmented" role="tablist" aria-label="Bagian hasil">
            {TABS.map(([id, label]) => (
              <button
                key={id}
                role="tab"
                aria-selected={tab === id}
                className={`segmented__item ${tab === id ? "segmented__item--on" : ""}`}
                onClick={() => setTab(id)}
              >
                {label}
              </button>
            ))}
          </nav>
        )}

        <div className="dash__body" key={key}>
          {phase === "upload" && (
            <UploadStep
              ready={ready}
              error={error}
              tab={input}
              onTab={setInput}
              paste={paste}
              onPaste={setPaste}
              file={file}
              mapping={mapping}
              onPickFile={onPickFile}
              onMap={setMapping}
              onClearFile={() => setFile(null)}
              shots={shots}
              drafts={drafts}
              ocrBusy={ocrBusy}
              onPickShots={onPickShots}
              onEditDraft={(id, text) =>
                setDrafts((d) => d.map((x) => (x.review_id === id ? { ...x, text } : x)))
              }
              onRemoveDraft={(id) => setDrafts((d) => d.filter((x) => x.review_id !== id))}
              onClearShots={() => {
                setShots([]);
                setDrafts([]);
              }}
              count={pending.length}
              canAnalyze={canAnalyze}
              onAnalyze={() => run(pending)}
              onSample={runSample}
            />
          )}

          {phase === "processing" && (
            <ProcessingStep elapsed={elapsed} estimate={estimate} count={batch} />
          )}

          {phase === "result" && result && (
            <>
              {tab === "laporan" && (
                <ReportPanel
                  result={result}
                  category={category}
                  onCategory={setCategory}
                  decisions={decisions}
                  onDecide={(id, value) => setDecisions((d) => ({ ...d, [id]: value }))}
                  onOpenEvidence={setOpenCard}
                />
              )}
              {tab === "tanya" && (
                <QnaPanel
                  messages={messages}
                  busy={asking}
                  error={askError}
                  aggregates={result.aspect_aggregates}
                  onAsk={ask}
                />
              )}
              {tab === "roadmap" && <RoadmapPanel />}
            </>
          )}
        </div>
      </main>

      <EvidenceDialog
        card={openCard}
        decision={openCard ? decisions[openCard.action_id] : null}
        onDecide={(id, value) => setDecisions((d) => ({ ...d, [id]: value }))}
        onClose={() => setOpenCard(null)}
      />
    </div>
  );
}
