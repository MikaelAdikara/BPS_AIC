/** Hook cangkang aplikasi: rute, tema, dan pengukuran luber horizontal. */

import { useCallback, useEffect, useRef, useState } from "react";

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
export const ROUTE = { landing: "#/", dashboard: "#/analisis", guide: "#/panduan" };

function routeFromHash(hash) {
  if (hash.startsWith(ROUTE.dashboard)) return "dashboard";
  if (hash.startsWith(ROUTE.guide)) return "guide";
  return "landing";
}

/** Parameter di belakang hash rute, mis. "#/analisis?masukan=shot" → "shot".
 *  Dipakai tautan dalam (halaman panduan → tab masukan yang tepat). */
export function hashParam(name) {
  const q = window.location.hash.split("?")[1];
  return q ? new URLSearchParams(q).get(name) : null;
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
        const hash = window.location.hash;
        // Hash tanpa awalan "#/" adalah JANGKAR di dalam halaman yang sedang terbuka
        // ("#gtempat" di panduan, "#bukti" di landing) - bukan perpindahan rute. Tanpa
        // pengecualian ini, mengeklik "Tempat ulasan" di nav panduan melempar pengguna
        // kembali ke landing: routeFromHash menjawab "landing" untuk semua hash asing.
        if (hash && !hash.startsWith("#/")) return prev;
        const next = routeFromHash(hash);
        if (next === prev.route) return prev;
        // Kembali ke landing = mundur; ke mana pun selain itu = maju.
        return { route: next, direction: next === "landing" ? "back" : "forward" };
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
const THEME_KEY = "ulasin:theme";

export function useTheme() {
  const [theme, setTheme] = useState(() =>
    window.localStorage?.getItem(THEME_KEY) === "dark" ? "dark" : "light"
  );

  useEffect(() => {
    const akar = document.documentElement;

    // Penanda ini mematikan seluruh transisi selama pergantian berlangsung. Alasan lengkapnya
    // ada di base.css; singkatnya, properti yang ditransisikan sambil membaca custom property
    // akan membeku di nilai tema lama begitu tokennya berganti.
    akar.setAttribute("data-theme-switching", "");
    akar.dataset.theme = theme;
    window.localStorage?.setItem(THEME_KEY, theme);

    // Dua frame, bukan satu. Frame pertama adalah frame tempat gaya barunya dihitung; melepas
    // penanda di situ mengembalikan transisi tepat sebelum perhitungan itu selesai, dan
    // pembekuan yang sama terjadi lagi.
    let frame2 = 0;
    const frame1 = requestAnimationFrame(() => {
      frame2 = requestAnimationFrame(() => akar.removeAttribute("data-theme-switching"));
    });
    return () => {
      cancelAnimationFrame(frame1);
      cancelAnimationFrame(frame2);
      akar.removeAttribute("data-theme-switching");
    };
  }, [theme]);

  return [theme, () => setTheme((t) => (t === "dark" ? "light" : "dark"))];
}

// --------------------------------------------------------------------------------------
// Pengukuran luber
// --------------------------------------------------------------------------------------

/** Memberi tahu apakah isi sebuah wadah MUAT secara horizontal.
 *
 * Dipakai tabel yang boleh digulir menyamping. Wadahnya memakai topeng gradien di tepi kanan
 * sebagai tanda "masih ada kolom di sebelah sana", dan tanda itu hanya benar selama isinya
 * memang terpotong - kalau tabelnya muat, topeng yang tetap terpasang memudarkan kolom
 * terakhir tanpa alasan. CSS tidak bisa menanyakan hal ini sendiri, jadi diukur di sini.
 *
 * `ResizeObserver` mengamati wadah DAN tabel di dalamnya: lebar wadah berubah saat jendela
 * diubah ukurannya, sedangkan lebar tabel berubah saat datanya berganti - dan keduanya dapat
 * terjadi tanpa render ulang React.
 *
 * Mengembalikan `[ref, fits]`.
 */
export function useOverflowX() {
  const [fits, setFits] = useState(true);
  const node = useRef(null);

  const ref = useCallback((el) => {
    node.current = el;
    if (!el) return;
    const ukur = () => setFits(el.scrollWidth <= el.clientWidth + 1);
    ukur();
    if (typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(ukur);
    ro.observe(el);
    if (el.firstElementChild) ro.observe(el.firstElementChild);
    el._ro?.disconnect();
    el._ro = ro;
  }, []);

  useEffect(() => () => node.current?._ro?.disconnect(), []);

  return [ref, fits];
}
