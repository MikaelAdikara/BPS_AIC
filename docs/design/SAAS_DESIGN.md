# Rancangan Produk SaaS - Ulasin

Dokumen ini adalah rancangan antarmuka **lengkap** untuk Ulasin sebagai produk SaaS utuh,
beserta alasan di balik setiap keputusan bentuknya. Dua prototipe menyertainya:

| Berkas | Isi |
| --- | --- |
| [`site.html`](site.html) | **Produk SaaS penuh** - situs publik (7 bagian), login, lalu dashboard 14 layar berkelompok. Ini acuan visual utama |
| [`prototype.html`](prototype.html) | Kerangka 14 layar beranotasi tier, untuk membaca cakupan dan alasan per layar |

Token warna dan tipografi di prototipe disalin dari
[`apps/web/src/styles/tokens.css`](../../apps/web/src/styles/tokens.css). Kalau keduanya berbeda,
**aplikasi yang benar** - prototipe mengikuti, bukan sebaliknya.

## 0. Peta layar `site.html`

Empat belas layar aplikasi, dikelompokkan menurut pekerjaan - dan **setiap layar turun dari
keluaran model yang memang ada**, bukan fitur yang ditambahkan agar terlihat ramai.

| Kelompok | Layar | Keluaran model yang menjadi sumbernya |
| --- | --- | --- |
| Analisis | Ruang kerja · Analisis baru · Hasil | `AnalysisResult` penuh (ACT-01, ING-05, OPP-01, BEN-01, QNA-01) |
| Eksplorasi | **Cari bukti** · **Peta aspek** · **Perbandingan varian** · Tren | Indeks embedding RET-01; `AspectAggregate` dipotong per periode dan per varian |
| Tindak lanjut | Papan tindakan · **Pantauan** · Laporan | `user_action` pada Action Card; ambang dijalankan atas angka yang sudah dihitung |
| Sistem | **Kesehatan model** · Tim · Langganan · Data &amp; privasi | MODEL_CARD, hasil gerbang VIS-01, status FALLBACK MODE |

Ditambah **keadaan kosong** (layar pertama sebelum ada analisis) dan **palet perintah ⌘K**
yang melompat ke layar mana pun - pola SaaS modern yang sekaligus menjadi jalur cepat saat
demo langsung ke juri.

Empat layar bertanda tebal adalah penambahan yang paling menaikkan nilai produk:

- **Cari bukti** memakai indeks embedding yang sama dengan penyusun bukti Action Card. Ia
  mengubah RET-01 dari mesin di balik layar menjadi alat yang langsung dipakai pengguna.
- **Perbandingan varian** menjawab pertanyaan yang tidak terjawab angka agregat: "keluhan
  ukuran 17%" tidak dapat ditindaklanjuti, tetapi "varian Mocca L menyumbang separuhnya" bisa.
- **Pantauan** menjalankan ambang atas angka yang sudah dihitung sistem - bukan tebakan baru.
- **Kesehatan model** adalah elemen tanda tangan produk ini: satu-satunya layar yang
  menampilkan rapor AI-nya sendiri, termasuk fitur foto yang dinyatakan NO-GO dan dimatikan.
  Tidak ada pesaing yang menampilkan kegagalannya sendiri di dalam produk.

### Empat field ACT-01 yang sebelumnya dihitung tetapi tidak pernah tampil

Pemeriksaan skema `ActionCard` terhadap prototipe menemukan enam field yang tidak muncul di
antarmuka. Dua di antaranya ternyata memang tampil (frekuensi dan rekomendasi, hanya lolos dari
pencocokan kata kunci). **Empat sisanya benar-benar hilang**, dan justru keempatnya yang
mengubah kartu dari laporan menjadi tugas yang dapat dieksekusi:

| Field | Kini tampil sebagai |
| --- | --- |
| `action_category` | Jenis tindakan |
| `estimated_effort` | Perkiraan usaha |
| `suggested_owner` | Usulan penanggung jawab |
| `expected_outcome` | Hasil yang diharapkan |

