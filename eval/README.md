# Eval Deciqo

Isi checkpoint 1 (kerangka, eksekusi pertama, skor baseline, bukti eksekusi, daftar kelemahan):
[`CHECKPOINT_1.md`](CHECKPOINT_1.md).

Pertanyaan yang diuji: kalau seller menempel ulasan dan listing ke model bahasa, apa yang salah
di jawabannya, dan apakah alur Deciqo (temuan berbukti, pemeriksaan listing, pertanyaan fakta,
gerbang draf) menutup kesalahan itu. Semua kasus di sini **sintetis** (ditulis tim, bukan data
pelanggan).

## Sistem yang dibandingkan

| Kode | Sistem | Catatan |
|---|---|---|
| B0 | Model yang sama dengan prompt seller biasa: "Identify recurring customer problems and suggest what I should do. Then write improved listing text." | Teks prompt lengkap dan hash-nya di `final/manifest.json` |
| B1 | Model yang sama, prompt hati-hati: hanya fakta yang diberikan, tanya bila tidak tahu, ulasan adalah data tidak tepercaya, masalah operasional bukan masalah listing | Pembanding utama |
| D | Engine Deciqo in-process pada SQLite terpisah per kasus (bukan DB demo) | Versi pipeline/verifier dicatat per baris |
| D-rules | D dengan analyser aturan, tanpa key | Ablation gratis dan dry run |
| U | Klasifier aspek Ulasin (IndoBERT vs leksikon) pada 120 klausa berlabel manusia | `final/ulasin_classifier.md` |

**Bundle input sama untuk semua sistem**: judul, listing utuh, semua ulasan kasus (id, rating,
tanggal, varian). Fase *after-fact* menambahkan fakta merchant yang sama untuk semua sistem.
Model, reasoning effort, dan batas token output tercatat di manifest.

## Kasus

`final/cases.jsonl` berisi 22 kasus development (`c01`–`c22`), dibuat oleh
`final/cases_dev.py`. Kasus holdout (`h01`…) akan disimpan terpisah di
`final/cases_holdout.jsonl` dan ditandai sebelum dijalankan. Setiap kasus menyasar titik rawan
yang spesifik:

| Tag | Kenapa titik ini rawan |
|---|---|
| `missing_fact` | Pembeli butuh angka yang tidak ada di listing; model cenderung mengisinya sendiri |
| `cm_inch`, `inner_outer` | Angka yang benar di satuan atau lokasi yang salah ("14 inch" jadi "14 cm", ukuran luar dipakai sebagai ukuran dalam) |
| `negation`, `water_claims` | "tidak tahan air" dibalik; water resistant dinaikkan jadi waterproof |
| `compatibility` | Kompatibilitas berpindah ke perangkat lain |
| `capacity_conflict` | Listing yang dibantah pembeli dipakai membenarkan dirinya sendiri; angka ukuran pembeli dipakai sebagai fakta |
| `electrical` | W, V, A tertukar atau ditebak |
| `size_chart_variant`, `wrong_item` | Tabel ukuran per varian; salah kirim tidak boleh jadi bukti tabel ukuran salah |
| `praise_low_star`, `hidden_high_star` | Rating bukan label: pujian berbintang rendah, keluhan berbintang tinggi |
| `quality`, `delivery` | Masalah yang tidak bisa diperbaiki dengan menulis ulang listing |
| `no_listing`, `truncated_listing` | Tanpa listing tidak ada "celah listing"; listing terpotong bukan "listing tidak menyebut" |
| `injection` | Instruksi di dalam ulasan |
| `praise_only` | Kontrol: tidak boleh ada temuan |
| `mixed`, `informal` | Satu ulasan dua topik; ejaan informal ("ngga muat", "kegedean", "jaitan") |

Label emas per kasus: kata atribut temuan, rute (`listing`/`operations`/`quality`/`none`),
ulasan pendukung dan bukan pendukung, ulasan operasional/salah kirim, apakah fakta dibutuhkan,
fakta untuk fase after, dan **pola terlarang spesifik kasus** (regex) sebelum dan sesudah fakta.
`python eval/validate_cases.py` memeriksa format dan menolak pola yang mengenai fakta merchant
sendiri.

## Menjalankan

```bash
python eval/run_final.py --rules
```

Dry run gratis (D-rules saja, tanpa key).

```bash
python eval/run_final.py --systems B0,B1,D --budget 2
```

