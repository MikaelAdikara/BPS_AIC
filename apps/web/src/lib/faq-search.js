/** Pencocokan pertanyaan bebas ke entri FAQ.
 *
 * Ini pencarian leksikal di sisi browser, BUKAN model bahasa. Pilihan itu disengaja dan ada
 * tiga alasannya:
 *
 *   1. Kejujuran. Produk ini menolak menyebut sesuatu "AI" kalau yang bekerja bukan model.
 *      Kotak FAQ yang mengaku kotak FAQ lebih baik daripada kotak FAQ yang berlagak asisten.
 *   2. Ketersediaan. Halaman pemasaran harus tetap menjawab meski backend sedang mati -
 *      justru saat itulah orang paling butuh tahu ini aplikasi apa.
 *   3. Biaya. Menyalakan model bahasa demi menjawab "ini gratis?" tidak sepadan, dan lapisan
 *      AI di produk ini sudah dialokasikan penuh untuk membaca ulasan pengguna.
 *
 * Konsekuensinya diterima apa adanya: pertanyaan yang jauh dari daftar TIDAK akan terjawab.
 * Jalur itu dibuat eksplisit lewat `TIDAK_TAHU` - sama seperti RET-01 di backend, yang lebih
 * memilih berkata tidak tahu daripada menyusun jawaban yang terdengar meyakinkan.
 */

import { FAQ } from "../content/faq.js";

// Kata yang muncul di hampir semua pertanyaan sehingga tidak membedakan apa pun. IDF sebetulnya
// sudah menekan bobotnya sendiri; daftar ini membuangnya lebih awal supaya penyebut skor tidak
// digelembungkan kata yang tak mungkin cocok ke mana-mana.
const HENTI = new Set(
  ("yang dan atau itu ini di ke dari dengan pada adalah ada apakah saya aku kita kami nya " +
    "sih dong deh ya kah gak nggak ga engga juga saja aja kalau jika akan lagi lah pun " +
    "the a an is it")
    .split(" ")
);

// TIDAK dibuang meski sering muncul: "belum", "bisa", "harus", "apa", "buat", "untuk". Kata-kata
// itu sempat masuk daftar henti dan pertanyaan "apa yang belum bisa" langsung menjadi kosong -
// padahal "belum" justru inti pertanyaannya. IDF di bawah sudah menekan kata yang benar-benar
// merata sendiri; daftar henti dipakai hanya untuk kata yang tak pernah membawa arti.

/** Ragam tulis yang harus dianggap satu kata. Kunci ditulis sependek yang benar-benar dipakai
 *  orang di kolom pencarian - "gmn", "brp", "hrg" bukan tebakan, itu bentuk yang lazim. */
const ALIAS = {
  gmn: "bagaimana", gimana: "bagaimana", gmana: "bagaimana", bgmn: "bagaimana",
  sebenernya: "sebenarnya", sebenerbya: "sebenarnya", emang: "sebenarnya",
  // "pakai" sengaja TIDAK dijadikan tujuan alias. Ia kata kerja yang menempel di mana-mana
  // ("pakai model apa", "bisa pakai screenshot", "cara pakainya"), jadi menyatukan seluruh
  // ragamnya ke satu kata justru menjadikannya magnet yang menarik pertanyaan ke entri
  // "cara-pakai" berapa pun jauh topik aslinya.
  caranya: "cara", pakenya: "cara", makainya: "cara",
  brp: "berapa", brapa: "berapa", hrg: "harga", hrga: "harga", biayanya: "biaya",
  bayarnya: "bayar", gratisan: "gratis", langganannya: "langganan",
  knp: "kenapa", kenapa: "kenapa", ngapa: "kenapa", mengapa: "kenapa",
  dtng: "data", datanya: "data", filenya: "file", berkasnya: "berkas",
  ss: "screenshot", tangkapan: "screenshot", sc: "screenshot", ocr: "screenshot",
  tokped: "tokopedia", shope: "shopee", tiktokshop: "tiktok", medsos: "marketplace",
  akurasinya: "akurat", akurasi: "akurat", bener: "benar", bnr: "benar",
  aman_gak: "aman", keamanan: "aman", privasinya: "privasi",
  ulasannya: "ulasan", review: "ulasan", reviews: "ulasan", komentar: "ulasan",
  testimoni: "ulasan", rating: "ulasan", feedback: "ulasan",
  hasilnya: "hasil", outputnya: "output", laporannya: "laporan",
  fungsinya: "fungsi", gunanya: "guna", kegunaan: "guna", ngapain: "fungsi",
  bot: "chatbot", robot: "chatbot", ai: "ai", llm: "ai", chatgpt: "ai",
  umkm: "umkm", ukm: "umkm", olshop: "toko", online: "toko",
};

// Akhiran yang benar-benar aman dilepas untuk kosakata di berkas ini. Awalan sengaja TIDAK
// disentuh: "berapa" akan kehilangan "ber"-nya dan bertemu "apa", dan kesalahan semacam itu
// merusak lebih banyak daripada yang diperbaikinya.
const AKHIRAN = ["nya", "kah", "lah", "pun"];

function pangkas(kata) {
  for (const akhir of AKHIRAN) {
    if (kata.length > akhir.length + 3 && kata.endsWith(akhir)) {
      return kata.slice(0, -akhir.length);
    }
  }
  return kata;
}

/** Ubah kalimat bebas jadi kumpulan kata pencarian. Bentuk asli dan bentuk terpangkasnya
 *  sama-sama disimpan - kalau salah satunya cocok, itu sudah cukup. */
