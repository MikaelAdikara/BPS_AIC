/** Komponen InsightUlasan.
 *
 * Dua aturan yang mengikat di seluruh berkas ini:
 * 1. Angka hasil hitungan selalu memakai kelas `.stat` - biru tebal, sesuai `.num` pada
 *    sistem desain Stitch. Itu yang membedakan fakta terhitung dari narasi yang disusun
 *    sistem. (Sebelumnya monospace; lihat catatan di docs/BRAND_GUIDELINES.md.)
 * 2. Warna tidak pernah menjadi satu-satunya penanda; setiap badge urgensi memuat teksnya.
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

/** Menyisipkan angka dalam kalimat dengan gaya angka terhitung. */
export function Narrative({ text, className = "body" }) {
  const parts = String(text).split(/(\d+(?:[.,]\d+)?%?)/g);
  return (
    <p className={className}>
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

export function EvidenceStrip({ citation, tag }) {
  // Rating dan tanggal menentukan seberapa berat sebuah kutipan patut ditimbang; tanpa
  // keduanya semua kutipan terlihat sama pentingnya.
  const meta = [
    citation.review_id,
    citation.rating ? `${citation.rating}/5` : null,
    citation.timestamp ? String(citation.timestamp).slice(0, 10) : null,
    citation.relevance_score != null ? `relevansi ${citation.relevance_score}` : null,
  ].filter(Boolean);

  return (
    <blockquote className="equote">
      <span className="qm" aria-hidden="true">
        ”
      </span>
      <p>{citation.quote}</p>
      <div className="meta">{meta.join(" · ")}</div>
      {tag && <span className="tag">{tag}</span>}
    </blockquote>
  );
}

export function ActionCard({ card, decision, onDecide, onOpenEvidence, index = 0 }) {
  const urgency = card.urgency;
  return (
    <article className="acard reveal" style={{ animationDelay: `${index * 60}ms` }}>
      <span className={`badge badge--${urgency}`}>{URGENCY_LABEL[urgency] ?? urgency}</span>
      <h4>{card.title}</h4>
      <Narrative text={card.recommended_action} className="" />

      {card.evidence_quotes.slice(0, 1).map((c) => (
        <EvidenceStrip key={c.citation_id} citation={c} />
      ))}

      {card.evidence_quotes.length > 0 && (
        <button className="link-more" onClick={() => onOpenEvidence(card)}>
          Lihat semua bukti ({card.evidence_quotes.length}) →
        </button>
      )}

      <div className="btn-row">
        {[
          ["accepted", "Terima"],
          ["rejected", "Tolak"],
          ["saved", "Simpan dulu"],
        ].map(([value, label]) => (
          <button
            key={value}
            className="btn-sm"
            aria-pressed={decision === value}
            onClick={() => onDecide(card.action_id, decision === value ? null : value)}
          >
            {label}
          </button>
        ))}
      </div>
      {decision && (
        <p className="meta" style={{ marginTop: 10 }}>
          Keputusan Anda tersimpan untuk sesi ini. Sistem tidak menjalankan apa pun sendiri.
        </p>
      )}
    </article>
  );
}

export function BenchmarkCard({ rows }) {
  if (!rows?.length) return null;
  return (
    <section className="panel">
      <div className="panel-title">Benchmark kategori</div>
      <p className="meta" style={{ marginBottom: 10 }}>
        Dibandingkan terhadap rata-rata kategori dari data publik. Bukan data toko pesaing, dan
        bersifat historis, bukan pemantauan langsung.
      </p>
      <table className="mtable">
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
              <td className="stat">{pct(r.store_pct)}</td>
              <td className="stat">{pct(r.baseline_pct)}</td>
              <td
                className="stat"
                style={{ color: r.gap > 0 ? "var(--red-ink)" : "var(--green-ink)" }}
              >
                {r.gap > 0 ? "+" : ""}
                {pct(r.gap)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="meta" style={{ marginTop: 8 }}>
        Dari <span className="stat">{rows[0].baseline_sample_size}</span> ulasan pembanding ·
        keyakinan {rows[0].confidence_level} · margin ±
        <span className="stat">{pct(rows[0].margin_of_error)}</span>
      </p>
    </section>
  );
}

/** Sebaran aspek sebagai batang horizontal.
 *
 * Batang horizontal dipilih karena tugas datanya membandingkan BESARAN antar kategori
 * yang labelnya panjang ("kesesuaian deskripsi"); batang vertikal memaksa label dimiringkan
 * dan tidak terbaca di layar HP. Nilainya juga dilabeli langsung di ujung kanan, sehingga
 * identitas tidak pernah bergantung pada warna saja.
 */
export function AspectChart({ aggregates }) {
  const [hover, setHover] = useState(null);
  if (!aggregates?.length) return null;

  const rows = [...aggregates].sort((a, b) => b.total_mentions - a.total_mentions).slice(0, 6);
  const max = Math.max(...rows.map((r) => r.total_mentions), 1);

  return (
    <section className="panel">
      <div className="panel-title">Sebaran per aspek</div>
      <div className="legend">
        <span>
          <i style={{ background: "var(--blue)" }} />
          Disebut
        </span>
        <span>
          <i style={{ background: "var(--red-base)" }} />
          Berisi keluhan
        </span>
      </div>

      <div className="bars">
        {rows.map((r, i) => {
          const netral = r.total_mentions - r.negative_count;
          return (
            <div className="bar" key={r.aspect}>
              <span className="bar__name">{aspectLabel(r.aspect)}</span>
              <span className="bar__track">
                <i
                  className="bar__fill"
                  style={{
                    width: `${(netral / max) * 100}%`,
                    background: "linear-gradient(90deg, var(--blue), var(--blue-light))",
                    animationDelay: `${i * 55}ms`,
                  }}
                  onMouseEnter={() =>
                    setHover(`${aspectLabel(r.aspect)}: ${r.total_mentions} sebutan`)
                  }
                  onMouseLeave={() => setHover(null)}
                />
                <i
                  className="bar__fill"
                  style={{
                    width: `${(r.negative_count / max) * 100}%`,
                    background: "linear-gradient(90deg, var(--red-base), var(--red-light))",
                    animationDelay: `${i * 55 + 40}ms`,
                  }}
                  onMouseEnter={() =>
                    setHover(`${aspectLabel(r.aspect)}: ${r.negative_count} berisi keluhan`)
                  }
                  onMouseLeave={() => setHover(null)}
                />
              </span>
              <span className="bar__val">{r.total_mentions}</span>
            </div>
          );
        })}
      </div>

      {/* Teks ini juga jalur baca alternatif bagi pembaca layar. */}
      <p className="meta" aria-live="polite" style={{ marginTop: 10 }}>
        {hover ?? "Arahkan kursor ke batang untuk melihat angkanya."}
      </p>
    </section>
  );
}

// --------------------------------------------------------------------------------------
// ING-05 / ING-07 - kualitas data dan pemetaan kolom
// --------------------------------------------------------------------------------------

const QUALITY_LABEL = { baik: "Baik", cukup: "Cukup", terbatas: "Terbatas" };

export function DataQualityCard({ quality }) {
  if (!quality) return null;
  return (
    <section className="panel" style={{ textAlign: "center" }}>
      <div className="panel-title" style={{ textAlign: "left" }}>
        Skor kualitas data
      </div>
      <span className="num-hero">{quality.score}</span>
      <span className="meta"> / 100</span>
      <p className="meta" style={{ marginTop: 8 }}>
        Kualitas data Anda: <strong>{QUALITY_LABEL[quality.level] ?? quality.level}</strong> ·{" "}
        <span className="stat">{quality.used}</span>/
        <span className="stat">{quality.total_uploaded}</span> baris dianalisis ·{" "}
        <span className="stat">{quality.with_rating}</span> punya rating ·{" "}
        <span className="stat">{quality.with_timestamp}</span> punya tanggal
      </p>
      {quality.notes?.length > 0 && (
        <ul
          className="meta"
          style={{ textAlign: "left", margin: "12px 0 0", paddingLeft: 18, lineHeight: 1.6 }}
        >
          {quality.notes.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

/** OPP-01 - aspek yang justru dipuji. Sinyal untuk promosi, bukan teks iklan jadi. */
export function OpportunitySection({ opportunities }) {
  if (!opportunities?.length) return null;
  return (
    <>
      {opportunities.map((o) => (
        <article className="acard" key={o.aspect}>
          <span className="badge badge--positive">Positif</span>
          <h4>{o.highlight}</h4>
          <p>
            <span className="stat">{o.positive_count}</span> sebutan positif ·{" "}
            <span className="stat">{pct(o.pct_positive)}</span> dari yang membahas{" "}
            {aspectLabel(o.aspect)}. Dapat Anda pakai sebagai bahan promosi. Sistem tidak
            menuliskan materi iklannya untuk Anda.
          </p>
          {o.evidence_quotes.map((c) => (
            <EvidenceStrip key={c.citation_id} citation={c} />
          ))}
        </article>
      ))}
    </>
  );
}

const VISUAL_LABEL = {
  produk_rusak: "Produk rusak",
  kemasan_rusak: "Kemasan rusak",
  produk_berbeda: "Produk berbeda dari pesanan",
  produk_normal: "Produk terlihat normal",
};

/** VIS-02 - temuan foto, termasuk yang abstain (bagian 19.2). */
export function VisualFindings({ findings }) {
  if (!findings?.length) return null;
  const decided = findings.filter((f) => !f.abstain);
  const abstained = findings.filter((f) => f.abstain);
  return (
    <section className="panel">
      <div className="panel-title">Temuan dari foto</div>
      {decided.length === 0 ? (
        <p className="body">
          Tidak ada foto yang dapat disimpulkan dengan cukup yakin. Semua foto ditandai perlu
          dilihat manusia.
        </p>
      ) : (
        <ul className="body" style={{ margin: 0, paddingLeft: 18 }}>
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
        <div className="banner-grey" style={{ marginTop: 14, marginBottom: 0 }}>
          <span className="stat">{abstained.length}</span> foto tidak disimpulkan karena sistem
          tidak cukup yakin. Foto tersebut menunggu Anda periksa sendiri. Sistem sengaja tidak
          menebak.
        </div>
      )}
    </section>
  );
}

// --------------------------------------------------------------------------------------
// QNA-01 - kotak tanya jawab dengan sitasi
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
    <section style={{ marginTop: 20 }}>
      <form
        className="qabox"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <label className="sr-only" htmlFor="qna">
          Tanya tentang hasil ini
        </label>
        <span aria-hidden="true">✎</span>
        <input
          id="qna"
          value={question}
          maxLength={500}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Tanya tentang hasil ini…"
        />
        <button className="btn btn--primary" type="submit" disabled={busy || !question.trim()}>
          {busy ? "Mencari…" : "Tanya"}
        </button>
      </form>

      <div className="chips">
        {SUGGESTED_QUESTIONS.map((q) => (
          <button key={q} type="button" className="chip" onClick={() => submit(q)} disabled={busy}>
            {q}
          </button>
        ))}
      </div>

      <p className="meta" style={{ marginTop: 10 }}>
        Jawaban hanya disusun dari ulasan yang Anda unggah dan selalu menyertakan kutipannya. Jika
        buktinya tidak ada, sistem akan mengatakan tidak tahu.
      </p>

      {error && (
        <div className="banner-error" style={{ marginTop: 12 }}>
          {error}
        </div>
      )}

      {answer && (
        <div style={{ marginTop: 14 }}>
          {answer.no_answer ? (
            <div className="banner-grey">
              <b>Sistem tidak menjawab pertanyaan ini.</b>
              <div style={{ marginTop: 4 }}>{answer.no_answer_reason}</div>
            </div>
          ) : (
            <div className="acard">
              <Narrative text={answer.answer} className="" />
              {answer.citations.map((c) => (
                <EvidenceStrip key={c.citation_id} citation={c} />
              ))}
            </div>
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
  ["text", "Teks ulasan", true],
  ["rating", "Rating", false],
  ["timestamp", "Tanggal", false],
  ["product_name", "Nama produk", false],
];

/** ING-07 - pengguna menentukan sendiri kolom mana yang berisi apa. */
export function ColumnMapper({ columns, mapping, onChange }) {
  return (
    <div>
      {MAPPABLE.map(([field, label, required]) => (
        <div className="map-row" key={field}>
          <label className="src" htmlFor={`map-${field}`}>
            {label}
            {required ? " *" : ""}
          </label>
          <span className="arrow" aria-hidden="true">
            →
          </span>
          <select
            id={`map-${field}`}
            value={mapping[field] ?? ""}
            onChange={(e) => onChange({ ...mapping, [field]: e.target.value })}
          >
            <option value="">{required ? "Pilih kolom" : "Tidak ada"}</option>
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
    <>
      <div className="mtable-scroll">
        <table className="mtable">
          <thead>
            <tr>
              {shown.map((c) => (
                <th key={c}>
                  {c}
                  {c === mapping.text && " · ulasan"}
                  {c === mapping.rating && " · rating"}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 5).map((row, i) => (
              <tr key={i}>
                {shown.map((c) => (
                  <td key={c} className="cell-clip">
                    {String(row[c] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="meta" style={{ marginTop: 8 }}>
        Menampilkan 5 dari <span className="stat">{rows.length}</span> baris terbaca
        {columns.length > shown.length &&
          ` · ${columns.length - shown.length} kolom lain disembunyikan`}
      </p>
    </>
  );
}

/** Bukti lengkap sebagai lembar yang naik dari bawah (bottom sheet), sesuai layar S4. */
export function EvidenceDrawer({ card, onClose }) {
  const headingRef = useRef(null);

  // Fokus berpindah ke judul saat panel dibuka, dan Esc menutupnya - panel yang tidak dapat
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
        <div className="handle" />
        <div className="drawer-head">
          <h3 tabIndex={-1} ref={headingRef}>
            Bukti untuk: {card.title}
          </h3>
          <button className="x" onClick={onClose} aria-label="Tutup">
            ×
          </button>
        </div>

        {card.evidence_quotes.length === 0 ? (
          <div className="banner-grey">
            Data belum cukup untuk menampilkan kutipan pendukung pada topik ini.
          </div>
        ) : (
          card.evidence_quotes.map((c) => (
            <EvidenceStrip key={c.citation_id} citation={c} tag={card.aspect_label} />
          ))
        )}

        {card.visual_evidence && (
          <div className="banner-grey" style={{ marginTop: 12 }}>
            {card.visual_evidence.abstain ? (
              <>
                Ada foto pada ulasan ini, tetapi sistem tidak cukup yakin untuk menyimpulkannya (
                {card.visual_evidence.abstain_reason}). Silakan periksa sendiri.
              </>
            ) : (
              <>
                Foto pada ulasan <span className="stat">{card.visual_evidence.review_id}</span>{" "}
                terdeteksi sebagai{" "}
                <b>{VISUAL_LABEL[card.visual_evidence.label] ?? card.visual_evidence.label}</b>{" "}
                dengan keyakinan{" "}
                <span className="stat">{pct(card.visual_evidence.confidence)}</span>.
              </>
            )}
          </div>
        )}

        <div className="reason-box">
          <h5>Kenapa ini diprioritaskan</h5>
          <Narrative text={card.priority_reasoning} className="body" />
        </div>

        <div className="banner-grey" style={{ marginTop: 12 }}>
          Risiko bila keliru: {card.risk_if_recommendation_wrong}
        </div>
      </aside>
    </div>
  );
}
