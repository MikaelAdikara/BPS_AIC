/** Studi kasus: satu toko, ulasan asli, angka asli.
 *
 * Semua angka di sini berasal dari SATU analisis sungguhan atas 66 ulasan Shopee nyata (hasil
 * scraping sendiri, dianonimkan - data/samples/demo_shopee_asli.csv) yang dijalankan di server
 * demo pada 23 Agustus 2026. Tidak ada yang dibulatkan ke atas, dan dataset yang sama tersedia
 * satu klik di layar kerja supaya pembaca bisa mereproduksi hasilnya sendiri.
 */

const KARTU = [
  { urgensi: "tinggi", judul: "Periksa kualitas produk pada batch terbaru", n: "13 dari 66", skor: "28,9" },
  { urgensi: "tinggi", judul: "Perbaiki keterangan kesesuaian dengan deskripsi", n: "7 dari 66", skor: "14,7" },
  { urgensi: "tinggi", judul: "Tinjau kecepatan dan cara membalas pembeli", n: "7 dari 66", skor: "12,6" },
  { urgensi: "sedang", judul: "Tinjau proses pengiriman pesanan", n: "3 dari 66", skor: "6,0" },
  { urgensi: "rendah", judul: "Tinjau proses kemasan pesanan", n: "3 dari 66", skor: "4,7" },
];

export function CaseStudy({ onStart }) {
  return (
    <section className="kasus" id="studi-kasus" aria-labelledby="kasus-judul">
      <div className="section-head">
        <h2 id="kasus-judul">
          Diuji pada ulasan asli, <span className="soft">bukan data buatan</span>
        </h2>
        <p>
          Satu toko fesyen di Shopee, 66 ulasan nyata yang kami ambil dan anonimkan sendiri, rata-rata
          2,88 bintang. Inilah yang keluar - apa adanya, termasuk bagian yang tidak rapi.
        </p>
      </div>

      <div className="kasus__grid">
        <div className="kasus__angka">
          <div>
            <b>66</b>
            <span>ulasan asli, Okt 2025 - Agu 2026</span>
          </div>
          <div>
            <b>19</b>
            <span>di antaranya memuat keluhan (29%)</span>
          </div>
          <div>
            <b>7</b>
            <span>aspek yang dikeluhkan - dari 11 yang dikenali</span>
          </div>
          <div>
            <b>55 dtk</b>
            <span>waktu analisis di server 2 vCPU tanpa GPU</span>
          </div>
        </div>

        <div className="kasus__kartu">
          <div className="kasus__kartu-judul">Lima hal yang harus dikerjakan lebih dulu - terurut</div>
          <ol>
            {KARTU.map((k) => (
              <li key={k.judul} className={`kasus__item kasus__item--${k.urgensi}`}>
                <span className="kasus__badge">{k.urgensi}</span>
                <span className="kasus__teks">{k.judul}</span>
                <span className="kasus__n">{k.n}</span>
                <span className="kasus__skor">{k.skor}</span>
              </li>
            ))}
          </ol>
          <blockquote className="kasus__kutip">
            <p>"Kenyamanan: nyaman. Bahan: bagus. Desain: bagus - padahal bagus bahannya tp dpet barang zonk"</p>
            <footer>bukti kartu #1 · ulasan asli, 1/5 bintang · relevansi 0,70</footer>
          </blockquote>
        </div>
      </div>

      <div className="kasus__catat">
        <p>
          <b>Yang tidak rapi, dan sengaja tidak disembunyikan:</b> tebakan kategorinya "fashion" dengan
          keyakinan <em>sedang</em> (17 dari 66 ulasan cocok); dua kartu terbawah hanya bertumpu pada 3
          ulasan dan sistem sendiri melabelinya rendah; satu kutipan bukti dimulai dengan pujian sebelum
          keluhannya - persis bagaimana orang Indonesia menulis ulasan, dan persis kenapa ini sulit.
        </p>
        <button type="button" className="btn btn--primary" onClick={onStart}>
          Jalankan dataset yang sama ›
        </button>
      </div>
    </section>
  );
}
