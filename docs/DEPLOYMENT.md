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
praktisnya **sekitar 400 ulasan**.

Karena itu server ini menyetel `MAX_REVIEWS_PER_REQUEST=400` lewat variabel lingkungan di
`docker-compose.override.yml`. Bawaan di kode tetap 1.000 supaya juri yang menjalankan
`docker compose up` di mesinnya sendiri tidak diam-diam dibatasi. Unggahan di atas batas
ditolak seketika dengan pesan yang menjelaskan sebabnya, alih-alih membuat pengguna menunggu
beberapa menit untuk berakhir pada kehabisan waktu yang tidak menerangkan apa pun.

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

## Checklist ketentuan penyedia VM

Ketentuan yang diberikan pengelola VM, dan bagaimana deployment ini memenuhinya. Setiap baris
diperiksa terhadap sistem yang benar-benar berjalan, bukan terhadap niat.

### 1. Aplikasi wajib mengikat `0.0.0.0`, bukan `127.0.0.1`

Terpenuhi. uvicorn dijalankan dengan `--host 0.0.0.0` (`docker/api.Dockerfile`) dan nginx
mendengarkan `0.0.0.0:80`. Diperiksa dari luar: `http://34.41.49.44` menjawab 200.

Satu nuansa yang perlu dicatat supaya tidak keliru dibaca sebagai pelanggaran: port 8000 milik
`api` justru SENGAJA diikat ke `127.0.0.1` di VM ini. Ketentuan itu berlaku untuk proses yang
melayani pengguna dari luar, dan di susunan ini yang melakukannya adalah nginx di port 80.
Container `web` menghubungi `api` lewat jaringan Docker (`http://api:8000`), bukan lewat port
host, sehingga mengikatnya ke loopback tidak menutup jalur siapa pun. Sebelum dirapatkan, port
8000 dipublikasikan ke `0.0.0.0` dan hanya selamat karena kebetulan firewall menutupnya -
artinya satu perubahan tag jaringan sudah cukup membuka API mentah ke internet tanpa disadari.

### 2. Wajib memakai tmux agar proses tidak mati saat koneksi putus

Tidak berlaku, dan yang dipakai lebih kuat. tmux menjaga proses tetap hidup ketika SSH putus,
tetapi tidak menolong ketika VM di-reboot. Di sini aplikasi berjalan sebagai container yang
diawasi daemon Docker, bukan sebagai proses di dalam sesi login.

Bukti yang sudah diperiksa, bukan diasumsikan:

| Yang diperiksa | Hasil |
|---|---|
| `who \| wc -l` | `0` - tidak ada satu pun sesi login, situs tetap melayani 200 |
| Induk proses container | `containerd-shim`, bukan `sshd` maupun `tmux` |
| Kebijakan restart | `unless-stopped` pada `api` dan `web` |
| `docker.service` saat boot | `enabled` |
| `insightulasan-deploy.timer` saat boot | `enabled` |

tmux tetap dipasang di VM untuk keperluan lain, tetapi tidak ada bagian sistem ini yang
bergantung padanya.

Reboot sengaja TIDAK diuji: akun yang ada tidak memiliki `compute.instances.start`, sehingga
VM yang gagal naik kembali tidak dapat dipulihkan tanpa pemilik project. Lima baris di atas
adalah bukti tanpa risiko itu.

### 3. Port yang boleh dipakai: 80 dan 443; port demo seperti 8000/8501 tertutup

Terpenuhi. Diperiksa dari luar VM:

| Port | Status |
|---|---|
| 80 | terbuka, HTTP 200 |
| 443 | tidak ada yang mendengarkan |
| 8000 | tidak terjangkau |
| 3000 | tidak terjangkau |
| 8501 | tidak terjangkau |

Pemetaan port 3000 yang ada di `docker-compose.yml` dihapus di override VM ini, dan 8000
dipindahkan ke loopback. Keduanya memang sudah tertutup firewall; menghapusnya membuat
konfigurasi tidak lagi menggantungkan keamanannya pada satu aturan jaringan yang kebetulan
berlaku.

**443 tidak dilayani, dan itu disengaja.** HTTPS menuntut sertifikat, dan otoritas sertifikat
publik tidak menerbitkan sertifikat untuk alamat IP telanjang - hanya untuk nama domain.
Pilihan yang tersisa adalah sertifikat tanda tangan sendiri, yang membuat peramban menampilkan
layar peringatan merah sebelum situs terbuka. Untuk demo yang dibuka juri, layar peringatan itu
lebih merugikan daripada ketiadaan HTTPS. Bila kelak ada nama domain, Let's Encrypt dapat
dipasang dan port 443 sudah terbuka menunggu.

### 4. IP bersifat efemeral

Diketahui dan sudah dicatat di bagian Mesin. Tidak dapat diperbaiki dari akun ini; lihat
bagian Izin.

### 5. VM masih polos, pasang kebutuhan sendiri

Terpasang: Docker Engine + Compose plugin, `python3-pip` (untuk mengunduh checkpoint), `git`,
`tmux`. Selebihnya hidup di dalam image, bukan di sistem induk - itulah sebabnya menyiapkan
ulang di mesin lain hanya menuntut Docker.

## Menyiapkan dari nol

```bash
git clone https://github.com/MikaelAdikara/BPS_AIC.git && cd BPS_AIC
pip install huggingface_hub && python3 scripts/download_checkpoint.py
docker compose up -d --build
```

Tanpa langkah checkpoint, sistem tetap berjalan memakai jalur leksikon dan menyatakan alasannya
di `/api/v1/readiness` - tetapi yang berjalan bukan sistem yang dijelaskan proposal.
