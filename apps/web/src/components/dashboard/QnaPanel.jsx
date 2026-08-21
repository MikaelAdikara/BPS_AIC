/** Tab Tanya Jawab - percakapan, bukan satu kotak jawaban yang menimpa dirinya sendiri.
 *
 * Riwayat disimpan di layar induk agar tidak hilang saat pengguna berpindah tab; komponen ini
 * hanya menampilkannya. Setiap jawaban membawa kutipan aslinya, dan bila buktinya tidak ada
 * sistem mengatakan tidak tahu alih-alih menyusun kalimat yang terdengar meyakinkan.
 *
 * Pertanyaan yang disarankan mengikuti aspek yang paling banyak DIKELUHKAN datanya. Daftar
 * tetap yang dulu ada di sini menawarkan pertanyaan soal ukuran/varian kepada pemilik warung
 * kopi; penggantinya lalu mengikuti aspek yang ditandai sendiri oleh pengguna di layar unggah -
 * lebih baik, tetapi masih tebakan yang dibuat tepat pada saat ia paling sedikit tahu, yaitu
 * sebelum melihat satu pun hasil. Sekarang urutannya datang dari `aspect_aggregates`, jadi yang
 * ditawarkan adalah pertanyaan tentang masalah yang benar-benar ada di datanya. Susunannya di
 * `lib/aspects.js`.
 */

import { useEffect, useRef, useState } from "react";
import { pertanyaanUntuk } from "../../lib/aspects.js";
import { EvidenceStrip, Narrative } from "../insight.jsx";

export function QnaPanel({ messages, busy, error, aggregates = [], onAsk }) {
  const disarankan = pertanyaanUntuk(aggregates);
  const dariData = aggregates.some((a) => a.negative_count > 0);
  const [question, setQuestion] = useState("");
  const tail = useRef(null);

  useEffect(() => {
    tail.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages.length, busy]);

  function submit(text) {
    const asked = (text ?? question).trim();
    if (!asked || busy) return;
    setQuestion("");
    onAsk(asked);
  }

  return (
    <div className="reading-col">
      {messages.length === 0 && (
        <>
          <h3 className="sec-title">
            {dariData ? "Berdasarkan yang paling sering dikeluhkan" : "Pertanyaan yang disarankan"}
          </h3>
          <div className="chips">
            {disarankan.map((q) => (
              <button key={q} type="button" className="chip" onClick={() => submit(q)} disabled={busy}>
                {q}
              </button>
            ))}
          </div>
        </>
      )}

      <div className="thread">
        {messages.map((m) =>
          m.role === "user" ? (
            <p className="bubble bubble--you" key={m.id}>
              {m.text}
            </p>
          ) : (
            <div className="bubble bubble--sys" key={m.id}>
              {m.answer.no_answer ? (
                <>
                  <b>Sistem tidak menjawab pertanyaan ini.</b>
                  <p className="body" style={{ marginTop: 4 }}>
                    {m.answer.no_answer_reason}
                  </p>
                </>
              ) : (
                <>
                  <Narrative text={m.answer.answer} className="" />
                  {m.answer.citations.map((c) => (
                    <EvidenceStrip key={c.citation_id} citation={c} />
                  ))}
                </>
              )}
            </div>
          )
        )}

        {busy && (
          <p className="bubble bubble--sys bubble--wait">Mencari di ulasan Anda…</p>
        )}
        <div ref={tail} />
      </div>

      {error && <div className="banner-error">{error}</div>}

      <form
        className="qabox qabox--sticky"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <label className="sr-only" htmlFor="qna">
          Tulis pertanyaan Anda tentang hasil ini
        </label>
        <span aria-hidden="true">✎</span>
        <input
          id="qna"
          value={question}
          maxLength={500}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Tulis pertanyaan Anda tentang hasil ini…"
        />
        <button className="btn btn--primary" type="submit" disabled={busy || !question.trim()}>
          {busy ? "Mencari…" : "Tanya"}
        </button>
      </form>

      <p className="meta" style={{ marginTop: 10 }}>
        Jawaban hanya disusun dari ulasan yang Anda masukkan dan selalu menyertakan kutipannya.
        Jika buktinya tidak ada, sistem akan mengatakan tidak tahu.
      </p>
    </div>
  );
}
