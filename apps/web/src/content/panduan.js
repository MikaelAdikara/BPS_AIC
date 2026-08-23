/** Isi halaman Panduan (#/panduan): dari mana ulasan diambil, dan bagaimana memasukkannya.
 *
 * Ditulis untuk pemilik toko yang tidak akrab dengan istilah "ekspor", "CSV", atau "unggah".
 * Aturannya: satu langkah = satu kalimat perintah, kata kerja di depan, nama menu ditebalkan
 * lewat tanda **...**. Jalur yang ditonjolkan di semua platform adalah yang paling universal
 * dan paling mudah dari ponsel - buka halaman ulasan, tangkap layar - karena jalur itu tidak
 * bergantung pada fitur penjual yang letaknya berpindah-pindah antar-versi aplikasi.
 *
 * Nama menu di bawah ini mengikuti aplikasi versi 2025-2026. Karena platform sering mengubah
 * tata letaknya, tiap platform punya kalimat "kalau tidak ketemu": cari kata Ulasan / Penilaian.
 */

export const JALUR = {
  shot: {
    id: "shot",
    nama: "Tangkapan layar / foto",
    label: "Paling mudah dari HP",
    hash: "#/analisis?masukan=shot",
  },
  paste: {
    id: "paste",
    nama: "Tempel teks",
    label: "Dari laptop atau WhatsApp",
    hash: "#/analisis?masukan=paste",
  },
  file: {
    id: "file",
    nama: "Berkas CSV",
    label: "Kalau sudah punya data",
    hash: "#/analisis?masukan=file",
  },
};

/** Satu entri per tempat ulasan. `layar` menggambarkan mock ponsel: judul layar, daftar menu,
 *  dan indeks baris yang harus diketuk; `langkah` adalah teks yang dibaca pengguna. */
