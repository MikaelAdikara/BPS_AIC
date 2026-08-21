/** Uji pencocokan FAQ. Jalankan dari apps/web dengan `npm test`.
 *
 * Memakai test runner bawaan Node (`node --test`), bukan Vitest atau Jest. Alasannya satu:
 * menambah kerangka uji berikut turunannya demi satu berkas 150 baris akan menggemukkan
 * `npm install` yang harus dijalankan panitia saat mereproduksi proyek ini.
 *
 * Dua daftar di bawah adalah alasan angka AMBANG di faq-search.js bernilai seperti sekarang.
 * Kalau entri FAQ ditambah atau kata kuncinya diubah, jalankan berkas ini lagi: `npm test --
 * --test-reporter=spec` mencetak skor tiap baris, dan jurang antara dua daftar itu yang harus
 * tetap lebar.
 */

import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { FAQ } from "../content/faq.js";
import { cari } from "./faq-search.js";

/** [pertanyaan yang diketik pengguna, id entri yang seharusnya keluar] */
const HARUS_KENA = [
  ["ulasin ini sebenernya buat apa sih", "apa-itu"],
  ["fungsinya apa", "apa-itu"],
  ["ini aplikasi apaan", "apa-itu"],
  ["cara pakainya gimana", "cara-pakai"],
  ["gmn cara makainya", "cara-pakai"],
  ["langkah pertama ngapain", "cara-pakai"],
  ["formatnya harus csv ya", "format-data"],
  ["bisa upload excel gak", "format-data"],
  ["boleh pakai screenshot", "format-data"],
  ["bisa connect ke tokopedia", "marketplace"],
  ["ada integrasi shopee?", "marketplace"],
  ["minimal berapa ulasan", "berapa-ulasan"],
  ["maksimal berapa baris yang bisa diupload", "berapa-ulasan"],
  ["prosesnya lama gak", "berapa-lama"],
  ["butuh waktu berapa menit", "berapa-lama"],
  ["ini gratis?", "biaya"],
  ["harus daftar akun dulu ga", "biaya"],
  ["data saya disimpan gak", "privasi"],
  ["aman gak nomor telepon pelanggan saya", "privasi"],
  ["pakai model apa", "ai-apa"],
  ["ulasan alay dan typo kebaca?", "bahasa"],
  ["hasilnya akurat gak", "akurat"],
  ["apa yang belum bisa", "belum-bisa"],
  ["hasilnya bisa didownload pdf", "hasil-apa"],
  ["bedanya sama dashboard shopee apa", "beda-marketplace"],
  ["cocok buat umkm makanan?", "untuk-siapa"],
  ["kamu bot ya", "chatbot-ini"],
];

/** Pertanyaan yang JUJURNYA tidak ada jawabannya. Semuanya harus jatuh ke TIDAK_TAHU -
 *  daftar ini yang menjaga ambang tidak diturunkan diam-diam demi menaikkan cakupan. */
const HARUS_MELESET = [
  "resep rendang padang yang enak",
  "siapa presiden indonesia",
  "tolong buatkan saya kode python",
  "berapa ongkir jakarta surabaya",
  "cuaca besok gimana",
  "kapan bumi kiamat",
];

describe("cari()", () => {
  it("mengembalikan entri yang tepat untuk pertanyaan dalam cakupan", () => {
    const meleset = [];
    for (const [tanya, harapan] of HARUS_KENA) {
      const { entri, skor } = cari(tanya);
      if (entri?.id !== harapan) {
        meleset.push(`  "${tanya}" -> ${entri?.id ?? "TIDAK_TAHU"} (harap ${harapan}, skor ${skor.toFixed(2)})`);
      }
    }
    assert.equal(meleset.length, 0, `\n${meleset.join("\n")}\n`);
  });

  it("berkata tidak tahu untuk pertanyaan di luar cakupan", () => {
    const kelewat = [];
    for (const tanya of HARUS_MELESET) {
      const { entri, skor } = cari(tanya);
      if (entri) kelewat.push(`  "${tanya}" -> ${entri.id} (skor ${skor.toFixed(2)})`);
    }
    assert.equal(kelewat.length, 0, `\n${kelewat.join("\n")}\n`);
  });

  it("selalu memberi jalan keluar, terjawab maupun tidak", () => {
    for (const tanya of [...HARUS_KENA.map((p) => p[0]), ...HARUS_MELESET, "", "???"]) {
      const { usul } = cari(tanya);
      assert.ok(usul.length > 0, `tidak ada usulan untuk "${tanya}"`);
    }
  });
});

describe("basis pengetahuan", () => {
  it("id-nya unik", () => {
    const id = FAQ.map((e) => e.id);
    assert.equal(new Set(id).size, id.length);
  });

  it("tiap usul menunjuk entri yang benar-benar ada", () => {
    const id = new Set(FAQ.map((e) => e.id));
    for (const entri of FAQ) {
      for (const tujuan of entri.usul ?? []) {
        assert.ok(id.has(tujuan), `${entri.id} menunjuk "${tujuan}" yang tidak ada`);
      }
    }
  });

  it("tiap entri punya judul, kata kunci, dan isi", () => {
    for (const entri of FAQ) {
      assert.ok(entri.q.length > 5, entri.id);
      assert.ok(entri.kata.split(" ").length >= 5, `${entri.id} kata kuncinya terlalu sedikit`);
      assert.ok(entri.a.length > 0, entri.id);
    }
  });
});
