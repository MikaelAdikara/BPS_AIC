/** Klien API backend.
 *
 * URL relatif disengaja: kode yang sama berjalan di dev (lewat proxy Vite) dan di container
 * (di belakang reverse proxy) tanpa alamat backend yang di-hardcode.
 */

const TIMEOUT_MS = 60_000;

async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...options,
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      // Backend mengembalikan ErrorResponse berbahasa Indonesia (bagian 25.13). Pakai pesan
      // itu apa adanya — menggantinya dengan pesan generik justru menghilangkan saran
      // perbaikan yang sudah disiapkan backend.
      throw Object.assign(new Error(payload?.message ?? "Terjadi masalah pada sistem."), {
        suggestedAction: payload?.suggested_action,
        code: payload?.error_code,
      });
    }
    return payload;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("Analisis memakan waktu terlalu lama. Coba dengan data lebih sedikit.");
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  readiness: () => request("/api/v1/readiness"),
  models: () => request("/api/v1/models"),
  sample: () => request("/api/v1/demo/sample"),
  analyze: (reviews) =>
    request("/api/v1/analyze", { method: "POST", body: JSON.stringify({ reviews }) }),
};

/** Ubah teks tempelan menjadi RawReview. Satu baris = satu ulasan. */
export function parsePastedText(text) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length >= 3)
    .map((line, index) => ({
      review_id: `paste_${index + 1}`,
      text: line,
      category: "other",
      source: "manual_upload",
    }));
}
