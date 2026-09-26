# Deciqo web

React 18, Vite, TypeScript, Tailwind CSS v4, dan Lucide. Jalankan dari direktori ini:

```sh
npm ci
npm run dev
npm test
npm run typecheck
npm run build
```

Vite meneruskan `/api` ke `http://127.0.0.1:8000`. Gunakan `API_URL` untuk target lain dan `PORT` untuk port web. Alias `@/` menunjuk `src/`.

## Antarmuka bersama

- `styles/tokens.css`: warna kedua tema, tipografi, ruang, bentuk, kedalaman, dan jembatan Tailwind.
- `components/ui.tsx`: Button (`variant`, `size`, `busy`), Chip (`tone`, `synthetic`), Card (`title`, `lead`, `icon`, `action`), Notice, Field (`label`, `hint`, `error`), Toast, Skeleton, LoadingState, Table, Quote, Metric, EmptyState.
- `components/Brand.jsx`: Brand, BrandMark, LangToggle, ThemeToggle.
- `lib/i18n.tsx`: `useI18n()` menyediakan `language`, `setLanguage`, `t('namespace.key', values)`, `localizeError(code)`, `plural(count)`.
- `lib/theme.tsx`: `useTheme()` menyediakan `theme` dan `toggleTheme()`.
- `api/auth.tsx`: `useAuth()` menyediakan `user`, `loading`, `error`, `refresh`, `login(email, password)`, `register(email, password, name)`, `logout`, `demo`.
- `api/http.js`: `request('/deciqo/...', { method, body, signal })`, cookie otomatis disertakan. Tangani `ApiError.code` dengan `localizeError` agar teks respons mentah tidak tampil.

Provider tersedia di akar aplikasi, termasuk bagi layar publik. Penyimpanan preferensi boleh gagal tanpa mematikan aplikasi.

## Integrasi layar publik

Pemilik landing/login menambahkan `screens/LandingScreen.tsx` dan `screens/LoginScreen.tsx`, masing-masing dengan **default export**. Router memuatnya otomatis. Layar mengatur landmark dan layout sendiri, memakai Brand, LangToggle, dan ThemeToggle; impor `styles/landing.css` langsung dari LandingScreen. Login membaca rute `#/register` untuk mode pendaftaran dan memanggil `useAuth()` untuk autentikasi.

`lib/messages-landing.js` mengekspor `landing = { en: {}, id: {} }`. Stub awal tersedia dan selanjutnya hanya pemilik landing yang mengeditnya. Kamus induk mengimpornya; tes memeriksa paritas kunci dan placeholder kedua bahasa. Gunakan kunci datar di setiap namespace.

Router hanya membaca hash berawalan `#/`. Anchor `#how` dan `#gate` mempertahankan permukaan aktif. Query dapat dibaca dari `parseRoute(window.location.hash).query`. Semua rute `#/app/...` memerlukan sesi; pemeriksaan sesi gagal menyediakan aksi coba lagi.

Sebelum layar publik terpasang, layar penghubung menyediakan login demo untuk memeriksa koneksi API. Data produk tidak direkayasa di frontend. Halaman workspace masih berupa slot untuk penyambungan read model.

`VITE_DEMO_EMAIL` dan `VITE_DEMO_PASSWORD` hanya untuk kredensial demo publik. Semua variabel `VITE_*` masuk bundle browser; jangan gunakan kredensial privat.
