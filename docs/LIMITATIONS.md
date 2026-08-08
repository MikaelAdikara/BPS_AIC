# Limitations

> **Placeholder (Fase 0).** Diisi bertahap seiring hasil evaluasi nyata muncul (Fase 3, 8).
> Blueprint bagian 43 mengatur batas klaim; dokumen ini adalah tempat keterbatasan ditulis
> apa adanya, bukan diperhalus.

## Keterbatasan yang sudah diketahui sejak desain

1. **Generalisasi zero-shot CLIP pada foto ulasan konsumen Indonesia belum terbukti.**
   Literatur pendukung berasal dari domain industri/manufaktur, bukan foto konsumen.
   Baru terjawab setelah go/no-go gate Fase 3 (blueprint bagian 19.3, 26.2).
2. **Baseline kategori bersifat historis dan statis**, bukan pemantauan kompetitor real-time,
   dan tidak sinkron periode dengan data pengguna (bagian 24.1).
3. **Dataset publik bias ke toko besar/aktif** — bukan representasi sempurna UMKM mikro
   (dossier bagian 14.2).
4. **Tidak ada riwayat lintas sesi pada Tier 1** — setiap sesi dimulai dari awal (ADR-010).
   Konsekuensinya, tren antar periode tidak dapat dihitung dari data historis pengguna.
5. **Rekomendasi adalah saran berbasis pola data, bukan kebenaran mutlak** — tombol tolak ada
   justru karena ini (bagian 43.3).
6. **Status legal scraping Apify: PARTIALLY VERIFIED**, bukan klaim aman mutlak
   (dossier bagian 21B.6.3).
7. **Cakupan bahasa daerah terbatas** pada campuran yang muncul di dataset yang tersedia,
   bukan seluruh bahasa daerah Indonesia.

## Keterbatasan yang ditemukan saat implementasi

### Severity adalah proksi dari rating, bukan ukuran dampak (Fase 4)

`severity` per keluhan diturunkan dari rating ulasan: bintang ≤2 → tinggi, 3 → sedang, ≥4 →
rendah. Konsekuensinya, keluhan nyata yang muncul di dalam ulasan berbintang tinggi
("bagus, tapi kekecilan") tercatat sebagai ringan meski masalah produknya sama saja.

Ini terlihat langsung pada dataset demo: `ukuran_varian` adalah aspek dengan keluhan terbanyak
(25 dari 120 ulasan) dan 18 poin persentase di atas baseline kategori, namun severity tipikalnya
hanya "sedang" karena banyak keluhan ukuran datang dari pembeli yang tetap memberi bintang 4–5.

Sistem tidak menyembunyikan ini — skor prioritas tetap menempatkannya di urutan pertama karena
frekuensi dan gap benchmark, dan `priority_reasoning` menyebut angka-angka itu apa adanya.
Tetapi severity **tidak boleh dibaca sebagai ukuran keparahan dampak bisnis**.

Perbaikan yang tepat adalah memprediksi severity dari teks, bukan menurunkannya dari rating —
tidak dikerjakan pada Tier 1 karena membutuhkan label severity dari manusia yang belum tersedia.

### Tren hanya tersedia bila data punya timestamp (Fase 4)

Dataset publik yang dipakai melatih tidak memuat tanggal, sehingga `trend` pada data nyata
selalu `tidak_cukup_data`. Tren hanya dapat dihitung bila data pengguna menyertakan timestamp.
Sistem melaporkan `tidak_cukup_data` alih-alih menebak "stabil" — menebak akan menyiratkan
sistem sudah memeriksa dan tidak menemukan perubahan.

### Bahasa daerah dan Inggris ditangani buruk — terukur (Fase 2)

Blueprint bagian 42.1 mengandaikan sistem tahan terhadap "campuran bahasa daerah". Diuji pada
NusaX-senti (expert-generated), klaim itu **tidak bertahan**:

| Bahasa | Leksikon | TF-IDF | IndoBERT |
| --- | --- | --- | --- |
| Indonesia | 0,686 | 0,396 | 0,519 |
| Inggris | 0,298 | 0,336 | 0,411 |
| Jawa | 0,477 | 0,435 | 0,434 |
| Sunda | 0,355 | 0,296 | 0,351 |
| Minang | 0,434 | 0,355 | 0,382 |

Tidak satu pun pendekatan menangani bahasa daerah dengan baik. Ulasan berbahasa Inggris juga
lemah, padahal **11,2% klausa pada data kami memuat kata Inggris** dan 6,5% didominasi Inggris —
"recommended seller", "packing bagus", "order 2 pcs barang working semua".

