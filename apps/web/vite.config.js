import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": "/src",
    },
  },
  server: {
    host: true,
    port: Number(process.env.PORT) || 5180,
    proxy: { "/api": process.env.API_URL || "http://127.0.0.1:8000" },
  },
  preview: { host: true, port: Number(process.env.PORT) || 3000 },
  build: { outDir: "dist" },
});
