/** Basis pengetahuan kotak FAQ di halaman pemasaran.
 *
 * SATU ATURAN yang mengikat seluruh berkas ini: tiap kalimat di sini harus benar tentang versi
 * yang BENAR-BENAR berjalan, bukan tentang versi yang direncanakan. Halaman pemasaran boleh
 * bersemangat, tetapi jawaban yang menjanjikan fitur yang belum ada akan ditagih pengguna pada
 * percobaan pertama - dan itu jenis kekecewaan yang paling mahal. Yang masih rencana ditulis
 * sebagai rencana, dengan katanya sendiri.
 *
 * Cakupannya sengaja LEBAR - 40 entri menutupi produk, cara pakai, isi hasil, model yang
 * dipakai, data dan privasi, batas yang diketahui, sampai soal repositori. Basis yang tipis
 * memaksa kotak ini terlalu sering berkata tidak tahu, dan kotak FAQ yang sering angkat tangan
 * lebih buruk daripada tidak ada kotak FAQ sama sekali.
 *
 * Sumber kebenarannya README bagian 2 (status fase), docs/LIMITATIONS.md, docs/MODEL_CARD.md,
 * docs/BUSINESS_VALUE.md, dan src/content/roadmap.js. Kalau salah satu berubah, berkas ini
 * ikut diperiksa.
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
  // ------------------------------------------------------------------ produk
  {
    id: "apa-itu",
    q: "Sebenarnya Ulasin itu untuk apa?",
    kata: "fungsi guna kegunaan gunanya ngapain produk aplikasi apaan definisi maksudnya sebenarnya adalah tentang",
    a: [
      "Ulasin membaca ulasan pelanggan toko Anda, lalu mengubahnya jadi daftar pendek berisi masalah yang paling perlu Anda kerjakan lebih dulu - bukan sekadar angka rata-rata bintang.",
      "Bedanya dengan dashboard marketplace: dashboard berhenti di “rating Anda 4,3”. Ulasin melanjutkan ke “82% keluhan bulan ini soal ukuran, ini enam kutipan aslinya, dan ini yang sebaiknya diperbaiki minggu ini”.",
    ],
    aksi: { label: "Coba sekarang", ke: "dashboard" },
    usul: ["cara-pakai", "hasil-apa", "beda-marketplace"],
  },
  {
    id: "untuk-siapa",
    q: "Ini cocok untuk siapa?",
    kata: "target pengguna user cocok pemilik penjual seller toko olshop umkm ukm mikro kecil pedagang",
    a: [
      "Penjual mikro dan kecil yang berjualan di satu sampai tiga marketplace, mengurus tokonya sendiri atau dengan satu-dua orang, dan menerima ulasan lebih banyak daripada yang sempat dibaca.",
      "Ambang praktisnya: kalau ulasan Anda di bawah 15 sebulan, membaca sendiri masih lebih cepat dan hasil di sini pun akan ditandai berkeyakinan rendah. Di atas 50-100 sebulan, membaca manual mulai tidak sepadan.",
      "Yang belum kami layani: merek dengan banyak toko sekaligus dan tim yang butuh pembagian akses. Keduanya butuh akun dan penyimpanan permanen yang sengaja belum ada.",
    ],
    usul: ["berapa-ulasan", "belum-bisa"],
  },
  {
    id: "masalah-apa",
    q: "Masalah apa yang sebenarnya diselesaikan?",
    kata: "masalah problem kenapa perlu butuh urgensi penting latar belakang alasan dibuat",
    a: [
      "Keluhan yang sama berulang di ulasan tanpa pernah terdeteksi. Konsekuensinya dua kali: penjualan yang hilang, dan biaya iklan yang dibakar untuk mendatangkan pembeli ke masalah yang belum diperbaiki.",
      "Di Indonesia ada 4,40 juta unit usaha e-commerce menurut BPS 2024, mayoritas mikro, dan margin mereka sudah tergerus 15-20% biaya platform sebelum satu rupiah masuk kantong. Di margin setipis itu, salah menebak prioritas perbaikan mahal sekali.",
    ],
    usul: ["apa-itu", "beda-tools"],
  },
  {
    id: "beda-marketplace",
    q: "Apa bedanya dengan laporan bawaan Shopee atau Tokopedia?",
    kata: "beda bedanya banding dibanding shopee tokopedia lazada bukalapak tiktok seller centre dashboard bawaan laporan statistik",
    a: [
      "Seller Centre menampilkan rating rata-rata, daftar ulasan, dan penyaringan per bintang. Semuanya berguna, tetapi berhenti di “berapa”, tidak sampai “apa yang salah dan mana yang dikerjakan duluan”.",
      "Ulasin mengelompokkan keluhan per aspek - ukuran, kemasan, pengiriman, pelayanan - mengurutkannya berdasarkan dampak, dan menempelkan kutipan aslinya sebagai bukti.",
      "Satu lagi: tiap dashboard hanya melihat kanalnya sendiri. Kalau Anda jualan di tiga tempat, tidak ada satu pun yang memberi gambaran utuh. Ulasin bekerja dari berkas ekspor kanal mana pun sekaligus.",
    ],
    usul: ["beda-tools", "format-data"],
  },
  {
    id: "beda-tools",
    q: "Sudah ada tool analisis ulasan lain, kenapa pakai ini?",
    kata: "kompetitor pesaing alternatif lain saingan yotpo birdeye thematic brand24 tools saas luar negeri asing mahal",
    a: [
      "Perkakas yang benar-benar mengekstrak aspek memang sudah ada. Masalahnya harga dan bahasa: Yotpo mulai USD 79/bulan, Birdeye USD 299-449/bulan per lokasi dengan kontrak setahun, Thematic mulai USD 2.000/bulan.",
      "Tier termurah Birdeye saja sekitar Rp4,8 juta sebulan. Untuk penjual yang marginnya sudah dipotong 15-20% biaya platform, itu bukan “mahal” - itu kategori yang berbeda sama sekali.",
      "Dan ketiganya dirancang untuk ulasan berbahasa Inggris. Tidak ada yang dibangun untuk membaca “bahannya oke sih cuma kekecilan bgt, sizechartnya ngaco”. Celah itu yang kami isi.",
    ],
    aksi: { label: "Lihat perbandingannya", ke: "#nilai" },
    usul: ["biaya", "bahasa"],
  },

  // ------------------------------------------------------------------ cara pakai
  {
    id: "cara-pakai",
    q: "Cara pakainya bagaimana?",
    kata: "cara caranya langkah mulai memulai pertama tutorial penggunaan step panduan pakai gunakan",
    a: [
      "Tiga langkah, tanpa pemasangan dan tanpa akun:",
      "1. Masukkan ulasan Anda - tempel teksnya satu ulasan per baris, unggah berkas CSV/JSON hasil ekspor marketplace, atau lampirkan tangkapan layar halaman ulasan.",
      "2. Tekan Mulai Analisis, lalu tunggu. Lamanya mengikuti banyaknya ulasan.",
      "3. Baca hasilnya: masalah teratas berurutan, tiap satunya dengan kutipan asli pelanggan sebagai bukti.",
    ],
    aksi: { label: "Mulai Analisis", ke: "dashboard" },
    usul: ["dari-mana-ulasan", "format-data", "berapa-lama", "dataset-contoh"],
  },
  {
    id: "dari-mana-ulasan",
    q: "Dari mana saya mengambil ulasannya?",
    kata: "ambil dapat dapet dapatkan sumber asal shopee tokopedia tiktok lazada bukalapak google maps whatsapp wa seller center centre penilaian toko ekspor export screenshot ss tangkap layar foto menu letak di mana dimana",
    a: [
      "Dari tempat ulasan toko Anda biasanya muncul: halaman Penilaian Toko / Ulasan di aplikasi Shopee, Tokopedia, TikTok Shop, Lazada, Bukalapak, tab Ulasan di Google Maps, atau chat WhatsApp pelanggan.",
      "Cara paling mudah dari HP: buka halaman ulasannya, tangkap layar beberapa kali sambil menggulir, lalu kirim semua tangkapan itu ke tab Tangkapan layar - teksnya dibaca otomatis dan bisa Anda perbaiki sebelum dianalisis. Tidak perlu mengunduh atau mengekspor apa pun.",
      "Halaman Panduan menunjukkan letak menunya per aplikasi dengan gambar, langkah demi langkah, dan langsung mengantar ke tab yang tepat.",
    ],
    aksi: { label: "Buka panduan per aplikasi", ke: "#/panduan" },
    usul: ["screenshot", "format-data", "tarik-otomatis"],
  },
  {
    id: "format-data",
    q: "Ulasan saya harus dalam bentuk apa?",
    kata: "format file berkas csv json excel xlsx tempel paste copy salin unggah upload bentuk data masukan input",
    a: [
      "Tiga jalur, pilih yang paling gampang buat Anda: tempel teks langsung (satu ulasan per baris), unggah CSV atau JSON hasil ekspor marketplace, atau lampirkan tangkapan layar halaman ulasan.",
      "Batasnya 5 MB dan 1.000 baris sekali unggah. Kalau berkas Anda lebih besar, potong dulu sebagian.",
      "Excel (.xlsx) belum didukung langsung - simpan dulu sebagai CSV dari Excel atau Google Sheets.",
    ],
    usul: ["kolom-csv", "screenshot", "berapa-ulasan"],
  },
  {
    id: "kolom-csv",
    q: "Kolom mana yang dipakai dari file CSV saya?",
    kata: "kolom column header mapping pemetaan tebak cocokkan nama field struktur",
    a: [
      "Sistem menebaknya sendiri dari nama kolom - “review”, “ulasan”, “komentar”, “rating”, “bintang”, “tanggal”, dan ragam lain yang lazim dipakai ekspor marketplace maupun dataset publik.",
      "Tebakan itu ditampilkan sebelum analisis jalan, dan Anda bisa menimpanya. Yang wajib cuma kolom teks ulasan; rating, tanggal, dan nama produk sifatnya opsional.",
      "Kalau kolom tanggal ada, perhitungan tren antar-periode ikut aktif. Kalau tidak ada, sisanya tetap jalan.",
    ],
    usul: ["format-data", "hasil-apa"],
  },
  {
    id: "screenshot",
    q: "Bisa dari tangkapan layar?",
    kata: "screenshot ss sc foto gambar tangkapan layar jpg png ocr baca scan potret pakai boleh dukung unggah upload",
    a: [
      "Bisa. Lampirkan tangkapan layar halaman ulasan, teksnya akan dibaca otomatis, lalu hasil bacaannya ditampilkan supaya Anda bisa memperbaikinya sebelum dianalisis.",
      "Langkah koreksi itu tidak dilewati dengan sengaja: pembacaan teks dari gambar tidak pernah sempurna, terutama pada tangkapan layar yang kecil atau buram. Lebih baik Anda memperbaiki satu-dua baris daripada sistem menganalisis kata yang salah baca.",
      "Yang belum bisa: menyimpulkan kondisi barang dari isi fotonya. Itu urusan lain, dan alasannya ada di pertanyaan soal analisis foto.",
    ],
    usul: ["foto-barang", "format-data"],
  },
  {
    id: "berapa-ulasan",
    q: "Minimal berapa ulasan supaya hasilnya berguna?",
    kata: "minimal minimum berapa banyak jumlah sedikit banyak batas maksimal maksimum kuota limit",
    a: [
      "Secara teknis satu ulasan pun jalan, tetapi di bawah 15 ulasan seluruh rekomendasi diberi tanda “keyakinan rendah - data terbatas” dan tingkat urgensinya dibatasi maksimal Sedang.",
      "Itu batas yang sengaja dipasang. Pola dari sepuluh ulasan belum tentu pola, dan sistem yang terdengar yakin pada data sesedikit itu justru menyesatkan.",
      "Batas atasnya 1.000 baris sekali unggah.",
    ],
    usul: ["akurat", "prioritas"],
  },
  {
    id: "berapa-lama",
    q: "Prosesnya berapa lama?",
    kata: "lama durasi waktu cepat lambat menunggu tunggu detik menit kecepatan performa",
    a: [
      "Terukur 88 detik untuk 66 ulasan pada mesin CPU dua inti tanpa kartu grafis. Kira-kira 1,3 detik per ulasan, jadi 300 ulasan sekitar tujuh menit.",
      "Angkanya bisa lebih cepat di mesin yang lebih besar. Selama proses berjalan, layar menampilkan perkiraan waktu dan jam berjalan supaya Anda tidak menebak-nebak.",
    ],
    usul: ["berapa-ulasan", "kenapa-gratis"],
  },
  {
    id: "dataset-contoh",
    q: "Bisa coba dulu tanpa data saya sendiri?",
    kata: "coba demo contoh sample sampel dummy tes test percobaan tanpa data lihat dulu",
    a: [
      "Bisa. Di layar awal ada tombol untuk memakai dataset contoh - sekali klik, langsung jalan sampai hasil, tanpa Anda perlu menyiapkan apa pun.",
      "Itu cara tercepat melihat bentuk hasilnya sebelum memutuskan mengunggah data toko sendiri.",
    ],
    aksi: { label: "Coba dataset contoh", ke: "dashboard" },
    usul: ["hasil-apa", "cara-pakai"],
  },
  {
    id: "kategori",
    q: "Kenapa harus pilih kategori produk?",
    kata: "kategori jenis produk fesyen fashion baju makanan minuman fnb f&b elektronik kerajinan pilihan dropdown wajib",
    a: [
      "Kategori menentukan pembanding yang dipakai: angka toko Anda diadu dengan rata-rata kategori itu dari data publik, jadi Anda tahu apakah “12% keluhan soal pengiriman” wajar atau di atas kebiasaan. Ia juga menentukan aspek mana yang berlaku untuk toko Anda - rasa cuma muncul untuk makanan dan minuman.",
      "Yang TIDAK dilakukannya, supaya tidak salah harap: kategori tidak menyaring aspek mana yang dianalisis. Seluruh aspek tetap dihitung; yang menyesuaikan diri hanyalah pembandingnya. Anda juga tidak perlu memilihnya di depan - sistem menebaknya dari isi ulasan, lalu menampilkan tebakan itu di kepala laporan untuk Anda ganti kalau meleset.",
      "Jujur soal cakupannya: data latih kami paling tebal di fesyen. Kategori makanan dan minuman hanya terwakili 196 dari sekitar 40.000 ulasan, jadi aspek rasa dan pembandingnya lemah buktinya di sana.",
    ],
    usul: ["profil-toko", "benchmark", "akurat"],
  },
  {
    id: "profil-toko",
    q: "Kenapa saya tidak ditanya nama toko dan produknya?",
    kata: "nama toko produk isian opsional profil identitas sapaan avatar kolom tambahan beri tahu lebih banyak formulir ditanya",
    a: [
      "Dulu memang ditanya, dan itu keliru. Nama produk sudah ada di dalam berkas yang Anda unggah - di kolom produk - jadi menanyakannya lagi berarti meminta Anda mengetik ulang sesuatu yang baru saja Anda kirim. Sekarang kolom itu dibaca langsung, dan ia yang mengisi bagian Per produk di laporan.",
      "Nama toko tidak ditanyakan karena tidak dipakai untuk apa pun yang berguna. Ia dulu cuma menyapa Anda di kepala layar dan mengisi inisial avatar. Laporan analisis tidak perlu menyapa pembacanya; yang perlu ada di kepala laporan adalah berapa ulasannya dan dari rentang tanggal kapan - dan keduanya dihitung dari data Anda sendiri.",
      "Kategori juga tidak lagi ditanyakan di depan: ia ditebak dari isi ulasan Anda, lalu tebakannya ditampilkan di kepala laporan sebagai pilihan yang bisa Anda ganti seketika, tanpa mengulang analisis.",
    ],
    usul: ["kategori", "privasi", "kutipan"],
  },
  {
    id: "fokus",
    q: "Dulu ada pilihan “yang paling ingin Anda tahu”, ke mana perginya?",
    kata: "fokus tandai aspek pilihan minat perhatian tiga maksimal personalisasi sesuaikan yang mau dianalisa hilang dihapus",
    a: [
      "Dihapus, karena pekerjaannya habis. Pilihan itu ada untuk menjaga satu-dua aspek tetap tampil di grafik yang dipotong enam baris. Sekarang laporan menampilkan SELURUH aspek, masing-masing dengan bagiannya sendiri - termasuk aspek yang tidak disebut satu ulasan pun, yang justru sering paling ingin Anda ketahui.",
      "Pertanyaan siap-pakai di tab Tanya Jawab dulu disusun dari aspek yang Anda tandai. Sekarang disusun dari aspek yang paling banyak dikeluhkan di data Anda - jadi ia menawarkan pertanyaan tentang masalah yang benar-benar ada, bukan tentang masalah yang Anda duga sebelum melihat satu pun hasil.",
      "Yang sengaja TIDAK berubah: urutan prioritas kartu tindakan tetap dihitung dari frekuensi, keparahan, dan keyakinan - tidak pernah dari apa yang sudah Anda curigai.",
    ],
    usul: ["prioritas", "profil-toko"],
  },

  // ------------------------------------------------------------------ hasil
  {
    id: "hasil-apa",
    q: "Hasilnya berbentuk apa?",
    kata: "hasil hasilnya output laporan report keluaran dapat dapet isi bentuk bentuknya berbentuk tampilan layar halaman",
    a: [
      "Satu laporan yang digulir, dengan rel bagian di sampingnya: Ringkasan, Prioritas, Per aspek, Per produk, Sebaran bintang, Riwayat antar periode, Peluang, Benchmark, dan Kualitas data. Bagian yang tidak punya datanya - misalnya Per produk kalau berkas Anda tidak memuat kolom produk - tidak ditampilkan sama sekali alih-alih tampil kosong.",
      "Di sebelahnya ada dua mode lain: Tanya Jawab untuk bertanya bebas soal ulasan Anda, dan Roadmap untuk apa yang belum ada beserta alasannya.",
      "Inti yang paling dipakai ada di bagian pertama: kartu-kartu tindakan berurutan dari yang paling mendesak, masing-masing dengan kutipan asli pelanggan dan tombol Terima atau Tolak.",
    ],
    usul: ["prioritas", "kutipan", "terima-tolak"],
  },
  {
    id: "prioritas",
    q: "Urutan prioritasnya dihitung dari apa?",
    kata: "prioritas urutan ranking peringkat skor score mendesak urgensi penting hitung rumus formula",
    a: [
      "Tiga faktor inti dikalikan: seberapa sering keluhan itu muncul, seberapa parah, dan seberapa yakin sistem pada klasifikasinya. Hasilnya lalu dinaikkan sedikit oleh dua pengali - seberapa baru kejadiannya, dan seberapa jauh angka Anda dari pembanding kategori.",
      "Seluruh perhitungan itu dilakukan kode biasa yang bisa diaudit baris per baris, bukan oleh model bahasa. Angka di produk ini tidak pernah dikarang.",
      "Yang perlu Anda tahu: bobot kedua pengali itu belum tervalidasi lewat pemakaian nyata. Kami menuliskannya terbuka di dokumentasi alih-alih menyajikannya sebagai angka final.",
    ],
    usul: ["angka-darimana", "akurat"],
  },
  {
    id: "kutipan",
    q: "Kenapa tiap rekomendasi ada kutipannya?",
    kata: "kutipan bukti evidence sumber quote asli verifikasi cek percaya alasan dasar",
    a: [
      "Supaya Anda bisa memeriksa sendiri, bukan sekadar percaya. Tiap rekomendasi membawa ulasan asli yang mendasarinya, jadi Anda bisa menerimanya dengan yakin atau menolaknya dengan alasan yang jelas.",
      "Aturannya keras di sisi sistem: rekomendasi yang tidak punya kutipan pendukung tidak diterbitkan sama sekali. Dan kalau ditanya sesuatu yang buktinya tidak ada di data Anda, sistem menjawab tidak tahu alih-alih menyusun kalimat yang terdengar meyakinkan.",
    ],
    usul: ["terima-tolak", "tanya-jawab"],
  },
  {
    id: "terima-tolak",
    q: "Tombol Terima dan Tolak itu buat apa?",
    kata: "terima tolak reject accept simpan nanti tombol keputusan setuju tidak setuju",
    a: [
      "Untuk menandai rekomendasi mana yang Anda ambil dan mana yang tidak relevan buat toko Anda. Tombol Tolak sengaja dibuat sama menonjolnya dengan Terima.",
      "Alasannya prinsip: sistem ini menyarankan, tidak memutuskan. Rekomendasinya saran berbasis pola data, bukan kebenaran mutlak - dan produk yang menyembunyikan tombol tolak sedang meminta kepatuhan, bukan keputusan.",
      "Catatan jujur: pada versi sekarang keputusan itu belum direkam untuk perbaikan model, karena tidak ada penyimpanan permanen sama sekali.",
    ],
    usul: ["kutipan", "simpan-riwayat"],
  },
  {
    id: "tanya-jawab",
    q: "Bisa tanya bebas soal ulasan saya?",
    kata: "tanya jawab bertanya pertanyaan qna q&a chat diskusi bebas eksplorasi gali",
    a: [
      "Bisa, di tab Tanya Jawab setelah analisis selesai. Misalnya “keluhan apa yang paling sering muncul?” atau “bagaimana pendapat pembeli soal pengiriman?”.",
      "Jawabannya disusun dari statistik yang sudah dihitung dan kutipan yang diambil dari ulasan Anda sendiri - selalu dengan sumbernya. Kalau buktinya tidak memadai, sistem bilang tidak tahu.",
      "Perlu dibedakan dari kotak yang sedang Anda pakai sekarang: yang ini menjawab soal produk Ulasin, yang di dashboard menjawab soal isi ulasan Anda.",
    ],
    usul: ["kutipan", "kotak-ini"],
  },
  {
    id: "benchmark",
    q: "Angka saya dibandingkan dengan apa?",
    kata: "benchmark banding pembanding rata-rata industri kategori normal wajar standar kompetitor toko lain",
    a: [
      "Dengan baseline kategori yang dihitung sebelumnya dari data publik - jadi Anda tahu apakah “12% keluhan soal pengiriman” itu wajar atau di atas kebiasaan kategori Anda.",
      "Batasnya perlu disebut: pembanding itu historis dan statis. Ia bukan pemantauan kompetitor real-time, dan tidak melihat toko tetangga Anda hari ini.",
    ],
    usul: ["kategori", "belum-bisa"],
  },
  {
    id: "ekspor",
    q: "Hasilnya bisa diunduh atau diekspor?",
    kata: "ekspor export unduh download simpan pdf excel csv cetak print bagikan share kirim",
    a: [
      "Belum bisa pada versi ini. Hasil hanya tampil di layar selama sesi berlangsung.",
      "Untuk sekarang, cara paling praktis menyimpannya adalah tangkapan layar. Ekspor PDF dan CSV termasuk yang direncanakan untuk tingkat berlangganan nanti.",
    ],
    usul: ["simpan-riwayat", "langganan"],
  },

  // ------------------------------------------------------------------ AI & model
  {
    id: "ai-apa",
    q: "AI apa yang dipakai di belakangnya?",
    kata: "ai model teknologi machine learning ml nlp indobert bert llm gpt openai algoritma mesin pakai dipakai belakang balik dalamnya",
    a: [
      "Lapisan teksnya IndoBERT yang kami latih ulang sendiri, dengan dua kepala sekaligus - satu mengenali aspek, satu menilai sentimen. Pengambilan kutipan buktinya memakai model pencarian semantik dan penyimpan vektor.",
      "Semuanya berjalan lokal di mesin yang menjalankan aplikasi ini. Tidak ada panggilan ke API AI pihak ketiga, jadi data ulasan Anda tidak pernah dikirim ke layanan luar.",
      "Yang belum jalan: lapisan model bahasa besar yang tugasnya menyusun narasi. Karena itu kalimat rekomendasinya sekarang memakai templat - lebih kaku, tetapi angka dan buktinya persis sama.",
    ],
    usul: ["angka-darimana", "privasi"],
  },
  {
    id: "angka-darimana",
    q: "Angka-angkanya dari mana? Bukan dikarang AI?",
    kata: "angka persentase persen statistik hitung dikarang halusinasi hallucination bohong ngarang akurat sumber",
    a: [
      "Bukan. Seluruh frekuensi, persentase, dan skor prioritas dihitung fungsi deterministik yang bisa diaudit baris per baris. Menjalankan ulang analisis yang sama menghasilkan angka yang sama persis.",
      "Model bahasa - kalau nanti diaktifkan - hanya menyusun kalimat dari angka yang sudah jadi, dan tidak pernah menghitung sendiri. Itu keputusan arsitektur yang dicatat sejak awal, khusus untuk mencegah angka halusinasi.",
    ],
    usul: ["prioritas", "ai-apa"],
  },
  {
    id: "bahasa",
    q: "Bahasa gaul dan singkatan kebaca tidak?",
    kata: "bahasa gaul slang singkatan typo salah ketik alay informal daerah campur inggris jawa sunda ejaan",
    a: [
      "Kebaca. Model dilatih pada ulasan e-commerce Indonesia yang memang ditulis apa adanya - singkatan, ejaan bebas, campuran bahasa daerah. Pada pengujian per jenis bahasa, typo dan slang termasuk yang paling kuat ditangani.",
      "Yang masih lemah dan tidak kami sembunyikan: kalimat sarkastis, kalimat bernegasi bertingkat, dan ulasan yang memuji sekaligus mengeluh dalam satu napas. Ketiganya memang jenis kalimat tersulit.",
    ],
    usul: ["akurat", "kategori"],
  },
  {
    id: "akurat",
    q: "Seberapa akurat sih hasilnya?",
    kata: "akurat akurasi tepat benar salah keliru presisi kualitas percaya andal reliabel skor metrik",
    a: [
      "Diuji pada label yang dibuat manusia, bukan pada label buatan mesin sendiri. Untuk sentimen, model hasil latihan kami mencetak 0,730 - di atas pendekatan kamus kata 0,700 dan TF-IDF 0,627.",
      "Untuk pengenalan aspek, hasilnya setara dengan pendekatan kamus kata dan tidak lebih baik. Gate internal kami untuk bagian itu dinyatakan TIDAK LULUS, dan angkanya tetap kami publikasikan apa adanya.",
      "Kesimpulan jujurnya: berguna sebagai penunjuk arah dan pengurut prioritas, bukan sebagai vonis. Tombol Tolak ada justru karena itu.",
    ],
    usul: ["bahasa", "terima-tolak", "belum-bisa"],
  },
  {
    id: "foto-barang",
    q: "Bisa menilai kondisi barang dari foto ulasan?",
    kata: "foto gambar visual barang rusak penyok kondisi cek periksa citra image vision clip",
    a: [
      "Belum, dan ini sengaja dimatikan. Teks pada foto sudah bisa dibaca, tetapi menyimpulkan kondisi barang dari isi gambarnya belum lolos pengujian.",
      "Angkanya: pada 97 foto ulasan asli, model hanya benar 45% - kalah dari tebakan sepele “semuanya normal” yang benar 61%. Dan 61% foto yang sebenarnya baik-baik saja justru ditandai bermasalah.",
      "Menyalakannya sekarang berarti mengirim Anda memeriksa barang yang tidak apa-apa. Jadi lebih baik mati sampai betul.",
    ],
    usul: ["screenshot", "belum-bisa"],
  },
  {
    id: "kotak-ini",
    q: "Kotak tanya ini AI juga?",
    kata: "kotak ini chatbot bot chat widget kamu kamu siapa asisten robot llm gpt",
    a: [
      "Bukan. Kotak ini mencocokkan pertanyaan Anda ke daftar jawaban yang sudah ditulis, jadi ia cepat, gratis, dan tetap menjawab meski server analisisnya sedang mati.",
      "Yang benar-benar memakai model adalah bagian analisis ulasan - itulah tempat kemampuan AI produk ini dipakai, dan bukan untuk menjawab “ini gratis?”.",
    ],
    usul: ["tanya-jawab", "ai-apa"],
  },

  // ------------------------------------------------------------------ data & privasi
  {
    id: "privasi",
    q: "Data ulasan saya disimpan atau tidak?",
    kata: "privasi privacy aman keamanan simpan disimpan bocor rahasia data pribadi jual dijual server",
    a: [
      "Tidak disimpan. Data Anda hidup di memori selama sesi analisis dan hilang begitu Anda menutup halaman. Tidak ada basis data pengguna sama sekali.",
      "Itu ditegakkan arsitektur, bukan janji kebijakan: tidak ada tempat penyimpanan yang bisa dibocorkan, dan tidak ada aset data yang bisa dijual sekalipun ada yang menawar.",
      "Semua model juga berjalan lokal, jadi ulasan Anda tidak pernah dikirim ke layanan AI pihak ketiga.",
    ],
    usul: ["pii", "simpan-riwayat", "pasang-sendiri"],
  },
  {
    id: "pii",
    q: "Kalau di ulasan ada nomor HP atau alamat pelanggan?",
    kata: "pii nomor hp telepon alamat email data pribadi pelanggan sensitif redaksi sensor mask uu pdp",
    a: [
      "Disamarkan otomatis sebelum data itu dilihat model mana pun. Enam pola ditangani: email, nomor telepon Indonesia, nomor panjang seperti resi dan rekening, alamat, nama akun, dan tautan.",
      "Cara kerjanya mengganti, bukan menghapus - “hubungi 0812-3456-7890” jadi “hubungi [nomor telepon]”. Kalimatnya tetap terbaca sebagai kutipan bukti, dan Anda bisa melihat sendiri bahwa penyamarannya berjalan.",
      "Batas jujurnya: penyamaran berbasis pola tidak akan pernah menangkap 100%. Ia andal pada pola terstruktur, tetapi tidak menangkap nama orang yang ditulis biasa. Karena itu ia dipasangkan dengan kebijakan tanpa penyimpanan, bukan diandalkan sendirian.",
    ],
    usul: ["privasi", "simpan-riwayat"],
  },
  {
    id: "simpan-riwayat",
    q: "Kenapa hasil kemarin hilang waktu saya buka lagi?",
    kata: "riwayat history simpan hilang lagi kemarin sebelumnya tersimpan sesi session bandingkan bulan tren",
    a: [
      "Karena memang tidak ada yang disimpan. Tiap sesi mulai dari nol - itu konsekuensi langsung dari keputusan tidak menyimpan data pengguna.",
      "Akibatnya perbandingan antar-bulan hanya bisa dihitung kalau berkas yang Anda unggah sendiri memuat kolom tanggal.",
      "Riwayat antar-sesi ada di rencana pengembangan, tetapi butuh akun dan penyimpanan permanen - dua hal yang sengaja belum ada di versi ini.",
    ],
    usul: ["privasi", "akun", "langganan"],
  },
  {
    id: "akun",
    q: "Perlu daftar akun dulu?",
    kata: "akun daftar login masuk registrasi signup sign up email password kata sandi",
    a: [
      "Tidak perlu sama sekali. Buka halaman, masukkan ulasan, dapat hasil. Tidak ada pendaftaran, tidak ada kartu kredit, tidak ada verifikasi email.",
      "Konsekuensinya disebut jujur: karena tidak ada akun, tidak ada tempat menyimpan riwayat Anda.",
    ],
    aksi: { label: "Langsung coba", ke: "dashboard" },
    usul: ["biaya", "simpan-riwayat"],
  },
  {
    id: "pasang-sendiri",
    q: "Bisa dipasang di server saya sendiri?",
    kata: "pasang install self host hosting server sendiri lokal offline docker compose deploy internal",
    a: [
      "Bisa. Seluruh sistem berjalan dari satu perintah docker compose, dan susunan yang sama itulah yang melayani demo publik.",
      "Karena semua model berjalan lokal tanpa API pihak ketiga, pemasangan sendiri berarti data binaan atau pelanggan Anda tidak pernah keluar dari mesin Anda. Itu relevan untuk pendamping UMKM dan organisasi yang datanya memang tidak boleh keluar.",
      "Kodenya terbuka dan panduan pemasangannya ada di README repositori.",
    ],
    usul: ["privasi", "repo"],
  },

  // ------------------------------------------------------------------ harga
  {
    id: "biaya",
    q: "Ini berbayar?",
    kata: "harga biaya bayar gratis langganan berlangganan free trial mahal murah tarif ongkos",
    a: [
      "Versi ini gratis, tanpa akun, tanpa batas percobaan.",
      "Gratisnya bukan subsidi sementara. Seluruh model berjalan di mesin yang menjalankan aplikasi ini, bukan lewat API berbayar per ulasan, jadi ongkos melayani satu penjual tinggal sekitar Rp1.330 sebulan.",
    ],
    usul: ["kenapa-gratis", "langganan", "akun"],
  },
  {
    id: "kenapa-gratis",
    q: "Kenapa gratis? Apa tangkapannya?",
    kata: "kenapa gratis tangkapan catch modal untung monetisasi bisnis model investor iklan jual data",
    a: [
      "Tidak ada tangkapannya, dan tidak ada iklan. Ongkos melayani satu penjual sekitar Rp1.330 per bulan - hitungannya diturunkan dari benchmark yang kami ukur sendiri, dan angkanya terbuka di dokumentasi.",
      "Yang membuatnya semurah itu: model berjalan lokal, jadi ongkos tidak naik bersama jumlah pemakaian seperti kalau memanggil API berbayar per ulasan.",
      "Dua hal yang sengaja tidak kami lakukan: menjual data pengguna - mustahil, tidak ada yang disimpan - dan memasang iklan, karena perkakas yang menyarankan prioritas kerja kehilangan kredibilitasnya begitu urutannya bisa dibeli.",
    ],
    aksi: { label: "Lihat hitungannya", ke: "#nilai" },
    usul: ["biaya", "langganan", "privasi"],
  },
  {
    id: "langganan",
    q: "Nanti bakal jadi berbayar?",
    kata: "langganan berlangganan premium pro upgrade nanti masa depan rencana berbayar tingkat paket",
    a: [
      "Rencananya ada tingkat berlangganan sekitar Rp39.000 sebulan untuk riwayat antar-periode, multi-toko, dan ekspor. Angka itu masih hipotesis - belum ada satu pun wawancara kesediaan membayar, dan kami menuliskannya begitu di dokumentasi.",
      "Yang penting: fitur berbayarnya persis daftar rencana pengembangan, yaitu hal-hal yang memang butuh akun dan penyimpanan. Yang gratis tetap utuh sebagai produk, bukan versi lumpuh yang memaksa naik tingkat.",
    ],
    usul: ["kenapa-gratis", "belum-bisa"],
  },

  // ------------------------------------------------------------------ batas & meta
  {
    id: "belum-bisa",
    q: "Apa yang belum bisa dilakukan?",
    kata: "belum bisa batas batasan limitasi kekurangan kelemahan lemah rencana roadmap nanti akan datang",
    a: [
      "Empat hal utama: menilai kondisi barang dari foto (diuji, belum lolos), riwayat antar-sesi, multi-toko dengan pembagian akses tim, dan menarik ulasan langsung dari marketplace tanpa ekspor manual.",
      "Masing-masing ada alasan teknisnya, bukan sekadar “segera hadir”. Daftar lengkapnya beserta alasannya ada di tab Roadmap setelah analisis selesai.",
      "Kami menulis batas ini terbuka karena perkakas yang menyembunyikan kelemahannya akan ketahuan pada percobaan pertama.",
    ],
    usul: ["foto-barang", "simpan-riwayat", "tarik-otomatis"],
  },
  {
    id: "tarik-otomatis",
    q: "Bisa tarik ulasan langsung dari marketplace saya?",
    kata: "tarik otomatis integrasi api koneksi hubungkan connect sinkron sambung scraping langsung shopee tokopedia lazada tiktok bukalapak marketplace",
    a: [
      "Belum. Versi ini bekerja dari berkas yang Anda ekspor sendiri atau tangkapan layar.",
      "Alasannya bukan teknis semata: status legal pengambilan data otomatis dari marketplace masih setengah terverifikasi, dan kami memilih tidak membangun fitur yang dasarnya belum jelas.",
    ],
    usul: ["format-data", "belum-bisa"],
  },
  {
    id: "repo",
    q: "Kodenya terbuka? Di mana dokumentasinya?",
    kata: "kode source code github repo repositori open source dokumentasi dokumen readme lisensi teknis",
    a: [
      "Terbuka. Repositorinya memuat seluruh kode, panduan pemasangan, catatan keputusan arsitektur, kartu model beserta metriknya, kartu dataset, daftar keterbatasan, dan dokumen nilai bisnis lengkap dengan hitungan ongkosnya.",
      "Termasuk yang biasanya tidak dipublikasikan: gate pengujian yang tidak lulus, beserta angkanya.",
    ],
    usul: ["pasang-sendiri", "akurat"],
  },
];

/** Pertanyaan yang ditawarkan lebih dulu sebelum pengguna mengetik apa pun. Empat ini dipilih
 *  karena mewakili empat kekhawatiran pertama yang berbeda - apa ini, bagaimana memakainya,
 *  data saya bagaimana, dan berapa bayarnya - bukan empat entri yang kebetulan paling atas. */
export const PEMBUKA = ["apa-itu", "cara-pakai", "privasi", "biaya"];