Ditampilkan pada panel bukti sebagai blok "Rencana kerjanya", disertai catatan bahwa perkiraan
usaha dan penanggung jawab disusun dari kategori tindakan - bukan dari pengetahuan tentang tim
pengguna. Tanpa catatan itu, angka tersebut mudah dibaca sebagai kepastian yang tidak dimiliki
sistem.

`risk_if_not_done` juga dinaikkan menjadi blok tersendiri ("Kalau dibiarkan"), berdampingan
dengan `risk_if_recommendation_wrong` yang sudah ada. Menampilkan kedua arah risiko sekaligus
menjaga keputusan tetap seimbang: biaya bertindak dan biaya diam sama-sama terlihat.

### Yang sengaja dihindari pada tampilannya

Diaudit terhadap daftar larangan desain produksi:

| Larangan | Penanganan |
| --- | --- |
| Side-stripe border sebagai aksen kartu | Dihapus dari Action Card; urgensi dibawa pill bertulisan + tint permukaan. Garis kiri hanya tersisa pada blockquote kutipan - konvensi tipografi, dan elemen tanda tangan merek |
| Grid kartu identik | Bagian masalah memakai tiga blok berbobot berbeda; bagian fitur memakai satu blok utama + daftar |
| Template hero-metric (angka besar + label + gradien) | Ringkasan angka disajikan sebagai satu baris tipografis, bukan empat ubin seragam |
| `z-index` sembarang | Skala semantik: sticky 20 → scrim 60 → drawer 61 → toast 80 |
| Border 1px + bayangan blur besar pada elemen sama | Border memakai `box-shadow` ring 1px; bayangan angkat hanya pada elemen melayang |
| Animasi seragam di semua bagian | Tiap reveal disesuaikan isinya; `prefers-reduced-motion` mematikan seluruhnya |

---

## 1. Satu hal yang menentukan seluruh bentuk dokumen ini

Rulebook AIC bagian 5.2 membatasi MVP penyisihan pada **alur interaksi inti: input tunggal →
output AI**, dan menyebut secara eksplisit tiga hal yang *tidak perlu*: dashboard analitik
tingkat lanjut, sistem otentikasi kompleks, dan halaman riwayat penggunaan. Melanggarnya tidak
menghasilkan diskualifikasi, tetapi terpotong di kriteria **Kesiapan MVP (15%)** - panitia
menyebut "overbuilt" dinilai negatif di sana.

Artinya: **produk SaaS penuh tidak boleh menjadi yang dikumpulkan.** Maka rancangan ini dipisah
tegas menjadi tiga lapis, dan pemisahan itu ikut terlihat di prototipe lewat badge warna:

| Lapis | Status | Yang dikerjakan | Terlihat juri sebagai |
| --- | --- | --- | --- |
| **Tier 1** | Sudah berfungsi di repo | Layar 1–4, alur linear | MVP yang dinilai |
| **Tier 2** | Dirancang, belum dibangun | Layar 5–9 | Rencana finalis |
| **Tier 3** | Roadmap | Layar 10–14 | Potensi pasca-kompetisi |

Ini bukan siasat menghindari aturan. Ini juga jawaban produk yang benar untuk permintaan
"jangan meribetkan user" - dan bagian 2 menjelaskan kenapa.

---

## 2. Use case: siapa yang membuka ini, kapan, dan untuk apa

Seluruh bentuk antarmuka ini diturunkan dari satu situasi konkret, bukan dari daftar fitur.

> **Bu Rina, pemilik toko fesyen mikro.** Literasi digital sedang. Membuka aplikasi ini
> **malam hari setelah tutup toko, di HP Android, dalam keadaan lelah**, untuk satu pertanyaan:
> *"besok saya harus benahi apa?"* Frekuensi: mingguan sampai bulanan, saat ulasan menumpuk.

Empat konsekuensi yang mengikat seluruh rancangan:

1. **Mobile-first, bukan mobile-friendly.** Layar utamanya HP. Prototipe default dibuka pada
   lebar HP; tombol "Layar lebar" ada hanya untuk memudahkan pemeriksaan desain.
