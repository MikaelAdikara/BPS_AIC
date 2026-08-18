# Architecture

> **Placeholder (Fase 0).** Diisi pada Fase 10, dirangkum dari blueprint bagian 16 (C4 diagrams)
> dan 46 (ADR). Sumber kebenaran: [INSIGHTULASAN_BLUEPRINT.md](reference/INSIGHTULASAN_BLUEPRINT.md).

## 1. System Context (C4 Level 1)
_Diisi dari blueprint bagian 15._

## 2. Container Diagram (C4 Level 2)
_Diisi dari blueprint bagian 16.1._

## 3. Component Diagram - Backend API (C4 Level 3)
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

ADR berikut TIDAK ada di blueprint bagian 46 - dibuat saat implementasi ketika kenyataan data
berbeda dari asumsi blueprint. Disetujui eksplisit sebelum dieksekusi.

### ADR-015 - Label aspek lewat weak supervision, bukan pemetaan label emosi/kategori

| Aspek | Keterangan |
| --- | --- |
| Context | Blueprint bagian 26.1 langkah 4 merencanakan pemetaan label emosi/kategori asli ke 11 aspek. Setelah dataset diunduh dan diperiksa (Fase 1), pemetaan ini terbukti tidak dapat dijalankan: `Emotion` PRDECT-ID adalah dimensi emosi (Happy/Sadness/Fear/Love/Anger) yang tidak berkorespondensi dengan aspek, dan `Category` adalah kategori produk - input untuk memilih aspek aktif, bukan label aspek. Tidak ada dataset ABSA Bahasa Indonesia publik di domain e-commerce yang sepadan (CASA = mobil, HoASA = hotel). |
| Decision | Label aspek dihasilkan **weak supervision**: labeling function berbasis leksikon menghasilkan label silver pada ulasan nyata untuk training, dan tim melabeli manual sampel bertingkat sebagai **gold test set** untuk evaluasi. |
| Alternatives | Anotasi manual penuh (volume tidak memadai dalam sisa waktu); pelabelan dibantu LLM lokal (inferensi CPU terlalu lambat untuk puluhan ribu baris, kualitas belum teruji); aspek berbasis rule tanpa model terlatih (bertentangan dengan dossier bagian 13.1 yang berargumen keyword tidak memadai). |
| Rationale | Evaluasi tetap jujur karena diukur pada data berlabel manusia, bukan pada output labeling function itu sendiri. Sekaligus menghasilkan perbandingan yang memang diwajibkan bagian 34: fine-tuned model vs keyword rule-based baseline, diukur pada gold. |
| Consequences & Risk | Ada risiko nyata model hanya menghafal keyword sehingga F1-nya setara baseline rule-based. Ini pertanyaan empiris yang dijawab pada Fase 2 dan **dilaporkan apa adanya** di MODEL_CARD.md, bukan disembunyikan. Konsekuensi kedua: seluruh metrik yang diukur pada split silver TIDAK boleh disebut akurasi sebenarnya - hanya kecocokan terhadap labeling function. |
| Revisit condition | Jika gold test set menunjukkan labeling function punya presisi rendah pada aspek tertentu, LF aspek itu direvisi dan silver label dibuat ulang sebelum fine-tuning final. |

### ADR-016 - Peran dataset e-commerce-sentiment: stress test, bukan data latih

| Aspek | Keterangan |
| --- | --- |
| Context | `simple.json` (17.000 baris) ternyata hanya memuat 2.193 komentar unik (87% duplikasi), berdistribusi kelas persis seimbang, tanpa keterangan sumber maupun metodologi anotasi pada dataset card. |
| Decision | `simple.json` **tidak dipakai**. `challange.json` (4.840 baris, seluruhnya unik, ditandai per fenomena linguistik) dipakai sebagai **stress/diagnostic test set**, bukan data latih. |
| Alternatives | Dedupe `simple.json` lalu ikut dilatih (provenance tetap tidak jelas, distribusi tetap tidak alami); membuang seluruh dataset (kehilangan test set sarkasme/slang yang sulit dibuat ulang). |
| Rationale | Melatih pada data dengan duplikasi 87% menyebabkan kebocoran duplikat lintas split dan mengajarkan distribusi buatan. Sebaliknya, penandaan fenomena pada `challange.json` persis memenuhi kebutuhan bagian 33.1: "performa slang/typo diuji terpisah pada subset ulasan sangat informal". |
| Consequences & Risk | Volume data latih berkurang dari rencana awal, dikompensasi Tokopedia 2019 (40.607 ulasan nyata). Hasil pada stress test kemungkinan jauh lebih rendah dari test set utama - itu memang tujuannya, dan dilaporkan terpisah. |
| Revisit condition | Tidak direncanakan berubah. |

### ADR-017 - Gold test set lewat pra-anotasi LLM + adjudikasi manusia

