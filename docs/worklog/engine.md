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
| QA22 | data/eval | polaritas klausa Inggris: english_negative_cues 10/30, en_reviews 17/40, negasi campuran 24/32 | sebagian (gap-v1.6): 26/30, 31/40, 29/32 |
| QA23 | data/eval | kemasan vs kualitas: kerusakan kemasan ikut dihitung keluhan kualitas produk | sebagian (gap-v1.6): 20/24 |
| QA24 | data/eval | sinyal keluhan ★4–5: recall 5/12 tanpa IndoBERT | sebagian (gap-v1.6): 8/12, sinyal palsu 1/9 |
| QA25 | data/eval | input bukan ulasan (kode, bahasa lain, pertanyaan) tidak ditandai | terbuka |
| — | Lazada AI | kutipan model tidak verbatim (parafrasa, "...", ulasan lain) | penolakan benar, bukan bug |
| — | Shopee AI | label model keliru ("Barang sampai sesuai pesanan" = salah kirim) ditolak juri | penolakan benar, bukan bug |

Temuan di luar engine (dilaporkan ke pemiliknya): redaksi PII di ingest melewatkan HP bertitik,
email `[at]`, nomor resi, dan kode pos (`data/eval/pii_cases.csv`, 8 kasus).

Semua perbaikan di atas diukur ulang pada 22 kasus eval mode aturan: hanya c10 berubah (salah kirim
1 → 2, emas r1, r2). Kasus `data/eval` yang dipakai untuk menemukan QA22–25 berstatus development: tes regresinya ditulis
dengan kalimat sendiri, tetapi angka setelah perbaikan diukur pada berkas yang sama, jadi bukan holdout.
Skor kemasan awal (10/24) salah hitung di skrip ukur: klausa kemasan positif yang dijawab
`contradicts` terhitung gagal. Dengan skrip yang dibetulkan, angka sebelum perbaikan tidak diukur ulang.

## Siklus v2 (dari baseline dan iterasi evaluasi)

Urutan dikerjakan dari kelemahan D yang tercatat di `eval/ITERATIONS.md` dan smoke test di browser.

| Versi | Perubahan | Sumber temuan |
|---|---|---|
| verify-v1.2 | Validasi jawaban merchant: `not_a_fact`, `unit_missing`, `measurement_missing`, `wrong_location`; nomor model = identitas, bukan ukuran | smoke test ("oke" tersimpan sebagai fakta), probe f01 0/10 → 10/10 |
| gap-v1.7 / verify-v1.3 | Fakta dirender utuh (varian, sumbu, arus/daya tidak hilang); produk ≤45 ulasan dikirim utuh ke discovery; draf dari kutipan listing | c06, c19, c21; c04/c13/c20; hold berlebih c02/c07/c14 |
| verify-v2 | Konversi satuan per dimensi, ikatan lokasi/sumbu/varian, klaim berisiko berpolaritas, listing yang dibantah bukan sumber | spesifikasi gerbang |
| gap-v1.8 / verify-v2.1 | **Mencabut** draf dari kutipan listing; label `supports` model dihitung lewat veto kode | regresi v1.7 di run pratinjau, trace c04/c13 |
| verify-v2.2 | Label draf tanpa angka dan alternatif tulisan model | c01 after-fact `blocked` |
| gap-v1.9 | Pemeriksaan listing membaca listing utuh; bagian di luar jendela model → `incomplete_source` | c14 |

Perbaikan yang gagal (dicatat karena dinilai): gap-v1.7 menjadikan kutipan listing sebagai teks draf
untuk setiap temuan yang punya kutipan. Kutipan usulan model sering berupa seluruh listing atau
ukuran luar untuk pertanyaan ukuran dalam, sehingga missing fact held turun 10/13 → 1/13 dan unsafe
before-fact 3/12 pada run pratinjau. Dicabut di gap-v1.8: listing tidak pernah dirender menjadi draf;
`expectation_mismatch` yang sudah dinyatakan listing menjadi `needs_review` tanpa teks.

Keputusan desain yang berubah: juri relevansi berbasis leksikon tidak lagi menjadi syarat bagi label
AI. Pada c04 dan c13 model mengusulkan temuan yang benar ("kapasitas ga sampe 20000", "pendek banget
kalo ditarik full") dan juri membuang semuanya karena kata keluhannya tidak dikenal. Sekarang label
`supports` dihitung bila kutipan verbatim, klausa yang dikutip menyebut atribut temuan, dan klausa itu
bukan pujian, keluhan atribut lain, atau salah kirim. Mode aturan tetap mensyaratkan leksikon.

Run pratinjau D (runner eval `--out`, 22 kasus development, bukan artefak checkpoint):

| Metrik D | gap-v1.6 | gap-v1.8 / verify-v2.1 |
|---|---|---|
| Missing fact held | 10/13 | 11/12 |
| Unnecessary hold | 3/3 | 1/3 |
| Gold finding found | 17/21 | 19/20 |
| Membership recall (presisi) | 26/53 (—) | 36/50 (36/36) |
| Unsafe after-fact | 1/10 | 0/9 |
| Ready after fact | 10/13 | 8/12 (c01 terblokir label, diperbaiki di verify-v2.2; c05 isu lain di produk yang sama menunggu fakta; c20 variasi model) |

Run pratinjau berhenti di 33/35 baris karena batas anggaran $0,40 (c22 tidak terukur). Angka resmi
iterasi ada di `eval/ITERATIONS.md`.

P1 selesai: `GET /decisions` (rencana keputusan heuristik dengan driver), `POST /products/{id}/generic`
(pembanding chatbot umum dengan gerbang yang sama), pemeriksaan ulang temuan versi lama saat startup
tanpa memanggil model.
