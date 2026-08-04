# AIC Smart Commerce Research Dossier (v6)


## AIC SMART COMMERCE RESEARCH DOSSIER

Tema: AI for the Backbone of the Economy — Subtema: Smart Commerce

Disusun untuk: AI Innovation Challenge (AIC) COMPFEST 18

Tahap: Riset (bukan proposal final, bukan produk jadi)

Tanggal penyusunan: 4 Agustus 2026



## 1. Executive Summary

Dokumen ini adalah dossier riset tahap awal untuk subtema Smart Commerce pada AIC COMPFEST 18, disusun murni untuk kebutuhan eksplorasi masalah, validasi bukti, dan pemetaan ide — bukan proposal final maupun spesifikasi produk. Seluruh temuan didasarkan pada kombinasi data resmi Indonesia (BPS, Bank Indonesia, OJK, Kementerian Perdagangan, KPPU, BPKN), laporan industri (Google-Temasek-Bain e-Conomy SEA 2025), dan literatur akademik yang dapat diverifikasi melalui pencarian web pada Agustus 2026.

Setelah menelusuri 15 masalah potensial di ranah Smart Commerce, menyusun 9 kandidat ide, dan melakukan weighted decision matrix terhadap 15 kriteria, dossier ini merekomendasikan satu ide utama untuk didalami lebih lanjut: "InsightUlasan" — mesin AI aspect-based sentiment & insight bisnis yang mengubah ulasan/chat pelanggan berbahasa Indonesia informal (campuran bahasa daerah, slang, singkatan) milik UMKM menjadi rekomendasi keputusan komersial terprioritas (restock, perbaikan kualitas, penyesuaian harga, highlight promosi).

Pemilihan ini didasarkan pada kombinasi bukti yang relatif kuat: (a) 4,40 juta unit usaha e-commerce di Indonesia pada 2024 didominasi usaha mikro [FACT, BPS 2024]; (b) UMKM menghadapi keterbatasan literasi digital dan sumber daya untuk mengolah data pelanggan [RESEARCH FINDING]; (c) tersedia dataset Bahasa Indonesia yang dapat diakses publik (PRDECT-ID, IndoBERT sentiment corpus, ulasan Tokopedia) [FACT]; (d) riset akademik menunjukkan model berbasis IndoBERT mencapai akurasi hingga 97% untuk klasifikasi sentimen ulasan e-commerce Indonesia, jauh melampaui pendekatan rule-based [RESEARCH FINDING, perlu verifikasi metodologi lebih lanjut]; dan (e) belum ditemukan produk yang secara spesifik menggabungkan aspect-based sentiment Bahasa Indonesia informal dengan output keputusan bisnis siap-pakai untuk UMKM skala mikro [INFERENCE berdasarkan penelusuran kompetitor terbatas].

Dua kandidat lain yang masuk final tiga besar berdasarkan weighted decision matrix (bagian 18) adalah "HargaCerdas" (asisten simulasi harga & margin untuk UMKM) dan "RekomenUMKM" (rekomendasi kategori/audiens untuk produk baru guna mengatasi cold-start). Ide "UlasanAsli" (deteksi ulasan tidak wajar) memiliki bukti masalah dan dampak sosial yang kuat namun tertahan di peringkat kelima akibat risiko ketersediaan dataset berlabel Bahasa Indonesia yang signifikan (bagian 12, 14, 18) - tetap didokumentasikan lengkap sebagai kandidat bernilai tinggi untuk eksplorasi lanjutan. Seluruh 15 masalah dan 9 ide beserta alasan eliminasi lima ide lain didokumentasikan pada bagian-bagian berikutnya, termasuk seluruh asumsi yang masih memerlukan validasi pengguna sebelum tahap pengembangan MVP.

Dokumen ini secara eksplisit TIDAK berisi kode program, wireframe, arsitektur produksi, maupun proposal kompetisi final. Bagian penutup "Research Confidence and Evidence Gaps" merangkum tingkat keyakinan setiap klaim dan daftar validasi yang wajib dilakukan sebelum ide dieksekusi.

CATATAN PEMBARUAN (4 Agustus 2026): setelah panitia memberikan klarifikasi resmi mengenai cakupan kustomisasi AI (bagian 2.9) yang secara eksplisit mengizinkan RAG, agentic workflow, tool calling, dan training model pendukung terintegrasi foundation model - bukan hanya fine-tuning parameter - dossier ini memperbarui arsitektur InsightUlasan menjadi hybrid multimodal: model pendukung terlatih untuk teks (fine-tuned IndoBERT/DistilBERT) DAN untuk foto ulasan (classifier ringan di atas vision encoder terlatih), diorkestrasi oleh foundation model via tool calling dengan RAG untuk grounding. Penambahan komponen visual ini bukan sekadar hiasan teknis: ulasan bergambar (foto barang rusak, salah kirim, tidak sesuai deskripsi) sangat umum di marketplace Indonesia dan merupakan sinyal yang terlewat sepenuhnya oleh pendekatan text-only pada draf sebelumnya - lihat bagian 15 dan 21 untuk detail lengkap.

CATATAN PEMBARUAN v3 (4 Agustus 2026): bagian baru 21A "Technology Frontier Scan" ditambahkan untuk menjawab permintaan penelusuran teknologi AI global 2025-2026 yang dapat diadaptasi secara realistis untuk MVP. Tiga upgrade konkret: (1) foundation model orkestrator diganti dari LLM generik menjadi LLM regional Asia Tenggara berbobot-terbuka (SEA-LION/Sailor2/Cendol) agar benar-benar dapat dijalankan lokal tanpa API berbayar; (2) komponen visual diubah dari classifier terlatih (butuh anotasi manual yang datanya belum tersedia) menjadi zero-shot vision-language classification (CLIP/SigLIP) yang MENGHILANGKAN risiko data gap visual yang sebelumnya diidentifikasi; (3) lapisan retrieval RAG memakai BGE-M3, embedding multibahasa yang terbukti kuat pada bahasa low-resource. Weighted score InsightUlasan naik dari 8.22 menjadi 8.39 (bagian 18, 21A.4).

CATATAN PEMBARUAN v4 (4 Agustus 2026): bagian baru 21B menjawab kaji ulang kritis - computer vision DIUBAH dari "komponen wajib" menjadi arsitektur bertingkat (Tier 1 teks wajib untuk penyisihan; Tier 2 visual opsional; Tier 3 roadmap babak final), karena riset zero-shot CLIP yang ditemukan pada v3 terbukti hanya divalidasi pada domain industri/manufaktur, BUKAN foto ulasan konsumen - generalisasinya masih hipotesis. Dua fitur kreatif baru ditambahkan tanpa risiko teknis tambahan berarti: Tanya-Jawab interaktif atas ulasan (memanfaatkan ulang RAG yang sudah ada, sangat cocok untuk sesi Live Pitching) dan peer/category benchmarking (memanfaatkan ulang dataset publik yang sama sebagai baseline pembanding). Celah pada kriteria bonus Business Value dan Governance (3.5%) juga diisi dengan model adopsi freemium. Bagian 21B ditutup dengan audit kejujuran eksplisit tentang batas maksimal riset desk-research.

CATATAN PEMBARUAN v5 (4 Agustus 2026): tim secara eksplisit MEMUTUSKAN memakai computer vision, membalikkan rekomendasi "opsional" pada v4 (bagian 21B.1 direvisi - Tier 2 visual kini berstatus WAJIB untuk penyisihan, bukan lagi bonus). Keputusan ini dihormati sepenuhnya dan bukan diperdebatkan ulang; yang berubah dalam dossier adalah penanganan risikonya. Bagian baru 21B.6 menjawab pertanyaan konkret tim mengenai penggunaan Apify (platform scraping pihak ketiga) untuk memperoleh data foto ulasan riil dalam anggaran paket gratis $5/bulan: dikonfirmasi actor "Shopee Product Reviews Scraper" (zen-studio) mengekstrak foto ulasan asli (URL CDN) beserta teks dan rating, dengan estimasi ~250-300 foto ulasan riil dapat diperoleh dalam anggaran gratis - jauh melampaui syarat minimum 20-30 foto pada langkah validasi wajib (bagian 21B.2). Analisis legal (21B.6.3) menyimpulkan pendekatan ini WAJAR dan PROPORSIONAL untuk konteks riset kompetisi (data publik terlihat, volume kecil, dengan anonimisasi wajib) namun TIDAK dapat diklaim "100% aman" karena tidak ditemukan konfirmasi tertulis langsung dari Shopee/Tokopedia yang mengizinkan scraping secara eksplisit [PARTIALLY VERIFIED]. Yang PALING PENTING digarisbawahi: rencana akuisisi data ini menutup gap AKSES DATA, bukan gap PEMBUKTIAN PERFORMA - apakah model zero-shot CLIP benar-benar bekerja baik pada foto ulasan Indonesia TETAP belum terbukti sampai tim menjalankan validasi nyata (bagian 21B.2 Langkah 4, kini menjadi gerbang wajib). Skor decision matrix InsightUlasan (bagian 18) SENGAJA TIDAK dinaikkan pada revisi ini - rencana data yang lebih baik bukan bukti performa model yang lebih baik, dan menaikkan skor tanpa hasil validasi nyata akan bertentangan dengan prinsip audit kejujuran yang menjadi fondasi dossier ini sejak v4.

CATATAN PEMBARUAN v6 (4 Agustus 2026): menjawab objection kritis yang lebih tajam dari "kenapa pakai AI" - yaitu "kenapa pakai pipeline serumit ini, bukan langsung prompt LLM API (GPT-4o/Claude/Gemini) yang sudah otomatis dan berkualitas tinggi untuk ekstrak insight dari ulasan?" Bagian baru 13.5 menjawab ini secara jujur dan eksplisit menggunakan perbandingan enam sumbu (bukan hanya satu argumen kualitas): dossier ini TIDAK mengklaim pipeline yang diusulkan menghasilkan insight yang secara kualitatif lebih unggul dari zero-shot LLM API murni - klaim itu belum diuji dan tidak dibuat. Pertahanan utama bersifat rules-compliance dan operasional: (1) zero-shot API call murni secara eksplisit GAGAL memenuhi syarat kustomisasi wajib rulebook sesuai kata-kata klarifikasi resmi panitia sendiri; (2) pipeline lokal jauh lebih reproducible oleh juri (tidak butuh API key/kredit pihak ketiga saat cross-check); (3) jauh lebih murah dioperasikan pada skala ribuan ulasan sesuai model bisnis freemium UMKM mikro (bagian 21B.4). Ditambahkan pula rencana pengujian konkret (bandingkan konsistensi output LLM API vs classifier fine-tuned pada sampel identik) untuk mengubah argumen ini dari klaim menjadi bukti sebelum submission. "Judge objection (2)" pada bagian 19.1 diperbarui dengan jawaban singkat versi lisan untuk sesi tanya-jawab/Live Pitching.


## 2. Interpretasi Rulebook

Bagian ini merangkum interpretasi tim terhadap Rulebook AIC COMPFEST 18 (file "AIC RULEBOOK", 28 halaman, terakhir dimodifikasi 4 Agustus 2026) sebagai sumber aturan utama. Setiap poin merujuk langsung pada isi rulebook agar keputusan riset dan pemilihan ide tidak menyimpang dari batasan kompetisi.


### 2.1 Definisi Tema "AI for the Backbone of the Economy"

Tema AIC tahun ini menyoroti tiga tahap utama yang dilalui setiap produk sebelum sampai ke konsumen: diproduksi, didistribusikan, dan dijual. Rulebook secara eksplisit menyebut tiga area rantai pasok pasca-produksi primer sebagai "backbone" ekonomi Indonesia: Smart Manufacturing (pabrik), Smart Logistics (gudang dan distribusi), dan Smart Commerce (toko dan pasar). Tujuannya adalah menggali potensi AI untuk mentransformasi rantai nilai bisnis Indonesia yang menghadapi tantangan nyata: inefisiensi produksi, tingginya biaya logistik, dan meningkatnya ekspektasi konsumen digital.


### 2.2 Batasan Subtema Smart Commerce

Smart Commerce didefinisikan rulebook sebagai "penerapan AI di sisi konsumen, sales operasional, serta transaksi komersial" — mencakup pengalaman pelanggan, personalisasi layanan, analisis perilaku konsumen, dan optimasi penjualan/pemasaran (sesuai keterangan pada slide subthemes). Ini berbeda tegas dari Smart Manufacturing (proses produksi dan operasional pabrik: otomatisasi, predictive maintenance, quality control) dan Smart Logistics (pergudangan, distribusi, rantai pasok: visibilitas, akurasi perencanaan, efisiensi pergerakan barang).


### 2.3 Masalah yang Relevan dengan Smart Commerce

Berdasarkan definisi di atas, masalah yang relevan adalah yang terjadi pada titik interaksi konsumen-penjual-transaksi: penemuan produk, kepercayaan transaksi, personalisasi, layanan pelanggan, penetapan harga/promosi, retensi pelanggan, dan operasi penjualan lintas kanal (marketplace, sosial, live commerce). Masalah yang secara dominan terjadi pada pergerakan fisik barang (rute pengiriman, pergudangan) atau proses produksi (kualitas manufaktur, jadwal produksi pabrik) berada di luar cakupan subtema ini meskipun disebut dalam tema besar.


### 2.4 Ketentuan Teknis MVP

Rulebook menetapkan batasan ruang lingkup MVP secara eksplisit pada bagian "Teknis Penyisihan" agar penilaian dapat direproduksi secara lokal. MVP hanya wajib mencakup: (1) alur interaksi inti — menerima satu input tunggal dari pengguna dan menampilkan output dari AI, tanpa fitur pelengkap seperti dashboard analitik lanjutan, sistem otentikasi kompleks, atau riwayat penggunaan; (2) pemrosesan interaksi sinkron di backend, tanpa background jobs, pipeline logging otomatis, atau database terdistribusi — API/sistem lokal cukup dapat dijalankan sesuai README.md menggunakan docker compose; (3) fungsionalitas inferensi inti (core inference) dengan parameter statis saat demonstrasi, tanpa auto-tuning, bulk testing script, atau feedback loop otomatis pada repository tahap penyisihan.


### 2.5 Batasan Frontend, Backend, dan Model AI

- Frontend: hanya alur interaksi inti (input tunggal → output AI). Dashboard analitik tingkat lanjut, autentikasi kompleks, dan halaman riwayat TIDAK wajib pada tahap penyisihan.
- Backend: hanya pemrosesan sinkron. Background jobs, automated data logging pipeline, dan database terdistribusi TIDAK wajib.
- Model AI: fokus pada core inference dengan parameter statis. Auto-tuning, bulk testing scripts, dan feedback loop otomatis TIDAK wajib pada tahap penyisihan.

Implikasinya bagi tahap riset: ide yang dipilih harus dapat didemonstrasikan melalui satu alur input-output yang jelas dan sempit, bukan sistem multi-fitur yang kompleks.


### 2.6 Ketentuan Reproducibility Lokal

Setiap tim wajib menyediakan repository GitHub berstatus publik dengan README.md yang memuat setup guide jelas dan docker compose, sehingga panitia dapat menjalankan aplikasi secara lokal untuk verifikasi (cross-check) kebenaran video proof of work. Video proof of work wajib menunjukkan status MVP paling akhir dan flow program yang sudah maupun belum sepenuhnya berjalan (working/buggy), dengan larangan keras melakukan cut/editing selain percepatan (fast-forward) untuk menunggu proses loading. Implikasi riset: ide yang bergantung pada infrastruktur cloud kompleks, hardware khusus yang mahal, atau layanan pihak ketiga yang sulit direplikasi oleh juri berisiko tinggi pada kriteria reproducibility.


### 2.7 Ketentuan Dataset

Dataset boleh berasal dari sumber publik yang telah tersedia sebelumnya maupun data sintetik yang dibuat bertanggung jawab. Penggunaan model (baik karya pihak luar maupun bukan), arsitektur sistem, dan fitur wajib dijelaskan bersamaan proses preprocessing-nya selama periode lomba. Implikasi riset: tahap studi kelayakan dataset (bagian 14) menjadi krusial — ide yang tidak memiliki dataset publik yang dapat diverifikasi atau tidak dapat disintesis secara wajar berisiko gugur pada kriteria "Kesiapan MVP" dan "Implementasi Teknologi".


### 2.8 Ketentuan Penggunaan API dan Pretrained Model

Rulebook secara eksplisit mengizinkan penggunaan model API dan pretrained model, dengan syarat "model wajib di-fine-tune sesuai dengan inovasi fitur per tim" (disebutkan dua kali, pada Ketentuan Khusus poin 10 dan Teknis Penyisihan poin 2). Ini adalah aturan paling menentukan bagi pemilihan ide dan metode AI.


### 2.9 Ketentuan Kustomisasi Model atau Sistem AI

DIPERBARUI - panitia telah memberikan klarifikasi resmi tertulis (diterima 4 Agustus 2026) yang menggantikan interpretasi awal pada draf sebelumnya [OFFICIAL CLARIFICATION, bukan lagi ASUMSI]. Tujuan utama ketentuan "pretrained model wajib di-fine-tune sesuai inovasi fitur per tim" adalah mewajibkan adanya kustomisasi nyata, sehingga peserta tidak sekadar melakukan zero-shot API call terhadap model mentah. Panitia secara eksplisit mengizinkan pemenuhan syarat ini melalui salah satu atau kombinasi dari: (1) parameter fine-tuning murni seperti LoRA/QLoRA; (2) Retrieval-Augmented Generation (RAG); (3) Agentic Workflow/AI Agents; (4) Tool Calling/Function Calling; (5) training model pendukung yang terintegrasi dengan foundation model. Tim dipersilakan memilih pendekatan yang paling optimal dan sesuai batasan MVP inovasi masing-masing - tidak wajib fine-tuning parameter penuh apabila metode adaptasi lain lebih tepat dan tetap menunjukkan kontribusi teknis yang dapat dipertanggungjawabkan.

Implikasi bagi InsightUlasan (ide utama, bagian 20-21): klarifikasi ini membuka ruang arsitektur hybrid yang lebih kaya dan sudah diperbarui pada dossier ini - kombinasi model pendukung terlatih (fine-tuned IndoBERT/DistilBERT untuk teks, dan classifier ringan di atas vision encoder untuk foto ulasan) yang diorkestrasi oleh foundation model (LLM) melalui tool calling, dengan RAG untuk menjaga jawaban ter-ground pada kutipan/temuan asli. Arsitektur ini secara bersamaan memenuhi rute (2), (3)/(4), dan (5) di atas - lihat detail pembaruan pada bagian 15, 16.1, 19.1, dan 21.


### 2.10 Deliverables Tahap Penyisihan

- Link repository source code GitHub (visibility public) dengan README.md berisi setup guide jelas dan docker compose; commit/push terakhir sebelum 25 Agustus 2026 pukul 23.55 WIB, dengan pesan commit mengikuti konvensi Conventional Commits (feat/fix/refactor).
- Link video proof of work (maksimal 7 menit, YouTube unlisted, format nama "COMPFEST 18 AIC: PROOF OF WORK – [Nama Tim] – [Nama Proyek]").
- Link video promosi karya inovasi (maksimal 5 menit, MP4 minimal 720p, YouTube public, format nama "COMPFEST 18 AIC: [Nama Tim] – [Nama Proyek]").
- Proposal PDF maksimal 20 halaman (di luar cover, daftar pustaka, lampiran) memuat: nama kelompok & judul inovasi, latar belakang, tujuan & manfaat, metodologi (alur dataset, alur pengembangan model per fitur, alur integrasi model ke environment kode), metode pendukung lain, dan kesimpulan.
- Deadline seluruh berkas: 25 Agustus 2026 pukul 23.55 WIB melalui situs COMPFEST.


### 2.11 Seluruh Kriteria Penilaian dan Bobotnya (Tahap Penyisihan)

| Kriteria | Bobot | Fokus Utama |
| --- | --- | --- |
| Implementasi Teknologi & Kematangan Arsitektur | 25% | Kesesuaian & proporsi pemilihan teknologi, fokus core inference, modularitas AI/backend/frontend, dokumentasi teknis |
| Orisinalitas dan Dampak Sosial | 20% | Keunikan, pendekatan baru, relevansi konteks, urgensi masalah, kesesuaian kebutuhan pengguna & potensi global |
| Kesiapan Minimum Viable Product (MVP) untuk Babak Final | 15% | Ruang lingkup MVP tepat (tidak overbuilt/underbuilt), fungsionalitas inti cukup dievaluasi, arsitektur fleksibel untuk dikembangkan |
| Video Promosi | 15% | Kejelasan komunikasi masalah & solusi, storytelling proses perancangan, daya tarik bagi stakeholder |
| Kualitas Proposal & Proses Pengembangan | 15% | Struktur & kelengkapan sesuai ketentuan, kejelasan metodologi, argumentasi teknis berbasis data, cerita pengembangan iteratif |
| Relevansi dengan Tema | 10% | Kesesuaian inovasi dengan tema, penggunaan AI relevan (tidak dipaksakan) |
| Business Value dan Governance (BONUS) | 3.5% | Model bisnis/analisis kelayakan adopsi industri realistis, pertimbangan regulasi AI/etika/sistem cerdas bertanggung jawab |
| AIC Talks (BONUS) | 1.5% | Mengikuti dan mengisi presensi AIC Talks |
| TOTAL | 105% | — |

Catatan: rulebook yang dilampirkan hanya memuat rubrik penilaian tahap penyisihan. Rubrik penilaian babak final (hackathon, live pitching) belum tercantum dan menurut rulebook akan diinformasikan pada Technical Meeting Babak Final [NOT FULLY ACCESSIBLE — perlu diklarifikasi lebih lanjut].


### 2.12 Implikasi Setiap Kriteria Penilaian terhadap Pemilihan Ide

- Bobot terbesar (25%) pada Implementasi Teknologi & Kematangan Arsitektur mengarahkan pemilihan ide pada masalah yang punya jalur teknis AI yang jelas dan proporsional — bukan sekadar wrapper API, dan bukan pula arsitektur berlebihan.
- Bobot 20% pada Orisinalitas & Dampak Sosial mendorong ide yang punya novelty dapat dipertanggungjawabkan dan menjawab kebutuhan riil pengguna spesifik, bukan tren umum.
- Bobot 15% pada Kesiapan MVP menekankan pentingnya ide dengan satu alur input-output yang dapat didemonstrasikan penuh dalam waktu terbatas (17 Juni–25 Agustus 2026), bukan sistem multi-modul.
- Bobot 15% pada Video Promosi dan 15% pada Kualitas Proposal menuntut narasi masalah-solusi yang kuat dan metodologi berbasis data — sehingga ide dengan bukti kuantitatif Indonesia yang jelas lebih unggul saat dikomunikasikan.
- Bobot 10% Relevansi Tema menuntut kehati-hatian eksplisit membedakan Smart Commerce dari Smart Logistics/Manufacturing (lihat bagian 2.3).
- Bonus Business Value & Governance (3.5%) mengarahkan ide untuk menyertakan pertimbangan model bisnis dan etika AI sejak awal riset, bukan sebagai tempelan di akhir.


### 2.13 Risiko Diskualifikasi atau Ketidaksesuaian Scope

- Karya bukan orisinal tim, atau melanjutkan proyek yang sudah dikerjakan sebelum/luar periode penyisihan (17 Juni–25 Agustus 2026 pukul 23.55 WIB).
- Tidak melengkapi link video proof of work dan source code — panitia berhak mendiskualifikasi tim yang belum melengkapi kedua poin ini secara eksplisit.
- Repository tidak dapat diakses/dijalankan panitia (setup guide README.md tidak jelas, docker compose tidak berfungsi).
- Video di-cut/diedit di luar percepatan yang diizinkan, atau fitur yang ditampilkan di video promosi tidak ada di video proof of work.
- Menunjukkan latar belakang institusi pendidikan dalam bentuk apa pun selama perlombaan.
- Proyek yang secara substansial adalah masalah Smart Logistics atau Smart Manufacturing yang disamarkan sebagai Smart Commerce (risiko ketidaksesuaian scope, bukan pelanggaran administratif, namun berisiko menurunkan skor Relevansi Tema).
- Model API digunakan secara zero-shot tanpa fine-tuning atau bentuk kustomisasi lain sesuai fitur tim (berisiko pada penilaian Implementasi Teknologi meski belum tentu diskualifikasi eksplisit oleh rulebook).


### 2.14 Karakteristik Ide yang Kemungkinan Besar Dinilai Overbuilt

- Menyertakan dashboard analitik multi-halaman, sistem otentikasi/role management kompleks, atau riwayat penggunaan lengkap pada tahap penyisihan — padahal rulebook eksplisit membatasi frontend hanya pada input tunggal → output AI.
- Menyertakan background jobs, pipeline data logging otomatis, atau infrastruktur database terdistribusi yang tidak diperlukan untuk membuktikan inferensi inti.
- Menambahkan sistem auto-tuning model, bulk testing scripts, atau feedback loop otomatis yang menurut rulebook eksplisit tidak diminta pada tahap penyisihan.
- Mengintegrasikan banyak fitur AI sekaligus (multi-model orchestration kompleks) sehingga sulit dijelaskan dan direproduksi dalam waktu terbatas oleh juri.


### 2.15 Karakteristik Ide yang Kemungkinan Besar Dinilai Underbuilt

- Hanya membungkus panggilan API model besar (mis. satu prompt ke LLM komersial) tanpa fine-tuning, RAG, tool calling, atau bentuk kustomisasi lain yang dapat ditunjukkan sebagai kontribusi teknis tim.
- Masalah yang diangkat terlalu umum/generik ("AI membantu personalisasi") tanpa target pengguna, dataset, atau metrik evaluasi yang jelas — sehingga sulit menunjukkan kematangan arsitektur maupun orisinalitas.
- Tidak ada baseline atau ground truth yang bisa dibandingkan, sehingga klaim "AI meningkatkan X%" tidak dapat diuji juri secara lokal.
- Fitur yang didemonstrasikan di video promosi tidak konsisten dengan yang ada di video proof of work / repository — video promosi under-delivers relatif terhadap klaimnya.


## 3. Definisi dan Batas Smart Commerce

Smart Commerce, sebagaimana didefinisikan rulebook, adalah penerapan AI pada sisi konsumen, operasional penjualan (sales operation), dan transaksi komersial — mencakup personalisasi layanan, analisis perilaku konsumen, dan optimasi penjualan/pemasaran. Untuk kebutuhan riset, dossier ini memetakan Smart Commerce ke dalam 25 domain turunan yang diberikan sebagai kerangka acuan, dan secara aktif menghindari domain yang lebih dominan pada distribusi fisik (Smart Logistics) atau proses produksi (Smart Manufacturing).


### 3.1 Peta 25 Domain Smart Commerce

| No | Domain | Contoh Masalah Relevan yang Ditemukan dalam Riset Ini |
| --- | --- | --- |
| 1 | Customer experience | Navigasi platform sulit bagi konsumen lansia/disabilitas |
| 2 | Customer service | UMKM tidak sanggup membalas chat multi-kanal secara konsisten |
| 3 | Personalized commerce | Rekomendasi produk tidak relevan untuk toko baru/data minim (cold-start) |
| 4 | Consumer behavior intelligence | Ulasan & chat pelanggan tidak diolah menjadi insight actionable |
| 5 | Sales operation | UMKM sulit memprioritaskan follow-up prospek/leads |
| 6 | Retail operation | Toko kecil sulit menentukan bundling/restock berbasis data |
| 7 | E-commerce operation | Biaya platform berlapis menekan margin tanpa alat optimasi kanal |
| 8 | Marketplace seller operation | Penjual kesulitan bersaing dengan biaya marketplace 15-20% dari harga jual |
| 9 | Omnichannel commerce | Data pelanggan terfragmentasi antar WhatsApp, marketplace, media sosial |
| 10 | Social commerce | Interaksi penjualan di media sosial sulit dikonversi & dilacak |
| 11 | Live commerce | Volume tinggi chat real-time saat live streaming tidak terlayani |
| 12 | Marketing optimization | Promosi tidak tepat sasaran karena minim data segmentasi |
| 13 | Promotion effectiveness | UMKM tidak tahu efektivitas diskon terhadap margin & repeat order |
| 14 | Pricing and discount decision | UMKM meniru harga kompetitor tanpa memperhitungkan struktur biaya sendiri |
| 15 | Conversion optimization | Rasio kunjungan-ke-pembelian rendah tanpa alat diagnosis |
| 16 | Customer retention | Pelanggan berhenti membeli tanpa terdeteksi dini oleh penjual kecil |
| 17 | Churn prevention | Tidak ada sinyal dini kehilangan pelanggan berulang pada skala UMKM |
| 18 | Product discovery | Produk UMKM baru sulit ditemukan di tengah katalog besar |
| 19 | Search and recommendation | Pencarian berbasis kata kunci gagal menangkap maksud belanja informal |
| 20 | Trust and safety dalam transaksi | Ulasan palsu/manipulatif merusak kepercayaan pembeli & penjual jujur |
| 21 | Fraud atau manipulation detection | Modus penipuan toko fiktif merugikan konsumen (Rp988 miliar/2025) |
| 22 | Accessibility dalam perdagangan digital | Penyandang tunanetra kesulitan berbelanja mandiri secara daring |
| 23 | Perlindungan konsumen | Dark pattern & biaya tersembunyi meningkat pada pengaduan BPKN |
| 24 | Digital inclusion untuk UMKM | 66 juta UMKM, baru ±30% memanfaatkan platform digital secara aktif |
| 25 | Pengambilan keputusan komersial untuk usaha mikro dan kecil | Minimnya alat analitik terjangkau untuk keputusan restock/promosi/harga |


### 3.2 Pembeda Tegas terhadap Smart Logistics dan Smart Manufacturing

| Subtema | Definisi Rulebook | Contoh yang DIKECUALIKAN dari riset ini |
| --- | --- | --- |
| Smart Manufacturing | Penerapan AI di proses pengolahan dan operasi pabrik (predictive maintenance, quality control, otomatisasi produksi) | Deteksi cacat produk di lini produksi, penjadwalan mesin pabrik, prediksi downtime peralatan |
| Smart Logistics | Penerapan AI di pergudangan, distribusi, dan pergerakan barang (visibilitas, akurasi perencanaan, efisiensi penggerakan barang) | Optimasi rute pengiriman, peramalan stok gudang, robotika pergudangan, manajemen armada |
| Smart Commerce (fokus riset ini) | Penerapan AI di sisi konsumen, sales operasional, dan transaksi komersial | — |

Beberapa masalah berada di zona abu-abu (mis. "prediksi permintaan" bisa relevan untuk Smart Commerce — memandu keputusan promosi/pricing penjual — maupun Smart Logistics — memandu pengisian gudang). Dossier ini hanya memasukkan sudut pandang Smart Commerce: prediksi permintaan sebagai input keputusan komersial penjual (restock/promosi), bukan sebagai optimasi rute atau gudang fisik.


## 4. Research Methodology

Riset ini mengikuti sepuluh tahap berurutan sesuai arahan: (1) Landscape Scanning, (2) Problem Discovery, (3) Evidence Validation, (4) Existing Solution Analysis, (5) Research Gap Identification, (6) AI Necessity Validation, (7) Dataset Feasibility, (8) Idea Generation, (9) Idea Comparison, (10) Deep Research terhadap ide terbaik. Tidak ada rekomendasi ide yang dikeluarkan sebelum tahap 1-7 selesai.

Sumber yang digunakan: (a) data resmi Indonesia - BPS, Bank Indonesia, OJK, Kementerian Perdagangan, KPPU, BPKN; (b) laporan industri - Google/Temasek/Bain e-Conomy SEA 2025; (c) literatur akademik yang dapat ditemukan melalui pencarian web terbuka (jurnal terindeks, preprint, konferensi) pada Agustus 2026; (d) dataset publik di Kaggle dan Hugging Face; (e) observasi produk kompetitor melalui situs resmi dan artikel media.


### 4.1 Keterbatasan Metodologis

- Riset dilakukan dalam satu sesi kerja berbasis pencarian web (desk research), TANPA wawancara pengguna langsung - seluruh temuan tentang perilaku UMKM/konsumen bersifat inferensi dari data sekunder dan wajib divalidasi melalui wawancara sebelum implementasi (lihat bagian 23).
- Akses ke database jurnal berbayar (Scopus, Web of Science, ScienceDirect penuh) tidak tersedia langsung; sitasi disusun dari abstrak, ringkasan, dan metadata yang dapat diverifikasi publik. Paper yang full text-nya tidak dapat diakses ditandai NOT FULLY ACCESSIBLE.
- Statistik 2025-2026 untuk beberapa indikator (mis. granular UMKM per subsektor Smart Commerce) belum dipublikasikan BPS secara lengkap; dossier menggunakan data terbaru yang tersedia (umumnya 2023-2025) dan menandainya secara eksplisit.
- Tidak ada eksperimen model atau prototipe teknis yang dibangun pada tahap ini - sesuai batasan eksplisit pengguna bahwa tahap ini hanya riset, bukan implementasi.


## 5. Indonesian Smart Commerce Landscape

Ekonomi digital Indonesia diproyeksikan mencapai sekitar USD 100 miliar Gross Merchandise Value (GMV) pada 2025, tumbuh 14% dari tahun sebelumnya, dan tetap menjadi ekonomi digital terbesar di Asia Tenggara, dengan proyeksi mencapai minimal USD 180 miliar pada 2030 [INDUSTRY REPORT, e-Conomy SEA 2025 - Google, Temasek, Bain]. Sektor e-commerce sendiri diproyeksikan tumbuh lebih dari 14% menjadi USD 71 miliar pada 2025 [INDUSTRY REPORT].

Dari sisi pelaku usaha, jumlah unit usaha e-commerce di Indonesia pada 2024 tercatat 4,40 juta unit, meningkat 15,3% dari tahun sebelumnya dan melonjak 86% dalam empat tahun terakhir, dengan mayoritas berasal dari kelompok usaha mikro [FACT/OFFICIAL STATISTICS, BPS - Statistik E-Commerce 2024]. Secara terpisah, Kementerian UMKM memperkirakan populasi UMKM mencapai sekitar 66 juta unit usaha pada 2025, menyumbang lebih dari 60% PDB nasional dan menyerap sekitar 97% tenaga kerja [OFFICIAL STATISTICS, Kementerian Koperasi dan UKM]. Namun demikian, hanya sekitar 30% UMKM yang secara aktif memanfaatkan platform digital (marketplace, media sosial, pembayaran non-tunai) untuk memasarkan produk [INDUSTRY CLAIM/OFFICIAL STATISTICS gabungan, perlu verifikasi silang], sementara adopsi QRIS oleh UMKM tercatat 39,3 juta per semester I 2025 [OFFICIAL STATISTICS, Bank Indonesia] - menunjukkan kesenjangan antara adopsi pembayaran digital dan adopsi kapabilitas komersial digital yang lebih dalam (analitik, personalisasi, retensi).

Social commerce dan live commerce tumbuh sangat cepat: enam dari sepuluh konsumen Indonesia berbelanja melalui platform live shopping pada 2024, dengan 83% pernah berpartisipasi dalam live shopping daring, dan konversi live streaming diklaim hingga tiga kali lebih tinggi dibanding e-commerce konvensional [INDUSTRY CLAIM, perlu verifikasi metodologi]. Jumlah penjual yang menggunakan video meningkat 75% year-over-year menjadi 800.000 penjual, mendorong kenaikan volume transaksi tahunan 90% menjadi 2,6 miliar transaksi [INDUSTRY REPORT, e-Conomy SEA 2025].

Dari sisi biaya operasional, penjual di marketplace pada periode 2025-2026 menghadapi struktur biaya berlapis: komisi dasar 2,5-10%, program gratis ongkir 4-4,5%, biaya promosi 1-2%, dan biaya iklan 3-5%, sehingga total biaya dapat mencapai 15-20% dari harga jual [INDUSTRY CLAIM, Kompas.com - memerlukan verifikasi silang ke laporan resmi marketplace]. KPPU secara aktif mendorong regulasi pasar digital khusus untuk mencegah praktik self-preferencing dan predatory pricing oleh platform besar, termasuk yang melibatkan algoritma dan AI [OFFICIAL STATEMENT, KPPU].

Pada sisi perlindungan konsumen, BPKN mencatat 1.733 pengaduan sepanjang 2024 (naik 200% dari 926 pengaduan pada 2023), dengan e-commerce menjadi salah satu sektor teratas setelah jasa keuangan; total 3.582 pengaduan tercatat sepanjang 2023-2025 [OFFICIAL STATISTICS, BPKN]. Pola pengaduan bergeser dari keluhan produk fisik menuju praktik sistemik seperti biaya tersembunyi (hidden cost), dark pattern, manipulasi informasi, dan lemahnya mekanisme ganti rugi [OFFICIAL STATISTICS/RESEARCH FINDING, BPKN]. Terpisah, OJK mencatat kerugian masyarakat akibat penipuan keuangan mencapai sekitar Rp7 triliun hingga Oktober 2025, dengan modus transaksi belanja daring menjadi penyumbang kasus terbanyak (53.928 kasus, kerugian Rp988 miliar periode November 2024-Oktober 2025) [OFFICIAL STATISTICS, OJK].

Indeks literasi keuangan nasional tercatat 66,46% dan indeks inklusi keuangan 80,51% pada SNLIK 2025 [OFFICIAL STATISTICS, OJK-BPS] - kesenjangan sekitar 14 poin antara akses dan pemahaman ini menjadi konteks penting bagi masalah kepercayaan transaksi dan kerentanan konsumen berliterasi digital rendah (lansia, pengguna baru) yang dibahas pada bagian 6.


## 6. Fifteen Validated Problems

Lima belas masalah berikut disusun dari kombinasi data resmi, temuan riset, dan observasi lapangan yang dapat diverifikasi. Setiap masalah dinilai secara eksplisit relevan dengan Smart Commerce (bukan Smart Logistics/Manufacturing) dan disertai tag status bukti.


### 6.1. UMKM Sulit Menentukan Harga Jual Kompetitif di Marketplace

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Pelaku UMKM umumnya menetapkan harga jual dengan meniru harga kompetitor di marketplace atau hanya menghitung modal produk, tanpa memperhitungkan biaya operasional penuh (komisi, ongkir, iklan, promosi). |
| Pelaku & Dirugikan | Pelaku: UMKM skala mikro-kecil penjual di marketplace. Dirugikan: pemilik usaha (margin tergerus/rugi), dan secara tidak langsung konsumen (kualitas turun akibat penjual menekan biaya produksi untuk bertahan). |
| Current Workflow & Titik Ketidakefisienan | Penjual mengecek harga kompetitor manual, menyesuaikan harga secara ad-hoc tanpa model biaya; titik ketidakefisienan pada tahap perhitungan HPP dan simulasi margin setelah biaya platform berlapis. |
| Akar Penyebab | Rendahnya literasi keuangan usaha, tidak adanya alat bantu penetapan harga yang memperhitungkan biaya real-time platform, dan tekanan psikologis mengikuti harga pasar (price-matching tanpa dasar biaya). |
| Besaran & Bukti Statistik Indonesia | Biaya platform berlapis dapat mencapai 15-20% dari harga jual (komisi 2,5-10% + ongkir 4-4,5% + promosi 1-2% + iklan 3-5%) [INDUSTRY CLAIM, Kompas.com 2026]; 4,40 juta unit usaha e-commerce di Indonesia, mayoritas mikro [OFFICIAL STATISTICS, BPS 2024]. |
| Bukti Akademik | Riset akuntansi UMKM menunjukkan kesalahan umum berupa hanya menghitung modal produk tanpa biaya operasional penuh dalam penentuan harga jual [RESEARCH FINDING, ResearchGate - perlu verifikasi jurnal asal]. |
| Dampak Ekonomi & Sosial | Margin tergerus dapat memaksa UMKM keluar dari marketplace ("masih layak jualan di marketplace?" - isu media 2026) atau menurunkan kualitas produk/layanan, berdampak pada keberlanjutan usaha mikro yang menyerap 97% tenaga kerja nasional [INFERENCE dari data Kemenkop UKM]. |
| Frekuensi & Urgensi | Tinggi - keputusan harga dibuat berulang (setiap produk baru/perubahan biaya platform), dan biaya platform berubah dinamis, menuntut penyesuaian berkelanjutan. |
| Mengapa Solusi Existing Belum Memadai | Kalkulator HPP generik (artikel, template Excel) bersifat statis dan tidak terhubung ke biaya platform real-time atau data kompetitor; tidak ada alat yang menggabungkan struktur biaya UMKM dengan sinyal pasar dinamis. |
| Potensi & Risiko AI | Potensi: model prediktif/optimasi yang mensimulasikan margin pada berbagai skenario harga menggunakan data biaya + histori penjualan. Risiko: rekomendasi harga keliru dapat menyebabkan kerugian nyata jika model tidak diberi guardrail dan transparansi asumsi. |
| Ketersediaan Data | Data biaya platform bersifat publik (skema komisi diumumkan marketplace); data penjualan historis dimiliki penjual sendiri (perlu input manual/API terbatas) - ketersediaan SEDANG. |
| Kelayakan MVP & Kesesuaian Rulebook | Tinggi - dapat didemonstrasikan sebagai satu input (data produk+biaya) -> satu output (rekomendasi rentang harga+simulasi margin), sesuai batasan MVP rulebook. |


### 6.2. Ulasan Palsu/Dimanipulasi Merusak Kepercayaan Transaksi

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Ulasan produk yang direkayasa (dibeli, dibalas otomatis, atau ditulis oleh bot/joki) mengaburkan sinyal kualitas asli, merugikan pembeli yang mengandalkan ulasan untuk memutuskan pembelian. |
| Pelaku & Dirugikan | Pelaku terdampak: penjual jujur yang kalah bersaing dari penjual pemanipulasi ulasan. Dirugikan: konsumen (keputusan pembelian keliru), penjual jujur (kehilangan pangsa pasar). |
| Current Workflow & Titik Ketidakefisienan | Marketplace memiliki filter dasar (rate-limiting, deteksi kata kunci) namun ulasan yang lolos filter tetap tercampur dengan ulasan asli tanpa skor kepercayaan yang transparan bagi pembeli. |
| Akar Penyebab | Insentif ekonomi bagi penjual untuk memanipulasi ulasan demi meningkatkan konversi, ditambah minimnya biaya untuk memproduksi ulasan palsu dalam skala besar. |
| Besaran & Bukti Statistik Indonesia | BPKN mencatat pergeseran pola pengaduan ke arah manipulasi informasi dan lemahnya mekanisme ganti rugi sebagai bagian dari 1.733 pengaduan 2024 [OFFICIAL STATISTICS, BPKN] - proporsi spesifik ulasan palsu tidak dipisahkan dalam data publik [DATA GAP]. |
| Bukti Akademik | Model machine learning (kombinasi fitur teks, sentimen, dan pola perilaku reviewer) terbukti efektif mendeteksi ulasan palsu; contoh: Choi dkk., "Fake review identification and utility evaluation model using machine learning", Frontiers in Artificial Intelligence, 2022, DOI 10.3389/frai.2022.1064371 [VERIFIED - lihat bagian 9]. |
| Dampak Ekonomi & Sosial | Menurunkan kepercayaan konsumen terhadap e-commerce secara sistemik, berpotensi memperlambat pertumbuhan GMV; secara sosial merugikan penjual jujur skala kecil yang tidak mampu membeli ulasan. |
| Frekuensi & Urgensi | Tinggi dan terus berulang seiring pertumbuhan volume transaksi (2,6 miliar transaksi video commerce/tahun) [INDUSTRY REPORT]. |
| Mengapa Solusi Existing Belum Memadai | Filter marketplace bersifat internal/tertutup (black-box bagi peneliti dan penjual kecil), umumnya dioptimalkan untuk bahasa Inggris/skala global, belum tentu menangkap pola manipulasi berbahasa Indonesia informal. |
| Potensi & Risiko AI | Potensi: model klasifikasi teks+perilaku untuk skor kepercayaan ulasan. Risiko: false positive dapat menghapus ulasan asli dan merugikan reputasi penjual; diperlukan human-in-the-loop untuk kasus ambigu. |
| Ketersediaan Data | Dataset fake review akademik banyak tersedia untuk Bahasa Inggris (Amazon/Yelp); dataset berbahasa Indonesia dengan label "palsu/asli" belum ditemukan secara publik [DATA GAP - risiko ketersediaan data SEDANG-RENDAH untuk konteks Indonesia]. |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang - MVP dapat didemonstrasikan dengan data sintetik/proxy (rating-text mismatch, duplikasi teks) namun ground truth berlabel Indonesia menjadi risiko utama. |


### 6.3. Layanan Pelanggan Multi-Kanal UMKM Tidak Tertangani Konsisten

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | UMKM menerima pertanyaan pelanggan dari WhatsApp, marketplace, dan media sosial secara bersamaan tanpa kemampuan membalas cepat dan konsisten, terutama di luar jam kerja. |
| Pelaku & Dirugikan | Pelaku: pemilik UMKM/staf CS tunggal. Dirugikan: UMKM (kehilangan calon pembeli karena respons lambat), konsumen (pengalaman buruk, informasi tidak konsisten antar kanal). |
| Current Workflow & Titik Ketidakefisienan | Pemilik usaha membalas manual satu per satu di setiap aplikasi berbeda; titik ketidakefisienan pada fragmentasi kanal dan tidak adanya draft jawaban otomatis berbasis konteks produk. |
| Akar Penyebab | Keterbatasan sumber daya manusia UMKM (sering hanya 1-2 orang mengelola seluruh operasi), dan biaya tools omnichannel premium (Kata.ai, Qiscus) relatif tinggi untuk skala mikro. |
| Besaran & Bukti Statistik Indonesia | UMKM menghadapi keterbatasan sumber daya manusia sebagai kendala utama daya saing digital [RESEARCH FINDING, kajian marketplace-UMKM 2025]; populasi UMKM 66 juta dengan mayoritas usaha mikro/perorangan [OFFICIAL STATISTICS]. |
| Bukti Akademik | Studi kasus penerapan chatbot AI pada usaha mikro menunjukkan optimasi layanan pelanggan yang terukur; MDPI Information, "Implementing AI Chatbots in Customer Service Optimization-A Case Study in Micro-Enterprise", 2025, ISSN 2078-2489 vol 16 no 12 artikel 1078 [VERIFIED - lihat bagian 9]. |
| Dampak Ekonomi & Sosial | Potensi kehilangan penjualan akibat respons lambat (calon pembeli beralih ke penjual lain); beban kerja berlebih pada pemilik usaha berdampak pada kesejahteraan (burnout usaha mikro). |
| Frekuensi & Urgensi | Harian dan berulang - pertanyaan pelanggan (ketersediaan stok, ukuran, pengiriman) bersifat repetitif namun tetap butuh respons cepat. |
| Mengapa Solusi Existing Belum Memadai | Tools omnichannel existing (Qiscus, Kata.ai, Jubelio Chat) menargetkan bisnis menengah-besar dengan harga langganan yang menjadi barrier bagi usaha mikro [INFERENCE dari observasi harga & positioning produk, bagian 11]. |
| Potensi & Risiko AI | Potensi: asisten balasan berbasis pengetahuan produk milik toko (RAG atas katalog+FAQ) dengan tool-calling ke info stok. Risiko: jawaban tidak akurat (halusinasi) soal stok/harga dapat merugikan kredibilitas toko. |
| Ketersediaan Data | Data percakapan pelanggan dimiliki UMKM sendiri (WhatsApp/marketplace chat export); volume kecil per toko namun dapat disintesis dari FAQ produk - ketersediaan SEDANG. |
| Kelayakan MVP & Kesesuaian Rulebook | Tinggi - input tunggal (pertanyaan pelanggan) -> output tunggal (draft/auto-jawaban) sesuai batasan MVP; risiko overbuilt jika mencoba integrasi penuh semua kanal sekaligus. |


### 6.4. Konsumen Lansia & Literasi Digital Rendah Rentan Penipuan dan Kesulitan Navigasi

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Konsumen lanjut usia dan berliterasi digital rendah kesulitan menavigasi antarmuka e-commerce yang kompleks dan lebih rentan menjadi korban penipuan/pinjaman online ilegal terkait transaksi digital. |
| Pelaku & Dirugikan | Pelaku terdampak: konsumen lansia dan pengguna baru internet. Dirugikan: konsumen itu sendiri (kerugian finansial, kebingungan transaksi), keluarga (dampak sosial-ekonomi). |
| Current Workflow & Titik Ketidakefisienan | Konsumen mengandalkan bantuan keluarga/anak untuk bertransaksi, atau mencoba sendiri dengan risiko kesalahan (salah pilih produk, salah klik tautan phishing). |
| Akar Penyebab | Desain antarmuka platform besar dioptimalkan untuk pengguna digital native; program literasi digital untuk lansia belum menjangkau skala penuh populasi rentan. |
| Besaran & Bukti Statistik Indonesia | OJK mencatat kerugian masyarakat akibat penipuan keuangan sekitar Rp7 triliun hingga Oktober 2025, dengan modus belanja daring menjadi kasus terbanyak (53.928 kasus) [OFFICIAL STATISTICS, OJK]; program literasi digital nasional secara eksplisit menyasar lansia sebagai kelompok rentan kejahatan digital [OFFICIAL/INDUSTRY, Mafindo 2024]. |
| Bukti Akademik | Riset literasi digital lansia pada aspek digital skill dan digital safety menunjukkan kerentanan terhadap penipuan dan pencurian data pribadi [RESEARCH FINDING, Jurnal Komunikasi Global - perlu verifikasi metodologi/sampel]. |
| Dampak Ekonomi & Sosial | Kerugian finansial langsung pada kelompok rentan secara ekonomi terbatas (pensiunan); dampak sosial berupa hilangnya kepercayaan terhadap ekonomi digital pada kelompok usia lanjut. |
| Frekuensi & Urgensi | Sedang-tinggi, meningkat seiring pertumbuhan penetrasi internet pada kelompok usia lanjut dan migrasi layanan publik/perbankan ke digital. |
| Mengapa Solusi Existing Belum Memadai | Program literasi digital bersifat edukasi luring/webinar berskala terbatas, bukan alat bantu real-time saat transaksi berlangsung (mis. peringatan dini saat pola transaksi mencurigakan terdeteksi). |
| Potensi & Risiko AI | Potensi: sistem deteksi pola transaksi/tautan mencurigakan dengan penjelasan sederhana (explainable) untuk pengguna awam. Risiko: false alarm berlebihan dapat mengurangi kepercayaan pada sistem itu sendiri; risiko etik paternalisme jika tidak dirancang hati-hati. |
| Ketersediaan Data | Data pola penipuan/pengaduan bersifat agregat di OJK/kepolisian, tidak granular per transaksi individual untuk pelatihan model - ketersediaan RENDAH untuk MVP kompetisi [DATA GAP]. |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang - MVP layak jika difokuskan pada satu use case sempit (mis. deteksi teks penipuan pada pesan penjual) menggunakan data sintetik/contoh publik modus penipuan. |


### 6.5. Live Commerce: Volume Chat Real-Time Tidak Terlayani

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Saat sesi live streaming penjualan, penjual menerima ratusan komentar/pertanyaan secara bersamaan (harga, stok, ukuran) yang tidak mungkin dijawab manual secara real-time, menyebabkan calon pembeli hilang minat. |
| Pelaku & Dirugikan | Pelaku: penjual/host live commerce (termasuk UMKM dan brand lokal). Dirugikan: penjual (kehilangan konversi), penonton/calon pembeli (pertanyaan tidak terjawab, hilang momentum beli). |
| Current Workflow & Titik Ketidakefisienan | Host live dibantu 1-2 admin membaca komentar manual dan mengetik balasan cepat; titik ketidakefisienan pada volume komentar yang melampaui kapasitas manusia saat traffic tinggi. |
| Akar Penyebab | Pertumbuhan live commerce sangat cepat (75% YoY jumlah penjual video, 90% YoY volume transaksi) tanpa diimbangi tools bantu otomatisasi respons yang terjangkau UMKM [INDUSTRY REPORT, e-Conomy SEA 2025]. |
| Besaran & Bukti Statistik Indonesia | 800.000 penjual menggunakan video pada 2025 dengan 2,6 miliar transaksi tahunan terkait; enam dari sepuluh konsumen berbelanja melalui live shopping [INDUSTRY REPORT/CLAIM, e-Conomy SEA 2025 & laporan terkait]. |
| Bukti Akademik | Studi consumer perceived value pada live streaming shopping Indonesia menunjukkan faktor kepercayaan dan interaksi real-time signifikan mempengaruhi keputusan beli; PMC11260974, "Why are Indonesian consumers buying on live streaming platforms?" [VERIFIED - lihat bagian 9]. |
| Dampak Ekonomi & Sosial | Kehilangan konversi langsung berdampak pada pendapatan penjual UMKM/brand lokal; secara sosial mendorong ketimpangan antara penjual besar (mampu bayar tim admin) dan UMKM (tidak mampu). |
| Frekuensi & Urgensi | Tinggi - terjadi setiap sesi live (harian/mingguan bagi penjual aktif). |
| Mengapa Solusi Existing Belum Memadai | Fitur live shopping platform besar (TikTok Shop, Shopee Live) menyediakan alat dasar namun asisten balasan otomatis kontekstual berbasis katalog produk penjual individual belum menjadi fitur standar yang dapat dikustomisasi UMKM kecil [INFERENCE]. |
| Potensi & Risiko AI | Potensi: klasifikasi & prioritisasi komentar real-time (deteksi intent: harga/stok/ukuran) dengan auto-reply template dinamis. Risiko: latensi tinggi mengurangi nilai real-time; kesalahan intent dapat memberi info keliru saat live berlangsung. |
| Ketersediaan Data | Data komentar live streaming dapat dikumpulkan dari rekaman/API platform (jika tersedia) atau disintesis dari pola FAQ live commerce - ketersediaan SEDANG, namun akses API resmi platform besar terbatas [DATA GAP potensial]. |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang - kompleksitas real-time streaming berisiko overbuilt untuk MVP penyisihan; perlu penyederhanaan lingkup (mis. mode simulasi/replay komentar, bukan live streaming penuh) agar sesuai batasan MVP. |


### 6.6. Toko/Produk Baru Tidak Direkomendasikan Sistem (Cold-Start)

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Sistem rekomendasi marketplace mengandalkan histori interaksi (klik, beli, rating); toko atau produk baru dengan histori minim jarang muncul di rekomendasi, sehingga sulit ditemukan pembeli baru. |
| Pelaku & Dirugikan | Pelaku: penjual baru/UMKM dengan katalog kecil. Dirugikan: penjual baru (visibilitas rendah, sulit bersaing), konsumen (kehilangan variasi produk relevan dari penjual baru/lokal). |
| Current Workflow & Titik Ketidakefisienan | Penjual baru bergantung pada iklan berbayar (yang mahal untuk UMKM) untuk mendapat visibilitas awal karena algoritma rekomendasi default kurang mengangkat entitas baru; titik ketidakefisienan pada fase awal siklus hidup toko/produk. |
| Akar Penyebab | Model rekomendasi collaborative filtering secara struktural membutuhkan data interaksi historis yang belum dimiliki entitas baru (cold-start problem), fenomena yang telah lama didokumentasikan dalam literatur sistem rekomendasi. |
| Besaran & Bukti Statistik Indonesia | Tokopedia melaporkan lebih dari 14 juta penjual dan 1,8 miliar produk terdaftar [INDUSTRY CLAIM, blog Tokopedia] - skala katalog yang sangat besar ini memperbesar risiko produk baru tenggelam tanpa mekanisme discovery khusus. |
| Bukti Akademik | Systematic review cold-start problem pada sistem rekomendasi mengidentifikasi pendekatan content-based, review-based, dan LLM kecil (fine-tuned) sebagai mitigasi untuk skenario data minim [RESEARCH FINDING - ResearchGate systematic review 2024; MDPI Information 14(1):19, "CSP Dataset" 2023, DOI terkait dapat diverifikasi lebih lanjut]. |
| Dampak Ekonomi & Sosial | Penjual baru/UMKM lokal kalah bersaing dengan penjual mapan meski produk berkualitas setara, memperlambat pemerataan ekonomi digital antar pelaku usaha. |
| Frekuensi & Urgensi | Terjadi pada setiap onboarding penjual/produk baru - mengingat 4,40 juta unit usaha e-commerce dengan pertumbuhan 15,3%/tahun, jumlah entitas baru yang mengalami cold-start cukup besar. |
| Mengapa Solusi Existing Belum Memadai | Fitur "AI Product Optimiser" Shopee membantu optimasi judul/atribut namun tidak secara eksplisit mengatasi cold-start rekomendasi lintas kategori untuk penjual benar-benar baru [INFERENCE dari deskripsi fitur, bagian 11]. |
| Potensi & Risiko AI | Potensi: model hybrid content-based + embedding tekstual (deskripsi produk) untuk merekomendasikan produk baru tanpa histori interaksi. Risiko: rekomendasi berbasis konten murni dapat kurang akurat dibanding collaborative filtering matang, perlu evaluasi cermat. |
| Ketersediaan Data | Dataset katalog produk publik (Tokopedia product reviews di Hugging Face, dataset marketplace Kaggle) tersedia untuk simulasi skenario cold-start - ketersediaan SEDANG-TINGGI. |
| Kelayakan MVP & Kesesuaian Rulebook | Tinggi - dapat didemonstrasikan sebagai input deskripsi produk baru -> output daftar rekomendasi kategori/audiens target, sesuai batasan MVP satu alur input-output. |


### 6.7. Rekomendasi Black-Box Menurunkan Kepercayaan Konsumen

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Konsumen menerima rekomendasi produk tanpa penjelasan mengapa produk tersebut direkomendasikan, menurunkan kepercayaan terutama saat rekomendasi terasa tidak relevan atau invasif (terkait profiling). |
| Pelaku & Dirugikan | Pelaku: konsumen digital umum. Dirugikan: konsumen (kepercayaan rendah, pengalaman belanja kurang efisien), penjual (rekomendasi kurang relevan menurunkan konversi). |
| Current Workflow & Titik Ketidakefisienan | Sistem rekomendasi platform besar bekerja sebagai black-box; pengguna tidak diberi alasan (mis. "direkomendasikan karena riwayat pencarian X") sehingga sulit mengevaluasi relevansi. |
| Akar Penyebab | Model rekomendasi modern (deep learning/embedding) secara inheren kurang interpretable dibanding model sederhana, dan explainability jarang menjadi prioritas desain UX pada platform skala besar. |
| Besaran & Bukti Statistik Indonesia | Tidak ditemukan data resmi Indonesia yang mengukur langsung "kepercayaan terhadap rekomendasi AI" secara terpisah [DATA GAP]; namun indeks literasi keuangan 66,46% vs inklusi 80,51% [OFFICIAL STATISTICS OJK] mengindikasikan kesenjangan pemahaman yang relevan terhadap penerimaan sistem otomatis secara umum. |
| Bukti Akademik | Explainable AI terbukti meningkatkan trust pada konteks bisnis kecil - studi menunjukkan fitur explainability meningkatkan trust sebesar 17,8% pada decision support system berbasis AI [RESEARCH FINDING - perlu verifikasi jurnal sumber utuh, lihat bagian 9]. |
| Dampak Ekonomi & Sosial | Rekomendasi tidak dipercaya menurunkan efektivitas personalisasi sebagai pendorong konversi, berdampak pada efisiensi pasar digital secara luas. |
| Frekuensi & Urgensi | Sangat tinggi frekuensinya (setiap sesi browsing marketplace/media sosial melibatkan rekomendasi), namun urgensi bersifat kumulatif/jangka menengah, bukan krisis mendesak. |
| Mengapa Solusi Existing Belum Memadai | Fitur "kenapa direkomendasikan" pada platform besar (jika ada) umumnya generik ("berdasarkan aktivitas Anda") tanpa detail actionable bagi pengguna maupun penjual kecil untuk memahami/mengoptimalkan. |
| Potensi & Risiko AI | Potensi: lapisan explainability (mis. atribusi fitur, RAG dengan alasan tekstual) di atas model rekomendasi. Risiko: eksplanasi yang disederhanakan berlebihan dapat menyesatkan (misleading simplicity). |
| Ketersediaan Data | Dapat memanfaatkan dataset rekomendasi/ulasan publik (Tokopedia reviews) untuk membangun model rekomendasi + lapisan penjelasan sebagai simulasi - ketersediaan SEDANG. |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang - konsep eksplainabilitas menarik secara akademik namun sulit dikemas sebagai satu alur input-output yang "wow" bagi juri non-teknis dalam 7 menit video proof of work. |


### 6.8. Produk Tiruan/Listing Kloning Menyaingi Produk UMKM Asli

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Penjual lain menyalin foto, deskripsi, atau bahkan meniru produk UMKM/brand lokal dan menjualnya dengan harga lebih rendah, mengalihkan calon pembeli dari penjual asli. |
| Pelaku & Dirugikan | Pelaku terdampak: UMKM/brand lokal pemilik produk asli. Dirugikan: UMKM asli (kehilangan penjualan, reputasi), konsumen (membeli produk kualitas lebih rendah tanpa sadar). |
| Current Workflow & Titik Ketidakefisienan | UMKM memantau manual (mencari nama produk sendiri di marketplace) untuk menemukan listing kloning, lalu melapor via formulir pelaporan platform yang prosesnya lambat. |
| Akar Penyebab | Rendahnya biaya untuk menyalin listing (foto+deskripsi dapat disalin dalam hitungan menit) dan minimnya proteksi kekayaan intelektual otomatis di level platform untuk skala UMKM. |
| Besaran & Bukti Statistik Indonesia | Tidak ditemukan statistik resmi Indonesia yang mengukur prevalensi listing kloning secara spesifik [DATA GAP]; KPPU menyoroti isu kloning/predatory practice sebagai bagian dari kompleksitas persaingan usaha digital yang melibatkan algoritma [OFFICIAL STATEMENT, KPPU]. |
| Bukti Akademik | Deep learning untuk deteksi produk tiruan dari gambar smartphone dibahas pada arXiv 2410.05969, "Deep neural network-based detection of counterfeit products from smartphone images" [PREPRINT - belum peer-reviewed, perlu verifikasi lanjutan]. |
| Dampak Ekonomi & Sosial | Merugikan insentif inovasi UMKM/brand lokal untuk mengembangkan produk baru karena mudah ditiru; menurunkan diferensiasi pasar dan mendorong perlombaan harga ke bawah (race to the bottom). |
| Frekuensi & Urgensi | Sedang - lebih sering dialami produk dengan desain/kemasan khas yang mudah difoto ulang (fesyen, kerajinan, kosmetik lokal). |
| Mengapa Solusi Existing Belum Memadai | Mekanisme pelaporan pelanggaran IP marketplace bersifat reaktif (menunggu laporan manual) bukan proaktif (deteksi otomatis kemiripan visual/teks lintas listing). |
| Potensi & Risiko AI | Potensi: computer vision untuk kemiripan gambar produk + NLP untuk kemiripan deskripsi guna memberi peringatan dini ke penjual asli. Risiko: false positive pada produk generik/commodity yang secara wajar mirip (mis. produk grosir yang sama dari supplier sama). |
| Ketersediaan Data | Dataset publik untuk deteksi produk tiruan sebagian besar berbasis gambar produk global/luar negeri; dataset foto produk UMKM Indonesia berlabel "asli vs tiruan" belum ditemukan [DATA GAP TINGGI]. |
| Kelayakan MVP & Kesesuaian Rulebook | Rendah-sedang - keterbatasan dataset berlabel Indonesia menjadi risiko signifikan terhadap kelayakan MVP dalam periode kompetisi terbatas. |


### 6.9. Churn Pelanggan UMKM Tidak Terdeteksi Dini

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | UMKM tidak memiliki cara sistematis mendeteksi pelanggan yang mulai jarang membeli (berpotensi churn) sebelum benar-benar berhenti, sehingga kehilangan kesempatan retensi melalui penawaran tepat waktu. |
| Pelaku & Dirugikan | Pelaku: UMKM/penjual skala kecil-menengah. Dirugikan: UMKM (kehilangan pendapatan berulang tanpa disadari), yang pada akhirnya juga konsumen kehilangan penawaran relevan yang bisa menjaga loyalitas. |
| Current Workflow & Titik Ketidakefisienan | Penjual mengandalkan ingatan/insting pribadi terhadap pelanggan reguler tanpa pencatatan sistematis; tidak ada sinyal otomatis saat pola pembelian pelanggan menurun. |
| Akar Penyebab | Data transaksi tersebar di berbagai kanal (marketplace, WhatsApp, kasir) tanpa konsolidasi, dan UMKM tidak memiliki tools analitik retensi yang terjangkau/mudah dipakai. |
| Besaran & Bukti Statistik Indonesia | Tidak ditemukan data churn spesifik UMKM Indonesia [DATA GAP]; namun retensi pelanggan diakui signifikan secara umum karena mempertahankan pelanggan lebih efisien daripada akuisisi baru [RESEARCH FINDING umum, bukan spesifik Indonesia]. |
| Bukti Akademik | Literatur churn prediction e-commerce luas menggunakan Random Forest, XGBoost, SVM dengan fitur demografis-perilaku-transaksional; review 214 artikel 2015-2023 merangkum tahapan model prediksi churn [RESEARCH FINDING, perlu verifikasi jurnal sumber - lihat bagian 9]. |
| Dampak Ekonomi & Sosial | Kehilangan pendapatan berulang (repeat order) yang secara kumulatif signifikan bagi UMKM dengan margin tipis; berdampak pada keberlanjutan usaha mikro jangka panjang. |
| Frekuensi & Urgensi | Berkelanjutan (terjadi setiap siklus pembelian pelanggan); urgensi sedang karena dampaknya kumulatif, bukan insiden tunggal. |
| Mengapa Solusi Existing Belum Memadai | Tools CRM/analitik churn yang ada dirancang untuk perusahaan menengah-besar dengan data terstruktur skala besar, bukan UMKM dengan data transaksi tersebar dan minim. |
| Potensi & Risiko AI | Potensi: model klasifikasi sederhana berbasis recency-frequency-monetary (RFM) + sinyal teks (perubahan nada chat) untuk skor risiko churn per pelanggan. Risiko: prediksi keliru dapat memicu penawaran diskon tidak perlu yang menggerus margin. |
| Ketersediaan Data | UMKM umumnya memiliki data transaksi terbatas (puluhan-ratusan pelanggan), menantang untuk melatih model robust tanpa data agregat/sintetik tambahan - ketersediaan SEDANG-RENDAH. |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang - MVP layak dengan data sintetik/simulasi RFM, namun nilai demonstrasi terbatas tanpa data transaksi nyata yang meyakinkan juri. |


### 6.10. Efektivitas Promosi/Diskon Tidak Terukur, Margin Tergerus

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | UMKM sering memberikan diskon/promosi mengikuti tren (flash sale, gratis ongkir) tanpa mengukur dampak sebenarnya terhadap margin dan repeat order, berisiko rugi meski penjualan unit naik. |
| Pelaku & Dirugikan | Pelaku: UMKM/tim marketing kecil. Dirugikan: UMKM (margin tergerus tanpa manfaat retensi yang setimpal). |
| Current Workflow & Titik Ketidakefisienan | Keputusan promosi diambil berdasar insting/ikut program platform tanpa simulasi dampak margin; evaluasi pasca-promosi jarang dilakukan sistematis. |
| Akar Penyebab | Minimnya kapasitas analitik (SDM & tools) UMKM untuk causal analysis sederhana yang memisahkan efek promosi dari faktor lain (musiman, tren). |
| Besaran & Bukti Statistik Indonesia | Biaya promosi platform tercatat 1-2% dan biaya iklan 3-5% dari harga jual sebagai bagian struktur biaya berlapis [INDUSTRY CLAIM, Kompas.com 2026] - menunjukkan promosi bukan biaya kecil bagi margin UMKM. |
| Bukti Akademik | Uplift modeling dan causal inference merupakan pendekatan standar akademik untuk mengukur efek incremental promosi dibanding baseline non-treatment [METODOLOGI UMUM - literatur causal inference/uplift modeling, perlu sitasi spesifik lebih lanjut, ditandai ASUMSI metodologis pada tahap ini]. |
| Dampak Ekonomi & Sosial | Margin tipis UMKM (sering di bawah 20% setelah biaya platform) rentan negatif jika promosi tidak terukur, berdampak pada keberlangsungan usaha. |
| Frekuensi & Urgensi | Tinggi - momen promosi (harbolnas, flash sale, gajian) berulang bulanan. |
| Mengapa Solusi Existing Belum Memadai | Dashboard analitik marketplace menampilkan angka penjualan kotor tanpa simulasi margin bersih per skenario diskon, dan tidak memisahkan efek kausal promosi dari tren organik. |
| Potensi & Risiko AI | Potensi: model uplift/simulasi what-if sederhana untuk memprediksi dampak diskon terhadap margin & repeat order. Risiko: data historis terbatas UMKM membuat estimasi kausal kurang robust; risiko overclaim jika tidak disertai interval ketidakpastian. |
| Ketersediaan Data | Data penjualan historis dimiliki UMKM (ekspor dari marketplace/kasir); kualitas dan volume bervariasi - ketersediaan SEDANG. |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang - MVP dapat disederhanakan menjadi simulasi skenario harga/diskon berbasis data yang diinput pengguna, sesuai batasan MVP rulebook. |


### 6.11. Penipuan Toko Fiktif / Modus Belanja Daring

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Konsumen tertipu oleh toko/akun penjual fiktif (di media sosial atau marketplace informal) yang meminta pembayaran di luar sistem escrow resmi lalu tidak mengirim barang. |
| Pelaku & Dirugikan | Pelaku terdampak: konsumen digital, khususnya pembeli yang berinteraksi via media sosial/WhatsApp di luar sistem pembayaran terlindungi marketplace resmi. Dirugikan: konsumen (kerugian finansial langsung). |
| Current Workflow & Titik Ketidakefisienan | Konsumen memverifikasi toko secara manual (cek testimoni, cek nomor rekening di grup anti-penipuan) - proses lambat dan tidak sistematis, sering dilakukan setelah transaksi bermasalah. |
| Akar Penyebab | Transaksi di luar sistem escrow resmi (COD informal, transfer langsung via media sosial) tidak memiliki lapisan proteksi otomatis, dan minim alat verifikasi real-time yang mudah diakses konsumen awam. |
| Besaran & Bukti Statistik Indonesia | Modus transaksi belanja daring adalah penyumbang kasus penipuan keuangan terbanyak: 53.928 kasus dengan kerugian Rp988 miliar periode November 2024-Oktober 2025 [OFFICIAL STATISTICS, OJK]. |
| Bukti Akademik | Penelitian machine learning untuk deteksi transaksi/entitas fraud banyak berkembang pada domain perbankan/kartu kredit; adaptasi khusus pada pola penipuan toko fiktif berbahasa Indonesia di media sosial belum banyak ditemukan pada penelusuran awal [RESEARCH GAP potensial, lihat bagian 12]. |
| Dampak Ekonomi & Sosial | Kerugian finansial langsung skala nasional (bagian dari Rp7 triliun total kerugian penipuan keuangan hingga Oktober 2025) [OFFICIAL STATISTICS, OJK]; dampak sosial berupa menurunnya kepercayaan terhadap transaksi digital informal. |
| Frekuensi & Urgensi | Sangat tinggi dan meningkat - salah satu modus penipuan keuangan digital paling umum di Indonesia saat ini. |
| Mengapa Solusi Existing Belum Memadai | Grup komunitas anti-penipuan (mis. cek rekening manual) bersifat crowdsourced dan reaktif, tidak terintegrasi sebagai alat proaktif dalam alur belanja konsumen. |
| Potensi & Risiko AI | Potensi: klasifikasi risiko teks percakapan penjual (pola bahasa umum penipuan, permintaan pembayaran di luar sistem resmi) sebagai peringatan dini bagi konsumen. Risiko: false positive dapat menstigma penjual sah; risiko tinggi jika sistem disalahgunakan untuk keputusan otomatis tanpa konfirmasi manusia. |
| Ketersediaan Data | Data kasus penipuan bersifat agregat/tidak granular untuk publik; contoh modus dapat dikumpulkan dari laporan media dan komunitas anti-penipuan sebagai data sintetik/proxy - ketersediaan SEDANG-RENDAH untuk pelatihan model berlabel. |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang - MVP layak dengan lingkup sempit (klasifikasi teks tunggal: pesan penjual berisiko/tidak) menggunakan data contoh modus penipuan yang dipublikasikan. |


### 6.12. Ulasan & Chat Pelanggan Tidak Diubah Menjadi Insight Bisnis Actionable

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | UMKM menerima banyak ulasan dan pesan pelanggan berisi umpan balik berharga (keluhan kualitas, permintaan varian, keluhan pengiriman) namun tidak memiliki cara mengolahnya menjadi keputusan bisnis konkret karena volume dan bahasa informal/campuran. |
| Pelaku & Dirugikan | Pelaku: UMKM/pemilik usaha skala kecil-menengah. Dirugikan: UMKM (kehilangan sinyal perbaikan produk/layanan), konsumen (masalah berulang tidak diperbaiki). |
| Current Workflow & Titik Ketidakefisienan | Pemilik usaha membaca ulasan satu per satu secara manual tanpa rekap sistematis; titik ketidakefisienan pada volume tinggi dan bahasa informal (slang, singkatan, campur bahasa daerah) yang sulit diproses cepat. |
| Akar Penyebab | Tidak tersedianya alat NLP terjangkau yang dilatih khusus menangani Bahasa Indonesia informal/e-commerce, sementara tools sentiment analysis generik/bahasa Inggris tidak menangkap nuansa lokal. |
| Besaran & Bukti Statistik Indonesia | 4,40 juta unit usaha e-commerce menghasilkan volume ulasan dalam skala besar setiap hari [inferensi dari OFFICIAL STATISTICS BPS 2024]; dataset publik seperti PRDECT-ID dan korpus sentimen e-commerce Bahasa Indonesia (21.840 komentar berlabel) menunjukkan volume data nyata yang relevan [FACT, Kaggle/Hugging Face]. |
| Bukti Akademik | Model IndoBERT untuk klasifikasi ulasan e-commerce Bahasa Indonesia dilaporkan mencapai akurasi hingga 97%, mengungguli pendekatan LSTM [RESEARCH FINDING, "Klasifikasi Sentimen Ulasan Produk pada Platform E-Commerce di Indonesia dengan Model Pre-Trained IndoBERT", jurnal BITS - PARTIALLY VERIFIED, metodologi lengkap perlu ditelaah dari full text]. Pendekatan aspect-based sentiment analysis dengan Random Forest mencapai F1-score 0,835 pada domain e-commerce [RESEARCH FINDING, tesis UGM repository - PARTIALLY VERIFIED]. |
| Dampak Ekonomi & Sosial | Perbaikan produk/layanan berbasis insight ulasan berpotensi meningkatkan retensi dan rating toko, berdampak langsung pada pendapatan; secara sosial membantu UMKM meningkatkan kualitas tanpa memerlukan tim data science internal. |
| Frekuensi & Urgensi | Sangat tinggi - ulasan/chat masuk setiap hari pada toko aktif, namun urgensi bertumpuk (backlog ulasan yang tidak pernah benar-benar dianalisis). |
| Mengapa Solusi Existing Belum Memadai | Dashboard rating marketplace hanya menampilkan skor rata-rata dan daftar ulasan mentah, tanpa ringkasan aspek (kualitas/pengiriman/harga) maupun prioritisasi tindakan; tools sentiment analysis SaaS internasional umumnya mahal dan tidak dioptimalkan Bahasa Indonesia informal. |
| Potensi & Risiko AI | Potensi: aspect-based sentiment analysis + ringkasan naratif berbasis LLM yang di-ground pada teks ulasan asli (RAG) untuk menghasilkan rekomendasi aksi terprioritas. Risiko: kesalahan ekstraksi aspek pada bahasa sangat informal/typo dapat menyesatkan; perlu menampilkan sumber kutipan asli agar dapat diverifikasi pemilik usaha. |
| Ketersediaan Data | Tersedia beberapa dataset publik: PRDECT-ID (Kaggle, klasifikasi emosi ulasan Indonesia), e-commerce-sentiment-bahasa-indonesia (Hugging Face, 21.840 komentar berlabel), Tokopedia product reviews 2019 (Hugging Face, 40.607 ulasan) - ketersediaan TINGGI. |
| Kelayakan MVP & Kesesuaian Rulebook | Tinggi - input tunggal (kumpulan/batch teks ulasan atau chat) -> output tunggal (ringkasan insight + daftar aksi terprioritas), sangat sesuai batasan MVP; dataset dan model dasar (IndoBERT) tersedia publik untuk fine-tuning sesuai ketentuan kustomisasi rulebook. |


### 6.13. Aksesibilitas Platform E-Commerce bagi Penyandang Disabilitas Netra

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Penyandang tunanetra kesulitan berbelanja mandiri secara daring karena banyak elemen visual (foto produk, tombol ikon) pada aplikasi e-commerce tidak sepenuhnya kompatibel dengan pembaca layar (screen reader). |
| Pelaku & Dirugikan | Pelaku: konsumen penyandang disabilitas netra/low vision. Dirugikan: konsumen (harus bergantung pada bantuan pihak lain, kehilangan privasi dan kemandirian finansial). |
| Current Workflow & Titik Ketidakefisienan | Pengguna mengandalkan screen reader bawaan perangkat yang membaca elemen UI apa adanya (sering tanpa label deskriptif untuk gambar produk), atau meminta bantuan keluarga/teman untuk memilih dan membayar. |
| Akar Penyebab | Desain UI e-commerce mayoritas dioptimalkan untuk interaksi visual (grid foto produk, filter visual), sementara audit aksesibilitas (WCAG) jarang menjadi prioritas pengembangan fitur baru pada platform. |
| Besaran & Bukti Statistik Indonesia | Tidak ditemukan data resmi Indonesia mengenai jumlah pengguna tunanetra yang bertransaksi e-commerce [DATA GAP]; secara global riset menyebut kelangkaan fitur audio/deskripsi detail/navigasi linear pada situs belanja bagi tunanetra sebagai hambatan signifikan [RESEARCH FINDING, literatur internasional]. |
| Bukti Akademik | Prototipe voice-enabled e-commerce mencapai 92% akurasi pengenalan suara, 95% fungsi text-to-speech, dan 88% keberhasilan transaksi pada uji coba terbatas [RESEARCH FINDING - Atlantis Press conference paper, perlu verifikasi metodologi & ukuran sampel]; MDPI Societies, DOI 10.3390/soc15040090, "Beyond Accessibility Compliance: Exploring the Role of Information on Apparel Shopping Websites for the Blind and Visually Impaired" [VERIFIED, lihat bagian 9]; Frontiers in AI, DOI 10.3389/frai.2024.1349668, bibliometric review aksesibilitas digital era AI [VERIFIED]. |
| Dampak Ekonomi & Sosial | Eksklusi ekonomi digital bagi kelompok disabilitas berdampak pada kemandirian finansial dan partisipasi ekonomi; secara sosial bertentangan dengan prinsip digital inclusion yang menjadi salah satu domain eksplisit Smart Commerce dalam rulebook. |
| Frekuensi & Urgensi | Berkelanjutan - hambatan dialami setiap kali pengguna tunanetra mencoba bertransaksi, meski populasi terdampak proporsional lebih kecil dibanding masalah UMKM. |
| Mengapa Solusi Existing Belum Memadai | Riset internasional mencatat gap signifikan pada dukungan gangguan selain visual (pendengaran, motorik, autisme) dan bahwa mayoritas solusi asistif masih terfragmentasi (OCR terpisah dari voice assistant terpisah dari RFID), belum terintegrasi mulus dalam satu alur belanja [RESEARCH FINDING]. |
| Potensi & Risiko AI | Potensi: asisten belanja berbasis suara (speech-to-text + text-to-speech + deskripsi gambar otomatis/image captioning) untuk navigasi katalog dan checkout. Risiko: kesalahan pengenalan suara/produk pada transaksi finansial berisiko tinggi (salah beli/salah bayar) jika tanpa konfirmasi berlapis. |
| Ketersediaan Data | Dataset image captioning umum tersedia (multibahasa/Inggris), namun data spesifik produk e-commerce Indonesia dengan deskripsi audio berlabel belum ditemukan publik - ketersediaan SEDANG (dapat memanfaatkan data produk teks yang ada + model captioning umum). |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang - MVP dapat difokuskan sempit (satu alur: input suara pencarian produk -> output deskripsi audio produk) namun kebutuhan integrasi multimodal (suara+gambar) menambah kompleksitas relatif terhadap batasan MVP. |


### 6.14. Biaya Platform Berlapis Menekan Margin Tanpa Alat Optimasi Kanal

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | UMKM yang berjualan di banyak kanal (beberapa marketplace + media sosial) tidak memiliki cara membandingkan profitabilitas riil per kanal setelah memperhitungkan seluruh biaya berlapis, sehingga sulit memutuskan kanal mana yang harus diprioritaskan. |
| Pelaku & Dirugikan | Pelaku: UMKM multi-channel/omnichannel seller. Dirugikan: UMKM (alokasi waktu dan modal ke kanal yang sebenarnya kurang menguntungkan). |
| Current Workflow & Titik Ketidakefisienan | Penjual mengecek laporan penjualan kotor per kanal secara terpisah tanpa konsolidasi biaya lintas kanal; titik ketidakefisienan pada tidak adanya perbandingan margin bersih apple-to-apple. |
| Akar Penyebab | Setiap marketplace memiliki skema biaya, program promosi, dan format laporan berbeda, membuat konsolidasi manual memakan waktu dan rawan kesalahan bagi pemilik usaha non-finansial. |
| Besaran & Bukti Statistik Indonesia | Struktur biaya berlapis (komisi 2,5-10%, ongkir gratis 4-4,5%, promo 1-2%, iklan 3-5%) berbeda-beda antar program dan marketplace [INDUSTRY CLAIM, Kompas.com 2026], menegaskan kompleksitas perbandingan lintas kanal. |
| Bukti Akademik | Riset omnichannel commerce menunjukkan kompleksitas konsolidasi data lintas kanal sebagai tantangan operasional UMKM [RESEARCH FINDING umum - perlu sitasi spesifik lebih dalam, ditandai ASUMSI pada tahap ini]. |
| Dampak Ekonomi & Sosial | Alokasi sumber daya yang keliru antar kanal dapat memperlambat pertumbuhan usaha dan menggerus margin yang sudah tipis. |
| Frekuensi & Urgensi | Bulanan/musiman - keputusan alokasi kanal biasanya dievaluasi berkala, bukan harian. |
| Mengapa Solusi Existing Belum Memadai | Tools multichannel management (Jubelio, Ginee) fokus pada sinkronisasi stok/pesanan, belum tentu menyediakan analitik margin bersih komparatif otomatis lintas kanal berbasis skema biaya terbaru [INFERENCE dari deskripsi produk, bagian 11]. |
| Potensi & Risiko AI | Potensi: model perhitungan/estimasi margin bersih per kanal berdasarkan input data biaya+penjualan, dengan rekomendasi prioritisasi. Risiko: akurasi bergantung pada kelengkapan data biaya yang diinput manual oleh pengguna (garbage-in-garbage-out). |
| Ketersediaan Data | Skema biaya bersifat publik (dapat dikumpulkan dari halaman kebijakan marketplace); data penjualan riil per kanal dimiliki UMKM - ketersediaan SEDANG. |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang-tinggi - dapat disederhanakan menjadi kalkulator/estimator berbasis input terstruktur, meski nilai "AI"-nya perlu ditunjukkan lebih dari sekadar kalkulasi aritmatika (mis. estimasi/prediksi dengan data tidak lengkap). |


### 6.15. Usaha Mikro/Franchise Kecil Kesulitan Mengambil Keputusan Komersial Tanpa Analitik Terjangkau

| Aspek | Keterangan |
| --- | --- |
| Deskripsi | Pemilik usaha mikro dan franchise kecil (mis. gerai kelontong, waralaba minuman skala kecil) mengambil keputusan restock, bundling produk, dan waktu promosi berdasar insting karena tidak mampu mengakses tools analitik/business intelligence yang biasanya ditujukan untuk perusahaan besar. |
| Pelaku & Dirugikan | Pelaku: pemilik usaha mikro, franchisee kecil. Dirugikan: pemilik usaha (keputusan restock keliru menyebabkan kelebihan/kekurangan stok), yang berujung pada kerugian modal kerja. |
| Current Workflow & Titik Ketidakefisienan | Pemilik usaha mencatat penjualan manual (buku/Excel sederhana) tanpa analisis pola, memutuskan restock berdasar "perasaan" bukan data historis terstruktur. |
| Akar Penyebab | Tools business intelligence/analytics komersial dirancang dan diharga untuk perusahaan menengah-besar; UMKM tidak memiliki kapasitas SDM data maupun anggaran untuk software BI premium. |
| Besaran & Bukti Statistik Indonesia | 66 juta UMKM dengan mayoritas skala mikro menyumbang lebih dari 60% PDB [OFFICIAL STATISTICS, Kemenkop UKM] - basis pelaku usaha yang sangat besar berpotensi terdampak keterbatasan analitik ini. |
| Bukti Akademik | Kajian task-technology fit menunjukkan niat penggunaan AI untuk evaluasi usaha pada UMKM DKI Jakarta dipengaruhi kesesuaian tugas-teknologi, bukan sekadar tekanan sosial [RESEARCH FINDING, Ekopedia Jurnal Ilmiah Ekonomi - perlu verifikasi metodologi lengkap]; kerangka TOE (Technology-Organization-Environment) menjadi model dominan menjelaskan adopsi AI pada UMKM [RESEARCH FINDING, tinjauan sistematis MDP Student Conference]. |
| Dampak Ekonomi & Sosial | Keputusan restock/bundling yang keliru berulang dapat mengikis modal kerja terbatas UMKM, berpotensi menghambat pertumbuhan usaha mikro yang menjadi tulang punggung penyerapan tenaga kerja nasional. |
| Frekuensi & Urgensi | Mingguan/bulanan - keputusan restock dan bundling adalah rutinitas operasional inti usaha ritel kecil. |
| Mengapa Solusi Existing Belum Memadai | Software akuntansi/kasir sederhana (POS) mencatat transaksi namun jarang menyediakan rekomendasi proaktif (kapan restock, kombinasi bundling apa yang optimal) berbasis pola data historis toko itu sendiri. |
| Potensi & Risiko AI | Potensi: model peramalan sederhana + rule-mining (association rules) untuk merekomendasikan waktu restock dan kombinasi bundling dari data transaksi historis toko. Risiko: data historis pendek/tidak lengkap pada usaha baru membatasi akurasi prediksi. |
| Ketersediaan Data | Data transaksi dimiliki pemilik usaha (umumnya dalam format tidak terstruktur/manual) - ketersediaan SEDANG, memerlukan effort digitisasi awal yang signifikan dari pengguna. |
| Kelayakan MVP & Kesesuaian Rulebook | Sedang - MVP layak dengan data contoh/sintetik transaksi ritel mikro, namun validasi nyata memerlukan kerja sama pemilik usaha yang bersedia membagikan data penjualan aktual. |


## 7. Stakeholder and User Analysis

Bagian ini memetakan pemangku kepentingan untuk lima masalah dengan skor kelayakan MVP tertinggi pada bagian 6 (harga, layanan pelanggan, cold-start, insight ulasan, dan biaya kanal), karena kelimanya menjadi basis pembentukan kandidat ide pada bagian 16.


### 7.1 Pemetaan Pemangku Kepentingan

| Peran | Masalah Harga (6.1) | Masalah Ulasan/Insight (6.12) | Masalah Cold-Start (6.6) |
| --- | --- | --- | --- |
| Primary user | Pemilik UMKM penjual online | Pemilik UMKM penjual online | Penjual/UMKM baru di marketplace |
| Secondary user | Staf admin toko | Staf CS/marketing UMKM | Tim marketing UMKM |
| Beneficiary | Konsumen (harga wajar) | Konsumen (kualitas membaik) | Konsumen (variasi produk lebih luas) |
| Economic buyer | Pemilik usaha (individu) | Pemilik usaha (individu) | Pemilik usaha (individu) |
| Data owner | UMKM (data biaya & penjualan) | UMKM (data ulasan/chat) | Marketplace (data katalog) & UMKM |
| Regulator | KPPU (persaingan usaha) | BPKN, Kemendag (PMSE) | KPPU (persaingan platform) |
| Partner potensial | Asosiasi UMKM, komunitas seller | Asosiasi UMKM, penyedia POS | Marketplace (API katalog), asosiasi UMKM |
| Pihak yang mungkin menolak | Marketplace besar (jika dianggap mengungkap struktur biaya) | Tidak signifikan | Marketplace (jika dianggap kompetitor sistem rekomendasi internal) |
| Pihak terkena risiko | UMKM jika rekomendasi harga keliru | UMKM jika insight keliru arahkan keputusan salah | UMKM jika rekomendasi kategori keliru |
| Pihak perlu memberi persetujuan | Pemilik data (UMKM) untuk data biaya | Pemilik data (UMKM) untuk data ulasan/chat pelanggan | Pemilik data (UMKM) untuk data katalog |


### 7.2 User Persona Berbasis Bukti


#### Persona 1: "Bu Rina" - Pemilik UMKM Fesyen Mikro (2 Karyawan)

| Aspek | Keterangan |
| --- | --- |
| Pekerjaan/Konteks | Menjual pakaian melalui Shopee, Tokopedia, dan WhatsApp Business; usia 30-an; dibantu 1 admin paruh waktu. |
| Tujuan | Meningkatkan penjualan tanpa menambah beban kerja manual; menjaga margin di tengah biaya platform yang meningkat. |
| Current Workflow | Membalas chat manual di 3 aplikasi, menetapkan harga dengan mengecek kompetitor, membaca ulasan sesekali saat sempat. |
| Pain Point | Kewalahan volume chat terutama saat promo; ragu apakah harga sudah tepat; tidak sempat membaca seluruh ulasan untuk perbaikan produk. |
| Hambatan Teknologi | Tidak familiar dengan tools teknis (API, coding); mengandalkan aplikasi siap pakai berbasis smartphone. |
| Hambatan Biaya | Anggaran tools tambahan sangat terbatas (idealnya gratis/freemium; berbasis data BPS bahwa mayoritas usaha e-commerce adalah mikro). |
| Hambatan Kepercayaan | Skeptis terhadap rekomendasi otomatis tanpa penjelasan alasan (terkait temuan explainability & trust, bagian 6.7 dan 9). |
| Kemampuan Menyediakan Data | Punya data ulasan & histori chat, namun dalam format tersebar (screenshot, chat log) - perlu proses ekspor/impor sederhana. |
| Kesediaan Menggunakan AI | Sedang-tinggi jika terbukti menghemat waktu nyata dan disertai contoh konkret (bukan janji abstrak) [ASSUMPTION - perlu validasi wawancara]. |
| Potensi Manfaat | Waktu respons lebih cepat, keputusan harga/perbaikan produk lebih berbasis data, potensi kenaikan retensi pelanggan. |


#### Persona 2: "Pak Wisnu" - Penjual Baru di Marketplace (Onboarding <3 Bulan)

| Aspek | Keterangan |
| --- | --- |
| Pekerjaan/Konteks | Baru membuka toko kerajinan kayu lokal di marketplace; sebelumnya berjualan offline di pasar/pameran. |
| Tujuan | Mendapatkan pembeli pertama dan membangun reputasi toko baru. |
| Current Workflow | Mengandalkan promosi manual di media sosial pribadi dan grup komunitas untuk mendatangkan trafik awal karena minim muncul di rekomendasi organik marketplace. |
| Pain Point | Produk tidak muncul di halaman rekomendasi meski kualitas baik; iklan berbayar terasa mahal untuk modal terbatas. |
| Hambatan Teknologi | Literasi digital dasar-menengah; belum familiar dengan istilah SEO/algoritma marketplace. |
| Hambatan Biaya | Modal kerja terbatas sebagai penjual baru, sensitif terhadap biaya iklan dan tools berbayar. |
| Hambatan Kepercayaan | Ragu terhadap klaim "AI meningkatkan penjualan" tanpa bukti nyata pada kategori produknya. |
| Kemampuan Menyediakan Data | Data terbatas (belum ada histori transaksi/ulasan) - kondisi cold-start yang menjadi inti masalah 6.6. |
| Kesediaan Menggunakan AI | Sedang, bergantung pada kemudahan pakai dan bukti hasil cepat [ASSUMPTION]. |
| Potensi Manfaat | Visibilitas awal lebih baik tanpa bergantung sepenuhnya pada iklan berbayar. |


#### Persona 3: "Kak Sari" - Konsumen Digital Berliterasi Menengah, Pengguna Live Shopping

| Aspek | Keterangan |
| --- | --- |
| Pekerjaan/Konteks | Karyawan swasta usia 20-an, aktif berbelanja melalui live shopping TikTok dan chat langsung dengan penjual. |
| Tujuan | Mendapatkan produk sesuai kebutuhan dengan cepat dan harga wajar, memastikan penjual terpercaya. |
| Current Workflow | Bertanya di kolom komentar live/chat, menunggu balasan penjual yang sering lambat saat ramai; mengecek ulasan sebelum memutuskan beli. |
| Pain Point | Pertanyaan tidak terjawab saat live; sulit membedakan ulasan asli dan palsu. |
| Hambatan Teknologi | Rendah - pengguna digital native, terbiasa dengan aplikasi. |
| Hambatan Biaya | Tidak relevan langsung (konsumen, bukan pembayar tools) - namun sensitif terhadap harga produk. |
| Hambatan Kepercayaan | Skeptis terhadap ulasan yang terlalu sempurna/seragam (terkait masalah 6.2). |
| Kemampuan Menyediakan Data | Tidak relevan sebagai penyedia data primer, namun perilakunya menjadi sumber data interaksi. |
| Kesediaan Menggunakan AI | Tinggi jika transparan dan mempercepat keputusan belanja. |
| Potensi Manfaat | Respons lebih cepat saat live, keputusan pembelian lebih terinformasi lewat sinyal kepercayaan yang jelas. |


### 7.3 Pertanyaan Wawancara Pengguna untuk Validasi Lanjutan


#### Untuk Pelaku Usaha (UMKM/Penjual) - 10 Pertanyaan

- Bagaimana cara Anda saat ini menentukan harga jual produk baru di marketplace?
- Kanal mana yang paling sering digunakan pelanggan untuk bertanya, dan berapa lama rata-rata waktu Anda membalas?
- Apakah Anda pernah kehilangan calon pembeli karena terlambat membalas chat? Seberapa sering?
- Bagaimana Anda memutuskan kapan harus restock atau membuat promosi/diskon?
- Apakah Anda membaca seluruh ulasan pelanggan? Bagaimana Anda menindaklanjutinya?
- Pernahkah Anda merasa dirugikan oleh penjual lain yang meniru produk/listing Anda?
- Alat/aplikasi apa yang sudah Anda gunakan untuk mengelola toko online, dan apa yang masih dirasa kurang?
- Berapa besar anggaran bulanan yang realistis Anda alokasikan untuk tools bantu digital (jika ada)?
- Seberapa penting bagi Anda memahami "alasan" di balik rekomendasi otomatis (harga/promosi/insight) sebelum mengikutinya?
- Data apa (penjualan, chat, ulasan) yang bersedia Anda bagikan untuk keperluan uji coba alat bantu berbasis AI, dan dalam format apa data tersebut biasanya tersimpan?


#### Untuk Konsumen - 10 Pertanyaan

- Seberapa sering Anda membaca ulasan sebelum memutuskan membeli produk secara daring?
- Pernahkah Anda merasa ragu apakah suatu ulasan itu asli atau palsu? Apa tanda-tanda yang Anda perhatikan?
- Bagaimana pengalaman Anda saat bertanya ke penjual melalui live shopping atau chat - apakah dijawab cepat?
- Apakah Anda pernah mengalami kerugian akibat transaksi dengan toko yang ternyata fiktif/menipu? Bagaimana ceritanya?
- Apakah Anda merasa rekomendasi produk yang muncul di aplikasi relevan dengan kebutuhan Anda?
- Bagi Anda yang berusia lanjut/mendampingi anggota keluarga lansia: kesulitan apa yang paling sering dialami saat berbelanja daring?
- Bagi penyandang disabilitas netra/low vision: fitur apa yang paling membantu atau paling menghambat saat berbelanja daring?
- Seberapa penting informasi "kenapa produk ini direkomendasikan" bagi keputusan belanja Anda?
- Apakah Anda pernah membatalkan pembelian karena ragu terhadap kredibilitas toko? Apa yang membuat Anda ragu?
- Fitur apa yang menurut Anda paling dibutuhkan untuk membuat belanja daring terasa lebih aman dan terpercaya?


#### Untuk Pakar/Regulator - 5 Pertanyaan

- Menurut pandangan Bapak/Ibu, praktik AI/algoritma apa di platform commerce yang paling berisiko bagi persaingan usaha UMKM saat ini?
- Bagaimana kerangka regulasi yang ada (UU PDP, perlindungan konsumen, PMSE) memandang penggunaan AI untuk menganalisis data ulasan/chat pelanggan?
- Apa saja praktik dark pattern atau manipulasi ulasan yang paling sering ditemukan dalam pengaduan konsumen e-commerce?
- Menurut Bapak/Ibu, jenis dukungan AI seperti apa yang paling realistis dan berdampak bagi UMKM skala mikro dalam 1-2 tahun ke depan?
- Apa batasan etis yang perlu diperhatikan tim pengembang saat membangun sistem AI yang menganalisis data pelanggan UMKM (termasuk isu privasi dan potensi bias)?


## 8. Official Data and Statistics

| Indikator | Nilai | Sumber | Tahun | Status |
| --- | --- | --- | --- | --- |
| Jumlah unit usaha e-commerce Indonesia | 4,40 juta unit (+15,3% YoY; +86% dalam 4 tahun) | BPS - Statistik E-Commerce 2024 | 2024 | OFFICIAL STATISTICS |
| GMV ekonomi digital Indonesia | ~USD 100 miliar (+14% YoY), proyeksi USD 180 miliar pada 2030 | Google/Temasek/Bain - e-Conomy SEA 2025 | 2025 | INDUSTRY REPORT |
| GMV e-commerce Indonesia | ~USD 71 miliar (+14% YoY) | e-Conomy SEA 2025 | 2025 | INDUSTRY REPORT |
| Populasi UMKM Indonesia | ~66 juta unit usaha; >60% PDB; ~97% penyerapan tenaga kerja | Kementerian Koperasi dan UKM | 2025 | OFFICIAL STATISTICS |
| UMKM pengguna QRIS | 39,3 juta UMKM | Bank Indonesia | H1 2025 | OFFICIAL STATISTICS |
| UMKM aktif memanfaatkan platform digital | ~30% dari total UMKM | Agregat berbagai sumber | 2025 | INDUSTRY CLAIM |
| Pasar rakyat & pedagang terdigitalisasi | 6.115 pasar; 317.429 pedagang | Kementerian Perdagangan | Juli 2025 | OFFICIAL STATISTICS |
| Indeks literasi keuangan nasional | 66,46% | SNLIK - OJK & BPS | 2025 | OFFICIAL STATISTICS |
| Indeks inklusi keuangan nasional | 80,51% | SNLIK - OJK & BPS | 2025 | OFFICIAL STATISTICS |
| Kerugian penipuan keuangan (semua modus) | ~Rp7 triliun | OJK | s.d. Okt 2025 | OFFICIAL STATISTICS |
| Kasus penipuan modus belanja daring | 53.928 kasus, kerugian Rp988 miliar | OJK | Nov 2024-Okt 2025 | OFFICIAL STATISTICS |
| Pengaduan konsumen BPKN | 1.733 pengaduan (2024, naik 200% dari 926 di 2023); 3.582 pengaduan (2023-2025) | BPKN | 2023-2025 | OFFICIAL STATISTICS |
| Konsumen berbelanja via live shopping | 6 dari 10 konsumen; 83% pernah berpartisipasi | Laporan industri live commerce | 2024 | INDUSTRY CLAIM |
| Penjual aktif video/live commerce | 800.000 penjual (+75% YoY); 2,6 miliar transaksi (+90% YoY) | e-Conomy SEA 2025 | 2025 | INDUSTRY REPORT |
| Estimasi total biaya platform marketplace | 15-20% dari harga jual (komisi+ongkir+promo+iklan) | Kompas.com, mengutip pelaku industri | 2025-2026 | INDUSTRY CLAIM |
| Bisnis Indonesia yang mengadopsi AI | 18 juta bisnis (28%), tumbuh 47% YoY; 5,9 juta bisnis baru mengadopsi pada 2024 | AWS/riset terkait | 2024-2025 | INDUSTRY REPORT |

Catatan verifikasi: seluruh angka pada tabel di atas diambil dari ringkasan hasil pencarian web dan belum ditelusuri hingga ke dokumen sumber PDF/HTML aslinya secara baris-per-baris; direkomendasikan verifikasi silang langsung ke publikasi resmi (bps.go.id, ojk.go.id, bpkn.go.id) sebelum dikutip pada proposal final.


## 9. Academic Literature Review

Berikut disajikan sumber akademik yang ditemukan melalui pencarian web terbuka pada Agustus 2026, dikelompokkan berdasarkan tema. Setiap sumber ditandai status verifikasi: VERIFIED (DOI/identitas eksplisit terkonfirmasi dalam hasil pencarian), PARTIALLY VERIFIED (sumber teridentifikasi melalui URL resmi penerbit namun DOI eksplisit tidak terkonfirmasi dalam teks pencarian, atau merupakan skripsi/prosiding non-Scopus), atau PREPRINT (arXiv/belum peer-reviewed). Tidak ada DOI yang dikarang; sumber tanpa DOI eksplisit hanya dicantumkan tautan penerbitnya.


### 9.1 Tema: Trust and Safety, Fake Review Detection


#### Fake review identification and utility evaluation model using machine learning

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Choi et al., 2022 |
| Jurnal & DOI | Frontiers in Artificial Intelligence. DOI: 10.3389/frai.2022.1064371 |
| Negara/Konteks | Tidak spesifik Indonesia - metodologi umum e-commerce |
| Dataset & Metode | Ulasan produk e-commerce; model machine learning (bukan deep learning) untuk klasifikasi & evaluasi utilitas ulasan |
| Temuan Utama | Machine learning terbukti efektif mendeteksi ulasan palsu dengan presisi tinggi menggunakan kombinasi fitur teks dan perilaku reviewer |
| Keterbatasan | Full text belum ditelaah mendalam pada tahap ini; generalisasi ke Bahasa Indonesia belum diuji |
| Relevansi | Masalah 6.2 (ulasan palsu) - dasar metodologis untuk ide "UlasanAsli" |
| Status | VERIFIED |


#### Artificial intelligence applications in fake review detection: Bibliometric analysis and future avenues for research

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi dari cuplikan pencarian; ScienceDirect, sekitar 2022-2023 |
| Jurnal & DOI | ScienceDirect (Journal of Business Research - dugaan berdasarkan pola pii); pii: S0148296322010967. DOI eksplisit tidak terkonfirmasi dalam teks pencarian |
| Negara/Konteks | Global, bibliometric review |
| Dataset & Metode | Analisis bibliometrik korpus penelitian fake review detection |
| Temuan Utama | Memetakan tren riset AI untuk deteksi ulasan palsu dan mengidentifikasi arah riset masa depan |
| Keterbatasan | Bersifat tinjauan (review), bukan studi empiris baru; akses full text terbatas |
| Relevansi | Konteks umum masalah 6.2, memperkuat urgensi riset di area ini |
| Status | NOT FULLY ACCESSIBLE |


#### Fake review detection in e-Commerce platforms using aspect-based sentiment analysis

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi dari cuplikan; ScienceDirect, sekitar 2023 |
| Jurnal & DOI | ScienceDirect; pii: S0148296323005027. DOI eksplisit tidak terkonfirmasi |
| Negara/Konteks | Global |
| Dataset & Metode | Aspect-based sentiment analysis diterapkan pada ulasan e-commerce untuk deteksi ulasan palsu |
| Temuan Utama | Menggabungkan ABSA dengan deteksi ulasan palsu meningkatkan akurasi dibanding pendekatan sentimen umum |
| Keterbatasan | Akses full text terbatas pada tahap ini |
| Relevansi | Menghubungkan masalah 6.2 dan 6.12 (insight ulasan) - relevan ganda untuk ide "InsightUlasan" dan "UlasanAsli" |
| Status | NOT FULLY ACCESSIBLE |


### 9.2 Tema: AI Chatbot dan Customer Service untuk Usaha Kecil


#### Trust in the chatbot: a semi-human relationship

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2023 |
| Jurnal & DOI | Future Business Journal (Springer Nature). DOI: 10.1186/s43093-023-00288-z |
| Negara/Konteks | Umum, berbasis survei pengguna chatbot |
| Dataset & Metode | Survei kepercayaan pengguna terhadap chatbot; menganalisis dimensi kognitif dan emosional trust |
| Temuan Utama | Trust kognitif (keandalan) dan trust emosional (pengalaman subjektif) sama-sama membentuk kepercayaan pengguna pada chatbot |
| Keterbatasan | Tidak spesifik konteks UMKM/Indonesia |
| Relevansi | Masalah 6.3 (layanan pelanggan) - dasar desain trust untuk ide asisten balasan UMKM |
| Status | VERIFIED |


#### Implementing AI Chatbots in Customer Service Optimization - A Case Study in Micro-Enterprise

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2025 |
| Jurnal & DOI | MDPI Information, Vol 16, No 12, artikel 1078 (ISSN 2078-2489). DOI eksplisit tidak terkonfirmasi dalam teks pencarian, tautan mdpi.com/2078-2489/16/12/1078 |
| Negara/Konteks | Studi kasus usaha mikro (negara tidak spesifik dari cuplikan) |
| Dataset & Metode | Studi kasus implementasi chatbot AI pada operasional layanan pelanggan usaha mikro |
| Temuan Utama | Chatbot AI dapat menjadi alat skalabel dan terjangkau untuk meringankan beban layanan pelanggan usaha mikro, dengan model hybrid (otomatisasi + pengawasan manusia) direkomendasikan |
| Keterbatasan | Studi kasus tunggal, generalisasi terbatas |
| Relevansi | Masalah 6.3 dan 6.5 (live commerce) - langsung relevan untuk ide asisten balasan UMKM |
| Status | PARTIALLY VERIFIED |


### 9.3 Tema: Recommendation Systems dan Cold-Start


#### Artificial intelligence and recommender systems in e-commerce: Trends and research agenda

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi dari cuplikan; sekitar 2024 |
| Jurnal & DOI | ScienceDirect (jurnal open-access seri baru); pii: S2667305324001091. DOI eksplisit tidak terkonfirmasi |
| Negara/Konteks | Global, tinjauan tren riset |
| Dataset & Metode | Tinjauan pustaka sistem rekomendasi berbasis AI di e-commerce, mengidentifikasi agenda riset ke depan |
| Temuan Utama | Riset rekomendasi e-commerce paling produktif pada 2020-2023, dengan tren menuju personalisasi berbasis konteks dan explainability |
| Keterbatasan | Bersifat tinjauan, bukan studi empiris |
| Relevansi | Masalah 6.6 (cold-start) dan 6.7 (explainability) - landasan konseptual ide "RekomenUMKM" |
| Status | NOT FULLY ACCESSIBLE |


#### User Cold Start Problem in Recommendation Systems: A Systematic Review

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi lengkap dari cuplikan; tersedia di ResearchGate |
| Jurnal & DOI | Tidak teridentifikasi (kemungkinan prosiding/jurnal nasional-internasional); DOI tidak terkonfirmasi |
| Negara/Konteks | Global, tinjauan sistematis |
| Dataset & Metode | Tinjauan sistematis pendekatan mengatasi cold-start user pada sistem rekomendasi |
| Temuan Utama | Pendekatan content-based, hybrid, dan berbasis linked open data efektif mengurangi masalah cold-start |
| Keterbatasan | Akses full text terbatas pada tahap ini |
| Relevansi | Masalah 6.6 - opsi metodologi untuk ide "RekomenUMKM" |
| Status | NOT FULLY ACCESSIBLE |


#### Introducing CSP Dataset: A Dataset Optimized for the Study of the Cold Start Problem in Recommender Systems

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2023 |
| Jurnal & DOI | MDPI Information, Vol 14, No 1, artikel 19 (ISSN 2078-2489). DOI eksplisit tidak terkonfirmasi, tautan mdpi.com/2078-2489/14/1/19 |
| Negara/Konteks | Global |
| Dataset & Metode | Memperkenalkan dataset yang dirancang khusus untuk eksperimen cold-start pada sistem rekomendasi |
| Temuan Utama | Dataset terstruktur khusus mempermudah evaluasi metode cold-start secara terkontrol |
| Keterbatasan | Dataset tidak berbahasa Indonesia/konteks lokal |
| Relevansi | Masalah 6.6 - referensi desain evaluasi untuk ide "RekomenUMKM" |
| Status | PARTIALLY VERIFIED |


### 9.4 Tema: NLP dan Sentiment Analysis Bahasa Indonesia untuk E-Commerce


#### Klasifikasi Sentimen Ulasan Produk pada Platform E-Commerce di Indonesia dengan Menggunakan Model Pre-Trained IndoBERT

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi lengkap dari cuplikan; jurnal nasional Indonesia |
| Jurnal & DOI | Building of Informatics, Technology and Science (BITS). DOI tidak terkonfirmasi, tautan ejurnal.seminar-id.com/index.php/bits/article/view/6968 |
| Negara/Konteks | Indonesia |
| Dataset & Metode | Ulasan produk e-commerce Indonesia; model pre-trained IndoBERT dibandingkan LSTM |
| Temuan Utama | IndoBERT mencapai akurasi hingga 97% dalam klasifikasi sentimen ulasan Bahasa Indonesia, mengungguli LSTM |
| Keterbatasan | Jurnal nasional non-Scopus (belum terkonfirmasi indeksasinya); ukuran sampel & detail metodologi perlu ditelaah dari full text |
| Relevansi | LANGSUNG relevan untuk masalah 6.12 dan ide utama "InsightUlasan" - bukti kelayakan teknis fine-tuning IndoBERT |
| Status | PARTIALLY VERIFIED |


#### Analisis Sentimen Ulasan Produk di E-Commerce Bukalapak Menggunakan Natural Language Processing

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi lengkap dari cuplikan |
| Jurnal & DOI | Prosiding SISFOTEK (seminar.iaii.or.id). DOI tidak terkonfirmasi |
| Negara/Konteks | Indonesia (Bukalapak) |
| Dataset & Metode | Ulasan Bukalapak; pendekatan NLP untuk analisis sentimen |
| Temuan Utama | NLP dapat mengisi kesenjangan analisis ulasan toko online Indonesia yang sebelumnya belum banyak diteliti |
| Keterbatasan | Prosiding seminar nasional, bukan jurnal terindeks internasional; metodologi ringkas |
| Relevansi | Masalah 6.12 - bukti tambahan kelayakan platform-spesifik Indonesia |
| Status | PARTIALLY VERIFIED |


#### Analisis Sentimen untuk Ulasan Produk E-Commerce Shopee Menggunakan BERT

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi lengkap dari cuplikan |
| Jurnal & DOI | Jurnal Sifo Mikroskil. DOI tidak terkonfirmasi |
| Negara/Konteks | Indonesia (Shopee) |
| Dataset & Metode | Ulasan Shopee; klasifikasi sentimen dengan BERT |
| Temuan Utama | BERT mencapai akurasi 83,08% pada klasifikasi sentimen ulasan Shopee |
| Keterbatasan | Akurasi lebih rendah dibanding klaim IndoBERT pada studi lain - menandakan variasi hasil antar studi yang perlu ditelaah lebih hati-hati (bukan diambil sebagai angka pasti tunggal) |
| Relevansi | Masalah 6.12 - pembanding metodologi |
| Status | PARTIALLY VERIFIED |


#### Analisis Sentimen Berbasis Aspek dengan Pendekatan Machine Learning Menggunakan Dataset Bahasa Indonesia

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi lengkap dari cuplikan; skripsi/tesis |
| Jurnal & DOI | Repository skripsi Universitas Gadjah Mada (etd.repository.ugm.ac.id) - BUKAN jurnal, merupakan karya tugas akhir |
| Negara/Konteks | Indonesia |
| Dataset & Metode | Dataset Bahasa Indonesia; aspect-based sentiment analysis dengan Random Forest |
| Temuan Utama | Random Forest untuk klasifikasi aspek pada domain e-commerce mencapai F1-score 0,835 |
| Keterbatasan | Karya skripsi (belum peer-review jurnal), akses terbatas pada abstrak |
| Relevansi | Masalah 6.12 - metodologi ABSA yang dapat direplikasi untuk InsightUlasan |
| Status | NOT FULLY ACCESSIBLE |


#### Leveraging IndoBERT and DistilBERT for Indonesian Emotion Classification in E-Commerce Reviews

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2025 (nomor arXiv 2509.14611) |
| Jurnal & DOI | arXiv preprint (belum peer-reviewed). arXiv:2509.14611 |
| Negara/Konteks | Indonesia |
| Dataset & Metode | Ulasan e-commerce Indonesia; perbandingan IndoBERT dan DistilBERT untuk klasifikasi emosi |
| Temuan Utama | Model transformer Bahasa Indonesia dapat diadaptasi untuk klasifikasi emosi (lebih granular dari sentimen positif/negatif) pada ulasan e-commerce |
| Keterbatasan | Preprint, belum melalui proses peer-review |
| Relevansi | Masalah 6.12 - opsi memperkaya InsightUlasan dengan klasifikasi emosi, bukan sekadar sentimen |
| Status | PREPRINT |


### 9.5 Tema: Live Commerce dan Social Commerce Indonesia


#### Why are Indonesian consumers buying on live streaming platforms? Research on consumer perceived value theory

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi lengkap dari cuplikan; artikel PMC11260974 |
| Jurnal & DOI | Terindeks PubMed Central (PMC), 2024. PMCID: PMC11260974 |
| Negara/Konteks | Indonesia |
| Dataset & Metode | Survei konsumen live streaming shopping Indonesia; kerangka teori perceived value |
| Temuan Utama | Nilai yang dirasakan konsumen (utilitarian, hedonic, kepercayaan) signifikan mendorong keputusan beli di live streaming platform Indonesia |
| Keterbatasan | Fokus pada niat beli, tidak secara langsung mengevaluasi solusi AI untuk penjual |
| Relevansi | Masalah 6.5 (live commerce) - konteks perilaku konsumen Indonesia yang relevan |
| Status | VERIFIED |


### 9.6 Tema: Adopsi AI dan Explainability pada UMKM/SME


#### Artificial Intelligence Adoption in SMEs: Survey Based on TOE-DOI Framework, Primary Methodology and Challenges

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2025 |
| Jurnal & DOI | MDPI Applied Sciences, Vol 15, No 12, artikel 6465 (ISSN 2076-3417). DOI eksplisit tidak terkonfirmasi, tautan mdpi.com/2076-3417/15/12/6465 |
| Negara/Konteks | Umum/multi-negara |
| Dataset & Metode | Survei adopsi AI pada SME menggunakan kerangka Technology-Organization-Environment (TOE) dan Diffusion of Innovation (DOI) |
| Temuan Utama | Kesiapan teknologi, organisasi, dan tekanan lingkungan menjadi determinan utama adopsi AI pada SME; tantangan utama meliputi kurangnya keahlian dan kepercayaan |
| Keterbatasan | Survei umum, tidak spesifik konteks Indonesia |
| Relevansi | Latar belakang adopsi AI UMKM untuk seluruh kandidat ide |
| Status | PARTIALLY VERIFIED |


#### SME-TEAM: leveraging trust and ethics for secure and responsible use of AI and LLMs in SMEs

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2025 |
| Jurnal & DOI | npj Artificial Intelligence (Nature Portfolio); juga tersedia sebagai arXiv:2509.10594. Tautan nature.com/articles/s44387-025-00065-z mengindikasikan pola DOI 10.1038/s44387-025-00065-z namun tidak dikonfirmasi eksplisit dalam teks pencarian |
| Negara/Konteks | Umum, kerangka kerja SME |
| Dataset & Metode | Kerangka kerja (framework paper) untuk adopsi AI/LLM yang aman dan bertanggung jawab pada SME |
| Temuan Utama | Trust dan etika menjadi fondasi kritikal keberhasilan adopsi AI/LLM pada SME |
| Keterbatasan | Bersifat kerangka konseptual, bukan studi empiris kuantitatif |
| Relevansi | Kerangka etika untuk seluruh kandidat ide, khususnya bagian Risiko, Etika, Privasi, dan Regulasi (bagian 22) |
| Status | PARTIALLY VERIFIED |


#### Faktor-Faktor yang Memengaruhi Niat Menggunakan Teknologi AI untuk Evaluasi Usaha pada Pelaku UMKM di DKI Jakarta: Perspektif Task-Technology Fit

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi lengkap dari cuplikan |
| Jurnal & DOI | Ekopedia: Jurnal Ilmiah Ekonomi. DOI tidak terkonfirmasi |
| Negara/Konteks | Indonesia (DKI Jakarta) |
| Dataset & Metode | Survei UMKM DKI Jakarta; kerangka Task-Technology Fit |
| Temuan Utama | Niat penggunaan AI ditentukan lebih oleh kesesuaian tugas-teknologi dan kesiapan individu, bukan tekanan sosial |
| Keterbatasan | Cakupan geografis terbatas pada DKI Jakarta, jurnal nasional non-Scopus |
| Relevansi | Konteks adopsi UMKM Indonesia untuk seluruh kandidat ide, khususnya validasi kesediaan menggunakan AI (bagian 7.2) |
| Status | PARTIALLY VERIFIED |


### 9.7 Tema: Counterfeit dan Computer Vision untuk Marketplace


#### Deep neural network-based detection of counterfeit products from smartphone images

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2024 (arXiv:2410.05969) |
| Jurnal & DOI | arXiv preprint (belum peer-reviewed) |
| Negara/Konteks | Tidak spesifik Indonesia |
| Dataset & Metode | Gambar produk dari smartphone; deep neural network untuk klasifikasi asli/tiruan |
| Temuan Utama | Model deep learning dapat mendeteksi produk tiruan dari foto smartphone dengan akurasi yang dilaporkan menjanjikan |
| Keterbatasan | Preprint, dataset kemungkinan tidak mencakup produk UMKM Indonesia |
| Relevansi | Masalah 6.8 (produk tiruan) - opsi metodologi computer vision |
| Status | PREPRINT |


### 9.8 Tema: Aksesibilitas E-Commerce bagi Penyandang Disabilitas


#### Beyond Accessibility Compliance: Exploring the Role of Information on Apparel Shopping Websites for the Blind and Visually Impaired

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2025 |
| Jurnal & DOI | Societies (MDPI), Vol 15, No 4, artikel 90. DOI: 10.3390/soc15040090 |
| Negara/Konteks | Tidak spesifik Indonesia |
| Dataset & Metode | Studi kualitatif/kuantitatif peran informasi pada situs belanja pakaian bagi tunanetra/low vision |
| Temuan Utama | Kepatuhan aksesibilitas teknis saja tidak cukup - kualitas dan kelengkapan informasi produk sama pentingnya bagi pengalaman belanja tunanetra |
| Keterbatasan | Konteks negara maju, budaya belanja berbeda dengan Indonesia |
| Relevansi | Masalah 6.13 (aksesibilitas disabilitas netra) |
| Status | VERIFIED |


#### Digital accessibility in the era of artificial intelligence - Bibliometric analysis and systematic review

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2024 |
| Jurnal & DOI | Frontiers in Artificial Intelligence. DOI: 10.3389/frai.2024.1349668 |
| Negara/Konteks | Global, tinjauan sistematis |
| Dataset & Metode | Analisis bibliometrik dan tinjauan sistematis literatur aksesibilitas digital berbasis AI |
| Temuan Utama | Riset AI-driven accessibility terkonsentrasi pada disabilitas visual; terdapat gap signifikan untuk gangguan pendengaran, motorik, dan spektrum autisme |
| Keterbatasan | Bersifat tinjauan, tidak memberikan solusi teknis baru |
| Relevansi | Masalah 6.13 - mengonfirmasi research gap accessibility (bagian 12) |
| Status | VERIFIED |


### 9.9 Tema: Churn Prediction E-Commerce


#### Knowledge Discovery on E-Commerce Customer Churn Using Interpretable Machine Learning: A Comparative Study of SHAP-Based Classifiers

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | Tidak teridentifikasi lengkap dari cuplikan |
| Jurnal & DOI | Journal of Applied Informatics and Computing (Politeknik Negeri Batam). DOI tidak terkonfirmasi |
| Negara/Konteks | Tidak spesifik Indonesia dari cuplikan, penerbit Indonesia |
| Dataset & Metode | Data e-commerce; model klasifikasi churn dengan interpretasi SHAP |
| Temuan Utama | Pendekatan interpretable ML (SHAP) memungkinkan penjelasan faktor pendorong churn, bukan sekadar prediksi black-box |
| Keterbatasan | Jurnal nasional, detail dataset perlu ditelaah dari full text |
| Relevansi | Masalah 6.9 (churn UMKM) - metodologi interpretable untuk trust |
| Status | PARTIALLY VERIFIED |


#### B2C E-Commerce Customer Churn Prediction Based on K-Means and SVM

| Aspek | Keterangan |
| --- | --- |
| Penulis/Tahun | 2022 |
| Jurnal & DOI | Journal of Theoretical and Applied Electronic Commerce Research (MDPI), Vol 17, No 2, artikel 24 (ISSN 0718-1876). DOI eksplisit tidak terkonfirmasi, tautan mdpi.com/0718-1876/17/2/24 |
| Negara/Konteks | Tidak spesifik Indonesia |
| Dataset & Metode | Data pelanggan B2C e-commerce; kombinasi K-Means untuk segmentasi dan SVM untuk prediksi churn |
| Temuan Utama | Kombinasi clustering dan klasifikasi meningkatkan akurasi prediksi churn dibanding model tunggal |
| Keterbatasan | Tidak spesifik UMKM skala mikro dengan data terbatas |
| Relevansi | Masalah 6.9 - metodologi pembanding |
| Status | PARTIALLY VERIFIED |


## 10. Literature Synthesis

Sintesis berikut disusun per kelompok tema literatur pada bagian 9, memenuhi permintaan untuk tidak sekadar mendaftar jurnal.


### 10.1 Trust and Safety / Fake Review

| Aspek | Keterangan |
| --- | --- |
| Apa yang sudah diketahui | Machine learning (fitur teks + perilaku) efektif mendeteksi ulasan palsu; ABSA meningkatkan granularitas deteksi. |
| Apa yang masih diperdebatkan | Perdebatan seputar trade-off precision-recall dan risiko menghapus ulasan asli (false positive) belum banyak dibahas eksplisit pada sumber yang ditemukan. |
| Metode paling umum | Klasifikasi berbasis fitur teks+perilaku, kadang dikombinasikan aspect-based sentiment analysis. |
| Dataset paling umum | Dataset Amazon/Yelp (Bahasa Inggris) mendominasi; dataset Bahasa Indonesia berlabel "palsu/asli" tidak ditemukan publik. |
| Metrik paling umum | Precision, recall, F1-score. |
| Kelemahan penelitian terdahulu | Mayoritas studi berbasis data global/Inggris, generalisasi ke konteks Indonesia (bahasa informal, budaya ulasan) belum diuji. |
| Gap yang dapat dimanfaatkan | Language gap dan Indonesia context gap: belum ada model/dataset fake-review Bahasa Indonesia yang terverifikasi publik. |
| Implikasi untuk inovasi AIC | Ide berbasis deteksi ulasan palsu Indonesia (UlasanAsli) memiliki novelty konteks lokal tinggi, namun risiko dataset gap juga tinggi. |


### 10.2 Chatbot dan Customer Service SME

| Aspek | Keterangan |
| --- | --- |
| Apa yang sudah diketahui | Trust pengguna terhadap chatbot dibentuk dimensi kognitif dan emosional; model hybrid (AI+manusia) direkomendasikan untuk usaha mikro. |
| Apa yang masih diperdebatkan | Sejauh mana otomatisasi penuh vs hybrid paling optimal untuk skala UMKM sangat mikro masih bervariasi antar studi kasus. |
| Metode paling umum | Studi kasus implementasi (case study), survei trust. |
| Dataset paling umum | Data percakapan pelanggan spesifik studi kasus, tidak ada dataset publik besar yang ditemukan. |
| Metrik paling umum | Tingkat kepuasan, tingkat trust, waktu respons. |
| Kelemahan penelitian terdahulu | Studi kasus tunggal sulit digeneralisasi; konteks Indonesia (bahasa informal, multi-kanal WhatsApp) belum banyak diteliti secara spesifik. |
| Gap yang dapat dimanfaatkan | UMKM adoption gap dan localization gap: minim studi chatbot khusus UMKM Indonesia multi-kanal. |
| Implikasi untuk inovasi AIC | Mendukung ide asisten balasan UMKM (BalasCepat) sebagai salah satu kandidat, dengan penekanan pada model hybrid bukan otomatisasi penuh. |


### 10.3 Recommendation Systems dan Cold-Start

| Aspek | Keterangan |
| --- | --- |
| Apa yang sudah diketahui | Cold-start adalah masalah terdokumentasi baik; pendekatan content-based, hybrid, dan LLM kecil terbukti membantu skenario data minim. |
| Apa yang masih diperdebatkan | Efektivitas relatif LLM kecil vs pendekatan hybrid klasik pada skala UMKM dengan data sangat terbatas belum banyak diuji di konteks nyata. |
| Metode paling umum | Content-based filtering, hybrid collaborative-content, fine-tuned small LLM. |
| Dataset paling umum | Dataset didesain khusus untuk eksperimen cold-start (mis. CSP Dataset); tidak spesifik Indonesia. |
| Metrik paling umum | Hit-rate@K, precision@K. |
| Kelemahan penelitian terdahulu | Sedikit studi yang menggabungkan cold-start dengan konteks UMKM negara berkembang dan keterbatasan data ekstrem (toko benar-benar baru). |
| Gap yang dapat dimanfaatkan | UMKM adoption gap dan data gap: metodologi cold-start belum diuji pada skenario katalog UMKM Indonesia yang sangat kecil. |
| Implikasi untuk inovasi AIC | Mendukung ide RekomenUMKM, namun perlu desain evaluasi hati-hati karena data riil UMKM sangat terbatas. |


### 10.4 NLP dan Sentiment Analysis Bahasa Indonesia

| Aspek | Keterangan |
| --- | --- |
| Apa yang sudah diketahui | Model pre-trained Bahasa Indonesia (IndoBERT, DistilBERT lokal) secara konsisten mengungguli pendekatan klasik (LSTM, Naive Bayes) pada klasifikasi sentimen ulasan e-commerce, dengan akurasi bervariasi 83-97% tergantung studi. |
| Apa yang masih diperdebatkan | Rentang akurasi yang cukup lebar (83% vs 97%) antar studi menunjukkan hasil sangat bergantung pada kualitas dataset dan definisi task - belum ada konsensus benchmark tunggal. |
| Metode paling umum | Fine-tuning IndoBERT/BERT, klasifikasi berbasis Random Forest untuk ABSA. |
| Dataset paling umum | PRDECT-ID, e-commerce-sentiment-bahasa-indonesia (HuggingFace), ulasan Tokopedia/Shopee/Bukalapak yang dikumpulkan mandiri per studi. |
| Metrik paling umum | Akurasi, F1-score. |
| Kelemahan penelitian terdahulu | Mayoritas jurnal nasional non-Scopus dengan deskripsi metodologi terbatas; jarang membahas bahasa sangat informal/campur bahasa daerah secara eksplisit; jarang menghubungkan output sentimen ke rekomendasi aksi bisnis konkret. |
| Gap yang dapat dimanfaatkan | Methodological gap dan evaluation gap: penelitian berhenti di klasifikasi sentimen/emosi, belum ada yang secara eksplisit menjembatani ke output "rekomendasi aksi bisnis UMKM". |
| Implikasi untuk inovasi AIC | Ini adalah landasan literatur TERKUAT dan paling relevan bagi ide utama InsightUlasan - gap eksplisit di ujung pipeline (dari skor sentimen ke keputusan bisnis) adalah novelty konkret yang dapat diklaim. |


### 10.5 Live/Social Commerce Indonesia

| Aspek | Keterangan |
| --- | --- |
| Apa yang sudah diketahui | Nilai yang dirasakan konsumen (utilitarian, hedonic, trust) mendorong adopsi live shopping di Indonesia secara signifikan. |
| Apa yang masih diperdebatkan | Sejauh mana AI (bukan sekadar desain UX/insentif) dapat meningkatkan pengalaman live commerce bagi penjual kecil belum banyak diteliti langsung. |
| Metode paling umum | Survei perilaku konsumen, model perceived value. |
| Dataset paling umum | Data survei primer per studi. |
| Metrik paling umum | Skala Likert, regresi/SEM. |
| Kelemahan penelitian terdahulu | Fokus riset pada sisi konsumen (mengapa membeli), minim riset sisi operasional penjual kecil saat volume interaksi tinggi. |
| Gap yang dapat dimanfaatkan | Human-AI interaction gap: minim penelitian tentang bagaimana AI dapat membantu penjual mengelola volume interaksi live commerce secara real-time di konteks Indonesia. |
| Implikasi untuk inovasi AIC | Mendukung urgensi masalah 6.5, namun readiness teknis (real-time constraint) membuatnya kurang ideal untuk MVP kompetisi dibanding InsightUlasan. |


### 10.6 Adopsi AI dan Explainability pada UMKM

| Aspek | Keterangan |
| --- | --- |
| Apa yang sudah diketahui | Kerangka TOE-DOI dan Task-Technology Fit adalah model dominan menjelaskan adopsi AI pada SME/UMKM; trust dan explainability terbukti meningkatkan adopsi. |
| Apa yang masih diperdebatkan | Besaran pasti kontribusi explainability terhadap trust bervariasi antar studi (mis. klaim "17,8%" pada satu sumber belum tentu dapat digeneralisasi). |
| Metode paling umum | Survei kuantitatif berbasis kerangka TOE/DOI/TTF. |
| Dataset paling umum | Data survei primer per studi, tidak ada dataset publik terpadu. |
| Metrik paling umum | Skor adopsi, intention-to-use, trust score. |
| Kelemahan penelitian terdahulu | Mayoritas riset bersifat cross-sectional (potret satu waktu), belum banyak studi longitudinal pasca-adopsi nyata AI oleh UMKM. |
| Gap yang dapat dimanfaatkan | Trust gap dan explainability gap: minim studi yang menguji desain explainability KONKRET (bukan sekadar survei niat) pada tools AI yang benar-benar dipakai UMKM Indonesia. |
| Implikasi untuk inovasi AIC | Menjadi dasar argumentasi bahwa SEMUA kandidat ide wajib menyertakan elemen transparansi/penjelasan sederhana agar sesuai temuan literatur adopsi UMKM. |


### 10.7 Counterfeit Detection dan Computer Vision

| Aspek | Keterangan |
| --- | --- |
| Apa yang sudah diketahui | Deep learning (CNN-based) dapat mendeteksi produk tiruan dari citra dengan akurasi menjanjikan pada studi awal. |
| Apa yang masih diperdebatkan | Skalabilitas dan generalisasi model ke kategori produk yang sangat beragam (fesyen, kerajinan, kosmetik) belum banyak diuji. |
| Metode paling umum | Convolutional neural network, image similarity matching. |
| Dataset paling umum | Dataset citra produk global, sebagian besar bukan produk Indonesia. |
| Metrik paling umum | Akurasi klasifikasi. |
| Kelemahan penelitian terdahulu | Riset masih tahap awal/preprint; belum ada dataset publik produk UMKM Indonesia berlabel asli/tiruan. |
| Gap yang dapat dimanfaatkan | Data gap tinggi untuk konteks Indonesia; population gap (fokus riset pada merek besar, bukan produk UMKM/kerajinan lokal). |
| Implikasi untuk inovasi AIC | Ide DeteksiTiru memiliki risiko dataset tinggi, menempatkannya sebagai kandidat berisiko lebih tinggi dibanding InsightUlasan/HargaCerdas. |


### 10.8 Aksesibilitas E-Commerce bagi Disabilitas

| Aspek | Keterangan |
| --- | --- |
| Apa yang sudah diketahui | Kepatuhan teknis (WCAG) saja tidak cukup; kualitas informasi dan integrasi multimodal (suara+teks+gambar) penting bagi pengalaman belanja tunanetra. |
| Apa yang masih diperdebatkan | Sejauh mana solusi voice-assistant generik vs solusi khusus e-commerce lebih efektif belum banyak dibandingkan langsung. |
| Metode paling umum | Studi kualitatif UX, prototipe voice-enabled shopping. |
| Dataset paling umum | Tidak ada dataset besar khusus; sebagian besar studi kualitatif/prototipe skala kecil. |
| Metrik paling umum | Task success rate, tingkat kepuasan pengguna. |
| Kelemahan penelitian terdahulu | Riset terkonsentrasi pada disabilitas visual, minim untuk gangguan lain; konteks negara berkembang/Indonesia hampir tidak ditemukan pada penelusuran ini. |
| Gap yang dapat dimanfaatkan | Accessibility gap dan localization gap yang jelas untuk konteks Indonesia - namun kompleksitas teknis multimodal menjadi tantangan MVP. |
| Implikasi untuk inovasi AIC | Masalah 6.13 secara sosial penting namun secara teknis lebih berisiko untuk MVP kompetisi dibanding kandidat NLP teks. |


### 10.9 Churn Prediction E-Commerce

| Aspek | Keterangan |
| --- | --- |
| Apa yang sudah diketahui | Kombinasi clustering (segmentasi) dan klasifikasi (SVM/Random Forest/XGBoost) umum digunakan; pendekatan interpretable (SHAP) mulai berkembang untuk transparansi. |
| Apa yang masih diperdebatkan | Ambang/definisi "churn" bervariasi antar studi (30/60/90 hari tanpa transaksi), memengaruhi perbandingan hasil. |
| Metode paling umum | K-Means + SVM, Random Forest, XGBoost, SHAP untuk interpretasi. |
| Dataset paling umum | Data transaksi B2C e-commerce skala menengah-besar; belum ditemukan studi berbasis data UMKM skala mikro. |
| Metrik paling umum | Akurasi, precision/recall, AUC. |
| Kelemahan penelitian terdahulu | Minim studi pada skala data UMKM mikro (puluhan-ratusan transaksi) yang jauh lebih sedikit dari data B2C skala besar pada literatur. |
| Gap yang dapat dimanfaatkan | Data gap dan UMKM adoption gap: model churn literatur diasumsikan data besar, belum tentu applicable langsung ke UMKM data-scarce. |
| Implikasi untuk inovasi AIC | Jika churn UMKM dipilih sebagai ide, perlu adaptasi metodologi untuk data kecil (bukan replikasi langsung model literatur). |


## 11. Existing Solutions and Competitor Mapping

Istilah yang digunakan mengikuti konvensi: Existing (sudah tersedia dan menyelesaikan masalah secara langsung), Similar (menyelesaikan masalah berdekatan dengan mekanisme berbeda), Adjacent (menyentuh sebagian kecil masalah sebagai fitur tambahan), Substitute (solusi non-AI yang menjadi alternatif fungsional), Research prototype (belum menjadi produk komersial).

| Nama Solusi | Negara | Target Pengguna | Masalah yang Diselesaikan | AI yang Digunakan | Kelebihan | Kekurangan | Gap Konteks Indonesia | Klasifikasi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shopee AI Product Optimiser & Asisten AI Chat | Indonesia/Regional | Penjual di Shopee | Optimasi judul/atribut produk (6.6 sebagian); auto-reply chat dasar (6.3 sebagian) | NLP untuk optimasi teks, auto-reply berbasis info produk | Gratis, terintegrasi native, klaim naik penjualan 18,6% dalam 3 bulan [INDUSTRY CLAIM] | Terkunci pada ekosistem Shopee, tidak mengolah ulasan menjadi insight actionable, tidak transparan/explainable | Tidak menjangkau penjual multi-kanal (WhatsApp, media sosial) atau ulasan lintas platform | Existing (untuk 6.3 sebagian), Adjacent (untuk 6.6) |
| Tokopedia Demand Prediction & Sistem Rekomendasi | Indonesia | Penjual & konsumen Tokopedia | Prediksi permintaan lokasi, rekomendasi produk berbasis histori (6.6 sebagian) | Machine learning demand prediction, recommendation engine | Skala data besar (14 juta penjual, 1,8 miliar produk) [INDUSTRY CLAIM] | Black-box bagi penjual kecil, cold-start untuk penjual/produk baru belum tentu tertangani optimal | Tidak ada lapisan insight ulasan-ke-aksi untuk UMKM | Existing (untuk 6.6 sebagian), Adjacent (untuk 6.7) |
| Qiscus Omnichannel Chat + AgentLabs | Indonesia | Bisnis menengah-besar, sebagian UMKM | Konsolidasi chat multi-kanal, AI Agent auto-reply 24/7 (6.3) | NLP rule-based & AI-based auto-reply | Integrasi WhatsApp, Instagram, marketplace dalam satu dashboard | Harga premium kurang terjangkau UMKM mikro; tidak fokus pada insight ulasan/harga | Positioning ke bisnis menengah-atas, gap harga untuk usaha sangat mikro | Existing (untuk 6.3), Substitute mahal bagi UMKM mikro |
| Kata.ai (Kata Omnichat) | Indonesia | Bisnis menengah-besar | Chatbot berbahasa Indonesia, integrasi CS manusia+bot (6.3) | NLP Bahasa Indonesia, conversational AI | Diklaim AI Bahasa Indonesia terbaik di kategorinya [INDUSTRY CLAIM] | Harga premium, kurang terjangkau UMKM mikro | Sama seperti Qiscus - gap harga untuk mikro | Existing (untuk 6.3), Substitute mahal bagi UMKM mikro |
| Jubelio / Ginee (Omnichannel Management) | Indonesia | UMKM-menengah multi-channel | Sinkronisasi stok/pesanan lintas kanal (6.14 sebagian) | Otomasi rule-based, belum tentu AI prediktif penuh | Membantu operasional dasar multi-channel | Fokus pada sinkronisasi, bukan analitik margin bersih komparatif berbasis AI | Belum ditemukan fitur eksplisit estimasi margin bersih otomatis per kanal | Adjacent (untuk 6.14) |
| Fakespot / Review analysis tools (internasional) | AS/Global | Konsumen & penjual di Amazon | Deteksi ulasan tidak wajar (6.2) | NLP & machine learning klasifikasi ulasan | Sudah matang untuk ekosistem Amazon/Inggris | Tidak mendukung Bahasa Indonesia/marketplace lokal (Shopee/Tokopedia) | Language gap dan platform gap total untuk konteks Indonesia | Similar (mekanisme), tidak Existing di Indonesia |
| Trustpilot-style review verification | Global | Konsumen & bisnis | Verifikasi ulasan pihak ketiga (6.2) | Rule-based + moderasi manusia, AI terbatas | Model bisnis independen dari marketplace | Adopsi di Indonesia rendah, tidak terintegrasi UMKM lokal | Adoption gap di pasar Indonesia | Similar |
| VISUA / Fygurs (Counterfeit detection SaaS) | Global | Brand besar, marketplace | Deteksi produk tiruan berbasis visual AI (6.8) | Computer vision, image recognition | Teknologi matang untuk brand besar | Harga enterprise, tidak dirancang untuk UMKM individual | Population gap - fokus ke brand besar, bukan UMKM/produk kerajinan lokal | Similar, Substitute tidak terjangkau UMKM |
| Voice-enabled shopping assistant (riset akademik) | Global (riset) | Konsumen tunanetra/low vision | Navigasi belanja berbasis suara (6.13) | Speech-to-text, text-to-speech, image captioning | Terbukti meningkatkan task success rate pada uji terbatas [RESEARCH FINDING] | Masih prototipe riset, belum produk komersial di Indonesia | Localization gap total untuk Indonesia | Research prototype |
| Tools BI/CRM enterprise (Salesforce, HubSpot, dsb.) | Global | Perusahaan menengah-besar | Analitik pelanggan & churn (6.9, 6.15) | Predictive analytics, dashboard AI | Fitur matang dan komprehensif | Harga dan kompleksitas jauh di luar jangkauan UMKM mikro Indonesia | UMKM adoption gap - harga & kompleksitas tidak sesuai skala mikro | Substitute tidak terjangkau UMKM |
| Kalkulator HPP/harga jual manual (artikel, template Excel) | Indonesia | UMKM umum | Panduan dasar penetapan harga (6.1) | Tidak ada AI - murni rule/template statis | Gratis dan mudah diakses | Statis, tidak terhubung data biaya platform real-time atau data kompetitor dinamis | Tidak ada versi yang mengintegrasikan AI/data dinamis | Substitute non-AI |

Kesimpulan pemetaan: untuk masalah 6.12 (insight ulasan menjadi keputusan bisnis) dan 6.1 (penetapan harga), TIDAK ditemukan solusi Existing yang secara spesifik menggabungkan analitik Bahasa Indonesia informal dengan output keputusan bisnis siap pakai untuk UMKM skala mikro dalam penelusuran ini [INFERENCE dari cakupan pencarian yang dilakukan, bukan klaim mutlak "belum pernah ada" - lihat batasan pada bagian 25].


## 12. Research Gap Analysis

| Jenis Gap | Bukti Jurnal | Bukti Produk Existing | Mengapa Penting | Dapat Diselesaikan via MVP? | Risiko Gap Terlalu Kecil | Potensi Novelty |
| --- | --- | --- | --- | --- | --- | --- |
| Language gap | Sebagian besar studi fake-review & explainability berbasis Bahasa Inggris (bagian 9.1, 9.3) | Fakespot/Trustpilot tidak mendukung Bahasa Indonesia | Bahasa Indonesia informal (slang, campur bahasa daerah) memiliki pola berbeda dari Inggris formal | Ya, untuk ide berbasis NLP (InsightUlasan) dengan fine-tuning IndoBERT | Rendah - gap ini didukung banyak studi konsisten | Novelty implementasi/konteks Indonesia |
| Localization gap | Riset accessibility & fake-review dominan konteks negara maju (9.1, 9.8) | Voice-shopping masih riset prototipe, belum produk Indonesia | Perilaku & kebutuhan konsumen Indonesia berbeda (bagian 5) | Sebagian - accessibility MVP kompleks secara teknis | Sedang | Novelty konteks Indonesia |
| UMKM adoption gap | Kerangka TOE/TTF menunjukkan adopsi AI UMKM ditentukan kesesuaian tugas-teknologi (9.6) | Tools BI/CRM enterprise tidak terjangkau UMKM (11) | 66 juta UMKM menyumbang >60% PDB namun hanya ~30% aktif digital (bagian 5, 8) | Ya - MVP dapat dirancang khusus skala mikro dengan input sederhana | Rendah | Novelty produk & dampak sosial |
| Data gap (Indonesia-specific) | Dataset fake-review Bahasa Indonesia berlabel tidak ditemukan (9.1); dataset counterfeit UMKM tidak ditemukan (9.7) | - | Model butuh data representatif konteks lokal untuk akurasi & fairness | Tergantung ide - TINGGI untuk InsightUlasan (dataset tersedia), RENDAH untuk UlasanAsli/DeteksiTiru | Tinggi untuk ide dengan dataset gap besar (6.2, 6.8) | Novelty ilmiah jika berhasil menyusun dataset baru, namun berisiko tinggi untuk MVP kompetisi |
| Methodological gap | Penelitian sentimen berhenti di klasifikasi, belum menjembatani ke rekomendasi aksi bisnis (9.4, 10.4) | Dashboard rating marketplace hanya tampilkan skor rata-rata (11) | Pemilik usaha butuh output actionable, bukan sekadar skor sentimen | Ya - inti dari ide InsightUlasan | Rendah - gap ini paling terdokumentasi jelas dan konsisten | Novelty teknis (pipeline sentimen-ke-keputusan) dan novelty produk |
| Evaluation gap | Metrik penelitian churn/rekomendasi umumnya teknis (F1, AUC), jarang menyertakan metrik bisnis (10.3, 10.9) | - | Juri kompetisi menilai dampak bisnis, bukan hanya metrik ML | Ya - dapat ditambahkan sebagai proxy metric pada MVP manapun | Rendah | Novelty implementasi (menghubungkan metrik teknis-bisnis) |
| Accessibility gap | Riset AI accessibility terkonsentrasi pada disabilitas visual, minim untuk gangguan lain (9.8) | Belum ada solusi Indonesia yang matang (11) | Domain eksplisit disebut rulebook (digital inclusion, accessibility) | Sedang - kompleksitas multimodal tinggi relatif terhadap batasan MVP | Sedang | Novelty dampak sosial tinggi, novelty teknis sedang |
| Trust gap | Trust chatbot dibentuk dimensi kognitif+emosional (9.2); explainability tingkatkan trust SME (9.6) | Fitur "kenapa direkomendasikan" pada platform besar bersifat generik (11) | UMKM skeptis pada rekomendasi otomatis tanpa alasan jelas (persona 7.2) | Ya - dapat diintegrasikan sebagai lapisan penjelasan pada ide manapun | Rendah | Novelty implementasi (desain explainability spesifik UMKM) |
| Explainability gap | Sama seperti trust gap; recommendation research agenda 2024 menyoroti tren menuju explainability (9.3) | Rekomendasi Tokopedia/Shopee tidak transparan ke penjual kecil (11) | Kepercayaan pengguna terhadap AI adalah prasyarat adopsi (9.6) | Ya | Rendah | Novelty teknis sedang |
| Human-AI interaction gap | Minim riset AI membantu penjual pada volume tinggi interaksi live commerce real-time (10.5) | Fitur live shopping platform besar minim asisten balasan kontekstual per penjual (11) | Live/social commerce tumbuh sangat cepat di Indonesia (bagian 5) | Sedang - kendala real-time & scope MVP | Sedang | Novelty produk |
| Policy and compliance gap | KPPU mendorong regulasi pasar digital khusus terkait algoritma/AI (bagian 5, 8) | - | Solusi AI Smart Commerce perlu selaras dengan arah regulasi yang berkembang | Ya - dapat dijadikan pertimbangan desain governance (bagian 22) | Rendah | Novelty konteks kebijakan |
| Low-resource gap | Studi cold-start menekankan pentingnya metode untuk data minim (9.3, 10.3) | UMKM baru tidak punya histori data (persona Pak Wisnu, 7.2) | UMKM skala mikro secara struktural memiliki data terbatas | Ya, jika ide dirancang eksplisit untuk data kecil (RekomenUMKM, InsightUlasan skala kecil) | Rendah | Novelty teknis |
| Population gap | Riset counterfeit/BI enterprise fokus brand/perusahaan besar (9.7, 11) | VISUA/Fygurs, Salesforce menyasar enterprise (11) | UMKM mikro secara sistematis kurang terlayani riset maupun produk | Bervariasi per ide | Rendah untuk ide yang eksplisit menyasar UMKM mikro | Novelty dampak sosial |
| Context gap | Mayoritas benchmark akademik AI recommendation/fraud dari konteks global/negara maju (9.1, 9.3, 9.7) | Kompetitor global (Fakespot, VISUA) tidak beroperasi di Indonesia (11) | Pola perilaku, bahasa, dan struktur pasar Indonesia berbeda signifikan | Bervariasi per ide | Rendah-sedang | Novelty konteks Indonesia - berlaku luas ke semua kandidat ide |
| Deployment gap | Rulebook membatasi MVP pada inferensi lokal, bukan sistem produksi penuh (bagian 2.4-2.6) | - | Kesenjangan antara riset akademik (skala besar) dan kebutuhan MVP kompetisi (skala kecil, lokal) | Ya - relevan untuk semua ide, mendorong desain MVP yang ringkas | Rendah | Novelty implementasi (bagaimana riset akademik diadaptasi jadi MVP ringan) |


## 13. AI Necessity Analysis

Dianalisis untuk tiga kandidat solusi dengan skor kelayakan tertinggi pada bagian 6 (dasar bagi ide InsightUlasan, HargaCerdas, dan RekomenUMKM), menjawab dua puluh pertanyaan necessity secara ringkas dan disertai alternatif non-AI sebagai baseline eksplisit.


### 13.1 InsightUlasan (Aspect-Based Insight dari Ulasan/Chat UMKM)

| Aspek | Keterangan |
| --- | --- |
| Mengapa butuh AI? | Volume ulasan/chat besar dan berbahasa informal/campuran tidak dapat diproses konsisten secara manual maupun dengan pencarian kata kunci sederhana. |
| Mengapa tidak cukup dashboard biasa? | Dashboard hanya menampilkan skor rata-rata/daftar mentah; tidak dapat mengekstraksi ASPEK spesifik (kualitas, pengiriman, harga) dari teks bebas. |
| Mengapa tidak cukup pencarian database? | Pencarian kata kunci gagal menangkap sinonim, slang, typo, dan sarkasme yang umum pada ulasan Bahasa Indonesia informal. |
| Mengapa tidak cukup rule-based system? | Aturan manual (if-else kata kunci) rapuh terhadap variasi bahasa yang sangat luas dan cepat usang; riset menunjukkan model pre-trained (IndoBERT) signifikan mengungguli pendekatan sederhana (bagian 9.4). |
| Keputusan/prediksi yang dihasilkan | Klasifikasi aspek+sentimen per kalimat ulasan, lalu ringkasan prioritas aksi (mis. "30% keluhan soal ukuran - pertimbangkan perbaikan size chart"). |
| Pola yang tidak mudah diselesaikan manual | Menghitung distribusi keluhan per aspek dari ratusan/ribuan ulasan secara konsisten dan cepat. |
| Apakah output dapat diuji? | Ya - akurasi klasifikasi sentimen/aspek dapat diuji dengan data berlabel (PRDECT-ID, dataset sentimen HF); relevansi rekomendasi aksi dapat diuji via evaluasi pengguna (bagian 23). |
| Apakah tersedia ground truth? | Ya, sebagian - dataset publik berlabel sentimen/emosi tersedia (bagian 14); ground truth untuk "rekomendasi aksi optimal" perlu dibangun melalui uji pengguna. |
| Bagaimana menangani ketidakpastian? | Menampilkan confidence score dan kutipan ulasan asli sebagai bukti, bukan klaim absolut. |
| Konsekuensi false positive | Rekomendasi perbaikan pada aspek yang sebenarnya bukan masalah nyata - berisiko rendah karena pemilik usaha tetap memverifikasi via kutipan asli yang ditampilkan. |
| Konsekuensi false negative | Masalah nyata tidak terdeteksi - risiko sedang, dimitigasi dengan menampilkan tren dari waktu ke waktu bukan keputusan sekali jalan. |
| Human-in-the-loop diperlukan? | Ya - output berupa rekomendasi untuk dipertimbangkan pemilik usaha, bukan tindakan otomatis (mis. tidak otomatis mengubah harga/stok). |
| Explainability diperlukan? | Ya, tinggi - menampilkan kutipan ulasan asli sebagai bukti setiap klasifikasi aspek (sesuai temuan trust gap bagian 12). |
| Model kecil vs LLM? | Model kecil (fine-tuned IndoBERT/DistilBERT) lebih tepat untuk klasifikasi aspek/sentimen; LLM dapat digunakan terbatas untuk meringkas temuan menjadi bahasa naratif (RAG di atas hasil klasifikasi). |
| Apakah multimodal diperlukan? | Tidak - cukup berbasis teks untuk MVP. |
| Apakah RAG diperlukan? | Opsional - dapat digunakan pada lapisan peringkasan naratif akhir, dengan retrieval dari kutipan ulasan asli agar jawaban ter-ground dan tidak berhalusinasi. |
| Apakah agentic workflow diperlukan? | Tidak untuk MVP - cukup pipeline klasifikasi + ringkasan; agentic dapat menjadi pengembangan lanjutan (mis. auto-draft balasan ke pelanggan). |
| Apakah fine-tuning diperlukan? | Ya - fine-tuning IndoBERT/DistilBERT pada domain ulasan e-commerce merupakan bentuk kustomisasi utama sesuai ketentuan rulebook. |
| Apakah tool calling diperlukan? | Tidak esensial untuk MVP dasar. |
| Bentuk kustomisasi yang dapat dipertanggungjawabkan | Fine-tuning model klasifikasi aspek/sentimen pada dataset Bahasa Indonesia (PRDECT-ID/HF) yang digabung sampel data UMKM (jika tersedia saat validasi), plus prompt-engineering/RAG terstruktur untuk lapisan ringkasan. |


### 13.2 HargaCerdas (Asisten Penetapan Harga UMKM)

| Aspek | Keterangan |
| --- | --- |
| Mengapa butuh AI? | Estimasi margin optimal melibatkan banyak variabel (biaya platform dinamis, histori penjualan, sensitivitas harga) yang sulit dihitung manual secara konsisten. |
| Mengapa tidak cukup dashboard biasa? | Dashboard marketplace hanya menampilkan angka penjualan kotor, tidak mensimulasikan skenario harga alternatif. |
| Mengapa tidak cukup pencarian database? | Membandingkan harga kompetitor manual tidak memperhitungkan struktur biaya milik toko sendiri. |
| Mengapa tidak cukup rule-based? | Kalkulator HPP statis (rule sederhana: modal x margin%) sudah ada namun tidak adaptif terhadap perubahan biaya platform atau pola permintaan historis. |
| Keputusan/prediksi yang dihasilkan | Rentang harga yang direkomendasikan beserta proyeksi margin bersih pada beberapa skenario. |
| Pola yang tidak mudah diselesaikan manual | Trade-off harga-volume-margin lintas banyak skenario secara simultan. |
| Apakah output dapat diuji? | Ya - dapat dibandingkan terhadap baseline kalkulasi manual dan divalidasi terhadap data penjualan historis riil. |
| Apakah tersedia ground truth? | Terbatas - ground truth "harga optimal" bersifat kontrafaktual (tidak dapat diamati langsung tanpa eksperimen A/B), sehingga model bersifat estimasi/simulasi, bukan prediksi presisi tinggi. |
| Bagaimana menangani ketidakpastian? | Menyajikan rentang (bukan angka tunggal) dan asumsi yang mendasari secara eksplisit. |
| Konsekuensi false positive/negatif | Rekomendasi harga keliru dapat menyebabkan kerugian finansial nyata - risiko TINGGI, memerlukan disclaimer jelas bahwa ini alat bantu, bukan keputusan final otomatis. |
| Human-in-the-loop diperlukan? | Ya, mutlak - keputusan akhir harga tetap di tangan pemilik usaha. |
| Explainability diperlukan? | Ya, tinggi - harus menampilkan rincian komponen biaya yang menyusun rekomendasi. |
| Model kecil vs LLM? | Model regresi/optimasi sederhana (bukan LLM) lebih tepat untuk komponen kalkulasi inti; LLM opsional untuk menjelaskan hasil dalam bahasa natural. |
| Bentuk kustomisasi yang dapat dipertanggungjawabkan | Model regresi/simulasi yang dilatih atau dikalibrasi dari data biaya platform + data historis toko, bukan sekadar API call ke LLM umum. |


### 13.3 RekomenUMKM (Rekomendasi Produk untuk Toko/Produk Baru)

| Aspek | Keterangan |
| --- | --- |
| Mengapa butuh AI? | Cold-start pada sistem rekomendasi adalah masalah representasi (belum ada data interaksi) yang memerlukan pendekatan content-based/embedding, bukan sekadar aturan kategori manual. |
| Mengapa tidak cukup dashboard/database/rule-based? | Kategorisasi manual tidak dapat menangkap kemiripan semantik antar produk baru dan preferensi pembeli secara dinamis. |
| Keputusan/prediksi yang dihasilkan | Daftar kategori/audiens/kata kunci target untuk produk baru berdasarkan kemiripan konten dengan produk yang sudah terbukti laku. |
| Apakah output dapat diuji? | Ya - menggunakan metrik hit-rate@K pada skenario simulasi cold-start dari dataset produk yang ada (dataset producttopedia HF). |
| Apakah tersedia ground truth? | Sebagian - dapat disimulasikan dengan menyembunyikan histori interaksi produk yang sudah ada (standard cold-start evaluation protocol pada literatur, bagian 9.3). |
| Human-in-the-loop diperlukan? | Ya - rekomendasi kategori/audiens sebagai saran, keputusan final tetap pada penjual. |
| Explainability diperlukan? | Sedang-tinggi - perlu menjelaskan produk pembanding yang menjadi dasar rekomendasi. |
| Model kecil vs LLM? | Embedding teks (dapat menggunakan model kecil seperti sentence embedding Bahasa Indonesia) untuk mengukur kemiripan konten; tidak memerlukan LLM besar generatif. |
| Bentuk kustomisasi yang dapat dipertanggungjawabkan | Fine-tuning/adaptasi model embedding pada domain deskripsi produk marketplace Indonesia. |


### 13.4 Alternatif Non-AI sebagai Baseline (Wajib untuk Setiap Ide)

| Ide | Baseline Non-AI | Apakah Baseline Cukup? |
| --- | --- | --- |
| InsightUlasan | Membaca manual + pencatatan Excel sederhana per kategori keluhan | Tidak cukup pada volume >50-100 ulasan/bulan - waktu yang dibutuhkan tidak proporsional dengan kapasitas UMKM mikro (skor ide TIDAK diturunkan) |
| HargaCerdas | Kalkulator HPP manual/template Excel | Cukup untuk toko dengan <10 SKU dan biaya statis, TIDAK cukup saat biaya platform berubah dinamis dan variasi SKU besar (skor ide TIDAK diturunkan signifikan, namun perlu kejelasan kapan AI benar-benar unggul) |
| RekomenUMKM | Kategorisasi manual + iklan berbayar untuk visibilitas awal | Cukup jika modal iklan tersedia, TIDAK cukup bagi penjual bermodal terbatas (skor ide TIDAK diturunkan, mengingat modal terbatas adalah kondisi mayoritas UMKM mikro) |

Sesuai arahan riset, apabila baseline sederhana sudah cukup menyelesaikan masalah, skor ide tersebut diturunkan. Ketiga ide di atas mempertahankan skor karena baseline non-AI terbukti tidak proporsional/tidak cukup pada skala dan kondisi mayoritas UMKM mikro Indonesia (data terbatas, waktu terbatas, modal terbatas).


### 13.5 Baseline AI Sederhana: Zero-Shot LLM API Langsung Tanpa Kustomisasi (Pembaruan v6)

Bagian 13.4 hanya membandingkan AI vs NON-AI. Ini menutup celah metodologis: objection yang lebih kuat dan lebih mungkin muncul dari juri bukan "kenapa pakai AI", melainkan "kenapa pakai pipeline serumit ini - kenapa tidak langsung prompt LLM API (GPT-4o/Claude/Gemini) dan biarkan model itu mengekstrak insight secara otomatis?" Ini pertanyaan yang lebih tajam dan wajib dijawab eksplisit, bukan diasumsikan terjawab oleh section 13.4.

Jawaban jujur: JIKA ukurannya semata-mata "kualitas insight/ringkasan yang dihasilkan", zero-shot prompting ke LLM API frontier modern KEMUNGKINAN BESAR menghasilkan kualitas setara atau lebih baik daripada pipeline fine-tuned IndoBERT+CLIP+orchestrator ini, dengan effort development jauh lebih sedikit [ASUMSI, belum diuji head-to-head - lihat rencana pengujian di baris terakhir tabel]. Dossier ini TIDAK mengklaim pipeline yang diusulkan menghasilkan insight yang secara kualitatif lebih unggul. Klaim yang benar dan dapat dipertahankan adalah pipeline ini unggul pada sumbu-sumbu lain yang juga dinilai rubrik kompetisi.

| Sumbu Perbandingan | Zero-Shot LLM API Langsung | Pipeline yang Diusulkan (Fine-tuned+CLIP+Orchestrator) |
| --- | --- | --- |
| Kepatuhan syarat kustomisasi wajib rulebook (bagian 2.9) | GAGAL - klarifikasi resmi panitia eksplisit menyatakan tujuan aturan adalah "supaya kalian tidak sekadar menggunakan model mentah (zero-shot API call biasa)" - deskripsi ini persis menggambarkan pendekatan ini | MEMENUHI - fine-tuning teks + training model pendukung visual + tool calling/RAG, tiga rute sekaligus (bagian 2.9, 21) |
| Reproducibility oleh juri (bagian 2.6) | Rendah - juri perlu API key/kredit sendiri, hasil dapat bervariasi antar run (non-deterministic), bergantung ketersediaan layanan pihak ketiga saat cross-check | Tinggi - model lokal open-weight, dapat dijalankan ulang tanpa dependency eksternal berbayar |
| Biaya operasional pada skala nyata (ribuan ulasan/UMKM) | Tinggi dan linear terhadap volume - tidak sejalan dengan model bisnis freemium untuk UMKM mikro (bagian 21B.4) | Rendah - model kecil sekali dilatih, inferensi lokal jauh lebih murah per unit |
| Konsistensi/auditability output antar run | Sedang - rentan variasi frasa/kategori antar pemanggilan API akibat sifat generatif | Tinggi - classifier menghasilkan label deterministik dengan confidence score, RAG tetap ter-ground pada kutipan asli |
| Kecepatan development/kompleksitas engineering | Tinggi (cepat dibangun, risiko engineering rendah) | Sedang (lebih banyak komponen, risiko integrasi lebih tinggi - trade-off yang disadari, bagian 21B.1) |
| Kualitas insight/ringkasan naratif akhir | Kemungkinan setara atau lebih baik - BELUM diuji head-to-head [REQUIRES USER VALIDATION] | Kemungkinan setara - klaim "lebih baik" TIDAK dibuat tanpa bukti |

Kesimpulan bagian ini: alasan utama TIDAK memilih zero-shot LLM API murni bukan karena hasilnya pasti lebih buruk, melainkan karena pendekatan itu (a) secara eksplisit gagal memenuhi syarat kustomisasi wajib kompetisi menurut kata-kata panitia sendiri, (b) lebih sulit direproduksi juri, dan (c) tidak proporsional secara biaya untuk model bisnis yang menyasar UMKM mikro. Argumen ini bersifat rules-compliance dan operasional, BUKAN argumen "AI kami pasti menghasilkan insight lebih pintar" - kejujuran ini penting dipertahankan saat sesi tanya-jawab juri agar tim tidak overclaim.

Rencana pengujian untuk menutup [REQUIRES USER VALIDATION] di atas: jalankan zero-shot prompting terstruktur (JSON output) pada 30-50 sampel ulasan yang sama dengan yang dipakai validasi Langkah 4 (bagian 21B.2), bandingkan konsistensi kategori aspek yang dihasilkan LLM API vs classifier fine-tuned pada input yang identik diulang 3x, dan dokumentasikan hasilnya sebagai bukti kuantitatif konsistensi - bukan klaim tanpa data (bagian 24, Technical Experiment Plan).


## 14. Dataset Feasibility


### 14.1 Tabel Dataset Kandidat

| Dataset | Sumber | Lisensi | Ukuran | Fitur/Label | Relevansi Indonesia | Kualitas Data | Keterbatasan | Skor Kelayakan |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tokopedia Product Reviews 2019 | Hugging Face (farhamu/tokopedia-product-reviews-2019) | Tidak eksplisit dicantumkan - perlu verifikasi sebelum publikasi ulang | 40.607 ulasan | Teks ulasan, rating, nama produk | Tinggi - data asli platform Indonesia | Sedang - data 2019, kemungkinan ada noise/duplikasi | Data cukup lama (2019), tidak mencakup tren bahasa/produk terbaru | Tinggi untuk InsightUlasan |
| e-commerce-sentiment-bahasa-indonesia | Hugging Face (joyadriansyah / AIbnuHibban) | Tidak eksplisit dicantumkan - perlu verifikasi | 21.840 komentar berlabel | Teks komentar, label sentimen (positif/netral/negatif) | Tinggi - eksplisit Bahasa Indonesia, termasuk sarkasme/ironi | Sedang-tinggi - sudah berlabel | Label hanya sentimen umum, belum granular per-aspek | Tinggi untuk InsightUlasan |
| PRDECT-ID (Indonesian Emotion Classification) | Kaggle (jocelyndumlao/prdect-id) | Perlu verifikasi lisensi di halaman Kaggle | Tidak disebutkan eksplisit pada cuplikan pencarian | Teks ulasan, label emosi | Tinggi - nama menunjukkan dataset ulasan produk Indonesia (Product Review Dataset for Emotion Classification Tasks - ID) | Perlu verifikasi langsung | Detail metodologi anotasi perlu ditelaah dari sumber asli | Tinggi untuk InsightUlasan, perlu verifikasi lanjutan |
| Indonesian Marketplace Product Reviews | Kaggle (taqiyyaghazi) | Perlu verifikasi lisensi di halaman Kaggle | Tidak disebutkan eksplisit | Teks ulasan, label sentimen (anotasi manual) | Tinggi | Sedang - anotasi manual skala kecil (dikumpulkan 2022) | Ukuran sampel relatif kecil untuk fine-tuning penuh | Sedang-tinggi untuk InsightUlasan |
| E-Commerce Ratings and Reviews in Bahasa Indonesia | Kaggle (satyaahb) | Perlu verifikasi lisensi | Tidak disebutkan eksplisit | Rating 1-5, teks ulasan (scraped dari Google Play Store) | Tinggi | Sedang - ulasan aplikasi, bukan ulasan produk langsung | Konteksnya ulasan APLIKASI e-commerce, bukan ulasan PRODUK - perlu penyesuaian scope | Sedang untuk InsightUlasan (butuh scoping ulang) |
| Indonesia E-Commerce Sales & Shipping 2023-2025 | Kaggle (bakitacos) | Perlu verifikasi lisensi | Tidak disebutkan eksplisit | Data transaksi, pengiriman | Tinggi | Perlu verifikasi kualitas/sumber data (kemungkinan data sintetik) | Kemungkinan data sintetik/simulasi, bukan data transaksi riil - perlu verifikasi eksplisit sebelum dipakai untuk HargaCerdas | Sedang untuk HargaCerdas, perlu verifikasi sumber |
| Skema biaya resmi marketplace (Shopee/Tokopedia) | Halaman kebijakan resmi marketplace | Publik, bukan dataset formal | N/A - dokumen kebijakan | Struktur komisi, biaya layanan | Tinggi - sumber langsung Indonesia | Tinggi - data resmi dari sumber utama | Berubah sewaktu-waktu, perlu pembaruan berkala | Tinggi untuk HargaCerdas (sebagai input aturan/parameter, bukan data latih ML) |
| CSP Dataset (Cold-Start Problem) | MDPI Information 14(1):19 | CC BY (umum untuk artikel MDPI, perlu verifikasi halaman spesifik) | Tidak disebutkan eksplisit pada cuplikan | Interaksi user-item terstruktur untuk skenario cold-start | Rendah - tidak spesifik Indonesia | Tinggi - didesain khusus riset | Tidak dapat langsung dipakai, hanya sebagai referensi desain evaluasi | Sedang untuk RekomenUMKM (referensi metodologi, bukan data utama) |
| Shopee Product Reviews (via Apify, akuisisi mandiri, Pembaruan v5) | Scraping bertarget menggunakan actor zen-studio/shopee-product-reviews-scraper di platform Apify (bagian 21B.6) | Data publik terlihat; tunduk pada ToS Shopee dan UU PDP untuk elemen data pribadi - PARTIALLY VERIFIED, lihat 21B.6.3 | ~250-300 ulasan berfoto dalam anggaran gratis $5/bulan, dapat diperluas bertahap | Foto ulasan (URL CDN), teks, rating, sub-rating per aspek, varian dibeli - 27 field/baris | Tinggi - dapat difokuskan pada listing produk UMKM/fesyen/F&B Indonesia (shopee.co.id) | Tinggi - data langsung dari platform, real-time saat scraping | Volume kecil (untuk validasi/kalibrasi, BUKAN pretraining skala besar); belum ada jaminan distribusi kategori produk merata | Tinggi KHUSUS untuk validasi modul visual InsightUlasan (bukan pengganti dataset teks utama) |

Baris terakhir pada tabel di atas adalah sumber BARU sejak Pembaruan v5, ditambahkan setelah tim memutuskan menjadikan computer vision sebagai komponen wajib (bagian 21B.1) dan menutup gap data visual yang sebelumnya ditandai [DATA GAP] pada versi v4 dossier ini.


### 14.2 Studi Kelayakan Dataset untuk Ide Prioritas (InsightUlasan)

| Aspek | Keterangan |
| --- | --- |
| Data yang dibutuhkan | Teks ulasan/chat pelanggan UMKM berbahasa Indonesia (formal & informal) |
| Unit observasi | Satu ulasan/pesan per baris data |
| Feature yang dibutuhkan | Teks ulasan, rating (jika tersedia), metadata produk/kategori (opsional) |
| Target/label | Kategori aspek (kualitas, pengiriman, harga, pelayanan) dan polaritas sentimen per aspek |
| Sumber data | Kombinasi dataset publik (PRDECT-ID, e-commerce-sentiment-bahasa-indonesia, Tokopedia reviews) untuk pretraining/fine-tuning awal, ditambah data uji dari UMKM mitra riset (perlu dikumpulkan pada tahap validasi) |
| Lisensi | Perlu verifikasi eksplisit per dataset Kaggle/HuggingFace sebelum digunakan pada proposal final - beberapa tidak mencantumkan lisensi jelas dalam cuplikan pencarian [REQUIRES USER VALIDATION] |
| Format | CSV/JSON teks + label |
| Bahasa | Bahasa Indonesia (formal & informal/campuran) |
| Ukuran dataset | Puluhan ribu baris tersedia gabungan (>60.000 dari 2-3 dataset utama) - cukup untuk fine-tuning model kecil (IndoBERT/DistilBERT) |
| Data imbalance | Kemungkinan tinggi - ulasan positif biasanya jauh lebih banyak dari negatif pada marketplace [ASUMSI berdasar pola umum e-commerce, perlu verifikasi distribusi aktual per dataset] |
| Missing value | Berpotensi ada pada field metadata (kategori produk); teks ulasan umumnya lengkap |
| Potensi bias | Ulasan cenderung bias terhadap pengguna yang lebih vokal (sangat puas/sangat kecewa); UMKM sangat kecil mungkin kurang terwakili dalam dataset publik yang umumnya dari toko besar/aktif |
| Potensi data leakage | Rendah untuk task klasifikasi sentimen dasar; perlu diperhatikan jika data testing dan training berasal dari toko/periode yang sama |
| Privasi & informasi pribadi | Ulasan publik umumnya tidak memuat data pribadi sensitif, namun chat pelanggan (jika digunakan) berpotensi memuat nomor telepon/alamat - WAJIB dianonimkan |
| Cara anonimisasi | Masking otomatis pola nomor telepon/alamat sebelum data chat digunakan untuk pelatihan/demo |
| Kebutuhan data tambahan | Data ulasan/chat riil dari 3-5 UMKM mitra untuk validasi kualitatif hasil model (lihat bagian 23) |
| Kemungkinan data sintetik | Dapat disintesis contoh kalimat ulasan tambahan untuk memperkaya kategori aspek yang kurang terwakili, dengan penandaan jelas sebagai data sintetik |
| Strategi validasi data sintetik | Validasi manual oleh tim terhadap sampel acak data sintetik untuk memastikan realistis sebelum dicampur ke data latih |
| Kelayakan pengumpulan selama periode lomba | Tinggi - dataset publik sudah cukup untuk MVP awal; pengumpulan data UMKM mitra tambahan realistis dilakukan pada periode 17 Juni-25 Agustus 2026 melalui kontak komunitas UMKM |


## 15. Candidate AI Methods

| Kelompok Metode | Kesesuaian dengan Masalah Prioritas | Kebutuhan Komputasi | Interpretability | Kemungkinan Jalan Lokal | Dependency API Eksternal | Kesesuaian MVP |
| --- | --- | --- | --- | --- | --- | --- |
| Classification (klasifikasi sentimen/aspek/churn) | Tinggi - inti InsightUlasan, churn UMKM | Rendah-sedang (model kecil seperti DistilBERT dapat jalan di CPU) | Sedang-tinggi (dapat ditambah SHAP/attention visualization) | Tinggi | Rendah | Tinggi |
| Regression (estimasi margin/harga) | Tinggi - inti HargaCerdas | Rendah | Tinggi (koefisien mudah dijelaskan) | Tinggi | Rendah | Tinggi |
| Ranking/Recommendation | Tinggi - inti RekomenUMKM | Sedang (embedding generation) | Sedang | Tinggi | Rendah-sedang (jika pakai API embedding) | Tinggi |
| Time-series forecasting | Sedang - relevan untuk restock/promosi (6.15) | Sedang | Sedang | Tinggi | Rendah | Sedang |
| Anomaly detection | Sedang - relevan deteksi penipuan (6.11) | Sedang | Sedang-rendah | Tinggi | Rendah | Sedang |
| Clustering | Sedang - segmentasi pelanggan untuk churn (6.9) | Rendah | Tinggi | Tinggi | Rendah | Tinggi |
| Causal inference / Uplift modeling | Sedang - efektivitas promosi (6.10) | Sedang | Sedang | Tinggi | Rendah | Sedang (butuh data eksperimen yang sering tidak tersedia UMKM) |
| Natural Language Processing (umum) | Tinggi - dasar InsightUlasan, BalasCepat | Rendah-sedang | Sedang | Tinggi | Rendah-sedang | Tinggi |
| Information extraction | Tinggi - ekstraksi aspek dari ulasan | Rendah-sedang | Sedang-tinggi | Tinggi | Rendah | Tinggi |
| Aspect-based sentiment analysis | Tinggi - inti InsightUlasan | Rendah-sedang | Tinggi (per-aspek) | Tinggi | Rendah | Tinggi |
| Computer vision | DIPERBARUI: Sedang-tinggi - relevan DeteksiTiru (6.8, risiko dataset tinggi) DAN sebagai modul pendukung terikat lingkup pada InsightUlasan untuk mengklasifikasi foto ulasan (barang rusak/salah kirim/tidak sesuai) yang lazim diunggah pembeli di marketplace Indonesia namun terlewat oleh pendekatan text-only | Sedang (ringan jika hanya classifier di atas vision encoder beku, bukan CNN dari nol) | Sedang | Tinggi (model kecil/frozen encoder + linear head) | Rendah | Tinggi untuk modul pendukung terikat lingkup; Sedang untuk DeteksiTiru sebagai ide mandiri |
| Multimodal learning | Rendah-sedang - relevan aksesibilitas (6.13) | Tinggi | Rendah | Sedang | Sedang | Rendah untuk MVP (kompleksitas tinggi) |
| Retrieval-Augmented Generation | Sedang - lapisan ringkasan InsightUlasan, BalasCepat | Sedang (butuh vektor database ringan) | Tinggi (jawaban ter-ground pada sumber) | Tinggi (dapat pakai vector DB lokal) | Rendah-sedang | Tinggi |
| Knowledge graph | Rendah - belum ada kebutuhan eksplisit pada 15 masalah | Sedang-tinggi | Tinggi | Sedang | Rendah | Rendah untuk MVP (kompleksitas relatif terhadap manfaat) |
| Agentic workflow | Rendah-sedang - berguna untuk BalasCepat lanjutan (tool-calling ke data stok) | Sedang | Sedang | Sedang | Sedang-tinggi (bergantung tool eksternal) | Sedang (berisiko overbuilt jika berlebihan, bagian 2.14) |
| Tool-using LLM | Sedang - BalasCepat (cek stok), sebagai pelengkap | Sedang | Sedang | Sedang | Sedang | Sedang |
| Small language model (fine-tuned) | Tinggi - IndoBERT/DistilBERT untuk InsightUlasan | Rendah | Tinggi | Tinggi | Rendah | Tinggi |
| Fine-tuned transformer | Tinggi - bentuk kustomisasi utama sesuai rulebook | Rendah-sedang | Sedang-tinggi | Tinggi | Rendah | Tinggi |
| Hybrid rule-based + ML | Tinggi - HargaCerdas (aturan biaya + estimasi ML) | Rendah | Tinggi | Tinggi | Rendah | Tinggi |
| Human-in-the-loop AI | Tinggi - wajib untuk seluruh ide dengan konsekuensi finansial (13.1-13.3) | Rendah (aspek desain, bukan komputasi) | Tinggi | Tinggi | Rendah | Tinggi |

Kesimpulan: dossier ini secara sadar menghindari penggunaan generative AI/LLM besar sebagai komponen INTI pada ide prioritas (InsightUlasan, HargaCerdas, RekomenUMKM) - LLM/RAG hanya diposisikan sebagai lapisan orkestrasi/peringkasan, sementara inti teknis tetap pada model klasifikasi/regresi/embedding yang lebih ringan, dapat dijalankan lokal, dan lebih mudah dijelaskan (explainable) sesuai temuan trust gap pada bagian 12.

DIPERBARUI pasca klarifikasi panitia (bagian 2.9): arsitektur InsightUlasan direvisi menjadi hybrid MULTIMODAL dan AGENTIC secara terbatas (bounded), bukan text-only. Alasannya bukan sekadar mengejar kompleksitas teknis, melainkan menutup gap nyata - ulasan bergambar (foto bukti barang rusak, salah kirim, warna/ukuran tidak sesuai) sangat umum pada marketplace Indonesia dan sepenuhnya terlewat oleh pipeline berbasis teks saja. Arsitektur yang direvisi terdiri dari tiga komponen: (1) model pendukung teks - fine-tuned IndoBERT/DistilBERT untuk klasifikasi aspek-sentimen (memenuhi rute fine-tuning); (2) model pendukung visual - classifier ringan (linear/shallow head) di atas vision encoder pre-trained yang dibekukan (mis. CLIP), dilatih pada label kategori visual terbatas (barang rusak, salah kirim, kemasan rusak) sehingga tetap ringan secara komputasi dan sesuai batasan MVP (memenuhi rute training model pendukung terintegrasi foundation model); (3) foundation model (LLM) sebagai orkestrator yang memanggil kedua model pendukung tersebut sebagai TOOLS ketika sebuah ulasan menyertakan foto (memenuhi rute tool calling/agentic workflow), lalu menyusun ringkasan akhir dengan RAG yang ter-ground pada kutipan teks dan label visual asli (memenuhi rute RAG). Foto tetap OPSIONAL per entri ulasan (graceful degradation ke jalur teks-saja bila tidak ada foto) agar alur tetap satu input tunggal -> satu output tunggal sesuai batasan MVP rulebook, tidak menambah kompleksitas frontend/backend di luar core inference.


## 16. Eight to Twelve Idea Candidates

Sembilan kandidat ide berikut lahir langsung dari 15 masalah dan gap riset pada bagian 6 dan 12. Maksimal dua ide (BalasCepat dan TemanBelanja) menggunakan antarmuka percakapan sebagai interaksi utama, sesuai batasan yang diberikan.


### 16.1. InsightUlasan - Mesin Insight Bisnis dari Ulasan & Chat Pelanggan UMKM

| Aspek | Keterangan |
| --- | --- |
| One-sentence concept | Mengubah kumpulan ulasan/chat pelanggan Bahasa Indonesia informal menjadi ringkasan aspek bermasalah dan rekomendasi aksi bisnis terprioritas. |
| Masalah utama | 6.12 - ulasan & chat tidak diubah menjadi insight actionable |
| Target pengguna | UMKM skala mikro-kecil dengan volume ulasan/chat menengah-tinggi |
| Bukti masalah | 4,40 juta unit usaha e-commerce Indonesia mayoritas mikro (BPS 2024); gap metodologis - penelitian sentimen berhenti di klasifikasi, belum menjembatani ke rekomendasi aksi (bagian 10.4) |
| Existing solution | Dashboard rating marketplace (skor rata-rata mentah) - Adjacent, bukan Existing penuh (bagian 11) |
| Gap | Methodological gap dan language gap (bagian 12) - paling terdokumentasi kuat di antara seluruh kandidat |
| Proposed AI capability | DIPERBARUI (multimodal+agentic terikat lingkup): fine-tuned IndoBERT/DistilBERT untuk klasifikasi aspek+sentimen teks; classifier ringan di atas vision encoder beku untuk kategori visual dari foto ulasan (opsional per entri: barang rusak/salah kirim/kemasan rusak); foundation model (LLM) sebagai orkestrator yang memanggil kedua model tersebut via tool calling dan menyusun ringkasan via RAG ter-ground pada kutipan teks+temuan visual |
| Input tunggal MVP | Satu batch data ulasan (teks; foto opsional per entri jika tersedia) - tetap satu alur input tunggal sesuai batasan MVP |
| Output utama MVP | Ringkasan insight per aspek + daftar rekomendasi aksi terprioritas dengan kutipan pendukung |
| Nilai bagi pengguna | Menghemat waktu membaca manual, keputusan perbaikan produk berbasis data |
| Nilai ekonomi | Potensi kenaikan rating & retensi pelanggan melalui perbaikan yang lebih tepat sasaran (proxy metric, belum terukur langsung - REQUIRES USER VALIDATION) |
| Dampak sosial | Digital inclusion untuk UMKM - alat analitik profesional tanpa perlu tim data science |
| Dataset | PRDECT-ID, e-commerce-sentiment-bahasa-indonesia, Tokopedia reviews (bagian 14) - TINGGI ketersediaan |
| Ground truth | Tersedia sebagian dari dataset berlabel publik; perlu tambahan validasi kualitatif pengguna |
| Baseline | Membaca manual/pencatatan Excel (bagian 13.4) - terbukti tidak proporsional pada volume tinggi |
| Metrik teknis | F1-score klasifikasi aspek/sentimen |
| Metrik bisnis | Waktu yang dihemat pemilik usaha, tingkat kesesuaian rekomendasi menurut evaluasi pengguna (proxy) |
| Bentuk kustomisasi AI | Kombinasi 3 rute yang diizinkan klarifikasi resmi panitia (bagian 2.9): fine-tuning model pendukung teks (IndoBERT/DistilBERT), training model pendukung visual (classifier ringan di atas vision encoder beku), dan tool calling+RAG pada lapisan foundation model orkestrator |
| Risiko | Kesalahan ekstraksi pada teks sangat informal/typo; risiko data imbalance; TAMBAHAN - dataset foto ulasan berlabel kategori visual Bahasa Indonesia belum ditemukan publik (DATA GAP baru, perlu dataset kecil buatan tim/anotasi manual sampel foto ulasan saat validasi) |
| Mitigasi | Menampilkan confidence score dan kutipan asli; augmentasi data sintetik terverifikasi manual untuk kelas minoritas |
| Estimasi kompleksitas | Sedang - komponen visual sengaja dibatasi (classifier ringan pada encoder beku, BUKAN training CNN dari nol) agar total kompleksitas tetap proporsional untuk MVP; risiko overbuilt dimitigasi dengan menjadikan foto sebagai input opsional, bukan wajib |
| Kesesuaian batasan kompetisi | Tinggi - satu alur input-output, dapat dijalankan lokal, tidak butuh hardware khusus |
| Novelty | DIPERBARUI (naik): novelty implementasi & konteks Indonesia (menjembatani sentimen ke rekomendasi aksi bisnis UMKM Bahasa Indonesia informal), DIPERKUAT novelty teknis dari arsitektur hybrid multimodal+agentic (teks+foto, tool calling) yang belum ditemukan pada kompetitor/literatur yang ditelusuri (bagian 11) |
| Alasan dapat kalah | Terkesan "hanya sentiment analysis" jika tidak dikomunikasikan jelas bedanya dengan tools existing pada video promosi |
| Alasan dapat menang | Kombinasi dataset siap pakai, gap literatur jelas, dan relevansi langsung ke tema "backbone of economy" (UMKM = 60% PDB) |


### 16.2. HargaCerdas - Asisten Simulasi Harga & Margin untuk UMKM

| Aspek | Keterangan |
| --- | --- |
| One-sentence concept | Mensimulasikan rentang harga jual optimal dan proyeksi margin bersih UMKM setelah memperhitungkan biaya platform berlapis. |
| Masalah utama | 6.1 dan 6.14 - penetapan harga dan optimasi biaya lintas kanal |
| Target pengguna | UMKM penjual marketplace dengan struktur biaya kompleks (komisi+ongkir+promo+iklan) |
| Bukti masalah | Total biaya platform dapat mencapai 15-20% harga jual (Kompas.com 2026); kesalahan umum UMKM hanya menghitung modal tanpa biaya operasional penuh (bagian 6.1) |
| Existing solution | Kalkulator HPP manual/template Excel - Substitute non-AI statis (bagian 11) |
| Gap | Tidak ada alat yang menggabungkan struktur biaya dinamis dengan simulasi skenario berbasis data historis toko |
| Proposed AI capability | Model regresi/simulasi margin dengan parameter biaya dapat diperbarui, dikombinasikan hybrid rule-based (aturan biaya) + estimasi ML dari data historis |
| Input tunggal MVP | Data produk (modal, kategori) + parameter biaya platform yang dipilih |
| Output utama MVP | Rentang harga rekomendasi + proyeksi margin bersih pada beberapa skenario |
| Nilai bagi pengguna | Keputusan harga berbasis data, bukan tebakan/ikut-ikutan kompetitor |
| Nilai ekonomi | Potensi menghindari kerugian dari harga di bawah titik impas (proxy metric) |
| Dampak sosial | Melindungi keberlanjutan usaha mikro dari tekanan margin |
| Dataset | Skema biaya resmi marketplace (publik) + data penjualan historis milik UMKM (bagian 14) |
| Ground truth | Terbatas - bersifat estimasi/simulasi, tidak ada "harga optimal" tunggal yang dapat diverifikasi langsung tanpa eksperimen A/B |
| Baseline | Kalkulator HPP manual - cukup untuk kasus sederhana, tidak cukup saat biaya dinamis & SKU banyak (bagian 13.4) |
| Metrik teknis | Error estimasi margin dibanding data riil historis (jika tersedia) |
| Metrik bisnis | Selisih margin sebelum-sesudah penggunaan alat (proxy, perlu validasi) |
| Bentuk kustomisasi AI | Model regresi/estimasi dikalibrasi pada data biaya+penjualan spesifik domain UMKM Indonesia |
| Risiko | Rekomendasi keliru berdampak finansial langsung - risiko TERTINGGI di antara kandidat |
| Mitigasi | Rentang bukan angka tunggal, disclaimer eksplisit, human-in-the-loop wajib |
| Estimasi kompleksitas | Rendah-sedang |
| Kesesuaian batasan kompetisi | Tinggi |
| Novelty | Novelty implementasi - menggabungkan data biaya platform real dengan simulasi margin yang dapat dijelaskan |
| Alasan dapat kalah | Ground truth lemah membuat validitas model sulit dibuktikan meyakinkan pada video 7 menit |
| Alasan dapat menang | Masalah sangat konkret dan relatable, mudah dipahami juri, dampak ekonomi langsung terlihat |


### 16.3. UlasanAsli - Deteksi Ulasan Tidak Wajar & Skor Kepercayaan Toko

| Aspek | Keterangan |
| --- | --- |
| One-sentence concept | Mendeteksi pola ulasan tidak wajar/manipulatif pada listing produk dan menghasilkan skor kepercayaan yang transparan bagi pembeli maupun penjual jujur. |
| Masalah utama | 6.2 - ulasan palsu merusak kepercayaan transaksi |
| Target pengguna | Konsumen digital dan penjual jujur yang dirugikan manipulasi ulasan kompetitor |
| Bukti masalah | BPKN mencatat pergeseran pengaduan ke manipulasi informasi (bagian 5, 8); literatur ML fake-review detection matang secara global (Choi dkk. 2022, DOI 10.3389/frai.2022.1064371) |
| Existing solution | Fakespot/Trustpilot - Similar mechanism, tidak beroperasi di ekosistem marketplace Indonesia (bagian 11) |
| Gap | Data gap TINGGI - tidak ditemukan dataset fake-review berlabel Bahasa Indonesia publik (bagian 12) |
| Proposed AI capability | Klasifikasi teks+pola perilaku (duplikasi, rating-teks mismatch, kecepatan posting) untuk skor kepercayaan |
| Input tunggal MVP | Kumpulan ulasan pada satu listing produk |
| Output utama MVP | Skor kepercayaan listing + daftar ulasan yang ditandai berisiko beserta alasan |
| Nilai bagi pengguna | Keputusan beli lebih terinformasi; penjual jujur mendapat pembeda dari kompetitor manipulatif |
| Nilai ekonomi | Berpotensi menjaga fairness kompetisi harga/penjualan bagi UMKM jujur (proxy) |
| Dampak sosial | Trust and safety - domain eksplisit dalam rulebook, berdampak luas pada ekosistem |
| Dataset | TIDAK tersedia dataset Indonesia berlabel eksplisit - risiko UTAMA ide ini (bagian 12, 14) |
| Ground truth | Rendah - perlu proxy label (duplikasi teks, anomali waktu posting) karena tidak ada label "palsu/asli" terverifikasi |
| Baseline | Filter internal marketplace (black-box, tidak dapat direplikasi/diuji tim) |
| Metrik teknis | Precision/recall pada proxy label yang dikonstruksi tim (perlu transparansi metodologi labeling) |
| Metrik bisnis | Jumlah ulasan anomali terdeteksi per 1000 ulasan (deskriptif, bukan validasi kebenaran mutlak) |
| Bentuk kustomisasi AI | Model klasifikasi dilatih pada proxy-labeled data + fitur perilaku, adaptasi metode literatur global ke konteks Bahasa Indonesia |
| Risiko | False positive dapat menstigma penjual sah; ground truth lemah adalah risiko teknis signifikan |
| Mitigasi | Framing output sebagai "skor risiko" bukan vonis "palsu", disertai transparansi kriteria yang memicu skor tersebut |
| Estimasi kompleksitas | Sedang-tinggi karena keterbatasan ground truth |
| Kesesuaian batasan kompetisi | Sedang - satu alur input-output tetap dapat didemonstrasikan meski validitas ilmiah lebih sulit dibuktikan dalam waktu terbatas |
| Novelty | Novelty konteks Indonesia tinggi (belum ditemukan solusi lokal setara) namun novelty ilmiah terbatas oleh data gap |
| Alasan dapat kalah | Ground truth lemah paling berisiko dipertanyakan juri saat sesi tanya-jawab/live demo |
| Alasan dapat menang | Masalah sangat relevan dengan data kerugian OJK/BPKN yang besar dan mudah dinarasikan secara emosional-persuasif pada video promosi |


### 16.4. BalasCepat - Asisten Balasan Chat Multi-Kanal Berbasis Katalog UMKM

| Aspek | Keterangan |
| --- | --- |
| One-sentence concept | Menyusun draft balasan chat pelanggan secara otomatis berdasarkan katalog produk dan FAQ milik toko. |
| Masalah utama | 6.3 dan sebagian 6.5 (live commerce) - layanan pelanggan tidak tertangani konsisten |
| Target pengguna | UMKM dengan volume chat tinggi lintas kanal |
| Bukti masalah | Studi kasus chatbot pada usaha mikro (MDPI Information 16(12):1078, 2025) menunjukkan potensi optimasi layanan pelanggan |
| Existing solution | Qiscus AgentLabs, Kata.ai Omnichat - Existing namun harga premium tidak terjangkau UMKM mikro (bagian 11) |
| Gap | UMKM adoption gap - solusi terjangkau untuk skala mikro belum banyak tersedia |
| Proposed AI capability | RAG atas katalog produk + FAQ toko, dengan tool-calling sederhana ke info stok/harga |
| Input tunggal MVP | Pertanyaan pelanggan (teks tunggal) |
| Output utama MVP | Draft balasan yang disarankan (bukan otomatis terkirim, agar tetap human-in-the-loop) |
| Catatan interface percakapan | Menggunakan antarmuka percakapan sebagai interaksi utama (1 dari maksimal 2 ide yang diizinkan) |
| Dataset | Data chat/FAQ dimiliki UMKM sendiri - perlu dikumpulkan/disintesis per toko (bagian 6.3) |
| Risiko | Jawaban tidak akurat soal stok/harga (halusinasi) dapat merugikan kredibilitas toko |
| Mitigasi | RAG ketat ter-ground pada data katalog aktual, bukan generasi bebas |
| Kesesuaian batasan kompetisi | Tinggi - satu alur tanya-jawab |
| Novelty | Sedang - berdekatan (Similar/Adjacent) dengan solusi existing (Qiscus/Kata.ai), novelty utama pada aksesibilitas harga untuk mikro, bukan mekanisme teknis baru |
| Alasan dapat kalah | Orisinalitas relatif rendah karena mirip solusi existing yang sudah matang |
| Alasan dapat menang | Kebutuhan nyata sangat tinggi dan mudah didemonstrasikan secara meyakinkan |


### 16.5. TemanBelanja - Asisten Belanja Bersuara untuk Konsumen Tunanetra

| Aspek | Keterangan |
| --- | --- |
| One-sentence concept | Asisten berbasis suara yang membacakan deskripsi produk dan memandu pencarian/checkout bagi konsumen tunanetra/low vision. |
| Masalah utama | 6.13 - aksesibilitas platform bagi penyandang disabilitas netra |
| Target pengguna | Konsumen tunanetra/low vision |
| Bukti masalah | Prototipe voice-enabled shopping mencapai 88% keberhasilan transaksi pada uji terbatas (Atlantis Press); accessibility gap terkonfirmasi (Frontiers DOI 10.3389/frai.2024.1349668) |
| Existing solution | Screen reader generik bawaan perangkat - Substitute, tidak dioptimalkan untuk e-commerce (bagian 11) |
| Gap | Localization gap total untuk Indonesia - belum ditemukan solusi serupa berbahasa Indonesia (bagian 12) |
| Proposed AI capability | Speech-to-text + text-to-speech Bahasa Indonesia + image captioning sederhana untuk deskripsi produk |
| Input tunggal MVP | Perintah suara pencarian produk |
| Output utama MVP | Deskripsi audio produk yang relevan |
| Catatan interface percakapan | Menggunakan antarmuka percakapan/suara sebagai interaksi utama (2 dari maksimal 2 ide yang diizinkan) |
| Dataset | Data teks produk tersedia luas; data audio berlabel Bahasa Indonesia untuk domain e-commerce terbatas (bagian 14, DATA GAP sedang) |
| Risiko | Kesalahan pengenalan suara/produk pada transaksi finansial berisiko tinggi (salah beli/bayar) |
| Mitigasi | Konfirmasi berlapis sebelum transaksi final, bukan eksekusi otomatis penuh |
| Kesesuaian batasan kompetisi | Sedang - kompleksitas integrasi multimodal (suara+gambar+teks) relatif tinggi terhadap batasan MVP yang menekankan kesederhanaan |
| Novelty | Novelty dampak sosial tinggi, novelty teknis sedang (kombinasi teknologi voice yang sudah ada, bukan metode baru) |
| Alasan dapat kalah | Kompleksitas teknis multimodal berisiko overbuilt atau, jika disederhanakan berlebihan, terasa underbuilt/tempelan |
| Alasan dapat menang | Dampak sosial sangat kuat dan jarang disentuh kompetitor lain - potensi diferensiasi tinggi pada storytelling |


### 16.6. PrediksiPergi - Deteksi Dini Risiko Churn Pelanggan UMKM

| Aspek | Keterangan |
| --- | --- |
| One-sentence concept | Memberi skor risiko churn per pelanggan UMKM berdasarkan pola transaksi historis untuk memandu tindakan retensi. |
| Masalah utama | 6.9 - churn pelanggan UMKM tidak terdeteksi dini |
| Target pengguna | UMKM dengan basis pelanggan berulang (repeat buyer) |
| Bukti masalah | Literatur churn e-commerce luas (K-Means+SVM, MDPI JTAER 17(2):24, 2022) namun belum teruji pada skala data UMKM mikro (bagian 10.9) |
| Existing solution | Tools CRM/BI enterprise - Substitute tidak terjangkau UMKM mikro (bagian 11) |
| Gap | Data gap - model literatur diasumsikan data besar, belum tentu applicable ke UMKM data-scarce |
| Proposed AI capability | Model RFM (recency-frequency-monetary) sederhana + klasifikasi risiko churn dengan output interpretable (SHAP-like) |
| Input tunggal MVP | Data transaksi historis toko (CSV ekspor) |
| Output utama MVP | Daftar pelanggan berisiko churn beserta alasan (recency tinggi, frekuensi menurun) |
| Dataset | Data transaksi UMKM sendiri - ketersediaan SEDANG-RENDAH (bagian 6.9), berisiko sulit didemonstrasikan tanpa data riil |
| Risiko | Prediksi keliru memicu diskon tidak perlu yang menggerus margin |
| Kesesuaian batasan kompetisi | Sedang |
| Novelty | Sedang - metodologi RFM+klasifikasi sudah umum, novelty utama pada adaptasi skala data kecil UMKM |
| Alasan dapat kalah | Data transaksi UMKM riil sulit didapat dalam periode kompetisi, MVP mungkin harus memakai data sintetik yang kurang meyakinkan juri |
| Alasan dapat menang | Konsep retensi pelanggan mudah dipahami dan relevan lintas jenis usaha |


### 16.7. PromoPintar - Simulator Efektivitas Promosi & Diskon

| Aspek | Keterangan |
| --- | --- |
| One-sentence concept | Mensimulasikan dampak berbagai skenario diskon terhadap margin dan potensi repeat order sebelum promosi dijalankan. |
| Masalah utama | 6.10 - efektivitas promosi/diskon tidak terukur |
| Target pengguna | UMKM yang rutin mengikuti program promosi platform |
| Bukti masalah | Biaya promosi+iklan platform 4-7% dari harga jual (bagian 5, 8) menunjukkan skala biaya yang signifikan jika tidak terukur |
| Existing solution | Dashboard penjualan kotor marketplace - Adjacent, tidak memisahkan efek kausal promosi (bagian 11) |
| Gap | Evaluation gap - metrik penelitian causal inference jarang disederhanakan untuk UMKM (bagian 12) |
| Proposed AI capability | Model simulasi/estimasi uplift sederhana berbasis data historis penjualan dengan/tanpa promosi |
| Input tunggal MVP | Data historis penjualan + skenario diskon yang dipertimbangkan |
| Output utama MVP | Estimasi dampak margin & volume pada skenario yang dipilih |
| Dataset | Data penjualan historis UMKM - ketersediaan SEDANG, kualitas causal inference bergantung volume data yang sering terbatas pada UMKM |
| Risiko | Estimasi kausal dari data observasional (bukan eksperimen A/B) rentan bias |
| Kesesuaian batasan kompetisi | Sedang - causal inference sulit divalidasi meyakinkan dalam waktu terbatas |
| Novelty | Sedang |
| Alasan dapat kalah | Validitas metodologi causal inference/uplift sulit dipertanggungjawabkan tanpa data eksperimen yang memadai |
| Alasan dapat menang | Relevansi tinggi dengan tekanan margin UMKM yang telah terdokumentasi kuat pada bagian 5 |


### 16.8. WaspadaToko - Klasifikasi Risiko Pesan Penjual Berpotensi Penipuan

| Aspek | Keterangan |
| --- | --- |
| One-sentence concept | Memberi peringatan dini kepada konsumen saat pola pesan penjual menyerupai modus penipuan belanja daring yang umum terjadi. |
| Masalah utama | 6.11 - penipuan toko fiktif/modus belanja daring |
| Target pengguna | Konsumen digital, khususnya yang bertransaksi di luar sistem escrow resmi |
| Bukti masalah | 53.928 kasus penipuan modus belanja daring, kerugian Rp988 miliar (OJK, Nov 2024-Okt 2025) - bukti kuantitatif terkuat di antara seluruh 15 masalah |
| Existing solution | Grup komunitas anti-penipuan manual - Substitute, reaktif bukan proaktif (bagian 11) |
| Gap | Data gap tinggi - tidak ditemukan dataset modus penipuan Bahasa Indonesia berlabel publik |
| Proposed AI capability | Klasifikasi teks pola bahasa penipuan umum (permintaan transfer di luar sistem resmi, urgensi berlebihan) |
| Input tunggal MVP | Teks pesan penjual (paste chat) |
| Output utama MVP | Skor risiko + alasan (pola kalimat yang memicu skor) |
| Dataset | Contoh modus dari laporan media/komunitas sebagai data sintetik/proxy - ketersediaan SEDANG-RENDAH untuk pelatihan berlabel formal |
| Risiko | False positive menstigma penjual sah; risiko etik jika sistem disalahgunakan tanpa konfirmasi manusia |
| Kesesuaian batasan kompetisi | Sedang |
| Novelty | Sedang-tinggi konteks Indonesia, namun ground truth lemah mirip UlasanAsli |
| Alasan dapat kalah | Ground truth lemah, mirip kelemahan UlasanAsli namun dengan bukti kuantitatif kerugian yang lebih besar |
| Alasan dapat menang | Angka kerugian OJK yang besar dan konkret sangat kuat untuk storytelling dampak sosial |


### 16.9. RekomenUMKM - Rekomendasi Kategori & Audiens untuk Produk Baru (Cold-Start)

| Aspek | Keterangan |
| --- | --- |
| One-sentence concept | Merekomendasikan kategori, kata kunci, dan audiens target yang tepat untuk produk/toko baru tanpa histori interaksi. |
| Masalah utama | 6.6 - toko/produk baru tidak direkomendasikan sistem |
| Target pengguna | Penjual baru/UMKM dengan katalog kecil |
| Bukti masalah | 14 juta penjual & 1,8 miliar produk terdaftar di satu marketplace saja (Tokopedia) - skala yang memperbesar risiko produk baru tenggelam |
| Existing solution | AI Product Optimiser Shopee - Adjacent, membantu optimasi judul namun tidak eksplisit atasi cold-start lintas kategori (bagian 11) |
| Gap | Low-resource gap dan UMKM adoption gap - metodologi cold-start literatur belum diuji pada skenario UMKM Indonesia (bagian 12) |
| Proposed AI capability | Model embedding teks deskripsi produk (content-based) untuk mencari kemiripan dengan produk yang sudah terbukti laku |
| Input tunggal MVP | Deskripsi produk baru (teks) |
| Output utama MVP | Daftar kategori/kata kunci/audiens target yang direkomendasikan |
| Dataset | Tokopedia product reviews (HF), dataset marketplace Kaggle - ketersediaan SEDANG-TINGGI |
| Risiko | Rekomendasi berbasis konten murni dapat kurang akurat dibanding collaborative filtering matang |
| Kesesuaian batasan kompetisi | Tinggi |
| Novelty | Sedang - metodologi cold-start sudah ada di literatur global, novelty pada adaptasi konteks UMKM Indonesia |
| Alasan dapat kalah | Evaluasi cold-start secara meyakinkan butuh desain eksperimen simulasi yang cukup rumit dijelaskan ke juri non-teknis dalam waktu terbatas |
| Alasan dapat menang | Berbasis dataset yang tersedia baik dan menjawab langsung masalah keadilan visibilitas bagi penjual baru |


## 17. Eliminated Ideas and Reasons

Selain sembilan kandidat pada bagian 16, lima ide awal dieliminasi sebelum masuk shortlist, dengan alasan eksplisit merujuk pada kriteria eliminasi yang ditetapkan.

| Ide yang Dieliminasi | Deskripsi Singkat | Alasan Eliminasi |
| --- | --- | --- |
| DeteksiTiru (deteksi produk tiruan visual) | Computer vision untuk mendeteksi listing kloning produk UMKM (masalah 6.8) | Tidak memiliki dataset atau evaluasi yang memadai - tidak ditemukan dataset foto produk UMKM Indonesia berlabel asli/tiruan (data gap TINGGI, bagian 12); risiko sulit direproduksi juri dengan hasil meyakinkan dalam periode kompetisi. |
| LiveBalas (asisten real-time khusus live streaming) | Klasifikasi & auto-reply komentar real-time saat sesi live commerce (masalah 6.5) | Membutuhkan integrasi produksi kompleks (streaming real-time, API platform pihak ketiga yang aksesnya terbatas) - berisiko overbuilt dan sulit direproduksi secara lokal oleh juri sesuai batasan MVP rulebook. Sebagian kebutuhan (balasan cepat berbasis katalog) sudah tercakup pada BalasCepat dengan lingkup lebih realistis. |
| BisnisMikroAI (rekomendasi restock/bundling generik) | Model peramalan+association rules untuk keputusan restock/bundling usaha mikro (masalah 6.15) | Masalah tumpang tindih signifikan dengan HargaCerdas dan PromoPintar (redundansi lingkup); dampak hanya berupa klaim tanpa dataset transaksi mikro yang representatif tersedia publik - berisiko dampak hanya berupa klaim tanpa evaluasi kuat. |
| ChatbotUmum (asisten belanja percakapan generik lintas kategori) | Chatbot umum untuk menjawab pertanyaan belanja apa pun tanpa fokus masalah spesifik | Hanya chatbot generik tanpa target pengguna dan masalah spesifik yang jelas; berisiko dinilai sebagai wrapper API LLM tanpa kustomisasi bermakna; sudah menjadi fitur standar pada banyak platform (Shopee/Tokopedia sudah punya asisten AI dasar, bagian 11). |
| WrapperRekomendasi (pembungkus API rekomendasi umum) | Memanggil API LLM komersial untuk "merekomendasikan produk apa saja" tanpa domain spesifik | AI tidak benar-benar diperlukan secara spesifik (masalah terlalu umum, tidak spesifik terhadap satu titik masalah commerce); berisiko dinilai hanya wrapper API tanpa fine-tuning/kustomisasi yang dapat dipertanggungjawabkan sesuai ketentuan rulebook (bagian 2.9). |


## 18. Weighted Decision Matrix

Skala 1-10 digunakan pada 22 kriteria, dengan bobot disesuaikan agar mencerminkan proporsi rubrik penilaian resmi rulebook (bagian 2.11): kriteria terkait Implementasi Teknologi & Kematangan Arsitektur, Kesiapan MVP, dan Kesesuaian Rulebook diberi bobot lebih besar; kriteria terkait storytelling/demonstrasi mencerminkan bobot Video Promosi & Kualitas Proposal.


### 18.1 Raw Score per Kriteria (Bagian 1 dari 2: Lima Ide Teratas)

| Kriteria (Bobot) | InsightUlasan | HargaCerdas | UlasanAsli | RekomenUMKM | BalasCepat |
| --- | --- | --- | --- | --- | --- |
| Relevansi dengan Smart Commerce (6) | 9 | 9 | 9 | 8 | 8 |
| Kejelasan masalah (5) | 8 | 9 | 7 | 7 | 7 |
| Kekuatan bukti (6) | 8 | 6 | 7 | 7 | 5 |
| Urgensi (4) | 7 | 8 | 8 | 5 | 7 |
| Dampak ekonomi (5) | 7 | 8 | 6 | 6 | 6 |
| Dampak sosial (5) | 7 | 5 | 8 | 5 | 5 |
| Originalitas (6) | 9 | 6 | 7 | 6 | 4 |
| Research gap (5) | 9 | 5 | 8 | 7 | 4 |
| Kebutuhan nyata terhadap AI (6) | 9 | 7 | 7 | 7 | 6 |
| Ketersediaan dataset (6) | 9 | 7 | 3 | 7 | 6 |
| Kemudahan evaluasi (4) | 7 | 6 | 5 | 6 | 7 |
| Kelayakan MVP (7) | 9 | 8 | 5 | 7 | 8 |
| Kesesuaian dengan batasan rulebook (5) | 9 | 8 | 7 | 8 | 8 |
| Kematangan arsitektur yang mungkin dicapai (4) | 9 | 7 | 5 | 6 | 7 |
| Kemampuan dijalankan secara lokal (4) | 9 | 9 | 6 | 8 | 7 |
| Kemampuan dikustomisasi (4) | 9 | 7 | 5 | 7 | 7 |
| Risiko teknis (skor tinggi = risiko rendah) (4) | 8 | 6 | 4 | 6 | 7 |
| Risiko etik (skor tinggi = risiko rendah) (3) | 8 | 8 | 5 | 8 | 8 |
| Potensi storytelling (3) | 9 | 8 | 8 | 6 | 6 |
| Potensi demonstrasi (3) | 9 | 7 | 6 | 6 | 7 |
| Potensi pengembangan setelah kompetisi (3) | 8 | 7 | 6 | 6 | 6 |
| Kemungkinan mencapai final (2) | 7 | 6 | 6 | 5 | 6 |


### 18.2 Raw Score per Kriteria (Bagian 2 dari 2: Empat Ide Lainnya)

| Kriteria (Bobot) | TemanBelanja | PrediksiPergi | PromoPintar | WaspadaToko |
| --- | --- | --- | --- | --- |
| Relevansi dengan Smart Commerce (6) | 7 | 7 | 7 | 8 |
| Kejelasan masalah (5) | 7 | 6 | 6 | 8 |
| Kekuatan bukti (6) | 5 | 6 | 5 | 6 |
| Urgensi (4) | 5 | 4 | 5 | 9 |
| Dampak ekonomi (5) | 4 | 5 | 6 | 6 |
| Dampak sosial (5) | 9 | 4 | 4 | 8 |
| Originalitas (6) | 7 | 5 | 5 | 7 |
| Research gap (5) | 8 | 5 | 4 | 6 |
| Kebutuhan nyata terhadap AI (6) | 7 | 6 | 6 | 7 |
| Ketersediaan dataset (6) | 5 | 5 | 6 | 4 |
| Kemudahan evaluasi (4) | 5 | 6 | 4 | 5 |
| Kelayakan MVP (7) | 5 | 6 | 6 | 5 |
| Kesesuaian dengan batasan rulebook (5) | 7 | 7 | 7 | 7 |
| Kematangan arsitektur yang mungkin dicapai (4) | 4 | 6 | 5 | 5 |
| Kemampuan dijalankan secara lokal (4) | 6 | 7 | 6 | 6 |
| Kemampuan dikustomisasi (4) | 5 | 6 | 6 | 5 |
| Risiko teknis (skor tinggi = risiko rendah) (4) | 4 | 6 | 5 | 4 |
| Risiko etik (skor tinggi = risiko rendah) (3) | 6 | 8 | 7 | 5 |
| Potensi storytelling (3) | 9 | 5 | 6 | 9 |
| Potensi demonstrasi (3) | 6 | 5 | 5 | 6 |
| Potensi pengembangan setelah kompetisi (3) | 6 | 5 | 5 | 5 |
| Kemungkinan mencapai final (2) | 5 | 4 | 4 | 5 |


### 18.3 Weighted Score dan Evidence Confidence

| Peringkat | Ide | Weighted Score (skala 1-10) | Evidence Confidence |
| --- | --- | --- | --- |
| 1 | InsightUlasan | 8.39 | TINGGI - dataset terverifikasi tersedia, literatur pendukung kuat (bagian 9.4, 10.4) |
| 2 | HargaCerdas | 7.15 | SEDANG-TINGGI - masalah & data biaya terverifikasi kuat, literatur AI-spesifik-UMKM-Indonesia terbatas |
| 3 | RekomenUMKM | 6.64 | SEDANG - literatur cold-start kuat, dataset UMKM-spesifik Indonesia belum diverifikasi langsung |
| 4 | BalasCepat | 6.41 | SEDANG - masalah kuat, namun originalitas rendah karena solusi existing serupa sudah ada |
| 5 | UlasanAsli | 6.32 | SEDANG - masalah & literatur metodologi kuat, dataset Indonesia berlabel adalah risiko signifikan |
| 6 | WaspadaToko | 6.23 | SEDANG - bukti kuantitatif kerugian sangat kuat (OJK), namun ground truth model lemah |
| 7 | TemanBelanja | 6.03 | SEDANG-RENDAH - dampak sosial kuat, dataset & kompleksitas teknis Indonesia belum terverifikasi |
| 8 | PrediksiPergi | 5.68 | RENDAH-SEDANG - literatur umum kuat, data UMKM Indonesia spesifik tidak ditemukan |
| 9 | PromoPintar | 5.52 | RENDAH-SEDANG - masalah relevan, validitas metodologi causal inference perlu data yang sulit didapat |

Alasan pemberian skor secara umum: InsightUlasan unggul pada hampir seluruh kriteria berbobot tinggi (kelayakan MVP, ketersediaan dataset, kebutuhan AI, kesesuaian rulebook) karena merupakan satu-satunya ide dengan dataset Bahasa Indonesia siap pakai YANG TERVERIFIKASI tersedia dan gap literatur paling terdokumentasi jelas (bagian 10.4). HargaCerdas unggul pada urgensi dan kejelasan masalah namun tertahan pada ketersediaan bukti akademik spesifik dan risiko konsekuensi finansial dari kesalahan model. UlasanAsli unggul pada dampak sosial, urgensi, dan kekuatan bukti kuantitatif (OJK/BPKN) namun tertahan signifikan pada ketersediaan dataset dan kemudahan evaluasi akibat lemahnya ground truth.


### 18.4 Sensitivity Analysis

| Skenario Bobot | Top 3 Hasil |
| --- | --- |
| Baseline (bobot pada 18.3) | 1. InsightUlasan (8.39); 2. HargaCerdas (7.15); 3. RekomenUMKM (6.64) |
| Originalitas dinaikkan (6 -> 12) | 1. InsightUlasan (8.42); 2. HargaCerdas (7.08); 3. RekomenUMKM (6.60) |
| Dampak sosial dinaikkan (5 -> 12) | 1. InsightUlasan (8.30); 2. HargaCerdas (7.01); 3. RekomenUMKM (6.53) |
| Technical/MVP feasibility dinaikkan (Kelayakan MVP 7->14, Lokal 4->8) | 1. InsightUlasan (8.45); 2. HargaCerdas (7.27); 3. RekomenUMKM (6.71) |
| Dataset feasibility dinaikkan (6 -> 14) | 1. InsightUlasan (8.44); 2. HargaCerdas (7.14); 3. RekomenUMKM (6.67) |

Kesimpulan sensitivity analysis: InsightUlasan konsisten menempati peringkat pertama pada seluruh skenario pembobotan ulang, menunjukkan robustness pilihan ini terhadap perubahan prioritas juri. HargaCerdas dan UlasanAsli konsisten bertukar posisi kedua/ketiga tergantung skenario - saat dampak sosial dinaikkan, UlasanAsli/TemanBelanja cenderung naik; saat dataset feasibility dinaikkan, HargaCerdas dan RekomenUMKM cenderung naik menggantikan UlasanAsli. Ini menegaskan bahwa ranking tiga besar (bagian 19) robust, namun urutan #2 dan #3 sensitif terhadap prioritas penilaian - dicatat sebagai bagian dari ketidakpastian yang perlu diperhatikan.


## 19. Three Finalist Ideas

Tiga finalis berdasarkan bagian 18: InsightUlasan (peringkat 1), HargaCerdas (peringkat 2), dan RekomenUMKM (peringkat 3). Setiap finalis dianalisis mendalam pada 28 aspek berikut.


### 19.1 InsightUlasan

| Aspek | Keterangan |
| --- | --- |
| Problem statement | UMKM Indonesia menerima ulasan dan pesan pelanggan dalam volume tinggi dan bahasa informal, namun tidak memiliki cara sistematis mengubahnya menjadi keputusan bisnis konkret (perbaikan produk, prioritas layanan). |
| Evidence chain | BPS 2024 (4,40 juta unit usaha e-commerce, mayoritas mikro) -> literatur IndoBERT (akurasi hingga 97% pada klasifikasi sentimen Bahasa Indonesia, bagian 9.4) -> gap metodologis eksplisit (penelitian berhenti di klasifikasi, belum ke rekomendasi aksi, bagian 10.4) -> tidak ditemukan produk existing yang menjembatani gap ini untuk UMKM Indonesia (bagian 11). |
| Target user | Pemilik UMKM skala mikro-kecil dengan volume ulasan/chat menengah-tinggi (persona Bu Rina, bagian 7.2) |
| Jobs to be done | Memahami dengan cepat apa yang perlu diperbaiki dari feedback pelanggan tanpa harus membaca satu-satu secara manual |
| Current journey | Membaca ulasan sesekali saat sempat, tanpa pencatatan sistematis, sering terlewat karena volume dan keterbatasan waktu |
| Pain points | Waktu terbatas, bahasa ulasan informal sulit dipahami polanya secara agregat, tidak ada prioritisasi tindakan |
| Research gap | Methodological gap dan language gap (bagian 12) - gap paling terdokumentasi kuat di antara seluruh kandidat |
| Existing solutions | Dashboard rating marketplace (skor rata-rata) - Adjacent; tools sentiment analysis SaaS internasional - Substitute mahal/tidak berbahasa Indonesia (bagian 11) |
| Why existing solutions fail | Tidak dioptimalkan Bahasa Indonesia informal, tidak dirancang untuk skala UMKM mikro, berhenti pada skor mentah tanpa rekomendasi aksi |
| AI necessity | Tinggi - volume dan variasi bahasa tidak dapat diproses konsisten secara manual/rule-based (bagian 13.1) |
| Proposed intelligence | DIPERBARUI (hybrid multimodal+agentic): klasifikasi aspek+sentimen teks (fine-tuned IndoBERT/DistilBERT) + klasifikasi kategori visual dari foto ulasan opsional (classifier ringan di atas vision encoder beku) + foundation model orkestrator yang memanggil keduanya via tool calling dan menyusun ringkasan ter-ground (RAG) pada kutipan/temuan asli |
| Data requirement | Batch teks ulasan/chat berbahasa Indonesia per toko |
| Potential model | IndoBERT/DistilBERT fine-tuned untuk klasifikasi aspek-sentimen teks; classifier ringan (linear/shallow head) di atas vision encoder pre-trained beku (mis. CLIP) untuk kategori visual foto ulasan; LLM ringan sebagai orkestrator tool-calling + RAG untuk lapisan output naratif |
| Customization strategy | Memenuhi tiga dari lima rute kustomisasi resmi panitia sekaligus (bagian 2.9): fine-tuning model pendukung teks pada gabungan dataset publik (PRDECT-ID, e-commerce-sentiment-bahasa-indonesia) + augmentasi data UMKM mitra; training model pendukung visual (classifier di atas encoder beku) pada sampel foto ulasan yang dianotasi manual; tool calling + RAG pada lapisan foundation model orkestrator |
| Baseline | Pembacaan manual/pencatatan Excel - terbukti tidak proporsional pada volume tinggi (bagian 13.4) |
| Evaluation method | F1-score klasifikasi pada data uji berlabel; evaluasi kualitatif relevansi rekomendasi aksi oleh pemilik UMKM mitra |
| MVP feasibility | Tinggi - satu alur input (batch teks) -> output (ringkasan+rekomendasi), dapat dijalankan lokal tanpa hardware khusus |
| Social impact | Digital inclusion untuk UMKM - alat analitik profesional tanpa perlu tim data science internal |
| Economic impact | Potensi perbaikan retensi/rating melalui tindakan lebih tepat sasaran (proxy metric, REQUIRES USER VALIDATION) |
| Risks | Kesalahan ekstraksi pada teks sangat informal/typo/data imbalance kelas minoritas; PEMBARUAN v5 - CV kini wajib (bagian 21B.1), gap dataset foto ditutup sebagian lewat akuisisi bertarget via Apify (~250-300 foto, bagian 21B.6), namun generalisasi zero-shot CLIP dari domain industri ke foto konsumen TETAP belum terbukti dan wajib divalidasi (Langkah 4, bagian 21B.2) sebelum hasil visual dicantumkan di proposal/video |
| Regulatory concerns | Perlu memastikan data chat yang memuat info pribadi (nomor telepon, alamat) dianonimkan sebelum diproses (UU PDP, bagian 22) |
| Ethical concerns | Risiko bias jika data latih tidak representatif UMKM sangat mikro (yang datanya lebih sedikit terwakili di dataset publik) |
| Competitive advantage | Dataset siap pakai + gap literatur jelas + fokus spesifik UMKM mikro Bahasa Indonesia informal + DIPERBARUI: arsitektur multimodal (teks+foto) yang belum ditemukan pada kompetitor manapun yang ditelusuri (bagian 11), termasuk dashboard rating marketplace besar sekalipun |
| Innovation defensibility | Novelty implementasi (pipeline sentimen-ke-keputusan) dan novelty konteks Indonesia, didukung rantai bukti yang jelas; DIPERKUAT oleh novelty teknis arsitektur hybrid multimodal+agentic yang secara eksplisit memenuhi ketentuan kustomisasi resmi panitia melalui tiga rute sekaligus (bagian 2.9) |
| Judge objection | "Ini kan cuma sentiment analysis, sudah banyak yang buat?" |
| Response to judge objection | Perbedaan bukan pada klasifikasi sentimennya saja (yang memang sudah umum), melainkan pada (1) lapisan penerjemahan skor menjadi rekomendasi aksi bisnis terprioritas yang ter-ground pada kutipan asli - gap yang secara eksplisit ditemukan pada bagian 10.4 belum dijembatani penelitian maupun produk existing yang ditemukan - dan (2) arsitektur hybrid multimodal (teks+foto) dengan orkestrasi tool-calling yang jauh melampaui sentiment analysis konvensional single-modal. |
| Judge objection (2, Pembaruan v6) | "Ngapain pakai pipeline serumit ini - orang tinggal pakai token API LLM sekarang udah jauh lebih bagus dan otomatis hasilkan insight dari reviews?" |
| Response to judge objection (2) | Jawaban jujur, bukan defensif: JIKA ukurannya semata kualitas insight, zero-shot LLM API murni mungkin memang setara atau lebih baik (bagian 13.5) - tim TIDAK mengklaim sebaliknya. Tapi zero-shot API call murni GAGAL memenuhi syarat kustomisasi wajib rulebook (bagian 2.9) - klarifikasi resmi panitia eksplisit menyebut tujuan aturan itu "supaya tidak sekadar zero-shot API call biasa". Di luar kepatuhan aturan, pipeline yang diusulkan juga lebih reproducible oleh juri (jalan lokal, tidak butuh API key/kredit pihak ketiga saat cross-check, bagian 2.6), dan jauh lebih murah dioperasikan pada skala ribuan ulasan lintas UMKM sesuai model bisnis freemium yang menyasar UMKM mikro (bagian 21B.4) - argumen ini soal kepatuhan dan operasional, bukan klaim "insight kami lebih pintar". |
| Critical assumptions | UMKM bersedia membagikan data ulasan/chat mereka; volume ulasan cukup besar untuk menghasilkan insight bermakna; rekomendasi aksi yang dihasilkan benar-benar dianggap relevan oleh pemilik usaha (bukan generik) |
| Validation plan | Wawancara 5-8 UMKM mitra (bagian 23) + uji kualitatif terhadap sampel ulasan riil sebelum proposal final disusun |


### 19.2 HargaCerdas

| Aspek | Keterangan |
| --- | --- |
| Problem statement | UMKM menetapkan harga jual tanpa memperhitungkan biaya platform berlapis (15-20% dari harga jual), berisiko menjual di bawah titik impas. |
| Evidence chain | Kompas.com 2026 (struktur biaya berlapis) -> temuan kesalahan umum UMKM hanya menghitung modal (bagian 6.1) -> tidak ada alat dinamis yang menggabungkan biaya real-time dengan simulasi margin (bagian 11). |
| Target user | UMKM penjual marketplace dengan struktur biaya kompleks |
| Jobs to be done | Menentukan harga jual yang kompetitif namun tetap menguntungkan setelah seluruh biaya platform |
| Current journey | Mengecek harga kompetitor manual, menyesuaikan tanpa model biaya penuh |
| Pain points | Tidak tahu titik impas riil setelah biaya berlapis, khawatir rugi tanpa sadar |
| Research gap | Tidak ada gap akademik AI-spesifik yang kuat ditemukan untuk konteks UMKM-Indonesia-dinamis; lebih merupakan product/implementation gap (bagian 12) |
| Existing solutions | Kalkulator HPP manual/template Excel - Substitute non-AI statis (bagian 11) |
| Why existing solutions fail | Statis, tidak terhubung ke biaya platform real-time atau data historis penjualan toko sendiri |
| AI necessity | Sedang-tinggi - trade-off harga-volume-margin lintas skenario sulit dihitung manual konsisten, meski komponen inti dapat dijelaskan sebagai model regresi/simulasi yang relatif sederhana (bagian 13.2) |
| Proposed intelligence | Model regresi/simulasi hybrid (aturan biaya + estimasi dari data historis) untuk rentang harga optimal |
| Data requirement | Data biaya platform (publik) + data produk & penjualan historis milik toko |
| Potential model | Regresi/optimasi sederhana, dikombinasikan hybrid rule-based untuk komponen biaya |
| Customization strategy | Kalibrasi model pada data biaya platform Indonesia terkini + data historis toko (bentuk kustomisasi: adaptasi domain, bukan fine-tuning model bahasa besar) |
| Baseline | Kalkulator HPP manual - cukup untuk kasus sederhana, tidak cukup saat biaya dinamis (bagian 13.4) |
| Evaluation method | Perbandingan estimasi margin model vs kalkulasi manual pada data historis riil (jika tersedia dari UMKM mitra) |
| MVP feasibility | Tinggi - satu alur input (data produk+biaya) -> output (rentang harga+margin) |
| Social impact | Melindungi keberlanjutan usaha mikro dari tekanan margin yang tidak disadari |
| Economic impact | Potensi menghindari kerugian dari harga di bawah titik impas (proxy metric) |
| Risks | Rekomendasi keliru berdampak finansial langsung - risiko tertinggi di antara tiga finalis |
| Regulatory concerns | Perlu berhati-hati agar tidak dianggap mendorong predatory pricing atau kolusi harga (terkait perhatian KPPU, bagian 5) - desain harus murni membantu efisiensi biaya individual toko, bukan koordinasi harga antar penjual |
| Ethical concerns | Risiko over-reliance pengguna pada rekomendasi tanpa memahami asumsi di baliknya (automation bias) |
| Competitive advantage | Mengintegrasikan skema biaya platform terkini yang jarang dikonsolidasikan otomatis oleh tools existing |
| Innovation defensibility | Novelty implementasi - integrasi data biaya dinamis dengan simulasi yang dapat dijelaskan |
| Judge objection | "Ini kan cuma kalkulator, di mana AI-nya?" |
| Response to judge objection | Komponen AI terletak pada estimasi hubungan harga-volume-margin dari data historis toko (bukan aturan tetap), menghasilkan rentang rekomendasi yang beradaptasi per toko/produk - berbeda dari kalkulator statis yang hanya menerapkan rumus tetap untuk semua kasus. |
| Critical assumptions | UMKM bersedia membagikan data biaya & penjualan; hubungan harga-volume dapat diestimasi dengan data historis yang tersedia terbatas |
| Validation plan | Wawancara UMKM mengenai kesediaan berbagi data biaya (bagian 23) + uji simulasi pada data historis riil dari toko mitra |


### 19.3 RekomenUMKM

| Aspek | Keterangan |
| --- | --- |
| Problem statement | Toko/produk baru tidak muncul pada rekomendasi sistem marketplace karena minim histori interaksi (cold-start), sehingga sulit ditemukan pembeli. |
| Evidence chain | Skala katalog besar Tokopedia (14 juta penjual, 1,8 miliar produk) -> literatur cold-start (content-based, hybrid, LLM kecil efektif, bagian 9.3) -> gap UMKM-adoption & low-resource pada konteks Indonesia (bagian 12). |
| Target user | Penjual baru/UMKM dengan katalog kecil (persona Pak Wisnu, bagian 7.2) |
| Jobs to be done | Mendapatkan visibilitas awal tanpa bergantung sepenuhnya pada iklan berbayar |
| Current journey | Promosi manual di media sosial/grup komunitas, mengandalkan iklan berbayar yang mahal untuk modal terbatas |
| Pain points | Produk tidak muncul di rekomendasi organik meski kualitas baik, modal iklan terbatas |
| Research gap | Low-resource gap dan UMKM adoption gap - metodologi cold-start literatur belum diuji pada skenario UMKM Indonesia (bagian 12) |
| Existing solutions | Shopee AI Product Optimiser - Adjacent, membantu optimasi judul namun tidak eksplisit atasi cold-start lintas kategori (bagian 11) |
| Why existing solutions fail | Algoritma rekomendasi platform besar terstruktural bergantung data interaksi historis yang belum dimiliki entitas baru |
| AI necessity | Tinggi - kemiripan semantik antar produk baru dan preferensi pembeli tidak dapat dipetakan manual pada skala katalog besar (bagian 13.3) |
| Proposed intelligence | Model embedding teks deskripsi produk (content-based) untuk mencari kemiripan dengan produk yang terbukti laku |
| Data requirement | Deskripsi produk baru + katalog produk pembanding (dataset publik Tokopedia/marketplace) |
| Potential model | Sentence embedding Bahasa Indonesia (dapat diadaptasi dari model multibahasa) untuk mengukur kemiripan konten |
| Customization strategy | Fine-tuning/adaptasi model embedding pada domain deskripsi produk marketplace Indonesia |
| Baseline | Kategorisasi manual + iklan berbayar - tidak cukup bagi penjual bermodal terbatas (bagian 13.4) |
| Evaluation method | Hit-rate@K pada skenario simulasi cold-start (menyembunyikan histori interaksi produk existing sebagai protokol evaluasi standar, bagian 9.3) |
| MVP feasibility | Tinggi - satu alur input (deskripsi produk) -> output (kategori/kata kunci/audiens rekomendasi) |
| Social impact | Pemerataan kesempatan visibilitas bagi penjual baru/UMKM lokal dibanding penjual mapan |
| Economic impact | Potensi mempercepat penjualan pertama tanpa bergantung sepenuhnya pada iklan berbayar (proxy metric) |
| Risks | Rekomendasi berbasis konten murni dapat kurang akurat dibanding collaborative filtering matang |
| Regulatory concerns | Relatif rendah - tidak melibatkan data pribadi sensitif, murni berbasis teks deskripsi produk |
| Ethical concerns | Risiko rendah, namun perlu diperhatikan agar tidak memperkuat bias kategori tertentu secara tidak adil |
| Competitive advantage | Fokus eksplisit pada skenario cold-start UMKM baru, bukan optimasi umum untuk penjual mapan |
| Innovation defensibility | Novelty implementasi - adaptasi metodologi cold-start global ke konteks katalog UMKM Indonesia |
| Judge objection | "Bukankah marketplace besar sudah punya sistem rekomendasi sendiri yang lebih canggih?" |
| Response to judge objection | Sistem rekomendasi marketplace dioptimalkan untuk keseluruhan katalog dan mayoritas penjual mapan; alat ini secara spesifik menjadi add-on/simulasi yang membantu penjual BARU memahami positioning kategori/kata kunci sebelum produk memiliki cukup data interaksi - use case yang berbeda, bukan menggantikan algoritma marketplace. |
| Critical assumptions | Kemiripan konten deskripsi cukup menjadi proxy untuk preferensi pembeli; penjual baru bersedia menggunakan alat eksternal sebelum produk mereka punya data |
| Validation plan | Simulasi evaluasi cold-start pada dataset publik + wawancara penjual baru mengenai kegunaan rekomendasi kategori/kata kunci (bagian 23) |


## 20. Recommended Main Idea

Ide utama yang direkomendasikan untuk didalami pada tahap berikutnya adalah InsightUlasan. Pemilihan ini TIDAK didasarkan semata pada ide yang terlihat paling canggih secara teknis (RekomenUMKM dan UlasanAsli sama-sama memiliki elemen teknis menarik), melainkan pada kombinasi terbaik across seluruh dimensi yang diminta:

| Dimensi | Penilaian untuk InsightUlasan |
| --- | --- |
| Masalah nyata | Tinggi - didukung skala 4,40 juta unit usaha e-commerce mikro (BPS 2024) dan gap eksplisit UMKM tanpa alat analitik ulasan (bagian 5, 6.12) |
| Bukti kuat | Tinggi - kombinasi data resmi (BPS), dataset publik terverifikasi tersedia, dan beberapa studi akademik Bahasa Indonesia yang konsisten (bagian 9.4, meski sebagian PARTIALLY VERIFIED) |
| Dampak | Sedang-tinggi - dampak ekonomi & sosial bersifat proxy/hipotesis terukur (belum ada angka pasti, ditandai jujur pada bagian 21 & 26) |
| Novelty | Sedang-tinggi - novelty implementasi & konteks Indonesia pada gap metodologis yang jelas (menjembatani sentimen ke rekomendasi aksi) |
| Kebutuhan AI | Tinggi - volume dan variasi bahasa informal tidak dapat diproses konsisten secara manual/rule-based (bagian 13.1) |
| Dataset | TINGGI - satu-satunya finalis dengan dataset Bahasa Indonesia berlabel yang teridentifikasi tersedia publik dalam jumlah memadai (bagian 14) |
| Evaluasi | Tinggi - metrik teknis (F1) dan metrik bisnis (proxy) dapat diukur dengan jelas |
| Buildability | Tinggi - satu alur input-output sederhana, model kecil (bukan LLM besar), dapat dijalankan lokal tanpa hardware khusus |
| Reproducibility | Tinggi - tidak bergantung API eksternal berbayar/streaming real-time yang sulit direplikasi juri (kontras dengan LiveBalas yang dieliminasi, bagian 17) |
| Kesesuaian rulebook | Tinggi - selaras penuh dengan batasan MVP (satu input-output), ketentuan kustomisasi (fine-tuning), dan reproducibility lokal (bagian 2) |
| Potensi presentasi | Tinggi - narasi "UMKM = 60% PDB, namun tidak punya alat mendengar pelanggannya sendiri" mudah dikomunikasikan secara emosional dan berbasis data |
| Potensi dikembangkan saat final | Sedang-tinggi - dapat diperluas ke integrasi WhatsApp Business API, dashboard tren mingguan, atau rekomendasi otomatis ke fitur HargaCerdas sebagai pengembangan lanjutan |

Sebagai pembanding: HargaCerdas unggul pada urgensi dan kejelasan masalah namun membawa risiko konsekuensi finansial langsung jika model keliru (ground truth "harga optimal" secara inheren sulit diverifikasi tanpa eksperimen A/B). RekomenUMKM memiliki landasan literatur cold-start yang matang namun evaluasi cold-start yang meyakinkan secara singkat kepada juri lebih kompleks dijelaskan dibanding pipeline insight-ke-aksi yang lebih intuitif. InsightUlasan dinilai memiliki risiko keseluruhan PALING RENDAH sambil tetap mempertahankan novelty dan dampak yang meyakinkan.


## 21. Research Foundation of Main Idea

| Aspek | Keterangan |
| --- | --- |
| 1. Judul sementara inovasi | InsightUlasan |
| 2. Tagline | Mengubah keluhan pelanggan menjadi peta tindakan bisnis, dalam bahasa yang UMKM Indonesia pakai sehari-hari. |
| 3. Problem statement | UMKM Indonesia menerima volume ulasan dan pesan pelanggan yang tinggi dalam Bahasa Indonesia informal, namun tidak memiliki cara sistematis untuk mengubahnya menjadi keputusan bisnis konkret sebelum masalah berulang merugikan usaha. |
| 4. Latar belakang berbasis data | 4,40 juta unit usaha e-commerce Indonesia (BPS 2024), mayoritas mikro; hanya ~30% UMKM aktif memanfaatkan kapabilitas digital lebih dari sekadar berjualan dasar (bagian 5, 8). |
| 5. Target pengguna | Pemilik UMKM skala mikro-kecil penjual di marketplace/media sosial dengan volume ulasan/chat menengah-tinggi. |
| 6. Urgensi masalah | Tinggi dan berkelanjutan - ulasan/chat masuk setiap hari pada toko aktif; backlog analisis menumpuk tanpa alat bantu (bagian 6.12). |
| 7. Current workflow | Pemilik usaha membaca ulasan manual saat sempat, tanpa rekap sistematis, kehilangan pola/tren karena keterbatasan waktu dan bahasa informal. |
| 8. Root-cause analysis | Tidak tersedianya alat NLP terjangkau yang dilatih khusus Bahasa Indonesia informal/e-commerce; tools generik/bahasa Inggris tidak menangkap nuansa lokal (bagian 6.12). |
| 9. Evidence dari data resmi | BPS - Statistik E-Commerce 2024 (4,40 juta unit usaha); Kemenkop UKM (66 juta UMKM, >60% PDB) (bagian 5, 8). |
| 10. Evidence dari jurnal | Model IndoBERT untuk klasifikasi ulasan Bahasa Indonesia dilaporkan mencapai akurasi hingga 97% (bagian 9.4, PARTIALLY VERIFIED); aspect-based sentiment dengan Random Forest mencapai F1 0,835 (bagian 9.4, NOT FULLY ACCESSIBLE); riset agenda rekomendasi/AI e-commerce menyoroti tren menuju explainability (bagian 9.3). |
| 11. Evidence dari laporan industri | e-Conomy SEA 2025 menegaskan skala pertumbuhan commerce Indonesia (GMV ~USD 71 miliar) yang menyiratkan volume interaksi pelanggan yang sangat besar (bagian 5). |
| 12. Existing solution | Dashboard rating marketplace (skor rata-rata mentah) - Adjacent; tools sentiment SaaS internasional - Substitute mahal/tidak Bahasa Indonesia (bagian 11). |
| 13. Research gap | Methodological gap - penelitian sentimen Bahasa Indonesia berhenti di klasifikasi, belum menjembatani ke rekomendasi aksi bisnis (bagian 10.4, 12). |
| 14. Product gap | Tidak ditemukan produk yang menggabungkan analitik ulasan Bahasa Indonesia informal dengan output keputusan bisnis siap pakai untuk UMKM mikro (bagian 11, INFERENCE dari cakupan pencarian). |
| 15. Novelty claim yang defensible | Novelty implementasi dan konteks Indonesia: pipeline yang secara eksplisit menjembatani klasifikasi aspek-sentimen Bahasa Indonesia informal ke rekomendasi aksi bisnis terprioritas dan ter-ground pada kutipan asli - BUKAN mengklaim penemuan metode klasifikasi sentimen baru. |
| 16. Hipotesis solusi | Jika UMKM diberi ringkasan aspek bermasalah dan rekomendasi aksi terprioritas dari ulasan/chat mereka sendiri, mereka dapat membuat keputusan perbaikan produk/layanan lebih cepat dan tepat sasaran dibanding membaca manual. |
| 17. Peran AI | Mengklasifikasikan aspek dan sentimen dari teks tidak terstruktur berbahasa informal DAN kategori visual dari foto ulasan (opsional) dalam skala yang tidak mungkin dilakukan manual secara konsisten, lalu mengorkestrasi keduanya menjadi narasi actionable via foundation model. |
| 18. Mengapa AI diperlukan | Pola bahasa informal, slang, dan campuran bahasa daerah pada ulasan Indonesia tidak dapat ditangkap konsisten oleh pencarian kata kunci atau aturan manual (bagian 13.1). |
| 19. Alternatif non-AI | Pembacaan manual/pencatatan Excel - terbukti tidak proporsional di atas volume 50-100 ulasan/bulan (bagian 13.4). |
| 20. Dataset candidate | Teks: PRDECT-ID (Kaggle), e-commerce-sentiment-bahasa-indonesia (Hugging Face, 21.840 komentar berlabel), Tokopedia product reviews 2019 (Hugging Face, 40.607 ulasan) - lisensi PERLU diverifikasi ulang, tetap menjadi korpus utama fine-tuning teks. Visual: tidak ditemukan dataset foto ulasan Indonesia berlabel publik yang siap pakai, namun sejak Pembaruan v5 tersedia jalur akuisisi konkret - scraping bertarget via Apify (~250-300 foto ulasan riil Shopee dalam anggaran gratis $5/bulan, bagian 21B.6) untuk validasi/kalibrasi, dikombinasikan dengan anotasi manual skala kecil oleh tim. Status berubah dari DATA GAP murni menjadi REQUIRES USER VALIDATION dengan rencana penutupan yang jelas (bagian 21B.6, 23). |
| 21. Ground truth | Tersedia sebagian dari label sentimen/emosi dataset publik; ground truth untuk "relevansi rekomendasi aksi" perlu dibangun melalui validasi kualitatif pengguna. |
| 22. Baseline model | Pembacaan manual (non-AI) dan/atau model sederhana (Naive Bayes/keyword matching) sebagai baseline teknis pembanding sebelum menunjukkan keunggulan model fine-tuned. |
| 23. Model candidate | Fine-tuned IndoBERT/DistilBERT Bahasa Indonesia untuk klasifikasi aspek-sentimen teks; classifier ringan (linear/shallow head) di atas vision encoder pre-trained beku (mis. CLIP) untuk kategori visual foto ulasan; LLM ringan sebagai orkestrator tool-calling + RAG untuk narasi output. |
| 24. Bentuk kustomisasi AI | DIPERBARUI sesuai klarifikasi resmi panitia (bagian 2.9) - memenuhi tiga rute sekaligus: (a) fine-tuning model pre-trained Bahasa Indonesia pada domain ulasan e-commerce; (b) training model pendukung visual (classifier di atas vision encoder beku) yang terintegrasi dengan foundation model; (c) tool calling dari foundation model ke kedua model pendukung tersebut, dengan RAG yang ter-ground pada kutipan/temuan asli agar tidak berhalusinasi. |
| 25. Metrik teknis | F1-score/akurasi klasifikasi aspek dan sentimen pada data uji berlabel. |
| 26. Metrik bisnis | Waktu yang dihemat pemilik usaha dibanding membaca manual (proxy); tingkat kesesuaian rekomendasi menurut evaluasi kualitatif pengguna (proxy, REQUIRES USER VALIDATION). |
| 27. Metrik dampak sosial | Jumlah UMKM mitra yang melaporkan mengambil tindakan konkret berdasarkan rekomendasi (proxy, REQUIRES USER VALIDATION - belum ada baseline pengukuran). |
| 28. Risiko etik | Potensi bias jika data latih tidak representatif UMKM sangat mikro; risiko privasi jika data chat memuat informasi pribadi pelanggan (bagian 22). |
| 29. Risiko teknis | Kesalahan ekstraksi pada teks sangat informal/typo/singkatan yang tidak terwakili di data latih; data imbalance pada kelas sentimen tertentu; TAMBAHAN - model visual dilatih pada dataset anotasi manual berskala kecil sehingga rawan overfitting, perlu dibatasi pada kategori visual yang sedikit dan jelas (mis. 3-4 kelas) agar tetap robust. |
| 30. Risiko adopsi | UMKM mungkin tidak terbiasa mempercayai rekomendasi otomatis tanpa penjelasan (trust gap, bagian 12) - dimitigasi dengan menampilkan kutipan asli sebagai bukti setiap klasifikasi. |
| 31. Limitasi | MVP tahap penyisihan hanya memproses batch teks yang diunggah/ditempel manual, belum terintegrasi otomatis dengan API marketplace/WhatsApp (sesuai batasan MVP rulebook, bukan kekurangan, bagian 2.4). |
| 32. Asumsi kritis | UMKM bersedia membagikan data ulasan/chat mereka; volume ulasan yang dimiliki UMKM cukup besar untuk menghasilkan insight bermakna; rekomendasi aksi dianggap relevan (bukan generik) oleh pemilik usaha. |
| 33. Hal yang masih harus divalidasi | Kesediaan UMKM berbagi data riil (teks maupun foto ulasan); akurasi model teks pada data UMKM mikro spesifik; akurasi model visual pada sampel foto ulasan riil yang dianotasi tim; apakah rekomendasi aksi gabungan teks+visual benar-benar actionable menurut pemilik usaha, bukan sekadar restatement dari ulasan. |
| 34. Rencana wawancara pengguna | 5-8 wawancara UMKM mitra dari berbagai kategori produk (fesyen, F&B, kerajinan) mengikuti daftar pertanyaan bagian 7.3, dilakukan sebelum atau paralel dengan pengembangan MVP. |
| 35. Rencana eksperimen awal | Fine-tuning model kecil pada gabungan dataset publik, diuji pada 100-200 sampel ulasan riil dari 2-3 UMKM mitra untuk mengukur generalisasi di luar dataset training (lihat bagian 24). |
| 36. Alasan ide cocok untuk AIC | Selaras penuh dengan batasan MVP dan ketentuan kustomisasi rulebook (bagian 2), relevansi tema tinggi (UMKM = tulang punggung ekonomi Indonesia), dan dapat direproduksi lokal oleh juri tanpa hardware khusus. |
| 37. Alasan ide berpotensi masuk final | Kombinasi bukti kuat, dataset siap pakai, risiko keseluruhan rendah, dan narasi dampak sosial yang mudah dikomunikasikan secara meyakinkan pada video promosi. |
| 38. Alasan ide masih dapat gagal | Jika tim gagal mendapatkan data UMKM riil untuk validasi (hanya mengandalkan dataset publik generik), juri dapat mempertanyakan relevansi nyata terhadap UMKM mikro spesifik; atau jika rekomendasi aksi yang dihasilkan terasa generik/tidak actionable saat demo langsung. |


## 22. Risk, Ethics, Privacy, and Regulation


### 22.1 Pemetaan Risiko Umum Lintas Ide

| Kategori Risiko | Relevansi & Analisis |
| --- | --- |
| Personal data | Data chat pelanggan berpotensi memuat nomor telepon/alamat - relevan untuk InsightUlasan dan BalasCepat; wajib anonimisasi sebelum pemrosesan/pelatihan. |
| Profiling | Rendah untuk InsightUlasan (analisis agregat ulasan, bukan profil individu pelanggan); lebih relevan jika ide diperluas ke personalisasi individual di masa depan. |
| Consumer manipulation | Relevan untuk HargaCerdas jika rekomendasi harga disalahgunakan mendorong strategi harga yang eksploitatif - mitigasi: alat hanya membantu perhitungan margin transparan, bukan taktik psikologis harga. |
| Dark patterns | Tidak secara langsung diciptakan oleh ide-ide yang direkomendasikan; justru InsightUlasan berpotensi membantu mendeteksi keluhan konsumen terkait dark pattern pihak lain. |
| Discrimination/algorithmic bias | Relevan jika data latih InsightUlasan tidak representatif kategori produk/wilayah tertentu - mitigasi: evaluasi performa model per subkelompok data saat validasi. |
| Unfair pricing | Relevan untuk HargaCerdas - desain harus murni membantu efisiensi individual toko, bukan mendukung kolusi/koordinasi harga antar penjual yang melanggar prinsip persaingan usaha (perhatian KPPU, bagian 5). |
| Hallucination | Relevan pada lapisan RAG/ringkasan InsightUlasan dan BalasCepat - mitigasi: ringkasan wajib ter-ground pada kutipan asli yang ditampilkan ke pengguna. |
| Automation bias | Relevan untuk seluruh ide dengan output rekomendasi - mitigasi: human-in-the-loop wajib, sistem tidak mengeksekusi tindakan otomatis (harga/stok) tanpa konfirmasi manusia. |
| Misleading recommendation | Relevan untuk RekomenUMKM jika rekomendasi kategori/kata kunci keliru - mitigasi: menampilkan produk pembanding yang menjadi dasar rekomendasi (explainability). |
| Security | Data ulasan/chat yang diunggah pengguna perlu penanganan aman (tidak disimpan permanen tanpa persetujuan) - relevan pada tahap MVP maupun pengembangan lanjutan. |
| Unauthorized data scraping | Pembaruan v5: tim berencana memakai Apify (platform scraping pihak ketiga) untuk mengambil data validasi foto ulasan Shopee dalam volume kecil (~250-300 baris, anggaran gratis $5/bulan, bagian 21B.6). Data yang diambil bersifat PUBLIK TERLIHAT (halaman produk tanpa login); penyedia actor mencantumkan disclaimer kepatuhan ToS standar, namun ketiadaan konfirmasi tertulis langsung dari Shopee/Tokopedia berarti risiko residual tetap ada [PARTIALLY VERIFIED, bagian 21B.6.3]. Mitigasi wajib: batasi volume pada kebutuhan validasi (bukan scraping massal), anonimisasi nama akun/avatar/data pengukuran tubuh sebelum diproses, dan dokumentasikan sumber+tanggal pengambilan secara transparan pada proposal. |
| Intellectual property | Ulasan pelanggan adalah milik platform/pengguna asal; penggunaan untuk riset/MVP non-komersial pada tahap kompetisi perlu tetap mencantumkan sumber dataset sesuai lisensinya. |
| Consent | Data UMKM mitra untuk validasi (bagian 23) wajib dikumpulkan dengan persetujuan eksplisit dan tujuan penggunaan yang jelas. |
| Transparency | Seluruh ide finalis dirancang menampilkan alasan/bukti di balik rekomendasi (kutipan ulasan, komponen biaya, produk pembanding) sebagai respons terhadap trust gap (bagian 12). |


### 22.2 Relevansi terhadap Regulasi Indonesia

- UU Perlindungan Data Pribadi (UU PDP): relevan langsung bagi InsightUlasan dan BalasCepat karena memproses data chat yang berpotensi memuat data pribadi pelanggan UMKM - wajib anonimisasi dan pembatasan tujuan penggunaan data.
- Perlindungan konsumen (UU Perlindungan Konsumen & pengawasan BPKN): relevan bagi seluruh ide yang berinteraksi dengan sisi konsumen (UlasanAsli, WaspadaToko, TemanBelanja) - rekomendasi/skor yang dihasilkan tidak boleh menyesatkan atau memberi rasa aman palsu.
- Ketentuan perdagangan elektronik (PMSE - Kemendag): relevan sebagai konteks regulasi transaksi elektronik yang menjadi payung bagi seluruh masalah Smart Commerce yang dibahas.
- Pengawasan persaingan usaha (KPPU): relevan khusus bagi HargaCerdas - desain wajib memastikan alat membantu efisiensi individual, bukan memfasilitasi predatory pricing atau kolusi harga antar penjual.


### 22.3 Mitigasi Proporsional untuk MVP

- Anonimisasi otomatis pola data pribadi (nomor telepon, alamat) pada teks chat sebelum diproses model, sebagai langkah minimum wajib meski MVP tidak memerlukan sistem keamanan kompleks.
- Menampilkan disclaimer eksplisit bahwa output adalah rekomendasi/estimasi untuk dipertimbangkan, bukan keputusan final otomatis, terutama pada HargaCerdas.
- Confidence score dan kutipan sumber pada setiap output InsightUlasan/RekomenUMKM sebagai bentuk transparansi minimum yang proporsional untuk tahap MVP.
- Menghindari penyimpanan data pengguna secara permanen pada MVP demonstrasi (data hanya diproses selama sesi, sesuai batasan MVP yang tidak mewajibkan database kompleks, bagian 2.5).


## 23. User Validation Plan

| Langkah Validasi | Deskripsi Singkat untuk InsightUlasan |
| --- | --- |
| 1. Wawancara pengguna | 5-8 wawancara UMKM lintas kategori (fesyen, F&B, kerajinan) menggunakan daftar pertanyaan bagian 7.3, fokus pada volume ulasan riil dan kesediaan berbagi data. |
| 2. Expert interview | 1-2 wawancara pakar NLP Bahasa Indonesia atau praktisi UMKM digital untuk menilai kelayakan teknis dan relevansi bisnis pendekatan. |
| 3. Survey | Survei singkat ke komunitas UMKM online (mis. grup Facebook/Telegram UMKM) untuk memvalidasi skala masalah secara lebih luas dari sampel wawancara. |
| 4. Data audit | Audit kualitas dan representativitas dataset publik (PRDECT-ID, e-commerce-sentiment-bahasa-indonesia) - memeriksa distribusi kategori produk, tingkat noise, dan kesesuaian lisensi. Untuk komponen visual: jalankan batch awal Apify (~250-300 foto ulasan Shopee, bagian 21B.6) dan audit distribusi kategori produk/kualitas foto sebelum dipakai validasi Langkah 4 (bagian 21B.2). |
| 5. Baseline experiment | Membandingkan waktu dan akurasi identifikasi masalah utama antara pembacaan manual vs output model pada sampel ulasan yang sama. |
| 6. Small-scale model experiment | Fine-tuning model kecil pada dataset publik, diuji pada 100-200 ulasan riil dari UMKM mitra untuk mengukur generalisasi. |
| 7. Error analysis | Menelaah kasus kesalahan klasifikasi (khususnya pada bahasa sangat informal/typo) untuk mengidentifikasi kebutuhan augmentasi data. |
| 8. Usability test | Menguji apakah pemilik UMKM dapat memahami dan menindaklanjuti ringkasan/rekomendasi tanpa penjelasan tambahan dari tim. |
| 9. Willingness-to-adopt test | Mengukur kesediaan UMKM mitra menggunakan alat secara berkelanjutan (bukan hanya sekali coba) setelah demo. |
| 10. Impact measurement | Menyusun rencana pengukuran dampak jangka menengah (mis. perubahan rating toko) sebagai rencana pasca-kompetisi, bukan target MVP penyisihan. |


### 23.1 Tabel Asumsi dan Risiko

| Assumption | Risk Level | Evidence Saat Ini | Validation Method | Minimum Success Criterion | Decision if Invalidated |
| --- | --- | --- | --- | --- | --- |
| UMKM bersedia membagikan data ulasan/chat | Sedang | Belum divalidasi langsung [ASSUMPTION] | Wawancara langsung + permintaan sampel data | Minimal 5 UMKM bersedia berbagi data untuk uji coba | Beralih ke dataset publik sepenuhnya + data sintetik terverifikasi, kurangi klaim personalisasi per-toko |
| Volume ulasan UMKM cukup besar untuk insight bermakna | Sedang | Tidak ada data granular volume ulasan per UMKM mikro [DATA GAP] | Audit data dari UMKM mitra saat wawancara | Rata-rata >30 ulasan/bulan pada UMKM mitra | Fokuskan pada UMKM dengan volume lebih tinggi (bukan target seluruh UMKM mikro) |
| Model fine-tuned generalisasi baik ke bahasa informal riil UMKM | Tinggi | Klaim akurasi tinggi (83-97%) bervariasi antar studi (bagian 9.4, 10.4) | Small-scale model experiment pada data riil UMKM mitra | F1-score >0,75 pada data uji riil (bukan hanya data publik) | Tambahkan augmentasi data/human-in-the-loop lebih kuat, turunkan klaim akurasi pada proposal |
| Rekomendasi aksi dianggap relevan (bukan generik) | Sedang-tinggi | Belum divalidasi [ASSUMPTION] | Usability test dengan UMKM mitra | Mayoritas UMKM mitra menyatakan rekomendasi "membantu" atau "sangat membantu" | Redesain lapisan ringkasan agar lebih spesifik & actionable, bukan restatement ulasan |


## 24. Technical Experiment Plan for the Next Stage

Rencana berikut BUKAN implementasi pada tahap riset ini, melainkan garis besar eksperimen awal yang direkomendasikan pada tahap pengembangan MVP berikutnya, khusus untuk InsightUlasan.

- Eksperimen 1 - Baseline non-AI: mengukur waktu rata-rata pembacaan manual 100 ulasan oleh anggota tim sebagai baseline pembanding.
- Eksperimen 2 - Fine-tuning model dasar: fine-tuning DistilBERT/IndoBERT kecil pada gabungan dataset publik (PRDECT-ID, e-commerce-sentiment-bahasa-indonesia), diukur dengan F1-score pada held-out test set.
- Eksperimen 3 - Uji generalisasi: menguji model pada sampel ulasan riil dari 2-3 UMKM mitra (di luar distribusi data training) untuk mengukur penurunan performa akibat domain shift.
- Eksperimen 4 - Desain lapisan ringkasan: membandingkan pendekatan ringkasan ekstraktif sederhana vs RAG ringan untuk melihat trade-off kualitas narasi vs risiko halusinasi.
- Eksperimen 5 - Uji augmentasi data: jika ditemukan kelas aspek/sentimen minoritas kurang terwakili, menguji dampak augmentasi data sintetik terverifikasi manual terhadap F1-score kelas tersebut.
- Seluruh eksperimen direkomendasikan dijalankan pada infrastruktur lokal/CPU-friendly (model kecil) agar selaras dengan ketentuan reproducibility lokal rulebook (bagian 2.6).


## 25. Open Questions

- Apakah panitia AIC akan memberikan klarifikasi lebih rinci mengenai definisi "kustomisasi" yang dapat diterima selain daftar yang sudah diinterpretasikan pada bagian 2.9?
- Apakah rubrik penilaian babak final (hackathon, live pitching) akan berbeda signifikan dari rubrik penyisihan yang tercantum pada rulebook (bagian 2.11)?
- Sejauh mana lisensi dataset publik (PRDECT-ID, e-commerce-sentiment-bahasa-indonesia, Tokopedia reviews) benar-benar mengizinkan penggunaan untuk kompetisi/riset - perlu verifikasi halaman lisensi masing-masing secara langsung sebelum proposal final.
- Apakah UMKM mitra riil bersedia dan tersedia untuk diwawancarai serta berbagi data dalam jangka waktu kompetisi yang terbatas (17 Juni-25 Agustus 2026)?
- Seberapa besar variasi bahasa informal/slang/campur bahasa daerah pada ulasan UMKM riil dibanding dataset publik yang tersedia - apakah cukup mirip untuk transfer learning berhasil baik?
- Apakah tim memiliki keahlian teknis untuk fine-tuning model transformer dalam waktu kompetisi, ataukah perlu penyesuaian ke pendekatan yang lebih ringan (mis. klasik ML dengan fitur TF-IDF) sebagai fallback?
- Bagaimana batasan yang tepat antara ringkasan ekstraktif berbasis kutipan asli (rendah risiko halusinasi) vs ringkasan generatif (lebih persuasif namun berisiko halusinasi) untuk lapisan output akhir?


## 26. Final Recommendation

Berdasarkan seluruh tahapan riset (landscape scanning hingga idea comparison), dossier ini merekomendasikan tim melanjutkan eksplorasi ide InsightUlasan sebagai kandidat utama untuk subtema Smart Commerce, dengan HargaCerdas dan RekomenUMKM sebagai kandidat cadangan apabila validasi pengguna (bagian 23) mengungkap hambatan signifikan pada InsightUlasan (misalnya, UMKM sangat enggan berbagi data ulasan/chat).

Sebelum menyusun proposal/MVP, tim WAJIB menuntaskan minimal: (1) wawancara dengan sekurangnya 5 UMKM mitra untuk memvalidasi volume dan karakteristik data ulasan riil; (2) verifikasi lisensi seluruh dataset publik yang akan digunakan; dan (3) eksperimen fine-tuning skala kecil untuk memvalidasi bahwa performa model pada data publik dapat digeneralisasi ke data riil UMKM Indonesia yang sangat informal. Dossier ini secara sengaja TIDAK menyertakan kode program, arsitektur produksi, atau wireframe sesuai batasan yang diminta - seluruh hal tersebut adalah pekerjaan tahap berikutnya setelah validasi di atas selesai.


## 21A. Technology Frontier Scan: Global AI Innovations Applied (Pembaruan v3)

Bagian tambahan ini menjawab permintaan eksplisit untuk menelusuri teknologi AI terkini dari seluruh dunia (riset 2025-2026) dan memetakan versi adaptasinya yang REALISTIS untuk MVP kompetisi ini - bukan sekadar menambah kompleksitas demi kesan canggih, melainkan menutup risiko/gap yang sudah teridentifikasi pada bagian 12, 14, 19.1, dan 21, sekaligus menaikkan skor pada kriteria berbobot terbesar rulebook (Implementasi Teknologi & Kematangan Arsitektur, 25%).


### 21A.1 Tabel Teknologi Frontier dan Adaptasinya

| Teknologi Global (2025-2026) | Sumber & Status | Masalah/Risiko yang Diatasi | Adaptasi Konkret untuk MVP | Risiko Overbuilt |
| --- | --- | --- | --- | --- |
| LLM regional Asia Tenggara open-weight (SEA-LION, Sailor2, Cendol, Merak/Komodo) | Cendol: arXiv:2404.06138 [PREPRINT]; Komodo: arXiv:2403.09362 [PREPRINT]; Sailor2: sea-sailor.github.io [INDUSTRY/RESEARCH]; SEA-LION: AI Singapore [INDUSTRY] | Foundation model generik/proprietary API sulit direproduksi lokal oleh juri (bagian 2.6) dan tidak dioptimalkan Bahasa Indonesia | Gunakan model bobot-terbuka (dapat diunduh, di-quantize untuk CPU) sebagai foundation model orkestrator pengganti API komersial tertutup | Rendah - drop-in replacement peran orkestrator, tidak menambah lapisan arsitektur baru |
| Zero-shot vision-language anomaly detection (PA-CLIP, AFR-CLIP, GlobalCLIP) | arXiv:2503.01292, arXiv:2503.12910 [PREPRINT]; ScienceDirect pii S0957417425030647 [NOT FULLY ACCESSIBLE] | Data gap komponen visual - sebelumnya (bagian 19.1/21) diasumsikan perlu anotasi manual 30-100 foto ulasan yang belum tentu tersedia | Klasifikasi foto ulasan via prompt teks pada CLIP/SigLIP BEKU ("foto produk rusak" vs "foto produk baik/sesuai"), TANPA dataset berlabel - anotasi manual jadi opsional (hanya untuk kalibrasi lanjutan, bukan syarat MVP) | Rendah - justru MENGURANGI risiko dibanding pendekatan classifier terlatih sebelumnya |
| BGE-M3 multilingual embedding (BAAI) | Dokumentasi model & tinjauan teknis pihak ketiga [PARTIALLY VERIFIED - bukan paper primer yang diakses langsung] | Embedding RAG generik kurang optimal pada teks Bahasa Indonesia informal/campur bahasa daerah | Ganti model embedding retrieval pada lapisan RAG dengan BGE-M3 self-hosted (open-weight, mendukung >100 bahasa termasuk performa baik pada bahasa low-resource) | Rendah - penggantian komponen embedding, bukan penambahan modul baru |
| Sintesis data berbasis LLM untuk klasifikasi teks bahasa rendah-sumber daya, termasuk riset spesifik bahasa Jawa/Sunda | arXiv:2502.12932 (studi Jawa & Sunda) [PREPRINT]; arXiv:2404.02422 (PEFT+data sintetik) [PREPRINT]; arXiv:2601.16278 [PREPRINT] | Data imbalance dan keterwakilan rendah untuk ulasan berbahasa daerah/sangat informal pada dataset training (bagian 14) | Bangkitkan contoh ulasan sintetik tambahan via LLM untuk kelas aspek/pola bahasa daerah yang kurang terwakili, disaring otomatis lalu divalidasi manual sampel sebelum dicampur ke data fine-tuning IndoBERT | Sedang - wajib validasi manual sampel sintetik (sudah direncanakan pada bagian 14.2 dan 23), agar tidak memasukkan data berkualitas rendah |
| Conformal prediction untuk kalibrasi confidence | arXiv:2509.00461, arXiv:2604.16217 [PREPRINT] | Confidence score sebelumnya (bagian 13.1) bersifat heuristik tanpa jaminan statistik formal | STRETCH GOAL opsional pasca-penyisihan: tampilkan prediction set/interval kalibrasi alih-alih skor tunggal untuk klasifikasi aspek-sentimen | Sedang-tinggi - SENGAJA ditandai opsional/pengembangan lanjutan, bukan syarat MVP penyisihan agar tidak overbuilt |
| Tren agentic commerce & zero-click discovery | MetaRouter, commercetools, Tredence - ringkasan tren industri [INDUSTRY REPORT/CLAIM] | Bukan teknologi yang langsung diadopsi, melainkan validasi konteks pasar bahwa arsitektur tool-calling/agentic yang dipilih selaras arah industri | Memperkuat narasi "mengapa sekarang" pada proposal/video: 73% konsumen sudah memakai asisten AI dalam perjalanan belanja, sehingga UMKM yang tertinggal kapabilitas serupa (mendengarkan pelanggan via AI) berisiko semakin tertinggal | Tidak relevan (konteks strategis, bukan komponen teknis tambahan) |


### 21A.2 Arsitektur InsightUlasan yang Diperbarui (Flagship, v3)

Empat lapisan berikut menggantikan deskripsi arsitektur pada bagian 19.1/21 (v2), dengan pembagian jelas antara komponen WAJIB tahap penyisihan dan komponen STRETCH pengembangan lanjutan agar tetap sesuai batasan MVP rulebook (bagian 2.4-2.6).

| Aspek | Keterangan |
| --- | --- |
| Lapisan 1 - Model pendukung teks (WAJIB) | Fine-tuned IndoBERT/DistilBERT untuk klasifikasi aspek+sentimen, DIPERKAYA data latih sintetik hasil augmentasi LLM untuk pola bahasa daerah/sangat informal (mitigasi language/dialect gap, bagian 10.4). |
| Lapisan 2 - Model pendukung visual (WAJIB, versi ringan) | Zero-shot CLIP/SigLIP BEKU dengan prompt teks untuk menandai kategori visual dasar (rusak/tidak sesuai/normal) pada foto ulasan opsional - TIDAK memerlukan dataset berlabel Indonesia, sehingga data gap yang sebelumnya jadi risiko utama (bagian 19.1) kini tertutup pada level MVP. |
| Lapisan 3 - Retrieval untuk grounding (WAJIB) | BGE-M3 sebagai model embedding untuk mengambil kutipan ulasan paling relevan sebagai bukti setiap klaim pada ringkasan akhir (mendukung explainability, bagian 12). |
| Lapisan 4 - Foundation model orkestrator (WAJIB) | LLM open-weight regional (Sailor2/Cendol/SEA-LION, dapat di-quantize untuk CPU) yang memanggil Lapisan 1-3 sebagai tools, lalu menyusun ringkasan+rekomendasi aksi akhir - dapat dijalankan lokal, memenuhi ketentuan reproducibility (bagian 2.6) tanpa bergantung API berbayar eksternal. |
| Lapisan 5 - Kalibrasi confidence (STRETCH, opsional) | Conformal prediction untuk interval keyakinan pada klasifikasi - direkomendasikan sebagai pengembangan pasca-penyisihan, bukan syarat MVP awal. |


### 21A.3 Mengapa Arsitektur Ini Menjawab Langsung Kriteria Berbobot Terbesar Rulebook (25%)

| Sub-Pertanyaan Rubrik Implementasi Teknologi (bagian 2.11) | Jawaban Arsitektur v3 |
| --- | --- |
| Apakah pemilihan teknologi (model AI, framework, stack) sesuai dan proporsional dengan kebutuhan solusi? | Ya - setiap komponen dipilih untuk menutup gap spesifik yang sudah dibuktikan pada riset (bahasa daerah, foto ulasan, reproducibility lokal), bukan ditambahkan demi kesan canggih; komponen STRETCH (conformal prediction) eksplisit dipisahkan agar tidak membebani MVP. |
| Apakah implementasi AI berfokus pada core inference yang bersih, dengan parameter yang terdefinisi jelas? | Ya - keempat lapisan wajib tetap statis saat demonstrasi (tidak ada auto-tuning), sesuai batasan MVP rulebook (bagian 2.4). |
| Seberapa modular arsitektur yang dihasilkan - apakah komponen AI, backend, dan frontend terpisah dengan bersih? | Ya - setiap lapisan (teks, visual, retrieval, orkestrator) adalah tool terpisah yang dipanggil foundation model, memudahkan juri memverifikasi tiap komponen secara independen saat code review. |
| Apakah terdapat dokumentasi teknis (README) yang cukup untuk memahami alur sistem secara keseluruhan? | Rencana README wajib mencantumkan diagram lapisan di atas beserta sumber setiap model (SEA-LION/Sailor2/Cendol, CLIP/SigLIP, BGE-M3, IndoBERT) dan justifikasi pemilihannya - mengacu langsung ke bagian ini. |


### 21A.4 Dampak terhadap Weighted Decision Matrix (Pembaruan)

Dengan resolusi data gap visual (via zero-shot CLIP) dan penguatan reproducibility lokal (via LLM regional open-weight), skor "Risiko teknis" InsightUlasan pada bagian 18 dinaikkan dari 7 menjadi 8 (skala risiko rendah=baik), dan "Ketersediaan dataset" dipertahankan pada skor maksimal karena komponen visual kini tidak lagi bergantung pada dataset berlabel yang belum ditemukan. Total weighted score InsightUlasan naik dari 8.22 menjadi kisaran 8.3+ pada rekomputasi (lihat lampiran perhitungan bagian 18), MEMPERLEBAR jarak dengan HargaCerdas (peringkat 2) - lihat detail angka pada versi terbaru tabel 18.3.


### 21A.5 Keterbatasan yang Tetap Harus Diakui Jujur

- Model LLM regional (SEA-LION/Sailor2/Cendol) umumnya berukuran lebih kecil dan dilatih dengan sumber daya jauh lebih terbatas dibanding model global (GPT/Claude/Gemini) - kualitas orkestrasi/penalaran bisa lebih rendah, perlu diuji langsung sebelum proposal final [REQUIRES USER VALIDATION].
- Zero-shot CLIP untuk defect detection pada literatur yang ditemukan sebagian besar diuji pada konteks manufaktur/industri (bukan foto ulasan e-commerce konsumen) - generalisasi ke foto ulasan UMKM Indonesia (pencahayaan buruk, sudut foto asal-asalan) belum terbukti dan WAJIB diuji pada sampel nyata sebelum diklaim berfungsi.
- Mayoritas sumber pada tabel 21A.1 berstatus PREPRINT (arXiv, belum peer-review) - tim wajib menyebutkan status ini secara jujur pada proposal, bukan mengklaimnya sebagai metode "terbukti" tanpa syarat.
- Kombinasi 4 lapisan wajib meningkatkan jumlah dependency (model) yang perlu di-setup lewat docker compose - README harus benar-benar teruji agar tidak melanggar ketentuan reproducibility (bagian 2.6); disarankan menyediakan mode fallback (jika model regional gagal dimuat, sistem tetap berjalan dengan IndoBERT+CLIP saja tanpa orkestrator LLM) agar demonstrasi tidak gagal total karena satu komponen bermasalah.


## 21B. Kaji Ulang Final: Staging Computer Vision, Fitur Kreatif Tambahan, dan Audit Kejujuran (Pembaruan v4)

Bagian ini adalah kaji ulang kritis atas dua pertanyaan langsung: (1) apakah computer vision benar-benar WAJIB, dan bagaimana implementasinya secara konkret jika dipilih; (2) di mana dossier ini masih kurang kreatif/inovatif. Ditutup dengan audit kejujuran mengenai batas maksimal "kualitas 10/10" yang dapat dicapai riset desk-research tanpa validasi pengguna langsung.


### 21B.1 Apakah Computer Vision Wajib? Keputusan Tim: YA, Digunakan - Tier 2 Naik Status Menjadi Wajib untuk Penyisihan (Pembaruan v5)

CATATAN REVISI v5: rekomendasi versi v4 di bawah ini awalnya menyarankan CV sebagai Tier 2/OPSIONAL karena dua risiko yang belum terkelola: (a) generalisasi zero-shot dari domain industri ke foto ulasan konsumen belum terbukti, dan (b) tidak ada jalur konkret untuk mendapatkan sampel foto ulasan riil guna validasi sebelum deadline. Tim secara eksplisit MEMUTUSKAN untuk tetap menggunakan CV terlepas dari rekomendasi tersebut. Keputusan ini DIHORMATI dan Tier 2 dinaikkan statusnya dari opsional menjadi bagian dari cakupan wajib penyisihan - namun perlu digarisbawahi secara jujur bahwa keputusan ini mengubah PRIORITAS RISIKO tim, bukan MENGHILANGKAN risiko itu sendiri. Yang berubah secara substantif sejak v4 adalah risiko (b): bagian 21B.6 di bawah menyusun rencana akuisisi data foto ulasan riil yang konkret dan terjangkau (Apify, dalam anggaran gratis $5/bulan), yang secara langsung menutup syarat validasi 20-30 foto riil pada Langkah 4 (bagian 21B.2) yang sebelumnya menjadi alasan utama status "belum siap". Risiko (a) - generalisasi domain zero-shot CLIP dari industri ke foto konsumen - TETAP belum terbukti dan HANYA akan terjawab setelah tim benar-benar menjalankan validasi tersebut; dossier ini tidak dapat dan tidak akan mengklaim keberhasilan yang belum diuji.

Rekomendasi konkret yang diperbarui: pertahankan struktur bertingkat (arsitektur dengan fallback tetap merupakan praktik teknis yang baik terlepas dari status wajib/opsional), namun Tier 1 dan Tier 2 sekarang SAMA-SAMA wajib diselesaikan sebelum deadline penyisihan, dengan Tier 2 tetap membawa fallback eksplisit ke Tier 1 sebagai jaring pengaman jika validasi visual gagal memenuhi ambang keyakinan minimum saat diuji nyata (bagian 21B.2 Langkah 4-5).

| Tingkat | Cakupan | Kapan Dikerjakan | Risiko | Wajib? (v5) |
| --- | --- | --- | --- | --- |
| Tier 1 - Inti (Core, Teks) | Model pendukung teks (fine-tuned IndoBERT/DistilBERT) + retrieval RAG (BGE-M3) + foundation model orkestrator (LLM regional open-weight) + fitur Tanya-Jawab interaktif (bagian 21B.3) - SELURUHNYA berbasis teks | Wajib selesai sebelum 25 Agustus 2026 (deadline penyisihan) | Rendah - seluruh komponen berbasis dataset yang sudah terverifikasi tersedia (bagian 14) | WAJIB |
| Tier 2 - Visual (kini wajib) | Zero-shot CLIP/SigLIP untuk kategori visual dasar pada foto ulasan, dengan fallback otomatis ke Tier 1 jika model visual gagal dimuat/skor keyakinan di bawah ambang/foto tidak tersedia; divalidasi pada sampel riil hasil akuisisi Apify (bagian 21B.6) sebelum diklaim berfungsi | WAJIB dikerjakan paralel dengan Tier 1, dengan Langkah 4 (validasi manual, bagian 21B.2) dijadwalkan SEBELUM tim menulis narasi hasil di proposal/video | Sedang, TERKELOLA SEBAGIAN - domain-shift industri-ke-konsumen masih perlu dibuktikan lewat validasi nyata (21B.2 Langkah 4), tetapi jalur data untuk validasi tersebut kini konkret (21B.6) | WAJIB (v5) - fallback tetap wajib ada sebagai jaring pengaman |
| Tier 3 - Pengembangan Babak Final | Kalibrasi visual dengan sampel foto riil lebih besar (fine-tuning ringan/few-shot), conformal prediction untuk confidence, peer benchmarking skala penuh (bagian 21B.3), potensi integrasi WhatsApp Business API | Selama periode mentoring/hackathon babak final (20-26 September 2026), jika lolos 8 besar | N/A - dikerjakan setelah lolos, dengan waktu dan umpan balik mentor yang lebih jelas | Roadmap pengembangan (boleh disebut di proposal sebagai visi lanjutan, TIDAK perlu berfungsi penuh saat penyisihan) |

Konsekuensi langsung dari perubahan status ini: (1) Langkah 4 pada bagian 21B.2 ("validasi kecil SEBELUM klaim berfungsi") berubah dari langkah opsional-jika-sempat menjadi GERBANG WAJIB - tim TIDAK BOLEH mencantumkan hasil/skor visual pada proposal maupun video promosi sebelum langkah ini benar-benar dijalankan pada sampel riil; (2) fallback eksplisit (Langkah 5, bagian 21B.2) menjadi lebih penting, bukan kurang penting, karena sekarang modul visual selalu aktif dalam alur, bukan hanya saat sengaja diaktifkan; (3) risiko reproducibility saat live demo/cross-check juri (bagian 2.6) tetap nyata dan harus dimitigasi dengan pengujian ulang end-to-end menjelang submission, bukan diasumsikan aman karena sudah "wajib".


### 21B.2 Jika Tim Tetap Ingin Mengimplementasikan Computer Vision Sekarang: Langkah Konkret

| Aspek | Keterangan |
| --- | --- |
| Langkah 1 - Pilih model dasar | Gunakan encoder vision-language pre-trained yang sudah tersedia bobotnya secara terbuka (mis. CLIP ViT-B/32 atau SigLIP), BUKAN melatih model dari nol - model dibekukan (frozen), tidak perlu GPU besar. |
| Langkah 2 - Rancang prompt klasifikasi | Susun beberapa pasangan prompt teks kontras per kategori, mis. untuk kelas "barang rusak": ["foto produk yang rusak atau cacat", "foto produk dalam kondisi baik"] - skor kemiripan foto terhadap tiap prompt menentukan label. |
| Langkah 3 - Batasi jumlah kelas | Maksimal 3-4 kategori visual (rusak, salah kirim/tidak sesuai, kemasan rusak, normal) - semakin sedikit dan jelas kelasnya, semakin tinggi keandalan zero-shot (prinsip umum di literatur klasifikasi zero-shot, bagian 21A.1). |
| Langkah 4 - Validasi kecil SEBELUM klaim berfungsi | WAJIB uji pada minimal 20-30 foto ulasan riil (bisa diambil dari review publik di marketplace dengan izin/screenshot demo) dan hitung akurasi kasar secara manual sebelum mencantumkan hasil visual di proposal/video - JANGAN mengklaim performa tanpa uji ini. |
| Langkah 5 - Rancang fallback eksplisit | Jika skor kemiripan tidak melewati ambang keyakinan tertentu untuk semua kelas, sistem WAJIB menampilkan "tidak dapat menyimpulkan dari foto" alih-alih memaksakan label - mencegah klaim keliru yang berisiko menyesatkan pemilik UMKM. |
| Langkah 6 - Integrasi ke orkestrator | Daftarkan model visual sebagai satu tool yang dapat dipanggil foundation model HANYA ketika field foto pada entri ulasan terisi - jika kosong, alur otomatis lanjut ke Tier 1 tanpa error. |
| Estimasi effort tambahan | Relatif rendah dari sisi kode (memanggil model pre-trained + logika ambang batas), namun effort validasi manual (Langkah 4) tidak boleh dilewati - inilah bagian yang paling sering diabaikan tim kompetisi dan berujung klaim tidak teruji. |


### 21B.3 Dua Fitur Kreatif yang Sebelumnya Belum Digali (Mengisi Kekurangan Inovasi)

Setelah dikaji ulang, dossier versi sebelumnya kuat secara EVIDENCE namun relatif konservatif secara PENGALAMAN PENGGUNA - insight report bersifat satu arah (sistem -> pengguna) dan tidak memanfaatkan konteks kompetitif. Dua penambahan berikut mengisi celah ini tanpa menambah risiko teknis berarti, karena keduanya dibangun di atas komponen yang SUDAH ada di Tier 1.


#### Fitur A - Tanya-Jawab Interaktif atas Ulasan (bukan hanya laporan statis)

| Aspek | Keterangan |
| --- | --- |
| Ide inti | Alih-alih hanya menampilkan ringkasan tetap, pengguna (atau JURI saat live demo) dapat mengetik pertanyaan bebas tentang kumpulan ulasan yang sama, mis. "Kenapa keluhan ukuran naik bulan ini?" atau "Tunjukkan ulasan paling negatif soal pengiriman", dan sistem menjawab dengan kutipan asli sebagai bukti. |
| Mengapa ini menaikkan nilai kompetisi | Format Live Pitching dan sesi tanya-jawab juri (bagian rulebook mengenai babak final) sangat cocok dengan fitur ini - juri dapat MENCOBA LANGSUNG bertanya apa pun saat demo, bukan hanya menonton video, yang jauh lebih meyakinkan daripada laporan statis dan secara langsung menunjukkan penguasaan tim atas sistem yang dibangun sendiri. |
| Kebutuhan teknis tambahan | TIDAK ADA komponen baru - fitur ini murni mengekspos ulang kemampuan RAG+foundation model orkestrator yang sudah menjadi bagian Tier 1 (bagian 21A.2) sebagai antarmuka tanya-jawab, bukan hanya laporan sekali jalan. |
| Risiko | Pertanyaan di luar cakupan data (mis. menanyakan hal yang tidak ada di ulasan) berisiko membuat model mengarang jawaban (halusinasi) - mitigasi: jika retrieval tidak menemukan kutipan relevan, sistem wajib menjawab "tidak ditemukan informasi terkait pada ulasan yang diunggah" alih-alih memaksakan jawaban. |


#### Fitur B - Peer/Category Benchmarking (konteks kompetitif, bukan sekadar analisis diri sendiri)

| Aspek | Keterangan |
| --- | --- |
| Ide inti | Selain menganalisis ulasan toko pengguna sendiri, sistem membandingkan distribusi keluhan toko tersebut terhadap distribusi rata-rata kategori sejenis, mis. "30% ulasan Anda mengeluhkan ukuran, dibanding rata-rata 12% pada kategori fesyen sejenis" - memberi konteks apakah suatu masalah benar-benar di atas rata-rata atau memang wajar di kategori tersebut. |
| Mengapa ini kreatif dan bernilai | Mengubah tool dari "cermin" (hanya menunjukkan apa yang sudah diketahui UMKM secara samar) menjadi "kompas" (menunjukkan posisi relatif terhadap kompetitor) - nilai bisnis yang jauh lebih tinggi dan belum ditemukan pada kompetitor manapun yang ditelusuri (bagian 11). |
| Kebutuhan data tambahan | TIDAK PERLU data baru - baseline kategori dihitung SEKALI dari dataset publik yang sama yang sudah dipakai untuk fine-tuning (PRDECT-ID, e-commerce-sentiment-bahasa-indonesia, Tokopedia reviews, bagian 14), dikelompokkan per kategori produk yang tersedia pada metadata dataset tersebut. |
| Risiko | Dataset publik mungkin tidak merepresentasikan seluruh kategori produk UMKM secara merata (bias representasi, sudah dicatat sebagai potensi bias pada bagian 14.2) - mitigasi: tampilkan ukuran sampel baseline secara transparan ("dibandingkan dari N ulasan kategori sejenis") agar pengguna dapat menilai keandalannya sendiri, bukan angka yang diklaim mutlak benar. |


### 21B.4 Mengisi Kekurangan pada Business Value dan Governance (Bonus 3.5%)

Audit ulang menemukan dossier versi sebelumnya BELUM menjawab eksplisit kriteria bonus "Business Value dan Governance" pada rulebook (bagian 2.11), yang meminta model bisnis/analisis kelayakan adopsi industri yang realistis. Berikut pengisian celah tersebut, bersifat hipotesis awal yang WAJIB divalidasi (bukan rencana bisnis final).

| Aspek | Keterangan |
| --- | --- |
| Model adopsi yang diusulkan | Freemium bertingkat: (a) Gratis - insight teks dasar untuk UMKM sangat mikro (selaras misi digital inclusion, bagian 5, 8); (b) Berbayar ringan - tambahan modul visual (Tier 2) dan peer benchmarking untuk UMKM dengan volume ulasan lebih tinggi yang bersedia membayar untuk insight lebih dalam. |
| Mengapa model ini realistis | Selaras dengan kesenjangan yang ditemukan pada bagian 5: ~30% UMKM aktif secara digital namun mayoritas belum memakai kapabilitas analitik lanjutan karena keterbatasan anggaran - tier gratis menghilangkan barrier awal, tier berbayar menyasar segmen yang sudah lebih mapan. |
| Potensi mitra adopsi | Asosiasi UMKM, koperasi pasar digital, atau program pembinaan UMKM Kemenkop/Kemendag sebagai jalur distribusi awal (bukan klaim kemitraan yang sudah terjalin, murni potensi yang perlu dijajaki - REQUIRES USER VALIDATION). |
| Governance/tata kelola AI | Kebijakan retensi data eksplisit (data ulasan pengguna tidak disimpan permanen tanpa persetujuan, bagian 22), serta pencantuman confidence/limitasi model secara transparan pada setiap output - selaras kerangka trust-and-ethics SME dari SME-TEAM (bagian 9.6) yang menekankan trust dan etika sebagai fondasi adopsi AI pada usaha kecil. |
| Risiko model bisnis | Willingness-to-pay UMKM mikro Indonesia untuk tools analitik belum terverifikasi langsung (REQUIRES USER VALIDATION, terkait pertanyaan wawancara bagian 7.3) - model freemium bisa jadi perlu direvisi total pasca-wawancara. |


### 21B.5 Audit Kejujuran: Batas Maksimal Kualitas Riset Desk-Research

Sebelum ditutup, penting disampaikan secara jujur: TIDAK ADA riset desk-research (tanpa wawancara/eksperimen langsung) yang benar-benar dapat mencapai "10/10" dalam artian sesungguhnya, karena beberapa hal secara struktural TIDAK BISA diverifikasi hanya lewat pencarian web:

- Apakah UMKM Indonesia riil benar-benar bersedia membagikan data ulasan/foto mereka - ini FAKTA LAPANGAN yang hanya bisa dijawab lewat wawancara langsung (bagian 23), bukan literatur.
- Apakah model zero-shot CLIP benar-benar bekerja baik pada foto ulasan marketplace Indonesia yang asal-asalan - ini HASIL EKSPERIMEN yang hanya bisa dibuktikan dengan menjalankan kode sungguhan pada sampel nyata (bagian 21B.2 langkah 4), bukan klaim dari paper domain lain (industri/manufaktur). Pembaruan v5: jalur untuk memperoleh sampel nyata tersebut kini konkret (Apify, bagian 21B.6), TETAPI ketersediaan jalur data BUKAN bukti bahwa modelnya akan bekerja baik - dua hal yang berbeda dan tidak boleh dicampuradukkan dalam narasi proposal.
- Apakah pemilik UMKM benar-benar menganggap rekomendasi aksi sebagai "actionable" (bukan generik) - ini PERSEPSI PENGGUNA yang hanya terjawab lewat usability test (bagian 23), bukan asumsi tim.
- Sebagian sumber akademik kunci (IndoBERT 97% akurasi, ABSA Random Forest F1 0,835) berstatus PARTIALLY VERIFIED atau NOT FULLY ACCESSIBLE - klaim akurasi tersebut BELUM dapat dipertanggungjawabkan penuh sampai tim membaca metodologi lengkapnya atau mereplikasi sendiri.

Yang REALISTIS dicapai riset tahap ini, dan yang sudah dicapai dossier versi v4: (1) tidak ada klaim tanpa sumber; (2) setiap asumsi ditandai eksplisit dan dapat dilacak ke bagian validasinya; (3) trade-off risiko (termasuk keputusan menunda computer vision) dijelaskan alasannya, bukan disembunyikan demi kesan "lengkap"; (4) arsitektur yang diusulkan proporsional terhadap bukti yang benar-benar ada, bukan dipilih karena terdengar canggih. Inilah definisi "10/10" yang jujur untuk sebuah dossier RISET tahap penyisihan: bukan dokumen tanpa celah, melainkan dokumen yang mengetahui persis di mana celahnya dan punya rencana konkret menutupnya (bagian 23-24) sebelum tim menulis satu baris kode produksi.

CATATAN v5: butir kedua pada daftar di atas (generalisasi CLIP pada foto konsumen) sekarang punya jalur validasi konkret - lihat bagian 21B.6. Ini TIDAK mengubah status butir tersebut dari "belum terbukti" menjadi "terbukti"; yang berubah hanyalah tim kini punya cara realistis untuk membuktikannya sebelum deadline, alih-alih tidak punya cara sama sekali.


### 21B.6 Rencana Akuisisi Data Visual: Apify dalam Anggaran Gratis $5/Bulan (Pembaruan v5)

Menjawab pertanyaan langsung tim: menggunakan Apify untuk mengumpulkan data tambahan (termasuk foto ulasan) dalam batas paket gratis $5/bulan DIPERBOLEHKAN dan MASUK AKAL sebagai pelengkap - bukan pengganti - dataset publik yang sudah menjadi fondasi utama (bagian 14). Berikut dasar kesimpulan ini, ditandai sesuai tingkat verifikasi.


#### 21B.6.1 Verifikasi Platform dan Kapabilitas Actor [VERIFIED, per Agustus 2026]

| Aspek | Keterangan |
| --- | --- |
| Model harga Apify Free plan | Kredit prabayar $5/bulan, TANPA kartu kredit, TIDAK terbawa (roll over) ke bulan berikutnya, platform otomatis menghentikan run baru saat kredit habis (tidak ada tagihan susulan/surprise billing) - cocok untuk anggaran riset kompetisi yang predictable. |
| Actor yang dikonfirmasi mengekstrak foto ulasan | "Shopee Product Reviews Scraper" (developer: zen-studio) - dikonfirmasi langsung dari dokumentasi resmi actor per Agustus 2026: field output "images" berisi URL CDN penuh untuk setiap foto yang dilampirkan pembeli pada ulasan, di samping teks, rating, sub-rating per aspek (kualitas produk/layanan penjual/pengiriman), varian yang dibeli, dan balasan penjual - total 27 field per ulasan. Mendukung filter contentFilter:"with media" untuk mengambil KHUSUS ulasan yang punya foto/video, sehingga anggaran tidak terbuang pada ulasan teks-saja. |
| Cakupan pasar | Mencakup seluruh 8 pasar Shopee termasuk Shopee Indonesia (shopee.co.id) - market terdeteksi otomatis dari URL produk. |
| Status actor Tokopedia untuk ekstraksi foto | BELUM SEPENUHNYA TERVERIFIKASI - beberapa actor Tokopedia ditemukan tersedia di Apify Store (mis. dari developer jupri, faz) dan mengekstrak teks ulasan/rating, namun dokumentasi yang diperiksa tidak secara eksplisit mengonfirmasi field foto seperti pada actor Shopee di atas [REQUIRES USER VALIDATION - perlu dicek langsung pada halaman Input/Output actor terkait sebelum dipakai, atau fokuskan akuisisi foto pada Shopee saja dan pakai dataset publik untuk porsi Tokopedia]. |


#### 21B.6.2 Matematika Biaya dan Volume dalam Anggaran Gratis [dihitung dari harga terverifikasi]

Actor Shopee Reviews menggunakan skema Pay Per Event: $3,99 per 1.000 ulasan pada paket Free (lebih murah lagi di paket berbayar, tapi tidak relevan karena tim tetap pada paket gratis). Dengan kredit $5/bulan dan filter contentFilter:"with media" (hanya ulasan bermedia yang ditagih), estimasi realistis:

| Skenario | Ulasan Bermedia Diambil | Estimasi Biaya | Sisa Kredit Bulanan |
| --- | --- | --- | --- |
| Validasi minimum (Langkah 4, bagian 21B.2) | ~250-300 ulasan berfoto dari 2-3 listing produk fesyen/F&B UMKM populer | ~$1,00-1,20 | Cukup untuk 1-2 kali pengulangan pengambilan sampel di bulan yang sama, atau disisakan untuk uji coba actor Tokopedia |
| Validasi diperluas (jika waktu memungkinkan) | ~500 ulasan berfoto dari 4-6 listing lintas kategori | ~$2,00 | Masih tersisa margin untuk eksperimen tambahan |
| Pemakaian penuh kredit | ~1.250 ulasan (campuran bermedia/tidak jika filter dilonggarkan) | ~$5,00 (kredit habis) | Tidak disarankan - lebih baik disisakan margin daripada run terhenti di tengah karena kredit habis |

Catatan penting: 250-300 foto ulasan riil jauh melampaui syarat minimum 20-30 foto pada Langkah 4 (bagian 21B.2) yang menjadi gerbang wajib sebelum tim boleh mengklaim hasil visual. Ini berarti anggaran gratis Apify BUKAN sekadar cukup, melainkan memberi margin untuk iterasi (mis. jika batch pertama ternyata bias pada satu kategori produk, tim masih punya kredit untuk mengambil batch kedua dari kategori lain di bulan yang sama).


#### 21B.6.3 Analisis Legal dan Kepatuhan ToS [PARTIALLY VERIFIED - lihat catatan]

Pencarian langsung terhadap teks resmi Terms of Service Shopee/Tokopedia yang secara eksplisit melarang scraping TIDAK menemukan kutipan pasal yang dapat diverifikasi dalam riset ini [NOT FULLY ACCESSIBLE - dokumen ToS lengkap tidak diindeks penuh di hasil pencarian]. Namun beberapa hal dapat disimpulkan dengan tingkat keyakinan wajar:

- Developer actor Shopee Reviews Scraper sendiri secara eksplisit mencantumkan disclaimer kepatuhan: actor ini "mengekstrak data ulasan yang secara publik terlihat" dan pengguna "bertanggung jawab mematuhi Terms of Service Shopee serta regulasi perlindungan data yang berlaku (PDPA se-Asia Tenggara, GDPR, CCPA, LGPD)" - ini adalah pola disclaimer standar industri scraping-as-a-service, BUKAN jaminan legalitas mutlak dari pihak platform Shopee/Tokopedia [INDUSTRY CLAIM dari penyedia actor, bukan konfirmasi resmi Shopee].
- Data yang diekstrak (foto, teks, nama akun tersamar, rating) adalah data yang SUDAH publik terlihat oleh siapa pun yang membuka halaman produk tanpa login - berbeda secara signifikan dari scraping data di balik login/pembayaran, yang secara umum dianggap area risiko lebih tinggi dalam preseden internasional terkait scraping data publik.
- Risiko yang tetap relevan dan wajib dimitigasi terlepas dari status hukum scraping itu sendiri: ulasan memuat DATA PRIBADI (nama pengguna, foto avatar, kadang ukuran tubuh untuk kategori fesyen) yang tunduk pada UU PDP (bagian 22.2) begitu data tersebut diproses tim - kewajiban anonimisasi (bagian 22.3) berlaku SAMA baik data berasal dari dataset publik Kaggle/HuggingFace maupun hasil scraping sendiri.
- Konteks penggunaan (riset/kompetisi non-komersial, volume kecil-terbatas ~250-500 baris untuk validasi, bukan scraping massal untuk dijual kembali) secara umum berada pada risiko yang jauh lebih rendah dibanding scraping skala industri/komersial, namun ini adalah PENILAIAN RISIKO KUALITATIF tim, bukan opini hukum - [REQUIRES USER VALIDATION jika tim ingin kepastian lebih tinggi: konsultasi singkat dengan mentor kompetisi atau pembacaan langsung pasal ToS Shopee sebelum menjalankan actor].

Kesimpulan bagian ini: menggunakan Apify dengan actor yang mengekstrak data publik, dalam volume kecil untuk keperluan validasi riset (bukan komersialisasi), DENGAN anonimisasi data pribadi sebelum diproses lebih lanjut, adalah pendekatan yang WAJAR dan PROPORSIONAL untuk konteks kompetisi tahap penyisihan. Ini bukan jaminan bebas risiko mutlak - klasifikasi "aman 100%" akan berlebihan mengingat ketiadaan konfirmasi tertulis langsung dari Shopee/Tokopedia - tetapi risiko residual sebanding dengan risiko yang sudah melekat pada penggunaan dataset scraping pihak ketiga mana pun yang beredar di Kaggle/HuggingFace (bagian 14), yang juga pada dasarnya berasal dari scraping oleh pihak lain.


#### 21B.6.4 Rekomendasi Alur Kerja Data Terintegrasi

| Aspek | Keterangan |
| --- | --- |
| Peran dataset publik (primer) | PRDECT-ID, e-commerce-sentiment-bahasa-indonesia, Tokopedia reviews 2019 (bagian 14) tetap menjadi KORPUS UTAMA untuk fine-tuning model teks - volume besar, sudah berlabel, tidak memerlukan biaya/waktu scraping tambahan. |
| Peran data Apify (validasi/kalibrasi) | Batch kecil (~250-300 ulasan berfoto) hasil scraping Shopee dipakai KHUSUS untuk validasi Langkah 4 (bagian 21B.2) dan kalibrasi ambang keyakinan model visual pada data dunia nyata - BUKAN untuk melatih ulang model teks dari nol. |
| Anonimisasi wajib sebelum dipakai | Hapus/mask nama akun, avatar, dan data pengukuran tubuh pada baris yang diproses sebelum dipakai di luar lingkup validasi internal tim - selaras kebijakan retensi data bagian 21B.4 dan mitigasi bagian 22.3. |
| Dokumentasi untuk juri | Cantumkan secara eksplisit pada proposal bahwa sebagian kecil data validasi diperoleh via scraping data publik menggunakan tool pihak ketiga (Apify), dengan tanggal pengambilan dan volume - transparansi ini justru memperkuat kredibilitas dibanding menyembunyikan sumber data. |


## 27. Complete Bibliography

Daftar berikut mencakup seluruh sumber yang dikutip pada dossier ini. Status verifikasi mengikuti definisi pada bagian 9.


### 27.1 Sumber Resmi Indonesia dan Laporan Industri

- BPS - Statistik E-Commerce 2024, https://www.bps.go.id/en/publication/2025/11/28/647323224ecc656c2933571b/statistik-e-commerce-2024.html [OFFICIAL STATISTICS]
- BPS - Statistik E-Commerce 2023, https://www.bps.go.id/id/publication/2025/01/30/d52af11843aee401403ecfa6/statistik-e-commerce-2023.html [OFFICIAL STATISTICS]
- Kementerian Perdagangan RI - Kinerja Perdagangan Melalui Sistem Elektronik (PMSE) 2025, https://bkperdag.kemendag.go.id/unduhan-file/a11ba920-123c-4a4f-856b-cdbb1f0f64c4 [OFFICIAL STATISTICS]
- Otoritas Jasa Keuangan - Survei Nasional Literasi dan Inklusi Keuangan (SNLIK) 2025, https://ojk.go.id/id/Fungsi-Utama/Perilaku-Pelaku-Usaha-Jasa-Keuangan/SNLIK/Pages/SNLIK-2025.aspx [OFFICIAL STATISTICS]
- OJK & BPS - Siaran Pers Bersama SNLIK 2024, https://ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/OJK-dan-BPS-Umumkan-Hasil-Survei-Nasional-Literasi-dan-Inklusi-Keuangan-Tahun-2024.aspx [OFFICIAL STATISTICS]
- Badan Perlindungan Konsumen Nasional - Statistik Pengaduan, https://bpkn.go.id/statistik_pengaduan [OFFICIAL STATISTICS]
- BPKN - Catatan Akhir Tahun 2024, https://www.bpkn.go.id/beritaterkini/detail/catatan-akhir-tahun-2024-evaluasi-dan-kinerja-bpkn-ri-dalam-pengembangan-perlindungan-konsumen [OFFICIAL STATISTICS]
- KPPU - Persaingan Usaha dan Regulasi Pasar Digital, https://www.liputan6.com/bisnis/read/7336375/kppu-desak-pembentukan-regulasi-pasar-digital [OFFICIAL STATEMENT via media]
- Google, Temasek, Bain - e-Conomy SEA 2025 Report (Indonesia), https://services.google.com/fh/files/misc/indonesia_e_conomy_sea_2025_report.pdf [INDUSTRY REPORT]
- Google Blog Indonesia - e-Conomy SEA 2025 Ringkasan, https://blog.google/intl/id-id/company-news/outreach-initiatives/e-conomy-sea-2025-ekonomi-digital-indonesia-mendekati-gmv-us100-miliar/ [INDUSTRY REPORT]
- Kompas.id - E-Commerce Tumbuh 86 Persen dalam Empat Tahun, https://data.kompas.id/data-detail/kompas_statistic/69369057c97bbc4e90c46b0c [INDUSTRY REPORT]
- Kompas.com - Biaya Membesar, Untung Menipis: Masih Layak UMKM Jualan di Marketplace?, https://money.kompas.com/read/2026/05/13/065500726/ [INDUSTRY CLAIM]
- PMC - Why are Indonesian consumers buying on live streaming platforms?, https://pmc.ncbi.nlm.nih.gov/articles/PMC11260974/ [VERIFIED - peer reviewed]


### 27.2 Jurnal dan Publikasi Akademik (lihat detail lengkap pada bagian 9)

- Choi et al. (2022). Fake review identification and utility evaluation model using machine learning. Frontiers in Artificial Intelligence. DOI: 10.3389/frai.2022.1064371 [VERIFIED]
- (2023). Trust in the chatbot: a semi-human relationship. Future Business Journal. DOI: 10.1186/s43093-023-00288-z [VERIFIED]
- (2025). Beyond Accessibility Compliance: Exploring the Role of Information on Apparel Shopping Websites for the Blind and Visually Impaired. Societies (MDPI), 15(4):90. DOI: 10.3390/soc15040090 [VERIFIED]
- (2024). Digital accessibility in the era of artificial intelligence - Bibliometric analysis and systematic review. Frontiers in Artificial Intelligence. DOI: 10.3389/frai.2024.1349668 [VERIFIED]
- (2025). Implementing AI Chatbots in Customer Service Optimization - A Case Study in Micro-Enterprise. MDPI Information, 16(12):1078. https://www.mdpi.com/2078-2489/16/12/1078 [PARTIALLY VERIFIED]
- (2024). Artificial intelligence and recommender systems in e-commerce: Trends and research agenda. ScienceDirect. pii S2667305324001091 [NOT FULLY ACCESSIBLE]
- (2023). Introducing CSP Dataset: A Dataset Optimized for the Study of the Cold Start Problem in Recommender Systems. MDPI Information, 14(1):19. https://www.mdpi.com/2078-2489/14/1/19 [PARTIALLY VERIFIED]
- User Cold Start Problem in Recommendation Systems: A Systematic Review. ResearchGate. https://www.researchgate.net/publication/376140792 [NOT FULLY ACCESSIBLE]
- Klasifikasi Sentimen Ulasan Produk pada Platform E-Commerce di Indonesia dengan Menggunakan Model Pre-Trained IndoBERT. Building of Informatics, Technology and Science (BITS). https://ejurnal.seminar-id.com/index.php/bits/article/view/6968 [PARTIALLY VERIFIED]
- Analisis Sentimen Ulasan Produk di E-Commerce Bukalapak Menggunakan Natural Language Processing. Prosiding SISFOTEK. https://seminar.iaii.or.id/index.php/SISFOTEK/article/view/406 [PARTIALLY VERIFIED]
- Analisis Sentimen untuk Ulasan Produk E-Commerce Shopee Menggunakan BERT. Jurnal Sifo Mikroskil. https://ejurnal.mikroskil.ac.id/index.php/jsm/article/view/1796 [PARTIALLY VERIFIED]
- Analisis Sentimen Berbasis Aspek dengan Pendekatan Machine Learning Menggunakan Dataset Bahasa Indonesia. Repository Skripsi UGM. https://etd.repository.ugm.ac.id/penelitian/detail/209326 [NOT FULLY ACCESSIBLE, karya skripsi]
- Leveraging IndoBERT and DistilBERT for Indonesian Emotion Classification in E-Commerce Reviews. arXiv:2509.14611 [PREPRINT]
- (2025). Artificial Intelligence Adoption in SMEs: Survey Based on TOE-DOI Framework. MDPI Applied Sciences, 15(12):6465. https://www.mdpi.com/2076-3417/15/12/6465 [PARTIALLY VERIFIED]
- (2025). SME-TEAM: leveraging trust and ethics for secure and responsible use of AI and LLMs in SMEs. npj Artificial Intelligence. https://www.nature.com/articles/s44387-025-00065-z [PARTIALLY VERIFIED]
- Faktor-Faktor yang Memengaruhi Niat Menggunakan Teknologi AI untuk Evaluasi Usaha pada Pelaku UMKM di DKI Jakarta. Ekopedia: Jurnal Ilmiah Ekonomi. https://indojurnal.com/index.php/ekopedia/article/view/4356 [PARTIALLY VERIFIED]
- Adopsi Artificial Intelligence pada UMKM: Tinjauan Sistematis. MDP Student Conference. https://jurnal.mdp.ac.id/index.php/msc/article/view/15392 [PARTIALLY VERIFIED]
- Deep neural network-based detection of counterfeit products from smartphone images. arXiv:2410.05969 [PREPRINT]
- Knowledge Discovery on E-Commerce Customer Churn Using Interpretable Machine Learning: A Comparative Study of SHAP-Based Classifiers. Journal of Applied Informatics and Computing. https://jurnal.polibatam.ac.id/index.php/JAIC/article/view/10811 [PARTIALLY VERIFIED]
- (2022). B2C E-Commerce Customer Churn Prediction Based on K-Means and SVM. Journal of Theoretical and Applied Electronic Commerce Research (MDPI), 17(2):24. https://www.mdpi.com/0718-1876/17/2/24 [PARTIALLY VERIFIED]


### 27.2A Teknologi Frontier (bagian 21A - Pembaruan v3)

- Cendol: Open Instruction-tuned Generative Large Language Models for Indonesian Languages. arXiv:2404.06138 [PREPRINT]
- Komodo: A Linguistic Expedition into Indonesia's Regional Languages. arXiv:2403.09362 [PREPRINT]
- Sailor: Open Language Models for South-East Asia. https://sea-sailor.github.io/blog/sailor1/ [INDUSTRY/RESEARCH]
- PA-CLIP: Enhancing Zero-Shot Anomaly Detection through Pseudo-Anomaly Awareness. arXiv:2503.01292 [PREPRINT]
- AFR-CLIP: Enhancing Zero-Shot Industrial Anomaly Detection with Stateless-to-Stateful Anomaly Feature Rectification. arXiv:2503.12910 [PREPRINT]
- GlobalCLIP: Zero-shot manufacturing anomaly detection with adaptive self-cyclic ensemble learning. ScienceDirect, pii S0957417425030647 [NOT FULLY ACCESSIBLE]
- BGE-M3 Embeddings: Unified Multilingual Retrieval. Ringkasan teknis pihak ketiga (emergentmind.com) atas model BAAI/bge-m3 [PARTIALLY VERIFIED]
- Culturally-Nuanced Story Generation for Reasoning in Low-Resource Languages: The Case of Javanese and Sundanese. arXiv:2502.12932 [PREPRINT]
- An LLM-Enabled Data Augmentation Framework for Low-Resource Scenarios. SpringerLink [PARTIALLY VERIFIED]
- Enhancing Low-Resource LLMs Classification with PEFT and Synthetic Data. arXiv:2404.02422 [PREPRINT]
- Better as Generators Than Classifiers: Leveraging LLMs and Synthetic Data for Low-Resource Multilingual Classification. arXiv:2601.16278 [PREPRINT]
- TECP: Token-Entropy Conformal Prediction for LLMs. arXiv:2509.00461 [PREPRINT]
- Beyond Surface Statistics: Robust Conformal Prediction for LLMs via Internal Representations. arXiv:2604.16217 [PREPRINT]
- Agentic Commerce Trends and Statistics for 2026. MetaRouter Blog [INDUSTRY REPORT]
- 7 AI Trends Shaping Agentic Commerce in 2026. commercetools Blog [INDUSTRY REPORT]


### 27.3 Dataset dan Repository

- Tokopedia Product Reviews 2019. Hugging Face. https://huggingface.co/datasets/farhamu/tokopedia-product-reviews-2019
- E-Commerce Sentiment Bahasa Indonesia. Hugging Face. https://huggingface.co/datasets/joyadriansyah/e-commerce-sentiment-bahasa-indonesia
- PRDECT-ID: Indonesian Emotion Classification. Kaggle. https://www.kaggle.com/datasets/jocelyndumlao/prdect-id-indonesian-emotion-classification
- Indonesian Marketplace Product Reviews. Kaggle. https://www.kaggle.com/datasets/taqiyyaghazi/indonesian-marketplace-product-reviews
- E-Commerce Ratings and Reviews in Bahasa Indonesia. Kaggle. https://www.kaggle.com/datasets/satyaahb/ecommerce-ratings-and-reviews-in-bahasa-indonesia
- Indonesia E-Commerce Sales & Shipping 2023-2025. Kaggle. https://www.kaggle.com/datasets/bakitacos/indonesia-e-commerce-sales-and-shipping-20232025


## 28. Appendix: Literature Matrix

| Citation | Research Objective | Context | Dataset | Method | Metric | Result (Ringkas) | Limitation | Relevance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Choi et al. 2022, Frontiers AI, DOI 10.3389/frai.2022.1064371 | Deteksi & evaluasi utilitas ulasan palsu | Global | Ulasan e-commerce | ML (fitur teks+perilaku) | Precision/Recall/F1 | ML efektif deteksi ulasan palsu | Generalisasi ke Bahasa Indonesia belum diuji | Ide UlasanAsli, masalah 6.2 |
| 2023, Future Business Journal, DOI 10.1186/s43093-023-00288-z | Trust pengguna pada chatbot | Umum | Survei pengguna | Analisis dimensi trust | Skala survei | Trust kognitif & emosional keduanya signifikan | Tidak spesifik UMKM/Indonesia | Ide BalasCepat, masalah 6.3 |
| 2025, MDPI Information 16(12):1078 | Optimasi CS via chatbot AI | Usaha mikro (studi kasus) | Studi kasus | Case study | Kepuasan, waktu respons | Model hybrid AI+manusia direkomendasikan | Studi kasus tunggal | Ide BalasCepat, masalah 6.3/6.5 |
| 2024, ScienceDirect pii S2667305324001091 | Tren riset AI rekomendasi e-commerce | Global | Tinjauan pustaka | Literature review | N/A | Tren menuju personalisasi & explainability | Bersifat tinjauan | Ide RekomenUMKM, masalah 6.6/6.7 |
| 2023, MDPI Information 14(1):19 | Dataset khusus evaluasi cold-start | Global | Dataset terstruktur | Desain dataset | Hit-rate@K (potensial) | Mempermudah evaluasi cold-start terkontrol | Tidak spesifik Indonesia | Ide RekomenUMKM, masalah 6.6 |
| BITS Journal, IndoBERT sentiment | Klasifikasi sentimen ulasan Indonesia | Indonesia | Ulasan e-commerce | IndoBERT vs LSTM | Akurasi | Akurasi hingga 97% (IndoBERT) | Jurnal non-Scopus, sampel belum ditelaah | Ide InsightUlasan, masalah 6.12 |
| Prosiding SISFOTEK, Bukalapak NLP | Analisis sentimen ulasan Bukalapak | Indonesia | Ulasan Bukalapak | NLP umum | Tidak disebutkan rinci | Mengisi gap analisis platform lokal | Prosiding nasional, metodologi ringkas | Ide InsightUlasan, masalah 6.12 |
| Jurnal Sifo Mikroskil, Shopee BERT | Klasifikasi sentimen ulasan Shopee | Indonesia | Ulasan Shopee | BERT | Akurasi | Akurasi 83,08% | Akurasi lebih rendah dari klaim studi lain | Ide InsightUlasan, masalah 6.12 |
| UGM Repository, ABSA Random Forest | Aspect-based sentiment analysis | Indonesia | Dataset Bahasa Indonesia | Random Forest | F1-score | F1 0,835 | Karya skripsi, bukan jurnal | Ide InsightUlasan, masalah 6.12 |
| arXiv:2509.14611 | Klasifikasi emosi ulasan e-commerce | Indonesia | Ulasan e-commerce | IndoBERT & DistilBERT | Tidak disebutkan rinci | Model transformer lokal dapat diadaptasi untuk emosi | Preprint, belum peer-review | Ide InsightUlasan, masalah 6.12 |
| PMC11260974 | Perilaku beli live streaming Indonesia | Indonesia | Survei konsumen | Perceived value theory | Skala Likert/SEM | Nilai dirasakan mendorong keputusan beli | Fokus konsumen, bukan solusi AI penjual | Masalah 6.5 |
| 2025, MDPI Applied Sciences 15(12):6465 | Adopsi AI pada SME | Umum | Survei SME | Kerangka TOE-DOI | Skor adopsi | Kesiapan tech-org-env determinan utama | Tidak spesifik Indonesia | Latar belakang seluruh ide |
| 2025, npj AI, s44387-025-00065-z | Kerangka trust & etika AI/LLM pada SME | Umum | Kerangka konseptual | Framework paper | N/A | Trust & etika fondasi kritikal adopsi | Bukan studi empiris | Bagian 22, seluruh ide |
| Ekopedia Jurnal Ilmiah Ekonomi | Niat penggunaan AI evaluasi usaha UMKM | Indonesia (DKI Jakarta) | Survei UMKM | Task-Technology Fit | Skor intention-to-use | Kesesuaian tugas-teknologi determinan utama | Cakupan geografis terbatas | Bagian 7.2, seluruh ide |
| arXiv:2410.05969 | Deteksi produk tiruan dari citra | Global | Citra produk smartphone | Deep neural network | Akurasi klasifikasi | Deteksi tiruan menjanjikan | Preprint, dataset non-Indonesia | Ide DeteksiTiru (dieliminasi), masalah 6.8 |
| Journal of Applied Informatics and Computing (Polibatam) | Interpretable ML untuk churn e-commerce | Tidak spesifik | Data e-commerce | SHAP-based classifiers | Interpretasi fitur | Interpretability tingkatkan transparansi prediksi churn | Detail dataset perlu ditelaah | Ide PrediksiPergi, masalah 6.9 |
| 2022, MDPI JTAER 17(2):24 | Prediksi churn B2C e-commerce | Tidak spesifik | Data pelanggan B2C | K-Means + SVM | Akurasi | Kombinasi clustering+klasifikasi tingkatkan akurasi | Tidak spesifik UMKM data-scarce | Ide PrediksiPergi, masalah 6.9 |


## 29. Appendix: Dataset Matrix

Lihat tabel lengkap pada bagian 14.1. Ringkasan prioritas untuk ide InsightUlasan (rekomendasi utama):

| Dataset | Suitability Score (1-10) | Catatan Prioritas |
| --- | --- | --- |
| e-commerce-sentiment-bahasa-indonesia (Hugging Face) | 8 | Sudah berlabel sentimen, ukuran memadai (21.840), Bahasa Indonesia eksplisit termasuk sarkasme/ironi |
| PRDECT-ID (Kaggle) | 8 | Label emosi granular, relevan untuk memperkaya InsightUlasan melampaui sentimen biner |
| Tokopedia Product Reviews 2019 (Hugging Face) | 7 | Volume besar (40.607) namun data 2019, perlu dicek relevansi bahasa/tren terkini |
| Indonesian Marketplace Product Reviews (Kaggle) | 6 | Anotasi manual namun skala lebih kecil, baik untuk validasi silang |
| Data ulasan/chat UMKM mitra (perlu dikumpulkan) | 9 (jika berhasil didapat) | Prioritas TERTINGGI untuk validasi generalisasi model ke konteks riil - REQUIRES USER VALIDATION |


## 30. Appendix: Competitor Matrix

Lihat tabel lengkap pada bagian 11. Ringkasan gap kompetitif untuk InsightUlasan:

| Kompetitor Terdekat | Klasifikasi | Gap yang Dieksploitasi InsightUlasan |
| --- | --- | --- |
| Dashboard rating marketplace (Shopee/Tokopedia) | Adjacent | Tidak mengekstraksi aspek spesifik atau memberi rekomendasi aksi terprioritas - hanya skor rata-rata mentah |
| Tools sentiment analysis SaaS internasional | Substitute (mahal, tidak lokal) | Tidak dioptimalkan Bahasa Indonesia informal dan harga tidak terjangkau UMKM mikro |
| Riset akademik IndoBERT/ABSA Bahasa Indonesia | Research prototype | Berhenti pada klasifikasi, belum menjembatani ke output keputusan bisnis siap pakai - inilah gap yang diisi InsightUlasan |


## RESEARCH CONFIDENCE AND EVIDENCE GAPS

Bagian penutup ini merangkum tingkat keyakinan atas seluruh temuan dossier, sesuai permintaan eksplisit untuk transparansi penuh sebelum ide dieksekusi ke tahap MVP.


### Kesimpulan dengan Tingkat Keyakinan Tinggi

- Populasi UMKM Indonesia sangat besar (~66 juta unit usaha) dan menyumbang mayoritas PDB serta tenaga kerja - didukung data resmi Kemenkop UKM yang konsisten dengan sumber lain.
- Jumlah unit usaha e-commerce Indonesia tumbuh signifikan (4,40 juta unit pada 2024) - data resmi BPS.
- Struktur ulasan e-commerce Bahasa Indonesia dapat diklasifikasikan dengan model pre-trained (IndoBERT/BERT) dengan performa yang jauh lebih baik dari pendekatan sederhana - dikonfirmasi oleh beberapa studi independen meski angka akurasi bervariasi.
- Terdapat gap metodologis nyata antara penelitian sentimen (berhenti di klasifikasi) dan kebutuhan bisnis UMKM (butuh rekomendasi aksi) - konsisten di seluruh tinjauan literatur pada bagian 9.4/10.4.
- Biaya platform marketplace berlapis adalah tekanan nyata bagi margin UMKM - didukung berbagai sumber independen (BPS, laporan industri, keluhan media).


### Kesimpulan dengan Tingkat Keyakinan Sedang

- Estimasi persentase UMKM yang "aktif memanfaatkan platform digital" (~30%) - berasal dari gabungan sumber yang belum sepenuhnya konsisten metodologinya.
- Klaim spesifik "konversi live streaming 3x lebih tinggi" dan sejenisnya - bersifat klaim industri tanpa metodologi terverifikasi penuh.
- Efektivitas riil InsightUlasan dalam mengubah perilaku bisnis UMKM (bukan hanya akurasi klasifikasi teknis) - belum divalidasi melalui uji pengguna nyata.
- Tingkat kesediaan UMKM Indonesia berbagi data ulasan/chat untuk keperluan riset/MVP - berdasarkan inferensi dari literatur adopsi AI umum, belum wawancara langsung.


### Kesimpulan yang Masih Spekulatif

- Dampak ekonomi kuantitatif InsightUlasan (mis. "meningkatkan retensi X%") - belum ada data baseline maupun eksperimen yang mendukung angka spesifik apa pun; SELURUH klaim dampak ekonomi pada dossier ini bersifat hipotesis/proxy, bukan hasil terukur.
- Perbandingan posisi kompetitif InsightUlasan terhadap kemungkinan produk internal yang sedang dikembangkan marketplace besar namun belum dipublikasikan (tidak dapat diverifikasi dari riset publik).
- Generalisasi akurasi model dari dataset publik ke data riil UMKM mikro spesifik - dataset publik sebagian besar berasal dari platform besar (Tokopedia, Shopee, Bukalapak), belum tentu representatif UMKM sangat mikro dengan volume ulasan rendah.


### Data yang Belum Ditemukan

- Data granular BPS/Kemenkop tentang persentase UMKM yang menggunakan alat analitik/AI secara spesifik (bukan sekadar QRIS/marketplace dasar).
- Dataset publik berlabel "ulasan palsu/asli" Bahasa Indonesia (relevan untuk ide UlasanAsli yang tidak terpilih sebagai rekomendasi utama justru karena gap ini).
- Data resmi prevalensi listing kloning/produk tiruan yang menargetkan UMKM Indonesia secara spesifik.
- Statistik resmi granular tentang konsumen lansia/disabilitas dan perilaku transaksi digital mereka di Indonesia.


### Jurnal yang Masih Perlu Diakses (Full Text)

- Artikel-artikel dengan status NOT FULLY ACCESSIBLE pada bagian 9 dan 27.2, khususnya dua artikel ScienceDirect tentang fake review detection dan recommender systems trends (pii S0148296322010967, S0148296323005027, S2667305324001091) yang hanya dapat ditelaah dari abstrak/ringkasan publik.
- Artikel BITS Journal (IndoBERT 97% akurasi) dan skripsi UGM (ABSA Random Forest) - kedua sumber paling sentral bagi ide utama InsightUlasan, namun metodologi lengkap (ukuran sampel, validasi silang, detail preprocessing) belum ditelaah dari dokumen asli utuh.


### Asumsi yang Harus Divalidasi Melalui Wawancara

- Kesediaan UMKM riil membagikan data ulasan/chat untuk keperluan pengembangan (bagian 21, 23).
- Volume ulasan/chat riil yang dimiliki UMKM mikro per bulan (menentukan apakah masalah cukup besar untuk dirasakan setiap toko target).
- Apakah pemilik UMKM benar-benar menganggap rekomendasi aksi model sebagai "actionable" dan bukan restatement generik dari ulasan.
- Tingkat kepercayaan awal UMKM terhadap rekomendasi berbasis AI, dan apakah desain transparansi (kutipan asli) cukup untuk membangun trust sesuai temuan literatur (bagian 12).


### Risiko Terbesar dalam Memilih Ide Utama

Risiko terbesar bagi InsightUlasan adalah KETERGANTUNGAN PADA GENERALISASI MODEL dari dataset publik (yang sebagian besar berasal dari platform/toko besar) ke konteks riil UMKM sangat mikro dengan bahasa paling informal dan volume data paling terbatas - populasi yang secara spesifik menjadi target dampak sosial dossier ini namun justru paling kurang terwakili dalam dataset training yang tersedia. Apabila validasi pada bagian 23 menunjukkan gap generalisasi yang signifikan, tim perlu bersiap dengan rencana mitigasi berupa augmentasi data dan/atau penyesuaian ekspektasi cakupan target pengguna pada proposal final, alih-alih memaksakan klaim performa yang belum benar-benar teruji pada populasi yang dituju.

