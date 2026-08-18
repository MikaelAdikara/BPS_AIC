# Input Apify - akuisisi foto ulasan

Berkas di folder ini adalah input yang dikirim ke actor **zen-studio/shopee-product-reviews-scraper**.
Disimpan supaya sumber dan cara pengambilan data dapat ditelusuri, sesuai kewajiban transparansi
pada dossier bagian 21B.6.3.

## Dua kekeliruan pada percobaan pertama (11 Agustus 2026)

**1. Format URL salah.** Skema input actor mendokumentasikan pola
`https://shopee.[domain]/product-i.[shop].[item]`. Yang dikirim adalah bentuk tautan berbagi
`https://shopee.co.id/product/{shop}/{item}?d_id=...`. Hasilnya actor mengembalikan produk yang
sama sekali berbeda - `itemId` pada keluaran tidak cocok dengan satu pun URL yang diminta.
Parameter pelacak (`d_id`, `uls_trackid`, `utm_content`) juga dibuang: ia tidak menunjuk produk
dan hanya menambah kemungkinan gagal parse.

**2. `starFilter: "all"` menghasilkan batch tanpa satu pun keluhan.** Dua puluh ulasan yang
kembali seluruhnya bintang lima. Untuk menguji kelas `produk_rusak`, `salah_kirim`, dan
`kemasan_rusak`, batch semacam itu tidak dapat menjawab apa pun - model yang selalu menjawab
"normal" akan terlihat sempurna.

`starFilter` hanya menerima **satu** nilai per run (`"all"`, `"5"`, `"4"`, `"3"`, `"2"`, `"1"`),
sehingga bintang rendah harus diambil lewat run terpisah.

## Urutan pengambilan

| Berkas | Tujuan | Kelas yang diharapkan |
| --- | --- | --- |
| `run1_bintang1.json` | Keluhan terberat - sumber utama foto bermasalah | produk_rusak, salah_kirim, kemasan_rusak |
| `run2_bintang2.json` | Keluhan sedang | idem |
| `run3_bintang3.json` | Keluhan ringan / campuran | campuran |
| - | Kelas `normal` **sudah terpenuhi** dari batch pertama (40 foto bintang 5) | normal |

Jalankan `run1` lebih dulu, periksa hasilnya, baru putuskan apakah `run2`/`run3` diperlukan.
Ulasan bintang rendah yang berfoto jauh lebih jarang daripada bintang lima, jadi jumlah yang
kembali kemungkinan kecil - itu wajar, bukan tanda kegagalan.

## Biaya

Tarif $3,99 per 1.000 ulasan, dan dengan `contentFilter: "with media"` hanya ulasan bermedia
yang ditagih. `maxReviewsPerProduct` diturunkan dari 500 ke 100 sebagai pagar: tiga produk kali
tiga run pada batas 500 berpotensi menembus kredit $5, sedangkan batas 100 menahan skenario
terburuk di sekitar $1,20 untuk seluruh tiga run.

## Setelah berkas hasil diunduh

```bash
python scripts/prepare_apify_photos.py path/ke/dataset.json
```

Skrip menolak melanjutkan bila batch seluruhnya berbintang tinggi atau berasal dari satu produk
saja - pemeriksaan itu ada justru karena kekeliruan di atas.
