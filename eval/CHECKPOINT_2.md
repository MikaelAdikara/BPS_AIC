# Checkpoint 2 — iterasi

Halaman ini memetakan isi wajib checkpoint 2 ke berkasnya. Semua kasus sintetis (ditulis tim).
Angka memakai format `k/n (persen; interval Wilson 95%)`. Model LLM `gpt-5-mini`, reasoning `low`.

| Wajib | Letak |
|---|---|
| Progres Evaluation Track | §1–§4, run di `eval/final/` (folder per versi), gerbang `eval/quality_gate.py` |
| Progres Product Track | §5 (commit `ecf92c7`–`7a4e3c5` setelah tag `checkpoint-1-baseline`) |
| Minimal satu siklus iterasi lengkap: temuan → perbaikan → uji ulang | §3 (tiga siklus v1.12 → v1.15 dengan fresh holdout per siklus) dan `eval/ITERATIONS.md` |
| Bukti eksekusi | `outputs.jsonl` + `manifest.json` + `gate.md` per run; log di `eval/final/checkpoint-2/` |

Engine sekarang `gap-v1.15` / `verify-v2.6`. Checkpoint 1 memakai `gap-v1` / `verify-v1`.

## 1. Ringkasan: dari baseline ke checkpoint 2

D = engine Deciqo dengan AI, fase before-fact, development 22 kasus kecuali disebut lain.

| Metrik D | Checkpoint 1 (`gap-v1`) | Checkpoint 2 (`gap-v1.15`) |
|---|---|---|
| Temuan emas ditemukan | 15/21 (71%; 50–86) | 21/21 (100%; 85–100) |
| Membership recall | 20/53 (38%; 26–51) | 47/53 (89%; 77–95) |
| Membership precision | 20/21 | 47/47 (100%; 92–100) |
| Fakta hilang ditahan | 8/13 (62%; 36–82) | 13/13 (100%; 77–100) |
| Hold berlebih | 3/3 | 2/3 |
| Wrong-item routing | 0/3 | 3/3 |
| Ready after fact | 7/13 | 12/13 (92%; 67–99) |
| Unsafe setelah fakta | 1/8 | 0/12 |
| Temuan pada kontrol pujian | 0 | 0 |

Sumber checkpoint 2: `final/rc-v1.15/report.md` (satu run, 62 kasus, empat sistem). Pada 40 kasus
holdout di run yang sama: temuan 36/36 (90–100), recall 106/125 (85%; 77–90), precision 106/107,
fakta ditahan 24/24, ready 19/24 (79%; 60–91), 0/20 draf terkena pola terlarang. Pembanding prompt
hati-hati B1 pada holdout yang sama: 6/40 teks terkena pola terlarang sebelum fakta, 7/24 sesudah.

**Batas penting:** holdout h01–h30 sudah terekspos saat iterasi, jadi di rc-v1.15 statusnya regresi.
Bukti generalisasi yang paling bersih adalah fresh holdout per siklus di §3, bukan angka gabungan.

## 2. Alat ukur baru sejak checkpoint 1

| Berkas | Isi |
|---|---|
| `eval/quality_gate.json` + `quality_gate.py` | Gerbang PASS/FAIL tiga lapis (integritas, keamanan, akurasi). Lantai akurasi dibandingkan dengan **batas bawah Wilson**, ditetapkan sebelum hasil gap-v1.13 dilihat; tidak boleh diturunkan untuk meloloskan run |
| `eval/make_holdout2.py`, `make_holdout3.py`, `make_holdout4.py` | Holdout baru h11–h22, h23–h30, h31–h40, masing-masing ditulis **sebelum** versi engine yang diuji dijalankan |
| `eval/final/cases_holdout{2,3,4}.lock` | Hash kasus; gerbang gagal bila berkas kasus berubah setelah dikunci |
| `eval/recall_loss.py` | Mengatribusikan kehilangan recall ke discovery, membership, veto juri, atau verifier |
| `eval/scoring.py`, `run_final.py` | Rescore tidak mewariskan label manusia ke output yang berubah; provider failure dicatat sebagai error, bukan sukses tanpa temuan |
| `ml/text/evaluate_aspect_human.py` | Mengukur head/ambang runtime IndoBERT sebenarnya, hash artefak, latency CPU |

