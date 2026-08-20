/** Label dan pemformat yang dipakai lintas layar.
 *
 * Semuanya dikumpulkan di sini karena label yang sama muncul di kartu aksi, tabel
 * benchmark, grafik aspek, dan jawaban tanya jawab - kalau tersebar, tiga di antaranya
 * pasti tertinggal saat ada istilah yang diubah.
 */

export const URGENCY_LABEL = { tinggi: "Tinggi", sedang: "Sedang", rendah: "Rendah" };

export const QUALITY_LABEL = { baik: "Baik", cukup: "Cukup", terbatas: "Terbatas" };

const ASPECT_LABEL = {
  kualitas_produk: "kualitas produk",
  kesesuaian_deskripsi: "kesesuaian deskripsi",
  harga_value: "harga",
  kemasan: "kemasan",
  pengiriman: "pengiriman",
  pelayanan_penjual: "pelayanan penjual",
  ukuran_varian: "ukuran/varian",
  rasa_kualitas_makanan: "rasa",
  kelengkapan: "kelengkapan",
  keaslian: "keaslian",
  kemudahan_penggunaan: "kemudahan pemakaian",
};

export const VISUAL_LABEL = {
  produk_rusak: "Produk rusak",
  kemasan_rusak: "Kemasan rusak",
  salah_kirim: "Salah kirim",
  produk_berbeda: "Produk berbeda dari pesanan",
  produk_normal: "Produk terlihat normal",
  normal: "Tidak ada masalah visual",
};

export const WARNING_TEXT = {
  data_kecil:
    "Data Anda kurang dari 15 ulasan. Anggap hasil ini sebagai indikasi awal, bukan kesimpulan pasti.",
  baris_dilewati: "Sebagian baris dilewati karena kosong atau terduplikasi.",
  pii_diredaksi:
    "Nomor telepon dan data pribadi yang ditemukan sudah disamarkan sebelum dianalisis.",
  mode_sederhana:
    "Mode sederhana aktif - sebagian penjelasan memakai teks standar. Seluruh angka dan bukti tetap lengkap.",
  data_kosong: "Tidak ada ulasan yang dapat dianalisis dari data ini.",
};

/** Kategori yang benar-benar dikenal backend (`Category` di apps/api/app/schemas/enums.py
 *  dan `categories` di configs/taxonomy.yaml). Menambah entri di sini tanpa menambahnya di
 *  dua tempat itu membuat analisis ditolak 422 saat tombolnya ditekan. */
export const CATEGORIES = [
  ["fashion", "Fashion"],
  ["electronics", "Elektronik"],
  ["food_beverage", "Makanan & Minuman"],
  ["craft", "Kerajinan Tangan"],
  ["other", "Lainnya"],
];

export const aspectLabel = (id) => ASPECT_LABEL[id] ?? id;

export const pct = (value) => `${Math.round(value * 100)}%`;
