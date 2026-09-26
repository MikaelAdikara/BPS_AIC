# UI refresh + vision — design (2026-09-26)

Disetujui user di sesi 2026-09-26. Tiga batch, dikerjakan paralel dengan kepemilikan file terpisah.

## Keputusan user
- Issue map: 3D sungguhan (WebGL, `react-force-graph-3d`), fallback 2D SVG yang sekarang.
- Vision: tampilkan gambar produk, cek foto pembeli (LLM vision OpenAI), OCR gambar produk (utama + galeri bila tersedia).
- "Compare with a general chatbot": dipindah ke paling bawah halaman produk, dilipat.
- "One fix, several listings?": ditulis ulang jadi "Masalah yang berulang di banyak produk".
- Filter tanggal: date picker (dari–sampai) + preset 7/30/90/Semua; rentang aktif selalu tertulis sebagai tanggal.

## Batch A — rapikan UI (Overview, Alerts, Sources)
- **Alerts timeline** (`screens/AlertsScreen.tsx`): tiap event = satu kartu menempel ke garis; ikon di atas garis.
  Baris 1 chip jenis + status, jam kanan. Baris 2 ringkasan pesan (clamp 2 baris). "Lihat pesan lengkap"
  di dalam kartu yang sama. "Delivery attempts" hanya jika >1 atau gagal.
- **Masalah berulang** (`OverviewInsights.tsx` candidate cards): per pola "Atribut · N produk · M ulasan",
  kalimat penjelas (kemungkinan penyebab di gudang/packing/foto, cek sebelum edit satu per satu),
  daftar produk dilipat (thumbnail bila ada `image_url`, jumlah ulasan), tautan ke issue.
  Kartu same-product lintas channel juga diberi judul/penjelas yang jelas.
- **Rentang tanggal**: komponen `DateRangeControl` (preset + kalender popover `react-day-picker`).
  API `GET /deciqo/overview` menerima `start`,`end` (YYYY-MM-DD, inklusif) selain `days` lama; periode
  pembanding = panjang sama tepat sebelum `start`. "All" = dari review tertua. Payload mengembalikan
  `range: {start, end, days}`. Star mix: toggle "Sepanjang waktu" / "<label tanggal>". Kandidat berulang
  dihitung dari temuan yang punya bukti dalam rentang (bila memungkinkan; kalau tidak, tetap semua dan
  label menjelaskannya).
- **Data sources**: kartu channel tinggi & grid seragam, angka sejajar, badge sampling + synced di footer,
  semua card di bawahnya lebar konten sama dan jarak konsisten.

## Batch B — halaman produk + gambar
Urutan baru `screens/ProductScreen.tsx`:
1. Header ringkas: gambar produk (fallback ikon), judul clamp 2 baris (bukan judul serif raksasa), channel,
   rating, n ulasan · n dengan foto, "Buka listing".
2. Kartu "Yang perlu kamu lakukan": temuan diurutkan dampak; tiap baris = masalah, pembeli terdampak,
   satu aksi (Isi fakta / Salin draf / Teruskan ke QC / Tinjau). Klik → membuka kartu temuan itu.
3. Kartu temuan (5 langkah dipadatkan): kutipan + foto pembeli berdampingan dengan badge vision
   (Foto mendukung / Tidak jelas / Tidak mendukung); fakta + draf satu alur; riwayat & bukti disisihkan dilipat.
4. "Detail investigasi" (dilipat): teks listing (edit + simpan), pipeline, re-run, cakupan OCR.
5. "Bandingkan dengan chatbot umum" (dilipat, paling bawah).
Products table: thumbnail di kolom produk.

## Batch C — vision + Issue map 3D
- Modul baru `apps/api/app/deciqo/engine/vision.py`, memakai `llm.py` (ledger, budget, purpose `vision`).
  - **Cek foto pembeli**: hanya foto dari ulasan bukti temuan dengan rating ≤3, maks 3 foto/temuan,
    maks N temuan/produk per run. Pertanyaan spesifik ke atribut temuan. Output strict JSON
    `{verdict: supports|contradicts|inconclusive, reason}`. Cache tabel `vision_checks`
    (key: image_url + finding attribute + prompt version). Vision hanya menambah bukti; tidak membuat,
    menghapus, atau mengubah bucket temuan.
  - **OCR gambar produk**: gambar utama (+ galeri `images_json` produk bila ada) → teks; disimpan
    `product_images_ocr` / kolom; ikut ke `listing_parts` sebagai "teks gambar" sehingga
    `coverage.images_read/images_total` nyata.
  - Tanpa OPENAI key / budget habis: dilewati, status `skipped` dengan alasan; UI menyebutnya.
- Apify: simpan galeri produk bila actor mengembalikan field gambar tambahan.
- Issue map 3D: `IssueMap3D` lazy-loaded, dipakai bila WebGL ada, bukan mobile (<768px), dan bukan
  `prefers-reduced-motion`; selain itu `IssueMap` 2D. Kalimat panduan, klik hub = kamera fokus + panel,
  hover tooltip, auto-rotate pelan saat idle, panel samping lebar tetap dan scroll sendiri.
- Dokumen: MODEL_CARD/LIMITATIONS diperbarui — CLIP tetap NO-GO; vision via LLM dengan abstain.

## Kontrak data (C menyediakan, B memakai)
- `finding` (full view) → tiap item `evidence[]` mendapat `images: string[]` (URL foto ulasan itu) dan
  `vision: {verdict, reason, model, checked_at} | null` (null = belum diperiksa).
- `finding.vision_summary: {checked, supports, contradicts, inconclusive, skipped_reason?} | null`.
- `product.image_url` (sudah ada), `product.images: string[]` (utama + galeri),
  `product.image_ocr: {status: done|skipped|pending, images_read, images_total, reason?}`.
- Endpoint baru `POST /deciqo/products/{id}/vision` menjalankan cek foto + OCR untuk produk itu
  (juga dijalankan otomatis di akhir analyse bila LLM terkonfigurasi).

## i18n
Semua string baru EN + ID di `apps/web/src/lib/messages-*.js`. Batch C memakai namespace baru `map3d`
untuk string peta 3D agar tidak bentrok dengan Batch A di `messages-insights.js`.

## Verifikasi
`npm run typecheck`, `npm test`, `npm run build` (apps/web); pytest unit untuk backend yang diubah;
cek visual di dev server (5180 → API 8000) desktop + mobile + dark.
