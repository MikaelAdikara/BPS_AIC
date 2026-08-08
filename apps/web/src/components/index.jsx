/** Komponen InsightUlasan.
 *
 * Dua aturan yang mengikat di seluruh berkas ini (docs/BRAND_GUIDELINES.md):
 * 1. Angka hasil hitungan dan kutipan verbatim selalu monospace — itu yang membedakan
 *    fakta terhitung dari narasi yang disusun sistem.
 * 2. Warna tidak pernah menjadi satu-satunya penanda; setiap pill urgensi memuat teksnya.
 */

import { useEffect, useRef, useState } from "react";

const URGENCY_LABEL = { tinggi: "Tinggi", sedang: "Sedang", rendah: "Rendah" };
const ASPECT_LABEL = {
  kualitas_produk: "kualitas produk",
  kesesuaian_deskripsi: "kesesuaian deskripsi",
  harga_value: "harga",
  kemasan: "kemasan",
  pengiriman: "pengiriman",
  pelayanan_penjual: "pelayanan penjual",
  ukuran_varian: "ukuran/varian",
  rasa_kualitas_makanan: "rasa",
  kelengkapan: "kelengkapan",
  keaslian: "keaslian",
  kemudahan_penggunaan: "kemudahan pemakaian",
};

export const aspectLabel = (id) => ASPECT_LABEL[id] ?? id;
const pct = (v) => `${Math.round(v * 100)}%`;

/** Menyisipkan angka dalam kalimat dengan gaya monospace. */
export function Narrative({ text }) {
  const parts = String(text).split(/(\d+(?:[.,]\d+)?%?)/g);
  return (
    <p style={{ margin: "0 0 var(--space-3)" }}>
      {parts.map((part, i) =>
        /^\d/.test(part) ? (
          <span key={i} className="stat">
            {part}
          </span>
        ) : (
          part
        )
      )}
    </p>
  );
}

export function EvidenceStrip({ citation }) {
  // Rating dan tanggal menentukan seberapa berat sebuah kutipan patut ditimbang; tanpa
  // keduanya semua kutipan terlihat sama pentingnya.
  const meta = [
    `Ulasan ${citation.review_id}`,
    citation.rating ? `${citation.rating}/5` : null,
    citation.timestamp ? String(citation.timestamp).slice(0, 10) : null,
    `relevansi ${citation.relevance_score}`,
  ].filter(Boolean);

  return (
    <blockquote className="evidence">
      <p className="evidence__quote">"{citation.quote}"</p>
      <div className="evidence__meta">{meta.join(" · ")}</div>
    </blockquote>
  );
}

export function ActionCard({ card, decision, onDecide, onOpenEvidence }) {
  const urgency = card.urgency;
  return (
    <article className="card">
      <span className={`pill pill--${urgency}`}>{URGENCY_LABEL[urgency] ?? urgency}</span>
      <h3 className="title">{card.title}</h3>
      <Narrative text={card.recommended_action} />

      {card.evidence_quotes.slice(0, 1).map((c) => (
        <EvidenceStrip key={c.citation_id} citation={c} />
      ))}

      {card.evidence_quotes.length > 0 && (
        <button className="linkish" onClick={() => onOpenEvidence(card)}>
          Lihat semua bukti ({card.evidence_quotes.length}) →
        </button>
      )}

      <div className="actions">
        {[
          ["accepted", "Terima", "btn--primary"],
          ["rejected", "Tolak", "btn--outline"],
          ["saved", "Simpan dulu", "btn--text"],
        ].map(([value, label, variant]) => (
          <button
            key={value}
            className={`btn ${variant}`}
            aria-pressed={decision === value}
            onClick={() => onDecide(card.action_id, decision === value ? null : value)}
          >
            {label}
          </button>
        ))}
      </div>
      {decision && (
        <p className="body-s" style={{ marginTop: "var(--space-3)" }}>
          Keputusan Anda tersimpan untuk sesi ini. Sistem tidak menjalankan apa pun sendiri.
        </p>
      )}
    </article>
  );
}

