# data/eval — data uji

Isi folder ini **hanya CSV, JSON, dan catatan**. Tidak ada berkas kode; test suite yang membaca
berkas-berkas ini ada di `eval/`.

## Isi

| Berkas | Isi | n | Dipakai suite |
|---|---|---|---|
| `star_text_mismatch.csv` | Ulasan bintang 4–5 yang memuat keluhan, plus kontrol negatif | 21 | s03 |
| `kemasan_precedence.csv` | Klausa yang memuat kata benda kemasan dan kata kerusakan sekaligus | 24 | s01, s03 |
| `english_negative_cues.csv` | Klausa Inggris dan Singlish berlabel aspek dan sentimen | 30 | s02 |
| `mixed_negation.csv` | Campuran Indonesia–Inggris dan negasi | 32 | s02 |
| `en_reviews.csv` | Ulasan Inggris/Singlish berlabel | 40 | s02 |
| `robustness_inputs.csv` | Kosong, emoji, gibberish, injection, HTML, bahasa lain, bukan ulasan | 36 | s04 |
| `narration_cases.json` | Keluaran LLM tiruan + vonis verifier yang diharapkan | 16 | s05 |
| `qna_questions.csv` | Pertanyaan sederhana, majemuk, kuantitatif, luar domain | 36 | s07 |
| `alert_scenarios.csv` | Timeline dengan dan tanpa lonjakan | 10 | s08 |
| `pii_cases.csv` | Kasus PII **fiktif** di dalam teks ulasan | 24 | s10 |
| `woo_seed_reviews.csv` | Ulasan untuk toko WooCommerce demo, memuat deret lonjakan kemasan | 40 | demo, s12 |
| `multistore/README.md` | Cara menyusun tiga toko demo dari data asli, manual lewat spreadsheet | — | s11 |

## Asal data

| Penanda `source` | Artinya |
|---|---|
| `real-shopee` | Ulasan asli hasil scraping sendiri (Okt 2025–Agu 2026), sudah melewati redaksi PII. Diambil dari `data/samples/demo_shopee_asli.csv` dan **dipilih manual**, bukan dengan skrip |
| `real-tokopedia-2019` | Dataset publik Tokopedia 2019, dipilih manual lewat filter spreadsheet |
| `team-written` | Ditulis tim untuk menutup kasus yang jarang muncul di data nyata: injection, PII, input kosong, negasi campuran |

Seluruh kasus PII **fiktif**. Tidak ada data pribadi orang sungguhan.

## Kasus yang terbukti gagal pada classifier aspek

Diuji pada sistem yang berjalan, sebagai bahan temuan baseline. Barisnya ditandai di kolom
`notes`:

1. `"Kemasan rusak, kotaknya sobek di beberapa sisi"` → masuk **kualitas_produk**, bukan kemasan.
2. `"dusnya penyok waktu sampai"` (bintang 5) → tidak masuk aspek kemasan.
3. `"Material feels thin…"` dan `"Size runs small…"` → terbaca **netral**, tidak pernah tercatat
   sebagai keluhan.

## Catatan pemakaian

- Jangan mengubah berkas-berkas ini setelah baseline dijalankan. Kalau ada label yang keliru,
  perbaiki dan **jalankan ulang baseline**, lalu catat di `eval/FINDINGS.md`.
- Ambang keputusan tidak boleh dipilih menggunakan berkas di folder ini — gunakan split validasi
  terpisah.
