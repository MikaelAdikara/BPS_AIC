/** Basis pengetahuan asisten FAQ di halaman pemasaran.
 *
 * SATU ATURAN yang mengikat seluruh berkas ini: tiap kalimat di sini harus benar tentang versi
 * yang BENAR-BENAR berjalan, bukan tentang versi yang direncanakan. Halaman pemasaran boleh
 * bersemangat, tetapi jawaban yang menjanjikan fitur yang belum ada akan ditagih pengguna pada
 * percobaan pertama - dan itu jenis kekecewaan yang paling mahal.
 *
 * Sumber kebenarannya README bagian 2 (status fase), docs/LIMITATIONS.md, dan
 * src/content/roadmap.js. Kalau salah satu berubah, berkas ini ikut diperiksa.
 *
 * Bentuk tiap entri:
 *   id     stabil, dipakai React sebagai key dan tidak pernah ditampilkan
 *   q      bentuk kanonik pertanyaannya, dipakai sebagai judul jawaban
 *   kata   kata kunci tambahan yang TIDAK muncul di `q` maupun `a`; di sinilah ragam
 *          sehari-hari, salah ketik yang lazim, dan singkatan didaftarkan
 *   a      jawaban, satu larik = satu paragraf
 *   aksi   tombol opsional di bawah jawaban: { label, ke } dengan `ke` = "dashboard"
 *          atau sebuah jangkar seperti "#cara-kerja"
 *   usul   id entri lain yang wajar ditanyakan berikutnya
 */

