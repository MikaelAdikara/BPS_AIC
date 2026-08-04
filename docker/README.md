# docker/

Deployment lokal sesuai blueprint bagian 30. **Maksimal 3 service** — frontend, api, dan
vector-store opsional. Dapat disederhanakan jadi 2 service jika Chroma di-embed langsung ke
proses api (ADR-007, bagian 47).

| Service | Port | Catatan |
| --- | --- | --- |
| `frontend` | 3000 | Static build React, di-serve container ringan; menunggu `api` healthy |
| `api` | 8000 | FastAPI; readiness=true hanya setelah seluruh model selesai dimuat |
| `vector-store` | 8001 | Opsional — hanya jika Chroma dijalankan terpisah |

## Target yang harus dipenuhi (bagian 30.3, 36)

- CPU-only sebagai default; GPU dipakai otomatis **jika terdeteksi**, bukan requirement.
- Offline penuh setelah image dibangun dan model di-cache.
- Startup di bawah 90 detik dari `docker compose up` hingga readiness=true.
- RAM target ~6–8GB total; disk ~3–5GB.
- Volume `model-artifacts` dan `vector-data` persisten; **tidak ada volume untuk data pengguna**
  (session-only, ADR-010).

## Catatan lokasi file

Blueprint bagian 31 menempatkan `docker-compose.yml` di folder ini. Karena juri kemungkinan besar
menjalankan `docker compose up` dari root repository, perlu diputuskan pada Fase 9 apakah compose
file dipindah ke root atau README memberi perintah `-f docker/docker-compose.yml` secara eksplisit.
Keputusan ini belum diambil.

_Belum ada implementasi. Dikerjakan pada Fase 9._
