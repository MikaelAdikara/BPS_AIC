# Demo live: toko WooCommerce asli → Deciqo

Toko WordPress + WooCommerce sungguhan berjalan di Docker (profile `store`), berisi katalog demo
yang sama dengan akun demo Deciqo. Ulasan yang ditulis di storefront memicu **webhook bawaan
WooCommerce** ke Deciqo. Deciqo langsung sinkron lewat REST, menganalisis, dan layar Deciqo yang
sedang terbuka memunculkan kartu **Alert baru** tanpa perlu refresh.

Semua isi toko (produk, ulasan, nama pengulas) ditulis tim, jadi tetap diberi label data demo.

## Menyalakan

```
docker compose --profile store up -d --build
```

Build pertama mengunduh WooCommerce, Storefront, dan paket bahasa Indonesia, jadi butuh internet
sekali. Setelah itu image dan volume cukup untuk demo tanpa internet.

| Apa | Alamat |
|---|---|
| Deciqo | http://localhost:3000 (akun demo) |
| Storefront | http://localhost:8081 |
| Admin WordPress | http://localhost:8081/wp-admin (kredensial uji di `.env.example`) |
| Webhook di admin | WooCommerce → Settings → Advanced → Webhooks |

## Sekali sebelum demo

1. Login akun demo, buka **Sumber data → WooCommerce**, klik **Hubungkan dan sinkronkan** di kartu
   *Toko WooCommerce lokal*. Id produk dan ulasan sama dengan data demo, jadi tidak ada duplikat.
2. Tekan **Reset workspace** supaya toko dan Deciqo kembali ke kondisi awal. Butuh sekitar 1–2 menit
   karena 4 produk dianalisis ulang. Sambungan ke toko lokal tetap ada setelah reset.

## Alur di depan juri

1. Buka storefront, lalu produk **Kursi lipat camping** → tab **Ulasan**.
2. Beri 2 bintang dan tulis keluhan soal layanan penjual, misalnya
   *"Chat ke penjual tidak dibalas lagi, padahal mau tanya soal garansi."* Nama dan email boleh kosong.
   Klik **Kirim**.
3. Pindah ke tab Deciqo. Dalam sekitar 20–30 detik muncul progres *"Ulasan baru dari WooCommerce ·
   menyinkronkan"*, lalu kartu **Alert baru · Muncul lagi — Kursi lipat camping · respon penjual**.
   Isu ini sebelumnya sudah ditangani (keputusan *acted*), jadi ulasan baru membukanya lagi.
4. Klik **Buka temuan** untuk menjelaskan bukti, keputusan, dan tindak lanjut.

Contoh lain: tas laptop (*"laptop 14 inch tetap tidak muat"*) menambah bukti ke isu ukuran yang
sudah ada. Isu seperti ini tidak selalu memunculkan alert, karena alert hanya dibuat untuk isu baru
atau isu yang muncul lagi (lihat halaman Alert → *Kapan alert dibuat*). Jeda 24 jam per temuan
mencegah alert "Muncul lagi" berulang, dan Reset workspace mengosongkannya.

## Cara kerjanya

```
storefront (review) ─► WordPress: comment_post ─► action wc_deciqo_review_changed
   ─► webhook WooCommerce (HMAC-SHA256, dikirim langsung) ─► POST /api/v1/deciqo/woo/webhook
   ─► job woo_webhook: sinkron REST wc/v3 + analisis ─► alert_events
   ─► layar Deciqo: GET /api/v1/deciqo/pulse tiap 3 detik ─► kartu Alert baru
```

- `docker/wordpress/`: image toko, mu-plugin `deciqo-store.php` (seed, webhook, reset), dan
  `catalog.json` + gambar produk (dibuat ulang dengan `scripts/build_wp_store.py`; tes gagal bila
  tertinggal dari `demo_catalog.py`).
- Isi webhook tidak dipakai sebagai data. Ia hanya memicu sinkron penuh lewat REST, jalur yang sama
  dengan tombol Sync. Ulasan yang masuk saat sinkron sedang berjalan membuat sinkron diulang sekali,
  jadi tidak ada yang hilang.
- Deciqo membaca toko lewat application password (WordPress `WP_ENVIRONMENT_TYPE=local`
  mengizinkannya lewat HTTP). Host `wordpress` adalah satu-satunya pengecualian SSRF tambahan, dan
  hanya aktif bila `WOO_DEMO_MODE=true`.
- Gambar produk di `localhost` tidak dikirim ke model vision karena model tidak bisa mengambilnya.

## Kalau ada masalah

- Kartu toko lokal menulis "belum menyala": cek `docker compose --profile store ps`, lalu tunggu
  status `wordpress` menjadi *healthy* (seed jalan setiap start).
- Alert tidak muncul: `docker compose logs api | grep webhook` harus menunjukkan
  `webhook woo action.wc_deciqo_review_changed`. Kalau tidak ada, cek webhook di admin Woo (status
  *Active*).
- Mengembalikan toko saja tanpa mereset Deciqo:
  `docker compose --profile store exec wordpress wp --allow-root deciqo reset`.
