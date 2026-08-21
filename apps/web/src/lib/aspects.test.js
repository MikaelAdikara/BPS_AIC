/** Penjaga sinkronisasi daftar aspek, plus perilaku pertanyaan yang disarankan.
 *
 * Berkas ini ada terutama untuk satu hal: `aspects.js` menyalin daftar aspek per kategori dari
 * `configs/taxonomy.yaml`, dan salinan tanpa penjaga akan menyimpang. Menyimpangnya pun senyap
 * - tidak ada yang gagal, hanya bagian "belum disebut sama sekali" di laporan yang diam-diam
 * berhenti menyebutkan satu aspek. Tes di bawah membaca config aslinya lalu membandingkan
 * kategori per kategori.
 *
 * YAML-nya diurai dengan regex, bukan dengan pustaka. Struktur yang dibaca cuma dua bentuk
 * (`- id:` diikuti `scope:` dan `active_for: [...]`) dan `apps/web` tidak punya dependensi
 * runtime selain React - menambah parser YAML demi satu tes bukan pertukaran yang sepadan.
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import test from "node:test";

import { aspekUntuk, pertanyaanUntuk } from "./aspects.js";

const TAXONOMY = fileURLToPath(new URL("../../../../configs/taxonomy.yaml", import.meta.url));

function bacaTaksonomi() {
  const raw = readFileSync(TAXONOMY, "utf8");
  const categories = raw.match(/^categories:\s*\[([^\]]+)\]/m)[1].split(",").map((c) => c.trim());

  const perKategori = Object.fromEntries(categories.map((c) => [c, []]));
  // Tiap blok aspek dimulai "  - id:" dan berakhir tepat sebelum blok berikutnya.
  for (const blok of raw.split(/^ {2}- id: /m).slice(1)) {
    const id = blok.split("\n")[0].trim();
    const scope = blok.match(/^ {4}scope:\s*(\S+)/m)[1];
    const aktif = blok.match(/^ {4}active_for:\s*\[([^\]]+)\]/m);
    const untuk =
      scope === "category_specific" ? aktif[1].split(",").map((c) => c.trim()) : categories;
    for (const c of untuk) perKategori[c].push(id);
  }
  return perKategori;
}

const agg = (aspect, negative_count) => ({ aspect, negative_count });

test("daftar aspek per kategori sama persis dengan configs/taxonomy.yaml", () => {
  for (const [kategori, aspek] of Object.entries(bacaTaksonomi())) {
    assert.deepEqual(
      [...aspekUntuk(kategori)].sort(),
      [...aspek].sort(),
      `aspek untuk kategori "${kategori}" menyimpang dari taxonomy.yaml`
    );
  }
});

test("rasa hanya berlaku pada makanan & minuman", () => {
  assert.ok(aspekUntuk("food_beverage").includes("rasa_kualitas_makanan"));
  assert.ok(!aspekUntuk("fashion").includes("rasa_kualitas_makanan"));
  assert.ok(!aspekUntuk("electronics").includes("rasa_kualitas_makanan"));
});

test("kategori yang tidak dikenal jatuh ke daftar bawaan, bukan larik kosong", () => {
  assert.deepEqual(aspekUntuk("entah_apa"), aspekUntuk("other"));
});

test("tanpa keluhan, hanya pertanyaan umum yang ditawarkan", () => {
  assert.equal(pertanyaanUntuk([]).length, 3);
  assert.equal(pertanyaanUntuk([agg("kemasan", 0)]).length, 3);
});

test("pertanyaan disusun menurut aspek yang paling banyak dikeluhkan", () => {
  const saran = pertanyaanUntuk([
    agg("kemasan", 2),
    agg("ukuran_varian", 9),
    agg("pengiriman", 5),
  ]);

  assert.ok(saran[0].includes("ukuran"));
  assert.ok(saran[1].includes("pengiriman"));
  assert.ok(saran[2].includes("kemasan"));
});

test("saran berhenti di empat dan tidak pernah duplikat", () => {
  const saran = pertanyaanUntuk([
    agg("kemasan", 9),
    agg("ukuran_varian", 8),
    agg("pengiriman", 7),
    agg("harga_value", 6),
    agg("keaslian", 5),
  ]);

  assert.equal(saran.length, 4);
  assert.equal(new Set(saran).size, 4);
});

test("aspek yang tidak punya pertanyaan tidak menyisakan lubang", () => {
  const saran = pertanyaanUntuk([agg("aspek_yang_tidak_ada", 9), agg("kemasan", 3)]);

  assert.ok(saran.every(Boolean));
  assert.ok(saran[0].includes("kemasan"));
});
