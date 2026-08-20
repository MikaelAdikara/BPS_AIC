/** Dua hook yang mengatur cangkang aplikasi: rute dan tema. */

import { useEffect, useState } from "react";

// --------------------------------------------------------------------------------------
// Rute
// --------------------------------------------------------------------------------------

/** Landing dan dashboard adalah dua alamat, bukan dua nilai state.
 *
 * Alasannya perilaku browser: tanpa alamat sendiri, tombol Back dari dashboard melempar
 * pengguna keluar dari situs dan menyegarkan halaman mengembalikannya ke halaman pemasaran
 * di tengah pekerjaan. Hash dipilih supaya tidak ada aturan fallback yang perlu ditambahkan
 * di nginx maupun `vite preview` - berkas statis yang sama melayani kedua rute.
 *
 * Hash yang diawali "#/" adalah rute; "#fitur" dan sejenisnya tetap tautan jangkar biasa
 * di dalam halaman landing.
 */
export const ROUTE = { landing: "#/", dashboard: "#/analisis" };

function routeFromHash(hash) {
  return hash.startsWith(ROUTE.dashboard) ? "dashboard" : "landing";
}

export function goTo(route) {
  const target = ROUTE[route] ?? ROUTE.landing;
  if (window.location.hash !== target) window.location.hash = target;
}

/** Mengembalikan `{ route, direction }`. `direction` dipakai transisi geser agar layar
 *  yang dibuka dari landing masuk dari kanan, dan yang dibuka lewat Back masuk dari kiri. */
export function useRoute() {
  const [state, setState] = useState(() => ({
    route: routeFromHash(window.location.hash),
    direction: "forward",
  }));

  useEffect(() => {
    function onChange() {
      setState((prev) => {
        const next = routeFromHash(window.location.hash);
        if (next === prev.route) return prev;
        return { route: next, direction: next === "dashboard" ? "forward" : "back" };
      });
    }
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  return state;
}

// --------------------------------------------------------------------------------------
// Tema
// --------------------------------------------------------------------------------------

/** Desain ini bermode terang; gelap adalah varian, bukan sebaliknya. Karena itu preferensi
 *  OS TIDAK dibaca saat muat - mesin yang kebetulan bertema gelap dulu membuka aplikasi dalam
 *  tampilan yang bukan tampilan rancangannya. Yang dihormati hanya pilihan eksplisit
 *  pengguna, dan pilihan itu diingat antar-kunjungan. */
const THEME_KEY = "insightulasan:theme";

export function useTheme() {
  const [theme, setTheme] = useState(() =>
    window.localStorage?.getItem(THEME_KEY) === "dark" ? "dark" : "light"
  );

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage?.setItem(THEME_KEY, theme);
  }, [theme]);

  return [theme, () => setTheme((t) => (t === "dark" ? "light" : "dark"))];
}
