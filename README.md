# InsightUlasan

Mengubah tumpukan ulasan dan foto pelanggan UMKM berbahasa Indonesia informal menjadi **tiga masalah paling mendesak, bukti kutipan aslinya, dan langkah konkret yang bisa langsung dikerjakan** — dalam satu kali unggah.

---

## Status pengembangan

Repositori ini dikerjakan bertahap mengikuti Fase 0–10 pada blueprint bagian 38. Status per commit terakhir:

| Fase | Cakupan | Status |
| --- | --- | --- |
| 0 | Scope freeze — taksonomi aspek, kelas visual, kontrak data | **selesai** |
| 1 | Data & baseline — unduh dataset, harmonisasi, baseline TF-IDF | **selesai** |
| 2 | Model teks — fine-tuning IndoBERT | **berjalan** |
| 3 | Model visual — zero-shot CLIP + go/no-go gate | belum |
| 4 | Retrieval & action engine | belum |
| 5 | Backend FastAPI | belum |
| 6 | Frontend React | belum |
| 7 | Integrasi | belum |
| 8 | Evaluasi penuh | belum |
| 9 | Docker & reproducibility | belum |
| 10 | Dokumentasi akhir | belum |

> **Belum ada aplikasi yang dapat dijalankan.** Yang sudah berfungsi adalah pipeline data dan model teks di `ml/`. Setup guide `docker compose` ditulis pada Fase 9, setelah reproducibility test dari fresh clone benar-benar lulus — bukan sebelumnya.
>
> **Tidak ada angka performa yang dikutip sebagai capaian di dokumen ini.** Metrik yang sudah terukur beserta batas penafsirannya ada di [docs/MODEL_CARD.md](docs/MODEL_CARD.md).

---

## Masalah yang diselesaikan

Pemilik UMKM mikro-kecil menerima ulasan dalam volume yang tidak sebanding dengan waktu yang mereka punya. Pola masalah nyata — ukuran salah, kemasan rusak, respons lambat — terkubur di antara ratusan baris teks yang tidak pernah dibaca sistematis, dan foto bukti yang dilampirkan pembeli nyaris tidak pernah ditinjau secara agregat.

Dari *"ratusan ulasan yang tidak sempat dibaca"* menjadi *"tiga masalah paling mendesak, bukti kutipan aslinya, dan langkah konkret minggu ini"*.

## Cara kerja

Lima tahap berurutan — jembatan inilah novelty produk, bukan satu model AI tunggal mana pun:

```
ulasan mentah (teks + foto opsional)
      -> pemahaman aspek & sentimen        (klasifikasi per klausa)
      -> penggabungan bukti teks + visual  (fusion terstruktur, dapat diaudit)
      -> penentuan prioritas               (skoring deterministic)
      -> rekomendasi aksi + bukti kutipan  (Action Card, wajib persetujuan manusia)
```

Lima lapisan yang menjalankannya:

| # | Lapisan | Model utama | Fallback |
| --- | --- | --- | --- |
| 1 | Text Intelligence — aspek + sentimen teks informal | IndoBERT-base (fine-tuned) | TF-IDF + Logistic Regression |
| 2 | Visual Intelligence — kondisi foto ulasan, dengan abstention wajib | CLIP ViT-B/32 zero-shot (frozen) | SigLIP |
| 3 | Retrieval & Evidence Grounding — kutipan asli sebagai bukti | BGE-M3 + Chroma | Multilingual E5-base |
| 4 | Action Recommendation Engine — skoring prioritas | deterministic, non-AI | — |
| 5 | Foundation Model Orchestrator — tool calling, narasi, Q&A | SEA-LION (quantized) | Sailor2 / FALLBACK MODE template |

## Prinsip yang tidak dinegosiasikan

1. **Berjalan lokal, CPU-friendly, offline setelah build.** Tidak ada API berbayar sebagai dependency inti — supaya siapa pun dapat memverifikasi sendiri.
2. **Foto ulasan opsional per entri.** Sistem berjalan penuh tanpa foto.
3. **Model visual wajib abstain saat ragu:** _"Tidak dapat menyimpulkan kondisi produk dari foto ini."_ Tidak pernah memaksakan label.
4. **LLM tidak pernah menghitung angka sendiri.** Seluruh frekuensi, persentase, dan skor berasal dari tool deterministic; LLM hanya menyusun narasi dari angka yang sudah dihitung.
5. **Tidak ada eksekusi tindakan bisnis otomatis.** Setiap Action Card wajib tombol terima/tolak/simpan.
6. **Tidak gagal total.** Jika orchestrator gagal dimuat, sistem otomatis masuk FALLBACK MODE — seluruh angka, skor, dan bukti tetap tersedia, hanya narasinya lebih sederhana.
7. **Tidak ada klaim performa yang belum diuji.** Angka apa pun di repositori ini dapat ditelusuri ke script evaluasi yang benar-benar dijalankan.

## Struktur repositori