2. **Satu layar, satu keputusan.** Bukan konsol dengan sepuluh widget. Setiap Action Card adalah
   satu keputusan yang bisa diterima atau ditolak.
3. **Teks minimum 16px, tidak ada istilah teknis.** Bukan "confidence 0,86" tetapi "cukup yakin".
4. **Kedalaman disembunyikan satu ketukan.** Bukti lengkap ada, tetapi di balik panel - tidak
   memenuhi layar pertama.

### 2.1 Jobs-to-be-done, dan tier mana yang menjawabnya

| Ritme | Pertanyaan pengguna | Dijawab oleh | Tier |
| --- | --- | --- | --- |
| Mingguan | "Besok saya benahi apa?" | Action Card terprioritas + bukti | **1** |
| Mingguan | "Kenapa saya harus percaya angka ini?" | Kutipan asli, skor kualitas data, pembanding kategori | **1** |
| Mingguan | "Boleh saya tanya sendiri ke datanya?" | Tanya jawab ter-ground | **1** |
| Bulanan | "Yang saya perbaiki bulan lalu berhasil tidak?" | Papan tindakan + sebelum/sesudah | 2 |
| Bulanan | "Ada masalah baru muncul?" | Tren antarperiode | 2 |
| Sesekali | "Bagaimana menunjukkan ini ke pemilik/staf?" | Laporan &amp; ekspor, tim &amp; peran | 2 / 3 |
| Terus-menerus | "Bisa tidak saya berhenti unggah manual?" | Koneksi marketplace | 3 |

**Tier 1 menjawab seluruh ritme mingguan - pekerjaan yang paling sering dilakukan.** Ritme
bulanan butuh data lintas sesi, yang secara teknis maupun aturan berada di luar MVP. Jadi
pemisahan tier bukan kompromi: ia mengikuti frekuensi pekerjaan nyata pengguna.

### 2.2 Kenapa "SaaS penuh" justru berbahaya bagi pengguna ini

Kalau seluruh 14 layar dijadikan MVP, Bu Rina membuka aplikasi dan bertemu ruang kerja, pemilih
toko, papan kanban, dan grafik tren - sebelum sempat bertanya "besok benahi apa?". Untuk
pengguna berliterasi digital sedang di HP pada malam hari, itu menambah langkah tanpa menambah
jawaban. Blueprint bagian 5.1 bahkan mencatat Bu Rina **tidak membutuhkan** dashboard tren
kompleks dan multi-toko.

Maka aturan lomba dan kebutuhan pengguna menunjuk arah yang sama, dan rancangan ini mengikuti
keduanya sekaligus.

---

## 3. Prinsip desain yang tidak boleh hilang saat tampilan dipercantik

Bagian ini ditujukan untuk pengerjaan UI/UX lanjutan. Tampilannya boleh berubah total; enam hal
berikut tidak boleh ikut hilang, karena masing-masing menopang klaim produk.

1. **Angka dan kutipan selalu monospace, narasi selalu sans.** Begitu pengguna melihat huruf
   mesin ketik, ia tahu itu keluaran hitungan atau rekaman apa adanya - bukan karangan sistem.
   Ini janji produk yang dinaikkan ke tingkat tipografi.
2. **Warna tidak pernah jadi satu-satunya penanda.** Setiap pill urgensi memuat teksnya.
   Pengguna buta warna harus mendapat informasi yang sama.
3. **Abu-abu untuk "tidak yakin", bukan merah.** Abstain bukan error. Merah untuk abstain akan
   terbaca sebagai kegagalan sistem, padahal itu perilaku yang benar.
4. **Sistem tidak pernah menandai keputusan sendiri.** Terima/Tolak/Simpan selalu kosong sampai
   manusia menekan. Tidak ada status yang berubah otomatis.
5. **Tidak ada klaim tanpa kutipan.** Jika bukti tidak ditemukan, yang tampil adalah "data belum
   cukup" - bukan kalimat yang terdengar meyakinkan tanpa dasar.
