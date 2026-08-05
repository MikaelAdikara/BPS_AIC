# Brand & UI Guidelines — InsightUlasan

Panduan ini cukup konkret untuk langsung dipakai mendesain di Figma **dan** sudah tersedia
sebagai token CSS di [`apps/web/src/styles/tokens.css`](../apps/web/src/styles/tokens.css) —
satu sumber kebenaran, bukan dua dokumen yang lambat laun berbeda.

---

## 1. Untuk siapa ini dirancang

Bu Rina, pemilik toko fesyen mikro. Literasi digital sedang. Membuka aplikasi ini **malam hari
setelah tutup toko**, di HP Android, dalam keadaan lelah, untuk satu pertanyaan: *"besok saya
harus benahi apa?"*

Tiga konsekuensi desain yang mengikat:

1. **Ukuran teks tidak boleh mengecil demi kerapian.** Body minimum 16px. Tidak ada teks 12px
   untuk konten yang harus dibaca.
2. **Satu layar, satu keputusan.** Bukan dashboard. Setiap Action Card adalah satu keputusan
   yang bisa diambil atau ditolak.
3. **Tidak ada istilah teknis di antarmuka.** Bukan "confidence score 0,86" tetapi "cukup
   yakin". Bukan "abstain" tetapi "tidak bisa disimpulkan dari foto ini".

## 2. Gagasan visual inti

> **Angka dan kutipan diketik mesin. Narasi ditulis bahasa manusia.**

Produk ini punya satu janji yang membedakannya: *angka tidak pernah dikarang, dan setiap klaim
punya kutipan aslinya.* Janji itu diangkat ke tingkat tipografi, bukan cuma ditulis di dokumen.

| Yang ditampilkan | Typeface | Alasan |
| --- | --- | --- |
| Angka hasil hitungan, persentase, skor | **IBM Plex Mono**, tabular | Ini keluaran tool deterministic. Rata kolomnya membuat angka bisa dibandingkan sekilas. |
| Kutipan ulasan asli | **IBM Plex Mono** | Menandakan **rekaman apa adanya** — tidak diparafrase, tidak dirapikan. |
| Narasi, judul, label, tombol | **Plus Jakarta Sans** | Suara manusia yang menjelaskan. |

Begitu pengguna melihat huruf monospace, ia tahu itu **bukan karangan sistem**. Pemisahan ini
konsisten di semua layar — termasuk angka yang muncul di tengah kalimat.

Plus Jakarta Sans dipilih bukan karena netral: ia dirancang sebagai identitas tipografi Jakarta,
punya karakter yang pas untuk produk yang melayani pedagang Indonesia, dan sangat terbaca pada
ukuran besar di layar HP.

## 3. Palet — "Nila & Struk"

Warna dasarnya **nila**, rujukan pada tarum, pewarna indigo tradisional tekstil Indonesia —
bukan biru SaaS generik. Tenang, dapat dipercaya, dan pas untuk kategori pertama produk ini
(fesyen). Permukaannya kertas hangat-netral, bukan krem.

### 3.1 Permukaan & teks

| Token | Hex | Pakai untuk |
| --- | --- | --- |
| `--paper` | `#F7F7F5` | Latar halaman |
| `--surface` | `#FFFFFF` | Kartu, panel |
| `--surface-sunken` | `#EFEFEC` | Blok kutipan, area input |
| `--ink` | `#1A1D26` | Teks utama |
| `--ink-muted` | `#5A6070` | Teks sekunder, metadata |
| `--rule` | `#DEDFDA` | Garis pemisah, tepi kartu |

### 3.2 Merek

| Token | Hex | Pakai untuk |
| --- | --- | --- |
| `--nila-700` | `#2B3A8F` | Tombol utama, tautan, aksen merek |
| `--nila-500` | `#4356C7` | Hover, cincin fokus |
| `--nila-100` | `#E6E9F8` | Latar bertint, badge netral |

### 3.3 Warna semantik — **ini aturan, bukan selera**

| Arti | Token | Hex | Catatan |
| --- | --- | --- | --- |
| Urgensi tinggi | `--urgency-high` | `#B3261E` | Pill terisi + label teks "Tinggi" |
| Urgensi sedang | `--urgency-medium` | `#9C5D00` | Pill terisi + label "Sedang" |
| Urgensi rendah | `--urgency-low` | `#5A6070` | Sengaja diam — abu-abu, bukan hijau |
| Temuan positif / peluang | `--positive` | `#1F6B4A` | Aspek yang dipuji pelanggan |
| **Keyakinan rendah / abstain** | `--abstain` | `#636774` | **ABU-ABU. TIDAK PERNAH MERAH.** |
| Error teknis | `--error` | `#B3261E` | Selalu **kotak bergaris**, bukan pill |

