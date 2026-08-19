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

## Memeriksa

```bash
tail -f ~/autodeploy.log
systemctl list-timers insightulasan-deploy.timer
```