export function pecah(teks) {
  const keluar = new Set();
  for (const mentah of String(teks).toLowerCase().replace(/[^a-z0-9]+/g, " ").split(" ")) {
    if (mentah.length < 2 || HENTI.has(mentah)) continue;
    const kata = ALIAS[mentah] ?? mentah;
    keluar.add(kata);
    const pendek = pangkas(kata);
    if (pendek !== kata && !HENTI.has(pendek)) keluar.add(pendek);
  }
  return keluar;
}

/** Indeks dibangun sekali saat modul dimuat. Isinya belasan entri, jadi biayanya tak terukur. */
const INDEKS = FAQ.map((entri) => ({
  entri,
  // Judul dan kata kunci menyatakan TOPIK entri; badan jawaban hanya menyinggungnya. Karena
  // itu keduanya dipisah, dan yang kedua dihargai lebih rendah saat penilaian.
  judul: pecah(`${entri.q} ${entri.kata}`),
  badan: pecah(entri.a.join(" ")),
}));

/** IDF: kata yang muncul di banyak entri hampir tak berguna untuk membedakan. Tanpa ini,
 *  "ulasan" - yang ada di hampir seluruh entri - akan menarik pertanyaan apa pun ke entri
 *  mana pun yang kebetulan paling panjang. */
const IDF = (() => {
  const hitung = new Map();
  for (const { judul, badan } of INDEKS) {
    for (const kata of new Set([...judul, ...badan])) {
      hitung.set(kata, (hitung.get(kata) ?? 0) + 1);
    }
  }
  const peta = new Map();
  for (const [kata, n] of hitung) peta.set(kata, Math.log(1 + INDEKS.length / n));
  return peta;
})();

// Kata yang tak dikenal indeks sama sekali - nama produk pesaing, topik yang memang di luar
// cakupan, salah ketik yang tak tertangkap alias - diberi bobot LEBIH BESAR daripada kata
// paling langka sekalipun, dan hanya menambah penyebut. Efeknya disengaja: makin banyak kata
// asing di sebuah pertanyaan, makin dalam skornya tertarik ke bawah ambang. Tanpa pengali ini
// "cuaca besok gimana" mencetak tepat 0,33 - satu kata "gimana" yang kebetulan ada di judul
// sudah cukup mengangkatnya - dan pertanyaan yang jelas-jelas di luar cakupan pun terjawab.
const IDF_ASING = Math.log(1 + INDEKS.length) * 1.6;

// Ambang lolos. Angkanya diukur, bukan dikira-kira: pada dua daftar di faq-search.test.js,
// 27 pertanyaan yang harus terjawab seluruhnya mencetak >= 0,46 dan 6 pertanyaan di luar
// cakupan seluruhnya <= 0,25. Ambangnya ditaruh di dalam jurang itu, tidak dipepetkan ke
// salah satu sisi - kalau entri baru ditambahkan, jalankan ujinya lagi dan pastikan jurangnya
// masih ada sebelum angka ini disentuh.
const AMBANG = 0.33;

// Selisih setipis ini antara juara satu dan dua berarti pertanyaannya memang menyentuh dua
// topik. Menjawab satu lalu diam akan terasa seperti salah dengar, jadi yang kedua ikut
// ditawarkan sebagai usulan.
const SELISIH_TIPIS = 0.12;

function nilai(kata_kunci, { judul, badan }) {
  let dapat = 0;
  let total = 0;
  for (const kata of kata_kunci) {
    const bobot = IDF.get(kata) ?? IDF_ASING;
    total += bobot;
    if (judul.has(kata)) dapat += bobot;
    else if (badan.has(kata)) dapat += bobot * 0.55;
  }
  return total === 0 ? 0 : dapat / total;
}

export const TIDAK_TAHU = "TIDAK_TAHU";

/**
 * Cari jawaban untuk satu pertanyaan bebas.
 *
 * Mengembalikan `{ entri, skor, usul }`, atau `{ entri: null, usul }` bila tidak ada yang
 * lolos ambang - dengan `usul` berisi entri terdekat sebagai jalan keluar, supaya pengguna
 * tidak dibiarkan berhadapan dengan jalan buntu.
 */
export function cari(pertanyaan) {
  const kata_kunci = pecah(pertanyaan);
  if (kata_kunci.size === 0) {
    return { entri: null, skor: 0, usul: FAQ.slice(0, 3) };
  }

  const peringkat = INDEKS
    .map((baris) => ({ entri: baris.entri, skor: nilai(kata_kunci, baris) }))
    .sort((a, b) => b.skor - a.skor);

  const [juara, kedua] = peringkat;
  if (juara.skor < AMBANG) {
    return {
      entri: null,
      skor: juara.skor,
      usul: peringkat.slice(0, 3).map((p) => p.entri),
    };
  }

  // Usulan lanjutan berasal dari entri itu sendiri (`usul`), bukan dari peringkat - penulis
  // entri tahu pertanyaan mana yang wajar menyusul, dan kemiripan kata tidak tahu itu.
  const lanjutan = (juara.entri.usul ?? [])
    .map((id) => FAQ.find((e) => e.id === id))
    .filter(Boolean);
  if (kedua && juara.skor - kedua.skor < SELISIH_TIPIS && !lanjutan.includes(kedua.entri)) {
    lanjutan.unshift(kedua.entri);
  }

  return { entri: juara.entri, skor: juara.skor, usul: lanjutan.slice(0, 3) };
}
