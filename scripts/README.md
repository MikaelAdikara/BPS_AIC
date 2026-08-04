# scripts/

Script setup dan utilitas yang dijalankan manual (bukan bagian runtime inference).

| Script | Fungsi | Fase | Referensi |
| --- | --- | --- | --- |
| `download_datasets.py` | Unduh PRDECT-ID, e-commerce-sentiment-bahasa-indonesia, Tokopedia reviews 2019 dari sumber resmi | 1 | bagian 26.1, 31.1 |
| `download_models.py` | Unduh model artifact ke `MODEL_CACHE_DIR` (sekali saat build/first-run) | 5/9 | bagian 30.3 |
| `precompute_baseline.py` | Hitung baseline kategori SEKALI dari dataset publik → `data/processed/category_baseline.json` | 4 | bagian 24.1, ADR-012 |
| `build_sample_dataset.py` | Susun dataset demo sesuai komposisi bagian 42.1 | 1 | bagian 42.1 |
| `reproducibility_check.sh` | Fresh clone → `docker compose up` → jalankan sample data, tanpa cache lokal | 9 | bagian 32 |

Script akuisisi foto via Apify dijalankan **hanya pada tahap pengembangan/validasi**, tidak pernah
menjadi dependency runtime aplikasi demo (blueprint bagian 15, dossier 21B.6.4).

_Belum ada implementasi._
