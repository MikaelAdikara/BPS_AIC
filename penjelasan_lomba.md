# Penjelasan Lomba — AI Innovation Challenge (AIC) COMPFEST 18

> Ringkasan ini difokuskan pada **apa yang harus dibangun, batasan proyek, kriteria penilaian, rubrik, dan seluruh deliverables/submisi**. Timeline acara sengaja tidak dibahas, kecuali batas waktu yang secara langsung memengaruhi validitas project/submission.

---

## 1. Inti Lomba: Project-nya Disuruh Ngapain?

AI Innovation Challenge (AIC) adalah kompetisi untuk membuat **inovasi berbasis Artificial Intelligence (AI)** yang menyelesaikan permasalahan nyata pada industri dan perdagangan Indonesia.

Tema utama:

> **AI for the Backbone of the Economy**

Artinya, project harus memakai AI untuk membantu mentransformasi rantai nilai bisnis, khususnya pada salah satu/lebih area berikut:

### A. Smart Manufacturing — Pabrik

AI digunakan pada proses pengolahan, produksi, atau operasi pabrik.

Contoh arah solusi:

- quality inspection / defect detection,
- predictive maintenance,
- optimasi proses produksi,
- forecasting kebutuhan bahan,
- optimasi penggunaan energi,
- monitoring proses produksi berbasis AI.

### B. Smart Logistics — Gudang & Distribusi

AI digunakan untuk membantu pergerakan barang dan operasi logistik.

Contoh arah solusi:

- route optimization,
- inventory forecasting,
- demand forecasting,
- warehouse optimization,
- anomaly detection pada distribusi,
- optimasi pengiriman,
- estimasi keterlambatan.

### C. Smart Commerce — Toko & Pasar

AI digunakan pada sisi konsumen, sales operational, atau transaksi komersial.

Contoh arah solusi:

- recommendation system,
- customer support berbasis AI,
- forecasting penjualan,
- fraud/anomaly detection,
- pricing intelligence,
- analisis perilaku pelanggan,
- sales assistant / commerce assistant.

Project tidak wajib berupa web app. Bentuk inovasi dapat berupa:

- aplikasi web,
- IoT,
- software,
- hardware + software,
- atau bentuk sistem lain,

selama **AI merupakan bagian yang relevan dari solusi**, bukan fitur tempelan.

---

# 2. Target Project pada Babak Penyisihan

Yang diminta pada penyisihan **bukan produk production-ready yang sangat besar**.

Fokusnya adalah membuat **Minimum Viable Product (MVP)** yang:

1. memiliki fungsi AI inti yang benar-benar dapat dijalankan;
2. menunjukkan solusi terhadap masalah yang dipilih;
3. cukup matang untuk dievaluasi;
4. arsitekturnya masih dapat dikembangkan pada babak final;
5. dapat dijalankan kembali secara lokal oleh panitia.

Project penyisihan juga harus menjadi project yang **dilanjutkan** jika lolos ke final.

Jadi, jangan membuat prototype sekali pakai yang kemudian akan dibuang total saat final.

---

# 3. Batasan Scope MVP

Panitia secara eksplisit membatasi scope agar peserta tidak overbuild.

## 3.1 Frontend / UI

Frontend cukup berfokus pada **alur interaksi inti**:

> user memberikan satu input → sistem memproses → output AI ditampilkan.

Tidak perlu membuat fitur produk sekunder yang kompleks, misalnya:

- advanced analytics dashboard,
- sistem autentikasi kompleks,
- user management,
- halaman riwayat penggunaan,
- administrasi kompleks,
- fitur non-core lainnya.

### Prinsip

Frontend dinilai sebagai alat untuk menunjukkan core use case.

**Jangan menghabiskan sebagian besar waktu pada UI kalau core AI belum matang.**

---

## 3.2 Backend & Integrasi

Backend cukup sampai pada **pemrosesan interaksi secara sinkron**.

Tidak perlu membuat:

- background jobs,
- distributed infrastructure,
- automated data logging pipeline,
- database terdistribusi,
- infrastruktur skala production.

