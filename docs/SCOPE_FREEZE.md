# Scope Freeze - Fase 0

Deliverable Fase 0 sesuai blueprint bagian 38.1. Dokumen ini mengunci apa yang dibangun untuk
Tier 1 (penyisihan) sebelum satu baris kode fitur ditulis. Perubahan setelah titik ini wajib
diedit di [blueprint](reference/INSIGHTULASAN_BLUEPRINT.md) lebih dulu, baru diikuti kodenya.

**Status: FROZEN.** Dikonfirmasi pada Fase 0.

---

## 1. Taksonomi aspek - FROZEN

Sebelas aspek, persis blueprint bagian 18.2. Config: [`configs/taxonomy.yaml`](../configs/taxonomy.yaml).

| # | ID | Label | Aktif untuk |
| --- | --- | --- | --- |
| 1 | `kualitas_produk` | Kualitas produk | semua kategori |
| 2 | `kesesuaian_deskripsi` | Kesesuaian deskripsi | semua kategori |
| 3 | `harga_value` | Harga dan value | semua kategori |
| 4 | `kemasan` | Kemasan | semua kategori (bobot lebih tinggi untuk F&B) |
| 5 | `pengiriman` | Pengiriman | semua kategori |
| 6 | `pelayanan_penjual` | Pelayanan/respons penjual | semua kategori |
| 7 | `ukuran_varian` | Ukuran/varian | semua kategori, dengan relabel |
| 8 | `rasa_kualitas_makanan` | Rasa/kualitas makanan | food_beverage |
| 9 | `kelengkapan` | Kelengkapan | fashion, craft, electronics, other |
| 10 | `keaslian` | Keaslian | fashion, craft, electronics, other |
| 11 | `kemudahan_penggunaan` | Kemudahan penggunaan | craft, electronics, other |

**Dua keputusan interpretasi yang diambil di Fase 0:**

1. **"Porsi/takaran" untuk F&B adalah relabel `ukuran_varian`, bukan aspek ke-12.** Bentuk
   keluhannya identik secara struktural ("jumlah/ukuran tidak sesuai ekspektasi"), sehingga tidak
   perlu kelas label tambahan yang harus dipetakan dari dataset publik. Berlaku juga untuk craft
   → "Dimensi produk".
2. **"Kurang relevan" diperlakukan sebagai NONAKTIF** pada kategori tersebut. Blueprint hanya
   eksplisit menyebut penonaktifan otomatis untuk `rasa_kualitas_makanan`; untuk tiga aspek
   lainnya dipakai frasa "kurang relevan". Menampilkan aspek tak relevan (mis. "keaslian" untuk
   toko F&B) merusak kepercayaan pada relevansi sistem (persona 5.3). Ini keputusan config murni
   - dapat dibalik tanpa retraining.

Sentimen: `positif | negatif | netral`. Severity: `rendah | sedang | tinggi`.

## 2. Kelas visual - FROZEN

Empat kelas, persis blueprint bagian 19.1. Config: [`configs/visual_classes.yaml`](../configs/visual_classes.yaml).

| # | ID | Label |
| --- | --- | --- |
| 1 | `produk_rusak` | Produk rusak/cacat |
| 2 | `salah_kirim` | Salah kirim/tidak sesuai |
| 3 | `kemasan_rusak` | Kemasan rusak |
| 4 | `normal` | Normal/tidak ada masalah visual |

Setiap kelas memakai prompt ensemble 2–3 varian (campuran Bahasa Indonesia + Inggris); skor akhir
per kelas adalah rata-rata seluruh varian, bukan satu prompt tunggal.

**Abstention wajib.** Pesan tetap: _"Tidak dapat menyimpulkan kondisi produk dari foto ini."_
Threshold absolut dan margin top1-vs-top2 **belum ditetapkan** - dikalibrasi dari distribusi skor
sampel validasi pada Fase 3, bukan angka default.