Total 62 kasus lolos `validate_cases.py` (22 development, 40 holdout; log di `checkpoint-2/`).

## 3. Siklus iterasi (temuan → perbaikan → uji ulang)

Iterasi 1–3 (gap-v1.6 → gap-v1.9) sudah terdokumentasi di `ITERATIONS.md`. Iterasi 4–5
(reevaluasi dan audit pitch, gap-v1.10 → gap-v1.12) dirangkum di §4. Setelah itu tiga siklus
berikut, masing-masing diuji pada development sebagai regresi **dan** satu holdout baru yang dikunci.

| Siklus | Temuan yang memicu | Perbaikan | Uji ulang | Gerbang |
|---|---|---|---|---|
| gap-v1.12 (diagnosis) | Holdout2 pertama h11–h22: ulasan berisi instruksi (`h17/r3`) terhitung sebagai bukti; recall 26/50; ready 5/8; 1 temuan di kontrol pujian h20 | — (run diagnosis) | `final/holdout2-first-v1.12/` | **FAIL** |
| gap-v1.13 / verify-v2.5 | Kegagalan holdout2 di atas | Ulasan instruksi ("abaikan instruksi", "tulis di listing: …") tidak pernah dihitung sebagai bukti walau kutipannya verbatim; label membership yang disisihkan juri dicatat agar kehilangan recall bisa diatribusikan | Dev `final/dev-regression-v1.13/`; fresh `final/holdout3-fresh-v1.13/` (h23–h30) | Dev **PASS**; holdout3 **FAIL**: precision 21/22 (Wilson bawah 0,78 < 0,85), temuan 7/7 tepat di lantai (n kecil) |
| gap-v1.14 / verify-v2.6 | Holdout3: veto juri leksikon salah membuang keluhan ber-kosakata baru ("4k nya cuma 30hz", "kirain bisa dicas, ternyata…") | Veto juri hanya berlaku bila leksikon membaca kebalikan dengan pasti, bukan saat "tidak yakin"; kelompok atribut yang nilainya bisa diperiksa merchant | Dev `final/dev-regression-v1.14/`; fresh `final/holdout4-fresh-v1.14/` (h31–h40) | Holdout4 **PASS** (pertama kali fresh holdout lolos seluruh gerbang); dev **FAIL**: held 12/13 |
| gap-v1.15 (`second_read.py`) | Menambah kata per kasus = overfitting; model dan leksikon kadang salah ke arah yang sama | **Second read**: panggilan model kedua yang independen membaca ulang setiap bukti yang akan dihitung, tanpa melihat label membership atau bintang, wajib mengutip kata penentu secara verbatim. Hasilnya tetap usulan: dihitung hanya bila kutipan lolos verifier, bukan salah kirim/instruksi | Release candidate `final/rc-v1.15/` (62 kasus); ablation `final/rc-v1.15-ablation-no-second-read/` | rc **FAIL** hanya pada kontrol pujian h20 (lihat §6); semua gerbang akurasi lulus |

Holdout4 fresh (gap-v1.14, 10 kasus): temuan 9/9 (70–100), recall 28/31 (90%; 75–97), precision
28/28, fakta ditahan 6/6, ready 5/6, 0/5 pola terlarang. B1 pada kasus sama: 4/10 terkena pola
terlarang sebelum fakta.

**Ablation second read** (run, kasus, dan versi sama; hanya `DECIQO_SECOND_READ=off`):

| Metrik D, holdout 40 kasus | Dengan second read | Tanpa second read |
|---|---|---|
| Membership recall | 106/125 (85%; 77–90) | 70/125 (56%; 47–64) — **FAIL** |
| Membership precision | 106/107 | 70/70 |
| Fakta ditahan | 24/24 | 21/24 — **FAIL** |
| Routing | 36/36 | 33/35 |
| Ready after fact | 19/24 | 17/24 |
| Biaya D per baris | $0,0053 | $0,0039 |

