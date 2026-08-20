# apps/web - Frontend React + Vite

Referensi: blueprint bagian 14 (wireframe per screen), 29 (arsitektur frontend), ADR-009,
`docs/BRAND_GUIDELINES.md`.

## Dua permukaan, bukan satu alur

Halaman pemasaran dan fitur analisis dipisahkan menjadi dua alamat. Sebelumnya keduanya satu
halaman: panel unggah duduk di bawah hero, dan tombol "Mulai" hanya menggulir ke sana.

Pemisahan ini bukan soal rapi. Halaman pemasaran perlu panjang dan bersuara - hero besar,
kartu mengambang, blok CTA gelap - sementara layar kerja perlu pendek dan diam. Menyatukannya
memaksa kompromi yang merugikan keduanya, dan membuat pengguna yang kembali harus menggulir
melewati materi promosi setiap kali ingin menganalisis data.

| Alamat | Permukaan | Isi |
| --- | --- | --- |
| `#/` | Landing | Hero, pita marketplace, cara kerja, fitur, CTA penutup |
| `#/analisis` | Dashboard | Unggah → Proses → Hasil (4 tab) |

Rute memakai **hash**, tanpa library router. Alasannya operasional: berkas statis yang sama
melayani kedua alamat, sehingga tidak ada aturan fallback yang perlu ditambahkan di nginx
maupun `vite preview`. Tombol Back dan muat-ulang tetap bekerja seperti yang diharapkan.

## Alur dashboard

Tiga fase berurutan. Navigasi tab baru muncul pada fase terakhir - sebelum ada hasil, tidak
ada apa pun untuk dijelajahi.

```
Unggah ──► Proses ──► Hasil ──┬── Hasil        rekomendasi + skor kualitas + benchmark
                              ├── Detail       peluang + temuan foto + sebaran aspek
                              ├── Tanya Jawab  percakapan ber-sitasi
                              └── Roadmap      yang belum ada, beserta alasannya
```

Fase disimpan sebagai state, bukan rute tersendiri: muat-ulang di tengah analisis tidak dapat
melanjutkan pekerjaan yang sedang berjalan, jadi alamat yang menjanjikan sebaliknya akan
menyesatkan.

## Tiga cara memasukkan ulasan

| Tab | Jalur | Catatan |
| --- | --- | --- |
| Tempel teks | Satu baris = satu ulasan | Tidak perlu berkas apa pun |
| Unggah berkas | CSV/JSON + pemetaan kolom | Tebakan kolom otomatis, dapat diubah |
| Tangkapan layar | OCR di backend (`POST /api/v1/ocr`) | Hasilnya **draf** yang wajib diperiksa |

Hasil OCR tidak pernah langsung dianalisis. Pembacaan teks dari gambar tidak pernah sempurna,
dan satu huruf yang salah baca merambat ke seluruh hasil - aspek salah dikenali, kutipan bukti
berbunyi janggal. Pemilik toko adalah satu-satunya yang tahu bunyi ulasan aslinya, jadi ia
menyunting lebih dulu.

## Susunan berkas

```
src/
  App.jsx                  cangkang: pilih rute, pegang tema, transisi geser
  lib/hooks.js             useRoute (hash) + useTheme
  lib/format.js            label aspek/urgensi, kategori, pemformat angka
  content/roadmap.js       isi tab Roadmap - data, bukan markup
  api/client.js            klien HTTP + pengurai CSV/JSON + pemetaan kolom
  screens/                 LandingScreen, DashboardScreen (pemegang state)
  components/landing/      hero, mockup ponsel, fitur, CTA penutup
  components/dashboard/    langkah unggah, pemrosesan, dan empat panel hasil
  components/insight.jsx   primitif hasil yang dipakai lintas tab
  styles/                  tokens → base → landing → dashboard
```

Gaya dipecah mengikuti pembagian yang sama. Aturannya: sesuatu masuk `base.css` hanya kalau
benar-benar dipakai kedua permukaan; kalau hanya satu sisi, ia tinggal di berkasnya sendiri.

## Aturan UI yang mengikat

- Setiap Action Card wajib tombol **Terima / Tolak / Simpan dulu** - tidak pernah eksekusi
  otomatis (ADR-013).
- Warna urgensi selalu didampingi **label teks** (aksesibilitas buta warna, bagian 14.3).
- Keyakinan rendah dan abstain memakai **abu-abu, bukan merah** - abstain bukan error.
- Angka hasil hitungan memakai kelas `.stat`; kutipan verbatim memakai monospace. Itu yang
  membedakan fakta terhitung dari narasi yang disusun sistem.
- Kategori produk hanya boleh memuat nilai yang dikenal `Category` di backend dan
  `configs/taxonomy.yaml`. Menambah entri di satu tempat saja membuat analisis ditolak 422.
- Bagian temuan foto **tidak dirender** selama backend tidak mengirim data - lebih baik tidak
  ada daripada ada tetapi berisi tebakan. Statusnya dijelaskan di tab Roadmap.

## Menjalankan

```bash
npm install
npm run dev        # http://localhost:5180, /api diproksikan ke 127.0.0.1:8000
npm run build      # keluaran statis ke dist/
```
