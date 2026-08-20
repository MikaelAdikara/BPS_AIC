/** Langkah kedua: progres yang mengikuti waktu nyata.
 *
 * Versi sebelumnya memajukan tahapan setiap 900 ms tanpa melihat apa pun. Untuk 66 ulasan itu
 * berarti batangnya penuh di detik ke-2,7 lalu berdiri di 100% selama dua puluh detik sisanya -
 * dan batang yang penuh sambil tidak terjadi apa-apa adalah cara tercepat membuat orang mengira
 * halamannya menggantung. Persentase yang tidak jujur lebih buruk daripada tidak ada persentase.
 *
 * Sekarang angkanya diturunkan dari waktu yang benar-benar berjalan, memakai kurva yang
 * MENDEKATI - tidak pernah mencapai - 100%. Hanya kedatangan jawaban dari server yang membawanya
 * ke 100%. Kalau tebakannya meleset, yang terjadi cuma batang yang merayap makin pelan, bukan
 * batang penuh yang berbohong.
 *
 * Ini satu-satunya momen bergerak yang diorkestrasi di seluruh aplikasi. Alasannya bukan hiasan:
 * analisis nyata bisa berjalan puluhan detik, dan spinner yang berputar tanpa arah tidak memberi
 * tahu apa pun tentang apakah sistem masih bekerja.
 */

export const STAGES = [
  "Membaca teks ulasan",
  "Mengambil bukti pendukung",
  "Mengelompokkan masalah",
  "Menyusun rekomendasi",
];

/* Batas bawah setiap tahap pada kurva progres. Bukan pembagian rata: mengambil bukti pendukung
 * (menghitung embedding tiap ulasan) memakan sebagian besar waktu, jadi ia juga menempati
 * sebagian besar batang. */
const AMBANG_TAHAP = [0, 0.16, 0.72, 0.9];

/* Perkiraan lama analisis = biaya tetap + biaya per ulasan.
 *
 * Diukur pada mesin pengembang 12 vCPU, embedding BGE-M3, batch disusun menurut panjang teks:
 * 10 ulasan 1,6 detik, 66 ulasan 10,3 detik - garis lurus dengan kemiringan ~0,15 detik per
 * ulasan dan biaya tetap yang nyaris nol.
 *
 * Angka di bawah sengaja sedikit di atas garis itu. Perkiraan yang meleset ke bawah tidak
 * merusak apa pun - kurvanya melambat mendekati plafon dan kalimat "lebih lama dari perkiraan"
 * muncul, keduanya jujur. Perkiraan yang terlalu longgar justru buruk: batangnya masih
 * merangkak di 40% padahal jawabannya sudah datang.
 *
 * Perkiraan ini TIDAK dapat mengetahui perangkat kerasnya. VM 2 vCPU dan mesin yang memuat
 * checkpoint IndoBERT (bukan leksikon) sama-sama lebih lambat; di sana kalimat "lebih lama
 * dari perkiraan" memang akan muncul, dan itulah gunanya. */
const BIAYA_TETAP_DETIK = 1.2;
const PER_ULASAN_DETIK = 0.15;

export function estimateSeconds(count) {
  return BIAYA_TETAP_DETIK + PER_ULASAN_DETIK * Math.max(count, 1);
}

/* Plafon sebelum jawaban datang. Sisanya sengaja ditinggal kosong: selama masih ada yang
 * ditunggu, batangnya tidak boleh terlihat selesai. */
const PLAFON = 0.96;

/** Kurva jenuh. Naik cepat di awal - saat memang paling banyak yang terjadi - lalu makin
 *  melambat, sehingga terlambat sedikit maupun terlambat banyak sama-sama terbaca sebagai
 *  "masih berjalan" alih-alih "macet". */
export function progressFraction(elapsed, estimate) {
  const tau = Math.max(estimate, 1) / 2.2;
  return PLAFON * (1 - Math.exp(-Math.max(elapsed, 0) / tau));
}

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

const detik = (n) => `${Math.max(0, Math.round(n))} detik`;

export function ProcessingStep({ elapsed = 0, estimate = 20, count = 0 }) {
  const fraction = progressFraction(elapsed, estimate);
  const percent = Math.round(fraction * 100);
  const stage = Math.max(0, AMBANG_TAHAP.filter((t) => fraction >= t).length - 1);
  const molor = elapsed > estimate * 1.35;

  return (
    <>
      <div className="panel">
        <div className="panel-title">
          Progres
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
        <p className="meta proc__line">
          <span>{STAGES[stage]}…</span>
          {/* Waktu berjalan ditampilkan apa adanya. Ia satu-satunya angka di layar ini yang
              benar-benar terukur, dan ia yang membuktikan sistemnya masih hidup. */}
          <span className="proc__clock">{detik(elapsed)}</span>
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

      {/* Perkiraannya disebut sebagai perkiraan, bukan janji. Begitu terlampaui jauh, kalimatnya
          berganti - karena pada titik itu yang dibutuhkan pengguna bukan angka lagi, melainkan
          kepastian bahwa menunggu masih ada gunanya. */}
      <p className="meta" aria-live="polite">
        {molor
          ? "Lebih lama dari perkiraan. Analisisnya masih berjalan - biarkan halaman ini terbuka."
          : `Perkiraan ${detik(estimate)} untuk ${count || "sekian"} ulasan.`}
      </p>
    </>
  );
}
