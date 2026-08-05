# Dataset Card

Status: **Fase 1.** Verifikasi lisensi, profiling, harmonisasi, dan pelabelan silver selesai.
Yang belum: anotasi gold test set oleh tim (§5a) dan akuisisi foto validasi visual (§8).

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

**Keputusan (ADR-016, disetujui):** `challange.json` dipakai sebagai **stress/diagnostic test set**,
bukan data latih; `simple.json` tidak dipakai sama sekali. Hasil stress test ada di MODEL_CARD §3.1.

## 5. Harmonisasi dan pelabelan (weak supervision, ADR-015)

Script: `ml/text/build_dataset.py` · seed 42 · laporan: `data/processed/build_report.json`.

**Unit data = klausa, bukan ulasan.** 54% ulasan PRDECT-ID menyebut ≥2 aspek yang sering
berlawanan sentimen ("barangnya bagus tapi pengirimannya lama"), sehingga sentimen tingkat
ulasan pasti salah untuk salah satu aspek. Klausa juga mengisi field `source_sentence` yang
diwajibkan schema bagian 25.4.

| Tahap | Hasil |
| --- | --- |
| Ulasan masuk | 46.007 (PRDECT-ID 5.400 + Tokopedia 40.607) |
| Dibuang: kosong/terlalu pendek | 652 |
| Dibuang: duplikat (pada teks ternormalisasi) | 5.369 |
| Ulasan bersih | **39.986** |
| Klausa hasil segmentasi | **96.300** |

**Sumber label:**

| Label | Cara diperoleh | Sifat |
| --- | --- | --- |
| Aspek (11, multi-label) | Labeling function leksikon per klausa; istilah topik dipisah tegas dari istilah polaritas | SILVER |
| Sentimen — PRDECT-ID | Label manusia `Sentiment` (biner) sebagai prior tingkat ulasan | manusia (biner) |
| Sentimen — Tokopedia | Diturunkan dari rating: 4–5 positif, 3 netral, 1–2 negatif | weak label |
| Sentimen — tingkat klausa | Leksikon polaritas + penanganan negasi; jika klausa tanpa sinyal, pakai prior ulasan | SILVER |
| Severity | Heuristik deterministic dari rating (negatif + rating ≤2 → tinggi, =3 → sedang, ≥4 → rendah) | heuristik |

Sentimen klausa: 56% berasal dari sinyal polaritas di klausa itu sendiri, 44% dari prior tingkat
ulasan. Porsi 44% inilah sumber derau utama pada label sentimen — terlihat dari kelas `netral`
yang runtuh pada evaluasi baseline (lihat MODEL_CARD §3.1).

**Distribusi hasil:**

| Dimensi | Sebaran |
| --- | --- |
| Sentimen klausa | positif 81.343 (84%) · negatif 12.711 (13%) · netral 2.246 (2%) |
| Kategori (ulasan) | electronics 19.348 · other 9.442 · fashion 8.939 · craft 2.061 · **food_beverage 196** |
| Klausa tanpa aspek | 43.589 (45%) — label sah, dipakai sebagai negatif |

Aspek per klausa: pengiriman 13,1% · kualitas_produk 14,9% · kesesuaian_deskripsi 11,8% ·
pelayanan_penjual 9,4% · kemasan 4,4% · harga_value 3,2% · ukuran_varian 2,2% · keaslian 1,3% ·
kemudahan_penggunaan 1,3% · rasa_kualitas_makanan 0,5% · kelengkapan 0,5%.

**Keterbatasan cakupan yang harus dicatat:** kategori `food_beverage` hanya terwakili 196 ulasan,
sehingga aspek `rasa_kualitas_makanan` praktis tidak terlatih memadai, dan baseline kategori F&B
untuk BEN-01 tidak akan punya sampel yang layak. Ini memengaruhi klaim "taxonomy dapat disesuaikan
per kategori" (bagian 18.2) — mekanismenya ada, tetapi buktinya untuk F&B lemah.

## 5a. Gold test set (berlabel manusia) — belum selesai

Berkas tugas anotasi sudah dibuat: `data/annotation/gold_annotation_task.csv` (500 klausa) dengan
panduan `data/annotation/PANDUAN_ANOTASI.md`. Sampel diambil **hanya dari split test** sehingga
produknya terpisah dari data latih, bertingkat per aspek (kuota 30/aspek) plus 143 klausa tanpa
aspek agar presisi labeling function ikut terukur, bukan hanya recall-nya.

Label silver sengaja **tidak** disertakan di berkas anotasi untuk menghindari anchoring bias.

**Sampai berkas ini dilabeli, tidak ada satu pun angka NLP-01 yang layak masuk proposal.**

## 6. Catatan asal-usul: tidak ada label aspek di dataset manapun

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

**Keputusan:** label aspek dihasilkan lewat weak supervision + gold test set berlabel manusia —
lihat ADR-015 di `docs/ARCHITECTURE.md` dan pelaksanaannya di §5 / §5a di atas.

## 7. Split — product-level, terverifikasi tanpa leakage

Split 70/15/15 dilakukan di tingkat **produk**, bukan per baris (bagian 26.1 langkah 6), lalu
diverifikasi eksplisit (langkah 7).

| Split | Klausa | Produk unik |
| --- | --- | --- |
| train | 69.800 | 3.329 |
| val | 15.308 | 713 |
| test (silver) | 11.192 | 715 |

Verifikasi leakage: **0 produk** dan **0 review_id** yang muncul di lebih dari satu split.

Yang tersisa dan dilaporkan terbuka: masih ada klausa dengan **teks identik** lintas split
(train↔val 1.969, train↔test 1.600, val↔test 916) — frasa generik pendek seperti "barang bagus"
yang wajar berulang di produk berbeda. Ini bukan kebocoran produk, tetapi tetap dapat membuat
metrik terlihat lebih baik lewat hafalan frasa. Karena itu `ml/text/baseline.py` selalu melaporkan
metrik ganda: pada test penuh **dan** pada subset `unseen` (klausa yang teksnya tak pernah muncul
di train, n=6.383). Selisih keduanya kecil (aspek 0,938 → 0,923; sentimen 0,563 → 0,561).

## 8. Privasi
PII di-mask sebelum data dipakai. Untuk data Apify (Fase 3): nama akun, avatar, dan data ukuran
tubuh dianonimkan sebelum diproses (dossier 21B.6.4).

## 9. Bias representasi yang diketahui
Dataset publik cenderung berasal dari toko besar/aktif — bukan representasi sempurna UMKM mikro
(dossier bagian 14.2). Tokopedia 2019 juga berusia 6+ tahun sehingga tidak mencerminkan tren bahasa
terbaru. Dicatat terbuka, tidak disembunyikan.
