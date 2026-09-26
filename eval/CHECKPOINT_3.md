# Checkpoint 3 — model freeze

Halaman ini memetakan isi checkpoint 3 ke berkasnya. Versi yang dibekukan: **`gap-v1.17` /
`verify-v2.6`** (commit checkpoint ini; basis `9cd3acc`). Model LLM `gpt-5-mini`, reasoning `low`. Angka memakai format
`k/n (persen; interval Wilson 95%)`.

| Isi | Letak |
|---|---|
| Versi beku dan alasannya | §1 |
| Siklus iterasi terakhir (temuan → perbaikan → uji ulang) | §2, run `eval/final/rc-v1.16/` dan `rc-v1.17/` |
| Uji ulang pada data nyata (15 produk di workspace demo) | §3 |
| Product Track sejak checkpoint 2 | §4 |
| Yang belum berhasil | §5 |
| Bukti eksekusi | §6, log di `eval/final/checkpoint-3/` |

## 1. Versi beku

Checkpoint 2 membekukan kandidat `gap-v1.15` (second read). Setelah itu kontainer lokal di-rebuild
dan seluruh workspace demo dianalisis ulang. Pembacaan manual atas bukti yang dihitung di data
Lazada nyata menemukan satu pola salah klasifikasi yang tidak muncul di kasus sintetis, lalu
diperbaiki di `gap-v1.16`. Run eval `rc-v1.16` lalu menunjukkan satu bagian perbaikan itu
membuang keluhan asli; itu diperbaiki di `gap-v1.17` dan diuji ulang pada 62 kasus yang sama
(`rc-v1.17`). Tidak ada perubahan engine sesudah run `rc-v1.17` dimulai.

## 2. Iterasi 9–10 — gerbang sebutan netral (gap-v1.15 → gap-v1.16 → gap-v1.17)

**Temuan.** Di data nyata, kalimat pujian dan kolom templat ulasan Lazada dihitung sebagai keluhan:

| Kutipan yang terhitung sebagai keluhan | Temuan |
|---|---|
| "Pilihan kabel yang serbaguna," | kabel bawaan 4-in-1 |
| "🔋Kapasitas: 20000mah", "🔋Kapasitas:20000" | kapasitas baterai |
| "⚡Kecepatan Pengisian:Kecepatan pengisian yang efisien" | fast charging |
| "Ideal untuk laptop 14-15 inci" (×3, bintang 5) | ukuran kompartemen laptop (seluruh temuan) |
| "sudah mendukung fitur vooc di hp Oppo keren gw recommend" | fast charging |

Diagnosis dengan `relevance.judge`: tujuh kutipan pertama dibaca kode sebagai
`mentions_attribute_without_complaint` (menyebut atribut, tanpa keluhan). Jalur itu sengaja
menerima label membership agar kosakata keluhan baru tidak hilang, sehingga satu label model sudah
cukup untuk menghitung sebuah pujian. Kutipan VOOC lolos lewat jalur sengketa.

**Perbaikan** (tanpa menambah kata per kasus):

1. Bukti yang dibaca kode sebagai sebutan netral diberi tanda dan **hanya dihitung bila second
   read yang independen juga menyatakan "reports"**. Kutipan yang ditampilkan diganti dengan kata
   penentu dari second read bila verbatim. Tanpa suara kedua (provider gagal, cache kosong),
   ulasannya pindah ke "tidak jelas" (`neutral_mention_unconfirmed`).
2. Kutipan second read yang berbunyi pujian tidak diterima di jalur konfirmasi, sengketa, maupun
   yatim (`quote_reads_as_praise`).
3. Kosakata pujian **umum** di leksikon: serbaguna, efisien, ideal, keren, recommend, mendukung,
   praktis, dan sejenisnya. Bila dinegasikan ("kurang efisien", "tidak mendukung fast charging")
   tetap terbaca keluhan.

Delapan tes regresi baru (termasuk kasus v1.17) di `tests/unit/test_deciqo_engine_second_read.py`.

**Uji ulang pada kasus eval** (`eval/final/rc-v1.16/`, 62 kasus, sistem D saja):

Semua angka D, satu run per versi. rc-v1.15 berasal dari checkpoint 2 (holdout saja).

