import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Port diambil dari env agar tidak bentrok dengan proses lain di mesin pengembang.
//
// `host: true` WAJIB, bukan preferensi. Tanpanya Vite hanya mengikat ke [::1] (IPv6 loopback),
// sehingga http://127.0.0.1:PORT gagal total dan halaman tidak muncul bagi siapa pun yang
// browser atau sistemnya me-resolve localhost ke IPv4. Ini juga syarat agar server terjangkau
// dari luar container pada Fase 9.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: Number(process.env.PORT) || 5180,
    proxy: { "/api": process.env.API_URL || "http://127.0.0.1:8000" },
  },
  preview: { host: true, port: Number(process.env.PORT) || 3000 },
  build: { outDir: "dist" },
});