6. **Satu-satunya momen bergerak adalah checklist pemrosesan.** Animasi lain menambah beban
   kognitif tanpa menambah informasi.

---

## 4. Arsitektur informasi

### 4.1 Tier 1 - dua permukaan, alur linear di dalam dashboard

```
Halaman pemasaran (#/)  ──"Mulai Analisis"──►  Dashboard (#/analisis)

Dashboard:  Unggah  →  Memproses  →  Hasil ─┬─ Hasil        ⇄ Panel Bukti
                                            ├─ Detail
                                            ├─ Tanya Jawab
                                            └─ Roadmap
                                                    ↓
                                            "Analisis baru"
```

Halaman pemasaran dan fitur analisis **dipisahkan menjadi dua alamat**. Sebelumnya keduanya satu
halaman dan tombol "Mulai" hanya menggulir ke panel unggah di bawah hero. Pemisahan ini bukan
soal kerapian: halaman pemasaran perlu panjang dan bersuara, sementara layar kerja perlu pendek
dan diam, dan menyatukannya memaksa kompromi yang merugikan keduanya. Pengguna yang kembali juga
tidak lagi harus melewati materi promosi setiap kali ingin bekerja.

Tab hasil baru muncul **setelah** ada hasil - sebelum itu tidak ada apa pun untuk dijelajahi.
Pemecahan menjadi empat tab menjaga tab Hasil tetap pendek: peluang dan sebaran aspek berguna
saat pemilik toko sedang menyusun promosi, bukan saat ia memutuskan apa yang harus dibenahi
besok pagi.

Tetap tidak ada halaman pengaturan, akun, maupun riwayat. Panel bukti adalah *lembar* di atas
layar hasil, bukan halaman terpisah - posisi gulir pengguna tidak hilang.

### 4.2 Tier 2 - navigasi mulai muncul

```
Ruang Kerja ─┬─ Unggah & Analisis → Hasil ⇄ Panel Bukti
             ├─ Papan Tindakan → detail tindakan
             ├─ Tren & Perbandingan
             └─ Laporan & Ekspor
```

### 4.3 Tier 3 - produk multi-pengguna

```
Masuk → Pilih Toko → Ruang Kerja ─┬─ (seluruh Tier 2)
                                  ├─ Koneksi Marketplace
                                  ├─ Tim & Peran
                                  ├─ Langganan
                                  └─ Tata Kelola & Audit
```

---

## 5. Spesifikasi layar

Nomor layar sama dengan penomoran di prototipe.

### Tier 1 - sudah berfungsi

| # | Layar | Isi | Fitur yang tampil |
| --- | --- | --- | --- |
| 0 | **Halaman pemasaran** | Hero, pita marketplace, cara kerja, tiga fitur inti, CTA penutup. Tidak memuat satu pun kontrol analisis | - |
| 1 | **Unggah** | Kategori produk, lalu empat cara masuk data (tempel / berkas / **tangkapan layar** / data contoh), pemetaan kolom, tabel pratinjau, catatan privasi | ING-01, ING-03, ING-04, ING-07, ING-09, **ING-10** |
| 2 | **Memproses** | Bilah progres + checklist bertahap empat tahap | Indikator NLP-01, RET-01, ACT-01 |
| 3a | **Hasil** | Ringkasan → skor kualitas data → Action Card → pembanding kategori → kotak tanya | ACT-01, ING-05, FUS-01, BEN-01, UX-01 |
| 3b | **Detail** | Peluang → temuan foto (bila ada) → sebaran aspek | OPP-01, VIS-01 |
| 3c | **Tanya Jawab** | Percakapan ber-sitasi, pertanyaan yang disarankan, kotak tulis menempel di bawah | QNA-01 |
| 3d | **Roadmap** | Kemampuan yang belum ada beserta ALASAN teknisnya | - |
| 4 | **Panel Bukti** | Kutipan lengkap dengan rating &amp; tanggal, bukti visual, alasan prioritas, risiko jika keliru, tombol keputusan | RET-01, VIS-01 |

