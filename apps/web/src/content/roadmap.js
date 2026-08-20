/** Isi layar Roadmap.
 *
 * Layar ini ada supaya batas versi sekarang terbaca sebagai keputusan, bukan sebagai
 * kekurangan yang disembunyikan. Karena itu tiap butir menyebut ALASAN teknisnya, bukan
 * sekadar "coming soon". Sumbernya docs/LIMITATIONS.md dan docs/SCOPE_FREEZE.md - kalau
 * salah satu berubah, berkas ini ikut diperbarui.
 */

export const ROADMAP = [
  {
    id: "visual",
    title: "Kesimpulan otomatis dari foto ulasan",
    status: "Diuji, belum lolos",
    body:
      "Foto yang Anda unggah sudah bisa dibaca teksnya, tetapi menyimpulkan kondisi barang dari gambarnya belum. Pengujian pada 97 foto ulasan asli menempatkan model di bawah tebakan sepele, dan 61% foto yang sebenarnya normal salah ditandai bermasalah. Menyalakannya sekarang berarti mengirim Anda memeriksa barang yang tidak apa-apa.",
  },
  {
    id: "kontradiksi",
    title: "Deteksi otomatis saat foto membantah teksnya",
    status: "Menunggu butir di atas",
    body:
      "Menandai ulasan yang menulis \u201cbarangnya bagus\u201d tetapi melampirkan foto barang rusak. Mesin pembandingnya sudah ada di backend; yang belum ada adalah sisi foto yang cukup dapat dipercaya untuk dijadikan pembanding.",
  },
  {
    id: "riwayat",
    title: "Riwayat antar-sesi dan tren antar-periode",
    status: "Belum dibangun",
    body:
      "Sekarang setiap sesi dimulai dari nol dan tidak ada yang disimpan setelah Anda menutup halaman. Konsekuensinya, perubahan antar-bulan hanya terhitung bila berkas Anda sendiri memuat kolom tanggal.",
  },
  {
    id: "multitoko",
    title: "Multi-toko dan pembagian akses tim",
    status: "Kandidat, belum komitmen",
    body:
      "Satu akun untuk beberapa toko sekaligus, dengan hak akses berbeda per anggota tim. Butuh akun dan penyimpanan permanen, dua hal yang sengaja tidak ada pada versi ini.",
  },
  {
    id: "koneksi",
    title: "Tarik ulasan langsung dari marketplace",
    status: "Kandidat, belum komitmen",
    body:
      "Menghapus langkah ekspor-lalu-unggah. Status legal pengambilan data otomatis masih setengah terverifikasi, jadi versi ini hanya bekerja dari berkas yang Anda ekspor sendiri.",
  },
];
