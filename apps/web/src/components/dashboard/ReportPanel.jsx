/** Laporan lengkap - satu gulungan, bukan tab bertumpuk.
 *
 * Sebelumnya hasil dipecah ke empat tab (Hasil, Detail, Tanya Jawab, Roadmap), dan bagian yang
 * ditambahkan sekarang akan menjadikannya tujuh. Tab yang berjumlah tujuh berhenti menjadi
 * navigasi: pengguna tidak lagi memilih, ia mencari - dan mencari di antara tujuh label
 * pendek lebih lambat daripada menggulir satu halaman yang tersusun.
 *
 * Jadi laporan menjadi satu permukaan yang digulir, dengan rel bagian yang menempel di
 * sampingnya. Tiga hal yang tersisa sebagai tab adalah tiga MODE yang berbeda, bukan tiga
 * bagian dari satu laporan: membaca laporan, bertanya kepadanya, dan melihat apa yang belum
 * dibangun.
 *
 * Bagian yang tidak punya data TIDAK dirender, dan namanya juga hilang dari rel. Kerangka
 * kosong berlabel "Per produk" pada berkas yang tidak punya kolom produk terbaca sebagai
 * kerusakan, bukan sebagai ketiadaan - dan rel yang menjanjikan bagian yang tidak ada saat
 * ditekan lebih buruk lagi.
 */

import { useEffect, useMemo, useRef, useState } from "react";

import { WARNING_TEXT } from "../../lib/format.js";
import { ActionCard, BenchmarkCard, DataQualityCard, OpportunityCard, VisualFindings } from "../insight.jsx";
import { SummaryHead } from "../report/Figures.jsx";
import { AspectSections } from "../report/Aspects.jsx";
import { PeriodChart } from "../report/Periods.jsx";
import { ProductTable } from "../report/Products.jsx";
import { RatingBands } from "../report/Ratings.jsx";

/** Satu bagian laporan. `id` dipakai rel sebagai sasaran lompatan. */
function Bagian({ id, judul, ket, children }) {
  return (
    <section className="lap__bagian" id={id} aria-labelledby={`${id}-judul`}>
      <div className="lap__kepala">
        <h3 id={`${id}-judul`}>{judul}</h3>
        {ket && <p className="meta">{ket}</p>}
      </div>
      {children}
    </section>
  );
}

/** Rel bagian yang menempel.
 *
 * Menyorot bagian yang sedang terbaca dengan IntersectionObserver, bukan dengan menghitung
 * `scrollY` pada setiap peristiwa gulir - penghitungan itu berjalan di utas utama pada tiap
 * frame gulir, dan di ponsel kelas menengah yang menjadi sasaran produk ini biayanya terlihat.
 *
 * `rootMargin` atas -45% membuat bagian dianggap aktif saat kepalanya melewati kira-kira
 * pertengahan layar, bukan saat piksel pertamanya menyentuh tepi atas. Tanpa itu, sorotan
 * melompat ke bagian berikutnya sementara mata masih membaca bagian sebelumnya.
 */