Yang penting:

- aplikasi dapat dijalankan secara lokal,
- integrasi FE ↔ BE ↔ AI jelas,
- flow sistem reproducible.

Panitia meminta sistem dapat dijalankan sesuai panduan pada `README.md`, menggunakan **Docker Compose**.

---

## 3.3 Model AI & Algoritma

Implementasi AI pada penyisihan cukup berfokus pada:

> **core inference**

Parameter boleh bersifat statis ketika demo berjalan.

Tidak diwajibkan membuat:

- auto-tuning system,
- bulk testing framework,
- automatic retraining pipeline,
- automated feedback loop,
- production MLOps penuh.

Tetapi AI yang digunakan harus punya alasan yang jelas:

- mengapa model tersebut dipilih,
- bagaimana model bekerja dalam use case,
- bagaimana dataset diperoleh,
- bagaimana preprocessing dilakukan,
- bagaimana model diintegrasikan ke aplikasi.

---

# 4. Aturan Model AI

Diperbolehkan menggunakan:

- model API,
- pre-trained model,
- model milik pihak lain,
- framework/library AI existing.

Namun rulebook menyebutkan:

> model wajib di-**fine-tune sesuai inovasi fitur per tim**.

Jadi penggunaan model/API tidak boleh berhenti pada sekadar:

> “ambil model existing → panggil API → selesai.”

Project harus menunjukkan pekerjaan pengembangan yang relevan dari tim terhadap kebutuhan inovasinya.

---

# 5. Dataset

Dataset boleh berasal dari:

- dataset publik yang sudah tersedia sebelumnya;
- data sintetis.

Yang harus dikerjakan dan dijelaskan selama periode lomba antara lain:

- penggunaan model,
- arsitektur sistem,
- feature,
- preprocessing,
- integrasi sistem.

Di proposal, jelaskan dengan jelas:

1. sumber dataset;
2. bagaimana dataset diperoleh;
3. cleaning / preprocessing;
4. feature engineering jika ada;
5. train/validation/test jika relevan;
6. bagaimana data dipakai oleh model.

---

# 6. Orisinalitas Project

Project harus merupakan **karya orisinal tim**.

Project yang dikumpulkan harus dikerjakan dalam periode pengerjaan kompetisi.

Tidak diperbolehkan melanjutkan project lama yang:

- sudah pernah dibuat sebelum kompetisi,
- sudah selesai sebelumnya,
- maupun masih berupa project ongoing dari luar periode lomba.

Repository GitHub juga akan digunakan untuk melihat proses pengerjaan project.

---

# 7. Repository GitHub — Requirement Penting

Repository project harus:

- berada di GitHub;
- memiliki visibility **public**;
- berisi source code;
- dapat diakses panitia;
- dapat dijalankan;
- memiliki setup guide yang jelas dalam `README.md`;
- menggunakan Docker Compose agar project dapat direproduksi secara lokal.

Setiap perubahan project diwajibkan di-commit dan di-push.

## Commit Message

Rulebook meminta commit deskriptif mengikuti gaya Conventional Commits, misalnya:

```text
feat: add demand forecasting endpoint
fix: handle missing inventory records
refactor: separate inference service from backend
```

Commit yang tidak deskriptif dapat dianggap tidak memenuhi standar development yang ditetapkan.

### Jangan lakukan

```text
update
fix
final
final2
coba
test
asd
```

### README minimal sebaiknya memuat

```text
# Nama Project

## Deskripsi
## Problem
## Core Features
## Architecture
## AI / Model
## Dataset
## Prerequisites
## Installation
## Environment Variables
## Running Locally
## Docker Compose
## Example Input
## Example Output
## Project Structure
## Known Limitations
```

---

# 8. Deliverables Babak Penyisihan

Ada **4 deliverable utama** yang perlu dikumpulkan.

## Deliverable 1 — GitHub Repository

Submit:

> **link repository source code GitHub**

Repository harus memiliki:

