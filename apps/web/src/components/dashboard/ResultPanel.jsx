/** Tab Hasil: apa yang harus dikerjakan lebih dulu, beserta dasar angkanya.
 *
 * Dua kolom di layar lebar. Pembagiannya bukan estetika - kedua sisi dibaca dengan cara yang
 * berbeda. Kartu aksi adalah kalimat yang dibaca berurutan sampai habis, jadi ia tinggal di
 * kolom utama dengan panjang baris yang terjaga. Ringkasan dan skor kualitas adalah angka
 * yang dipindai sekali lalu dijadikan rujukan; menaruhnya di rel kanan yang menempel berarti
 * angka itu tetap terlihat sambil pengguna menyusuri kartu, alih-alih tergulir hilang di atas.
 *
 * Benchmark tetap di kolom utama meski isinya angka: ia tabel empat kolom, dan rel 340px
 * memaksanya digulir menyamping.
 *
 * Urutan DOM-nya rel dulu, baru kolom utama. Di layar sempit keduanya bertumpuk apa adanya -
 * ringkasan lebih dulu, persis urutan membaca yang benar - dan penempatan kolom pada layar
 * lebar diurus grid, bukan urutan markup.
 */

import { useState } from "react";
import { WARNING_TEXT } from "../../lib/format.js";
import { ActionCard, BenchmarkCard, DataQualityCard, Narrative } from "../insight.jsx";

export function ResultPanel({ result, decisions, onDecide, onOpenEvidence, onAsk }) {
  const [question, setQuestion] = useState("");

  return (
    <>
      <div className="result-grid">
        <aside className="result-side">
          <section className="panel">
            <div className="panel-title">Ringkasan</div>
            <Narrative text={result.summary.executive_summary_text} className="body" />
            {result.warnings?.map((w) => (
              <div key={w} className="banner-grey" style={{ margin: "10px 0 0" }}>
                {WARNING_TEXT[w] ?? w}
              </div>
            ))}
          </section>

          <DataQualityCard quality={result.data_quality} />
        </aside>

        <div className="result-main">
          {result.top_actions.length > 0 ? (
            <>
              <h3 className="sec-title">Yang perlu dikerjakan lebih dulu</h3>
              {result.top_actions.map((card, i) => (
                <ActionCard
                  key={card.action_id}
                  index={i}
                  card={card}
                  decision={decisions[card.action_id]}
                  onDecide={onDecide}
                  onOpenEvidence={onOpenEvidence}
                />
              ))}
            </>
          ) : (
            <div className="banner-grey">
              Tidak ada keluhan yang cukup sering muncul untuk dijadikan prioritas. Itu kabar baik,
              tetapi periksa juga apakah data yang Anda masukkan sudah mewakili seluruh ulasan.
            </div>
          )}

          <BenchmarkCard rows={result.benchmark} />
        </div>
      </div>

      <form
        className="qabox qabox--foot"
        onSubmit={(e) => {
          e.preventDefault();
          const asked = question.trim();
          if (!asked) return;
          setQuestion("");
          onAsk(asked);
        }}
      >
        <label className="sr-only" htmlFor="ask-here">
          Tanya tentang hasil ini
        </label>
        <span aria-hidden="true">✎</span>
        <input
          id="ask-here"
          value={question}
          maxLength={500}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Tanya tentang hasil ini…"
        />
        <button className="btn btn--primary" type="submit" disabled={!question.trim()}>
          Tanya
        </button>
      </form>

      <p className="meta" style={{ marginTop: 16 }}>
        Model: {result.model_versions?.text} · mode {result.mode}
      </p>
    </>
  );
}