export function BenchmarkCard({ rows }) {
  if (!rows?.length) return null;
  return (
    <section className="card">
      <h3 className="title">Perbandingan kategori sejenis</h3>
      <p className="body-s" style={{ marginBottom: "var(--space-4)" }}>
        Dibandingkan terhadap rata-rata kategori dari data publik. Bukan data toko pesaing, dan
        bersifat historis — bukan pemantauan langsung.
      </p>
      <table className="bench">
        <thead>
          <tr>
            <th>Aspek</th>
            <th>Toko Anda</th>
            <th>Rata-rata</th>
            <th>Selisih</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 5).map((r) => (
            <tr key={r.aspect}>
              <td>{aspectLabel(r.aspect)}</td>
              <td>{pct(r.store_pct)}</td>
              <td>
                {pct(r.baseline_pct)} <span style={{ opacity: 0.6 }}>±{pct(r.margin_of_error)}</span>
              </td>
              <td style={{ color: r.gap > 0 ? "var(--urgency-high)" : "var(--positive)" }}>
                {r.gap > 0 ? "+" : ""}
                {pct(r.gap)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="body-s" style={{ marginTop: "var(--space-3)" }}>
        Dari <span className="stat">{rows[0].baseline_sample_size}</span> ulasan pembanding ·
        keyakinan {rows[0].confidence_level}
      </p>
    </section>
  );
}

// --------------------------------------------------------------------------------------
// ING-05 / ING-07 — kualitas data dan pemetaan kolom
// --------------------------------------------------------------------------------------

const QUALITY_LABEL = { baik: "Baik", cukup: "Cukup", terbatas: "Terbatas" };

export function DataQualityCard({ quality }) {
  if (!quality) return null;
  const tone =
    quality.level === "baik" ? "positive" : quality.level === "cukup" ? "urgency-medium" : "urgency-high";
  return (
    <section className="card">
      <div className="quality">
        <div className="quality__score" style={{ color: `var(--${tone})` }}>
          <span className="stat quality__number">{quality.score}</span>
          <span className="body-s">dari 100</span>
        </div>
        <div>
          <h3 className="title" style={{ margin: 0 }}>
            Kualitas data Anda: {QUALITY_LABEL[quality.level] ?? quality.level}
          </h3>
          <p className="body-s" style={{ marginTop: "var(--space-1)" }}>
            <span className="stat">{quality.used}</span> dari{" "}
            <span className="stat">{quality.total_uploaded}</span> baris dianalisis ·{" "}
            <span className="stat">{quality.with_rating}</span> punya rating ·{" "}
            <span className="stat">{quality.with_timestamp}</span> punya tanggal
          </p>
        </div>
      </div>
      <ul className="notes">
        {quality.notes.map((n) => (
          <li key={n}>{n}</li>
        ))}
      </ul>
    </section>
  );
}

/** OPP-01 — aspek yang justru dipuji. Sinyal untuk promosi, bukan teks iklan jadi. */
export function OpportunitySection({ opportunities }) {
  if (!opportunities?.length) return null;
  return (
    <section className="card card--positive">
      <span className="pill pill--positive">Kekuatan</span>
      <h3 className="title">Yang sudah Anda lakukan dengan baik</h3>
      <p className="body-s" style={{ marginBottom: "var(--space-4)" }}>
        Aspek berikut paling sering dipuji pembeli. Anda dapat memakainya sebagai bahan promosi —
        sistem tidak menuliskan materi iklannya untuk Anda.
      </p>
      {opportunities.map((o) => (
        <div key={o.aspect} className="opp">
          <p style={{ margin: 0 }}>
            <strong>{o.highlight}</strong>
          </p>
          <p className="body-s">
            <span className="stat">{o.positive_count}</span> sebutan positif ·{" "}
            <span className="stat">{pct(o.pct_positive)}</span> dari yang membahas{" "}
            {aspectLabel(o.aspect)}
          </p>
          {o.evidence_quotes.map((c) => (
            <EvidenceStrip key={c.citation_id} citation={c} />
          ))}
        </div>
      ))}
    </section>
  );
}

const VISUAL_LABEL = {
  produk_rusak: "Produk rusak",
  kemasan_rusak: "Kemasan rusak",
  produk_berbeda: "Produk berbeda dari pesanan",
  produk_normal: "Produk terlihat normal",
};

/** VIS-02 — temuan foto, termasuk yang abstain (bagian 19.2). */
export function VisualFindings({ findings }) {
  if (!findings?.length) return null;
  const decided = findings.filter((f) => !f.abstain);
  const abstained = findings.filter((f) => f.abstain);
  return (
    <section className="card">
      <h3 className="title">Temuan dari foto</h3>
      {decided.length === 0 ? (
        <p className="body-s">
          Tidak ada foto yang dapat disimpulkan dengan cukup yakin. Semua foto ditandai perlu
          dilihat manusia.
        </p>
      ) : (
        <ul className="notes">
          {decided.map((f) => (
            <li key={f.image_ref}>
              <strong>{VISUAL_LABEL[f.label] ?? f.label}</strong> pada ulasan{" "}
              <span className="stat">{f.review_id}</span> · keyakinan{" "}
              <span className="stat">{pct(f.confidence)}</span>
            </li>
          ))}
        </ul>
      )}
      {abstained.length > 0 && (
        <p className="banner banner--muted" style={{ marginTop: "var(--space-4)" }}>
          <span className="stat">{abstained.length}</span> foto tidak disimpulkan karena sistem
          tidak cukup yakin. Foto tersebut menunggu Anda periksa sendiri — sistem sengaja tidak
          menebak.
        </p>
      )}
    </section>
  );
}

// --------------------------------------------------------------------------------------
// QNA-01 — kotak tanya jawab dengan sitasi
// --------------------------------------------------------------------------------------

const SUGGESTED_QUESTIONS = [
  "Apa keluhan yang paling sering muncul?",
  "Bagaimana pendapat pembeli tentang pengiriman?",
  "Apakah ada masalah dengan ukuran atau varian?",
];

export function QnABox({ analysisId, onAsk }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function submit(q) {
    const asked = (q ?? question).trim();
    if (!asked || busy) return;
    setBusy(true);
    setError(null);
    setQuestion(asked);
    try {
      setAnswer(await onAsk(analysisId, asked));
    } catch (err) {
      setError(err.message);
      setAnswer(null);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h3 className="title">Tanya data Anda</h3>
      <p className="body-s" style={{ marginBottom: "var(--space-4)" }}>
        Jawaban hanya disusun dari ulasan yang Anda unggah dan selalu menyertakan kutipannya.
        Jika buktinya tidak ada, sistem akan mengatakan tidak tahu.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <label className="label" htmlFor="qna">
          Pertanyaan Anda
        </label>
        <input
          id="qna"
          className="input"
          value={question}
          maxLength={500}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Misalnya: keluhan apa yang paling sering muncul?"
        />
        <div className="actions">
          <button className="btn btn--primary" type="submit" disabled={busy || !question.trim()}>
            {busy ? "Mencari bukti…" : "Tanya"}
          </button>
        </div>
      </form>

      <div className="chips">
        {SUGGESTED_QUESTIONS.map((q) => (
          <button key={q} type="button" className="chip" onClick={() => submit(q)} disabled={busy}>
            {q}
          </button>
        ))}
      </div>

      {error && <div className="banner banner--error">{error}</div>}

      {answer && (
        <div style={{ marginTop: "var(--space-5)" }}>
          {answer.no_answer ? (
            <div className="banner banner--muted">
              <strong>Sistem tidak menjawab pertanyaan ini.</strong>
              <div style={{ marginTop: "var(--space-1)" }}>{answer.no_answer_reason}</div>
            </div>
          ) : (
            <>
              <Narrative text={answer.answer} />
              {answer.citations.map((c) => (
                <EvidenceStrip key={c.citation_id} citation={c} />
              ))}
            </>
          )}
        </div>
      )}
    </section>
  );
}

// --------------------------------------------------------------------------------------
// Unggah berkas (ING-02) dan pratinjau
// --------------------------------------------------------------------------------------

const MAPPABLE = [
  ["text", "Kolom teks ulasan", true],
  ["rating", "Kolom rating (opsional)", false],
  ["timestamp", "Kolom tanggal (opsional)", false],
  ["product_name", "Kolom nama produk (opsional)", false],
];

/** ING-07 — pengguna menentukan sendiri kolom mana yang berisi apa. */
export function ColumnMapper({ columns, mapping, onChange }) {
  return (
    <div className="mapper">
      {MAPPABLE.map(([field, label, required]) => (
        <div key={field}>
          <label className="label" htmlFor={`map-${field}`}>
            {label}
          </label>
          <select
            id={`map-${field}`}
            className="input"
            value={mapping[field] ?? ""}
            onChange={(e) => onChange({ ...mapping, [field]: e.target.value })}
          >
            <option value="">{required ? "— pilih kolom —" : "— tidak ada —"}</option>
            {columns.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      ))}
    </div>
  );
}

/** Pratinjau lima baris pertama supaya pengguna tahu yang terbaca benar sebelum menganalisis. */
export function PreviewTable({ rows, columns, mapping }) {
  if (!rows?.length) return null;
  const shown = columns.slice(0, 4);
  return (
    <div className="preview">
      <table className="bench">
        <thead>
          <tr>
            {shown.map((c) => (
              <th key={c}>
                {c}
                {c === mapping.text && <span className="tag">teks ulasan</span>}
                {c === mapping.rating && <span className="tag">rating</span>}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 5).map((row, i) => (
            <tr key={i}>
              {shown.map((c) => (
                <td key={c} className="preview__cell">
                  {String(row[c] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="body-s">
        Menampilkan 5 dari <span className="stat">{rows.length}</span> baris terbaca
        {columns.length > shown.length && ` · ${columns.length - shown.length} kolom lain disembunyikan`}
      </p>
    </div>
  );
}

export function EvidenceDrawer({ card, onClose }) {
  const headingRef = useRef(null);

  // Fokus berpindah ke judul saat panel dibuka, dan Esc menutupnya — panel yang tidak dapat
  // ditutup keyboard membuat pengguna terjebak.
  useEffect(() => {
    headingRef.current?.focus();
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!card) return null;
  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Bukti pendukung"
        onClick={(e) => e.stopPropagation()}
      >
        <button className="linkish" onClick={onClose}>
          ← Kembali ke hasil
        </button>
        <h2 className="display-m" tabIndex={-1} ref={headingRef} style={{ marginTop: "var(--space-4)" }}>
          Bukti untuk: {card.title}
        </h2>
        <p className="body-s">{card.one_line_summary}</p>

        {card.evidence_quotes.length === 0 ? (
          <p className="banner banner--muted">
            Data belum cukup untuk menampilkan kutipan pendukung pada topik ini.
          </p>
        ) : (
          card.evidence_quotes.map((c) => <EvidenceStrip key={c.citation_id} citation={c} />)
        )}

        {card.visual_evidence && (
          <>
            <h3 className="title" style={{ marginTop: "var(--space-8)" }}>
              Bukti visual
            </h3>
            {card.visual_evidence.abstain ? (
              <p className="banner banner--muted">
                Ada foto pada ulasan ini, tetapi sistem tidak cukup yakin untuk menyimpulkannya
                ({card.visual_evidence.abstain_reason}). Silakan periksa sendiri.
              </p>
            ) : (
              <p className="body-s">
                Foto pada ulasan <span className="stat">{card.visual_evidence.review_id}</span>{" "}
                terdeteksi sebagai{" "}
                <strong>
                  {VISUAL_LABEL[card.visual_evidence.label] ?? card.visual_evidence.label}
                </strong>{" "}
                dengan keyakinan <span className="stat">{pct(card.visual_evidence.confidence)}</span>.
              </p>
            )}
          </>
        )}

        <h3 className="title" style={{ marginTop: "var(--space-8)" }}>
          Kenapa ini diprioritaskan
        </h3>
        <Narrative text={card.priority_reasoning} />

        <h3 className="title" style={{ marginTop: "var(--space-6)" }}>
          Kalau rekomendasi ini keliru
        </h3>
        <p className="body-s">{card.risk_if_recommendation_wrong}</p>
      </aside>
    </div>
  );
}
