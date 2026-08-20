/** Langkah kedua: checklist yang maju bertahap.
 *
 * Ini satu-satunya momen bergerak yang diorkestrasi di seluruh aplikasi. Alasannya bukan
 * hiasan: analisis nyata pada CPU dua inti bisa berjalan lebih dari satu menit, dan spinner
 * yang berputar tanpa arah tidak memberi tahu apa pun tentang apakah sistem masih bekerja.
 */

export const STAGES = [
  "Membaca teks ulasan",
  "Mengambil bukti pendukung",
  "Mengelompokkan masalah",
  "Menyusun rekomendasi",
];

const Check = () => (
  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M5 12.5l4.5 4.5L19 7.5"
      stroke="#fff"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export function ProcessingStep({ stage }) {
  const percent = Math.round(((stage + 1) / STAGES.length) * 100);

  return (
    <>
      <div className="panel">
        <div className="panel-title">
          Progres{" "}
          <em>
            <span className="stat">{percent}</span>%
          </em>
        </div>
        <div
          className="track track--lg"
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Progres analisis"
        >
          <div className="fill fill--blue" style={{ width: `${percent}%` }} />
        </div>
        <p className="meta" style={{ marginTop: 9 }}>
          {STAGES[stage]}…
        </p>
      </div>

      <div className="panel">
        <div className="panel-title">Tahapan</div>
        {STAGES.map((s, i) => {
          const state = i < stage ? "done" : i === stage ? "active" : "pending";
          return (
            <div key={s} className={`check-row ${state}`} style={{ animationDelay: `${i * 0.12}s` }}>
              <span className={`check-circle ${state}`}>{state === "done" && <Check />}</span>
              <span className="lbl">{s}</span>
            </div>
          );
        })}
      </div>

      <p className="meta">Biasanya kurang dari satu menit untuk 100 ulasan.</p>
    </>
  );
}
