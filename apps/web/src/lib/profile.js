/** Profil toko - keterangan yang diberikan pengguna tentang dirinya sebelum menganalisis.
 *
 * Empat isian, dan hanya satu yang wajib. Yang penting bukan jumlahnya melainkan bahwa tiap
 * isian punya akibat yang bisa ditunjuk. Isian yang tidak mengubah apa pun adalah cara
 * tercepat membuat orang berhenti mengisi formulir:
 *
 *   `category`  dikirim pada tiap ulasan. Menentukan baseline pembanding yang dipakai
 *               `compare_category_baseline()`, dan menentukan daftar aspek di `focus`.
 *   `product`   dikirim sebagai `product_name` pada ulasan yang belum membawanya sendiri,
 *               sehingga kutipan bukti menyebut produk mana yang dibicarakan.
 *   `store`     TIDAK pernah dikirim ke server. Murni sapaan di layar - judul dan avatar.
 *   `focus`     TIDAK pernah dikirim ke server. Menyusun pertanyaan yang disarankan di tab
 *               Tanya Jawab, dan menahan aspek pilihan itu tetap tampil di grafik sebaran.
 *
 * Yang sengaja TIDAK dilakukan `focus`: mengubah urutan Action Card. Urutannya berasal dari
 * `priority_score` yang dihitung dari frekuensi, keparahan, dan keyakinan - menaikkan aspek
 * ke atas hanya karena pengguna menandainya berarti memberitahunya bahwa yang paling
 * mendesak adalah yang sudah ia curigai. Itu membalik arah produknya.
 */

/** Aspek yang aktif per kategori - salinan `configs/taxonomy.yaml` (status FROZEN Fase 0).
 *
 * Disalin, bukan diambil dari API, karena daftar ini dibutuhkan SEBELUM ada analisis: pengguna
 * memilih fokusnya di layar unggah, saat backend belum pernah dihubungi. Konsekuensinya daftar
 * ini bisa menyimpang dari config, dan itu ditangkap oleh `profile.test.js` yang membaca
 * `configs/taxonomy.yaml` langsung lalu membandingkannya baris demi baris.
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

/** Batas tiga, bukan tanpa batas.
 *
 * Fokus yang mencakup segalanya bukan fokus, dan akibat nyatanya terlihat di tab Tanya Jawab:
 * sebelas pertanyaan yang disarankan bukan lagi saran, melainkan daftar yang harus dibaca
 * dulu. Tiga muat dalam satu tarikan mata dan tetap menyisakan pilihan. */
export const MAX_FOKUS = 3;

export const PROFIL_AWAL = { category: "fashion", store: "", product: "", focus: [] };

/** Daftar aspek yang boleh dipilih sebagai fokus untuk satu kategori. */
export function aspekUntuk(category) {
  return [...UNIVERSAL, ...(PER_KATEGORI[category] ?? PER_KATEGORI.other)];
}

/** Perbarui profil sambil menjaga `focus` tetap sah.
 *
 * Berganti kategori dapat menonaktifkan aspek yang sudah ditandai - toko fesyen yang menandai
 * "keaslian" lalu pindah ke Makanan & Minuman. Membiarkannya tersimpan diam-diam menghasilkan
 * pertanyaan tentang keaslian pada toko makanan, dan pengguna tidak pernah melihat chip yang
 * menyebabkannya karena chipnya sudah tidak ada di layar.
 */
export function ubahProfil(profil, perubahan) {
  const next = { ...profil, ...perubahan };
  if (perubahan.category && perubahan.category !== profil.category) {
    const sah = new Set(aspekUntuk(next.category));
    next.focus = next.focus.filter((a) => sah.has(a));
  }
  return next;
}

export function pilihFokus(profil, aspek) {
  if (profil.focus.includes(aspek)) {
    return { ...profil, focus: profil.focus.filter((a) => a !== aspek) };
  }
  if (profil.focus.length >= MAX_FOKUS) return profil;
  return { ...profil, focus: [...profil.focus, aspek] };
}

/* Kata yang dibuang saat menyusun inisial. Hampir setiap nama toko Indonesia diawali salah
 * satunya, dan "Toko Bu Rina" yang jadi "TB" menyapa seluruh penggunanya dengan huruf yang
 * sama. Kalau setelah disaring tidak ada kata tersisa, penyaringannya diabaikan - "Toko Toko"
 * tetap harus menghasilkan sesuatu. */
const KATA_UMUM = new Set(["toko", "cv", "pt", "ud", "the", "olshop", "store", "shop"]);

/** Dua huruf untuk avatar. Tanpa nama toko, "OU" - Owner UMKM, sapaan bawaan layar ini. */
export function inisial(nama) {
  const kata = String(nama ?? "").trim().split(/\s+/).filter(Boolean);
  if (!kata.length) return "OU";
  const inti = kata.filter((k) => !KATA_UMUM.has(k.toLowerCase()));
  const dipakai = (inti.length ? inti : kata).slice(0, 2);
  return dipakai.map((k) => k[0].toUpperCase()).join("");
}

/** Sapaan di kepala layar. Nama toko dipotong supaya judulnya tidak membungkus tiga baris. */
export function sapaan(nama) {
  const bersih = String(nama ?? "").trim();
  if (!bersih) return "Halo, Owner UMKM!";
  return `Halo, ${bersih.length > 28 ? `${bersih.slice(0, 28).trimEnd()}…` : bersih}!`;
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

/* Dipakai saat pengguna tidak menandai fokus apa pun. Ketiganya berlaku untuk toko mana pun. */
const UMUM = [
  "Apa keluhan yang paling sering muncul?",
  "Bagaimana dibanding rata-rata kategori sejenis?",
  "Aspek apa yang justru dipuji pembeli?",
];

/** Pertanyaan yang disarankan di tab Tanya Jawab.
 *
 * Fokus pengguna didahulukan, lalu dilengkapi pertanyaan umum sampai empat - kolom saran yang
 * cuma berisi satu chip terbaca sebagai kehabisan ide, bukan sebagai penyesuaian.
 */
export function pertanyaanUntuk(focus = []) {
  const dari_fokus = focus.map((a) => PERTANYAAN[a]).filter(Boolean);
  return [...dari_fokus, ...UMUM.filter((q) => !dari_fokus.includes(q))].slice(0, 4);
}
