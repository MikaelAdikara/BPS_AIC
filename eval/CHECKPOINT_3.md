# Checkpoint 3 — model freeze

Halaman ini memetakan isi checkpoint 3 ke berkasnya. Versi yang dibekukan: **`gap-v1.19` /
`verify-v2.6`** (basis `d192d46` = `gap-v1.17`). Model LLM `gpt-5-mini`, reasoning `low`. Angka memakai format
`k/n (persen; interval Wilson 95%)`.

| Isi | Letak |
|---|---|
| Versi beku dan alasannya | §1 |
| Siklus iterasi terakhir (temuan → perbaikan → uji ulang) | §2 (`rc-v1.16/`, `rc-v1.17/`) dan §2a (`rc-v1.17-r2/`, `rc-v1.18/`, `rc-v1.18-r2/`, `rc-v1.19/`, `rc-v1.19-r2/`) |
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
(`rc-v1.17`). Audit data nyata berikutnya menemukan dua masalah pengelompokan (§2a). `gap-v1.18`
memperbaikinya, tetapi dua run eval ditambah replikasi `gap-v1.17` menunjukkan veto barunya membuang
bukti emas; `gap-v1.19` mempersempit veto itu. Setiap versi diuji dua kali pada 62 kasus yang sama.
Tidak ada perubahan engine sesudah run `rc-v1.19` dimulai.

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

## 2a. Iterasi 11–12 — pengelompokan antar-temuan (gap-v1.17 → gap-v1.18 → gap-v1.19)

**Temuan** (audit bukti di 15 produk demo sesudah `gap-v1.17`):

| Masalah | Contoh | Jumlah |
|---|---|---|
| Klausa yang sama terhitung di dua atau tiga temuan | "sampai 11 jam tak kunjung full" di fast charging **dan** input pengisian; "sesuai harga. lumayan agak tipis, seller respon lambat" dikutip utuh di bahan, ketebalan busa, **dan** respon penjual | 17 pasang |
| Keluhan atribut lain masuk temuan yang salah | "Poto nya beda", "tidak sesuai dengan gambar" → ukuran tas; dua keluhan voucher/koin → layanan kurir | 4 kutipan |

**Diagnosis.** (1) Di jalur *dispute*, second read yang menyatakan "reports" langsung diterima walau
juri kode membaca klausa itu sebagai keluhan atribut lain (`complaint_not_about_this_attribute`);
di jalur *orphan*, klausa tanpa atribut yang dikenal diterima, sementara kosakata foto ("poto") dan
kompensasi (voucher, koin, retur) belum ada di leksikon. (2) Second read `confirm` memeriksa setiap
pasangan (ulasan, temuan) sendiri-sendiri, jadi tidak ada tahap yang melihat bahwa satu klausa
sudah dipakai temuan lain.

**Perbaikan** (aturan umum, bukan kata per kasus):

1. `_about_other_attribute`: second read ditolak bila **kata yang dikutip** adalah keluhan foto/gambar
   atau kompensasi pesanan (kelompok meta `appearance`, `refund`) dan tidak menyebut atribut temuan
   ini. Keluhan semacam itu tidak pernah menjadi bukti atribut fisik. Klausa tanpa atribut yang
   dikenal tetap lolos agar kosakata keluhan baru ("mentok 30") tidak hilang. (Versi v1.18 memakai
   semua kelompok leksikon; lihat iterasi 12 di bawah.)
2. Leksikon: "poto" masuk kelompok tampilan; kelompok baru `refund` (voucher, koin, cashback, retur,
   pengembalian) bersifat operasional.
3. `exclusive_clauses` (sesudah `dedupe`): satu klausa menjadi bukti satu temuan. Ulasan boleh
   mendukung beberapa temuan bila klausanya berbeda. Kutipan seluruh ulasan dipersempit ke klausa di
   dalam kutipan yang menyebut atribut temuan itu. Klausa yang tetap bentrok dipegang temuan yang
   atributnya disebut klausa itu, lalu yang dukungannya terbanyak; temuan lain memindahkannya ke
   "tidak jelas" (`clause_counted_in_other_finding`).

Lima belas tes baru di `tests/unit/test_deciqo_engine_grouping.py`, termasuk tiga yang lahir dari
regresi saat replay (atribut di luar leksikon seperti "earbud kiri/kanan", ulasan bertemplat
Lazada, dan kutipan yang tidak boleh melebar ke klausa lain).

**Uji ulang pada data nyata.** Replay dari cache analisis (tanpa panggilan model) di dalam kontainer,
dengan triage IndoBERT yang sama; replay `gap-v1.17` mereproduksi hasil live persis (61 temuan / 199
bukti), jadi selisih di bawah hanya berasal dari perubahan kode.