- source code project,
- `README.md`,
- setup guide,
- Docker Compose,
- implementasi model/inference,
- frontend/backend sesuai kebutuhan,
- konfigurasi yang diperlukan agar aplikasi bisa dijalankan.

---

## Deliverable 2 — Video Proof of Work

### Tujuan

Proof of Work bukan video promosi.

Video ini digunakan untuk membuktikan:

- kondisi MVP sebenarnya,
- fungsi yang working,
- fungsi yang masih buggy,
- flow aplikasi,
- bahwa project benar-benar dapat berjalan.

### Durasi

**Maksimal 7 menit.**

### Upload

YouTube dengan visibility:

> **Unlisted**

### Format judul

```text
COMPFEST 18 AIC: PROOF OF WORK - [Nama Tim] - [Nama Proyek]
```

### Isi yang harus diperlihatkan

Video hanya perlu menunjukkan:

- jalannya MVP;
- apa yang dilakukan sistem;
- flow program;
- kondisi fitur saat submission.

Jika fitur masih buggy atau belum sempurna, tunjukkan dan jelaskan statusnya.

**Jangan menyamarkan fitur gagal seolah-olah working.**

Semua fitur yang diperlihatkan pada video promosi harus juga terdapat pada Proof of Work.

---

# 9. Ketentuan Rekaman Proof of Work

## Jika Software-only

Video harus memperlihatkan secara bersamaan:

- terminal,
- aplikasi,
- timestamp.

Diperbolehkan:

- fast-forward saat menunggu loading;
- voice-over.

**Dilarang keras melakukan cut video atau editing lain** yang dapat menghilangkan kontinuitas demonstrasi.

---

## Jika Hardware + Software

Project wajib menyediakan:

> **mock data mode**

Artinya, software harus bisa dijalankan **tanpa hardware fisik**, sehingga panitia tetap dapat melakukan cross-check.

Video menunjukkan:

- terminal,
- aplikasi,
- timestamp,
- hardware yang bekerja, jika sudah terintegrasi.

Jika hardware belum fully integrated, demonstrasi boleh menggunakan mock data mode.

Sama seperti software-only:

- fast-forward loading diperbolehkan;
- voice-over diperbolehkan;
- cut/edit manipulatif dilarang.

---

# 10. Deliverable 3 — Video Promosi Karya Inovasi

Video promosi berbeda dengan Proof of Work.

Proof of Work = **bukti teknis**.

Video Promosi = **menjual ide, dampak, dan produk**.

### Durasi

**Maksimal 5 menit.**

### Format

- MP4
- resolusi minimal **720p**

### Upload

YouTube dengan visibility:

> **Public**

### Format judul

```text
COMPFEST 18 AIC: [Nama Tim] - [Nama Proyek]
```

### Isi video

Video harus menjelaskan:

1. masalah yang diangkat;
2. proses perancangan karya;
3. solusi AI yang dibuat;
4. bagaimana solusi menyelesaikan masalah;
5. manfaat bagi user / industri;
6. demonstrasi produk;
7. value dan potensi implementasi.

Penyajian diharapkan menarik bagi:

- calon pengguna,
- stakeholder,
- industri,
- bahkan investor.

Demonstrasi boleh berupa:

- screen recording,
- video kamera,
- atau kombinasi keduanya.

---

# 11. Deliverable 4 — Proposal PDF

Proposal maksimal:

> **20 halaman**

Yang **tidak dihitung** dalam batas 20 halaman:

- cover;
- daftar pustaka;
- lampiran.

Proposal minimal memuat:

## 11.1 Nama Kelompok & Nama Inovasi

Berisi identitas project.

**Catatan:** selama kompetisi peserta dilarang menunjukkan latar belakang institusi pendidikan dalam bentuk apa pun.

Jadi jangan menjadikan universitas/sekolah sebagai bagian branding proposal/project.

---

## 11.2 Latar Belakang

Jelaskan:

- masalah nyata yang ingin diselesaikan;
- siapa yang mengalami masalah;
- mengapa masalah penting;
- kondisi existing;
- kekurangan solusi saat ini.