| Aspek | Keterangan |
| --- | --- |
| Context | ADR-015 mensyaratkan gold test set berlabel manusia sebagai satu-satunya penengah yang sah. Melabeli 500 klausa dari nol memakan ~3–4 jam waktu tim, dan itu menjadi penghambat tunggal bagi seluruh angka NLP-01. |
| Decision | Tiga tahap: (1) labeling function menghasilkan label silver, (2) LLM membaca tiap klausa secara semantik dan menghasilkan pra-anotasi independen, (3) manusia mengadjudikasi **hanya baris yang kedua sumbernya berbeda**, ditambah sampel acak baris yang disepakati sebagai kontrol. Hasil akhir disebut **human-adjudicated**, bukan anotasi manusia dari nol. |
| Alternatives | Manusia melabeli seluruh 500 dari nol (asal-usul terkuat, tetapi 3–4 jam dan menghambat semuanya); LLM melabeli sendiri tanpa adjudikasi (tidak sah dipakai mengevaluasi model yang labeling function-nya ditulis oleh pihak yang sama). |
| Rationale | Beban manusia turun dari 500 ke 302 baris, sementara keputusan akhir tetap di tangan manusia. Sampel kontrol menjaga terhadap kekeliruan yang kebetulan disepakati kedua sumber otomatis - justru jenis kesalahan yang paling berbahaya karena tidak meninggalkan jejak. |
| Consequences & Risk | Pra-anotasi LLM **tidak independen sepenuhnya** dari labeling function: keduanya berangkat dari definisi taksonomi yang sama. Karena itu kesepakatan antara keduanya TIDAK boleh dilaporkan sebagai ukuran akurasi, dan hanya baris hasil adjudikasi yang boleh menjadi dasar angka proposal. Provenance wajib ditulis eksplisit di MODEL_CARD dan proposal. |
| Hasil awal | Kesepakatan aspek 56,4%, sentimen 80,4%. Perselisihan menyingkap tiga bug labeling function yang nyata: kata "enak" memicu aspek rasa pada konteks non-makanan, aturan cadangan "barang" memicu kualitas produk pada kalimat pengiriman, dan variasi kata ("sampenya" vs "sampai") membuat leksikon meleset. |
| Revisit condition | Bila hasil adjudikasi menunjukkan pra-anotasi LLM menyimpang sistematis pada aspek tertentu, aspek itu dilabeli manusia penuh pada iterasi berikutnya. |

### ADR-018 - Q&A dijawab dari statistik terhitung + retrieval, bukan dari LLM generatif

| Aspek | Keterangan |
| --- | --- |
| Context | QNA-01 (blueprint bagian 30.2) menjanjikan tanya jawab atas ulasan pengguna. Implementasi awal hanya berupa stub yang selalu menolak menjawab dengan alasan "mode sederhana", sehingga fitur ini mati sepanjang orchestrator belum ada - padahal FALLBACK MODE (ADR-014) menyatakan yang boleh berbeda hanyalah lapisan narasi, bukan datanya. |
| Decision | Jawaban disusun dari dua sumber yang sudah ada dan keduanya dapat ditelusuri: (1) agregat aspek hasil `calculate_aspect_statistics` untuk angkanya, (2) `EvidenceIndex` untuk kutipannya. Tidak ada teks yang dihasilkan model generatif. Tanpa kutipan yang lolos ambang, sistem menolak menjawab. |
| Alternatives | Menunggu orchestrator SEA-LION (fitur mati sampai Fase 10, dan tetap berisiko halusinasi); membiarkan stub menolak selamanya (menjanjikan fitur di UI yang tidak pernah bekerja). |
| Rationale | Angka pada jawaban berasal dari tool yang sama dengan angka pada Action Card, sehingga tidak mungkin bertentangan dengan layar lain. Setiap jawaban membawa kutipan verbatim, sehingga pengguna dapat memeriksa sendiri - sifat yang justru hilang bila jawabannya dikarang model. |
| Consequences & Risk | Jawaban terdengar seperti template dan tidak menangani pertanyaan majemuk. Risiko utamanya **false grounding**: retrieval selalu mengembalikan tetangga terdekat, sehingga pertanyaan di luar domain dapat terjawab lengkap dengan kutipan yang tampak sah - "Berapa harga saham Telkom besok?" sempat terjawab oleh statistik harga produk. Ditangani penjaga `is_out_of_domain()`; lihat baris berikut. |
| Penjaga domain | Diukur pada korpus contoh (120 ulasan, 467 kata unik) atas 14 pertanyaan: rasio kata asing pada pertanyaan wajar berhenti di 0,50, pertanyaan di luar domain mulai dari 0,75. Ambang ditetapkan 0,65. Pada batch kecil kosakata menyempit sehingga penjaga lebih mudah menolak - arah kegagalan yang memang dipilih, karena menolak dapat diperbaiki pengguna sedangkan jawaban keliru tidak terdeteksi. |
| Revisit condition | Bila orchestrator aktif, lapisan narasi boleh menggantikan template - tetapi syarat "tanpa kutipan tidak menjawab" dan penjaga domain tetap berlaku di atasnya. |