| Metrik D | rc-v1.15 holdout | rc-v1.16 holdout | rc-v1.16 development |
|---|---|---|---|
| Temuan emas ditemukan | 36/36 | 36/36 (100%; 90–100) | 21/21 (100%; 85–100) |
| Routing | 36/36 | 35/36 (97%; 86–100) | 21/21 |
| Membership precision | 106/107 | 96/97 (99%; 94–100) | 43/43 (100%; 92–100) |
| Membership recall | 106/125 (85%; 77–90) | **96/125 (77%; 69–83)** | 43/53 (81%; 69–89) |
| Fakta ditahan | 24/24 | 24/24 | **12/13** |
| Ready after fact | 19/24 | 19/24 (79%; 60–91) | 12/13 |
| Pola terlarang di draf | 0/20 | 0/32 (gabungan) | |
| Kontrol pujian | 1 temuan (h20) | 1 temuan (h20) | 0 |

Gerbang `rc-v1.16`: **FAIL** pada h20 (sama seperti v1.15) dan fakta ditahan dev 12/13 (juga terjadi
di v1.14; variasi antar-run yang sudah tercatat). Semua gerbang akurasi lulus. Biaya run $0,5206.

**Temuan dari rc-v1.16.** Recall holdout turun 10 bukti dengan precision tetap (satu bukti salah).
`recall_loss.py` mengatribusikan 4 bukti emas yang hilang ke `second_read_praise`: pembaca kedua
menyatakan "reports", tetapi kutipannya dibaca pujian oleh leksikon, misalnya "pendek banget,
kirain bisa setinggi badan" (kata "bisa"). Aturan v1.16 butir 2 terlalu kasar untuk kalimat
harapan-vs-kenyataan. Sisa selisih berada di rentang variasi antar-run.

**Perbaikan gap-v1.17.** Bila pembaca kedua menyatakan "reports", dua suara independen sepakat dan
bukti tetap dihitung; bunyi kutipan hanya menentukan kutipan mana yang ditampilkan. Pujian murni di
data nyata tetap tertahan oleh kosakata pujian (dibaca kebalikan, bukan netral) dan gerbang sebutan
netral. Tes regresi baru untuk kasus h23/r1.

**Uji ulang gap-v1.17** (`eval/final/rc-v1.17/`, 62 kasus yang sama, sistem D, biaya $0,5233):

| Metrik D | rc-v1.15 holdout | rc-v1.16 holdout | **rc-v1.17 holdout** | rc-v1.17 development |
|---|---|---|---|---|
| Temuan emas ditemukan | 36/36 | 36/36 | 36/36 (100%; 90–100) | 21/21 (100%; 85–100) |
| Routing | 36/36 | 35/36 | 35/36 (97%; 86–100) | 21/21 |
| Membership precision | 106/107 | 96/97 | 101/102 (99%; 95–100) | 44/44 (100%; 92–100) |
| Membership recall | 106/125 (85%) | 96/125 (77%) | **101/125 (81%; 73–87)** | 44/53 (83%; 71–91) |
| Fakta ditahan | 24/24 | 24/24 | 24/24 | 13/13 |
| Ready after fact | 19/24 | 19/24 | 20/24 (83%; 64–93) | 10/13 (77%; 50–92) |
| Pola terlarang di draf | 0/20 | | 0/20 | 0/11 |
| Kontrol pujian | 1 (h20) | 1 (h20) | 1 (h20) | 0 |

Gerbang: development **PASS** penuh; holdout dan gabungan **FAIL hanya pada h20** (keputusan label
yang sama seperti checkpoint 2 §6). `second_read_praise` tidak lagi muncul di `recall_loss.py`
(145/178 bukti emas terhitung di seluruh 62 kasus, 16 terhitung di temuan lain).

Batas: recall holdout v1.17 masih 5 bukti di bawah v1.15 dalam satu run per versi; selisih itu
belum bisa dipisahkan dari variasi antar-run (±3 di Iterasi 3) tanpa replikasi. Ready after fact
development turun 12/13 → 10/13; belum dianalisis per kasus.

## 3. Uji ulang pada data nyata

Workspace demo: 15 produk, sebagian besar snapshot publik Lazada. Sebelum iterasi ini seluruh
analisis tersimpan masih `gap-v1.9` (second read belum pernah berjalan pada data ini), jadi selisih
di bawah adalah efek gabungan v1.9 → v1.17, bukan efek iterasi ini saja.

