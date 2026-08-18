# Prompt Eksekusi untuk Claude Code - InsightUlasan (AIC COMPFEST 18)

Salin seluruh isi di bawah ini sebagai pesan pertama ke Claude Code, dijalankan di root folder repository yang baru diinisialisasi. Pastikan `INSIGHTULASAN_BLUEPRINT.md` dan `AIC_RESEARCH_DOSSIER.md` sudah disalin ke root repo sebelum memulai (lihat catatan di bagian paling bawah file ini).

---

## PROMPT (mulai dari sini)

Kamu akan membangun **InsightUlasan**, sistem AI untuk kompetisi AI Innovation Challenge (AIC) COMPFEST 18, subtema Smart Commerce. Ini bukan proyek dari nol - seluruh riset dan desain sistem SUDAH selesai dan dituangkan dalam dua dokumen yang ada di root repo ini:

- `INSIGHTULASAN_BLUEPRINT.md` - blueprint sistem dan produk lengkap (50 bagian: arsitektur AI, data contract, API contract, struktur repo, roadmap, dst). **Ini adalah sumber kebenaran utama untuk SEMUA keputusan implementasi.**
- `AIC_RESEARCH_DOSSIER.md` - dasar riset (masalah, evidence, dataset, kompetitor, keputusan arsitektur v1-v6). Rujuk ini kalau butuh alasan "kenapa" di balik keputusan yang ada di blueprint.

**Baca kedua file itu penuh sebelum menulis kode apa pun.** Jangan mendesain ulang fondasi produk - fondasinya sudah dikunci. Tugasmu adalah mengeksekusi, bukan meninjau ulang arsitektur, kecuali kamu menemukan blocker teknis nyata (jelaskan blocker-nya dan tanya sebelum menyimpang dari blueprint).

### Batasan Non-Negotiable (jangan dilanggar tanpa konfirmasi eksplisit)

1. **Tidak ada dependency cloud/API berbayar sebagai inti sistem.** Seluruh model (teks, visual, embedding, orchestrator) harus berjalan lokal, CPU-friendly, offline setelah build. Ini bukan preferensi gaya - ini syarat kelulusan rulebook (reproducibility lokal juri).
2. **Foto ulasan tetap OPSIONAL per entri.** Sistem harus tetap berjalan penuh tanpa foto (graceful degradation ke jalur teks-saja).
3. **Model visual WAJIB abstain saat confidence rendah** - jangan pernah memaksakan label. Pesan abstain: "Tidak dapat menyimpulkan kondisi produk dari foto ini."
4. **LLM/foundation model TIDAK PERNAH menghitung angka sendiri.** Semua angka (frekuensi, persentase, skor prioritas) dihitung tool deterministic (bagian 27.3 blueprint). LLM hanya menyusun narasi dan menjawab Q&A berbasis evidence yang diberikan.
5. **Tidak ada eksekusi tindakan bisnis otomatis.** Setiap Action Card wajib tombol accept/reject/save - tidak pernah mengubah harga/stok/promosi sendiri.
6. **Sistem tidak boleh gagal total kalau LLM orchestrator gagal dimuat.** WAJIB ada FALLBACK MODE (template deterministic) - lihat ADR-014 di blueprint bagian 46.
7. **Satu alur input → satu output AI terpadu, sinkron.** Tidak ada background job, distributed database, auto-tuning, atau multi-halaman dashboard kompleks pada Tier 1. Lihat blueprint bagian 4.5 "What We Will Not Build for Preliminary MVP" - daftar itu mengikat.
8. **Docker compose maksimal 3 service** (frontend, api, vector-store opsional). Jangan menambah service tanpa alasan kuat.
9. **Jangan mengklaim performa yang belum diuji.** Kalau kamu menulis README/dokumentasi/komentar kode yang menyebut angka akurasi, hasil harus benar-benar berasal dari evaluasi yang sudah dijalankan (bagian 33 blueprint), bukan target/asumsi.
10. **Conventional Commits wajib** (feat:/fix:/refactor:/docs:/test:) - ini syarat rulebook, bukan preferensi gaya.

### Stack yang Sudah Diputuskan (jangan diganti tanpa alasan kuat - lihat ADR di bagian 46 blueprint)

- Backend: **FastAPI** (Python), satu service, service layer modular secara kode
- Frontend: **React + Vite** untuk MVP kompetisi (Streamlit boleh dipakai HANYA untuk eksperimen validasi model di Tier 0, bukan untuk produk final)
- Model teks: **fine-tuned IndoBERT-base**, fallback TF-IDF + Logistic Regression
- Model visual: **CLIP ViT-B/32** zero-shot (frozen, tidak dilatih dari nol), fallback SigLIP
- Embedding/retrieval: **BGE-M3**, fallback Multilingual E5-base
- Vector store: **Chroma** (embedded)
- Foundation model orchestrator: **SEA-LION** (quantized), fallback Sailor2 atau FALLBACK MODE deterministic
- Struktur repo: ikuti persis bagian 31 blueprint (`apps/web`, `apps/api`, `ml/`, `data/`, `configs/`, `docs/`, `scripts/`, `tests/`, `docker/`)

### Urutan Kerja (ikuti Fase 0–10, bagian 38 blueprint)

Jangan lompat fase. Setiap fase punya *acceptance criterion* dan *go/no-go gate* sendiri di tabel bagian 38.1 - cek itu sebelum lanjut ke fase berikutnya.

