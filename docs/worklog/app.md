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

## Katalog produk

- Katalog membaca urutan, jumlah ulasan, rating, jumlah temuan, jumlah yang dapat diperbaiki di listing, status analisis, dan stale dari API. Aksi investigasi semua memakai job server.
- Browser memperlihatkan empat produk dengan label sintetis dan engine aturan. Navigasi produk berhasil. Pada 375px, dokumen 360px dan tabel 651px bergulir di dalam kartu.
- Isu waktu pengiriman menampilkan arahan operasional, melewati formulir fakta dan draf listing.
- Verifikasi: 28 tes, typecheck, dan build lulus. Sources, Alerts, Settings, grafik, dan decision plan belum tersambung.

## Settings dasar

- Profil membaca akun aktif; nama dan nomor telepon disimpan melalui PATCH /auth/me. Bahasa/tema memakai provider bersama. Status engine, model, fetch, dan anggaran berasal dari status server; versi/pipeline/verifier/commit berasal dari endpoint version.
- Browser pada basis data uji terpisah: nomor 123 ditolak dengan pesan lokal; nama uji tersimpan dan bertahan setelah reload; profil dipulihkan dan toast Profil disimpan tampil. Pada 375px gelap/ID, dokumen 360px tanpa overflow horizontal.
- Refresh profil berjalan di latar belakang agar workspace dan toast tidak terlepas saat penyimpanan. Perubahan berkas provider saat pengembangan memuat ulang halaman penuh untuk mencegah konteks ganda; perubahan layar tetap memakai hot update.
- Verifikasi: 29 tes, typecheck, dan build lulus. Sources, Alerts, Telegram linking, grafik, dan decision plan belum tersambung.

## Migrasi volume dan Sources

- Dengan izin perluasan tugas, migrasi database mengarsipkan tabel berbasis store_id/issue_id yang bertabrakan dengan skema aktif. Tabel akun/sesi dipertahankan. Migrasi berada dalam transaksi dan snapshot SQLite dibuat sebelum rebuild container.
- Pada volume container, arsip berisi 14 produk, 45 ulasan, 5 fakta, dan 29 alert; pemeriksaan foreign key tidak menemukan pelanggaran. Login demo lewat port 8000 berhasil. Tes migrasi/platform/sources: 27 lulus.
- Sources menyediakan pilihan channel tersimpan, koneksi toko Woo, sinkron/disconnect, impor teks/CSV, paket contoh server, demo langsung, serta dialog reset/hapus.
- Browser port 8000: pilihan Woo/Manual tersimpan; impor teks menghasilkan 2 baru; impor ulang menghasilkan 0 baru dan 2 tetap; investigasi dan sinkron Woo selesai. Sources gelap/ID pada 375px memiliki dokumen 360px tanpa overflow. Dialog hapus memfokuskan Batal dan kembali ke tombol pembuka sesudah dibatalkan.
- CSV, pemuatan paket, demo langsung, dan aksi reset/hapus belum diuji end-to-end. Form penambahan satu ulasan demo, Lazada live, Alerts, grafik, decision plan, dan Telegram linking belum tersedia.
- Verifikasi web: 29 tes, typecheck, dan build lulus. API pengujian memakai 8000; container dibangun ulang bila backend berubah.

## Overview, filter, alert, dan kontrak engine

- Overview memakai read model server untuk grafik bukti unik per produk/ulasan, rentang waktu, ranking, dan keputusan dengan driver heuristik. Kandidat lintas produk/channel memakai hasil engine; bukan identitas SKU.
- Filter dan urutan produk/isu dikirim ke API. Alerts menyediakan status, aturan, pesan, dan tautan temuan. Settings menyediakan kode tautan Telegram, status kedaluwarsa, unlink, dan tombol uji.
- Produk menampilkan alasan already_in_listing, cakupan model_chars, pembanding chatbot umum dengan kalimat terblokir tetap terlihat, serta anggaran dan perkiraan investigasi dari server.
- Verifikasi: 29 tes web, typecheck, build, dan 90 tes backend terarah lulus. Korpus PII mencakup nomor bertitik, email tersamar, nama kontekstual, alamat gedung, dan ukuran pribadi. Tes startup memastikan pemeriksaan ulang di thread latar memegang ANALYSIS_LOCK.
- Pemeriksaan browser untuk fitur tambahan belum selesai. Pengiriman Telegram nyata dan pembandingan provider nyata belum diuji.

## Integrasi dan pengujian workspace