```
apps/
  web/          React + Vite — 4 screen (belum dibangun)
  api/           FastAPI — routers, services, tools, adapters, schemas (belum dibangun)
ml/
  text/          Pipeline data + baseline + fine-tuning teks   <- berfungsi
  vision/        Validasi zero-shot CLIP (Fase 3)
  embeddings/    BGE-M3 + vector store (Fase 4)
  orchestrator/  Konfigurasi quantization (Fase 5)
  evaluation/    Hasil evaluasi + experiment_log.md
data/
  raw/ interim/ processed/   tidak di-commit, dihasilkan script
  annotation/    berkas anotasi gold test set                  <- di-commit
  samples/       dataset demo untuk juri (Fase 1 lanjutan)
  schemas/       JSON schema kontrak data
configs/         taksonomi aspek, kelas visual, threshold      <- FROZEN sejak Fase 0
docs/            ARCHITECTURE, MODEL_CARD, DATASET_CARD, LIMITATIONS, RESPONSIBLE_AI
docs/reference/  blueprint, dossier riset, ringkasan aturan lomba
scripts/         unduh dataset, precompute baseline
tests/           unit / integration / e2e (Fase 5+)
docker/          docker-compose.yml (Fase 9)
```

## Menjalankan pipeline yang sudah ada

Prasyarat: Python 3.11+. GPU opsional — hanya mempercepat fine-tuning; target deployment tetap CPU-only.

```bash
python -m venv .venv && source .venv/Scripts/activate   # Linux/macOS: source .venv/bin/activate
pip install -r ml/requirements.txt
```

Unduh dataset publik ke `data/raw/` (tidak di-commit):

```bash
python scripts/download_datasets.py
```

Bangun dataset klausa berlabel + split product-level, lalu jalankan baseline:

```bash
python ml/text/build_dataset.py
python ml/text/baseline.py
```

Fine-tuning IndoBERT (dua head: aspek multi-label + sentimen 3 kelas):

```bash
python ml/text/finetune.py --epochs 3 --batch-size 32
```

Susun berkas tugas anotasi gold test set:

```bash
python ml/text/make_gold_task.py --n 500
```

Seluruh script memakai seed tetap (42) dan menulis hasilnya ke `ml/evaluation/`.

## Dataset

Dataset **tidak di-commit** — diunduh ulang dari sumber resmi oleh `scripts/download_datasets.py`. Lisensi seluruhnya sudah diverifikasi:

| Dataset | Sumber | Lisensi | Peran |
| --- | --- | --- | --- |
| PRDECT-ID | `ZakyF/PRDECT-ID` | CC-BY-4.0 | training + gold test |
| Tokopedia Product Reviews 2019 | `farhamu/tokopedia-product-reviews-2019` | Apache-2.0 | training + domain testing |
| e-commerce-sentiment-bahasa-indonesia | `AIbnuHibban/e-commerce-sentiment-bahasa-indonesia` | MIT | stress test saja |

**Atribusi wajib (CC-BY-4.0):** Sutoyo, R. dkk. _PRDECT-ID: Indonesian product reviews dataset for emotions classification tasks_. Data in Brief (2022). arXiv:2406.10118.

Rincian pemrosesan, sumber label, dan keterbatasan cakupan ada di [docs/DATASET_CARD.md](docs/DATASET_CARD.md).

## Dokumentasi

| Dokumen | Isi |
| --- | --- |
| [docs/SCOPE_FREEZE.md](docs/SCOPE_FREEZE.md) | Cakupan Tier 1 yang dikunci: taksonomi, kelas visual, fitur, formula prioritas |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Ringkasan arsitektur + 16 Architecture Decision Record |
| [docs/MODEL_CARD.md](docs/MODEL_CARD.md) | Metrik yang sudah terukur, beserta batas penafsirannya |
| [docs/DATASET_CARD.md](docs/DATASET_CARD.md) | Sumber, lisensi, pemrosesan, bias yang diketahui |
| [docs/LIMITATIONS.md](docs/LIMITATIONS.md) | Keterbatasan yang diketahui, ditulis apa adanya |
| [docs/RESPONSIBLE_AI.md](docs/RESPONSIBLE_AI.md) | Privasi, governance, threat model |
| [ml/evaluation/experiment_log.md](ml/evaluation/experiment_log.md) | Catatan tiap eksperimen yang dijalankan |

Sumber kebenaran desain ada di [`docs/reference/`](docs/reference/) — blueprint sistem, dossier riset, dan ringkasan aturan lomba. Rujuk pakai nomor bagian, mis. "blueprint bagian 22.2".

## Konvensi kontribusi

- **Conventional Commits wajib**: `feat:` / `fix:` / `refactor:` / `docs:` / `test:`.
- Commit dan push setiap ada perubahan berarti — riwayat commit adalah bagian dari bukti proses pengembangan.
- Perubahan keputusan desain diedit di `docs/reference/` **lebih dulu**, baru diikuti kodenya, supaya dokumen tetap satu sumber kebenaran.

## Lisensi

[MIT](LICENSE). Lisensi dataset dan model yang dipakai tercantum di atas dan di DATASET_CARD.