1. **Fase 0 - Scope freeze:** Konfirmasi ulang ke saya taxonomy aspek final (bagian 18.2) dan kelas visual final (bagian 19.1) sebelum mulai coding - ini sudah didesain di blueprint, tugasmu hanya konfirmasi tidak ada perubahan.
2. **Fase 1 - Data & baseline:** Setup `scripts/download_datasets.py` untuk PRDECT-ID, e-commerce-sentiment-bahasa-indonesia, Tokopedia reviews (bagian 26.1). Bangun baseline TF-IDF + Logistic Regression dulu SEBELUM fine-tuning - ini wajib sebagai pembanding (bagian 34).
3. **Fase 2 - Text model:** Fine-tuning IndoBERT sesuai pipeline bagian 26.1. Jangan klaim hasil sebelum evaluasi (bagian 33.1) selesai.
4. **Fase 3 - Visual model:** Jalankan eksperimen zero-shot CLIP sesuai bagian 26.2. Di akhir fase ini, **ambil keputusan go/no-go eksplisit** (bagian 19.3, 22) berdasarkan selective accuracy dan coverage aktual - laporkan ke saya sebelum lanjut integrasi.
5. **Fase 4 - Retrieval & action engine:** Implementasikan RET-01 dan ACT-01. Priority score formula di bagian 22.2 SUDAH dikaji ulang (bukan formula naif) - ikuti versi final, jangan pakai formula perkalian mentah dari draf awal.
6. **Fase 5 - Backend:** Implementasikan seluruh endpoint (bagian 28) dan 10 tool contracts (bagian 27.3) persis sesuai schema JSON di bagian 25.
7. **Fase 6 - Frontend:** 4 screen sesuai wireframe tekstual bagian 14 - jangan menambah screen di luar itu untuk Tier 1.
8. **Fase 7 - Integration:** Sambungkan semua, uji seluruh sequence diagram di bagian 7.5–7.9 (termasuk failure/fallback flow).
9. **Fase 8 - Evaluation:** Jalankan evaluasi penuh (bagian 33), catat hasil apa adanya di `docs/MODEL_CARD.md`.
10. **Fase 9 - Docker & reproducibility:** WAJIB test dari fresh clone tanpa cache lokal (bagian 32) sebelum lanjut - kalau gagal, ini prioritas mutlak di atas fitur apa pun.
11. **Fase 10 - Dokumentasi:** README, MODEL_CARD.md, DATASET_CARD.md, ARCHITECTURE.md, LIMITATIONS.md, RESPONSIBLE_AI.md - semua sudah ada strukturnya di bagian 31.1 blueprint.

### Cara Kerja yang Diharapkan

- **Kerjakan satu fase penuh sebelum mulai fase berikutnya**, dan laporkan ringkas apa yang selesai + apa yang perlu keputusan saya (terutama gate Fase 3 dan Fase 9).
- **Kalau kamu mau menyimpang dari blueprint** (ganti library, ubah schema, skip suatu fitur P0) - **berhenti dan tanya dulu**, jangan asumsikan dan lanjut. Blueprint sudah melalui proses kajian ulang berkali-kali (lihat ADR di bagian 46), jadi kalau ada yang terlihat "kurang optimal", kemungkinan besar itu trade-off yang sudah disadari - cek dulu apakah sudah dijelaskan di sana sebelum mengubahnya.
- **Fitur P0 vs P1 vs Tier 2/3 sudah dipetakan** di bagian 8–12 blueprint dengan ID (ING-xx, NLP-xx, VIS-xx, RET-xx, ACT-xx, dst). Kerjakan HANYA P0 dulu sampai stabil sebelum menyentuh P1.
- **Jangan menulis proposal, pitch deck, atau script video** - itu di luar scope kerja ini, murni implementasi teknis.
- Referensi silang bagian blueprint pakai nomor bagian (mis. "bagian 22.2") supaya kita bisa saling merujuk cepat tanpa ambiguitas.

### Mulai Dari Sini

Langkah pertama: baca `INSIGHTULASAN_BLUEPRINT.md` bagian 31 (Repository Structure) dan `AIC_RESEARCH_DOSSIER.md` sekilas untuk konteks, lalu inisialisasi struktur folder repo kosong sesuai bagian 31 (folder + file placeholder + `.gitignore` + `.env.example` + `README.md` awal) sebagai commit pertama (`feat: initialize repository structure per blueprint section 31`). Setelah itu, laporkan ke saya dan mulai Fase 0.

---

## Catatan Persiapan (untuk kamu, bukan bagian prompt di atas)

1. Pindahkan dua file berikut ke root folder repository baru sebelum menjalankan Claude Code:
   - `INSIGHTULASAN_BLUEPRINT.md`
   - `AIC_RESEARCH_DOSSIER.md`
2. Kedua file ini adalah hasil konversi markdown dari dokumen Word yang sudah kamu terima sebelumnya - isinya identik, hanya format berbeda (markdown jauh lebih mudah dibaca Claude Code dibanding .docx).
3. Kalau kamu memakai Claude Code lewat terminal: `cd` ke folder repo, lalu jalankan `claude`, lalu tempel prompt di atas (bagian "PROMPT (mulai dari sini)" sampai "Mulai Dari Sini") sebagai pesan pertama.
4. Kalau tim berubah pikiran soal satu keputusan (mis. ganti FastAPI ke Flask), edit dulu bagian relevan di `INSIGHTULASAN_BLUEPRINT.md` SEBELUM menyuruh Claude Code kerja - supaya dokumen tetap jadi satu sumber kebenaran yang konsisten, bukan bercabang antara apa yang didokumentasikan dan apa yang benar-benar dikerjakan.