Idealnya didukung oleh:

- data,
- studi,
- evidence,
- observasi,
- sumber industri.

---

## 11.3 Tujuan dan Manfaat Pengembangan

Jelaskan:

- tujuan sistem;
- target pengguna;
- value yang diberikan;
- perubahan yang diharapkan setelah solusi digunakan.

---

## 11.4 Metodologi

Rulebook secara eksplisit meminta metodologi mencakup:

### A. Alur memperoleh dataset

Misalnya:

```text
Sumber Data
    ↓
Pengumpulan
    ↓
Cleaning
    ↓
Preprocessing
    ↓
Dataset Siap Model
```

### B. Alur pengembangan model untuk setiap feature

Untuk setiap fitur AI:

```text
Problem
    ↓
Input
    ↓
Preprocessing
    ↓
Model
    ↓
Inference
    ↓
Output
```

### C. Alur integrasi model ke environment code

Misalnya:

```text
Frontend
    ↓
Backend API
    ↓
AI Service
    ↓
Model Inference
    ↓
Backend Response
    ↓
Frontend Output
```

---

## 11.5 Metode Pendukung Decision Making

Proposal dapat memuat:

- benchmark model,
- evaluation metric,
- eksperimen,
- baseline comparison,
- literature review,
- trade-off teknologi,
- architecture decision,
- alasan memilih model.

Tujuannya membuktikan keputusan tim **bukan asal memilih teknologi**.

---

## 11.6 Kesimpulan

Ringkas:

- masalah;
- solusi;
- AI yang digunakan;
- dampak;
- kesiapan MVP;
- arah pengembangan berikutnya.

---

# 12. Checklist Submission

Sebelum submit, pastikan semua berikut terpenuhi.

## Project

- [ ] Project sesuai tema **AI for the Backbone of the Economy**
- [ ] Masuk Smart Manufacturing, Smart Logistics, atau Smart Commerce
- [ ] AI benar-benar menjadi bagian penting solusi
- [ ] Project dibuat pada periode lomba
- [ ] Project merupakan karya orisinal tim
- [ ] MVP memiliki core use case yang dapat dijalankan
- [ ] Scope tidak overbuild
- [ ] Project dapat dikembangkan lagi saat final

## AI

- [ ] Model/AI yang dipakai relevan dengan problem
- [ ] Core inference berjalan
- [ ] Dataset dan preprocessing terdokumentasi
- [ ] Alasan pemilihan model jelas
- [ ] Penggunaan pre-trained/API disertai adaptasi/fine-tuning sesuai inovasi

## Repository

- [ ] Repository GitHub public
- [ ] Source code lengkap
- [ ] README lengkap
- [ ] Setup guide dapat diikuti
- [ ] Docker Compose tersedia
- [ ] Program dapat dijalankan secara lokal
- [ ] Commit history mencerminkan proses pengembangan
- [ ] Commit message deskriptif
- [ ] Tidak ada dependency/secret penting yang hilang
- [ ] Tidak ada API key rahasia di repository

## Proof of Work

- [ ] Maksimal 7 menit
- [ ] YouTube Unlisted
- [ ] Judul sesuai format
- [ ] Menampilkan MVP nyata
- [ ] Terminal + aplikasi + timestamp terlihat
- [ ] Menunjukkan fitur working maupun buggy secara jujur
- [ ] Tidak menggunakan cut yang dilarang
- [ ] Jika hardware, mock data mode tersedia

## Video Promosi

- [ ] Maksimal 5 menit
- [ ] MP4
- [ ] Minimal 720p
- [ ] YouTube Public
- [ ] Judul sesuai format
- [ ] Menjelaskan problem
- [ ] Menjelaskan solusi
- [ ] Menjelaskan AI
- [ ] Menjelaskan dampak/value
- [ ] Menunjukkan demonstrasi produk
- [ ] Semua fitur yang diperlihatkan juga ada di Proof of Work

## Proposal

