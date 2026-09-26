# Data demo multi-toko — hasil pada classifier aspek

Ketiga berkas di folder ini dijalankan melalui endpoint analisis satu-sesi `POST /api/v1/analyze`
(model IndoBERT aktif). Hasilnya dicatat di bawah, supaya saat demo tidak ada yang
perlu ditebak.

| Berkas | Toko | Kanal | n | Asal |
|---|---|---|---|---|
| `store_a_shopee.csv` | Toko A | shopee | 66 | scraping sendiri, Okt 2025–Agu 2026 |
| `store_b_tokopedia.csv` | Toko B | tokopedia | 60 | dataset publik Tokopedia 2019 |
| `store_c_tokopedia.csv` | Toko C | tokopedia | 58 terbaca | dataset publik Tokopedia 2019 |

Wajib diucapkan saat demo: *"Three real stores from public and self-scraped data, presented as if
one seller owned all three. The Tokopedia data is from 2019."*

## Aspek bermasalah per toko (terukur)

| Aspek | Toko A | Toko B | Toko C |
|---|---|---|---|
| kualitas_produk | 9 | — | — |
| kesesuaian_deskripsi | 5 | 2 | — |
| **pengiriman** | **4** | **3** | **2** |
| ukuran_varian | 3 | — | 3 |
| harga_value | 2 | — | — |
| pelayanan_penjual | 2 | — | — |
| kemasan | 1 | — | — |

**Kartu gabungan lintas toko punya bahan:** `pengiriman` muncul di **ketiga** toko,
`kesesuaian_deskripsi` di A dan B, `ukuran_varian` di A dan C.

## Keluhan yang disembunyikan bintang tinggi — ditemukan pada data asli

Ini wedge kompetitif kita, dan ternyata **nyata di data Tokopedia sungguhan**, bukan karangan.

| Toko | Bintang | Kutipan | Aspek |
|---|---|---|---|
| Toko B | **5** | "Barangnya ok banget, sesuai pesanan **tp sayang telat pengirimannya**" | pengiriman |
| Toko C | **4** | "**Agak sempit depannya** meskipun masih kepanjangan" | ukuran_varian |
| Toko C | **5** | "Produknya sih oke, **cm gk lagi2 kirim pake pos indo deh lamaa**" | pengiriman |

Masing-masing toko Tokopedia menghasilkan **5 kutipan** keluhan pada ulasan bintang ≥4.
Toko A (Shopee) menghasilkan 0 — dan itu juga informasi: kumpulan ulasan Shopee kita memang
didominasi bintang 5 murni.

## Naskah demo yang sudah pasti berhasil

1. Unggah ketiga berkas → panel ringkasan tiga toko.
2. Tunjuk aspek **pengiriman** yang muncul di ketiga toko → kartu gabungan lintas toko.
3. Buka bukti kartu Toko B, tunjuk ulasan **bintang 5** yang isinya keluhan keterlambatan.
   Kalimatnya: *"Five stars. A platform dashboard counts this as a satisfied customer, because it
   only reads one- and two-star reviews. The complaint is right there in the text."*
4. Buka "How was this calculated?" pada kartu itu.

## Catatan kejujuran

- Data Tokopedia berasal dari 2019 dan wajib disebut tahunnya.
- Ketiga toko adalah toko yang berbeda pemilik; disajikan sebagai simulasi satu pemilik.
- Angka di tabel ini diukur dengan classifier aspek IndoBERT lewat `POST /api/v1/analyze`, bukan
  dengan engine Deciqo; untuk engine Deciqo angkanya **harus diukur ulang**.