**Urutan bagian pada tab Hasil mengikuti urutan pertanyaan pengguna**, bukan urutan pipeline
teknis: apa ringkasnya → seberapa layak dipercaya → apa yang harus dikerjakan → bagaimana
dibanding yang lain → boleh saya tanya sendiri.

Layar Roadmap adalah bagian dari produk, bukan dokumentasi yang tercecer ke antarmuka. Ia ada
supaya batas versi ini terbaca sebagai keputusan yang disengaja - lengkap dengan angka
pengujiannya - bukan sebagai kekurangan yang kebetulan tidak sempat dibahas.

### Tier 2 - dirancang, belum dibangun

| # | Layar | Kenapa belum di MVP |
| --- | --- | --- |
| 5 | **Ruang Kerja** | Baru bermakna setelah ada lebih dari satu sesi analisis; di MVP hanya menambah langkah |
| 6 | **Papan Tindakan** | Butuh penyimpanan lintas sesi (di luar batas MVP). Memuat peringatan sebab-akibat eksplisit |
| 7 | **Tren &amp; Perbandingan** | Rulebook menyebut dashboard analitik lanjutan sebagai contoh over-scope; tren dari satu batch juga menyesatkan secara statistik |
| 8 | **Laporan &amp; Ekspor** | Menjawab persona Admin Toko; di Tier 1 tangkapan layar sudah memadai |
| 9 | **Unggah Foto Massal** | Menunggu model visual lolos go/no-go gate |

### Tier 3 - roadmap

| # | Layar | Catatan |
| --- | --- | --- |
| 10 | **Masuk &amp; Multi-toko** | Otentikasi kompleks disebut rulebook sebagai backend terlalu rumit. Masuk lewat nomor WhatsApp dipilih karena lebih akrab bagi UMKM daripada email |
| 11 | **Koneksi Marketplace** | Bergantung ketersediaan API resmi Shopee/Tokopedia - ditulis sebagai rencana, tidak pernah diklaim berfungsi |
| 12 | **Tim &amp; Peran** | Batas peran mengunci satu prinsip: yang menerima rekomendasi tetap pemilik keputusan |
| 13 | **Langganan** | Paket gratis sengaja cukup menjawab pertanyaan inti UMKM mikro, bukan demo lumpuh |
| 14 | **Tata Kelola &amp; Audit** | Tombol hapus data dan larangan melatih model dari data pengguna sudah berlaku sejak Tier 1 |

---

## 6. Peta seluruh fitur ke layar

Diambil dari inventaris fitur blueprint bagian 8. Kolom terakhir menunjukkan apakah fitur itu
sudah berjalan di repo hari ini.

