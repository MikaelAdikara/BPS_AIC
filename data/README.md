# data/

Kebijakan sesuai blueprint bagian 31.1.

| Folder | Di-commit? | Isi |
| --- | --- | --- |
| `raw/` | **TIDAK** | Dataset publik hasil unduhan `scripts/download_datasets.py` |
| `interim/` | **TIDAK** | Hasil antara harmonisasi/pembersihan |
| `processed/` | **TIDAK** | Data siap latih + artifact baseline kategori |
| `samples/` | **YA** | Dataset demo kecil agar juri dapat mencoba tanpa data sendiri (ING-04) |
| `schemas/` | **YA** | JSON schema kontrak data (bagian 25) |

Dataset publik pihak ketiga **tidak** di-commit — alasan lisensi dan ukuran. Script unduh
mengambil ulang dari sumber resmi.

Data pengguna saat runtime bersifat **session-only** dan tidak pernah ditulis ke folder ini
(ADR-010, bagian 27.2).

## Komposisi dataset demo yang harus dipenuhi (bagian 42.1)

Dataset di `samples/` dirancang agar satu demo tunggal dapat menunjukkan seluruh kapabilitas:

- Bahasa informal (slang, singkatan, campuran bahasa daerah) pada minimal 30% baris.
- Beberapa aspek berbeda terwakili merata.
- Keluhan berulang pada satu aspek dengan frekuensi tinggi (memicu Action Card urgensi tinggi).
- Pujian jelas pada aspek lain (memicu promotion highlight).
- Foto rusak yang jelas (kasus visual confident).
- Foto blur/tidak jelas (memicu abstention).
- Satu kasus contradiction eksplisit: teks positif, foto menunjukkan masalah.
- Kategori produk yang tersedia di benchmark baseline agar BEN-01 bermakna.

_Belum dibuat. Dikerjakan pada Fase 1._
