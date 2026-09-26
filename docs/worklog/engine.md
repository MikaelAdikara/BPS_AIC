# Worklog engine

## Checkpoint 1

Selesai dan terbukti (tes `tests/unit/test_deciqo_engine*.py`, `test_deciqo_gate.py`):

- Verifier kutipan: substring setelah normalisasi aman, tanpa fuzzy; pemisah desimal dipertahankan.
- Pemeriksa angka bersatuan di draf: angka dan satuan harus sama persis dengan sumber
  (`gap-v1`/`verify-v1` belum mengonversi satuan).
- Leksikon engine bersama (keluhan, pujian, negasi, kelompok atribut) dan juri relevansi berbasis kode.
  Rating tidak dipakai. Salah kirim dirutekan ke temuan operasional.
- Triage memakai klasifier IndoBERT yang sudah dimuat API bila ada, leksikon bila tidak;
  cache per `version_hash` ulasan + versi model.
- Analyser aturan (cadangan tanpa AI) dengan bentuk output yang sama dengan discovery.
- Discovery + membership lewat Responses API (structured output strict), reservasi anggaran,
  ledger per panggilan, respons `incomplete` = gagal, key ditolak → mode aturan berlabel.
- Pipeline: metrik dan severity dari kode, id temuan dari atribut yang dinormalisasi, rekonsiliasi,
  reopen hanya dari ulasan setelah `acted_at`, alert isu baru tanpa teks ulasan.
- Read model (inbox, summary, channels, products, product view) dan endpoint fakta, draf, keputusan.
- `harness.run_bundle` untuk runner eval.

Keputusan:

- Label model tidak pernah dihitung apa adanya: dukungan dihitung hanya bila kutipan verbatim
  dan juri relevansi setuju. Ini bisa membuang dukungan asli yang kosakatanya belum dikenal
  leksikon; dicatat sebagai risiko untuk diukur di eval.
- Anggaran habis ditangani seperti key ditolak (mode aturan berlabel), bukan analisis gagal,
  supaya merchant tetap melihat temuan yang cakupannya disebut jelas.

Belum (menunggu hasil baseline): konversi satuan, lokasi/sumbu/varian, klaim non-angka berpolaritas,
validasi fakta, pemeriksaan ulang temuan saat versi verifier berubah.

## Log QA engine

Engine dijalankan atas data yang masuk lewat ingest yang sama dengan aplikasi: snapshot Lazada
(10 produk, 517 ulasan), paket Shopee tim, Tokopedia 2019, Blibli/TikTok sintetis, dan `data/eval`.
Setiap kegagalan yang bisa direproduksi menjadi tes di `tests/unit/test_deciqo_engine_qa.py`
(nama `test_qaNN_*`). Status "terbuka" berarti belum diperbaiki.

### Biaya dan latensi mode AI (terukur)

| Data | Produk | Biaya | Latensi per produk |
|---|---|---|---|
| Snapshot Lazada, ±50 ulasan/produk | 10 | $0,135 | 40–67 detik (discovery ±20 s + membership ±25 s) |
| Shopee tim + Tokopedia 2019 + sintetis | 10 | $0,082 | 0–67 detik |

Analisis diserialkan satu lock, jadi "analyse all" 10 produk Lazada ±9 menit. UI perlu progres job.

### Kegagalan dan status

