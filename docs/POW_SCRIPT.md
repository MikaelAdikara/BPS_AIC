# Naskah video Proof of Work - satu take, 7 menit, tanpa cut

Dokumen ini adalah run sheet perekaman: apa yang dibuka, apa yang diklik, apa yang diucapkan,
dan urutan pemulihannya kalau ada yang meleset. Urutan demonya mengikuti [PITCH.md](PITCH.md)
bagian "Urutan demo proof of work"; berkas ini menambah detail eksekusi yang tidak ada di sana.

**Aturan keras dari rulebook yang membentuk seluruh rencana ini:**

1. **Maksimal 7 menit, dilarang cut.** Satu take utuh. Kalau salah di menit 5 - ulang dari nol.
   Karena itu semua yang lambat/berisiko disiapkan SEBELUM tombol rekam ditekan.
2. **Semua fitur yang tampil wajib ada di repositori** - menampilkan yang tidak ada = risiko
   diskualifikasi. Semua langkah di bawah sudah dicek ada di `main`.
3. **Tanpa jejak institusi.** Tidak ada logo/almamater/nama kampus di wallpaper, jendela,
   nama akun OBS, bookmark bar, atau notifikasi.
4. PoW = **bukti teknis** (beda dengan video inovasi yang promosi). Nada bicaranya insinyur
   yang menunjukkan barangnya bekerja - bukan iklan.

Yang dinilai video ini secara tidak langsung: Implementasi Teknologi (25%), Kesiapan MVP (15%),
dan kualitas Video itu sendiri (15%). Maka strukturnya: *jalan → hitung → jujur*.

---

## A. Persiapan (kerjakan 60-90 menit sebelum rekam)

### A.1 Jendela dan tab - siapkan PERSIS urutan ini

**Chrome, profil tamu** (Ctrl+Shift+N atau profil baru - tanpa bookmark, tanpa ekstensi,
sembunyikan bookmark bar Ctrl+Shift+B, zoom 110%):

| Tab | URL | Untuk segmen |
| --- | --- | --- |
| 1 | `http://localhost:3000` (landing) | 3 |
| 2 | `http://localhost:3000/api/docs` | 8 |
| 3 | `https://github.com/MikaelAdikara/BPS_AIC` (buka tab Commits) | 1 |
| 4 | GitHub → `docs/MODEL_CARD.md`, gulir dulu ke bagian "VIS-01 - hasil gerbang Fase 3" | 9 |

**Windows Terminal**, font 18pt, dua tab:

- Tab A: di root repo, riwayat bersih (`cls`). Dipakai untuk `docker compose up` + `curl`.
- Tab B: perintah fallback SUDAH DIKETIK, tinggal Enter (lihat A.4).

