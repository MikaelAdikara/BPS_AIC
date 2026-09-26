# Aplikasi web

## Fondasi bersama

- Tailwind CSS v4 dan plugin Vite, TypeScript, Lucide, clsx, tailwind-merge, tw-animate-css, alias `@/`, dan script `typecheck` tersedia.
- Token terang/gelap, tipografi, ruang, gerak, serta komponen dasar tersedia. Gaya analisis dan panduan yang tidak dipakai dihapus; layar tersebut dilepas dari router.
- Kamus namespace EN/ID, stub `messages-landing`, provider bahasa/tema, guard sesi, klien cookie, dan auth context tersedia. Layar publik menerima default export TSX dari pemiliknya.
- `npm test`: 21 tes lulus. `npm run typecheck` dan `npm run build` lulus.
- Browser dengan API lokal: pengguna tanpa sesi diarahkan ke login; login demo membuka workspace; sesi bertahan saat reload; logout kembali ke login. Pergantian EN/ID dan tema bekerja; bahasa/tema bertahan saat reload. Pada lebar 375px, lebar dokumen 360px, tanpa overflow horizontal.
- Halaman workspace masih berupa slot. Read model, shell navigasi, Overview, dan Issues belum tersambung. Landing/login lengkap belum terpasang; layar penghubung sementara menyediakan tombol login demo.
- Antarmuka komponen dan integrasi layar publik didokumentasikan di `apps/web/README.md`.
