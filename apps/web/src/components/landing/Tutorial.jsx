/** Tutorial 60 detik - ditulis untuk orang yang tidak akrab dengan istilah "CSV", "ekspor",
 *  atau "unggah". Setiap langkah satu kalimat perintah, satu kalimat penenang. Jalur yang
 *  ditonjolkan adalah yang paling mudah bagi pengguna ponsel: tangkapan layar / foto - tidak
 *  perlu tahu di mana berkas disimpan. */

const LANGKAH = [
  {
    n: "1",
    judul: "Buka halaman ulasan toko Anda di HP",
    isi: "Di aplikasi Shopee/Tokopedia, masuk ke toko Anda lalu ke bagian ulasan. Tidak perlu mengunduh apa pun.",
    tenang: "Kalau punya berkas ekspor, boleh dipakai - tapi tidak wajib.",
  },
  {
    n: "2",
    judul: "Tangkap layarnya, atau foto layarnya",
    isi: "Tekan tombol tangkapan layar di HP, beberapa kali sambil menggulir. Atau buka Ulasin di HP lain dan foto layarnya langsung dengan tombol kamera.",
    tenang: "Sistem membaca teksnya sendiri. Anda tinggal memeriksa hasil bacaannya - salah huruf bisa diperbaiki.",
  },
  {
    n: "3",
    judul: "Tekan \"Analisis\", tunggu sebentar",
    isi: "Biasanya kurang dari satu menit. Ada penunjuk progresnya, jadi Anda tahu apa yang sedang dikerjakan.",
    tenang: "Data Anda tidak disimpan di mana pun setelah halaman ditutup.",
  },
  {
    n: "4",
    judul: "Baca tiga hal teratas - itu saja dulu",
    isi: "Yang paling atas paling mendesak. Tiap kartu membawa kutipan ulasan aslinya, jadi Anda tidak perlu percaya - tinggal lihat sendiri.",
    tenang: "Tekan \"Terima\" atau \"Tolak\" di tiap kartu. Yang memutuskan tetap Anda, bukan sistem.",
  },
];

export function Tutorial() {
  return (
    <section className="tutor" id="cara-pakai" aria-labelledby="tutor-judul">
      <div className="section-head">
        <h2 id="tutor-judul">
          Cara pakai dalam 60 detik, <span className="soft">tanpa istilah teknis</span>
        </h2>
        <p>
          Kalau Anda bisa mengirim foto lewat WhatsApp, Anda bisa memakai ini. Tidak perlu akun, tidak
          perlu memasang apa pun.
        </p>
      </div>
      <ol className="tutor__langkah">
        {LANGKAH.map((l) => (
          <li key={l.n} className="tutor__item">
            <span className="tutor__no" aria-hidden="true">
              {l.n}
            </span>
            <div>
              <h3>{l.judul}</h3>
              <p>{l.isi}</p>
              <p className="tutor__tenang">{l.tenang}</p>
            </div>
          </li>
        ))}
      </ol>
      <p className="tutor__nota">
        Bingung di tengah jalan? Di dalam aplikasi ada tombol <b>Panduan</b> yang menunjukkan tiga
        langkah ini lagi - dan kotak tanya-jawab di pojok halaman ini menjawab pertanyaan umum tanpa
        perlu membaca apa pun.
      </p>
    </section>
  );
}