**File Explorer** dibuka di `C:\Users\mikae\Downloads\pow-assets\` berisi:

- `ulasan-ss-1.png`, `ulasan-ss-2.png` - gambar daftar ulasan untuk demo OCR (mock generik,
  bukan tiruan UI marketplace; katakan itu terus terang di narasi).
- `arsip-lama.json` - hasil unduhan Arsip dari satu analisis data contoh yang dijalankan
  SEBELUM rekaman (lihat A.3). Tanpa berkas ini segmen "bandingkan" tidak bisa didemokan.

**Di luar layar rekaman** (HP / monitor kedua / kertas): naskah ini + stopwatch berjalan.

### A.2 Kebersihan layar

- Focus assist / jangan ganggu AKTIF; tutup WhatsApp, Discord, email.
- **Jeda sinkronisasi OneDrive** (ikon awan → Pause 2 hours) - repo ada di OneDrive dan
  popup "file synced" adalah pengganggu nomor satu.
- Wallpaper polos, taskbar bersih, laptop dicolok listrik, jam sistem terlihat (bukti waktu).
- Ukuran pointer mouse: Settings → Mouse → besarkan ke 3-4 supaya terlihat di 1080p.

### A.3 Gladi resik (WAJIB, minimal 2x penuh)

1. `docker compose up` dari kondisi container mati (image sudah ter-build sebelumnya -
   JANGAN rekam build pertama, itu 5-10 menit). Catat berapa detik sampai readiness hijau.
2. Jalankan sekali "Coba dengan data contoh" sampai selesai; catat durasinya (di VM 50-55
   dtk; di laptop bisa beda). **Unduh Arsip dari hasil ini** → simpan sebagai
   `pow-assets\arsip-lama.json`. Ini jadi "analisis bulan lalu" untuk segmen 7.
3. Uji tab B fallback (A.4) sekali penuh, lalu KEMBALIKAN (perintah pemulihan di bawah).
4. Uji OCR dengan kedua PNG - pastikan teks terbaca dan draf muncul.
5. Total waktu gladi harus ≤ 6:30 supaya take asli punya napas 30 detik.

### A.4 Perintah segmen fallback (tab Terminal B - PowerShell)

```powershell
# MEMATIKAN checkpoint (jalankan saat segmen 8):
docker compose stop api; Rename-Item .\models\indobert-nlp01 indobert-nlp01.off; docker compose start api
```

```powershell
# Cek kejujuran sistem setelah restart:
curl.exe -s http://localhost:8000/api/v1/readiness
```

```powershell
# PEMULIHAN (setelah rekaman selesai - JANGAN lupa):
docker compose stop api; Rename-Item .\models\indobert-nlp01.off indobert-nlp01; docker compose start api
```

Catatan: volume `./models` dipasang read-only ke container, jadi rename hanya bisa saat
container api berhenti - itulah kenapa urutannya stop → rename → start. `web` tidak ikut
mati. Setelah start tanpa checkpoint, readiness tetap 200 tetapi `text_mode` berubah dan
`errors` menyebut "model teks memakai leksikon - ..." - itulah kalimat yang dibacakan.

### A.5 Setelan OBS Studio

- Sumber: **Window Capture per jendela** (Chrome, Terminal, Explorer) atau Display Capture
  satu monitor bersih - jangan monitor yang ada naskahnya.
- Output: 1920×1080, 30 fps, rekam ke **MKV** (Settings → Advanced → Recording → remux
  otomatis ke MP4) supaya crash di menit 6 tidak menghancurkan seluruh rekaman.
- Mikrofon: filter Noise Suppression (RNNoise) + Gain; rekam tes 15 detik, dengarkan.
- Hotkey mulai/berhenti diset; JANGAN alt-tab ke OBS di tengah take.

---

## B. Naskah menit-per-menit (target 6:30, pagu 7:00)

Format: `[waktu] APA YANG DILAKUKAN` lalu *kalimat yang diucapkan* (boleh diparafrase,
jangan dibaca kaku).

**[0:00-0:25] Identitas + bukti keadaan repo.** Mulai di Terminal A. Ketik
`git log -1 --oneline` dan `git status`.
*"Ini Ulasin dari tim [NAMA TIM]. Ulasin membaca seluruh ulasan pelanggan UMKM dan
mengubahnya jadi tiga tindakan paling mendesak - dengan setiap angkanya bisa dihitung ulang.
Ini commit terakhir repositori kami, keadaannya bersih - semua yang Anda lihat tujuh menit
ke depan ada di commit ini."* (Tab 3 GitHub boleh dilirik 3 detik untuk riwayat commit.)

**[0:25-1:10] Nyala dari nol, tanpa API key.** Terminal A: `docker compose up -d` lalu
`curl.exe -s http://localhost:8000/api/v1/readiness` (ulangi curl sampai siap; sambil
menunggu, bicara).
*"Satu perintah, docker compose up. Tidak ada API key, tidak ada layanan pihak ketiga -
model IndoBERT yang kami fine-tune sendiri dimuat di CPU laptop ini. ... Readiness hijau:
text_mode full."* (Opsional yang sudah diuji saat gladi: matikan Wi-Fi di sini dan katakan
*"mulai titik ini, internet mati - sistem tetap penuh"*.)

**[1:10-1:40] Landing 30 detik saja.** Tab 1. Gulir pelan: hero → pita logo → "Buka
Hitungannya" → berhenti.
*"Ini halamannya - untuk pemilik toko yang gaptek sekalipun ada halaman panduan per
aplikasi. Tapi video ini tentang bukti, jadi langsung ke layar kerja."* Klik **Mulai
Analisis**.

**[1:40-2:50] Analisis data nyata.** Klik **Coba dengan data contoh** → **Analisis 66
ulasan**.
*"66 ulasan asli sebuah toko Shopee - bahasa sehari-hari, ada 'zonk', ada 'ngepas bgt'.
Pemiliknya sempat membaca sepuluh; sistem membaca semuanya."* Sambil progres berjalan,
sebut arsitektur satu kalimat: *"Di dalamnya: IndoBERT dua kepala untuk aspek dan
sentimen, retrieval bukti, dan mesin skor deterministik - tanpa database, data hilang
saat sesi ditutup."* Saat laporan muncul: *"66 dari 66 terbaca, [X] detik."*

**[2:50-3:40] INTI: Buka Hitungannya.** Kartu #1 → **Bagaimana angka ini dihitung?**
Tunjuk barisnya dengan kursor, KALIKAN DENGAN SUARA:
*"Frekuensi 0,197, keparahan 1, pengali tren 1,468 - nol koma satu sembilan tujuh kali
satu kali satu koma empat enam delapan kali seratus = 28,92. Persis angka di kartu.
Silakan hitung ulang - sistem ini tidak pernah mengarang angka, LLM tidak boleh menyentuh
aritmetika."* Buka satu kutipan bukti, lalu klik **Terima** di kartu:
*"Keputusan tetap di manusia."*

**[3:40-4:10] Draf balasan.** Buka draf balasan dari kartu/panel.
*"Sistem menyusun draf balasan dari keluhan nyata - dan tombol Salin TERKUNCI sampai
bagian [keputusan Anda] diisi manual. Kami sengaja membuat jalan pintasnya tidak ada:
yang tahu kebijakan toko adalah pemiliknya."* Sunting 3-4 kata, salin.

