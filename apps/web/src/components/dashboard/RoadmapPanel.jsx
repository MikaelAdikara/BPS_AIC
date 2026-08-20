/** Tab Roadmap - daftar apa yang BELUM ada, lengkap dengan alasannya.
 *
 * Bentuknya rel vertikal, bukan deretan kartu. Butir-butirnya memang berurutan: yang kedua
 * menunggu yang pertama selesai, dan dua terakhir belum tentu dikerjakan sama sekali. Deretan
 * kartu seragam menghapus urutan itu - kelimanya terbaca sama-sama akan datang.
 *
 * Layar ini tetap tidak dipoles seperti tab lain. Yang belum dikomit bergaris putus dan tanpa
 * isian, supaya sekilas pun terbaca sebagai "belum", bukan sebagai fitur yang dipromosikan.
 */

import { ROADMAP, ROADMAP_STAGES } from "../../content/roadmap.js";

export function RoadmapPanel() {
  return (
    <div className="reading-col">
      <p className="body" style={{ marginBottom: 24, maxWidth: "68ch" }}>
        Beberapa kemampuan berikut belum dibangun pada versi ini. Daftarnya ditulis apa adanya
        supaya tidak ada kemampuan yang tampak dijanjikan padahal belum benar-benar ada. Makin ke
        bawah, makin belum pasti.
      </p>

      <ol className="rmap">
        {ROADMAP_STAGES.map(([stage, label]) => {
          const items = ROADMAP.filter((item) => item.stage === stage);
          if (!items.length) return null;
          return (
            <li key={stage}>
              {/* Judul kelompok memakai `aria-hidden` pada relnya saja; teksnya sendiri tetap
                  dibaca, karena "menunggu prasyarat" adalah informasi, bukan hiasan. */}
              <h3 className="rmap__group">{label}</h3>
              <ol className="rmap__items">
                {items.map((item) => (
                  <li className={`rstop rstop--${stage}`} key={item.id}>
                    <span className="rstop__node" aria-hidden="true" />
                    <article className="rstop__card">
                      <div className="rstop__head">
                        <h4 className="rstop__title">{item.title}</h4>
                        <span className="rstop__tag">{item.status}</span>
                      </div>
                      <p className="rstop__body">{item.body}</p>
                      {item.blockedBy && (
                        <span className="rstop__blocked">
                          Menunggu: {item.blockedBy}
                        </span>
                      )}
                    </article>
                  </li>
                ))}
              </ol>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