export const PLATFORM = [
  {
    id: "shopee",
    logo: "shopee",
    nama: "Shopee",
    aksen: "#ee4d2d",
    ringkas: "Aplikasi Shopee di HP - sebagai penjual maupun pembeli",
    layar: {
      judul: "Toko Saya",
      menu: ["Pesanan Saya", "Produk Saya", "Penilaian Toko", "Performa Toko", "Promosi Saya"],
      ketuk: 2,
      hasil: "Penilaian Toko",
    },
    langkah: [
      "Buka aplikasi **Shopee**, ketuk tab **Saya** di kanan bawah, lalu **Toko Saya**.",
      "Ketuk **Penilaian Toko**. Kalau ada saringan **Dengan Komentar**, pilih itu supaya yang tampil hanya ulasan bertulisan.",
      "Tangkap layar beberapa kali sambil menggulir ke bawah - satu tangkapan biasanya memuat 3-5 ulasan.",
      "Kirim semua tangkapan layar itu ke Ulasin lewat tab **Tangkapan layar**.",
    ],
    alternatif:
      "Buka **Seller Centre** → **Layanan Pelanggan** → **Penilaian Toko**, lalu blok teks ulasannya, salin, dan tempel di Ulasin - satu ulasan per baris.",
    kalauTidakKetemu:
      "Buka salah satu produk Anda seperti pembeli, gulir ke **Penilaian Produk** → **Lihat Semua**. Jalur ini selalu ada.",
    jalur: ["shot", "paste"],
  },
  {
    id: "tokopedia",
    logo: "tokopedia",
    nama: "Tokopedia",
    aksen: "#42b549",
    ringkas: "Aplikasi Tokopedia atau Tokopedia Seller",
    layar: {
      judul: "Toko Saya",
      menu: ["Pesanan", "Produk", "Ulasan", "Statistik", "Chat"],
      ketuk: 2,
      hasil: "Ulasan",
    },
    langkah: [
      "Buka aplikasi **Tokopedia Seller** (atau menu **Toko Saya** di aplikasi Tokopedia).",
      "Ketuk **Ulasan**. Urutkan **Terbaru** kalau pilihannya ada.",
      "Tangkap layar beberapa kali sambil menggulir - tidak perlu mengunduh apa pun.",
      "Kirim tangkapan layarnya ke Ulasin lewat tab **Tangkapan layar**.",
    ],
    alternatif:
      "**Seller Center** → **Ulasan**; blok teksnya, salin, lalu tempel di Ulasin satu ulasan per baris.",
    kalauTidakKetemu:
      "Buka halaman salah satu produk Anda, ketuk **Ulasan** → **Lihat Semua Ulasan**, lalu tangkap layar.",
    jalur: ["shot", "paste"],
  },
  {
    id: "tiktokshop",
    logo: "tiktokshop",
    nama: "TikTok Shop",
    aksen: "#111111",
    ringkas: "Aplikasi TikTok Shop Seller Center",
    layar: {
      judul: "Seller Center",
      menu: ["Pesanan", "Produk", "Ulasan", "Promosi", "Data"],
      ketuk: 2,
      hasil: "Ulasan",
    },
    langkah: [
      "Buka aplikasi **TikTok Shop Seller Center** (atau seller-id.tiktok.com di laptop).",
      "Cari menu **Ulasan** / **Penilaian & Ulasan** - biasanya di bawah **Produk** atau **Layanan Pelanggan**.",
      "Tangkap layar daftar ulasannya sambil menggulir.",
      "Kirim ke Ulasin lewat tab **Tangkapan layar**.",
    ],
    alternatif:
      "Blok teks ulasan di Seller Center, salin, lalu tempel di Ulasin satu ulasan per baris.",
    kalauTidakKetemu:
      "Buka etalase toko Anda di aplikasi TikTok seperti pembeli, ketuk produk → **Ulasan**, lalu tangkap layar.",
    jalur: ["shot", "paste"],
  },
  {
    id: "lazada",
    logo: "lazada",
    nama: "Lazada",
    aksen: "#0f146d",
    ringkas: "Aplikasi Lazada Seller Center",
    layar: {
      judul: "Seller Center",
      menu: ["Pesanan", "Produk", "Ulasan Produk", "Promosi", "Keuangan"],
      ketuk: 2,
      hasil: "Ulasan Produk",
    },
    langkah: [
      "Buka aplikasi **Lazada Seller Center**.",
      "Cari **Ulasan Produk** - biasanya di bawah menu **Produk**.",
      "Tangkap layar daftar ulasannya sambil menggulir.",
      "Kirim ke Ulasin lewat tab **Tangkapan layar**.",
    ],
    alternatif:
      "Blok teks ulasannya di Seller Center, salin, lalu tempel di Ulasin.",
    kalauTidakKetemu:
      "Buka halaman produk Anda seperti pembeli, gulir ke **Ulasan Produk** → **Lihat Semua**, lalu tangkap layar.",
    jalur: ["shot", "paste"],
  },
  {
    id: "bukalapak",
    logo: "bukalapak",
    nama: "Bukalapak",
    aksen: "#E31E52",
    ringkas: "Aplikasi Bukalapak - menu Lapak Saya",
    layar: {
      judul: "Lapak Saya",
      menu: ["Transaksi", "Barang", "Ulasan", "Promosi", "Saldo"],
      ketuk: 2,
      hasil: "Ulasan",
    },
    langkah: [
      "Buka aplikasi **Bukalapak**, ketuk **Lapak Saya**.",
      "Ketuk **Ulasan** (di beberapa versi bernama **Feedback**).",
      "Tangkap layar sambil menggulir.",
      "Kirim ke Ulasin lewat tab **Tangkapan layar**.",
    ],
    alternatif: "Blok teks ulasannya, salin, lalu tempel di Ulasin satu ulasan per baris.",
    kalauTidakKetemu:
      "Buka halaman barang Anda seperti pembeli, gulir ke bagian **Ulasan**, lalu tangkap layar.",
    jalur: ["shot", "paste"],
  },
  {
    id: "google",
    logo: "google",
    nama: "Google Maps",
    aksen: "#4285F4",
    ringkas: "Untuk warung, kafe, salon, bengkel - usaha yang punya lokasi",
    layar: {
      judul: "Nama Usaha Anda",
      menu: ["Ringkasan", "Ulasan", "Foto", "Info", "Update"],
      ketuk: 1,
      hasil: "Ulasan",
    },
    langkah: [
      "Buka **Google Maps**, cari nama usaha Anda, ketuk hasilnya.",
      "Geser tab ke **Ulasan**. Ketuk **Urutkan** → **Terbaru** kalau perlu.",
      "Tangkap layar beberapa kali sambil menggulir.",
      "Kirim ke Ulasin lewat tab **Tangkapan layar**.",
    ],
    alternatif:
      "Buka Google Maps di peramban, blok teks ulasannya, salin, tempel di Ulasin - atau lewat **Profil Bisnis** Google Anda → **Ulasan**.",
    kalauTidakKetemu:
      "Ketik nama usaha Anda di pencarian Google; kotak usaha di sebelah kanan punya tautan **Ulasan Google**.",
    jalur: ["shot", "paste"],
  },
  {
    id: "chat",
    logo: null,
    nama: "WhatsApp & catatan sendiri",
    aksen: "#25D366",
    ringkas: "Keluhan lewat chat, DM Instagram, atau buku catatan",
    layar: {
      judul: "Chat pelanggan",
      menu: ["Kak ukurannya kekecilan 😢", "Packingnya penyok", "Pengiriman 5 hari", "Warnanya beda", "Makasih, cepat!"],
      ketuk: -1,
      hasil: null,
      mode: "chat",
    },
    langkah: [
      "Di **WhatsApp**, tekan-tahan pesan keluhan, ketuk pesan lain untuk memilih beberapa sekaligus, lalu **Salin**.",
      "Buka Ulasin, tab **Tempel teks**, tempelkan. Pastikan **satu keluhan per baris**.",
      "Atau: tangkap layar percakapannya dan kirim lewat tab **Tangkapan layar** - teksnya dibaca otomatis.",
      "Punya catatan di buku? Ketik saja langsung di kotak tempel, satu keluhan per baris.",
    ],
    altJudul: "Terbiasa spreadsheet?",
    alternatif:
      "Kalau sudah terbiasa dengan Excel/Google Sheets: satu kolom bernama **ulasan**, satu baris per keluhan, simpan sebagai **CSV**, lalu unggah. Ada contoh berkasnya di bawah.",
    kalauTidakKetemu: null,
    jalur: ["paste", "shot", "file"],
  },
];

