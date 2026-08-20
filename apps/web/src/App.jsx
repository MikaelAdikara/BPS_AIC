/** Cangkang InsightUlasan.
 *
 * Dua permukaan yang benar-benar terpisah: halaman pemasaran di "#/" dan dashboard analisis
 * di "#/analisis". Berkas ini hanya memilih salah satunya, memegang tema, dan mengurus
 * transisi geser di antara keduanya.
 */

import { useEffect, useRef, useState } from "react";
import { DashboardScreen } from "./screens/DashboardScreen.jsx";
import { LandingScreen } from "./screens/LandingScreen.jsx";
import { useRoute, useTheme } from "./lib/hooks.js";

export default function App() {
  const [theme, toggleTheme] = useTheme();
  const { route, direction } = useRoute();
  const frame = useRef(null);

  // Dashboard TIDAK dilepas saat pengguna kembali ke halaman pemasaran.
  //
  // Melepasnya berarti membuang hasil analisis yang sudah jadi - beserta keputusan Terima/Tolak
  // dan seluruh riwayat tanya jawab - hanya karena pengguna menekan logo untuk melihat sesuatu
  // sebentar. Analisis 66 ulasan memakan hampir satu menit, dan tidak ada yang disimpan di
  // server untuk dipulihkan (ADR-010, sesi tunggal). Jadi ia dipasang sekali lalu disembunyikan.
  //
  // Pemasangannya tetap ditunda sampai benar-benar dibuka, supaya pengunjung yang hanya membaca
  // halaman pemasaran tidak ikut menanggung biaya render dan panggilan /readiness-nya.
  const [dashboardPernahDibuka, setDashboardPernahDibuka] = useState(route === "dashboard");
  useEffect(() => {
    if (route === "dashboard") setDashboardPernahDibuka(true);
  }, [route]);

  useEffect(() => {
    // Berpindah permukaan berarti berganti halaman, jadi posisi gulir dimulai dari atas -
    // tanpa ini dashboard terbuka di tengah-tengah, sejauh halaman landing tergulir tadi.
    window.scrollTo({ top: 0, behavior: "auto" });

    // Animasi masuk dijalankan ulang dengan tangan, bukan lewat `key` yang memasang ulang
    // komponennya: pemasangan ulang itulah yang tadinya menghapus hasil analisis. Melepas
    // kelasnya lalu membaca `offsetWidth` memaksa reflow, dan itu yang membuat browser
    // memperlakukan pemasangan kelas berikutnya sebagai animasi baru.
    const el = frame.current;
    if (!el) return;
    el.classList.remove("route--in");
    void el.offsetWidth;
    el.classList.add("route--in");
  }, [route, direction]);

  return (
    <div className="route route--in" ref={frame} data-dir={direction}>
      <div hidden={route !== "landing"}>
        <LandingScreen theme={theme} onToggleTheme={toggleTheme} />
      </div>
      {dashboardPernahDibuka && (
        <div hidden={route !== "dashboard"}>
          <DashboardScreen theme={theme} onToggleTheme={toggleTheme} />
        </div>
      )}
    </div>
  );
}
