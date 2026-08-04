# Dataset Card

> **Placeholder (Fase 0).** Diisi pada Fase 1 sesuai blueprint bagian 26.1 dan 31.1.

## 1. Dataset yang dipakai

| Dataset | Sumber | Peran | Lisensi | Status verifikasi |
| --- | --- | --- | --- | --- |
| PRDECT-ID | Kaggle (jocelyndumlao/prdect-id) | Training inti | perlu diverifikasi | **belum diverifikasi** |
| e-commerce-sentiment-bahasa-indonesia | Hugging Face | Training inti | perlu diverifikasi | **belum diverifikasi** |
| Tokopedia Product Reviews 2019 | Hugging Face (farhamu/...) | Training + domain testing | perlu diverifikasi | **belum diverifikasi** |
| Foto ulasan Shopee via Apify | Akuisisi mandiri, ~250–300 foto | Validasi/kalibrasi visual saja | data publik, tunduk ToS + UU PDP | PARTIALLY VERIFIED (dossier 21B.6.3) |

Verifikasi lisensi adalah prasyarat sebelum publikasi proposal final (blueprint bagian 26.1 langkah 2,
bagian 48). Dataset publik **tidak di-commit** ke repository — diunduh ulang lewat
`scripts/download_datasets.py`.

## 2. Harmonisasi taxonomy dan label mapping
_Tabel pemetaan label asli ketiga dataset ke taxonomy aspek + sentimen tunggal (bagian 18.2).
Diisi pada Fase 1._

## 3. Preprocessing
_Normalisasi slang, penanganan negasi, deduplikasi, pembersihan encoding. Diisi pada Fase 1._

## 4. Split
_70/15/15 **product-level split** (bukan random per baris) + verifikasi eksplisit tidak ada leakage
review_id/produk lintas split. Diisi pada Fase 1._

## 5. Distribusi kelas dan imbalance
_Distribusi aktual per dataset diukur, bukan diasumsikan. Mitigasi: class weighting._

## 6. Data sintetik
_Jika dipakai: ditandai eksplisit sebagai sintetik, divalidasi manual pada sampel sebelum dicampur._

## 7. Privasi
_PII di-mask sebelum data dipakai. Untuk data Apify: nama akun, avatar, dan data ukuran tubuh
dianonimkan sebelum diproses (dossier 21B.6.4)._

## 8. Bias representasi yang diketahui
_Dataset publik cenderung berasal dari toko besar/aktif — bukan representasi sempurna UMKM mikro
(dossier bagian 14.2). Dicatat terbuka, tidak disembunyikan._
