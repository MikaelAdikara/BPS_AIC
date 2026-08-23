/** Pemandu langkah pertama - untuk pengguna yang belum pernah memakai alat seperti ini.
 *
 * Muncul sekali saat layar kerja pertama kali dibuka (ditandai di localStorage), tiga langkah,
 * bahasa sehari-hari, bisa dilewati kapan saja dan dibuka lagi lewat tombol "Panduan". Ia tidak
 * menutupi kontrol apa pun dan tidak menahan pengguna yang sudah tahu - satu klik "Lewati" dan ia
 * tidak kembali sampai diminta.
 */

import { useEffect, useState } from "react";
import { hashParam } from "../../lib/hooks.js";

const KEY = "ulasin.panduan.v1";

const LANGKAH = [
  {
    judul: "Masukkan ulasan Anda - cara apa pun yang paling mudah",
    isi: "Tempel teksnya, unggah berkas, atau yang paling gampang dari HP: foto/tangkapan layar halaman ulasan toko Anda. Tidak perlu berkas apa pun.",
    tip: "Belum punya data? Tekan \"Coba dengan data contoh\" - itu ulasan asli dari sebuah toko.",
  },
  {
    judul: "Pilih jenis toko Anda, lalu tekan Analisis",
    isi: "Jenis toko dipakai untuk membandingkan Anda dengan toko sejenis. Analisis biasanya kurang dari satu menit - ada penunjuk progresnya.",
    tip: "Data Anda hanya hidup selama halaman ini terbuka. Tutup halaman, hilang.",
  },
  {
    judul: "Baca tiga kartu teratas, periksa buktinya",
    isi: "Yang paling atas paling mendesak. Tiap kartu membawa kutipan ulasan aslinya. Tekan \"Bagaimana angka ini dihitung?\" kalau ingin melihat cara sistem menghitungnya.",
    tip: "Tekan \"Terima\" atau \"Tolak\" di tiap kartu - yang memutuskan tetap Anda.",
  },
];

export function FirstRunGuide() {
  const [buka, setBuka] = useState(false);
  const [i, setI] = useState(0);

  useEffect(() => {
    // Pengguna yang datang dari halaman panduan (#/analisis?masukan=...) baru saja membaca
    // langkah-langkahnya; membuka pemandu lagi di atas tab yang ia tuju hanya menghalangi.
    // Tidak ditandai "sudah dilihat" - kunjungan biasa berikutnya tetap mendapatkannya.
    if (hashParam("masukan")) return;
    try {
      if (!window.localStorage?.getItem(KEY)) setBuka(true);
    } catch {
      /* tanpa localStorage: tampilkan saja sekali */
      setBuka(true);
    }
  }, []);

  const tutup = () => {
    try {
      window.localStorage?.setItem(KEY, "1");
    } catch {
      /* abaikan */
    }
    setBuka(false);
    setI(0);
  };

  return (
    <>
      <button type="button" className="panduan__tombol" onClick={() => { setI(0); setBuka(true); }}>
        <span aria-hidden="true">?</span> Panduan
      </button>

      {buka && (
        <div className="panduan" role="dialog" aria-modal="false" aria-labelledby="panduan-judul">
          <div className="panduan__kepala">
            <span className="panduan__langkah">Langkah {i + 1} dari {LANGKAH.length}</span>
            <button type="button" className="panduan__lewati" onClick={tutup}>
              Lewati
            </button>
          </div>
          <h3 id="panduan-judul">{LANGKAH[i].judul}</h3>
          <p>{LANGKAH[i].isi}</p>
          <p className="panduan__tip">{LANGKAH[i].tip}</p>
          {i === 0 && (
            <a href="#/panduan" className="dari-mana">
              Bingung di mana ulasan toko Anda berada? Lihat panduan per aplikasi ›
            </a>
          )}
          <div className="panduan__kaki">
            <div className="panduan__titik" aria-hidden="true">
              {LANGKAH.map((_, j) => (
                <i key={j} className={j === i ? "is-aktif" : ""} />
              ))}
            </div>
            {i < LANGKAH.length - 1 ? (
              <button type="button" className="btn btn--primary" onClick={() => setI(i + 1)}>
                Selanjutnya ›
              </button>
            ) : (
              <button type="button" className="btn btn--primary" onClick={tutup}>
                Mulai ›
              </button>
            )}
          </div>
        </div>
      )}
    </>
  );
}
