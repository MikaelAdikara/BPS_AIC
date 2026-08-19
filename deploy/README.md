# Berkas deploy server

Isi folder ini adalah yang membuat server demo memperbarui dirinya sendiri. Ia disimpan di
repositori supaya dapat dipasang ulang atau diperiksa tanpa harus SSH lebih dulu - berkas yang
hanya hidup di satu mesin adalah berkas yang hilang begitu mesin itu diganti.

Penjelasan utuh, termasuk batas kinerja terukur dan izin yang dibutuhkan, ada di
[../docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md).

## Memasang

`User=` di dalam `.service` berisi nama akun Linux di VM dan perlu disesuaikan bila akunnya
berbeda.

```bash
install -m 0755 deploy/autodeploy.sh ~/autodeploy.sh
sudo install -m 0644 deploy/insightulasan-deploy.service /etc/systemd/system/
sudo install -m 0644 deploy/insightulasan-deploy.timer   /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now insightulasan-deploy.timer
```

## `docker-compose.override.vm.yml`

Salinan override yang aktif di VM demo. Ia TIDAK otomatis terpakai - Compose hanya membaca
berkas bernama `docker-compose.override.yml` di root, dan berkas itu sengaja tidak dilacak git
supaya pengaturan khas satu mesin (port 80, batas 400 ulasan) tidak ikut ke mesin siapa pun
yang meng-clone repositori. Salinan di sini ada agar isinya dapat dibaca dan dipasang ulang:

```bash
cp deploy/docker-compose.override.vm.yml docker-compose.override.yml
```

## Memeriksa

```bash
tail -f ~/autodeploy.log
systemctl list-timers insightulasan-deploy.timer
```