| | Sebelum (`gap-v1.9`) | Sesudah (`gap-v1.17`) |
|---|---|---|
| Produk dianalisis | 15 | 15/15, 0 gagal |
| Pujian/kolom templat yang terhitung sebagai keluhan (daftar §2) | 8 kutipan di 5 temuan | 0 |
| Temuan yang seluruh buktinya pujian | 1 ("Ideal untuk laptop 14-15 inci") | 0 |
| Temuan / total ulasan pendukung | — | 61 / 199 |
| Second read: diterima / ditarik / diveto | — | 46 / 5 / 19 |

Keluhan nyata yang sebelumnya tidak terhitung kini muncul, misalnya "Trus gak ada kabel usb buat
nge-charge-nya" dan "bukan 20000 tapi 10000". Pemeriksaan ini dilakukan satu penilai (penulis
perbaikan) dengan membaca semua kutipan; belum ada label buta.

## 4. Product Track sejak checkpoint 2

| Area | Perubahan |
|---|---|
| Halaman produk | Kolom baca terpusat (maks. 1040 px); konten workspace selalu di tengah. Judul landing versi Indonesia dari 5 baris menjadi 3 |
| Tombol "Langkah berikutnya" | Menjalankan langkahnya, bukan hanya menyebutnya: isi fakta, buat draf, buka listing, atau untuk isu operasional menyalin ringkasan siap kirim (isu, hitungan, kutipan verbatim) dan bisa langsung **dikirim ke Telegram** (`POST /telegram/brief`) |
| Jalan buntu | "Buat draf" dan "Cek foto" kini ada di kartu temuan, tidak lagi hanya di Detail investigasi yang terlipat |
| Catat keputusan | Satu klik: pilihan cepat sesuai rute isu (listing / QC / operasional), detail opsional; abaikan satu klik per alasan. Server tetap menyimpan catatan |
| Rentang tanggal | Kolom "Dari / Sampai" bisa diketik; kalender melompat ke tanggal itu. Sebaran bintang mengikuti rentang terpilih, "Sepanjang waktu" sebagai pembanding |
| Keamanan | Log httpx menulis URL Bot API Telegram beserta token bot; logger httpx kini di level WARNING |

## 5. Yang belum berhasil

1. **Pengelompokan antar-temuan** di data nyata kadang meleset: "Poto nya beda" masuk ke temuan
   ukuran tas, keluhan voucher/refund tergabung ke temuan kurir, "paket cuma datang satu" dilabeli
   salah varian. Polaritasnya benar; atribut tujuannya yang keliru. Belum ada gerbang eval untuk ini.
2. **Satu ulasan dapat terhitung di dua temuan** ("sampai 11 jam tak kunjung full" di fast charging
   dan input pengisian). Sering sah (dua masalah dalam satu ulasan), tetapi belum diukur.
3. **Tidak ada gold set berlabel untuk data Lazada.** §3 adalah audit satu penilai, bukan skor.
4. Butir checkpoint 2 §6 yang masih terbuka: hold berlebih, label manusia buta (`labels.csv`),
   replikasi antar-run, klasifier neural tidak lebih baik dari leksikon.
5. **Token bot Telegram** sudah telanjur tercatat di log kontainer sebelum perbaikan; perlu dirotasi.

## 6. Bukti eksekusi dan reproduksi

- `eval/final/checkpoint-3/pytest.txt`: 735 tes backend/integrasi lulus.
- `eval/final/checkpoint-3/web.txt`: 29 tes web lulus, typecheck lulus.
- `eval/final/checkpoint-3/validate_cases.txt`: 62 kasus valid.
- `eval/final/rc-v1.17/` dan `rc-v1.16/`: `manifest.json`, `outputs.jsonl`, `report.md`, `gate.md`.
- `eval/final/rc-v1.16/` disimpan utuh sebagai run yang memicu iterasi 10, bukan diganti.
- Runtime: `/api/v1/version` melaporkan `gap-v1.17` / `verify-v2.6`; 15/15 produk demo tersimpan
  dengan versi itu (analisis ulang 0 gagal).

```powershell
.venv/Scripts/python.exe -m pytest tests -q
npm --prefix apps/web test
.venv/Scripts/python.exe eval/run_final.py --holdout --systems D --budget 1.5 --workers 10 --out eval/final/rc-v1.17
.venv/Scripts/python.exe eval/quality_gate.py --status holdout eval/final/rc-v1.17
.venv/Scripts/python.exe eval/recall_loss.py eval/final/rc-v1.17
```