- [ ] PDF
- [ ] Maksimal 20 halaman di luar cover, daftar pustaka, dan lampiran
- [ ] Nama tim & nama inovasi
- [ ] Latar belakang
- [ ] Tujuan & manfaat
- [ ] Metodologi
- [ ] Alur dataset
- [ ] Alur pengembangan model tiap feature
- [ ] Alur integrasi model ke code
- [ ] Alasan technical decision
- [ ] Kesimpulan
- [ ] Bebas plagiarisme
- [ ] Tidak menunjukkan latar belakang institusi pendidikan

---

# 13. Kriteria Penilaian Penyisihan

Bobot utama penilaian adalah sebagai berikut:

| Kriteria | Bobot |
|---|---:|
| Orisinalitas dan Dampak Sosial | 20% |
| Implementasi Teknologi & Kematangan Arsitektur | 25% |
| Kesiapan MVP untuk Babak Final | 15% |
| Video Promosi | 15% |
| Kualitas Proposal & Proses Pengembangan | 15% |
| Relevansi dengan Tema | 10% |
| **Total nilai utama** | **100%** |
| Business Value & Governance — Bonus | +3.5% |
| AIC Talks — Bonus | +1.5% |
| **Maksimum** | **105%** |

---

# 14. Rubrik Penilaian Detail

## 14.1 Orisinalitas dan Dampak Sosial — 20%

Juri melihat:

- apakah solusi unik dan inovatif;
- apakah pendekatannya memiliki kebaruan;
- apa perbedaannya dibanding solusi existing;
- seberapa relevan solusi terhadap konteks masalah;
- seberapa besar masalah yang diselesaikan;
- seberapa urgent masalah tersebut;
- apakah solusi sesuai kebutuhan target user;
- apakah solusi memiliki kemungkinan digunakan dalam konteks lebih luas/global.

### Agar kuat di bagian ini

Jangan cuma berkata:

> "Belum ada aplikasi seperti ini."

Lebih kuat jika proposal menunjukkan:

```text
Existing solution A → kekurangan X
Existing solution B → kekurangan Y

Solusi kami:
- menyelesaikan X
- menyelesaikan Y
- menambahkan Z
```

---

# 15. Implementasi Teknologi & Kematangan Arsitektur — 25%

Ini adalah **bobot terbesar**.

Juri mengevaluasi:

- apakah pemilihan teknologi sesuai kebutuhan;
- apakah model AI/framework/stack proporsional;
- apakah AI fokus pada core inference yang jelas;
- apakah parameter inference didefinisikan dengan jelas;
- apakah arsitektur modular;
- apakah AI, backend, dan frontend terpisah secara bersih;
- apakah README cukup menjelaskan alur sistem.

### Yang perlu ditunjukkan

Idealnya punya arsitektur seperti:

```text
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Backend   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ AI Service  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Model/Data  │
└─────────────┘
```

Bukan satu file besar yang mencampurkan:

- frontend,
- preprocessing,
- inference,
- business logic,
- data.

---

# 16. Kesiapan MVP untuk Babak Final — 15%

Juri melihat apakah scope MVP:

- sesuai batasan;
- tidak terlalu besar;
- tidak terlalu kecil;
- sudah memiliki core functionality;
- dapat dievaluasi;
- dapat dikembangkan lebih lanjut;
- arsitekturnya fleksibel;
- masih memiliki area improvement yang nyata.

Menariknya, project **tidak harus sempurna**.

Rulebook bahkan mempertimbangkan:

> apakah tim mengetahui bagian sistem yang masih dapat ditingkatkan secara signifikan?

Artinya, mampu menjelaskan limitation dengan baik justru merupakan bagian dari kematangan engineering.

---

# 17. Video Promosi — 15%

Juri melihat:

- apakah masalah dan solusi dapat dipahami;
- apakah bahasa video lugas;
- apakah storytelling menarik;
- apakah proses dari ide → development → execution terlihat;
- apakah video menarik bagi stakeholder;
- apakah konten sesuai requirement.

Video ini bukan sekadar demo UI.

Susunan yang aman:

