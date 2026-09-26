# Data demo multi-toko — cara menyiapkan (manual, tanpa skrip)

Tujuan: satu berkas per toko, supaya demo multi-store memakai **ulasan asli**, bukan karangan.

## Komposisi yang dituju

| Toko | Kanal | Sumber | Jumlah | Catatan |
|---|---|---|---|---|
| Store A | Shopee | `data/samples/demo_shopee_asli.csv` | 66 | ulasan asli hasil scraping sendiri, tidak disaring |
| Store B | Tokopedia | `data/raw/tokopedia_reviews_2019` | ~150 | satu `shop_id` kategori fashion |
| Store C | Tokopedia | `data/raw/tokopedia_reviews_2019` | ~150 | `shop_id` fashion yang berbeda |

Dataset Tokopedia 2019 punya kolom `shop_id`: 158 toko, 77 toko dengan ≥30 ulasan, dan empat
toko fashion dengan 800–1.300 ulasan.

## Langkah (spreadsheet, bukan kode)

1. Buka `tokopedia-product-reviews-2019.csv` di spreadsheet.
2. Filter `category = fashion`.
3. Urutkan menurut `shop_id`, pilih dua `shop_id` dengan jumlah ulasan terbanyak.
4. Untuk tiap toko, salin sekitar 150 baris pertama ke berkas baru:
   `store_b_tokopedia.csv` dan `store_c_tokopedia.csv`.
5. Tambahkan dua kolom di tiap berkas: `store` (nama toko demo) dan `channel` (`tokopedia`).
6. Untuk Store A, salin `demo_shopee_asli.csv` lalu tambahkan `store` dan `channel=shopee`.
7. Simpan ketiganya di folder ini.

**Jangan memakai skrip Python atau notebook untuk menyaring.** Filter spreadsheet cukup, dan itu
termasuk "menyiapkan data uji" yang diizinkan.

## Yang harus muncul di demo

- Satu aspek yang sama muncul di **dua toko berbeda** → kartu gabungan.
- Minimal satu ulasan bintang 4–5 yang isinya keluhan → bukti wedge kompetitif.
- Satu toko dengan ulasan sangat sedikit → memicu label "not enough data".

Periksa ketiganya secara manual setelah berkas jadi, dan catat nomor barisnya di
`multistore_expectations.md` supaya saat demo tidak perlu mencari.

## Yang wajib diucapkan saat demo

> "These are three real stores from public data, presented as if one seller owned all three. The
> Tokopedia data is from 2019."

Jangan pernah menyebutnya sebagai data pelanggan nyata milik satu penjual.
