/** Tab Roadmap - daftar apa yang BELUM ada, lengkap dengan alasannya.
 *
 * Layar ini sengaja tidak dipoles seperti tab lain: kartunya bergaris putus-putus dan tanpa
 * warna aksen, supaya sekilas pun terbaca sebagai "belum", bukan sebagai fitur yang sedang
 * dipromosikan.
 */

import { ROADMAP } from "../../content/roadmap.js";

export function RoadmapPanel() {
  return (
    <>
      <p className="body" style={{ marginBottom: 20 }}>
        Beberapa kemampuan berikut belum dibangun pada versi ini. Daftarnya ditulis apa adanya
        supaya tidak ada kemampuan yang tampak dijanjikan padahal belum benar-benar ada.
      </p>

      {ROADMAP.map((item) => (
        <article className="future" key={item.id}>
          <span className="future__tag">{item.status}</span>
          <h4>{item.title}</h4>
          <p>{item.body}</p>
        </article>
      ))}
    </>
  );
}
