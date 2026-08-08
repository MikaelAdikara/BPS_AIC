# docker/

Deployment lokal InsightUlasan (blueprint bagian 30). Berkas `docker-compose.yml` ada di
**root repository**, bukan di folder ini — juri menjalankan `docker compose up` dari root,
dan meminta mereka mengetik `-f docker/docker-compose.yml` hanya menambah satu cara gagal.
Ini menutup pertanyaan terbuka yang sebelumnya dicatat di sini.

## Menjalankan

```bash
docker compose up --build
```

Frontend di <http://localhost:3000>, API di <http://localhost:8000>.

Container `web` menunggu `api` melewati healthcheck-nya, dan healthcheck itu menembak
`/api/v1/readiness` — bukan `/health`. Bedanya penting: `/health` menjawab begitu proses
hidup, sedangkan halaman depan baru berguna setelah model selesai dimuat.

## Dua service, bukan tiga

Blueprint menyediakan ruang untuk `vector-store` terpisah. Ia tidak dipakai: indeks bukti
dibangun per sesi analisis di dalam proses `api` dan hilang bersama sesinya (ADR-007,
ADR-010), sehingga service ketiga tidak punya pekerjaan yang tersisa.

## Checkpoint model

Bobot IndoBERT berukuran 476 MB dan tidak masuk git (lihat `.gitignore`). Compose
memasangnya dari host sebagai volume **read-only**:

```yaml
- ./models:/app/models:ro
```

**Sistem tetap berjalan kalau folder itu kosong.** Tanpa checkpoint, klasifikasi turun ke
jalur leksikon dan `/api/v1/readiness` menyatakan keterbatasannya. Hasil analisisnya lebih
lemah, tetapi seluruh alur — unggah, prioritas, bukti, tanya jawab — tetap dapat
didemonstrasikan. Ini keputusan sadar: `docker compose up` yang gagal total hanya karena
satu berkas besar tidak ada akan membuat sistem tampak rapuh padahal tidak.

Distribusi checkpoint (HuggingFace Hub atau rilis GitHub) belum ditetapkan dan menunggu
keputusan pemilik repo.

## Yang sudah dan belum diverifikasi

| Diperiksa | Cara | Hasil |
| --- | --- | --- |
| Sintaks `docker-compose.yml` | parser YAML | sah, dua service |
| Seluruh sumber `COPY` ada | pemindaian Dockerfile terhadap berkas nyata | sah setelah satu perbaikan |
| Jalur di dalam container | simulasi `parents[4]` → `/app` | cocok dengan titik pasang volume |
| Endpoint healthcheck | dicocokkan ke rute `main.py` | ada |
| `npm ci` punya lockfile | keberadaan `package-lock.json` | ada |
| **Image benar-benar terbangun dan berjalan** | — | **BELUM** — Docker tidak terpasang di mesin pengembangan |

Baris terakhir ditulis apa adanya: konfigurasi ini disusun dan diperiksa secara statis,
tetapi `docker compose up` belum pernah dijalankan sampai selesai. Perbaikan yang sudah
ditemukan lewat pemeriksaan statis: `COPY data/baseline` menunjuk folder yang tidak ada
(seharusnya `data/processed/category_baseline.json`), dan konteks build tanpa
`.dockerignore` ikut mengirim `.venv` serta `node_modules`.

## Target bagian 30.3 yang menjadi acuan

- CPU-only default; torch varian CPU dipasang eksplisit supaya roda CUDA ~2 GB tidak ikut.
- Offline penuh setelah build pertama — cache HuggingFace dipertahankan di volume `hf-cache`.
- Startup sampai readiness: ~53 detik terukur di luar container; `start_period` healthcheck
  disetel 120 detik untuk mesin yang lebih lambat.
- Tidak ada volume untuk data pengguna. Ulasan hidup selama satu request dan tidak pernah
  menyentuh disk — ketiadaan volume itu bagian dari janjinya, bukan kelalaian konfigurasi.
