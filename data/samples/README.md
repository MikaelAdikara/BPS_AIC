# Dataset demo bawaan (ING-04)

`demo_reviews.csv` - 120 ulasan fesyen, mengikuti schema Raw Review (blueprint bagian 25.1).
Disertakan di repositori supaya siapa pun dapat mencoba sistem tanpa menyiapkan data sendiri.

Dihasilkan ulang lewat:

```bash
python scripts/build_sample_dataset.py
```

## Asal data dan lisensi

Teks ulasan diambil **apa adanya** dari Tokopedia Product Reviews 2019
(`farhamu/tokopedia-product-reviews-2019`, **Apache-2.0**) - tanpa normalisasi, sehingga typo,
singkatan, dan gaya bahasa aslinya tetap utuh. Ini disengaja: demo yang memakai kalimat
"rapi" tidak akan menunjukkan tantangan sebenarnya.

## Yang DISINTESIS - wajib dibaca sebelum mengutip angka demo

| Field | Status | Keterangan |
| --- | --- | --- |
| `text`, `rating`, `product_id`, `product_name` | **asli** | Dari dataset sumber |
| `timestamp` | **SINTETIS** | Dataset sumber tidak memuat tanggal |
| `variant` | kosong | Tidak tersedia di sumber |
| `image_paths` | kosong | Diisi pada Fase 3, setelah foto validasi tersedia |

**Tanggal disintesis dengan sengaja tidak acak:** keluhan ukuran dipadatkan pada 30 hari
terakhir, sisanya tersebar 30–90 hari ke belakang, supaya fitur tren (`AspectAggregate.trend`)
punya sesuatu untuk ditampilkan saat demo.

Konsekuensinya harus disebut terang-terangan: **tren "meningkat" pada demo adalah properti
dataset demo yang kami rancang, bukan temuan tentang perilaku pasar.** Angka tren dari berkas
ini tidak boleh dikutip di proposal maupun video sebagai temuan.

## Komposisi

Dikurasi, bukan diambil acak - satu batch harus mampu memicu seluruh kapabilitas sistem
(blueprint bagian 42.1). Statistik lengkap ada di `composition.json`.

| Elemen | Target bagian 42.1 | Tercapai |
| --- | --- | --- |
| Total ulasan | - | 120 |
| Bahasa informal | ≥30% | 31% |
| Keluhan berulang satu aspek | ada | `ukuran_varian` - 31 penyebutan, mayoritas negatif |
| Pujian jelas aspek lain | ada | `pengiriman` - 53 penyebutan, mayoritas positif |
| Aspek berbeda terwakili | ada | 9 dari 11 aspek muncul |
| Kategori punya baseline benchmark | ada | seluruhnya `fashion` |
| Foto jelas / foto blur / kontradiksi | ada | **belum** - menunggu Fase 3 |

Dua aspek yang tidak muncul (`rasa_kualitas_makanan`, `kelengkapan`) memang tidak relevan atau
sangat jarang pada kategori fesyen - ini perilaku taksonomi yang benar, bukan kekurangan data.

## Privasi

Baris yang memuat pola PII (nomor telepon, email, alamat jalan, nomor identitas) **dibuang**
saat kurasi, bukan diredaksi. Untuk berkas kecil yang di-commit ke repositori publik, membuang
lebih aman daripada mengandalkan redaksi yang mungkin tidak sempurna.

Ini terpisah dari `redact_personal_data()` yang berjalan pada data pengguna saat runtime
(GOV-01, Fase 5).

## Yang belum lengkap

Slot foto masih kosong. Setelah foto validasi tersedia pada Fase 3, tiga kasus wajib ditambahkan
agar demo dapat menunjukkan lapisan visual secara utuh:

1. Foto kerusakan yang jelas → VIS-01 memberi label dengan confidence tinggi
2. Foto blur/gelap → memicu **abstention** eksplisit
3. Teks positif + foto bermasalah → memicu **contradiction flag** dan `requires_human_review`

Kasus nomor 2 dan 3 justru yang paling penting ditunjukkan: keduanya membuktikan sistem jujur
saat tidak yakin, bukan hanya bekerja saat kondisinya ideal.
