# Suite komponen (data/eval)

Commit `bfb21ff`, engine `gap-v1.10` / `verify-v2.3`. Deterministik, tanpa model. Label dari `data/eval/` (asal per baris di berkas itu). Format sel: `k/n (persen; interval Wilson 95%)`.

Pembanding: sinyal keluhan engine Deciqo (menentukan ulasan mana masuk triage) dan leksikon Ulasin as-shipped. Aspek hanya dinilai untuk kemasan, pengiriman, ukuran, dan layanan penjual, yang padanannya di engine jelas.

## s01 · Kemasan + kerusakan dalam satu klausa

| Sistem | Metrik | Hasil |
|---|---|---|
| deciqo_lexicon | complaint_recall | 19/21 (90%; 71–97) |
| deciqo_lexicon | control_specificity | 3/3 (100%; 44–100) |
| deciqo_lexicon | aspect_hit | 17/17 (100%; 82–100) |
| ulasin_lexicon | complaint_recall | 11/21 (52%; 32–72) |
| ulasin_lexicon | control_specificity | 3/3 (100%; 44–100) |
| ulasin_lexicon | aspect_hit | 12/17 (71%; 47–87) |

Contoh kegagalan Deciqo (maks. 8 per metrik):

- `complaint_recall` KP07: segelnya sudah terbuka waktu diterima
- `complaint_recall` KP10: tidak pakai bubble wrap sama sekali

## s02 · Negasi Inggris, Singlish, dan campuran

| Sistem | Metrik | Hasil |
|---|---|---|
| deciqo_lexicon | complaint_recall | 55/68 (81%; 70–88) |
| deciqo_lexicon | control_specificity | 33/34 (97%; 85–99) |
| deciqo_lexicon | aspect_hit | 39/42 (93%; 81–98) |
| ulasin_lexicon | complaint_recall | 11/68 (16%; 9–27) |
| ulasin_lexicon | control_specificity | 33/34 (97%; 85–99) |
| ulasin_lexicon | aspect_hit | 32/42 (76%; 61–87) |

Contoh kegagalan Deciqo (maks. 8 per metrik):

- `complaint_recall` EN12: Took two weeks to arrive with no update
- `complaint_recall` EN13: Courier left it outside without knocking
- `complaint_recall` EN19: Battery drains very fast
- `complaint_recall` EN20: Stopped charging after a week
- `complaint_recall` MN25: took two weeks to arrive
- `complaint_recall` ER09: Delivery took almost two weeks with no update.
- `complaint_recall` ER20: Ordered two, only one arrived.
- `complaint_recall` ER23: Description says waterproof, it is not.
- `control_specificity` MN06: shipping not fast but ok lah
- `aspect_hit` ER20: Ordered two, only one arrived.
- `aspect_hit` ER33: Fast response but the item was out of stock after payment.
- `aspect_hit` ER40: Item ok but delivery guy was rude.

## s03 · Keluhan di ulasan bintang 4–5 dan kontrolnya

| Sistem | Metrik | Hasil |
|---|---|---|
| deciqo_lexicon | complaint_recall | 9/12 (75%; 47–91) |
| deciqo_lexicon | control_specificity | 8/9 (89%; 56–98) |
| deciqo_lexicon | same_label_any_rating | 21/21 (100%; 85–100) |
| ulasin_lexicon | complaint_recall | 0/12 (0%; 0–24) |
| ulasin_lexicon | control_specificity | 8/9 (89%; 56–98) |

Contoh kegagalan Deciqo (maks. 8 per metrik):

- `complaint_recall` SHP95734159145: alhamdulillah pket dah sampe, pas di badan suka sma baju nya, kaos yg 
- `complaint_recall` SHP80405302429: Bahan:lumayan Desain:oke Tekstur:lembut Pengemasan dan pengiriman cepe
- `complaint_recall` SM05: Barang sesuai. Tapi estimasi 3 hari jadi 8 hari.
- `control_specificity` SHP78252741100: Barang nya cepet banget sampe nya pesen hari Senin Selasa nya udh samp

## s04 · Input aneh di parser tempel dan sinyal keluhan

| Sistem | Metrik | Hasil |
|---|---|---|
| deciqo_ingest | no_crash | 36/36 (100%; 90–100) |
| deciqo_ingest | empty_gives_zero_reviews | 2/2 (100%; 34–100) |

## s10 · Redaksi PII fiktif di pintu ingest

| Sistem | Metrik | Hasil |
|---|---|---|
| deciqo_ingest | required_pii_masked | 17/17 (100%; 82–100) |
| deciqo_ingest | known_gap_masked | 2/2 (100%; 34–100) |
| deciqo_ingest | no_false_redaction | 3/3 (100%; 44–100) |
| deciqo_ingest | optional_masked_info | 4/6 (67%; 30–90) |

Contoh kegagalan Deciqo (maks. 8 per metrik):

- `optional_masked_info` P05 (tracking_no): Nomor resi JP1234567890 belum update
- `optional_masked_info` P21 (postal_code): Kode pos 60119, alamat sudah benar

## f01 · Validasi jawaban fakta merchant (probe)

| Sistem | Metrik | Hasil |
|---|---|---|
| deciqo_facts | invalid_answer_rejected | 10/10 (100%; 72–100) |
| deciqo_facts | valid_answer_accepted | 5/5 (100%; 57–100) |

## Tidak dijalankan

- s05 narasi + verifier: kasus menguji narasi Ulasin (kata eksekusi, perbandingan kurir) yang tidak ada di alur Deciqo; gerbang angka Deciqo diuji lewat kasus `eval/final/cases.jsonl` dan tes unit engine.
- s07 Q&A, s08 alert timeline, s11/s12 toko demo: dipakai untuk demo dan tes platform, bukan metrik engine di sini.
- s10 jenis tanpa detektor residu (nama, handle): lolos bila teks berubah; ini batas bawah yang longgar.