export const FAQ = [
  {
    id: "apa-itu",
    q: "Sebenarnya Ulasin itu untuk apa?",
    kata: "fungsi guna kegunaan gunanya ngapain produk aplikasi apaan definisi maksudnya sebenarnya gimana",
    a: [
      "Ulasin membaca ulasan pelanggan toko Anda, lalu mengubahnya jadi daftar pendek berisi masalah yang paling perlu Anda kerjakan lebih dulu - bukan sekadar angka rata-rata bintang.",
      "Bedanya dengan dashboard marketplace: dashboard berhenti di “rating Anda 4,3”. Ulasin melanjutkan ke “82% keluhan bulan ini soal ukuran, ini enam kutipan aslinya, dan ini yang sebaiknya diperbaiki minggu ini”.",
    ],
    usul: ["cara-pakai", "beda-marketplace"],
  },
  {
    id: "cara-pakai",
    q: "Cara pakainya bagaimana?",
    kata: "cara caranya langkah mulai memulai pertama tutorial penggunaan step panduan",
    a: [
      "Tiga langkah, tanpa pemasangan dan tanpa akun:",
      "1. Masukkan ulasan Anda - tempel teksnya satu ulasan per baris, unggah berkas CSV/JSON hasil ekspor marketplace, atau lampirkan tangkapan layar halaman ulasan.",
      "2. Tekan Mulai Analisis, lalu tunggu. Lamanya mengikuti banyaknya ulasan.",
      "3. Anda dapat daftar prioritas beserta kutipan asli yang mendasarinya, dan bisa bertanya lanjutan soal hasilnya.",
    ],
    aksi: { label: "Coba sekarang", ke: "dashboard" },
    usul: ["format-data", "berapa-lama", "berapa-ulasan"],
  },
  {
    id: "format-data",
    q: "Ulasan saya harus dalam bentuk apa?",
    kata: "format berkas file csv json excel xlsx unggah upload tempel paste tangkapan layar screenshot foto data masukan input kolom",
    a: [
      "Ada tiga jalur masuk, dan Anda boleh pakai yang mana saja:",
      "Tempel teks - satu ulasan per baris. Paling cepat kalau ulasannya sedikit.",
      "Berkas CSV atau JSON - hasil ekspor dari marketplace atau catatan Anda sendiri. Batasnya 5 MB dan 1.000 baris sekali unggah. Kolom mana yang berisi teks ulasan, rating, dan tanggal ditebak otomatis, dan tebakan itu masih bisa Anda betulkan sebelum analisis jalan.",
      "Tangkapan layar halaman ulasan - teksnya dibaca otomatis, lalu ditampilkan sebagai draf yang masih bisa Anda sunting kalau ada yang salah baca.",
      "Berkas Excel (.xlsx) belum didukung. Simpan dulu sebagai CSV lewat Excel atau Google Sheets.",
    ],
    usul: ["marketplace", "berapa-ulasan"],
  },
  {
    id: "marketplace",
    q: "Bisa langsung tarik ulasan dari Tokopedia atau Shopee?",
    kata: "tokopedia shopee lazada bukalapak tiktok google maps integrasi hubungkan koneksi konek sambung otomatis tarik ambil scrape akun toko api",
    a: [
      "Belum, dan ini disengaja. Versi sekarang bekerja dari berkas yang Anda ekspor sendiri atau tangkapan layar yang Anda ambil sendiri - jadi Ulasin tidak pernah minta akses ke akun toko Anda.",
      "Menarik ulasan langsung sudah ada di roadmap, tetapi status legal pengambilan data otomatis dari marketplace masih setengah terverifikasi. Kami memilih menunggu kejelasan itu daripada menyalakannya sekarang.",
    ],
    usul: ["format-data", "belum-bisa"],
  },
  {
    id: "berapa-ulasan",
    q: "Berapa banyak ulasan yang dibutuhkan?",
    kata: "jumlah minimal minimum sedikit banyak batas maksimal kuota berapa baris limit",
    a: [
      "Tidak ada batas minimum yang mengunci, tetapi di bawah 15 ulasan seluruh rekomendasi diberi tanda “data terbatas” dan tingkat urgensinya dibatasi maksimal Sedang. Alasannya sederhana: pola dari sepuluh ulasan belum tentu pola, dan sistem tidak boleh terdengar yakin pada data sesedikit itu.",
      "Batas atasnya 1.000 baris sekali unggah berkas. Hasil paling berguna biasanya di kisaran 50-300 ulasan dari satu rentang waktu yang sama.",
    ],
    usul: ["berapa-lama", "akurat"],
  },
  {
    id: "berapa-lama",
    q: "Analisisnya berapa lama?",
    kata: "lama waktu durasi cepat lambat menunggu tunggu detik menit loading proses prosesnya",
    a: [
      "Tergantung banyaknya ulasan dan kekuatan mesin yang menjalankannya. Sebagai gambaran nyata: 66 ulasan pernah terukur sekitar 88 detik pada CPU dua inti, tanpa kartu grafis.",
      "Layar prosesnya menampilkan perkiraan waktu yang dihitung dari jumlah ulasan Anda, jadi Anda tahu harus menunggu berapa lama sejak awal.",
    ],
    usul: ["berapa-ulasan", "biaya"],
  },
  {
    id: "biaya",
    q: "Ini berbayar? Perlu daftar akun?",
    kata: "harga biaya bayar gratis langganan berlangganan free trial akun daftar login masuk registrasi kartu kredit tangkapan subsidi",
    a: [
      "Versi ini gratis dan tidak ada pendaftaran akun sama sekali. Buka halaman, masukkan ulasan, dapat hasil.",
      "Gratisnya bukan karena disubsidi sementara. Seluruh model berjalan di mesin yang menjalankan aplikasi ini, bukan lewat API berbayar per ulasan, jadi ongkos melayani satu penjual tinggal sekitar Rp1.330 sebulan - hitungannya terbuka di berkas BUSINESS_VALUE di repositori.",
      "Ke depan direncanakan tingkat berlangganan sekitar Rp39.000/bulan untuk riwayat antar-periode, multi-toko, dan ekspor. Angka itu masih hipotesis dan belum diuji ke calon pengguna. Yang gratis tetap utuh, bukan versi lumpuh yang memaksa naik tingkat.",
    ],
    usul: ["privasi", "belum-bisa"],
  },
  {
    id: "privasi",
    q: "Data ulasan saya disimpan atau tidak?",
    kata: "privasi aman keamanan simpan disimpan hapus dihapus rahasia bocor data pribadi nama nomor telepon alamat pii dijual server",
    a: [
      "Tidak disimpan permanen. Data Anda hanya hidup selama sesi berjalan dan hilang begitu sesi berakhir - tidak ada basis data pengguna, tidak ada riwayat antar-kunjungan.",
      "Sebelum model apa pun melihat teksnya, data pribadi yang menempel di ulasan - nama orang, nomor telepon, alamat, nomor resi - diredaksi lebih dulu. Langkah itu wajib dan tidak bisa dimatikan.",
      "Model-modelnya berjalan di mesin yang menjalankan aplikasi ini, bukan dikirim ke layanan AI pihak ketiga.",
    ],
    usul: ["ai-apa", "biaya"],
  },
  {
    id: "ai-apa",
    q: "AI apa yang dipakai di balik layar?",
    kata: "model teknologi machine learning llm chatgpt gpt openai indobert bert nlp algoritma mesin teknis dalamnya",
    a: [
      "Ada beberapa lapisan, masing-masing untuk pekerjaan yang berbeda. Untuk membaca teks ulasan bahasa Indonesia dipakai IndoBERT yang kami latih ulang dengan dua keluaran sekaligus: aspek apa yang sedang dibicarakan, dan sentimennya. Untuk mencari kutipan pendukung dipakai model embedding dengan pencarian semantik.",
      "Yang penting Anda ketahui: seluruh angka - frekuensi, persentase, skor prioritas - dihitung rumus deterministik, bukan dikarang model bahasa. Model bahasa hanya menyusun kalimatnya dari angka yang sudah jadi. Itu sebabnya hasil yang sama tetap sama kalau dijalankan ulang.",
    ],
    usul: ["akurat", "beda-marketplace"],
  },
  {
    id: "bahasa",
    q: "Ulasan bahasa gaul dan typo bisa terbaca?",
    kata: "bahasa gaul slang singkatan alay typo salah ketik ejaan daerah jawa sunda inggris campur informal singkat",
    a: [
      "Bisa, dan memang untuk itu model bahasanya dilatih ulang - ulasan asli pelanggan Indonesia penuh singkatan, ejaan bebas, dan campuran bahasa daerah. Kata seperti “bgt”, “gak”, “kekecilan”, “fast respon” dinormalkan lebih dulu sebelum dibaca.",
      "Yang masih sering meleset dan kami akui terbuka: kalimat sarkastik, dan ulasan yang memuji sekaligus mengeluh dalam satu napas. Keduanya sedang jadi fokus perbaikan.",
    ],
    usul: ["akurat", "ai-apa"],
  },
  {
    id: "akurat",
    q: "Seberapa akurat hasilnya? Boleh langsung dipercaya?",
    kata: "akurat akurasi tepat benar salah keliru percaya andal keandalan performa evaluasi metrik kualitas meleset halusinasi ngarang",
    a: [
      "Perlakukan hasilnya sebagai saran berbasis pola, bukan kebenaran mutlak. Karena itu tiap rekomendasi datang bersama kutipan asli yang mendasarinya - supaya Anda bisa memeriksa sendiri apakah kesimpulannya masuk akal, dan menolaknya kalau tidak. Tombol Tolak ada justru untuk itu.",
      "Kalau bukti pendukungnya tidak memadai, sistem memilih mengatakan tidak tahu daripada menyusun jawaban yang terdengar meyakinkan.",
      "Angka evaluasi yang sudah terukur beserta batas penafsirannya ada di berkas MODEL_CARD di repositori - termasuk bagian yang belum lolos target kami sendiri.",
    ],
    usul: ["belum-bisa", "ai-apa"],
  },
  {
    id: "belum-bisa",
    q: "Apa yang belum bisa dilakukan Ulasin?",
    kata: "belum keterbatasan batasan limitasi kekurangan roadmap rencana nanti coming soon kelemahan bug rusak error",
    a: [
      "Daftar ini kami tampilkan terbuka, bukan disembunyikan:",
      "Menyimpulkan kondisi barang dari foto ulasan belum menyala. Teks di dalam foto sudah bisa dibaca, tetapi menilai “barangnya rusak atau tidak” dari gambarnya masih kalah dari tebakan sepele saat diuji, jadi belum kami nyalakan.",
      "Tidak ada riwayat antar-sesi. Perbandingan antar-bulan hanya terhitung kalau berkas Anda sendiri memuat kolom tanggal.",
      "Belum ada multi-toko dan pembagian akses tim, dan belum bisa menarik ulasan langsung dari marketplace.",
      "Alasan teknis tiap butir ada di tab Roadmap di dalam dashboard.",
    ],
    aksi: { label: "Lihat roadmap di dashboard", ke: "dashboard" },
    usul: ["marketplace", "akurat"],
  },
  {
    id: "hasil-apa",
    q: "Hasilnya berbentuk apa?",
    kata: "hasil keluaran output laporan dapat isi tampilan dashboard grafik ekspor unduh download pdf cetak",
    a: [
      "Satu halaman hasil berisi empat bagian: daftar masalah terurut beserta kartu rekomendasi yang bisa Anda terima atau tolak, detail tambahan berupa peluang dan sebaran aspek, ruang tanya jawab tentang ulasan Anda sendiri, dan roadmap yang menyebut apa yang belum ada.",
      "Tiap kartu rekomendasi bisa dibuka untuk melihat kutipan asli yang mendasarinya.",
      "Mengunduh hasil sebagai PDF atau CSV belum tersedia di versi ini.",
    ],
    usul: ["cara-pakai", "belum-bisa"],
  },
  {
    id: "beda-marketplace",
    q: "Bedanya dengan analitik bawaan marketplace apa?",
    kata: "beda perbedaan bandingkan pesaing kompetitor keunggulan kenapa harus alternatif dibanding unik kelebihan",
    a: [
      "Analitik bawaan marketplace berhenti di skor rata-rata dan grafik tren rating. Ia tidak memberi tahu aspek apa yang sedang bermasalah, tidak mengurutkan mana yang paling mendesak, dan tidak menunjukkan kutipan yang mendasarinya.",
      "Perkakas sentiment analysis biasa berhenti selangkah lebih jauh - ia bisa bilang “60% negatif” - tetapi tetap tidak menjawab pertanyaan yang sebenarnya Anda punya: minggu ini saya harus mengerjakan apa lebih dulu, dan apa buktinya.",
      "Bagian yang menjembatani dua pertanyaan itu yang jadi inti Ulasin.",
      "Perkakas yang benar-benar mengekstrak aspek memang ada - Thematic, Birdeye, Yotpo - tetapi harga masuknya USD 79 sampai USD 2.000 per bulan dan semuanya dirancang untuk ulasan berbahasa Inggris. Celah itu yang kami isi.",
    ],
    usul: ["apa-itu", "untuk-siapa"],
  },
  {
    id: "untuk-siapa",
    q: "Ini cocok untuk usaha seperti apa?",
    kata: "siapa target pengguna umkm toko usaha bisnis kategori fashion fesyen makanan minuman kuliner elektronik kosmetik jenis cocok",
    a: [
      "Dirancang untuk pemilik usaha mikro dan kecil yang jualan online dan menerima ulasan lebih banyak daripada waktu yang mereka punya untuk membacanya.",
      "Cakupan datanya paling kuat di kategori fesyen, karena di situ data latihnya paling tebal. Kategori makanan dan minuman masih tipis - hanya 196 dari sekitar 40.000 ulasan latih - jadi aspek rasa dan pembanding kategorinya lebih lemah buktinya. Kami sebut ini di muka supaya Anda tidak menemukannya sendiri setelah kecewa.",
    ],
    usul: ["apa-itu", "akurat"],
  },
  {
    id: "chatbot-ini",
    q: "Kamu ini AI-nya Ulasin?",
    kata: "kamu siapa bot robot asisten chatbot beneran manusia cs customer service admin hidup",
    a: [
      "Bukan. Saya kotak FAQ: jawaban saya dicocokkan dari daftar pertanyaan yang sudah ditulis manusia sebelumnya, dan saya tidak mengarang kalimat baru. Kalau pertanyaan Anda tidak ada padanannya di daftar itu, saya akan bilang begitu apa adanya.",
      "AI sungguhannya ada di dalam dashboard, dan ia bekerja pada ulasan yang Anda masukkan - bukan pada percakapan ini.",
    ],
    aksi: { label: "Buka dashboard", ke: "dashboard" },
    usul: ["ai-apa", "apa-itu"],
  },
];

/** Pintu masuk saat percakapan masih kosong. Empat, bukan semuanya: daftar panjang berhenti
 *  terbaca sebagai contoh dan mulai terbaca sebagai menu. */
export const PEMBUKA = ["apa-itu", "cara-pakai", "format-data", "privasi"];