Satu bug konkret yang sudah teridentifikasi: penanda negasi hanya memuat bentuk Indonesia
(tidak/bukan/belum/jangan/tanpa/kurang), sehingga **"kualitas not oke" terbaca positif**.

Konsekuensi untuk klaim: sistem boleh disebut menangani **Bahasa Indonesia informal termasuk
slang dan typo** — itu terukur. Sistem **tidak boleh** disebut menangani bahasa daerah, dan
dukungan bahasa Inggris harus disebut terbatas.

### Bukti ditampilkan utuh, sehingga kadang terbaca positif (Fase 5)

Klasifikasi berjalan di tingkat **klausa**, tetapi bukti diindeks dan ditampilkan di tingkat
**ulasan utuh** (blueprint bagian 21.1: kutipan sepotong justru mengurangi kepercayaan).

Konsekuensinya terlihat pada ulasan campuran. Sebuah ulasan yang memuji pelayanan tetapi
mengeluh soal kualitas akan sah menjadi bukti untuk Action Card kualitas — namun kutipan yang
tampil adalah keseluruhan ulasannya, yang bisa terbaca positif sekilas.

Bukti sudah difilter agar hanya ulasan yang benar-benar memuat keluhan pada aspek itu yang
dipilih (tanpa filter ini, kartu "perbaiki keterangan ukuran" sempat mendapat kutipan
"warna/ukuran sesuai"). Yang belum dilakukan adalah menyorot klausa keluhannya di dalam kutipan.
Itu pekerjaan frontend pada Fase 6 dan tercatat sebagai perbaikan yang direncanakan, bukan
sebagai sesuatu yang sudah beres.

## Keterbatasan fitur Tier 1 yang baru dibangun

**Tanya jawab hanya mengenali satu topik per pertanyaan.** `_detect_aspect()` memilih aspek
dengan kata kunci terbanyak, sehingga "bagaimana pengiriman dan kemasannya?" dijawab untuk salah
satunya saja. Pertanyaan majemuk, perbandingan antar periode, dan pertanyaan lanjutan ("kenapa
begitu?") belum ditangani.

**Penjaga pertanyaan di luar domain lebih mudah menolak pada batch kecil.** Penjaganya
membandingkan kata pada pertanyaan dengan kosakata ulasan pengguna. Batch 10 ulasan hanya
memuat beberapa puluh kata unik, sehingga pertanyaan yang sebenarnya wajar dapat ikut ditolak.
Arah kegagalan ini dipilih sadar: penolakan terlihat oleh pengguna dan dapat diperbaiki, jawaban
keliru yang disertai kutipan meyakinkan tidak.

**Pemenggal imbuhan pada penjaga domain tidak menangani peluluhan bunyi.** "pengiriman" menjadi
"irim", bukan "kirim", karena huruf yang luluh tidak dapat dipulihkan tanpa menebak. Yang
dibutuhkan penjaga hanyalah konsistensi antara pertanyaan dan korpus, sehingga ini tidak
merugikan — efeknya hanya membuat penjaga sedikit lebih ketat.

**OPP-01 memakai ambang tetap, belum dikalibrasi.** Aspek disebut "dipuji" bila ≥70% sebutannya
positif dan disebut minimal 5 kali. Kedua angka ini ditetapkan dari penalaran, bukan dari
pengujian terhadap penilaian manusia tentang apa yang pantas disebut kekuatan toko.

**Skor kualitas data (ING-05) adalah heuristik, bukan ukuran tervalidasi.** Bobot penaltinya
(−35 untuk <15 ulasan, −20 untuk rating/tanggal yang banyak kosong) dipilih agar urutannya masuk
akal, dan belum pernah diuji terhadap seberapa akurat hasil analisis sebenarnya pada tiap
tingkat. Skornya sebaiknya dibaca sebagai peringatan relatif, bukan sebagai probabilitas.

**Unggahan foto belum ada di antarmuka.** Skema `ReviewImage` dan `VisualPrediction` sudah siap
dan panel temuan visual sudah terpasang, tetapi endpoint unggah gambar maupun model visual
terlatih belum ada (lihat butir 1 di atas). Layar pertama menyatakan hal ini apa adanya alih-alih
menyediakan slot yang tidak berfungsi.

## Keterbatasan yang baru dapat diisi setelah pengujian

_Diisi setelah Fase 3 dan Fase 8 — kosong sampai ada angka nyata._