Second read menaikkan recall 36 bukti dengan harga satu bukti salah dan ~1,4× biaya. Satu run per
kondisi; model nondeterministik, tetapi selisih recall jauh di atas variasi ±3 yang tercatat di
Iterasi 3.

## 4. Iterasi 4–5: reevaluasi dan audit pitch (gap-v1.10 → gap-v1.12)

Rincian klaim pitch: [PITCH_CLAIMS.md](PITCH_CLAIMS.md). Artefak: `final/reevaluation-before/`,
`reevaluation-after/`, `reevaluation-holdout/`, `pitch-gap-v1.11/`, `pitch-gap-v1.12/`,
`pitch-holdout-regression-v1.12/`.

- gap-v1.10 / verify-v2.3: kelompok atribut suhu (c15 kembali menemukan r2/r3), salah kirim
  membandingkan varian eksplisit (XL vs L), routing operasional tidak bergantung pada discovery,
  cache triage menyertakan versi leksikon, status `incomplete_source` sebelum error kutipan.
- gap-v1.11: membership membaca **seluruh** ulasan tersimpan (bukan 150 terakhir) dan teks utuh
  (bukan 600 karakter); harness meneruskan provider failure sebagai error.
- gap-v1.12 / verify-v2.4: konflik label discovery vs membership diselesaikan hanya bila semua
  span verbatim mendapat verdict tegas yang sama; kelompok kapasitas.
- Klasifier U: runtime `indobert-nlp01@thr0.3+asp-v2` macro F1 0,585 vs leksikon 0,581 (n=120).
  Tidak ada keunggulan berarti; tidak ada retraining (tidak ada split validasi baru).

Holdout pertama (h01–h10) yang semula fresh: temuan 8/9, recall 11/20, ready 4/6. Setelah
dipakai audit, statusnya regresi.

## 5. Product Track sejak checkpoint 1

| Commit | Perubahan |
|---|---|
| `ecf92c7`, `2c53f04`, `6d31d8d`, `3b696e8`, `bfb21ff` | Reservasi biaya terlihat di anggaran fetch; tinjauan listing dan ketahanan workspace; teks editor dipisah dari spesifikasi sumber; ukuran pribadi ditutup; kontrak API tinjauan diselaraskan |
| `2dd0e53`, `0bc20d7`, `1295e16` | UI landing dan dashboard baru; peta isu, tren per kanal, sebaran bintang di Overview; strip urgensi di layar Isu |
| `2220f91`, `67b5cff`, `7a4e3c5` | Paket Tokopedia PRDECT-ID, jumlah terjual, produk sintetis kedua; "pembeli terdampak" sebagai batas bawah (proyeksi hanya untuk sampel lengkap); papan kanal dan kartu paket dengan sampling dan unit terjual |
| `379b2de`, `5436525` | `start.bat` sekali klik / `stop.bat`; proyek video demo |
| Commit checkpoint ini | Engine gap-v1.15 / verify-v2.6 (second read, ulasan instruksi, veto juri, membership penuh), alat eval baru, run v1.12–v1.15 |

## 6. Yang belum berhasil

1. **Kontrol pujian h20** (keyboard): "ga ada cacat sama sekali, cuma saya kurang suka rgb nya
   terlalu terang" menjadi temuan `missing_fact` kontrol kecerahan RGB, konsisten dari v1.12 hingga
   v1.15. Bisa dibaca sebagai preferensi, bukan cacat; label emas kasus ini tidak diubah demi lolos
   gerbang. Keputusan label perlu penilai manusia.
2. **Hold berlebih** 2/3 di development dan 2/4 di holdout: listing sudah menjawab, draf tetap
   meminta fakta (c14 masih tertahan). Pemetaan atribut/nilai/satuan listing belum cukup tegas.
