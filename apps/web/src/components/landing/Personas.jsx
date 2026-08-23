/** "Untuk siapa" - lima skenario pemakaian yang konkret, ditulis dari sudut pandang orangnya.
 *
 * Setiap kartu menjawab tiga hal yang sama: siapa, apa yang ia unggah, apa yang ia dapat. Tidak
 * ada persona yang dijanjikan fitur yang belum ada; skenario pendamping UMKM dan merek multi-SKU
 * ditulis dengan batasnya.
 */

const SKENARIO = [
  {
    siapa: "Penjual fesyen di Shopee & Tokopedia",
    ciri: "2 toko · 300 ulasan/bulan · sendirian",
    unggah: "Tangkapan layar halaman ulasan dari kedua aplikasi, difoto dari HP.",
    dapat: "Satu daftar prioritas untuk kedua toko sekaligus - misal \"keluhan ukuran 3× lebih sering dari rata-rata kategori\" - plus draf balasan untuk ulasan negatifnya.",
  },
  {
    siapa: "Warung makanan yang jualan lewat GoFood & ShopeeFood",
    ciri: "Ulasan pendek, penuh singkatan",
    unggah: "Tempel ulasan langsung, satu per baris - tidak perlu berkas.",
    dapat: "Aspek rasa, porsi, kemasan, dan pengiriman dipisahkan; terlihat bahwa \"kemasan bocor\" muncul di 1 dari 8 ulasan, bukan sekadar terasa sering.",
  },
  {
    siapa: "Reseller elektronik dengan 40 SKU",
    ciri: "Ulasan bercampur antar produk",
    unggah: "Ekspor CSV; kolom produk ikut dipetakan.",
    dapat: "Laporan per produk - SKU mana yang menyumbang keluhan \"tidak sesuai deskripsi\" - dan arsip bulanan untuk dibandingkan setelah deskripsinya diperbaiki.",
  },
  {
    siapa: "Pendamping UMKM dari dinas atau inkubator",
    ciri: "Mendampingi 30 pelaku usaha",
    unggah: "Berkas per binaan, satu per satu - tidak ada akun, tidak ada data yang disimpan di server.",
    dapat: "Bahan pendampingan yang konkret untuk tiap binaan: tiga hal yang harus dikerjakan, dengan bukti kutipan yang bisa ditunjukkan langsung ke pemilik toko.",
  },
  {
    siapa: "Merek menengah dengan tim CS kecil",
    ciri: "Ribuan ulasan, butuh tren",
    unggah: "CSV per bulan (maksimal 400 ulasan per analisis di server demo; lebih besar di mesin sendiri).",
    dapat: "Perbandingan antar-bulan yang jujur soal signifikansinya - selisih kecil ditulis \"belum berarti\", bukan dirayakan. Batasnya: belum ada integrasi langsung ke marketplace.",
  },
];

export function Personas() {
  return (
    <section className="persona" id="untuk-siapa" aria-labelledby="persona-judul">
      <div className="section-head">
        <h2 id="persona-judul">
          Untuk siapa, <span className="soft">dan apa yang mereka dapat</span>
        </h2>
        <p>Lima skenario nyata. Semuanya memakai alur yang sama - yang berbeda hanya apa yang diunggah.</p>
      </div>
      <div className="persona__grid">
        {SKENARIO.map((s) => (
          <article className="persona__kartu" key={s.siapa}>
            <h3>{s.siapa}</h3>
            <span className="persona__ciri">{s.ciri}</span>
            <dl>
              <dt>Yang diunggah</dt>
              <dd>{s.unggah}</dd>
              <dt>Yang didapat</dt>
              <dd>{s.dapat}</dd>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}
