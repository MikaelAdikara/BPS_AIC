# InsightUlasan

Ubah tumpukan ulasan dan foto pelanggan UMKM berbahasa Indonesia informal menjadi tiga masalah paling mendesak beserta bukti kutipan asli dan langkah konkret yang bisa langsung dikerjakan — dalam satu kali unggah.

> **Status: struktur repository awal (Fase 0).**
> Belum ada fungsionalitas yang berjalan. Dokumen ini akan dilengkapi pada Fase 10 sesuai
> [blueprint](docs/reference/INSIGHTULASAN_BLUEPRINT.md) bagian 31.1. Tidak ada angka
> performa yang dicantumkan di sini sebelum evaluasi (bagian 33) benar-benar dijalankan.

---

## Apa yang dibangun

InsightUlasan menjembatani lima tahap berurutan (blueprint bagian 3):

`ulasan mentah (teks + foto opsional)` → `pemahaman aspek & sentimen` → `penggabungan bukti teks+visual` → `penentuan prioritas` → `rekomendasi aksi bisnis dengan bukti yang dapat diverifikasi`

Lima lapisan intelligence (bagian 1.1):

| Lapisan | Komponen | Model |
| --- | --- | --- |
| 1. Text Intelligence | Klasifikasi aspek + sentimen teks informal | IndoBERT-base (fine-tuned), fallback TF-IDF + Logistic Regression |
| 2. Visual Intelligence | Klasifikasi kondisi visual foto ulasan, dengan abstention wajib | CLIP ViT-B/32 zero-shot (frozen), fallback SigLIP |
| 3. Retrieval & Evidence Grounding | Kutipan ulasan asli sebagai bukti setiap klaim | BGE-M3 + Chroma, fallback Multilingual E5-base |
| 4. Action Recommendation Engine | Skoring prioritas deterministic + Action Card | Non-AI, formula bagian 22.2 |
| 5. Foundation Model Orchestrator | Tool calling, narasi, Q&A | SEA-LION quantized, fallback Sailor2 / FALLBACK MODE template |

## Prinsip yang tidak dinegosiasikan

1. Seluruh model berjalan **lokal dan CPU-friendly**, offline setelah build — tanpa API berbayar sebagai dependency inti.
2. Foto ulasan **opsional per entri** — sistem berjalan penuh tanpa foto.
3. Model visual **wajib abstain** saat confidence rendah: _"Tidak dapat menyimpulkan kondisi produk dari foto ini."_
4. **LLM tidak pernah menghitung angka sendiri.** Semua angka berasal dari tool deterministic (bagian 27.3).
5. **Tidak ada eksekusi tindakan bisnis otomatis** — setiap Action Card wajib tombol terima/tolak/simpan.
6. Sistem **tidak gagal total** jika LLM orchestrator gagal dimuat — ada FALLBACK MODE deterministic (ADR-014).

## Struktur repository

```
apps/web/     React + Vite frontend (4 screen, bagian 14)
apps/api/     FastAPI backend — routers, services, tools, adapters, schemas (bagian 27)
ml/           Pipeline training teks, validasi visual, embedding, orchestrator, evaluasi (bagian 26, 33)
data/         raw/interim/processed (tidak di-commit) + samples & schemas (di-commit)
configs/      Threshold, path model, taxonomy aspek per kategori
docs/         ARCHITECTURE, MODEL_CARD, DATASET_CARD, LIMITATIONS, RESPONSIBLE_AI
docs/reference/  Blueprint & research dossier (sumber kebenaran, bukan kode)
scripts/      Unduh dataset, precompute baseline, setup
tests/        unit / integration / e2e (bagian 32)
docker/       docker-compose.yml + Dockerfile bersama
```

## Menjalankan (belum tersedia)

Setup guide `docker compose` akan ditulis pada Fase 9 setelah reproducibility test dari fresh clone
benar-benar lulus (blueprint bagian 32, 38.1). Sampai saat itu, README ini sengaja tidak memuat
perintah yang belum diuji.

## Dokumentasi

| Dokumen | Isi |
| --- | --- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Ringkasan C4 + keputusan arsitektur kunci |
| [docs/MODEL_CARD.md](docs/MODEL_CARD.md) | Data training, metrik evaluasi, batas kemampuan, bias |
| [docs/DATASET_CARD.md](docs/DATASET_CARD.md) | Sumber, lisensi, preprocessing tiap dataset |
| [docs/LIMITATIONS.md](docs/LIMITATIONS.md) | Keterbatasan yang diketahui, ditulis apa adanya |
| [docs/RESPONSIBLE_AI.md](docs/RESPONSIBLE_AI.md) | Governance, privasi, dan responsible AI |

## Lisensi

MIT — lihat [LICENSE](LICENSE). Kompatibilitas dengan lisensi dataset dan model yang dipakai masih
perlu diverifikasi eksplisit (blueprint bagian 26.1, 48).
