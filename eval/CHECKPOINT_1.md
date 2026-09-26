# Checkpoint 1 — baseline

Halaman ini memetakan isi wajib checkpoint 1 ke berkasnya. Semua kasus sintetis (ditulis tim).
Angka memakai format `k/n (persen; interval Wilson 95%)`.

| Wajib | Letak |
|---|---|
| Kerangka test suite | `eval/` (lihat §1) |
| Hasil eksekusi pertama + skor baseline | `eval/final/run1-baseline-gap-v1/` (§2, §3) |
| Bukti eksekusi test suite | `outputs.jsonl` + `manifest.json` run pertama, dan log di `eval/final/checkpoint-1/` (§4) |
| Daftar kelemahan | `eval/ITERATIONS.md` bagian "Baseline checkpoint 1" dan "Deciqo v1" (§5) |

## 1. Kerangka test suite

| Berkas | Isi |
|---|---|
| `eval/final/cases.jsonl` (`cases_dev.py`) | 22 kasus development `c01`–`c22`, label emas, fakta fase after, pola terlarang per kasus |
| `eval/final/cases_holdout.jsonl` (`cases_holdout.py`) | 10 kasus holdout `h01`–`h10`, tidak dipakai run iterasi |
| `eval/validate_cases.py` | Validasi format kasus dan pola terlarang |
| `eval/run_final.py` | Runner B0 / B1 / D / D-rules, fase before-fact dan after-fact, `--budget`, `--rules`, `--rescore`, `--out` |
| `eval/prompts.py` | Prompt baseline B0 dan B1 (hash di manifest) |
| `eval/deciqo_adapter.py` | Memanggil engine Deciqo in-process pada SQLite terpisah per kasus |
| `eval/scoring.py` | Metrik, interval Wilson, `report.md`, lembar label buta |
| `eval/components.py` | Suite komponen deterministik atas `data/eval/` |
| `eval/ulasin_classifier.py` | Baseline historis U (klasifier aspek Ulasin) |
| `tests/` | Unit dan integration test (pytest) |

Sistem: **B0** prompt seller biasa, **B1** prompt hati-hati, **D** engine Deciqo, **D-rules** engine
tanpa AI, **U** klasifier Ulasin. Model `gpt-5-mini`, reasoning effort `low`, bundle input sama.

## 2. Eksekusi pertama

`eval/final/run1-baseline-gap-v1/manifest.json` mencatat setiap run beserta commit dan waktunya
(UTC; WIB = UTC+7):

| Run | Sistem | Keterangan |
|---|---|---|
| `20260926T025532Z` | B0, B1 | 70/70 baris, $0,20, commit `46a16a2` |
| `20260926T030228Z` | D-rules | engine `gap-v1` / `verify-v1` |
| `20260926T030240Z` – `20260926T030811Z` | D (dan D-rules) | engine AI `gap-v1` / `verify-v1` |

Output mentah: `outputs.jsonl` (140 baris: 4 sistem × 22 kasus before-fact + 13 kasus after-fact).
Laporan: `report.md`. Lembar label buta: `labels.csv` (kunci terpisah di `blind_key.json`).

## 3. Skor baseline (before-fact, 22 kasus development)

| Metrik | B0 | B1 | D (AI) | D-rules |
|---|---|---|---|---|
| Output berisi teks listing | 22/22 | 22/22 | 0/22 | 0/22 |
| Unsafe output rate | 12/22 (55%; 35–73) | 3/22 (14%; 5–33) | tidak terdefinisi (0 teks) | tidak terdefinisi |
| Fakta hilang ditahan (D) / ditanyakan (B, proxy) | 5/13 (38%; 18–64) | 12/13 (92%; 67–99) | 8/13 (62%; 36–82) | 4/13 (31%; 13–58) |
| Hold berlebih | 1/3 | 1/3 | 3/3 | 1/3 |
| Temuan emas ditemukan (B: proxy kata atribut) | 21/21 | 21/21 | 15/21 (71%; 50–86) | 7/21 (33%; 17–55) |
| Membership recall (D) | – | – | 20/53 (38%; 26–51) | 15/53 (28%; 18–42) |
| Wrong-item routing (D) | – | – | 0/3 | 1/3 |
| Temuan pada kontrol pujian | 0 | 0 | 0 | 0 |

