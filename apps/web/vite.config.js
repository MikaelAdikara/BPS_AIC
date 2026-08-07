import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Port diambil dari env agar tidak bentrok dengan proses lain di mesin pengembang.
// Proxy dev-only: frontend memanggil /api/... relatif, sehingga kode yang sama berjalan
// di dev maupun di container tanpa URL backend yang di-hardcode.
export default defineConfig({
  plugins: [react()],
  server: {
    port: Number(process.env.PORT) || 5180,
    proxy: { "/api": process.env.API_URL || "http://127.0.0.1:8000" },
  },
  build: { outDir: "dist" },
});
