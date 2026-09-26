# Aplikasi web

## Fondasi bersama

- Tailwind CSS v4 dan plugin Vite, TypeScript, Lucide, clsx, tailwind-merge, tw-animate-css, alias `@/`, dan script `typecheck` tersedia.
- Token terang/gelap, tipografi, ruang, gerak, serta komponen dasar tersedia. Gaya analisis dan panduan yang tidak dipakai dihapus; layar tersebut dilepas dari router.
- Kamus namespace EN/ID, stub `messages-landing`, provider bahasa/tema, guard sesi, klien cookie, dan auth context tersedia. Layar publik menerima default export TSX dari pemiliknya.
- `npm test`: 21 tes lulus. `npm run typecheck` dan `npm run build` lulus.
- Browser dengan API lokal: pengguna tanpa sesi diarahkan ke login; login demo membuka workspace; sesi bertahan saat reload; logout kembali ke login. Pergantian EN/ID dan tema bekerja; bahasa/tema bertahan saat reload. Pada lebar 375px, lebar dokumen 360px, tanpa overflow horizontal.
- Halaman workspace masih berupa slot. Read model, shell navigasi, Overview, dan Issues belum tersambung. Landing/login lengkap belum terpasang; layar penghubung sementara menyediakan tombol login demo.
- Antarmuka komponen dan integrasi layar publik didokumentasikan di `apps/web/README.md`.

## Shell, Overview, dan Issues

- Shell navigasi, kartu akun, badge jumlah isu terbuka dari API, drawer mobile dengan penguncian fokus, dan toggle bahasa/tema tersedia.
- Konteks workspace memuat channels, summary, inbox, dan status bersama. Bucket, support, denominator, serta urutan mengikuti API; tab hanya menyaring bucket yang sudah diterima.
- Overview menampilkan bucket aktif, isu prioritas, channel dan waktu sinkron, label data sintetis, dan mode aturan. Issues menyediakan tab serta keadaan kosong; pemilihan tab disimpan per tab browser.
- Fungsi `run()` mengikuti job, menampilkan progres/toast, lalu memuat ulang workspace. Polling berhenti setelah delapan error beruntun, berhenti segera pada 401/404, dan dapat melanjutkan job dari status server setelah reload.
- Browser memakai API dari source repo pada port 8002 dan basis data uji terpisah. Port 8000 sedang dilayani container dengan respons auth yang tidak sesuai kontrak source; perlu rebuild dari commit yang dipakai untuk demo.
- Browser: akun demo menampilkan 4 produk, 21 ulasan, bucket 2 perlu fakta / 3 siap ditindak / 1 dipantau dari API. Tab Diabaikan kosong, tab Perlu Anda menampilkan kutipan asli dan support/denominator. Pada 375px gelap/ID: halaman 360px, tabel 286px dengan konten 663px hanya bergulir di dalam kartu. Fokus Tab dari kontrol terakhir drawer kembali ke kontrol pertama.
- Alias Vite dinormalisasi ke forward slash. Sebelum perbaikan, hot reload memuat provider bahasa lewat dua URL modul dan layar kosong; setelah perbaikan, hot reload kamus dan pergantian bahasa berhasil. Tes regresi alias ditambahkan.
- Verifikasi: 28 tes lulus, typecheck dan build lulus; pemeriksa mekanis antarmuka tidak menemukan pelanggaran.
- Halaman produk, Sources, Alerts, Settings, serta grafik dan decision plan belum tersambung. Landing/login tetap menunggu pemiliknya.

## Halaman produk

- Halaman produk membaca source, statistik, tahapan investigasi, finding, bukti, pemeriksaan listing, draf, dan keputusan dari API.
- Lima langkah tersedia: kutipan pelanggan, cakupan pemeriksaan listing, konfirmasi fakta, draf yang lolos status server, dan keputusan dengan catatan penerapan atau alasan pengabaian. Isu operasional diarahkan ke tindakan operasional.
- Browser pada basis data uji terpisah: fakta kosong ditolak dan pesan inline bertahan; fakta 32 x 24 cm tersimpan; draf memuat fakta tersebut; salin berhasil; penerapan mengubah bucket ke monitoring dan menampilkan follow-up menunggu ulasan baru beserta riwayat.
- Pada 375px gelap/ID, dokumen 360px tanpa overflow horizontal. Alias modul memakai /src agar hot reload kamus berbagi provider; perubahan teks terlihat tanpa layar kosong.
- Verifikasi: 28 tes, typecheck, dan build lulus. Pemeriksa mekanis antarmuka tidak menemukan pelanggaran.
- Sources, katalog produk, Alerts, Settings, grafik, dan decision plan belum tersambung. Landing Orang 4 telah masuk ke main.
