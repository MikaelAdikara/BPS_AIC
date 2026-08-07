/** Komponen InsightUlasan.
 *
 * Dua aturan yang mengikat di seluruh berkas ini (docs/BRAND_GUIDELINES.md):
 * 1. Angka hasil hitungan dan kutipan verbatim selalu monospace — itu yang membedakan
 *    fakta terhitung dari narasi yang disusun sistem.
 * 2. Warna tidak pernah menjadi satu-satunya penanda; setiap pill urgensi memuat teksnya.
 */

import { useEffect, useRef } from "react";

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
  return (
    <blockquote className="evidence">
      <p className="evidence__quote">"{citation.quote}"</p>
      <div className="evidence__meta">
        Ulasan {citation.review_id} · relevansi {citation.relevance_score}
      </div>
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