3. **Ready after fact** 19/24 di holdout: sebagian karena kasus tanpa listing (`needs_listing`
   sesuai aturan produk), sebagian karena model membagi satu atribut menjadi dua isu sehingga fakta
   hanya diterapkan ke satu (h06 panjang vs lebar).
4. **Dev-regression-v1.14 gagal** pada held 12/13; rc-v1.15 kembali 13/13, tetapi satu run.
   Stabilitas antar-run belum diukur untuk v1.15 (belum ada replikasi).
5. **Penulis holdout = penulis perbaikan engine.** Holdout dikunci sebelum run, tetapi tetap bias
   penulis. Label manusia buta untuk output engine (`labels.csv`) masih pending; skor otomatis
   hanya pola terlarang dan matcher isu emas, tidak menilai seluruh section draf.
6. **Klasifier neural** tidak lebih baik dari leksikon; TF-IDF tidak dapat direproduksi
   (`data/processed/clauses_train.csv` tidak ada). Ukuran/varian F1 0,231.
7. **Runtime**: container localhost belum di-rebuild ke gap-v1.15; demo browser belum
   di-rehearsal pada build baru. Engine D di harness memakai triage leksikon, bukan neural.
8. Validasi merchant, WTP, dampak bisnis, dan angka historis deck (lihat PITCH_CLAIMS) tidak dapat
   digantikan tes sintetis.

## 7. Rencana menuju checkpoint 3 (model freeze, 18.00)

1. **Freeze kandidat gap-v1.15** kecuali ada regresi keamanan. Jalankan satu replikasi rc-v1.15
   untuk mengukur variasi antar-run sebelum membekukan angka.
2. Tulis **holdout5 fresh** (dikunci sebelum run) dan jalankan sekali pada versi beku; itu angka
   yang dipakai di Evaluation Artifact, bukan run terbaik.
3. Putuskan h20 lewat penilai manusia; bila tetap "pujian murni", perbaiki di jalur preferensi vs
   cacat tanpa menambah kata per kasus.
4. Hold berlebih: petakan atribut/lokasi/nilai/satuan listing sebelum menyatakan pertanyaan terjawab.
5. Isi `labels.csv` oleh dua penilai buta pada sampel output rc-v1.15; laporkan kappa.
6. Rebuild container, cek `/api/v1/version` = gap-v1.15 / verify-v2.6, rehearsal demo penuh
   (save fakta → draf → applied → reopen).
7. Mulai Evaluation Artifact dan pitch deck dengan redaksi dari PITCH_CLAIMS.md.

## 8. Bukti eksekusi dan reproduksi

- `eval/final/checkpoint-2/pytest.txt`: 706 tes backend/integrasi lulus.
- `eval/final/checkpoint-2/web.txt`: 29 tes web lulus, typecheck lulus.
- `eval/final/checkpoint-2/validate_cases.txt`: 62 kasus valid.
- Setiap folder run memuat `manifest.json` (commit, dirty files, versi engine, prompt + hash, harga,
  anggaran), `outputs.jsonl` (output mentah, trace, usage), `report.md`, `gate.md`, `labels.csv`.
  Manifest run v1.12–v1.15 mencatat commit dasar + working tree kotor; commit checkpoint ini
  membekukan kode yang menghasilkan run tersebut.
- Biaya API delapan run v1.12–v1.15: $2,4533 menurut ledger runner (rc-v1.15 sendiri $1,0973).

```powershell
.venv/Scripts/python.exe -m pytest tests -q
npm --prefix apps/web test
.venv/Scripts/python.exe eval/validate_cases.py
.venv/Scripts/python.exe eval/run_final.py --holdout --systems B0,B1,D,D-rules --budget 2 --out eval/final/rc-replication
.venv/Scripts/python.exe eval/quality_gate.py eval/final/rc-replication
$env:DECIQO_SECOND_READ = 'off'; .venv/Scripts/python.exe eval/run_final.py --holdout --systems D --budget 1 --out eval/final/ablation
```