/** Cara memasukkan ke Ulasin - tiga kartu di bawah pemilih platform. */
export const CARA = [
  {
    id: "shot",
    judul: "Tangkapan layar atau foto",
    untuk: "Paling mudah dari HP. Tidak perlu tahu di mana berkas tersimpan.",
    langkah: [
      "Buka Ulasin, ketuk tab **Tangkapan layar**.",
      "Ketuk area unggah, pilih semua tangkapan layar sekaligus (boleh 20-an).",
      "Tunggu beberapa detik - teksnya dibaca otomatis, lalu ditampilkan sebagai daftar yang bisa Anda perbaiki.",
      "Di laptop tanpa berkas? Ketuk **Ambil foto layar ulasan dengan kamera**, arahkan ke layar HP yang menampilkan ulasan.",
    ],
    catatan: "Salah baca satu-dua huruf tidak apa-apa - sistem toleran terhadap ejaan. Yang penting kalimatnya terbaca.",
  },
  {
    id: "paste",
    judul: "Tempel teks",
    untuk: "Dari laptop, WhatsApp, atau ketik langsung.",
    langkah: [
      "Blok teks ulasan di layar, salin (Ctrl+C atau tekan-tahan → Salin).",
      "Buka Ulasin, tab **Tempel teks**, tempelkan (Ctrl+V).",
      "Pastikan satu ulasan per baris - tekan Enter di antara dua ulasan.",
      "Tekan **Analisis**.",
    ],
    catatan: "Nomor HP, email, alamat, dan nomor rekening yang ikut tertempel disamarkan otomatis sebelum dianalisis. Nama orang tidak dideteksi - hapus sendiri kalau ada.",
  },
  {
    id: "file",
    judul: "Berkas CSV / JSON",
    untuk: "Kalau sudah punya data di Excel atau hasil ekspor.",
    langkah: [
      "Pastikan ada satu kolom berisi teks ulasan - beri nama **ulasan**. Kolom rating, tanggal, dan produk boleh ada, tidak wajib.",
      "Di Excel: **File → Simpan Sebagai → CSV UTF-8**. Di Google Sheets: **File → Unduh → CSV**.",
      "Buka Ulasin, tab **Unggah berkas**, tarik berkasnya ke kotak.",
      "Periksa kolom yang tertebak, lalu tekan **Analisis**.",
    ],
    catatan: "Maksimal 5 MB dan 1.000 baris sekali jalan. Berkas Excel (.xlsx) harus disimpan dulu sebagai CSV.",
    unduh: { href: "/templates/ulasan-contoh.csv", label: "Unduh contoh berkas CSV" },
  },
];