```text
Problem
↓
Why it matters
↓
Existing gap
↓
Our solution
↓
How AI works
↓
Demo
↓
Impact
↓
Future potential
```

---

# 18. Kualitas Proposal & Proses Pengembangan — 15%

Juri melihat:

- struktur proposal;
- kelengkapan proposal;
- metodologi;
- alur dataset;
- integrasi model;
- seberapa jelas dan logis penjelasan teknis;
- apakah pilihan teknologi/model/arsitektur memiliki dasar analisis;
- apakah proses development bersifat iteratif dan reflektif.

Jangan membuat proposal hanya seperti dokumentasi fitur.

Yang ingin dilihat:

```text
Kami mencoba A
↓
hasilnya kurang karena X
↓
kami evaluasi
↓
kami memilih B
↓
hasilnya lebih sesuai karena Y
```

Ini jauh lebih kuat daripada:

> "Kami menggunakan model B."

---

# 19. Relevansi dengan Tema — 10%

Juri mengecek:

1. apakah inovasi sesuai tema;
2. apakah AI benar-benar relevan terhadap tema.

Jadi project harus jelas memiliki hubungan dengan:

- produksi,
- distribusi/logistik,
- atau commerce.

Project AI yang menarik tetapi tidak mempunyai kaitan yang kuat dengan rantai nilai tersebut berisiko kehilangan poin besar.

---

# 20. Bonus — Business Value & Governance (+3.5%)

Bonus ini mengevaluasi apakah tim menyertakan:

- model bisnis;
- analisis kelayakan adopsi industri;
- potential buyer/user;
- implementation feasibility;
- regulasi AI;
- etika;
- responsible AI / governance.

Contoh hal yang dapat ditulis:

```text
Target Customer
Business Model
Cost Structure
Deployment Model
Data Privacy
Human Oversight
AI Risk
Bias
Security
Regulatory Consideration
```

Ini bonus, tetapi +3.5% cukup besar untuk membedakan dua tim dengan nilai teknis mirip.

---

# 21. Bonus — AIC Talks (+1.5%)

Bonus diperoleh dengan:

- mengikuti AIC Talks;
- mengisi presensi.

---

# 22. Cara Berpikir Agar Project Sesuai Rubrik

Jangan mulai dari:

> "Kita mau pakai LLM / Computer Vision / XGBoost."

Mulai dari:

```text
MASALAH
↓
USER
↓
PAIN POINT
↓
DATA
↓
DECISION / OUTPUT YANG DIBUTUHKAN
↓
AI YANG PALING COCOK
↓
MVP
```

Contoh:

```text
Gudang sering overstock dan stockout
↓
Warehouse manager
↓
Tidak mengetahui demand beberapa hari ke depan
↓
Historical sales + inventory
↓
Prediksi kebutuhan stok
↓
Forecasting model
↓
Dashboard sederhana:
input SKU → prediksi demand → rekomendasi reorder
```

AI menjadi solusi terhadap decision nyata, bukan sekadar gimmick.

---

# 23. Prioritas Pengerjaan Berdasarkan Bobot

Kalau resource terbatas, urutan prioritas yang paling masuk akal berdasarkan rubrik:

## Prioritas 1 — Core AI + Architecture — 25%

Pastikan:

- AI works;
- output relevan;
- arsitektur bersih;
- setup reproducible.

## Prioritas 2 — Problem & Impact — 20%

Pastikan:

- problem valid;
- evidence kuat;
- solusi berbeda;
- user jelas.

## Prioritas 3 — MVP — 15%

Pastikan core flow benar-benar works.

## Prioritas 4 — Proposal — 15%

Dokumentasikan reasoning dan proses development.

## Prioritas 5 — Video Promosi — 15%

Buat storytelling bagus setelah produk cukup matang.

## Prioritas 6 — Theme Fit — 10%

Pastikan dari awal project tidak keluar jalur tema.

## Bonus

Tambahkan business feasibility + responsible AI kalau core sudah aman.

---

# 24. Struktur Project yang Aman

Contoh struktur repository:

