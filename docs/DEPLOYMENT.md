# Deployment

Dokumen ini mencatat bagaimana InsightUlasan berjalan di server demo, apa yang otomatis, dan
batas-batas yang sudah TERUKUR - bukan yang diperkirakan.

## Alamat

<http://34.41.49.44>

Situs terbuka publik tanpa autentikasi. Ini keputusan sadar untuk demo lomba (juri harus bisa
membuka tautan tanpa dibagi kredensial), bukan kelalaian. Data yang diunggah pengguna tetap
tidak pernah menyentuh disk (ADR-010), sehingga yang terekspos adalah aplikasinya, bukan data
siapa pun.

## Mesin

| | |
|---|---|
| Project | `kemenkop-comfest-18` |
| Instance | `normal-1`, zona `us-central1-a` |
| Tipe | `e2-standard-2` (2 vCPU, 8 GB) |
| IP eksternal | 34.41.49.44 - **efemeral** |

IP-nya efemeral, artinya **alamat di atas berubah bila VM pernah dimatikan**. Mengubahnya
menjadi statis memerlukan izin `compute.addresses.create` yang tidak dimiliki pemilik akun saat
ini; lihat bagian Izin.

Port 80 terbuka lewat aturan bawaan `default-allow-http`, yang berlaku karena instance ini
bertag `http-server`. Tidak ada aturan firewall baru yang dibuat untuk deployment ini.

## Susunan

Dua container lewat `docker compose`, didefinisikan di `docker-compose.yml` pada root
repositori:

- `api` - FastAPI + uvicorn, port 8000. Memuat checkpoint IndoBERT dari `./models` yang
  dipasang read-only. Checkpoint 499 MB tidak ikut git dan diunduh sekali dengan
  `python3 scripts/download_checkpoint.py`.
- `web` - nginx menyajikan build Vite, dan mem-proxy `/api/` ke `api:8000`.

Di VM ada satu berkas tambahan yang **tidak** ada di repositori,
`docker-compose.override.yml`, berisi dua hal: `web` dilayani di port 80 (bukan 3000, supaya
tidak perlu aturan firewall baru) dan `restart: unless-stopped` pada kedua service supaya demo
kembali hidup sendiri setelah VM di-reboot.

## Deploy otomatis

Setiap commit baru di `origin/main` diambil dan diterapkan sendiri, paling lama 2 menit setelah
push. Yang mengerjakannya:

- `~/autodeploy.sh`
- `insightulasan-deploy.service` + `insightulasan-deploy.timer` (systemd, interval 2 menit)

Alurnya: `git fetch` → bila SHA berubah, `git reset --hard origin/main` → `docker compose
build` → **hanya bila build berhasil**, `docker compose up -d` → tunggu `/readiness` menjawab →
`docker image prune`.

Urutan itu disengaja. Build berjalan lebih dulu dan container lama tidak disentuh sampai build
terbukti berhasil, sehingga **push yang tidak dapat di-build tidak menjatuhkan situs demo** -
container lama terus melayani dan kegagalannya tercatat di log.

Polling, bukan GitHub Actions atau webhook. Repositori ini publik; dua alternatif itu menuntut
kunci SSH atau kredensial deploy disimpan sebagai secret di GitHub, plus port masuk terbuka ke
VM. Polling tidak menaruh rahasia apa pun di luar VM dan tidak membuka satu pun port. Harganya
keterlambatan paling lama dua menit.

### Memantau

```bash
tail -f ~/autodeploy.log                                  # riwayat deploy
systemctl list-timers insightulasan-deploy.timer          # kapan pemeriksaan berikutnya
~/autodeploy.sh                                           # paksa periksa sekarang
```

`git reset --hard` berarti mesin ini adalah target deploy, bukan tempat menyunting kode.
Perubahan yang dibuat langsung di VM akan hilang pada deploy berikutnya - kecuali berkas tak
terlacak seperti `docker-compose.override.yml`, yang tidak tersentuh oleh reset.

## Batas kinerja yang terukur

Diukur di `e2-standard-2` (2 vCPU) lewat endpoint `/api/v1/analyze`:

| Jumlah ulasan | Waktu |
|---|---|
| 66 | 88 detik |
| 186 | 163 detik |

Kedua titik itu memberi sekitar **0,62 detik per ulasan** ditambah **~47 detik biaya tetap**
(pemuatan model dan penyiapan indeks bukti).

Batas waktu klien dan `proxy_read_timeout` nginx sama-sama 300 detik, sehingga plafon
praktisnya **sekitar 400 ulasan**, bukan 1.000 seperti yang diizinkan
`MAX_REVIEWS_PER_REQUEST`. Unggahan yang jauh lebih besar dari itu akan kehabisan waktu.

Jalan keluarnya menaikkan ukuran mesin - beban ini terikat CPU, jadi `e2-standard-8` (8 vCPU)
memangkas komponen per-ulasan kira-kira empat kali lipat. Itu memerlukan izin yang belum ada.

## Izin

Akun yang dipakai saat ini dapat SSH dan menjalankan apa pun DI DALAM VM, tetapi tidak dapat
mengelola siklus hidup VM-nya. Yang ditolak dan sudah dipastikan lewat `testIamPermissions`:

- `compute.instances.stop` / `.start` / `.setMachineType` - sehingga **VM tidak dapat diubah
  ukurannya** dari akun ini
- `compute.addresses.create` - sehingga IP demo tidak dapat dikunci menjadi statis

Keduanya perlu dikerjakan pemilik project. Untuk menaikkan mesin dan sekaligus mempertahankan
alamat demo, urutannya penting - kunci IP-nya LEBIH DULU, karena mematikan VM melepaskan IP
efemeral:

```bash
gcloud compute addresses create insightulasan-demo-ip \
  --addresses=34.41.49.44 --region=us-central1 --project=kemenkop-comfest-18
gcloud compute instances stop normal-1 --zone=us-central1-a --project=kemenkop-comfest-18
gcloud compute instances set-machine-type normal-1 --machine-type=e2-standard-8 \
  --zone=us-central1-a --project=kemenkop-comfest-18
gcloud compute instances start normal-1 --zone=us-central1-a --project=kemenkop-comfest-18
```

Setelah menyala kembali tidak ada langkah manual: `restart: unless-stopped` menghidupkan kedua
container, dan timer deploy otomatis melanjutkan sendiri.

## Menyiapkan dari nol

```bash
git clone https://github.com/MikaelAdikara/BPS_AIC.git && cd BPS_AIC
pip install huggingface_hub && python3 scripts/download_checkpoint.py
docker compose up -d --build
```

Tanpa langkah checkpoint, sistem tetap berjalan memakai jalur leksikon dan menyatakan alasannya
di `/api/v1/readiness` - tetapi yang berjalan bukan sistem yang dijelaskan proposal.
