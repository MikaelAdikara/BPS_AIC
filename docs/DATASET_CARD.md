# Dataset Card

Status: **Fase 1 berjalan.** Verifikasi lisensi dan profiling dataset selesai; harmonisasi label
aspek tertahan menunggu keputusan (lihat bagian 6).

## 1. Dataset yang dipakai — lisensi TERVERIFIKASI

Menjawab open question #1 blueprint bagian 48 dan prasyarat bagian 26.1 langkah 2. Ketiga dataset
punya lisensi eksplisit di halaman sumbernya, diverifikasi lewat HuggingFace API pada 5 Agustus 2026.

| Dataset | Sumber kanonik | Lisensi | Ukuran | Peran |
| --- | --- | --- | --- | --- |
| PRDECT-ID | `ZakyF/PRDECT-ID` | **CC-BY-4.0** | 5.400 ulasan | Training inti + gold test |
| e-commerce-sentiment-bahasa-indonesia | `AIbnuHibban/e-commerce-sentiment-bahasa-indonesia` | **MIT** | 21.840 baris | lihat catatan §4 |
| Tokopedia Product Reviews 2019 | `farhamu/tokopedia-product-reviews-2019` | **Apache-2.0** | 40.607 ulasan | Training + domain testing |

**CC-BY-4.0 mewajibkan atribusi.** PRDECT-ID wajib disitir di proposal dan MODEL_CARD.md:
Sutoyo, R. dkk. _PRDECT-ID: Indonesian product reviews dataset for emotions classification tasks_,
Data in Brief (2022), arXiv:2406.10118.

Ketiganya permisif dan kompatibel dengan lisensi MIT repository ini. Dataset **tidak di-commit** —
diunduh ulang lewat `scripts/download_datasets.py` (bagian 31.1).

