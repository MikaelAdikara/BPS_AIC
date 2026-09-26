# Suite komponen (data/eval)

Commit `39c3780`, engine `gap-v1.7` / `verify-v1.3`. Deterministik, tanpa model. Label dari `data/eval/` (asal per baris di berkas itu). Format sel: `k/n (persen; interval Wilson 95%)`.

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
| deciqo_lexicon | complaint_recall | 54/68 (79%; 68–87) |
| deciqo_lexicon | control_specificity | 32/34 (94%; 81–98) |
| deciqo_lexicon | aspect_hit | 39/42 (93%; 81–98) |
| ulasin_lexicon | complaint_recall | 11/68 (16%; 9–27) |
| ulasin_lexicon | control_specificity | 33/34 (97%; 85–99) |
| ulasin_lexicon | aspect_hit | 32/42 (76%; 61–87) |

Contoh kegagalan Deciqo (maks. 8 per metrik):

- `complaint_recall` EN12: Took two weeks to arrive with no update
- `complaint_recall` EN13: Courier left it outside without knocking
- `complaint_recall` EN19: Battery drains very fast
- `complaint_recall` EN20: Stopped charging after a week
- `complaint_recall` MN19: the color is different from the picture
- `complaint_recall` MN25: took two weeks to arrive
- `complaint_recall` ER09: Delivery took almost two weeks with no update.
- `complaint_recall` ER20: Ordered two, only one arrived.
- `control_specificity` MN06: shipping not fast but ok lah
- `control_specificity` ER19: Bubble wrap was generous, nothing damaged.
- `aspect_hit` ER20: Ordered two, only one arrived.
- `aspect_hit` ER33: Fast response but the item was out of stock after payment.
- `aspect_hit` ER40: Item ok but delivery guy was rude.

## s03 · Keluhan di ulasan bintang 4–5 dan kontrolnya

| Sistem | Metrik | Hasil |
|---|---|---|
| deciqo_lexicon | complaint_recall | 8/12 (67%; 39–86) |
| deciqo_lexicon | control_specificity | 8/9 (89%; 56–98) |
| deciqo_lexicon | same_label_any_rating | 21/21 (100%; 85–100) |
| ulasin_lexicon | complaint_recall | 0/12 (0%; 0–24) |
| ulasin_lexicon | control_specificity | 8/9 (89%; 56–98) |

Contoh kegagalan Deciqo (maks. 8 per metrik):

- `complaint_recall` SHP95734159145: alhamdulillah pket dah sampe, pas di badan suka sma baju nya, kaos yg 
- `complaint_recall` SHP80405302429: Bahan:lumayan Desain:oke Tekstur:lembut Pengemasan dan pengiriman cepe
- `complaint_recall` SM04: Suka warnanya. Sayang jahitan bagian dalam agak berantakan.
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
| deciqo_ingest | required_pii_masked | 11/17 (65%; 41–83) |
| deciqo_ingest | known_gap_masked | 0/2 (0%; 0–66) |
| deciqo_ingest | no_false_redaction | 3/3 (100%; 44–100) |
| deciqo_ingest | optional_masked_info | 1/6 (17%; 3–56) |

Contoh kegagalan Deciqo (maks. 8 per metrik):

- `required_pii_masked` P04 (name): Atas nama Siti Rahma, pesanan INV/2026/0012345
- `required_pii_masked` P08 (name): Rekening BCA [nomor] a.n. Contoh Nama untuk refund
- `required_pii_masked` P10 (body_measurements): Tinggi 165 berat 55 muat nggak ya?
- `required_pii_masked` P16 (name): Kirim ulang ke rumah ibu saya, Ibu Sri, di Bandung
- `required_pii_masked` P19 (name): Saya Andi dari Surabaya, barang sampai cepat
- `required_pii_masked` P20 (phone_dotted): No HP 0812.3456.7890 (WA only)
- `known_gap_masked` P17 (phone_spelled): WA: nol delapan satu dua tiga empat lima enam
- `known_gap_masked` P18 (email_obfuscated): email: budi[at]example[dot]com
- `optional_masked_info` P04 (order_id): Atas nama Siti Rahma, pesanan INV/2026/0012345
- `optional_masked_info` P05 (tracking_no): Nomor resi JP1234567890 belum update
- `optional_masked_info` P16 (city): Kirim ulang ke rumah ibu saya, Ibu Sri, di Bandung
- `optional_masked_info` P19 (city): Saya Andi dari Surabaya, barang sampai cepat
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
