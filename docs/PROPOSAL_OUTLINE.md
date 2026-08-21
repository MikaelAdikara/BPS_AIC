# Kerangka Proposal

Kerangka kerja untuk menyusun proposal PDF babak penyisihan. **Ini bukan proposalnya** - ini
peta bahannya: apa yang harus ditulis di tiap bagian, berapa halaman jatahnya, dan di berkas
mana bahan mentahnya sudah tersedia.

Batas: **20 halaman** di luar cover, daftar pustaka, dan lampiran.

> **Larangan yang mudah dilanggar tanpa sadar:** peserta dilarang menunjukkan latar belakang
> institusi pendidikan dalam bentuk apa pun. Periksa cover, header, footer, nama berkas,
> metadata PDF, watermark templat slide, dan tangkapan layar yang memuat nama akun.

---

## Prinsip penulisan yang menentukan nilai

Rubrik bagian 18 menilai proposal bukan dari kelengkapan fitur, melainkan dari **jejak
berpikirnya**. Yang dicari juri:

```
Kami mencoba A  →  hasilnya kurang karena X  →  kami evaluasi  →  kami pilih B  →  lebih sesuai karena Y
```

bukan:

> "Kami menggunakan model B."

**Proyek ini punya tujuh cerita semacam itu yang benar-benar terjadi**, lengkap dengan angka
dan tanggalnya. Kebanyakan tim harus mengarang narasi iterasi; di sini tinggal disalin dari
`experiment_log.md` dan ADR. Bagian 4 di bawah memetakan ketujuhnya.

Aturan kedua, yang berlaku sepanjang dokumen: **gate yang gagal ditulis sebagai gagal.** Rubrik
bagian 16 secara eksplisit menghargai tim yang tahu bagian mana dari sistemnya masih lemah.
Menyembunyikan Fase 2 (aspek) dan Fase 3 (visual) justru membuang keunggulan yang sudah dimiliki
- dan panitia dapat memeriksa repositori.

---

## 1. Nama kelompok & nama inovasi — ½ halaman

Nama tim · **Ulasin** · satu kalimat yang menyebut untuk siapa dan menyelesaikan apa.

