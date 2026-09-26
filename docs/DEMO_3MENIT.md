# Runbook demo live — 3 menit

Satu alur, satu produk: **Tas laptop kanvas 14 inci** di toko Woo sintetis. Diuji ulang 26 Sep 17.10 WIB
pada build `959e726` + perbaikan label draf. Kalimat panggung dalam bahasa Inggris (pitch English only).

## Persiapan (H-30 menit, urut)

1. `start.bat` → buka <http://localhost:3000>, login `demo@deciqo.app` / `deciqo-demo`.
2. **Reset workspace**: Data sources → WooCommerce → Reset (±90 detik, memanggil AI). Jangan muat paket
   Tokopedia/Lazada: Decision plan #1 harus tetap tas laptop.
3. Buka isu tas laptop (Overview → Decision plan #1 → **Open**) lalu klik **Run comparison** (±25 detik).
   Hasilnya tersimpan, jadi di panggung tidak perlu menunggu.
4. Cek status di Overview: kanal "Connected", engine AI (bukan rules). Bila `key_rejected`, lihat Cadangan.
5. Telegram (bila dipakai): isi `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_CHAT_ID` di `.env`, HP sudah `/start` ke
   bot, lalu `docker compose up -d api`. Uji dengan tombol tes di Settings. Nada notifikasi HP dinyalakan.
6. Siapkan dua tab: (a) isu tas laptop, (b) Data sources → WooCommerce → **Demo tools** (form review).
7. Zoom browser 110–125% supaya terbaca proyektor.

**Jangan gladi alur penuh setelah langkah 2.** Alert "came back" punya cooldown 24 jam per isu dan batas
8 alert/jam; gladi berulang membuat alert di panggung tidak keluar. Kalau terlanjur, reset lagi.

## Alur 3 menit

| Waktu | Layar dan klik | Kalimat |
|---|---|---|
| 0:00–0:20 | **Overview**. Tunjuk "Decision plan: do these first" | "This is a controlled, synthetic store connected through the WooCommerce REST API. Twenty-one reviews become five decisions, ranked by impact per minute of work." |
| 0:20–0:55 | Klik **Open** di #1. Tunjuk **1 · What customers say** (3/4, 1 tersembunyi di bintang 4–5, klik satu kutipan) lalu **2 · What your listing says** | "Three of four reviews, one of them hidden in a five-star review. Every number is counted, not generated. The listing promises it fits 14-inch laptops. That's the conflict. The missing fact is the inner compartment size." |
| 0:55–1:30 | Buka kartu **Compare with a general chatbot** (sudah dijalankan). Tunjuk baris *Blocked: unsourced claim* ukuran kompartemen (angkanya beda tiap run; baca yang tampil saat persiapan) | "Same model, same input, as a general chatbot. It writes a confident spec: [angka di layar] centimetres. Nobody measured that. Deciqo blocks it. On 40 held-out synthetic cases, a general chatbot added unsupported specs in 68% of drafts, 15% even with a careful prompt. Deciqo: 0 of the 20 drafts it wrote." |
| 1:30–2:00 | **3 · Confirm the missing fact**: ketik `kompartemen dalam 32 x 24`, unit `cm` → **Confirm fact** → **Draft listing fixes** → draft *Ready* | "So Deciqo asks the merchant to measure. Now the draft uses only that number, and cites where it came from." |
| 2:00–2:10 | **5 · Record your decision**: catatan singkat → **Mark applied** | "The merchant pastes it and marks it applied. Deciqo never edits the store." |
| 2:10–2:45 | Tab **Demo tools**: pilih tas laptop, rating 2, teks review (juri boleh mengetik) → kirim. Isi ±20 detik jeda dengan kalimat di kanan. Kembali ke isu: status **Came back**; HP bunyi | "Now a new review arrives. We poll the store every fifteen minutes; here we trigger the sync. …The issue came back, and the merchant just got this on Telegram: product, issue, count, link. No review text leaves the system." |
| 2:45–3:00 | Kembali ke Overview | "Hundreds of reviews. Three decisions that matter. Deciqo finds the missing fact, refuses to invent one, and keeps watching after you fix it." |

Teks review juri yang sudah teruji: `Laptop 14 inci saya tetap tidak masuk, resletingnya susah ditutup.`

## Jangan

- Jangan klik **Open live listing**: domain `woo-demo.deciqo.app` tidak ada.
- Jangan pakai tombol **Open next issue** di Overview: tombol itu membuka kemeja, bukan #1 Decision plan.
- Di kartu perbandingan, jangan berlama-lama di baris "Passed the fact gate". Gerbang memeriksa angka
  dan klaim berisiko, sehingga kalimat karangan tanpa angka (mis. "metal zipper") bisa lolos.
- Jangan menyebut "webhook" atau "realtime". W1 tidak dibangun; yang ada polling 15 menit dan sync manual.
- Jangan menyebut toko ini toko merchant. Label "Synthetic data" memang tampil di layar.

## Cadangan

| Gagal | Lakukan |
|---|---|
| OpenAI menolak key | Status berpindah ke rule engine berlabel. Katakan: "This is what the merchant sees when the AI provider is down: counts still work, drafts say unavailable." |
| Sync review juri > 40 detik | Lanjut ke penutup; buka hasilnya saat Q&A |
| Telegram tidak bunyi | Buka layar **Alerts**: event tercatat beserta status kirimnya |
| Laptop/Docker mati | Putar rekaman demo bertanggal (rekam hari ini setelah alur lulus) |