**[4:10-4:40] Tanya jawab + penolakan.** Tab Tanya Jawab. Ketik: `berapa persen keluhan
soal ukuran?` → jawaban berkutipan. Lalu ketik: `besok harga saham Telkom naik atau
turun?`
*"Pertanyaan di luar data ulasan DITOLAK, bukan dijawab sok tahu. Ini perilaku yang kami
uji, bukan kebetulan."*

**[4:40-5:20] OCR dari tangkapan layar.** Kembali ke unggah (Analisis baru) → tab
**Tangkapan layar** → tarik `ulasan-ss-1.png` dan `ulasan-ss-2.png` dari Explorer.
*"Jalur untuk pengguna yang cuma punya HP: tangkapan layar. Ini mock daftar ulasan yang
kami buat sendiri untuk demo - teksnya dibaca Tesseract lokal, hasilnya jadi draf yang
WAJIB diperiksa."* Perbaiki satu huruf di satu draf. (JANGAN jalankan analisis kedua -
makan waktu; katakan *"dari sini alurnya sama seperti tadi"*.)

**[5:20-5:50] Arsip & pembanding yang menolak sombong.** Panel Arsip → unggah
`arsip-lama.json` → bandingkan.
*"Tanpa database, riwayat jadi milik pengguna: arsip diunduh sebagai berkas, dibandingkan
antar-periode. Dan lihat - selisih kecil ditulis 'belum berarti', karena sistem menolak
mengklaim perbaikan yang tidak signifikan secara statistik."*

**[5:50-6:30] Cabut model, sistem mengaku.** Terminal B: Enter pada perintah fallback.
Sambil api restart (~beberapa detik karena tidak memuat IndoBERT), bicara:
*"Sekarang bagian yang jarang didemokan tim lain: kami MATIKAN checkpoint modelnya."*
`curl` readiness → tunjuk baris errors:
*"Sistem tidak pura-pura sehat: readiness menyebut model teks jatuh ke leksikon, dan
analisis TETAP berjalan dengan angka yang sama-sama deterministik. Gagal dengan anggun itu
fitur, bukan kecelakaan."* (Jalankan sekali analisis contoh singkat kalau waktunya ada.)

**[6:30-7:00] Jujur, lalu tutup.** Tab 4 (MODEL_CARD di GitHub).
*"Terakhir, yang belum kami capai, tertulis dengan angka: model visual kami TIDAK lolos
gerbang evaluasi - 0,45 di bawah pembanding sepele 0,61 - jadi tidak kami kirim. Kepala
aspek baru setara leksikon pada label manusia, dan kami tulis itu sebelum juri bertanya.
Semua ada di repositori: docker compose up, tujuh menit, laptop siapa pun. Terima kasih."*
Berhenti merekam.

### Prioritas buang kalau molor (potong SEBELUM rekam, bukan saat rekam)

1. Analisis contoh di mode fallback (cukup readiness + kalimatnya)
2. Landing (ganti jadi 10 detik lewat saja)
3. Segmen arsip (sebut lisan sambil menunjuk tombolnya)

JANGAN pernah membuang: Buka Hitungannya, cabut checkpoint, dan pengakuan jujur - tiga
segmen itulah pembeda dari 30+ tim lain.

---

## C. "Editing" di bawah aturan tanpa cut

- **Boleh:** memangkas kepala/ekor rekaman (sebelum kata pertama, sesudah kata terakhir),
  normalisasi volume (target ≈ -14 LUFS), noise reduction ringan, subtitle bahasa
  Indonesia yang dibakar (burn-in) MENGIKUTI ucapan - subtitle menambah kejelasan tanpa
  menyentuh kontinuitas gambar.
- **Jangan:** memotong di tengah, mempercepat bagian menunggu, menyambung dua take,
  zoom/pan hasil edit yang menyembunyikan layar. Semua itu terbaca sebagai cut.
- Ragu soal overlay teks statis (nama tim di pojok)? Aturan menuntut tanpa cut, bukan
  tanpa teks - tetapi kalau mau nol risiko, tulis nama tim di slide fisik/di ucapan saja,
  atau tanyakan di Discord panitia sebelum submit.
- Ekspor: MP4 H.264 1080p 30fps, bitrate 8-10 Mbps, audio AAC 192 kbps. Putar hasil ekspor
  SAMPAI HABIS sekali sebelum diunggah (cek audio tidak geser).
- Unggah sesuai ketentuan pengumpulan di guidebook (tautan video, bukan berkas ke form,
  kecuali diminta lain). Setelah submit, jangan ubah repo melewati batas yang diatur.

## D. Lima menit terakhir sebelum menekan Rekam

- [ ] `git status` bersih, commit terakhir sudah di-push
- [ ] Kedua container Running, readiness full (curl sekali)
- [ ] 4 tab Chrome pada posisi yang benar, tab 1 aktif? Bukan - **Terminal A aktif** (take
      mulai dari terminal)
- [ ] `pow-assets` berisi 2 PNG + `arsip-lama.json`
- [ ] Tab Terminal B: perintah fallback sudah terketik
- [ ] Focus assist on, OneDrive pause, mic dites, stopwatch nol
- [ ] Air minum. Tarik napas. Kalau gagal, ulang - take ketiga hampir selalu yang terbaik.
