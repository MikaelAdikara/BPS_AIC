/** Penjaga sinkronisasi daftar aspek, plus pemeriksaan perilaku profil.
 *
 * Berkas ini ada terutama untuk satu hal: `profile.js` menyalin daftar aspek per kategori dari
 * `configs/taxonomy.yaml`, dan salinan tanpa penjaga akan menyimpang. Menyimpangnya pun senyap
 * - tidak ada yang gagal, pengguna toko makanan cuma tidak pernah ditawari "rasa" sebagai
 * fokus. Tes di bawah membaca config aslinya lalu membandingkan kategori per kategori.
 *
 * YAML-nya diurai dengan regex, bukan dengan pustaka. Struktur yang dibaca cuma dua bentuk
 * (`- id:` diikuti `scope:` dan `active_for: [...]`) dan `apps/web` tidak punya dependensi
 * runtime selain React - menambah parser YAML demi satu tes bukan pertukaran yang sepadan.
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import test from "node:test";

import { MAX_FOKUS, aspekUntuk, inisial, pertanyaanUntuk, pilihFokus, sapaan, ubahProfil, PROFIL_AWAL } from "./profile.js";

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

test("daftar aspek per kategori sama persis dengan configs/taxonomy.yaml", () => {
  for (const [kategori, aspek] of Object.entries(bacaTaksonomi())) {
    assert.deepEqual(
      [...aspekUntuk(kategori)].sort(),
      [...aspek].sort(),
      `aspek untuk kategori "${kategori}" menyimpang dari taxonomy.yaml`
    );
  }
});

test("rasa hanya ditawarkan pada makanan & minuman", () => {
  assert.ok(aspekUntuk("food_beverage").includes("rasa_kualitas_makanan"));
  assert.ok(!aspekUntuk("fashion").includes("rasa_kualitas_makanan"));
  assert.ok(!aspekUntuk("electronics").includes("rasa_kualitas_makanan"));
});

test("berganti kategori membuang fokus yang tidak lagi berlaku", () => {
  const fesyen = { ...PROFIL_AWAL, category: "fashion", focus: ["keaslian", "pengiriman"] };
  const makanan = ubahProfil(fesyen, { category: "food_beverage" });
  assert.deepEqual(makanan.focus, ["pengiriman"]);
});

test("berganti isian lain tidak menyentuh fokus", () => {
  const awal = { ...PROFIL_AWAL, focus: ["keaslian"] };
  assert.deepEqual(ubahProfil(awal, { store: "Toko Bu Rina" }).focus, ["keaslian"]);
});

test("fokus berhenti di batas, dan mencabut pilihan selalu boleh", () => {
  let p = { ...PROFIL_AWAL };
  for (const a of ["kemasan", "pengiriman", "harga_value"]) p = pilihFokus(p, a);
  assert.equal(p.focus.length, MAX_FOKUS);

  const penuh = pilihFokus(p, "kualitas_produk");
  assert.deepEqual(penuh.focus, p.focus, "penambahan keempat harus diabaikan");

  assert.deepEqual(pilihFokus(p, "pengiriman").focus, ["kemasan", "harga_value"]);
});

test("inisial melewati kata umum nama toko", () => {
  assert.equal(inisial("Toko Bu Rina"), "BR");
  assert.equal(inisial("CV Karya Mandiri"), "KM");
  assert.equal(inisial("Rina"), "R");
  assert.equal(inisial("  "), "OU");
  assert.equal(inisial(""), "OU");
  // Semua katanya ada di daftar buang - penyaringannya diabaikan alih-alih menghasilkan "".
  assert.equal(inisial("Toko Store"), "TS");
});

test("sapaan memotong nama yang kepanjangan", () => {
  assert.equal(sapaan(""), "Halo, Owner UMKM!");
  assert.equal(sapaan("Toko Bu Rina"), "Halo, Toko Bu Rina!");
  assert.ok(sapaan("A".repeat(60)).endsWith("…!"));
});

test("pertanyaan yang disarankan selalu empat dan tanpa duplikat", () => {
  const kosong = pertanyaanUntuk([]);
  assert.equal(kosong.length, 3, "tanpa fokus, hanya pertanyaan umum yang ditawarkan");

  const terfokus = pertanyaanUntuk(["kemasan", "pengiriman", "rasa_kualitas_makanan"]);
  assert.equal(terfokus.length, 4);
  assert.equal(new Set(terfokus).size, 4);
  assert.ok(terfokus[0].includes("kemasan"));
});
