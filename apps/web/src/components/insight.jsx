/** Primitif penampil hasil - dipakai bersama oleh tab Hasil, Detail, dan Tanya Jawab.
 *
 * Dua aturan yang mengikat di seluruh berkas ini:
 * 1. Angka hasil hitungan selalu memakai kelas `.stat` - biru tebal. Itu yang membedakan
 *    fakta terhitung dari narasi yang disusun sistem.
 * 2. Warna tidak pernah menjadi satu-satunya penanda; setiap badge urgensi memuat teksnya.
 */

import { useEffect, useRef } from "react";
import { useOverflowX } from "../lib/hooks.js";
import { QUALITY_LABEL, URGENCY_LABEL, VISUAL_LABEL, aspectLabel, pct } from "../lib/format.js";

/** Menyisipkan angka dalam kalimat dengan gaya angka terhitung. */
export function Narrative({ text, className = "body" }) {
  const parts = String(text ?? "").split(/(\d+(?:[.,]\d+)?%?)/g);
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

const DECISIONS = [
  ["accepted", "Terima"],
  ["rejected", "Tolak"],
  ["saved", "Simpan dulu"],
];

export function DecisionRow({ actionId, decision, onDecide }) {
  return (
    <div className="btn-row">
      {DECISIONS.map(([value, label]) => (
        <button
          key={value}
          className="btn-sm"
          aria-pressed={decision === value}
          onClick={() => onDecide(actionId, decision === value ? null : value)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

/** Kartu aksi.
 *
 * Tingkat urgensi ditandai TIGA kali, sengaja: rona latar kartu (terbaca saat memindai), badge
 * bertulisan (terbaca saat berhenti), dan nomor urut (terbaca bahkan tanpa warna sama sekali).
 * Tidak ada satu pun penanda yang berdiri sendiri.
 */
export function ActionCard({ card, decision, onDecide, onOpenEvidence, index = 0 }) {
  return (
    <article
      className={`acard acard--${card.urgency} reveal`}
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <span className="acard__rank" aria-hidden="true">
        {index + 1}
      </span>
      <span className={`badge badge--${card.urgency}`}>
        {URGENCY_LABEL[card.urgency] ?? card.urgency}
      </span>
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

      <DecisionRow actionId={card.action_id} decision={decision} onDecide={onDecide} />
      {decision && (
        <p className="meta" style={{ marginTop: 10 }}>
          Keputusan Anda tersimpan untuk sesi ini. Sistem tidak menjalankan apa pun sendiri.
        </p>
      )}
    </article>
  );
}

export function DataQualityCard({ quality }) {
  if (!quality) return null;
  return (
    <section className="panel quality">
      <div className="panel-title">Skor kualitas data</div>
      <p className="quality__score">
        <span className="num-hero">{quality.score}</span>
        <span className="meta"> / 100</span>
      </p>
      <p className="meta">
        Kualitas data Anda: <strong>{QUALITY_LABEL[quality.level] ?? quality.level}</strong> ·{" "}
        <span className="stat">{quality.used}</span>/
        <span className="stat">{quality.total_uploaded}</span> baris dianalisis ·{" "}
        <span className="stat">{quality.with_rating}</span> punya rating ·{" "}
        <span className="stat">{quality.with_timestamp}</span> punya tanggal
      </p>
      {quality.notes?.length > 0 && (
        <ul className="meta note-list">
          {quality.notes.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function BenchmarkCard({ rows }) {
  const [scroll, fits] = useOverflowX();
  if (!rows?.length) return null;
  return (
    <section className="panel">
      <div className="panel-title">Benchmark kategori</div>
      <p className="meta" style={{ marginBottom: 10 }}>
        Dibandingkan terhadap rata-rata kategori dari data publik. Bukan data toko pesaing, dan
        bersifat historis, bukan pemantauan langsung.
      </p>
      <div className={`mtable-scroll ${fits ? "mtable-scroll--fit" : ""}`} ref={scroll}>
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
      </div>
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
 * Batang horizontal dipilih karena tugas datanya membandingkan BESARAN antar kategori yang
 * labelnya panjang ("kesesuaian deskripsi"); batang vertikal memaksa label dimiringkan dan
 * tidak terbaca di layar HP. Nilainya dilabeli langsung di ujung kanan, sehingga identitas
 * tidak pernah bergantung pada warna saja.
 */
export function AspectChart({ aggregates }) {
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
            <div
              className="bar"
              key={r.aspect}
              title={`${aspectLabel(r.aspect)}: ${r.total_mentions} sebutan, ${r.negative_count} berisi keluhan`}
            >
              <span className="bar__name">{aspectLabel(r.aspect)}</span>
              <span className="bar__track">
                <i
                  className="bar__fill"
                  style={{
                    width: `${(netral / max) * 100}%`,
                    background: "linear-gradient(90deg, var(--blue), var(--blue-light))",
                    animationDelay: `${i * 55}ms`,
                  }}
                />
                <i
                  className="bar__fill"
                  style={{
                    width: `${(r.negative_count / max) * 100}%`,
                    background: "linear-gradient(90deg, var(--red-base), var(--red-light))",
                    animationDelay: `${i * 55 + 40}ms`,
                  }}
                />
              </span>
              <span className="bar__val">{r.total_mentions}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

/** OPP-01 - aspek yang justru dipuji. Sinyal untuk promosi, bukan teks iklan jadi. */
export function OpportunityCard({ opportunity: o }) {
  return (
    <article className="acard">
      <span className="badge badge--positive">Peluang</span>
      <h4>{o.highlight}</h4>
      <p>
        <span className="stat">{o.positive_count}</span> sebutan positif ·{" "}
        <span className="stat">{pct(o.pct_positive)}</span> dari yang membahas{" "}
        {aspectLabel(o.aspect)}. Dapat Anda pakai sebagai bahan promosi. Sistem tidak menuliskan
        materi iklannya untuk Anda.
      </p>
      {o.evidence_quotes.map((c) => (
        <EvidenceStrip key={c.citation_id} citation={c} />
      ))}
    </article>
  );
}

/** VIS-02 - temuan foto, termasuk yang abstain.
 *
 * Backend hanya mengisi `findings` bila model visual lolos gerbang go/no-go. Selama belum,
 * daftarnya kosong dan bagian ini TIDAK dirender - lebih baik tidak ada daripada ada tetapi
 * berisi tebakan. Status itu dijelaskan pada tab Roadmap.
 */
export function VisualFindings({ findings }) {
  if (!findings?.length) return null;
  const decided = findings.filter((f) => !f.abstain);
  const abstained = findings.filter((f) => f.abstain);
  return (
    <section className="panel">
      <div className="panel-title">Temuan dari foto ulasan</div>
      {decided.length === 0 ? (
        <p className="body">
          Tidak ada foto yang dapat disimpulkan dengan cukup yakin. Semua foto ditandai perlu
          dilihat manusia.
        </p>
      ) : (
        <ul className="body note-list">
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

/** Bukti lengkap. Lembar yang naik dari bawah di layar sempit, dialog di tengah pada layar
 *  lebar - keduanya elemen `dialog` yang sama, hanya berbeda posisi dan animasi lewat CSS.
 *
 *  `dialog` dipakai, bukan div bertumpuk, karena ia sudah membawa jebakan fokus, penutupan
 *  dengan Esc, dan lapisan teratas yang tidak bisa terpotong oleh `overflow` induk mana pun.
 */
export function EvidenceDialog({ card, decision, onDecide, onClose }) {
  const ref = useRef(null);
  const headingRef = useRef(null);

  // `onClose` biasanya ditulis sebagai arrow inline di pemanggilnya, sehingga identitasnya
  // berubah pada SETIAP render induk. Kalau ia ikut menjadi dependensi efek di bawah, efek itu
  // melepas lalu memasang ulang pendengarnya berkali-kali - dan peristiwa `close` milik
  // `<dialog>` dikirim secara asinkron, jadi ia dapat tiba tepat di sela pelepasan itu dan
  // hilang tanpa jejak. Akibatnya panel tampak tertutup tetapi state React masih menganggapnya
  // terbuka, dan kartu berikutnya tidak dapat dibuka sama sekali.
  const tutupRef = useRef(onClose);
  tutupRef.current = onClose;

  useEffect(() => {
    const el = ref.current;
    if (!el || !card) return undefined;
    if (!el.open) el.showModal();
    headingRef.current?.focus();
    // Peristiwa `close` menangkap SEMUA jalan keluar - tombol silang, klik latar, dan Esc
    // yang ditangani browser sendiri - sehingga state React tidak pernah tertinggal terbuka.
    const onCloseEvent = () => tutupRef.current?.();
    el.addEventListener("close", onCloseEvent);
    return () => el.removeEventListener("close", onCloseEvent);
  }, [card]);

  // Setiap jalan keluar yang PUNYA penanganya sendiri memanggil ini, bukan hanya menutup
  // elemennya dan berharap peristiwa `close` menyusul. Peristiwa itu tetap dipasang untuk Esc,
  // yang ditangani browser tanpa melewati kode mana pun - tetapi ia bukan satu-satunya
  // tumpuan. Memanggilnya dua kali tidak berakibat apa-apa: keduanya menyetel state ke null.
  const tutup = () => {
    ref.current?.close();
    onClose();
  };

  if (!card) return null;

  return (
    <dialog
      className="sheet"
      ref={ref}
      aria-label={`Bukti untuk ${card.title}`}
      onClick={(e) => {
        // Latar milik elemen dialog itu sendiri, jadi klik di luar panel muncul sebagai
        // klik pada dialognya.
        if (e.target === ref.current) tutup();
      }}
    >
      <div className="sheet__inner">
        <div className="sheet__handle" aria-hidden="true" />
        <div className="sheet__head">
          <h3 tabIndex={-1} ref={headingRef}>
            Bukti untuk: {card.title}
          </h3>
          <button className="sheet__x" onClick={tutup} aria-label="Tutup">
            ×
          </button>
        </div>

        {card.evidence_quotes.length === 0 ? (
          <div className="banner-grey">
            Data belum cukup untuk menampilkan kutipan pendukung pada topik ini.
          </div>
        ) : (
          <div className="sheet__quotes">
            {card.evidence_quotes.map((c) => (
              <EvidenceStrip key={c.citation_id} citation={c} tag={card.aspect_label} />
            ))}
          </div>
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
                dengan keyakinan <span className="stat">{pct(card.visual_evidence.confidence)}</span>
                .
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

        <div className="sheet__foot">
          <DecisionRow
            actionId={card.action_id}
            decision={decision}
            onDecide={(id, value) => {
              onDecide(id, value);
              tutup();
            }}
          />
        </div>
      </div>
    </dialog>
  );
}