Mirror yang sengaja **tidak** dipakai: `SEACrowd/prdect_id` dan `SEACrowd/casa`/`hoasa` memakai
loading script yang menuntut `trust_remote_code` (risiko keamanan, bagian 36.1 "untrusted
serialized model"); `carant-ai/compiled-absa-indonesian` berstatus gated tanpa lisensi.

## 2. Skema asli tiap dataset

| Dataset | Kolom | Label yang tersedia |
| --- | --- | --- |
| PRDECT-ID | Category, Product Name, Location, Price, Overall Rating, Number Sold, Total Review, Customer Rating, Customer Review, Sentiment, Emotion | Sentiment **biner** (Positive/Negative), Emotion 5 kelas (Happy/Sadness/Fear/Love/Anger) |
| e-commerce-sentiment | comment, rating, sentiment (+ category pada `challange.json`) | Sentiment **3 kelas**; `category` = jenis fenomena linguistik, **bukan** aspek produk |
| Tokopedia 2019 | text, rating, category, product_name, product_id, sold, shop_id, product_url | **tidak ada label sentimen** — hanya rating 1–5 |

## 3. Profiling data nyata

| Metrik | PRDECT-ID | Tokopedia 2019 |
| --- | --- | --- |
| Baris | 5.400 | 40.607 |
| Produk unik | 1.308 | 3.664 (158 toko) |
| Median ulasan/produk | 3 | 2 |
| Duplikasi teks | 1,8% | 8,1% |
| Distribusi rating | 5★ 40%, 1★ 34% | 5★ 75%, 4★ 19% |
| Kategori produk | 29 kategori | 5 (elektronik, fashion, olahraga, handphone, pertukangan) |

Keduanya mendukung **product-level split** (bagian 26.1 langkah 6) — jumlah produk unik memadai.
Tokopedia sangat condong positif (75% bintang 5), sesuai dugaan imbalance pada dossier 14.2;
mitigasi memakai class weighting, bukan oversampling naif.

**Sinyal aspek pada data nyata** (probe leksikon naif, bukan labeling function final):

| Aspek | PRDECT-ID | Tokopedia |
| --- | --- | --- |
| pengiriman | 37,4% | 35,4% |
| kualitas_produk | 32,1% | 26,9% |
| pelayanan_penjual | 24,1% | 20,3% |
| kesesuaian_deskripsi | 22,0% | 28,7% |
| kemasan | 16,9% | 8,5% |
| ukuran_varian | 10,6% | 3,5% |
| harga_value | 10,4% | 6,1% |
| kelengkapan | 10,3% | 2,5% |
| keaslian | 5,7% | 3,1% |
| kemudahan_penggunaan | 4,8% | 1,7% |
| rasa_kualitas_makanan | 4,5% | 0,9% |
| **≥1 aspek terdeteksi** | **84%** | **75%** |
| Rata-rata aspek/ulasan | 1,79 (54% punya ≥2) | 1,37 (42% punya ≥2) |

Artinya taksonomi 11 aspek memang tercermin di data nyata, dan sifat **multi-label** pada bagian 18.1
terkonfirmasi secara empiris — bukan asumsi.

## 4. Catatan kualitas: `e-commerce-sentiment-bahasa-indonesia`

Dataset ini **tidak layak dipakai sebagai data latih apa adanya**:

- `simple.json` berisi 17.000 baris tetapi hanya **2.193 komentar unik (87% duplikasi)**. Frasa
  generik berulang 130–150 kali ("Fifty fifty", "Standar lah", "Biasa aja sih").
- Distribusi kelas **persis seimbang** (5.667 / 5.667 / 5.666) — pola yang tidak terjadi pada
  ulasan marketplace nyata.
- Dataset card tidak menyebut sumber, metode pengumpulan, maupun metodologi anotasi.

Melatih di atasnya berisiko kebocoran duplikat lintas split dan mengajarkan distribusi buatan.

`challange.json` (4.840 baris, **seluruhnya unik**) justru bernilai tinggi untuk keperluan lain:
setiap baris ditandai jenis fenomena linguistik — `sarcasm`, `negation`, `typos_informal`,
`colloquial_slang`, `mixed_sentiment`, `ambiguous`, dan lainnya. Ini persis yang dibutuhkan
bagian 33.1 ("performa slang/typo diuji terpisah pada subset ulasan sangat informal").

**Usulan peran baru:** `challange.json` dipakai sebagai **stress/diagnostic test set**, bukan data
latih; `simple.json` tidak dipakai. Menunggu persetujuan.

## 5. Harmonisasi taxonomy dan label mapping

_Tertahan — lihat bagian 6._

## 6. BLOCKER: tidak ada label aspek di dataset manapun

Blueprint bagian 26.1 langkah 4 merencanakan: _"aspek dipetakan dari label emosi/kategori asli ke
taksonomi 11 aspek (bagian 18.2) via mapping table manual"_.

Setelah data diunduh dan diperiksa, pemetaan ini **tidak dapat dijalankan sebagaimana tertulis**:

- `Emotion` PRDECT-ID (Happy/Sadness/Fear/Love/Anger) adalah dimensi **emosi**, bukan aspek. Tidak
  ada fungsi yang memetakan "Sadness" ke "ukuran_varian" — satu ulasan sedih bisa soal aspek apa pun.
- `Category` PRDECT-ID dan Tokopedia adalah **kategori produk** (Women's Fashion, elektronik),
  yaitu input untuk memilih aspek mana yang aktif — bukan label aspek itu sendiri.
- `category` pada `challange.json` adalah taksonomi **fenomena linguistik**, bukan aspek produk.

Penelusuran dataset beraspek berbahasa Indonesia yang tersedia publik juga tidak menemukan
pengganti yang cocok: CASA (ulasan mobil, 6 aspek) dan HoASA (hotel, 10 aspek) berada di domain
yang berbeda dan aspeknya tidak sepadan dengan taksonomi e-commerce kita.

Keputusan cara memperoleh label aspek belum diambil — lihat catatan di `ml/README.md` dan laporan
Fase 1.

## 7. Split
_Rencana: 70/15/15 product-level split + verifikasi eksplisit tanpa leakage. Belum dijalankan._

## 8. Privasi
PII di-mask sebelum data dipakai. Untuk data Apify (Fase 3): nama akun, avatar, dan data ukuran
tubuh dianonimkan sebelum diproses (dossier 21B.6.4).

## 9. Bias representasi yang diketahui
Dataset publik cenderung berasal dari toko besar/aktif — bukan representasi sempurna UMKM mikro
(dossier bagian 14.2). Tokopedia 2019 juga berusia 6+ tahun sehingga tidak mencerminkan tren bahasa
terbaru. Dicatat terbuka, tidak disembunyikan.