Sumber: [README §1](../README.md#1-ringkasan)

---

## 2. Latar belakang — 3 halaman

Susun dari besar ke sempit: pasarnya, lalu titik sakitnya, lalu celah yang ditinggalkan solusi
yang sudah ada.

| Isi | Bahannya ada di |
| --- | --- |
| 4,40 juta unit usaha e-commerce, mayoritas mikro (BPS 2024); 66 juta UMKM, >60% PDB (Kemenkop UKM) | [README §3.1](../README.md#31-besarannya) |
| Margin sudah tergerus 15-20% biaya platform; pengaduan BPKN naik 200% | [README §3.1](../README.md#31-besarannya) |
| Siapa yang mengalami: persona "Bu Rina", UMKM fesyen mikro dua karyawan | [dossier §7.2](reference/AIC_RESEARCH_DOSSIER.md) |
| Kondisi existing + kekurangan spesifik per produk bernama | [README §3.2](../README.md#32-solusi-yang-sudah-ada-dan-di-mana-persisnya-mereka-berhenti) |

**Bagian ini yang menentukan 20% Orisinalitas dan Dampak.** Tabel pesaing wajib menyebut nama
produk, bukan kategori - "Shopee Seller Centre berhenti di rating rata-rata dan tidak
mengelompokkan keluhan per aspek", bukan "dashboard marketplace kurang lengkap". Sertakan
harganya: celah antara yang gratis-tapi-dangkal dan yang mampu-tapi-Rp4,8-juta-per-bulan adalah
argumen terkuat yang dimiliki proyek ini.

Tutup dengan aritmetika waktu yang **memisahkan terukur dari asumsi** (6,7 menit sistem vs ~2,7
jam manual). Memisahkan keduanya secara terbuka lebih meyakinkan daripada satu angka bulat
tanpa asal-usul.

---

## 3. Tujuan dan manfaat — 1,5 halaman

| Isi | Bahannya ada di |
| --- | --- |
| Tujuan sistem, target pengguna, value | [BUSINESS_VALUE §2, §4](BUSINESS_VALUE.md) |
| Tiap janji + ukuran pembuktinya + statusnya | [BUSINESS_VALUE §4](BUSINESS_VALUE.md) |

Pakai tabel "yang dijanjikan / ukuran pembuktinya / status" apa adanya. Kolom status yang memuat
"belum diukur" pada satu baris justru menaikkan kredibilitas tiga baris lainnya.

---

## 4. Metodologi — 8 halaman ← **porsi terbesar, dan inti nilainya**

### 4.1 Alur memperoleh dataset — 1,5 halaman

```
Sumber (3 dataset publik)
    ↓
Pengumpulan
    ↓
Cleaning + harmonisasi
    ↓
Pelabelan (weak supervision)  ← ADR-015 lahir di sini
    ↓
Split product-level 70/15/15  ← leakage terverifikasi 0
    ↓
39.986 ulasan → 96.300 klausa
```

Sumber, lisensi, dan atribusi: [DATASET_CARD](DATASET_CARD.md) · [README §10](../README.md#10-dataset-dan-lisensi)

### 4.2 Alur pengembangan model per fitur — 2 halaman

Untuk NLP-01, VIS-01, RET-01, dan ACT-01, masing-masing:
`Problem → Input → Preprocessing → Model → Inference → Output`

Sumber: [ARCHITECTURE](ARCHITECTURE.md) · [README §5.2, §5.3](../README.md#52-lima-lapisan-ai)

### 4.3 Alur integrasi ke environment code — 1 halaman

`Frontend → Backend API → Tool Registry → Model Adapter → Response → Frontend`

Diagram siap pakai ada di [README §5.1](../README.md#51-diagram-kontainer). Tekankan bahwa
sepuluh tool contract adalah **satu-satunya sumber angka**, dan model bahasa berada di hilir.

### 4.4 Tujuh iterasi yang benar-benar terjadi — 3,5 halaman ← **tulis ini paling serius**

Tiap kotak di bawah sudah berbentuk narasi rubrik. Angkanya dapat ditelusuri ke
[`ml/evaluation/experiment_log.md`](../ml/evaluation/experiment_log.md).

| # | Coba A | Gagal karena | Pilih B | Hasilnya | Rujukan |
| --- | --- | --- | --- | --- | --- |
| 1 | Petakan label emosi PRDECT-ID ke 11 aspek | `Emotion` adalah dimensi emosi (Happy/Sadness/Anger), tidak berkorespondensi dengan aspek. Tidak ada dataset ABSA e-commerce Bahasa Indonesia (CASA=mobil, HoASA=hotel) | Weak supervision + gold test set berlabel manusia sebagai penengah | Pipeline label jalan, **dan risikonya diakui di muka**: metrik pada silver berpotensi sirkular | ADR-015 |
| 2 | Pakai dataset ketiga sebagai data latih | 87% barisnya duplikat, distribusi kelas persis seimbang, label = pemetaan langsung dari rating | Jadikan **stress test** - tiap baris ditandai fenomena linguistik | Melahirkan diagnosis per fenomena yang jadi argumen inti proposal | ADR-016 |
| 3 | Manusia melabeli 500 klausa gold dari nol | 3-4 jam, dan menjadi penghambat tunggal seluruh angka NLP-01 | Pra-anotasi LLM + manusia mengadjudikasi hanya 302 baris yang berselisih, plus sampel kontrol | Beban turun 40%, keputusan tetap di manusia. **Perselisihannya menyingkap 3 bug labeling function yang nyata** | ADR-017 |
| 4 | Gate Fase 2 dinyatakan **GO** dari angka silver (aspek 0,985) | Angka silver mengukur kecocokan terhadap labeling function, bukan akurasi. Pada gold, 7 dari 11 kelas aspek **identik sampai tiga desimal** dengan leksikon | Verdict dibalik jadi **DIREVISI**, lalu label diperbaiki dan model dilatih ulang | Sentimen **LULUS** (0,730 vs 0,700 vs 0,627); aspek **TIDAK LULUS** - dan dilaporkan begitu | E04→E05→E06 |
| 5 | Zero-shot CLIP untuk menilai kondisi barang dari foto | Argmax **0,45**, kalah dari tebakan sepele "selalu normal" **0,61**; 61% foto normal salah ditandai bermasalah | **NO-GO** - lapisan visual tidak dinyalakan | Pengguna tidak dikirim memeriksa barang yang tidak apa-apa. Jalur linear probe disiapkan untuk final | Gate Fase 3 |
| 6 | Q&A berupa stub yang selalu menolak selama orchestrator belum ada | Melanggar ADR-014: yang boleh berbeda saat fallback hanya lapisan **narasi**, bukan datanya | Dijawab dari statistik terhitung + retrieval, tanpa LLM | Fitur hidup pada konfigurasi yang benar-benar berjalan | ADR-018 |
| 7 | Skor prioritas = perkalian mentah enam faktor | `Business Relevance` tumpang tindih dengan `Severity` - satu hal dihitung dua kali | Tiga faktor inti dikalikan, recency & benchmark jadi pengali (+0,3 / +0,2) | Formula lebih dapat dipertahankan. **Bobotnya masih belum divalidasi**, dan itu ditulis | [README §5.4](../README.md#54-formula-skor-prioritas) |

Nomor 4 adalah cerita terkuat yang dimiliki proyek ini: **tim membalik keputusan GO-nya sendiri
setelah menemukan angkanya sirkular.** Tulis dengan urutan waktu dan tanggalnya. Itu bukti
proses yang tidak bisa dikarang.

---

## 5. Metode pendukung decision making — 3 halaman

| Isi | Bahannya ada di |
| --- | --- |
| Baseline comparison: leksikon vs TF-IDF vs IndoBERT pada gold | [MODEL_CARD §4](MODEL_CARD.md) |
| Diagnosis per fenomena linguistik: runtuh pada negasi 0,163 / sarkasme 0,198 / sentimen campuran 0,113, tetapi kuat pada typo 0,736 dan slang 0,789 | [experiment_log](../ml/evaluation/experiment_log.md) catatan E02 |
| Trade-off teknologi: local-first vs API komersial | ADR-001 |
| Keputusan arsitektur: 18 ADR (015-018 lahir dari asumsi yang terbukti salah) | [ARCHITECTURE](ARCHITECTURE.md) |

Tabel fenomena itu **argumen inti kenapa AI dibutuhkan**, bukan sekadar lampiran: ia
membuktikan dengan angka bahwa pendekatan kecocokan permukaan menangani typo dan slang dengan
baik namun runtuh pada fenomena komposisional. Itulah celah yang harus ditutup model kontekstual
- klaim yang terbukti, bukan asumsi.

---

## 6. Business value & governance — 2 halaman ← **bonus +3,5%**

| Isi | Bahannya ada di |
| --- | --- |
| Target customer, model bisnis, struktur biaya, unit economics | [BUSINESS_VALUE](BUSINESS_VALUE.md) §2, §5, §6 |
| Ongkos marginal ~Rp1.330/penjual/bulan, diturunkan dari benchmark terukur | [BUSINESS_VALUE §6](BUSINESS_VALUE.md) |
| Kelayakan adopsi: 6 dari 7 hambatan sudah terjawab produk yang berjalan | [BUSINESS_VALUE §7](BUSINESS_VALUE.md) |
| Privasi, pengawasan manusia, risiko AI, bias, keamanan, UU PDP | [RESPONSIBLE_AI](RESPONSIBLE_AI.md) |

Bonus ini bernilai +3,5% - cukup untuk memisahkan dua tim yang nilai teknisnya mirip. Dua
halaman adalah investasi yang sepadan.

---

## 7. Kesimpulan — 1 halaman

Masalah · solusi · AI yang dipakai · dampak · kesiapan MVP · arah pengembangan.

Sebutkan **secara eksplisit** apa yang belum ada dan mengapa. Rubrik bagian 16 menilai apakah
tim mengetahui bagian sistemnya yang masih dapat ditingkatkan secara signifikan - jadi paragraf
keterbatasan adalah paragraf yang menghasilkan nilai, bukan paragraf yang mengurangi.

Sumber: [LIMITATIONS](LIMITATIONS.md) · [`src/content/roadmap.js`](../apps/web/src/content/roadmap.js)

---

## Anggaran halaman

| Bagian | Halaman |
| --- | ---: |
| 1. Nama & inovasi | 0,5 |
| 2. Latar belakang | 3 |
| 3. Tujuan & manfaat | 1,5 |
| 4. Metodologi (termasuk 3,5 hal. iterasi) | 8 |
| 5. Metode pendukung decision making | 3 |
| 6. Business value & governance | 2 |
| 7. Kesimpulan | 1 |
| Cadangan | 1 |
| **Total** | **20** |

---

## Daftar periksa sebelum ekspor PDF

- [ ] ≤ 20 halaman di luar cover, daftar pustaka, lampiran
- [ ] Tidak ada nama/logo/alamat institusi pendidikan - termasuk di metadata PDF dan tangkapan layar
- [ ] Tiap angka dapat ditelusuri ke satu baris `experiment_log.md`
- [ ] Atribusi CC-BY-4.0 PRDECT-ID tercantum (Sutoyo dkk., Data in Brief 2022)
- [ ] Gate yang gagal (aspek TIDAK LULUS, visual NO-GO) tertulis apa adanya
- [ ] Angka `silver_*` tidak dikutip sebagai capaian - hanya gold yang boleh
- [ ] Klaim kustomisasi bertumpu pada fine-tuning + RAG, **bukan** tool calling
- [ ] Fitur yang muncul di video promosi juga ada di Proof of Work
- [ ] Bebas plagiarisme
