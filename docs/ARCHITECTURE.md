# Architecture

> **Placeholder (Fase 0).** Diisi pada Fase 10, dirangkum dari blueprint bagian 16 (C4 diagrams)
> dan 46 (ADR). Sumber kebenaran: [INSIGHTULASAN_BLUEPRINT.md](reference/INSIGHTULASAN_BLUEPRINT.md).

## 1. System Context (C4 Level 1)
_Diisi dari blueprint bagian 15._

## 2. Container Diagram (C4 Level 2)
_Diisi dari blueprint bagian 16.1._

## 3. Component Diagram — Backend API (C4 Level 3)
_Diisi dari blueprint bagian 16.2._

## 4. Deployment Diagram
_Diisi dari blueprint bagian 16.3._

## 5. Data Flow & Lineage
_Diisi dari blueprint bagian 16.4–16.5._

## 6. AI Tool Orchestration
_Diisi dari blueprint bagian 16.6 dan 27.3 (10 tool contracts)._

## 7. Architecture Decision Records (ringkasan)
_Empat belas ADR pada blueprint bagian 46 dirangkum di sini, dengan status implementasi aktual._

| ADR | Keputusan | Status implementasi |
| --- | --- | --- |
| ADR-001 | Local-first, bukan commercial API | belum diimplementasikan |
| ADR-002 | IndoBERT-base sebagai model teks primary | belum diimplementasikan |
| ADR-003 | CLIP ViT-B/32 sebagai vision model primary | belum diimplementasikan |
| ADR-004 | Frozen zero-shot visual, bukan trained classifier | belum diimplementasikan |
| ADR-005 | BGE-M3 sebagai embedding primary | belum diimplementasikan |
| ADR-006 | SEA-LION quantized sebagai orchestrator | belum diimplementasikan |
| ADR-007 | Chroma embedded sebagai vector store | belum diimplementasikan |
| ADR-008 | FastAPI, satu service, service layer modular | belum diimplementasikan |
| ADR-009 | React + Vite untuk competition MVP | belum diimplementasikan |
| ADR-010 | Temporary storage session-only, tanpa DB persisten | belum diimplementasikan |
| ADR-011 | Skor deterministic, LLM hanya menyusun narasi | belum diimplementasikan |
| ADR-012 | Benchmark precomputed aggregate | belum diimplementasikan |
| ADR-013 | Tidak ada eksekusi tindakan bisnis otomatis | belum diimplementasikan |
| ADR-014 | FALLBACK MODE deterministic template wajib | belum diimplementasikan |

## 8. ADR tambahan (pasca-blueprint)

ADR berikut TIDAK ada di blueprint bagian 46 — dibuat saat implementasi ketika kenyataan data
berbeda dari asumsi blueprint. Disetujui eksplisit sebelum dieksekusi.

### ADR-015 — Label aspek lewat weak supervision, bukan pemetaan label emosi/kategori

| Aspek | Keterangan |
| --- | --- |
| Context | Blueprint bagian 26.1 langkah 4 merencanakan pemetaan label emosi/kategori asli ke 11 aspek. Setelah dataset diunduh dan diperiksa (Fase 1), pemetaan ini terbukti tidak dapat dijalankan: `Emotion` PRDECT-ID adalah dimensi emosi (Happy/Sadness/Fear/Love/Anger) yang tidak berkorespondensi dengan aspek, dan `Category` adalah kategori produk — input untuk memilih aspek aktif, bukan label aspek. Tidak ada dataset ABSA Bahasa Indonesia publik di domain e-commerce yang sepadan (CASA = mobil, HoASA = hotel). |
| Decision | Label aspek dihasilkan **weak supervision**: labeling function berbasis leksikon menghasilkan label silver pada ulasan nyata untuk training, dan tim melabeli manual sampel bertingkat sebagai **gold test set** untuk evaluasi. |
| Alternatives | Anotasi manual penuh (volume tidak memadai dalam sisa waktu); pelabelan dibantu LLM lokal (inferensi CPU terlalu lambat untuk puluhan ribu baris, kualitas belum teruji); aspek berbasis rule tanpa model terlatih (bertentangan dengan dossier bagian 13.1 yang berargumen keyword tidak memadai). |
| Rationale | Evaluasi tetap jujur karena diukur pada data berlabel manusia, bukan pada output labeling function itu sendiri. Sekaligus menghasilkan perbandingan yang memang diwajibkan bagian 34: fine-tuned model vs keyword rule-based baseline, diukur pada gold. |
| Consequences & Risk | Ada risiko nyata model hanya menghafal keyword sehingga F1-nya setara baseline rule-based. Ini pertanyaan empiris yang dijawab pada Fase 2 dan **dilaporkan apa adanya** di MODEL_CARD.md, bukan disembunyikan. Konsekuensi kedua: seluruh metrik yang diukur pada split silver TIDAK boleh disebut akurasi sebenarnya — hanya kecocokan terhadap labeling function. |
| Revisit condition | Jika gold test set menunjukkan labeling function punya presisi rendah pada aspek tertentu, LF aspek itu direvisi dan silver label dibuat ulang sebelum fine-tuning final. |

### ADR-016 — Peran dataset e-commerce-sentiment: stress test, bukan data latih

| Aspek | Keterangan |
| --- | --- |
| Context | `simple.json` (17.000 baris) ternyata hanya memuat 2.193 komentar unik (87% duplikasi), berdistribusi kelas persis seimbang, tanpa keterangan sumber maupun metodologi anotasi pada dataset card. |
| Decision | `simple.json` **tidak dipakai**. `challange.json` (4.840 baris, seluruhnya unik, ditandai per fenomena linguistik) dipakai sebagai **stress/diagnostic test set**, bukan data latih. |
| Alternatives | Dedupe `simple.json` lalu ikut dilatih (provenance tetap tidak jelas, distribusi tetap tidak alami); membuang seluruh dataset (kehilangan test set sarkasme/slang yang sulit dibuat ulang). |
| Rationale | Melatih pada data dengan duplikasi 87% menyebabkan kebocoran duplikat lintas split dan mengajarkan distribusi buatan. Sebaliknya, penandaan fenomena pada `challange.json` persis memenuhi kebutuhan bagian 33.1: "performa slang/typo diuji terpisah pada subset ulasan sangat informal". |
| Consequences & Risk | Volume data latih berkurang dari rencana awal, dikompensasi Tokopedia 2019 (40.607 ulasan nyata). Hasil pada stress test kemungkinan jauh lebih rendah dari test set utama — itu memang tujuannya, dan dilaporkan terpisah. |
| Revisit condition | Tidak direncanakan berubah. |
