# Model Card

> **Placeholder (Fase 0).** Diisi pada Fase 2 (model teks), Fase 3 (model visual), dan Fase 8
> (evaluasi penuh), sesuai blueprint bagian 26.1 langkah 19 dan bagian 33.
>
> **Aturan pengisian:** setiap angka di dokumen ini WAJIB berasal dari script/notebook evaluasi
> yang benar-benar dijalankan dan dapat ditelusuri balik (blueprint bagian 40). Tidak ada target,
> asumsi, atau angka dari literatur yang ditulis seolah hasil pengukuran tim.

## 1. Ringkasan model

| Komponen | Model | Status |
| --- | --- | --- |
| Text Intelligence (NLP-01) | IndoBERT-base, fine-tuned | belum dilatih |
| Text fallback | TF-IDF + Logistic Regression | **terlatih (baseline Fase 1)** |
| Visual Intelligence (VIS-01) | CLIP ViT-B/32 zero-shot, frozen | belum dievaluasi |
| Embedding (RET-01) | BGE-M3 | belum diintegrasikan |
| Orchestrator | SEA-LION quantized | belum diintegrasikan |

## 2. Data training
_Diisi dari hasil Fase 1 — lihat [DATASET_CARD.md](DATASET_CARD.md)._

## 3. Metrik evaluasi — model teks (bagian 33.1)

### 3.1 Baseline TF-IDF + Logistic Regression (Fase 1, sudah dijalankan)

Script: `ml/text/baseline.py` · seed 42 · hasil mentah: `ml/evaluation/baseline_results.json`
· log: `ml/evaluation/experiment_log.md` E02–E03.

**Cara membaca angka di bawah — penting.** Label aspek dan sebagian label sentimen dihasilkan
labeling function (ADR-015), bukan manusia. Karena itu:

| Kolom | Artinya |
| --- | --- |
| `silver_test` | Kecocokan model terhadap **labeling function**, BUKAN akurasi sebenarnya |
| `silver_test_unseen` | Sama, tetapi hanya pada klausa yang teksnya tak pernah muncul di train |
| `stress_challange` | Sentimen pada `challange.json` — label **independen** dari LF kita |

| Task | silver_test | silver_test_unseen | stress_challange |
| --- | --- | --- | --- |
| Sentimen (macro F1, 3 kelas) | 0,563 | 0,561 | **0,720** |
| Aspek (macro F1, multi-label 11 kelas) | 0,938 | 0,923 | tidak berlaku (tanpa label aspek) |

**Angka aspek 0,938 TIDAK boleh dibaca sebagai akurasi 94%.** Model TF-IDF hanya berhasil
memulihkan aturan leksikon yang membuat labelnya — ini persis risiko sirkularitas yang dicatat
pada ADR-015. Angka aspek yang bermakna baru ada setelah gold test set selesai dilabeli.

**Temuan sentimen:** kelas `netral` runtuh pada label silver (F1 0,113, support 256) namun jauh
lebih baik pada label independen (F1 0,609, support 1.223). Diagnosisnya: aturan silver untuk
netral terlalu jarang memicu, bukan modelnya yang gagal. Perlu diperbaiki sebelum Fase 2.

**Kelemahan baseline per fenomena bahasa** (stress test, macro F1): mixed_sentiment 0,113 ·
negation 0,163 · sarcasm 0,198 · ambiguous 0,237, berbanding typos_informal 0,736 ·
short_vague 0,778 · colloquial_slang 0,789. Baseline menangani variasi permukaan dengan baik
tetapi runtuh pada fenomena komposisional — inilah celah yang harus dibuktikan tertutup oleh
IndoBERT pada Fase 2 (bagian 34 baseline #3).

Catatan kejujuran: `challange.json` labelnya independen dari labeling function kita, tetapi
provenance datasetnya sendiri tidak terdokumentasi di sumbernya (ADR-016). Ia dipakai sebagai
**diagnostik**, bukan sebagai ground truth kompetisi.

### 3.2 Model fine-tuned IndoBERT
_Belum dilatih (Fase 2)._

### 3.3 Evaluasi pada gold test set berlabel manusia
_Belum tersedia. Ini akan menjadi satu-satunya angka NLP-01 yang layak dikutip di proposal._

## 4. Metrik evaluasi — model visual (bagian 33.2)
_Accuracy pada kasus tidak abstain, macro F1, coverage, abstention rate, selective accuracy,
performa per kualitas foto. Belum diukur. **Tidak ada target minimum yang diklaim di muka.**_

## 5. Perbandingan baseline (bagian 34)
_Delapan baseline. Belum dijalankan._

## 6. Go/No-Go gate model visual (bagian 19.3, 26.2)
_Keputusan GO / CONDITIONAL GO / NO-GO diambil di akhir Fase 3 berbasis selective accuracy dan
coverage aktual. **Belum diambil.**_

## 7. Batas kemampuan dan bias yang diketahui
_Diisi setelah error analysis (bagian 26.1 langkah 15). Lihat juga [LIMITATIONS.md](LIMITATIONS.md)._

## 8. Reproducibility
_Seed, hyperparameter, versi model, dan perintah reproduksi dicatat di sini setelah training._
