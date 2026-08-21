/** Tab Detail: hal yang menarik tetapi bukan keputusan besok pagi.
 *
 * Dipisahkan dari tab Hasil justru supaya tab Hasil tetap pendek. Peluang dan sebaran aspek
 * berguna saat pemilik toko sedang menyusun promosi, bukan saat ia sedang memutuskan apa yang
 * harus dibenahi lebih dulu.
 */

import { AspectChart, OpportunityCard, VisualFindings } from "../insight.jsx";

export function DetailPanel({ result, focus = [] }) {
  const opportunities = result.opportunities ?? [];

  return (
    <div className="reading-col">
      <h3 className="sec-title">Peluang yang ditemukan</h3>
      {opportunities.length > 0 ? (
        opportunities.map((o) => <OpportunityCard key={o.aspect} opportunity={o} />)
      ) : (
        <div className="banner-grey">
          Belum ada aspek yang dipuji cukup konsisten untuk disebut peluang. Sistem tidak
          mengarang satu pun agar bagian ini terisi.
        </div>
      )}

      <VisualFindings findings={result.visual_findings} />

      <AspectChart aggregates={result.aspect_aggregates} focus={focus} />
    </div>
  );
}
