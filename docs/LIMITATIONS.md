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

## Keterbatasan yang baru dapat diisi setelah pengujian

_Diisi setelah Fase 3 dan Fase 8 — kosong sampai ada angka nyata._
