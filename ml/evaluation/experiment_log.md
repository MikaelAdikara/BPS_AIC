# Experiment Log

Blueprint bagian 31.1: pencatatan eksperimen cukup berupa file markdown/CSV — tidak perlu
tools eksperimen tracking kompleks untuk skala tim ini.

**Aturan:** satu baris per run. Angka yang masuk ke MODEL_CARD.md, proposal, atau video WAJIB
dapat ditelusuri balik ke salah satu baris di sini beserta script yang menghasilkannya
(blueprint bagian 40).

| # | Tanggal | Fase | Komponen | Script | Konfigurasi | Metrik | Hasil | Catatan |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E01 | 2026-08-05 | 1 | Dataset build | `ml/text/build_dataset.py` | seed=42, split produk 70/15/15 | jumlah klausa, leakage | 39.986 ulasan → 96.300 klausa; train 69.800 / val 15.308 / test 11.192; leakage produk & review_id = 0 | Label SILVER dari labeling function (ADR-015) |
| E02 | 2026-08-05 | 1 | Baseline sentimen | `ml/text/baseline.py` | TF-IDF char_wb 3–5, LogReg balanced, seed=42 | macro F1 | silver_test **0,563**; unseen **0,561**; stress challange **0,720** | netral F1 hanya 0,113 pada silver (support 256) — label silver netral bermasalah |
| E03 | 2026-08-05 | 1 | Baseline aspek | `ml/text/baseline.py` | TF-IDF char_wb 3–5, OvR LogReg balanced, seed=42 | macro F1 multi-label | silver_test **0,938**; unseen **0,923** | **Angka ini sirkular** — mengukur kecocokan terhadap labeling function, bukan akurasi |
| E04 | 2026-08-05 | 2 | Fine-tune IndoBERT | `ml/text/finetune.py` | 3 epoch, batch 32, lr 2e-5, max_len 32, seed=42, GTX 1650, 112,8 mnt | macro F1 | aspek silver **0,985**; sentimen silver **0,628**; stress **0,730** | Gate Fase 2 **GO**. Kenaikan pada label independen hanya +0,010 — lihat catatan di bawah |
| E05 | 2026-08-06 | 2 | Evaluasi GOLD | `ml/text/evaluate_gold.py` | gold 500 klausa (ADR-017) | macro F1 | leksikon aspek **0,734** sent **0,599** · TF-IDF **0,744**/**0,676** · IndoBERT **0,733**/**0,668** | **Gate Fase 2 DIREVISI** — pada aspek fine-tuning tidak menambah apa pun |
| E06 | 2026-08-06 | 2 | Latih ulang label diperbaiki | `ml/text/finetune.py` | 2 epoch, batch 32, seed 42 | macro F1 | NusaX-ind **0,730** (dari 0,519); netral **0,645** (dari 0,021); gold aspek 0,766; PRDECT biner 0,851 (dari 0,952) | Gate sentimen **LULUS**, aspek **TIDAK LULUS** — lihat MODEL_CARD §4 |

## Catatan E02 — rincian stress test per fenomena

Diukur pada `challange.json` (label independen dari labeling function kita, tetapi provenance
datasetnya sendiri tidak terdokumentasi — lihat ADR-016). Macro F1, terendah dulu:

| Fenomena | macro F1 |
| --- | --- |
| mixed_sentiment | 0,113 |
| negation | 0,163 |
| sarcasm | 0,198 |
| ambiguous | 0,237 |
| question_conditional | 0,459 |
| aspect_based | 0,552 |
| contextual | 0,608 |
| comparative | 0,656 |
| typos_informal | 0,736 |
| short_vague | 0,778 |
| colloquial_slang | 0,789 |
| emotional_exaggeration | 0,825 |

Pola ini konsisten dengan argumen dossier bagian 13.1: pendekatan berbasis kecocokan permukaan
menangani typo dan slang dengan baik (0,74–0,79) namun runtuh pada fenomena komposisional —
negasi, sarkasme, dan sentimen campuran (0,11–0,20). Inilah tepatnya celah yang harus ditutup
model kontekstual pada Fase 2, dan menjadi pembanding yang bermakna untuk bagian 34 baseline #3.

## Catatan E05 — angka yang berlaku, dan pembalikan verdict

Diukur pada gold, kesimpulan Fase 2 yang semula GO tidak bertahan.

**Aspek — tujuh dari sebelas kelas identik sampai tiga desimal antara leksikon dan IndoBERT**
(kualitas_produk 0,427/0,425 · kesesuaian_deskripsi 0,773/0,773 · harga_value 0,914/0,914 ·
ukuran_varian 0,817/0,817 · kemasan 0,907/0,907 · pengiriman 0,718/0,718 · keaslian 0,969/0,969).
Model mereproduksi aturan leksikon, tidak memindahkan satu pun keputusan. Risiko sirkularitas
ADR-015 terwujud hampir sepenuhnya.

Selisih 0,011 antara TF-IDF dan IndoBERT ada dalam rentang derau untuk n=500 — tidak boleh
dilaporkan sebagai satu mengalahkan yang lain.

**Sentimen — fine-tuning benar-benar bekerja, kecuali netral:**

| Kelas | Leksikon | TF-IDF | IndoBERT | n |
| --- | --- | --- | --- | --- |
| negatif | 0,555 | 0,733 | **0,805** | 108 |
| positif | 0,810 | 0,891 | **0,917** | 322 |
| netral | 0,433 | 0,403 | **0,282** | 70 |

Unggul telak pada dua kelas terbesar, runtuh pada netral — dan kelas ketiga itu yang menyeret
macro F1-nya ke bawah TF-IDF.

Dua akar masalah ada di **label**, bukan di model: label aspek 100% keluaran leksikon sehingga
model tidak mungkin melampauinya, dan aturan `review_prior` merusak kelas netral.

## Catatan E04 — apa yang sebenarnya berubah

Rata-rata stress naik tipis (+0,010), tetapi menyembunyikan dua arah yang berlawanan:

| Fenomena | Baseline | Fine-tuned | Selisih |
| --- | --- | --- | --- |
| negation | 0,163 | 0,559 | **+0,397** |
| mixed_sentiment | 0,113 | 0,311 | **+0,198** |
| emotional_exaggeration | 0,825 | 0,987 | +0,162 |
| typos_informal | 0,736 | 0,805 | +0,069 |
| sarcasm | 0,198 | 0,179 | **−0,018** |
| ambiguous | 0,236 | 0,199 | **−0,037** |
| question_conditional | 0,459 | 0,358 | **−0,101** |

Fine-tuning menutup celah **negasi** secara meyakinkan — fenomena yang memang diargumentasikan
tidak tertangani pendekatan permukaan. Sarkasme **tidak membaik**, dan itu konsisten: labeling
function berbasis leksikon secara desain melabeli kalimat sarkastik dengan salah, sehingga model
mewarisi kesalahan itu.

## Catatan E04 — stratifikasi menurut asal label

| Asal label | Macro F1 |
| --- | --- |
| `clause_polarity` | **0,993** |
| `review_prior` | **0,564** |

Jurang 0,43 pada model dan distribusi yang sama, dibedakan hanya oleh asal label, adalah bukti
bahwa aturan `review_prior` menghasilkan label yang tidak dapat dipelajari. Revisi aturan
ditunda sampai gold test set tersedia sebagai penengah yang sah.

## Yang belum diukur

- Ambang kelas negatif — model kurang berani menyebut negatif (91 keluhan diprediksi netral pada PRDECT). Penyetelan ditunda ke Fase 8.
- Model visual (Fase 3) — menunggu foto validasi.