- Seluruh 584 tes unit backend lulus. Setelah penambahan metadata batas fetch dan perbaikan URL publik, 26 tes sumber/platform/URL lulus; web tetap 29 tes, typecheck, dan build lulus.
- Browser Overview menampilkan keputusan dari engine dan rentang 7 hari. Overview dan Alerts gelap/ID pada 375px memiliki lebar dokumen 360px. Loading dan pesan error tampil saat container belum siap atau query ditolak; rentang query sudah diperbaiki dengan tes HTTP.
- Sources menyediakan URL Lazada, status belum dikonfigurasi, batas URL/ulasan/biaya dari API, serta formulir ulasan toko demo sintetis. Hasil pencarian produk kosong menyediakan tombol hapus filter.
- Kamus bahasa memicu reload penuh saat pengembangan supaya provider tidak terduplikasi di Windows. Label persentase kandidat dibedakan dari seluruh ulasan. URL publik membuang fragmen router agar tautan alert baru tidak memiliki dua fragmen.
- Form Lazada dan ulasan demo belum diuji sampai selesai melalui browser. Telegram nyata belum dikirim.

## Pembanding dan keputusan

- Browser memanggil pembanding pada produk sintetis Kursi lipat camping: respons gpt-5-mini/verify-v2.2 memuat 29 kalimat, 8 diblokir, dan klaim tanpa sumber tetap terlihat. Hasil disimpan server. Ini satu contoh integrasi, bukan pengukuran keunggulan model.
- Hasil pembanding berada di disclosure agar investigasi produk tetap mudah dicapai. Overview membaca GET /decisions secara langsung dan mempertahankan urutan/driver server.
- Pengurutan share server memakai denominator kandidat yang diinvestigasi, dan kandidat atribut lintas produk dibatasi pada attribute_key yang sama.
- Verifikasi tambahan: 4 tes insights, 29 tes web, typecheck, dan build lulus.

## Detail produk dan ketahanan UI

- Teks listing tersimpan bisa ditinjau/diperbarui. Metrik rating tanpa ulasan pendukung diberi keterangan deskriptif, bukan prediksi; varian dengan sedikit bukti berlabel eksploratif. Draf needs_review tanpa teks menampilkan alasan tinjauan yang sesuai.
- Panel investigasi mempunyai meter anggaran dari API. Riwayat alert menampilkan tanggal kelompok tanpa mengubah urutan server. Error boundary luar menyediakan pesan lokal dan muat ulang bila provider gagal. Menghapus pilihan CSV juga mengosongkan input berkas.
- Browser: penambahan satu ulasan sintetis selesai; form Lazada menampilkan batas server 12 URL/30 ulasan/$1. Pencarian produk tanpa hasil menampilkan keadaan kosong dan hapus filter; urutan nama berasal dari API. Produk gelap/ID pada 375px memiliki lebar dokumen 360px.
- Status fetch menghitung reservasi biaya dengan fungsi yang sama seperti penjaga anggaran. Tes sumber terkait: 17 lulus. Paket snapshot Lazada sedang diproses; belum dinyatakan selesai. Pengiriman Telegram nyata dan fetch berbayar belum diuji.

## Verifikasi snapshot selesai

- Pemuatan paket snapshot Lazada selesai 10/10 produk. Job API melaporkan 517 masuk, 515 baru, 2 kosong dilewati, dan 3 diredaksi. Pilihan channel serta bahasa/tema dipulihkan sesudah pengujian.
- Seluruh 586 tes unit backend lulus setelah perubahan anggaran fetch. Overview menampilkan lima keputusan pertama dari urutan API, dengan tombol untuk seluruh keputusan, agar grafik tetap mudah dicapai pada katalog besar.
- Fetch provider berbayar, pengiriman Telegram nyata, dan aksi hapus/reset lewat browser tetap belum diuji. Hapus/reset dan isolasi data sudah diuji pada database sementara dalam tes backend.

## Editor listing berspesifikasi

- Probe produksi menemukan bahwa listing_text berisi deskripsi dan spesifikasi sumber. Menyimpan teks gabungan sebagai deskripsi menggandakan spesifikasi dan memicu analisis ulang.
- ProductView menambah listing_edit_text untuk deskripsi mentah; listing_text tetap teks gabungan yang diperiksa. Editor memakai listing_edit_text. Server menganggap penyimpanan ulang teks gabungan yang identik sebagai tidak berubah.
- Tes round-trip memastikan spesifikasi hanya muncul sekali, teks tidak berubah tidak memicu perubahan, dan deskripsi baru tetap memakai spesifikasi sumber. Editor/route/pipeline: 19 tes lulus; web: 29 tes, typecheck, dan build lulus.

## Verifikasi produksi lanjutan

- Seluruh 587 tes unit backend lulus setelah perbaikan editor. Browser produksi menampilkan model_chars 143/143 dan menyimpan ulang deskripsi tanpa analisis baru; toast Listing saved terlihat.
- Filter dampak tinggi di Issues produksi menghasilkan 18 baris; pada 375px lebar dokumen 360px. Filter dipulihkan setelah pengujian.
- Snapshot memperlihatkan ukuran pribadi berbentuk tinggi saya. Redaksi mencakup kata ganti pada ukuran pribadi, dengan tes regresi; spesifikasi tinggi/berat produk tetap dipertahankan.