| 15 produk demo | gap-v1.17 | gap-v1.18 | gap-v1.19 |
|---|---|---|---|
| Temuan / bukti | 61 / 199 | 59 / 181 | 59 / 181 (identik dengan v1.18) |
| Pasangan klausa sama di dua temuan | 17 | **0** | **0** |
| Kutipan salah kelompok (tabel temuan) | 4 | **0** | **0** |
| Ulasan yang sah mendukung >1 temuan dengan klausa berbeda | — | 24 | 24 |

Dua temuan hilang karena seluruh buktinya adalah klausa yang sudah dihitung temuan lain ("kapasitas
baterai dan performa pengisian" vs "daya baterai sangat singkat"; "label/varian vs barang" yang
hanya berisi "tidak sesuai deskripsi 66 watt"). Satu kehilangan yang tidak diinginkan:
"lengennya kurang pajang kain nya tipis…" kini hanya terhitung di ketebalan kain karena ejaan
"pajang"/"lengen" tidak dikenal leksikon.

**Uji ulang pada kasus eval** (62 kasus, sistem D, dua run per versi pada hari yang sama agar efek
perubahan bisa dipisahkan dari variasi antar-run; `rc-v1.17-r2` dijalankan dari commit `d192d46`).

**Temuan dari rc-v1.18 (iterasi 12).** Recall holdout v1.18 lebih rendah di **kedua** run (97, 96)
dibanding kedua run v1.17 (101, 99). `recall_loss.py` menunjukkan 3–4 bukti emas baru berstatus
`complaint_not_about_this_attribute`: veto second read membuangnya karena kelompok leksikon terlalu
kasar ("kecemplung ember … ga **nyala**" = baterai pada temuan tahan air; "ipad **air**" = air pada
kompatibilitas; "yang kanan **mati**" pada ketahanan earbud). Veto tidak mencatat alasannya sendiri,
jadi grep awal atas `quote_about_other_attribute` tidak menemukannya. Aturan satu-klausa hanya
sekali memindahkan bukti emas (h15/r1, satu dari dua run).

**Perbaikan gap-v1.19.** Veto dibatasi ke kelompok meta (foto/gambar, kompensasi). Tiga kutipan
emas tadi menjadi tes regresi. Di data nyata hasilnya identik dengan v1.18 (semua salah kelompok
yang ditemukan audit adalah keluhan foto atau voucher).

Satu sel = dua run (`rc-vX` / `rc-vX-r2`). Biaya ±$0,52 per run.

| Metrik D | gap-v1.17 | gap-v1.18 | **gap-v1.19 (beku)** |
|---|---|---|---|
| Holdout: temuan emas ditemukan | 36/36, 36/36 | 36/36, 36/36 | 36/36, 36/36 |
| Holdout: membership precision | 101/102, 99/99 | 97/98, 96/97 | 97/97, 98/99 |
| Holdout: membership recall | 101/125, 99/125 | 97/125, 96/125 | 97/125, 98/125 |
| Holdout: fakta ditahan | 24/24, 24/24 | 23/24, 24/24 | 24/24, 23/24 |
| Holdout: ready after fact | 20/24, 20/24 | 19/24, 19/24 | 19/24, 17/24 |
| Development: membership recall | 44/53, 43/53 | 46/53, 40/53 | 43/53, 43/53 |
| Development: membership precision | 44/44, 43/43 | 46/46, 40/40 | 43/44, 43/43 |
| Development: fakta ditahan | 13/13, 13/13 | 12/13, 13/13 | 11/13, 13/13 |
| Pola terlarang di draf (after) | 0 | 0 | 0 |
| Kontrol pujian | h20 (1 temuan) | h20 | h20 |
| Bukti emas terbuang oleh veto second read | 0 | 3, 4 | **0, 0** |
| Bukti emas dipindah oleh aturan satu klausa | — | 1, 0 | 1, 0 |
| Gerbang development | PASS, PASS | FAIL, PASS | FAIL, PASS |
| Gerbang holdout | FAIL (h20) ×2 | FAIL | FAIL |

**Bacaan.** v1.19 menghilangkan kerusakan veto v1.18 (bukti emas terbuang 3–4 → 0) dan precision
tetap ≥97/99. Recall holdout rata-rata 97,5 vs 100 pada v1.17; dari selisih itu, aturan satu klausa
menjelaskan rata-rata 0,5 bukti per run, sisanya berada di rentang variasi antar-run yang terlihat di
tabel (v1.17 sendiri 99–101). Kegagalan "fakta ditahan" (c20, c02, h33, h11) semuanya satu temuan
yang oleh discovery diberi tipe `expectation_mismatch`, dan tidak satu pun tersentuh veto atau aturan
satu klausa; pola yang sama tercatat di v1.14 dan v1.16. Gerbang tidak diubah. Kontrol pujian h20
tetap gagal di semua versi (keputusan label checkpoint 2 §6).