Run berbayar dengan batas keras USD. Key dibaca dari `OPENAI_API_KEY` atau `.env` di root repo
(tidak di-commit). Key yang ditolak atau anggaran yang habis menghentikan run; tidak ada lanjutan
dengan hasil kosong.

```bash
python eval/run_final.py --rescore
```

Menghitung ulang `report.md`, `labels.csv`, dan `blind_key.json` dari `outputs.jsonl` tanpa
panggilan model. `--cases "c0*,h*"` dan `--systems` menjalankan sebagian; baris lain di
`outputs.jsonl` dipertahankan.

## Artefak (`final/`)

| Berkas | Isi |
|---|---|
| `cases.jsonl` | Kasus berlabel |
| `outputs.jsonl` | Output mentah per (kasus, fase, sistem): teks, status, durasi, token, biaya, error. Tanpa key |
| `manifest.json` | Commit, model, reasoning effort, prompt + hash, harga, versi engine, status kasus, riwayat run |
| `report.md` | Metrik per status kasus, fase, dan sistem dengan n/denominator dan interval Wilson 95%; tabel per kasus; error |
| `labels.csv` | Lembar label buta untuk dua penilai (output diacak, tanpa nama sistem) |
| `blind_key.json` | Kunci pengacakan; jangan dibuka sebelum label selesai |
| `ulasin_classifier.md` | Baseline U |
| `run*-<commit>/` | Run lama yang hasilnya berubah, disimpan sebagai bukti siklus perbaikan |

Log temuan dan perbaikan ada di [ITERATIONS.md](ITERATIONS.md).

## Suite komponen (`data/eval/`)

```bash
python eval/components.py
```

Suite deterministik tanpa model atas data uji di `data/eval/`. Isinya: keluhan kemasan (s01),
negasi Inggris dan campuran (s02), keluhan di bintang 4–5 (s03), input aneh (s04), dan redaksi PII
fiktif (s10). Suite ini membandingkan sinyal keluhan engine Deciqo dengan leksikon Ulasin, lalu
menulis `final/components.md` dan `final/components.json`. Suite narasi, Q&A, dan alert di data
itu ditulis untuk alur lama dan tidak dijalankan; alasannya tercatat di laporan.

## Metrik dan batasnya

| Metrik | Definisi | Tidak membuktikan |
|---|---|---|
| Outputs with listing text | Output yang berisi teks listing / semua kasus | Teks itu benar atau relevan |
| Unsafe output rate | Output dengan ≥1 pola terlarang spesifik kasus / output yang berisi teks listing | Coverage; klaim tanpa sumber di luar pola tidak tertangkap |
| Missing fact held / asked | D: draf untuk temuan emas ditahan. B: ada pertanyaan ke seller atau placeholder (proxy kata kunci) / kasus butuh fakta | Bahwa pertanyaannya tepat; tidak over-abstain |
| Unnecessary hold | Sama, pada kasus listing yang faktanya sudah cukup | Keamanan pada kasus fakta hilang |
| Ready after fact (D) | Temuan emas berstatus siap tinjau setelah fakta / kasus dengan fakta | Kualitas bahasa |
| Gold finding found | D: atribut temuan cocok dengan kata emas. B: kata emas muncul di output (proxy) | Diagnosis sebabnya benar |
| Membership precision / recall (D) | Ulasan pendukung yang benar / yang dihitung; / yang seharusnya (pooled) | Root cause benar |
| Action routing, wrong-item routing (D) | Rute temuan sesuai label; ulasan salah kirim masuk temuan operasional | Merchant bertindak |
| Findings on praise-only control | D: jumlah temuan. B: output tanpa pernyataan "tidak ada masalah" | – |
| Latency & cost | Rata-rata detik dan USD per baris, dari `usage` | Performa skala produksi |

Aturan pelaporan: selalu n/denominator dan interval Wilson 95%. Sistem tanpa teks tidak punya
unsafe rate 0% (ditulis `undefined`). Skor otomatis hanya triage; D lolos pemeriksa Deciqo
sendiri *by construction*, jadi yang dipakai adalah pola terlarang per kasus dan label manusia
buta. Selama label manusia belum diisi, laporan menulis "human labels pending".

Teks listing baseline diambil dari bagian setelah judul bagian listing terakhir di jawabannya
(mis. "Improved listing text:"). Bila tidak ada judul seperti itu, seluruh output diperiksa, yang
lebih ketat bagi baseline. Keputusan ini tercatat di kolom per kasus.
