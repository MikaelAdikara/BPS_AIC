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

## Yang belum diukur

- **Gold test set berlabel manusia** — berkas anotasi sudah disiapkan
  (`data/annotation/gold_annotation_task.csv`, 500 klausa) tetapi belum dilabeli. Sampai selesai,
  belum ada satu pun angka NLP-01 yang layak masuk proposal.
- Presisi/recall labeling function terhadap gold — dihitung setelah anotasi selesai.
- Fine-tuning IndoBERT (Fase 2).