After-fact: unsafe B0 1/13, B1 1/13, D 1/8, D-rules 1/6; ready after fact D 7/13, D-rules 4/13.
Biaya per baris: B0 $0,0028, B1 $0,0029, D $0,0027. Tabel lengkap dengan interval ada di
`run1-baseline-gap-v1/report.md`.

Baseline U (`eval/final/ulasin_classifier.md`, 120 klausa berlabel manusia): macro F1 IndoBERT
0,579, leksikon 0,581, TF-IDF 0,585. IndoBERT setara dengan leksikon.

Skor otomatis hanya triage (pola terlarang dan proxy kata kunci). Label manusia buta: pending.

## 4. Bukti eksekusi

- Setiap baris `outputs.jsonl` memuat `run_id`, sistem, fase, status, durasi, token, biaya, dan
  output mentah. `manifest.json` memuat commit, prompt dan hash-nya, harga, dan anggaran per run.
- `eval/final/checkpoint-1/rescore.txt`: `report.md` baseline dihitung ulang dari `outputs.jsonl`
  tanpa panggilan model; bagian metriknya identik.
- `eval/final/checkpoint-1/pytest.txt`: hasil `python -m pytest tests -q` pada commit yang tercatat
  di kepala berkas.
- `eval/final/checkpoint-1/validate_cases.txt`: hasil `python eval/validate_cases.py`.

Reproduksi:

```bash
python eval/validate_cases.py
python eval/run_final.py --rules
python eval/run_final.py --rescore
python -m pytest tests -q
```

`--rules` gratis (D-rules). Run berbayar: `python eval/run_final.py --systems B0,B1,D --budget 2`
dengan `OPENAI_API_KEY` di environment.

## 5. Daftar kelemahan

Lengkap dengan output mentah per kasus di `eval/ITERATIONS.md`. Ringkasnya:

Baseline B0/B1:

1. B0 mengarang ukuran saat fakta hilang (c01 "34.5 x 25 cm", c13, c21, c06).
2. B0 mengarang spesifikasi listrik (c05 profil PD, c19 output USB).
3. B0 menutup keluhan kualitas dengan klaim garansi tanpa sumber (c11, c16, c12, c08).
4. Injeksi di ulasan masuk ke teks listing B0 (c15 "Garansi Resmi 5 Tahun").
5. Listing yang dibantah dipakai lagi (c04 B1 "20000 mAh").
6. Angka pembeli menjadi spesifikasi (c18 B0 "2 cup beras").
7. Prompt hati-hati (B1) mengurangi tetapi tidak menghilangkan; teks siap salin tetap ditulis 22/22.

Deciqo v1 (`gap-v1` / `verify-v1`):

1. Triage membuang keluhan sebelum model membacanya (c04, c13 `kept 0 of 4`; c20).
2. Temuan AI dibuang di tahap relevansi (c18).
3. Draf tetap ditahan walau listing sudah menjawab (c02, c07, c14; hold berlebih 3/3).
4. Salah kirim tidak dirutekan (c10, c06; 0/3).
5. Fakta yang benar ditolak gerbang angka (c19).
6. Tabel ukuran dirangkai jadi satu dimensi dan tetap `ready` (c06).
7. Fakta kehilangan atributnya (c21).
8. Recall membership rendah (20/53).
9. Keluhan kualitas satu ulasan terlewat (c16).

Tambahan dari QA engine atas data marketplace (Lazada, Shopee, Tokopedia) dan `data/eval/`:
QA01–QA25 di `docs/worklog/engine.md`. Suite komponen `eval/final/components.md`: keluhan bahasa
Inggris hampir tidak dikenali, keluhan halus di bintang 4–5 lolos, redaksi nama orang dan ukuran
tubuh belum ada, jawaban fakta "oke" diterima (f01 0/10).

Siklus perbaikan sesudah baseline dicatat di `eval/ITERATIONS.md` (Iterasi 1 dan seterusnya).