function Rel({ bagian }) {
  const [aktif, setAktif] = useState(bagian[0]?.id);
  const daftar = useRef(null);

  useEffect(() => {
    const nodes = bagian
      .map(({ id }) => document.getElementById(id))
      .filter(Boolean);
    if (!nodes.length) return undefined;

    const pengamat = new IntersectionObserver(
      (entries) => {
        const terlihat = entries.filter((e) => e.isIntersecting);
        if (terlihat.length) setAktif(terlihat[0].target.id);
      },
      { rootMargin: "-45% 0px -45% 0px", threshold: 0 }
    );
    nodes.forEach((n) => pengamat.observe(n));
    return () => pengamat.disconnect();
  }, [bagian]);

  // Di layar sempit relnya menggulir menyamping; butir aktif ditarik ke dalam pandangan
  // supaya ia tidak tertinggal di luar layar saat halaman digulir.
  //
  // Digulir dengan menyetel `scrollLeft` pada relnya sendiri, BUKAN dengan `scrollIntoView`.
  // Bukan selera: `scrollIntoView` menggulir leluhur pertama yang bisa digulir pada sumbu yang
  // diminta, dan di layar lebar relnya tersusun tegak sehingga tidak ada satu pun - yang
  // ditemukan berikutnya adalah dokumen. Akibatnya seluruh halaman bergeser ~22px ke samping
  // lalu terkunci di sana, karena `html { overflow-x: hidden }` menghapus bilah gulir yang
  // bisa dipakai menggeser balik. Menjaganya dengan memeriksa lebar pun tidak cukup: pada
  // render pertama relnya masih bertata letak sempit, jadi pemeriksaannya lolos sekali - satu
  // kali sudah cukup. Menyetel `scrollLeft` tidak punya jalan keluar ke dokumen sama sekali.
  useEffect(() => {
    const ol = daftar.current;
    if (!ol || ol.scrollWidth <= ol.clientWidth) return;
    const butir = ol.querySelector('[aria-current="true"]');
    if (!butir) return;
    const tengah = butir.offsetLeft - (ol.clientWidth - butir.offsetWidth) / 2;
    ol.scrollTo({ left: Math.max(0, tengah), behavior: "smooth" });
  }, [aktif]);

  return (
    <nav className="lap__rel" aria-label="Bagian laporan">
      <ol ref={daftar}>
        {bagian.map(({ id, judul }) => (
          <li key={id}>
            <a href={`#${id}`} aria-current={aktif === id ? "true" : undefined}>
              {judul}
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}

export function ReportPanel({
  result,
  category,
  onCategory,
  decisions,
  onDecide,
  onOpenEvidence,
}) {
  const punyaProduk = (result.products ?? []).length > 0;
  const punyaRiwayat = Boolean(result.period_history);
  const punyaBintang = Boolean(result.ratings);
  const peluang = result.opportunities ?? [];
  const benchmark = result.benchmark_by_category?.[category] ?? result.benchmark ?? [];

  // Rel dan isi digambar dari SATU daftar. Dua daftar terpisah adalah cara paling pasti
  // membuat rel menunjuk bagian yang sudah tidak dirender.
  //
  // Dimemo karena `Rel` memakainya sebagai dependensi efek yang memasang IntersectionObserver.
  // Larik yang dibangun ulang tiap render punya identitas baru tiap render, sehingga efeknya
  // membongkar lalu memasang kembali pengamatnya pada SETIAP render - termasuk render yang
  // dipicu pengamat itu sendiri saat menyorot bagian baru.
  const bagian = useMemo(
    () =>
      [
        { id: "lap-ringkas", judul: "Ringkasan", ada: true },
        { id: "lap-prioritas", judul: "Prioritas", ada: true },
        { id: "lap-aspek", judul: "Per aspek", ada: true },
        { id: "lap-produk", judul: "Per produk", ada: punyaProduk },
        { id: "lap-bintang", judul: "Sebaran bintang", ada: punyaBintang },
        { id: "lap-riwayat", judul: "Riwayat", ada: punyaRiwayat },
        { id: "lap-peluang", judul: "Peluang", ada: peluang.length > 0 },
        { id: "lap-banding", judul: "Benchmark", ada: benchmark.length > 0 },
        { id: "lap-mutu", judul: "Kualitas data", ada: Boolean(result.data_quality) },
      ].filter((b) => b.ada),
    [punyaProduk, punyaBintang, punyaRiwayat, peluang.length, benchmark.length, result.data_quality]
  );

  return (
    <div className="lap">
      <Rel bagian={bagian} />

      <div className="lap__isi">
        <Bagian id="lap-ringkas" judul="Ringkasan">
          <SummaryHead result={result} category={category} onCategory={onCategory} />
          {result.warnings?.map((w) => (
            <div key={w} className="banner-grey">
              {WARNING_TEXT[w] ?? w}
            </div>
          ))}
        </Bagian>

        <Bagian
          id="lap-prioritas"
          judul="Yang perlu dikerjakan lebih dulu"
          ket="Terurut menurut skor prioritas - dihitung dari frekuensi, keparahan, dan selisih terhadap kategori sejenis. Bukan menurut yang paling mudah dikerjakan."
        >
          {result.top_actions.length > 0 ? (
            result.top_actions.map((card, i) => (
              <ActionCard
                key={card.action_id}
                index={i}
                card={card}
                decision={decisions[card.action_id]}
                onDecide={onDecide}
                onOpenEvidence={onOpenEvidence}
              />
            ))
          ) : (
            <div className="banner-grey">
              Tidak ada keluhan yang cukup sering muncul untuk dijadikan prioritas. Itu kabar
              baik, tetapi periksa juga apakah data yang Anda masukkan sudah mewakili seluruh
              ulasan.
            </div>
          )}
        </Bagian>

        <Bagian
          id="lap-aspek"
          judul="Per aspek"
          ket="Seluruh aspek yang dikenali sistem, termasuk yang tidak disebut satu ulasan pun. Tekan satu baris untuk melihat dasar angkanya."
        >
          <AspectSections result={result} category={category} />
        </Bagian>

        {punyaProduk && (
          <Bagian
            id="lap-produk"
            judul="Per produk"
            ket="Dibaca dari kolom produk pada berkas yang Anda unggah. Tekan judul kolom untuk mengurutkan."
          >
            <ProductTable products={result.products} />
          </Bagian>
        )}

        {punyaBintang && (
          <Bagian
            id="lap-bintang"
            judul="Sebaran bintang"
            ket="Bukan sekadar berapa banyak per bintang - juga keluhan apa yang ada di dalam tiap pita."
          >
            <RatingBands ratings={result.ratings} />
          </Bagian>
        )}

        {punyaRiwayat && (
          <Bagian
            id="lap-riwayat"
            judul="Riwayat antar periode"
            ket="Dihitung dari kolom tanggal pada berkas Anda sendiri."
          >
            <PeriodChart history={result.period_history} />
          </Bagian>
        )}

        {peluang.length > 0 && (
          <Bagian
            id="lap-peluang"
            judul="Peluang yang ditemukan"
            ket="Aspek yang justru dipuji pembeli. Bahan untuk promosi - sistem sengaja tidak menuliskan materi iklannya."
          >
            {peluang.map((o) => (
              <OpportunityCard key={o.aspect} opportunity={o} />
            ))}
          </Bagian>
        )}

        {benchmark.length > 0 && (
          <Bagian id="lap-banding" judul="Dibanding kategori sejenis">
            <BenchmarkCard rows={benchmark} />
          </Bagian>
        )}

        {result.data_quality && (
          <Bagian
            id="lap-mutu"
            judul="Kualitas data"
            ket="Seberapa jauh hasil di atas layak dipercaya, dilihat dari data yang masuk."
          >
            <DataQualityCard quality={result.data_quality} />
            <VisualFindings findings={result.visual_findings} />
            <p className="meta">
              Model: {result.model_versions?.text} · mode {result.mode}
            </p>
          </Bagian>
        )}
      </div>
    </div>
  );
}
