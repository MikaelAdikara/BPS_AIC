# data/samples — dataset demo

Tiga berkas, seluruhnya berisi **teks ulasan nyata**. Tidak ada yang dikarang.

| Berkas | Isi | Asal |
| --- | --- | --- |
| `demo_reviews.csv` | 120 ulasan | Teks nyata dari dataset publik (PRDECT-ID dkk), **dikurasi** agar satu batch memicu seluruh kapabilitas sistem |
| `demo_shopee_asli.csv` | 66 ulasan | **Scraping sendiri** dari dua listing Shopee nyata, Okt 2025 - Agu 2026, via Apify. Tidak disaring |
| `demo_toko_fashion.csv` | 55 ulasan | **Disintesis** untuk menguji alur. Jangan dipakai sebagai bukti kegunaan nyata |

## Perbedaan yang menentukan saat demo

`demo_reviews.csv` **dikurasi** — dipilih supaya Action Card, temuan kekuatan, dan pembanding
kategori semuanya muncul. Bagus untuk menunjukkan kapabilitas, tetapi juri yang jeli berhak
bertanya apakah datanya dipilih agar terlihat bagus. Jawabannya: ya, dan itu ditulis apa adanya
di sini.

`demo_shopee_asli.csv` **tidak disaring**. Ia mentah, penuh singkatan dan typo, dan hasilnya
lebih berantakan — beberapa kutipan bukti tidak persis cocok dengan judul kartunya. Justru itu
nilainya: ia membuktikan sistem bekerja pada kenyataan, bukan pada data yang sudah dirapikan.

## Privasi pada `demo_shopee_asli.csv`

Nama akun, URL foto profil, dan data ukuran tubuh (tinggi/berat/pinggang/dada/bahu) yang ikut
terbawa scraping **tidak disertakan**. Teks ulasannya melewati `redact_personal_data()` yang
sama dengan yang dipakai aplikasi. Kewajiban UU PDP berlaku sama baik data berasal dari dataset
publik maupun hasil scraping sendiri (dossier bagian 21B.6.3).
