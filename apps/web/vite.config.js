import { defineConfig, normalizePath } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
export default defineConfig({
  plugins: [
    {
      name: "reload-context-providers",
      enforce: "pre",
      handleHotUpdate({ file, server }) {
        if (
          /\/src\/(?:api\/(?:auth|workspace)\.tsx|lib\/(?:i18n|theme)\.tsx|lib\/messages[^/]*\.js)$/.test(
            normalizePath(file),
          )
        ) {
          server.ws.send({ type: "full-reload" });
          return [];
        }
      },
    },
    react(),
    tailwindcss(),
  ],
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
