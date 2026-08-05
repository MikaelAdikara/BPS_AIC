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

### 3.2 Model fine-tuned IndoBERT (Fase 2, sudah dijalankan)

Script: `ml/text/finetune.py` · seed 42 · 3 epoch · batch 32 · lr 2e-5 · AdamW + OneCycleLR ·
112,8 menit pada GTX 1650 · checkpoint terpilih dari epoch 3 berdasar validation F1 (bukan
training loss) · ambang aspek 0,70 disetel dari validation set.

Arsitektur: satu encoder IndoBERT-base dengan dua head terpisah (aspek multi-label 11 kelas,
sentimen 3 kelas), mean pooling atas token non-padding.

#### Perbandingan terhadap baseline

| Metrik | Baseline TF-IDF | Fine-tuned IndoBERT | Selisih |
| --- | --- | --- | --- |
| Aspek — macro F1 (silver) | 0,938 | **0,985** | +0,047 |
| Aspek — macro F1 (silver unseen) | 0,923 | **0,981** | +0,058 |
| Sentimen — macro F1 (silver) | 0,563 | **0,628** | +0,065 |
| Sentimen — macro F1 (stress) | 0,720 | **0,730** | +0,010 |

**Gate Fase 2 terlampaui** (kriteria: macro F1 > baseline). Tetapi angka-angka di atas tidak
boleh dibaca begitu saja — tiga catatan berikut menentukan artinya.

#### Catatan 1 — angka aspek tetap sirkular

Kenaikan 0,938 → 0,985 **bukan bukti akurasi 98%**. Kedua model sedang memulihkan aturan
leksikon yang membuat labelnya; IndoBERT hanya memulihkannya lebih baik. Ini persis risiko yang
dicatat pada ADR-015. Angka aspek yang bermakna baru ada setelah gold test set selesai dilabeli.

#### Catatan 2 — kenaikan pada label independen sangat tipis

Pada stress set yang labelnya tidak berasal dari labeling function kita, kenaikannya hanya
**+0,010** — di dalam rentang derau. Rata-rata itu menyembunyikan pergerakan besar ke dua arah:

| Fenomena | Baseline | Fine-tuned | Selisih |
| --- | --- | --- | --- |
| negation | 0,163 | 0,559 | **+0,397** |
| mixed_sentiment | 0,113 | 0,311 | **+0,198** |
| emotional_exaggeration | 0,825 | 0,987 | +0,162 |
| typos_informal | 0,736 | 0,805 | +0,069 |
| short_vague | 0,778 | 0,825 | +0,048 |
| colloquial_slang | 0,789 | 0,827 | +0,038 |
| comparative | 0,656 | 0,686 | +0,031 |
| aspect_based | 0,552 | 0,571 | +0,019 |
| contextual | 0,608 | 0,589 | −0,019 |
| sarcasm | 0,198 | 0,179 | **−0,018** |
| ambiguous | 0,236 | 0,199 | **−0,037** |
| question_conditional | 0,459 | 0,358 | **−0,101** |

Pembacaan jujurnya: fine-tuning **benar-benar menutup celah negasi** — kenaikan +0,397 pada
fenomena yang secara khusus diargumentasikan tidak dapat ditangani pendekatan permukaan.
Sentimen campuran juga membaik besar meski levelnya masih rendah.

Sebaliknya, **sarkasme tidak membaik sama sekali** (0,198 → 0,179), dan `ambiguous` serta
`question_conditional` justru turun. Ini masuk akal dan tidak disembunyikan: data latih kami
tidak memuat label sarkasme, dan labeling function berbasis leksikon secara desain memberi label
yang SALAH pada kalimat sarkastik ("mantap banget nih ditipu" akan dinilai positif). Model
belajar dari label itu, jadi wajar ia mewarisi kelemahannya.

**Klaim yang boleh dibuat dari data ini:** fine-tuning memberi perbaikan besar dan terukur pada
negasi dan sentimen campuran. **Klaim yang TIDAK boleh dibuat:** bahwa sistem menangani sarkasme,
atau bahwa fine-tuning unggul menyeluruh pada bahasa informal.

#### Catatan 3 — bukti bahwa aturan label sentimen bermasalah

Metrik sentimen distratifikasi menurut asal labelnya:

| Asal label | Macro F1 | Artinya |
| --- | --- | --- |
| `clause_polarity` (klausa punya sinyal polaritas) | **0,993** | Model memulihkan aturan LF nyaris sempurna |
| `review_prior` (klausa tanpa sinyal, mewarisi sentimen ulasan) | **0,564** | Model tidak dapat mempelajarinya |

Jurang 0,43 pada model, distribusi, dan arsitektur yang sama — dibedakan **hanya oleh asal
label** — adalah bukti kuat bahwa aturan `review_prior` menghasilkan label yang tidak dapat
dipelajari, karena memang tidak berkorespondensi dengan isi klausanya. Klausa tanpa muatan
penilaian ("paket sudah diterima") diberi sentimen keseluruhan ulasan secara sewenang-wenang.

Ini menguatkan dugaan Fase 1 yang saat itu belum punya bukti sah. Kelas `netral` tetap rusak
(F1 0,136). **Revisi aturan sentimen ditunda sampai gold test set tersedia** — gold adalah
penengah yang sah, dan retraining sebelum itu berarti menebak dua kali.

#### Aspek per kelas (silver, terendah)

`kelengkapan` 0,926 (support 46) · `ukuran_varian` 0,980 · `kemudahan_penggunaan` 0,983 ·
`rasa_kualitas_makanan` 0,984. Aspek bersupport kecil tetap paling rapuh — konsisten dengan
keterbatasan cakupan kategori pada DATASET_CARD §5.

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