| ID | Fitur | Layar | Tier | Berjalan? |
| --- | --- | --- | --- | --- |
| ING-01 | Ingestion teks + foto opsional | 1 | 1 | Teks ya, foto belum |
| ING-03 | Tempel teks langsung | 1 | 1 | Ya |
| ING-04 | Dataset contoh bawaan | 1 | 1 | Ya |
| ING-05 | Skor kualitas data | 3 | 1 | Ya |
| ING-06 | Buang duplikat/kosong | 1 (senyap) | 1 | Ya |
| ING-07 | Deteksi + pemetaan kolom manual | 1 | 1 | Ya |
| ING-08 | Impor folder foto massal | 9 | 2 | Belum |
| ING-09 | Pemrosesan sesi saja | 1 | 1 | Ya |
| GOV-01 | Redaksi PII | 1 (senyap) | 1 | Ya |
| GOV-02 | Model &amp; dataset card | - (repo) | 1 | Ya |
| GOV-03 | Jejak audit penuh | 14 | 3 | Belum |
| GOV-04 | Akses berbasis peran | 12 | 3 | Belum |
| NLP-01 | Klasifikasi aspek + sentimen | 3 | 1 | Ya |
| NLP-02 | Normalisasi slang/typo | - (pipeline) | 1 | Ya |
| NLP-03/04 | Clustering &amp; isu berulang | 7 | 2 | Belum |
| VIS-01 | Klasifikasi visual + abstain | 3, 4 | 1 | Menunggu gate |
| VIS-02 | Deteksi foto buram | 9 | 1–2 | Belum |
| FUS-01 | Deteksi kontradiksi teks–foto | 3, 4 | 1 | Ya |
| RET-01 | Retrieval bukti | 3, 4 | 1 | Ya |
| ACT-01 | Skoring prioritas + Action Card | 3 | 1 | Ya |
| BEN-01 | Pembanding kategori | 3 | 1 | Ya |
| QNA-01 | Tanya jawab ter-ground | 3 | 1 | Ya |
| OPP-01 | Temuan kekuatan | 3 | 1 | Ya |
| OPP-02 | Kutipan positif untuk marketing | 8 | 2 | Belum |
| ATR-01 | Pelacakan tindakan | 5, 6 | 2 | Belum |
| EXP-01 | Ekspor PDF/CSV | 8 | 2 | Belum |
| MON-01 | Log terstruktur tanpa PII | - (ops) | 1 | Ya |
| MON-02 | Pemantauan drift | - (ops) | 2 | Belum |
| UX-01 | Halaman hasil terpadu | 3 | 1 | Ya |
| UX-02 | Dashboard tren historis | 7 | 2 | Belum |
| UX-03 | Multi-toko / ruang kerja | 5, 10 | 2–3 | Belum |

---

## 7. Inventaris komponen

Komponen bertanda ✅ sudah ada di [`apps/web/src/components/index.jsx`](../../apps/web/src/components/index.jsx).

| Komponen | Fungsi | Aturan yang mengikat |
| --- | --- | --- |
| ✅ `ActionCard` | Objek utama produk - satu keputusan | Pill urgensi wajib bertulisan; tombol keputusan selalu kosong di awal |
| ✅ `EvidenceStrip` | Kutipan verbatim + rating + tanggal | Kutipan monospace, tidak pernah diparafrase |
| ✅ `EvidenceDrawer` | Panel bukti lengkap | Fokus pindah ke judul saat dibuka; Esc menutup |
| ✅ `Narrative` | Kalimat dengan angka disorot monospace | Angka tidak boleh sans |
| ✅ `DataQualityCard` | Skor + catatan pembatas | Skor tidak pernah tampil tanpa catatan |
| ✅ `OpportunitySection` | Temuan kekuatan | Hijau; menyatakan bukan generator iklan |
| ✅ `VisualFindings` | Temuan foto termasuk abstain | Abstain abu-abu, tidak merah |
| ✅ `BenchmarkCard` | Pembanding kategori | Wajib menyebut "bukan data pesaing" |
| ✅ `QnABox` | Tanya jawab + pertanyaan saran | Menampilkan penolakan apa adanya |
| ✅ `ColumnMapper` / `PreviewTable` | Pemetaan kolom &amp; pratinjau | Hanya kolom teks yang wajib |
| `WorkspaceCard` | Ringkas status toko | Tier 2 |
| `ActionBoard` | Kanban tindakan | Tier 2 - wajib peringatan sebab-akibat |
| `TrendChart` | Grafik antarperiode | Tier 2 - wajib menampilkan n per titik |
| `ReportBuilder` | Pemilih isi laporan | Tier 2 - wajib peringatan UU PDP |
| `ConnectorRow` | Sambungan marketplace | Tier 3 |
| `RoleRow` / `PlanCard` / `AuditRow` | Peran, paket, jejak | Tier 3 |

---

## 8. Kesesuaian dengan tujuan lomba

Tema: **AI for the Backbone of the Economy**. Subtema dipilih: **Smart Commerce** - AI di sisi
konsumen dan operasional penjualan, mencakup analisis perilaku konsumen.