export const SEBELUM_MULAI = [
  {
    judul: "Berapa banyak ulasan?",
    isi: "Mulai dari 15 ulasan polanya sudah terlihat; 30 ke atas lebih meyakinkan. Di bawah 15, sistem tetap bekerja tetapi memberi tahu bahwa datanya masih sedikit.",
  },
  {
    judul: "Apakah data saya aman?",
    isi: "Tidak ada akun, tidak ada yang disimpan setelah halaman ditutup. Nomor telepon, email, alamat, dan nomor rekening yang terdeteksi disamarkan sebelum dianalisis. Gambar dibaca teksnya lalu dibuang.",
  },
  {
    judul: "Belum punya ulasan sama sekali?",
    isi: "Tekan **Coba dengan data contoh** di layar kerja - itu 66 ulasan asli dari sebuah toko, supaya Anda tahu bentuk hasilnya sebelum memakai data sendiri.",
  },
];

export const TANYA = [
  {
    q: "Ulasannya campur bahasa Inggris atau bahasa daerah, bisa?",
    a: "Bisa, dengan catatan. Sistem dilatih pada ulasan marketplace Indonesia termasuk singkatan dan bahasa gaul; kalimat Inggris penuh dan bahasa daerah terbaca lebih kasar. Kutipan aslinya selalu ditampilkan, jadi Anda bisa menilai sendiri.",
  },
  {
    q: "Hasil bacaan tangkapan layar ada yang salah. Bagaimana?",
    a: "Setelah gambar dibaca, teksnya muncul sebagai daftar yang bisa Anda sunting sebelum dianalisis - perbaiki yang salah, hapus yang bukan ulasan (misalnya nama menu yang ikut terbaca), lalu tekan Analisis.",
  },
  {
    q: "Saya cuma punya HP, tidak punya laptop.",
    a: "Cukup. Seluruh alur - tangkap layar, unggah, baca hasil - dirancang untuk layar HP. Kalau ingin memotret layar HP lain, pakai tombol kamera di tab Tangkapan layar.",
  },
  {
    q: "Bisakah ulasan dari dua toko dicampur?",
    a: "Bisa secara teknis, tetapi hasilnya jadi rata-rata dua toko. Lebih berguna dianalisis terpisah - lalu pakai fitur Arsip untuk membandingkannya.",
  },
  {
    q: "Ulasannya ada fotonya. Apakah fotonya ikut dinilai?",
    a: "Belum. Foto ulasan tidak dinilai kondisinya; yang dibaca hanya teks. Kami menulis alasannya terbuka di halaman Roadmap - model visual kami belum lolos uji dan kami tidak mau menebak.",
  },
];
