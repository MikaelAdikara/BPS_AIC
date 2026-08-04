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
| Text fallback | TF-IDF + Logistic Regression | belum dilatih |
| Visual Intelligence (VIS-01) | CLIP ViT-B/32 zero-shot, frozen | belum dievaluasi |
| Embedding (RET-01) | BGE-M3 | belum diintegrasikan |
| Orchestrator | SEA-LION quantized | belum diintegrasikan |

## 2. Data training
_Diisi dari hasil Fase 1 — lihat [DATASET_CARD.md](DATASET_CARD.md)._

## 3. Metrik evaluasi — model teks (bagian 33.1)
_Macro F1 aspek, per-class F1, sentiment F1, confusion matrix, performa subset slang/typo,
performa per kategori produk. Belum diukur._

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
