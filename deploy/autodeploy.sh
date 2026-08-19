#!/usr/bin/env bash
# Deploy otomatis InsightUlasan - dijalankan systemd timer tiap 2 menit.
#
# Berbasis polling, bukan GitHub Actions atau webhook. Alasannya: repositori ini publik, dan
# dua alternatif itu menuntut kunci SSH atau kredensial deploy disimpan sebagai secret di
# GitHub plus port masuk yang terbuka ke VM. Polling tidak menaruh rahasia apa pun di luar VM
# dan tidak membuka satu pun port baru. Harganya keterlambatan paling lama dua menit, yang
# tidak berarti apa-apa untuk demo lomba.
set -u

REPO_DIR="$HOME/BPS_AIC"
LOG="$HOME/autodeploy.log"
LOCK="$HOME/.autodeploy.lock"

catat() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

# Build memakan menit-menit. Tanpa kunci ini, timer berikutnya menyala di tengah build
# sebelumnya dan keduanya menulis ke direktori yang sama.
exec 9>"$LOCK"
flock -n 9 || exit 0

cd "$REPO_DIR" || { catat "FATAL: $REPO_DIR tidak ada"; exit 1; }

git fetch --quiet origin main || { catat "fetch gagal (jaringan?)"; exit 1; }

LOKAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
[ "$LOKAL" = "$REMOTE" ] && exit 0

catat "commit baru terdeteksi: ${LOKAL:0:7} -> ${REMOTE:0:7}"

# reset --hard, bukan pull: mesin ini target deploy, bukan tempat mengerjakan kode. Perubahan
# lokal apa pun di sini adalah kecelakaan dan harus kalah dari repositori. Berkas tak terlacak
# (docker-compose.override.yml) tidak tersentuh oleh reset.
git reset --hard --quiet origin/main || { catat "reset gagal"; exit 1; }
catat "sekarang di: $(git log -1 --format='%h %s' | cut -c1-70)"

# Build LEBIH DULU, tukar container hanya bila build berhasil. Urutan ini yang menjaga demo
# tetap hidup ketika rekan tim mendorong kode yang tidak bisa di-build: container lama terus
# melayani, dan kegagalannya tercatat alih-alih menjatuhkan situs.
if ! docker compose build >> "$LOG" 2>&1; then
    catat "BUILD GAGAL - deployment lama DIPERTAHANKAN, situs tetap hidup"
    exit 1
fi

if ! docker compose up -d >> "$LOG" 2>&1; then
    catat "GAGAL menjalankan container baru"
    exit 1
fi

# Tunggu API benar-benar siap sebelum menyatakan berhasil. Model butuh ~1 menit dimuat, dan
# melaporkan "berhasil" sebelum itu membuat log berbohong.
for _ in $(seq 1 24); do
    if curl -sf --max-time 5 http://127.0.0.1:8000/api/v1/readiness > /dev/null 2>&1; then
        MODE=$(curl -s --max-time 5 http://127.0.0.1:8000/api/v1/models | grep -o '"text_mode":"[^"]*"')
        catat "BERHASIL - API siap ($MODE)"
        docker image prune -f > /dev/null 2>&1   # image lama menumpuk mengisi disk
        exit 0
    fi
    sleep 10
done
catat "PERINGATAN: container jalan tetapi /readiness belum menjawab setelah 4 menit"
exit 1