## 3. Uji ulang pada data nyata

Workspace demo: 15 produk, sebagian besar snapshot publik Lazada. Sebelum iterasi ini seluruh
analisis tersimpan masih `gap-v1.9` (second read belum pernah berjalan pada data ini), jadi selisih
di bawah adalah efek gabungan v1.9 → v1.17, bukan efek iterasi ini saja. Kolom `gap-v1.19` adalah
state live sesudah rebuild kontainer (lihat §2a untuk selisih v1.17 → v1.19).

| | Sebelum (`gap-v1.9`) | `gap-v1.17` | **`gap-v1.19` (beku)** |
|---|---|---|---|
| Produk dianalisis | 15 | 15/15, 0 gagal | 15/15, 0 gagal |
| Pujian/kolom templat yang terhitung sebagai keluhan (daftar §2) | 8 kutipan di 5 temuan | 0 | 0 |
| Temuan yang seluruh buktinya pujian | 1 ("Ideal untuk laptop 14-15 inci") | 0 | 0 |
| Temuan / total ulasan pendukung | — | 61 / 199 | 59 / 181 |
| Klausa sama terhitung di dua temuan | — | 17 pasang | 0 |
| Kutipan salah kelompok (§2a) | — | 4 | 0 |
| Second read: diterima / ditarik / diveto | — | 46 / 5 / 19 | — |

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

1. **Pengelompokan antar-temuan: sebagian besar selesai di `gap-v1.19` (§2a).** Sisa: "paket cuma
   datang satu" masih masuk temuan salah varian (kurang jumlah terbaca sebagai salah kirim; rutenya
   tetap operasional). Pemilihan temuan untuk klausa yang bentrok memakai kosakata leksikon, jadi
   ejaan di luar kosakata ("pajang", "lengen") kalah dari temuan lain; di eval v1.18 ini memindahkan
   1 bukti emas (h15/r1) di satu dari dua run. Veto salah kelompok hanya mengenal foto/gambar dan
   kompensasi; salah kelompok lain belum tertangkap. Belum ada gerbang eval khusus untuk salah kelompok.
2. **Satu klausa di dua temuan: selesai di `gap-v1.19`** (17 → 0 pasang di data nyata). Ulasan yang
   memuat dua masalah berbeda tetap dihitung di kedua temuan (24 ulasan).
3. **Tidak ada gold set berlabel untuk data Lazada.** §3 adalah audit satu penilai, bukan skor.
4. Butir checkpoint 2 §6 yang masih terbuka: hold berlebih, label manusia buta (`labels.csv`),
   replikasi antar-run, klasifier neural tidak lebih baik dari leksikon.
5. **Token bot Telegram** sudah telanjur tercatat di log kontainer sebelum perbaikan; perlu dirotasi.

## 6. Bukti eksekusi dan reproduksi

- `eval/final/checkpoint-3/pytest.txt`: 748 tes backend/integrasi lulus, 3 dilewati karena snapshot data tidak ada di git (`gap-v1.19`, worktree bersih tanpa perubahan lain).
- `eval/final/checkpoint-3/web.txt`: 29 tes web lulus, typecheck lulus.
- `eval/final/checkpoint-3/validate_cases.txt`: 62 kasus valid.
- `eval/final/rc-v1.19/`, `rc-v1.19-r2/`, `rc-v1.18/`, `rc-v1.18-r2/`, `rc-v1.17-r2/`, `rc-v1.17/`, `rc-v1.16/`: `manifest.json`,
  `outputs.jsonl`, `report.md`, `gate.md`. `rc-v1.17-r2` dijalankan dari commit `d192d46`.
- `eval/final/rc-v1.16/` disimpan utuh sebagai run yang memicu iterasi 10, bukan diganti.
- Runtime: `/api/v1/version` melaporkan `gap-v1.19` / `verify-v2.6`; 15/15 produk demo tersimpan
  dengan versi itu (analisis ulang dari cache, 0 gagal; backup DB sebelum rebuild di volume data).
  Pemeriksaan ulang saat startup melewati 12 produk karena IndoBERT belum dimuat (hash triage
  berbeda); dijalankan ulang dengan `DECIQO_TRIAGE_LOAD_MODEL=true`.

```powershell
.venv/Scripts/python.exe -m pytest tests -q
npm --prefix apps/web test
.venv/Scripts/python.exe eval/run_final.py --holdout --systems D --budget 1.5 --workers 10 --out eval/final/rc-v1.19
.venv/Scripts/python.exe eval/quality_gate.py --status all eval/final/rc-v1.19
.venv/Scripts/python.exe eval/recall_loss.py eval/final/rc-v1.19
```
