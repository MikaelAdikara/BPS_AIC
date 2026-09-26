# Worklog platform

## Selesai dan terbukti

| Bagian | Bukti |
|---|---|
| SQLite + migrasi idempoten semua tabel, `/api/v1/version` | `tests/unit/test_deciqo_platform.py` |
| Akun: register/login/logout/me, sesi cookie HttpOnly (hash token disimpan), throttle login, isolasi 404 | tes platform + `test_isolasi_akun_404` |
| Ingest satu pintu: id stabil, redaksi PII sebelum simpan, statistik dari baris tersimpan, sinkron penuh menandai ulasan hilang | `test_deciqo_sources.py` |
| Impor tempel/CSV (header fleksibel, `rating \| teks`) | `test_impor_*` |
| Toko Woo sintetis (`woo-demo`) + konektor read-only anti-SSRF + sinkron + status sumber stale | `test_sinkron_*`, `test_ssrf_*`, `test_status_sumber_*` |
| Seed akun demo: katalog sintetis → analisis → fakta ukuran lipat + keputusan acted pada kursi lipat | dicoba di Docker: 4 produk dianalisis engine AI, `demo_state` facts=1 decisions=1, produk kontrol tanpa temuan |
| Job latar di DB, `interrupted` saat restart, maksimal 2 aktif/akun | `test_job_terputus_*` |
| Outbox alert: dedupe fingerprint, cooldown reopen 24 jam, 8/jam + ringkasan, pesan tanpa teks ulasan, sink simulasi untuk data sintetis | `test_alert_*`; di Docker: ulasan demo baru → alert `simulated` |
| Telegram: long polling, tautan kode sekali pakai / kontak sendiri, perintah ringkas, penerima demo dari `TELEGRAM_CHAT_ID` | `test_deciqo_platform_telegram.py`; bot tim nyata: pesan uji dan alert `new_issue` akun demo terkirim ke dua chat (status `sent`) |
| Lazada lewat Apify: fetch live dengan batas biaya + snapshot bertanggal 10 produk / 517 ulasan | `test_deciqo_sources_lazada.py`; biaya pengambilan snapshot $0.59 tercatat di ledger lokal |

## Keputusan

- Model teks dimuat di thread terpisah: endpoint akun dan workspace melayani sejak detik pertama;
  `/readiness` tetap 503 sampai model siap.
- `EMBEDDING_MODE=tfidf` bawaan: model embedding ~2 GB tidak diunduh saat startup.
- Pola redaksi alamat dipersempit (butuh nama berhuruf kapital) karena pola lama menghapus frasa
  umum di ulasan seperti "dibawa jalan jalan".
- Actor Lazada `lergassy/lazada-scraper` dipilih karena memberi tanggal ulasan absolut dan varian;
  actor lain yang dicoba hanya memberi 5 ulasan per produk dengan tanggal relatif.
- Snapshot Lazada menambah ulasan bintang 1–3 karena 30 ulasan terbaru hampir seluruhnya bintang 5;
  komposisinya ditulis di `data/marketplace/README.md`.

## Ditunda / terbuka

- Chat ID di `TELEGRAM_CHAT_ID` hanya menerima alert akun demo; akun lain wajib menautkan lewat kode bot.