**Kenapa abstain harus abu-abu.** Saat model visual menjawab *"Tidak dapat menyimpulkan kondisi
produk dari foto ini"*, itu bukan kegagalan — itu sistem yang jujur mengakui batasnya, dan justru
alasan ia layak dipercaya. Mewarnainya merah membuat pengguna mengira ada yang rusak, lalu berhenti
memercayai seluruh hasil.

**Kenapa error dan urgensi-tinggi boleh sewarna.** Keduanya `#B3261E`, tetapi **bentuknya berbeda**:
urgensi selalu *pill terisi di dalam kartu*, error selalu *kotak bergaris di luar alur konten*.
Dibedakan bentuk lebih andal daripada dibedakan rona.

### 3.4 Aturan warna yang tidak bisa ditawar

- **Warna tidak pernah menjadi satu-satunya penanda.** Setiap pill urgensi wajib memuat teksnya
  ("Tinggi"/"Sedang"/"Rendah"). Pengguna buta warna harus mendapat informasi yang sama persis.
- Kontras teks minimum **4,5:1**. Seluruh pasangan warna pada `tokens.css` sudah diverifikasi
  memenuhi ini di mode terang **dan** gelap. Dua nilai sempat diturunkan gelapnya karena gagal:
  `--urgency-medium` dari `#B26B00` ke `#9C5D00`, dan `--abstain` dari `#6E7280` ke `#636774`.
  Jalankan ulang pemeriksaan kontras bila mengubah warna apa pun.
- Jangan menambah warna semantik baru. Kalau butuh kategori baru, pakai bentuk atau posisi.

## 4. Tipografi

Skala dirancang mobile-first. Angka di kolom manapun memakai `font-variant-numeric: tabular-nums`.

| Peran | Ukuran/tinggi baris | Berat | Typeface |
| --- | --- | --- | --- |
| Display L — judul layar | 30 / 36 | 700 | Plus Jakarta Sans |
| Display M — ringkasan eksekutif | 24 / 32 | 700 | Plus Jakarta Sans |
| Title — judul Action Card | 19 / 26 | 600 | Plus Jakarta Sans |
| Body | 16 / 26 | 400 | Plus Jakarta Sans |
| Body S — metadata | 14 / 22 | 400 | Plus Jakarta Sans |
| Label — eyebrow, header tabel | 13 / 16 | 600, `0.04em`, UPPERCASE | Plus Jakarta Sans |
| **Stat** — angka hasil hitungan | 16 / 24 | 600, tabular | **IBM Plex Mono** |
| **Quote** — kutipan verbatim | 15 / 26 | 400 | **IBM Plex Mono** |

IBM Plex Mono punya x-height lebih kecil dari Plus Jakarta Sans. Saat angka mono muncul di dalam
kalimat sans, naikkan ukurannya **1px** agar terlihat sepadan.

## 5. Tata letak

- Satu kolom di semua ukuran layar. Tidak ada sidebar, tidak ada nav global.
- Lebar konten maksimum **560px** — panjang baris nyaman dibaca, dan desktop tidak terasa kosong
  karena kartunya memang objek tunggal.
- Padding tepi: 16px (mobile), 24px (≥600px).
- Basis spasi **4px**: `4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 56 · 72`.
- Radius: kartu **10px**, input 8px, pill 999px.
- Elevasi: satu tingkat saja — `0 1px 2px rgba(26,29,38,.06)` plus garis `--rule`. Tidak ada
  bayangan tebal; kedalaman datang dari garis dan permukaan.

## 6. Anatomi komponen

### 6.1 Action Card — objek utama produk

```
┌──────────────────────────────────────────────┐
│ ● Tinggi          ← pill terisi + teks       │
│                                              │
│ Revisi panduan ukuran varian M dan L         │  Title 19/26 · 600
│                                              │
│ 25 dari 120 ulasan (21%) menyebut ukuran     │  Body + angka MONO
│ lebih kecil dari perkiraan pembeli.          │
│                                              │
│ ┃ "ukurannya kekecilan, padahal udah         │  ← EVIDENCE STRIP
│ ┃  pesan size L"                             │    mono, surface-sunken
│ ┃  Ulasan #482 · 2 dari 5 · 14 Jul           │    garis kiri nila
│                                              │
│ Lihat 24 bukti lainnya  →                    │  tautan nila-700
│                                              │
│ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│ │  Terima  │ │  Tolak   │ │ Simpan dulu   │  │  ← min 44px tinggi
│ └──────────┘ └──────────┘ └───────────────┘  │
└──────────────────────────────────────────────┘
```

**Evidence strip adalah elemen tanda tangan produk ini.** Garis vertikal `--nila-700` selebar 3px,
latar `--surface-sunken`, teks mono. Ia selalu menempel pada klaim yang didukungnya — tidak pernah
berdiri sendiri, tidak pernah diringkas. Kutipan **tidak boleh dipotong di tengah kata**; kalau
terlalu panjang, potong di batas kalimat dan beri "…".