| Id | Sumber | Kegagalan | Status (versi) |
|---|---|---|---|
| QA01 | Lazada | "tahan lama", "baterainya lama" terbaca keluhan (kata "lama") | diperbaiki (gap-v1.1) |
| QA02 | Lazada | "pesanan sudah sampai", "dikirim barang rusak" terbaca salah kirim | diperbaiki (gap-v1.1) |
| QA03 | Lazada | "masuk di cas", "kapasitas besar", "longgar pas pengisian" terbaca keluhan ukuran | diperbaiki (gap-v1.1) |
| QA04 | Lazada | keluhan cacat yang menyebut "dikirim" terhitung keluhan pengiriman | diperbaiki (gap-v1.1) |
| QA05 | Lazada | templat "Label:isi" + emoji tidak dipecah per klausa | diperbaiki (gap-v1.1) |
| QA06 | Lazada | negasi tida/gx/eggk tidak dikenali | diperbaiki (gap-v1.1) |
| QA07 | Lazada | temuan "kualitas jahitan" menyalin bukti "kualitas produk" (isu kembar) | diperbaiki (gap-v1.1) |
| QA08 | Lazada | "Soft Case Laptop" tidak dikenali sebagai tas oleh analyser aturan | diperbaiki (gap-v1.1) |
| QA09 | Lazada | "malah di kirim" (kata depan terpisah); "dicas" tidak dikenali konteks baterai | diperbaiki (gap-v1.1) |
| QA10 | Lazada AI | juri menilai seluruh ulasan, bukan klausa yang dikutip: pujian di klausa lain membatalkan 23 label | diperbaiki (gap-v1.2) |
| QA11 | Lazada AI | kembung/bengkak/lobet, "ga penuh", "gk bsa" tidak terbaca keluhan baterai | diperbaiki (gap-v1.2) |
| QA12 | Lazada AI | "tidak sesuai pesanan", "merek tidak sesuai", dus vs isi beda tidak dikenali salah kirim | diperbaiki (gap-v1.2) |
| ID-1 | Review O1 | parafrasa atribut membuat isu baru; isu acted jadi not_detected, reopen tidak terjadi | diperbaiki (gap-v1.3) |
| ID-2 | Review O1 | dua isu kembar dengan bukti sama (tas laptop) | diperbaiki (gap-v1.3) |
| QA13 | Tokopedia | "tidak cepat rusak" terbaca keluhan | diperbaiki (gap-v1.4) |
| QA14 | Tokopedia | "2x lipat" terbaca ukuran lipat | diperbaiki (gap-v1.4) |
| QA15 | Tokopedia | "pecah ketika sampai" terbaca keluhan pengiriman | diperbaiki (gap-v1.4) |
| QA16 | Tokopedia | "tp" tidak memisah klausa kontras | diperbaiki (gap-v1.4) |
| QA17 | Shopee/Tokopedia | produk tanpa listing: draf needs_merchant_fact padahal next=paste_listing | diperbaiki (verify-v1.1) |
| QA18 | Shopee AI | kata cacat di label temuan (koyak, robek, noda) tidak menandai atribut | diperbaiki (gap-v1.5) |
| QA19 | Shopee AI | ejaan pesen/mesen/psen dan akhiran -nya melewatkan salah kirim | diperbaiki (gap-v1.5) |
| QA20 | Sintetis | triage leksikon melewatkan mengelupas/baret/luber/pertanyaan; rice cooker tidak pernah dianalisis | diperbaiki (gap-v1.5) |
| QA21 | Lazada | "order PB merk lain" (pembanding) terbaca salah kirim | diperbaiki (gap-v1.5) |
| QA22 | data/eval | polaritas klausa Inggris: 10/30 dan 17/40 benar | terbuka |
| QA23 | data/eval | kemasan vs kualitas: 10/24; "kemasan rusak, kotaknya sobek" juga dihitung kualitas | terbuka |
| QA24 | data/eval | sinyal keluhan ★4–5: recall 5/12 tanpa IndoBERT | terbuka |
| QA25 | data/eval | input bukan ulasan (kode, bahasa lain, pertanyaan) tidak ditandai | terbuka |
| — | Lazada AI | kutipan model tidak verbatim (parafrasa, "...", ulasan lain) | penolakan benar, bukan bug |
| — | Shopee AI | label model keliru ("Barang sampai sesuai pesanan" = salah kirim) ditolak juri | penolakan benar, bukan bug |

Temuan di luar engine (dilaporkan ke pemiliknya): redaksi PII di ingest melewatkan HP bertitik,
email `[at]`, nomor resi, dan kode pos (`data/eval/pii_cases.csv`, 8 kasus).

Semua perbaikan di atas diukur ulang pada 22 kasus eval mode aturan: hanya c10 berubah (salah kirim
1 → 2, emas r1, r2). Kasus `data/eval` yang dipakai untuk menemukan QA22–25 berstatus development.
