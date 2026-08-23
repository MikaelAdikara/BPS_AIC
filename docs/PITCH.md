# Pitch Ulasin - narasi, titik pembeda, dan naskah

Dokumen ini menjawab satu pertanyaan: **kenapa juri memilih Ulasin di antara 30+ tim?** Isinya
bukan daftar fitur - fitur ada di README - melainkan *bagaimana* fitur itu diceritakan supaya
terdengar berbeda. Dipakai untuk video promosi, video proof of work, pembukaan proposal, dan
sesi klarifikasi.

## Satu kalimat

> **Ulasin membaca 100% ulasan pelanggan, menunjuk tiga hal yang harus dikerjakan minggu ini,
> dan membuktikan setiap angkanya - sampai juri bisa mengalikannya sendiri.**

Kalimat itu memuat tiga klaim yang masing-masing bisa didemokan dalam 20 detik: *100%*
(laporan: 66 dari 66), *tiga hal* (kartu prioritas), *bisa dihitung ulang* (Buka Hitungannya).

## Titik pembeda - yang tidak dimiliki tim lain, dan kenapa tidak bisa ditiru semalam

| Titik | Apa yang dilihat juri | Kenapa tim lain tidak punya |
| --- | --- | --- |
| **Buka Hitungannya** | Klik satu kartu → klausa mentah → agregat → komponen rumus → aritmetika yang menghasilkan skor persis di kartu | Menuntut seluruh pipeline deterministik sejak hari pertama (ADR-011). Wrapper LLM tidak bisa menampilkan ini karena angkanya memang dikarang ulang tiap panggilan |
| **Hasil negatif yang dipublikasikan** | Gerbang visual NO-GO; aspek TIDAK LULUS pada label manusia; pembacaan LLM mengalahkan model sendiri - semuanya di MODEL_CARD dengan angka | Tim lomba menyembunyikan kegagalan. Juri industri tahu ini, dan kejujuran berangka adalah sinyal "bisa dipekerjakan" yang paling langka |
| **Berjalan tanpa API key** | `docker compose up` → jalan, di laptop juri, offline | Mayoritas tim bergantung pada kunci API yang harus juri sediakan sendiri |
| **Gagal dengan anggun, didemokan** | Cabut checkpoint → sistem tetap menganalisis dan `/readiness` menjelaskan apa yang mati | Tidak ada tim yang berani mendemokan mode gagalnya |
| **Dua fitur yang belum ada di pasar** | Draf balasan dengan `[keputusan Anda: ...]`; arsip antar-sesi tanpa database yang menolak menyebut "membaik" tanpa signifikansi | Keduanya lahir dari prinsip, bukan dari daftar fitur |
| **Bahasa Indonesia informal, diukur** | "zonk", "ngepas bgt", "tdk tembus pandang" terbaca; macro F1 sentimen 0,730 pada label manusia independen | Model yang di-fine-tune sendiri pada 96 ribu klausa marketplace - dan dievaluasi pada label yang bukan buatan sendiri |

## 30 detik (pembuka video promosi - JANGAN dibuka dengan "UMKM adalah tulang punggung ekonomi")

> Toko ini punya 66 ulasan. Pemiliknya sempat membaca sepuluh. Ulasin membaca 66-nya dalam 55
> detik - dan bilang: tiga belas pembeli mengeluhkan kualitas, tujuh bilang barangnya tidak sesuai
> deskripsi, tujuh lagi tidak dibalas chatnya. Inilah ulasan yang membuktikannya. Dan inilah
> *rumus* yang menghitungnya - silakan kalikan sendiri. Ulasin: setiap angka membawa buktinya.

## 2 menit (inti proposal / sesi klarifikasi)

1. **Masalah yang spesifik**, bukan besar: biaya platform naik per Januari 2026, pengaduan konsumen
   naik 200%, 80% pembeli membaca ulasan - dan keluhan yang berulang pelan-pelan tidak pernah
   terlihat oleh penjual yang membaca ulasan selagi sempat.
2. **Yang ada berhenti terlalu awal**: dashboard marketplace berhenti di rating; LLM API menjawab
   tanpa bisa dihitung ulang dan mengirim data keluar; yang mampu (Thematic, Birdeye) berharga
   jutaan per bulan dan berbahasa Inggris.
3. **Jembatan lima tahap** - ulasan → aspek+sentimen → bukti → prioritas → tindakan - dengan dua
   sifat: angka tidak pernah dikarang, sistem tidak pernah gagal total.
4. **Bukti, bukan klaim**: sentimen LULUS pada label manusia independen; aspek TIDAK LULUS dan
   kami tulis kenapa; gerbang visual dieksekusi kode, bukan diingat.
5. **Apa yang belum, dan rencananya** - ROADMAP_FINAL berspesifikasi. Tim yang tahu persis
   kelemahannya adalah tim yang akan menang hackathon 10 jam.

## Tiga keberatan yang pasti muncul, dan jawabannya

**"Kenapa tidak pakai ChatGPT saja?"** - Coba tanya dua kali "berapa persen keluhan ukuran?"; Anda
akan dapat dua angka. Ulasin satu angka, dengan rumus dan kutipannya, dihitung di mesin Anda,
tanpa data keluar. Dan ketika pembacaan LLM ternyata lebih baik untuk *satu* sub-tugas (aspek),
kami mengukurnya, menulisnya, dan memindahkan pengetahuannya ke model lokal - bukan memanggil API.

**"Ini overbuilt untuk MVP?"** - Satu alur: unggah → analisis sinkron → hasil. Tidak ada akun,
database, background job. Panel-panel lain hanyalah cara membaca satu hasil yang sama. Yang
dilarang rulebook memang tidak ada.

**"Akurasinya berapa?"** - Sentimen: macro F1 0,730 vs leksikon 0,700 pada label manusia
independen (NusaX + PRDECT-ID). Aspek: 0,58 pada 120 klausa berlabel manusia - **setara leksikon,
belum lulus**, dan kami yang pertama mengatakannya. Jawaban ini lebih kuat daripada "94%".

## Urutan demo proof of work (7 menit, tanpa cut)

1. `docker compose up` + `/api/v1/readiness` (30 dtk)
2. Coba data contoh - 66 ulasan Shopee asli → layar proses → Laporan (60 dtk)
3. Kartu #1 → **Buka Hitungannya** → kalikan di suara: "0,197 × 1 × 1,468 × 100 = 28,92" (60 dtk)
4. Draf balasan → tombol Salin terkunci sampai disunting (30 dtk)
5. Tanya jawab: satu pertanyaan wajar, satu pertanyaan saham yang ditolak (40 dtk)
6. OCR tangkapan layar / foto kamera → draf (40 dtk)
7. Unduh arsip → bandingkan → "belum berarti" (40 dtk)
8. **Cabut checkpoint, nyalakan ulang, analisis tetap jalan, `/readiness` jujur** (60 dtk)
9. Sebut yang belum sempurna: visual NO-GO, aspek TIDAK LULUS (30 dtk)

Semua fitur yang tampil di video promosi wajib ada di sini - rulebook.