Tombol: `Terima` (isi nila-700) · `Tolak` (garis) · `Simpan dulu` (teks saja). Ketiganya wajib ada
— tidak pernah ada kartu tanpa jalan keluar bagi pengguna.

### 6.2 Kartu temuan visual

Dua keadaan, dan **keduanya sama pentingnya untuk ditunjukkan**:

```
Yakin                              Tidak bisa disimpulkan
┌───────────────────────┐          ┌───────────────────────┐
│ [foto]                │          │ [foto, opacity .55]   │
│ Kemasan rusak         │          │ Tidak bisa disimpulkan│
│ Cukup yakin · 82%     │          │ dari foto ini         │
└───────────────────────┘          │ Foto kurang jelas     │
  border: --rule                   └───────────────────────┘
                                     border & teks: --abstain
```

Kartu abstain **tidak** diberi ikon peringatan, tidak diberi warna merah, dan tidak disembunyikan.

### 6.3 Kartu perbandingan kategori

Angka toko dan angka baseline diletakkan berdampingan dalam mono agar sebanding sekilas.
Ukuran sampel **selalu** tampil — `n=8.939` — dan tingkat keyakinan ditulis sebagai kata.
Istilah yang dipakai: **"rata-rata kategori sejenis"**. Jangan pernah menulis "kompetitor" atau
"rata-rata pasar" — datanya agregat publik, bukan data toko pesaing.

### 6.4 Banner mode & peringatan

| Situasi | Bentuk | Teks |
| --- | --- | --- |
| Data sedikit (<15 ulasan) | Banner `--urgency-medium` bertint | "Data Anda masih sedikit. Anggap hasil ini sebagai indikasi awal, bukan kesimpulan." |
| FALLBACK MODE aktif | Banner `--ink-muted` bertint, kecil | "Mode sederhana aktif — sebagian penjelasan memakai teks standar." |
| Analisis visual tidak tersedia | Catatan sebaris di bagian visual | "Analisis foto tidak tersedia saat ini. Hasil dari teks tetap lengkap." |

## 7. Nada bahasa

Aktif, ringkas, tidak menjanjikan kepastian yang tidak dimiliki.

| Tulis begini | Bukan begini | Kenapa |
| --- | --- | --- |
| "Periksa panduan ukuran varian M dan L" | "Optimasi listing" | Perintah yang bisa dikerjakan besok pagi |
| "25 dari 120 ulasan" | "Banyak ulasan" | Angka konkret adalah inti produk |
| "Cukup yakin" | "Confidence 0,86" | Istilah teknis di antarmuka melelahkan |
| "Tidak bisa disimpulkan dari foto ini" | "Klasifikasi gagal" | Ini keputusan jujur, bukan error |
| "Data belum cukup untuk menjawab ini" | "Maaf, saya tidak tahu" | Antarmuka tidak minta maaf |
| "Simpan dulu" | "Submit" | Tombol menyebut apa yang terjadi |

Nama tombol **tidak berubah** sepanjang alur: yang bertuliskan "Terima" menghasilkan status
"Diterima".

## 8. Gerak

Satu momen terorkestrasi saja: **checklist pemrosesan** pada Screen 2. Tahapan muncul berurutan
dengan jeda 120ms dan tanda centang yang masuk dengan `translateY(4px) → 0`. Ini yang meyakinkan
pengguna bahwa sistem benar-benar bekerja, bukan spinner yang berputar tanpa arti.

Selebihnya seperlunya: transisi keadaan 160ms `ease-out`, evidence drawer masuk 200ms. Hormati
`prefers-reduced-motion: reduce` — nonaktifkan seluruh transform, sisakan perubahan opasitas.

## 9. Aksesibilitas — lantai, bukan tambahan

- Target sentuh minimum **44 × 44px**.
- Cincin fokus **selalu terlihat**: `2px solid var(--nila-500)` dengan `outline-offset: 2px`.
  Jangan pernah `outline: none` tanpa pengganti.
- Setiap Action Card dapat dijangkau keyboard dengan urutan tab yang masuk akal.
- Progress bar memakai `role="progressbar"` beserta `aria-valuenow`.
- Foto ulasan wajib punya `alt` yang menjelaskan temuannya, bukan "gambar".
- Panel bukti memindahkan fokus ke judulnya saat dibuka, dan mengembalikan fokus saat ditutup.

## 10. Yang sengaja tidak ada

Tidak ada logo bermerek dagang, ilustrasi maskot, gradien dekoratif, grafik donat, ikon emoji
sebagai penanda status, maupun mode gelap sebagai fitur pamer. Produk ini dinilai dari kejelasan
keputusan yang dihasilkannya — setiap elemen yang tidak membantu pengguna memutuskan sesuatu
adalah beban.

Mode gelap **didukung** lewat token, tetapi bukan prioritas Tier 1.