```text
project/
│
├── frontend/
│   ├── ...
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   ├── api/
│   ├── services/
│   └── Dockerfile
│
├── ai/
│   ├── model/
│   ├── preprocessing/
│   ├── inference/
│   └── ...
│
├── data/
│   ├── sample/
│   └── README.md
│
├── docs/
│   └── architecture.md
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

Prinsipnya:

> evaluator harus bisa memahami dan menjalankan project tanpa perlu menebak-nebak.

---

# 25. Definition of Done Penyisihan

Project dapat dianggap siap dikumpulkan kalau seseorang yang bukan anggota tim dapat melakukan:

```text
git clone
↓
baca README
↓
setup environment
↓
docker compose up
↓
buka aplikasi
↓
masukkan input
↓
AI inference berjalan
↓
output muncul
```

dan evaluator juga dapat memahami:

```text
problem apa yang diselesaikan
↓
mengapa AI dibutuhkan
↓
data dari mana
↓
model apa yang digunakan
↓
kenapa model tersebut dipilih
↓
bagaimana AI diintegrasikan
↓
apa hasilnya
↓
apa limitation
↓
apa yang akan dikembangkan di final
```

Jika dua flow tersebut sudah jelas, project secara teknis sudah berada pada bentuk yang sangat dekat dengan apa yang diminta rulebook.

---

# 26. Kesalahan yang Paling Harus Dihindari

### 1. AI hanya gimmick

Contoh buruk:

> Sistem inventory biasa lalu ditambahkan chatbot.

Kalau chatbot tidak menyelesaikan core problem, nilai teknologi dan relevansi dapat lemah.

### 2. Overbuild frontend

Dashboard sangat cantik tetapi model tidak tervalidasi.

### 3. Repository tidak reproducible

Project hanya jalan di laptop developer.

### 4. README minim

Evaluator tidak tahu cara menjalankan project.

### 5. Demo video berbeda dengan kondisi repository

Panitia dapat melakukan cross-check.

### 6. Menyembunyikan bug

Proof of Work meminta kondisi MVP sebenarnya.

### 7. Video promosi menampilkan fitur yang tidak ada

Semua fitur video promosi harus muncul di Proof of Work.

### 8. Proposal hanya menjelaskan fitur

Proposal harus menunjukkan:

- metodologi,
- reasoning,
- eksperimen,
- decision making.

### 9. Project lama digunakan ulang

Project harus dikerjakan pada periode kompetisi.

### 10. Menaruh nama/institusi pendidikan

Rulebook melarang menunjukkan latar belakang institusi selama perlombaan.

---

# 27. Ringkasan Super Singkat

Untuk penyisihan AIC, tim harus membuat:

> **MVP AI yang menyelesaikan masalah nyata pada manufacturing, logistics, atau commerce, dapat dijalankan secara lokal dan direproduksi oleh panitia, disertai bukti development dan dokumentasi yang jelas.**

Yang dikumpulkan:

1. **GitHub repository public**
   - source code,
   - README,
   - Docker Compose,
   - setup reproducible.

2. **Proof of Work**
   - max 7 menit,
   - YouTube unlisted,
   - demo teknis kondisi MVP sebenarnya.

3. **Video Promosi**
   - max 5 menit,
   - public,
   - MP4 ≥ 720p,
   - menjelaskan problem, solusi, AI, demo, dan impact.

4. **Proposal PDF**
   - max 20 halaman di luar cover/daftar pustaka/lampiran,
   - problem,
   - objective,
   - metodologi,
   - dataset,
   - model,
   - integrasi,
   - reasoning,
   - kesimpulan.

Nilai terbesar datang dari:

> **Implementasi Teknologi & Kematangan Arsitektur — 25%**

disusul:

> **Orisinalitas & Dampak Sosial — 20%**

Jadi tujuan project bukan membuat aplikasi paling besar atau UI paling kompleks.

Tujuannya adalah membuat:

> **solusi AI yang problem-nya kuat, teknologinya masuk akal, MVP-nya bekerja, arsitekturnya bersih, dan seluruh prosesnya dapat dibuktikan.**