**Satu-satunya perubahan yang masih terbuka:** penggabungan kelas jika evaluasi Fase 3 membuktikan
dua kelas tidak terpisahkan (kandidat: `salah_kirim` vs `produk_rusak`) - bagian 26.2 langkah 10.
Penambahan kelas baru tidak terbuka; batas tetap maksimal 4.

## 3. Fitur Tier 1 - FROZEN

**Must Build (P0)** - blueprint bagian 9.1, 10, 47:
`ING-01`, `ING-03`, `ING-04`, `ING-09`, `GOV-01`, `GOV-02`, `NLP-01`, `VIS-01`, `FUS-01`,
`RET-01`, `ACT-01`, `QNA-01`, `BEN-01`, `UX-01`, `MON-01`.

**Should Build (P1, hanya setelah seluruh P0 stabil)**:
`ING-05`, `ING-06`, `ING-07`, `NLP-02`, `VIS-02`, `OPP-01`.

**Tidak dibangun untuk penyisihan** - blueprint bagian 4.5, mengikat: dashboard tren multi-halaman,
autentikasi/role management, background job, distributed DB, auto-tuning, feedback loop otomatis,
action tracking penuh, multi-toko, billing, marketplace connector otomatis, continuous learning,
generator konten marketing.

**Feature freeze date: H-7 sebelum deadline.** Setelah tanggal itu tidak ada fitur P1 baru -
hanya stabilisasi P0 (bagian 47).

## 4. Format Action Card - FROZEN

Schema persis blueprint bagian 22.1 (21 field, termasuk `priority_reasoning`,
`risk_if_recommendation_wrong`, dan `user_action`).

**Formula priority score** (bagian 22.2, versi final hasil kajian - bukan perkalian mentah):

```
score = frequency_norm × severity_norm × confidence_norm
        × (1 + 0.3 × recency_norm + 0.2 × benchmark_gap_norm)
```

Seluruh faktor dinormalisasi ke 0–1 sebelum dikalikan, hasil di-scale ke 0–100.
`Business Relevance` **dihapus** sebagai faktor kuantitatif terpisah (risiko double-counting
dengan Severity). Bobot 0.3 / 0.2 berstatus `[REQUIRES VALIDATION]` - wajib diuji sensitivity
±50% pada Fase 8 sebelum dianggap final.

Jika total ulasan sesi < 15: badge "confidence rendah - data terbatas" pada seluruh Action Card,
dan urgensi dibatasi maksimal "Sedang".

## 5. Kontrak data dan API - FROZEN

Schema JSON bagian 25 (13 schema) dan endpoint bagian 28.1 dikunci sekarang agar frontend dapat
mulai dengan mock data sebelum backend selesai (mitigasi risiko bagian 39.1). Perubahan schema
setelah titik ini butuh persetujuan seluruh tim.

## 6. Yang sengaja BELUM diputuskan

| Item | Diputuskan pada | Alasan |
| --- | --- | --- |
| Threshold confidence & margin visual | Fase 3 | Harus dari distribusi skor sampel nyata, bukan default |
| Go/No-Go modul visual | akhir Fase 3 | Berbasis selective accuracy + coverage aktual |
| `min_similarity` retrieval | Fase 4 | Dikalibrasi pada data uji |
| Threshold urgensi (rendah/sedang/tinggi) | Fase 8 | Dikalibrasi saat evaluasi |
| Varian SEA-LION quantized yang dipakai | Fase 5 | Bergantung stabilitas di lingkungan uji |
| Lokasi `docker-compose.yml` (root vs `docker/`) | Fase 9 | Bergantung hasil reproducibility test |
| Verifikasi lisensi 3 dataset publik | Fase 1 | Prasyarat sebelum proposal final |

## 7. Gate Fase 0 → Fase 1

**GO.** Taksonomi aspek dan kelas visual dikunci; tidak ada perubahan tertunda yang memblokir
pekerjaan data dan baseline.