| Kriteria (bobot) | Bagaimana rancangan ini menjawab |
| --- | --- |
| **Implementasi Teknologi &amp; Kematangan Arsitektur (25%)** | Layar 3 menampilkan keluaran lima lapisan (teks, visual, fusi, retrieval, aksi) dalam satu halaman terpadu. Banner "mode sederhana" membuat *graceful degradation* terlihat pengguna, bukan tersembunyi di log. Rulebook menekankan **proporsional**, bukan canggih - pemisahan tier adalah bukti proporsionalitas itu |
| **Orisinalitas &amp; Dampak Sosial (20%)** | Action Card adalah novelty inti: jembatan dari klasifikasi ke keputusan bisnis. Dampak sosialnya melekat di bentuk antarmuka - teks 16px, tanpa jargon, mobile-first, untuk pengguna berliterasi digital sedang. Ini penerapan langsung semangat *#EncloseTheGap* |
| **Kesiapan MVP (15%)** | Yang dikumpulkan tetap alur linear empat layar, satu input → satu output AI. Sembilan layar sisanya ditandai jelas sebagai rancangan/roadmap dan **tidak ada di repo produk** |
| **Video Promosi (15%)** | Video hanya boleh menampilkan fitur yang benar-benar berjalan. Kolom "Berjalan?" pada bagian 6 adalah daftar sah isi video - badge hijau di prototipe menandai batas itu |
| **Kualitas Proposal &amp; Proses (15%)** | Setiap layar disertai alasan desain di prototipe, dan setiap keputusan merujuk bagian blueprint atau rulebook yang bersangkutan |
| **Relevansi Tema (10%)** | UMKM adalah punggung ekonomi; ulasan pelanggan adalah data perilaku konsumen. AI dipakai di tempat yang memang membutuhkannya (memahami bahasa informal), bukan dipaksakan - perhitungan prioritas justru sengaja deterministik |
| **Business Value &amp; Governance (bonus 3,5%)** | Layar 13 memuat model freemium yang dirancang sejak riset; Layar 14 memuat tata kelola data. Keduanya ditandai roadmap, tidak diklaim berfungsi |

---

## 9. Yang sengaja tidak ada

Ketiadaan berikut adalah keputusan, bukan kekurangan yang belum sempat dikerjakan.

- **Tidak ada generator materi iklan.** Temuan positif menyajikan sinyal dan kutipannya;
  pemiliknya yang menyusun promosi. Menulis iklan otomatis mengubah produk ini menjadi alat
  pemasaran yang klaimnya tidak dapat diverifikasi.
- **Tidak ada skor kepuasan tunggal.** Satu angka "skor toko 78/100" mudah dipahami tetapi
  menyembunyikan aspek mana yang bermasalah - persis informasi yang dibutuhkan untuk bertindak.
- **Tidak ada eksekusi otomatis.** Sistem tidak pernah mengubah halaman produk, membalas
  pelanggan, atau menandai tindakan selesai.
- **Tidak ada perbandingan dengan toko tertentu.** Yang ditampilkan agregat kategori dari data
  publik, dan istilahnya "rata-rata kategori", bukan "pesaing".
- **Tidak ada slot foto yang belum berfungsi.** Model visual belum lolos gate, jadi slotnya
  ditandai nonaktif dengan alasannya - tombol mati lebih merusak kepercayaan daripada
  ketiadaan tombol.

---

## 10. Untuk pengerjaan UI/UX lanjutan

Yang bebas diubah: tata letak, skala tipografi, bentuk kartu, ilustrasi, mikro-interaksi,
palet turunan, dan seluruh gaya visual.

Yang perlu dipertahankan: enam prinsip pada bagian 3, pemisahan tier pada bagian 1, dan urutan
bagian Layar 3 pada bagian 5. Ketiganya menopang klaim produk maupun posisi terhadap rubrik.

Ketika token warna atau tipografi berubah, ubah di
[`apps/web/src/styles/tokens.css`](../../apps/web/src/styles/tokens.css) lebih dulu, lalu
salin ke prototipe - bukan sebaliknya. Satu sumber kebenaran, supaya dokumen dan aplikasi tidak
perlahan berbeda.
