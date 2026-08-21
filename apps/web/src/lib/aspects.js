/** Daftar aspek per kategori, dan pertanyaan yang disarankan di tab Tanya Jawab.
 *
 * Berkas ini dulu bernama `profile.js` dan menyimpan empat isian yang ditanyakan di layar
 * unggah: nama toko, produk, kategori, dan "yang paling ingin Anda tahu". Keempatnya dicabut,
 * masing-masing karena alasannya sendiri:
 *
 *   nama toko  Tidak ada di berkas ekspor marketplace mana pun - ekspor ulasan berisi ulasan
 *              ATAS produk Anda, dan tidak pernah menyebutkan nama toko Anda sendiri karena
 *              Anda sudah tahu. Jadi tidak ada yang bisa dideteksi, dan yang sebenarnya perlu
 *              diperbaiki bukan cara menanyakannya melainkan kebutuhannya: laporan analitik
 *              tidak menyapa pembacanya dengan nama, ia menunjukkan angkanya.
 *   produk     Sudah ada di berkas, di kolom yang bahkan sudah dipetakan di layar unggah.
 *              Menanyakannya lagi tepat setelah membaca 66 baris berisi nama produk terbaca
 *              seperti sistem yang tidak membaca apa-apa.
 *   kategori   Sekarang ditebak `detect_category()` di backend lalu DITAMPILKAN sebagai chip
 *              yang bisa diganti di kepala laporan. Deteksi yang terlihat dan bisa dikoreksi
 *              lebih baik daripada pertanyaan yang menghalangi, dan jauh lebih baik daripada
 *              deteksi diam-diam.
 *   fokus      Kehilangan tugasnya. Ia dulu menahan aspek pilihan pengguna tetap tampil di
 *              grafik yang dipotong enam baris; sekarang SELURUH aspek punya bagiannya
 *              sendiri, termasuk yang tidak disebut satu ulasan pun.
 *
 * Yang tersisa dari berkas lama adalah bagian yang tetap dibutuhkan: daftar aspek per
 * kategori, karena laporan menyebutkan aspek yang NOL sebutan - dan aspek yang nol sebutan,
 * menurut definisinya, tidak ada di dalam data yang dikembalikan backend.
 */

/** Aspek yang aktif per kategori - salinan `configs/taxonomy.yaml` (status FROZEN Fase 0).
 *
 * Tetap disalin, bukan diambil dari API, dan tetap dijaga `aspects.test.js` yang membaca
 * `configs/taxonomy.yaml` langsung lalu membandingkannya kategori demi kategori. Salinan tanpa
 * penjaga akan menyimpang, dan menyimpangnya senyap: tidak ada yang gagal, hanya bagian "belum
 * disebut sama sekali" yang diam-diam berhenti menyebutkan satu aspek.
 */
const UNIVERSAL = [
  "kualitas_produk",
  "kesesuaian_deskripsi",
  "harga_value",
  "kemasan",
  "pengiriman",
  "pelayanan_penjual",
  "ukuran_varian",
];

const PER_KATEGORI = {
  fashion: ["kelengkapan", "keaslian"],
  food_beverage: ["rasa_kualitas_makanan"],
  craft: ["kelengkapan", "keaslian", "kemudahan_penggunaan"],
  electronics: ["kelengkapan", "keaslian", "kemudahan_penggunaan"],
  other: ["kelengkapan", "keaslian", "kemudahan_penggunaan"],
};

/** Daftar aspek yang berlaku untuk satu kategori. */
export function aspekUntuk(category) {
  return [...UNIVERSAL, ...(PER_KATEGORI[category] ?? PER_KATEGORI.other)];
}

/* Satu pertanyaan per aspek, ditulis sebagaimana pemilik toko menanyakannya - bukan
 * "Bagaimana performa aspek pengiriman?" melainkan "Bagaimana pendapat pembeli tentang
 * pengiriman?". Pertanyaan yang berbunyi seperti kolom basis data tidak pernah diklik. */
const PERTANYAAN = {
  kualitas_produk: "Apa yang paling sering dikeluhkan soal kualitas produknya?",
  kesesuaian_deskripsi: "Apakah barang yang datang sesuai dengan deskripsinya?",
  harga_value: "Menurut pembeli, harganya sepadan atau tidak?",
  kemasan: "Bagaimana pendapat pembeli tentang kemasannya?",
  pengiriman: "Bagaimana pendapat pembeli tentang pengiriman?",
  pelayanan_penjual: "Bagaimana pembeli menilai respons dan pelayanan toko?",
  ukuran_varian: "Apakah ada masalah dengan ukuran atau varian?",
  rasa_kualitas_makanan: "Apa komentar pembeli tentang rasanya?",
  kelengkapan: "Apakah ada pesanan yang datang tidak lengkap?",
  keaslian: "Apakah ada pembeli yang meragukan keaslian produknya?",
  kemudahan_penggunaan: "Menurut pembeli, produknya mudah dipakai atau tidak?",
};

/* Berlaku untuk toko mana pun, dipakai melengkapi sampai empat. */
const UMUM = [
  "Apa keluhan yang paling sering muncul?",
  "Bagaimana dibanding rata-rata kategori sejenis?",
  "Aspek apa yang justru dipuji pembeli?",
];

const MAX_SARAN = 4;

/** Pertanyaan yang disarankan, disusun dari apa yang DATANYA keluhkan.
 *
 * Sebelumnya disusun dari aspek yang ditandai pengguna sebelum ia melihat apa pun - tebakan
 * yang dibuat tepat pada saat ia paling sedikit tahu. Sekarang urutannya datang dari
 * `aspect_aggregates`, jadi pertanyaan yang ditawarkan adalah pertanyaan tentang masalah yang
 * benar-benar ada di datanya.
 *
 * Yang sengaja TIDAK berubah: ini hanya menyusun SARAN. Urutan Action Card tetap berasal dari
 * `priority_score`, dan tidak ada di berkas ini yang menyentuhnya.
 */
export function pertanyaanUntuk(aggregates = []) {
  const berkeluhan = [...aggregates]
    .filter((a) => a.negative_count > 0)
    .sort((a, b) => b.negative_count - a.negative_count)
    .map((a) => PERTANYAAN[a.aspect])
    .filter(Boolean);

  const unik = [...new Set(berkeluhan)];
  return [...unik, ...UMUM.filter((q) => !unik.includes(q))].slice(0, MAX_SARAN);
}
