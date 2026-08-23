/** "Buka Hitungannya" - fitur tanda tangan Ulasin, didemokan di halaman depan dengan data asli.
 *
 * Pembaca memilih satu kartu aksi, lalu melihat rantai lengkap yang menghasilkan skornya:
 * klausa mentah yang dibaca model -> agregat -> komponen rumus -> aritmetikanya. Angka-angka di
 * sini disalin apa adanya dari jejak perhitungan (`POST /api/v1/trace`) analisis sungguhan
 * atas 66 ulasan Shopee asli pada 23 Agustus 2026 - yang sama dengan studi kasus di bawah.
 * Tidak ada yang dibulatkan supaya "pas"; pembaca boleh mengalikannya sendiri dan menemukan
 * angka yang sama.
 */

import { useState } from "react";

const RUMUS = "skor = frekuensi × keparahan × (1 + 0,3 × tren + 0,2 × selisih_baseline) × 100";

const KARTU = [
  {
    id: "ACT-001",
    aspek: "kualitas produk",
    judul: "Periksa kualitas produk pada batch terbaru",
    urgensi: "tinggi",
    klausa: [
      "yang hitam jahitan tidak rapi kerut di bagian leher",
      "bahan: ada robek",
      "gua cht tidak di bales barang rusak bolong - niat jualan gasi",
      "jelek banget pesan warna lain yang dtng warna lain",
      "awalnya mau batalin pesanan karena takut lama",
    ],
    klausaTotal: 77,
    klausaNegatif: 13,
    agregat: { sebutan: 77, keluhan: 13, positif: 42, netral: 22, tren: "meningkat" },
    faktor: [
      { k: "Frekuensi", v: "0,197", dari: "13 ulasan berkeluhan ÷ 66 ulasan" },
      { k: "Keparahan", v: "1,0", dari: "keparahan tipikal 'tinggi', dari rating ulasan berkeluhan" },
      { k: "Tren 30 hari", v: "1,0", dari: "keluhan meningkat dalam 30 hari terakhir" },
      { k: "Selisih baseline", v: "0,84", dari: "16,8 poin di atas rata-rata kategori fesyen, ÷ 20" },
    ],
    hitung: "0,197 × 1,0 × (1 + 0,3×1,0 + 0,2×0,84) × 100",
    inti: "0,197",
    pengubah: "1,468",
    skor: "28,92",
  },
  {
    id: "ACT-002",
    aspek: "kesesuaian deskripsi",
    judul: "Perbaiki keterangan kesesuaian dengan deskripsi",
    urgensi: "tinggi",
    klausa: [
      "kecewa sih sama toko ini order nya yang warna coklat yang dateng malah warna hitam",
      "barang nya robek tidak sesuai desain",
      "pesan warna lain yang dtng warna lain",
      "bahan baju warna coklatnya halus - halo kak kenapa chat saya tidak dibalas",
    ],
    klausaTotal: 40,
    klausaNegatif: 7,
    agregat: { sebutan: 40, keluhan: 7, positif: 24, netral: 9, tren: "meningkat" },
    faktor: [
      { k: "Frekuensi", v: "0,106", dari: "7 ulasan berkeluhan ÷ 66 ulasan" },
      { k: "Keparahan", v: "1,0", dari: "keparahan tipikal 'tinggi'" },
      { k: "Tren 30 hari", v: "1,0", dari: "keluhan meningkat dalam 30 hari terakhir" },
      { k: "Selisih baseline", v: "0,44", dari: "8,75 poin di atas rata-rata kategori, ÷ 20" },
    ],
    hitung: "0,106 × 1,0 × (1 + 0,3×1,0 + 0,2×0,44) × 100",
    inti: "0,106",
    pengubah: "1,388",
    skor: "14,72",
  },
];

export function Proof({ onStart }) {
  const [aktif, setAktif] = useState(0);
  const [buka, setBuka] = useState(false);
  const k = KARTU[aktif];

  return (
    <section className="bukti" id="bukti" aria-labelledby="bukti-judul">
      <div className="section-head">
        <span className="bukti__eyebrow">Fitur tanda tangan</span>
        <h2 id="bukti-judul">
          Buka Hitungannya. <span className="soft">Setiap angka bisa Anda hitung ulang.</span>
        </h2>
        <p>
          Alat lain meminta Anda percaya. Ulasin meminta Anda memeriksa: dari kalimat mentah yang
          dibaca model sampai rumus yang menghasilkan skor - semuanya terbuka, di tiap kartu.
          Coba di bawah ini, dengan angka dari ulasan sungguhan.
        </p>
      </div>

      <div className="bukti__panggung">
        <div className="bukti__kartu-kolom">
          {KARTU.map((x, i) => (
            <button
              type="button"
              key={x.id}
              className={`bukti__kartu bukti__kartu--${x.urgensi} ${i === aktif ? "is-aktif" : ""}`}
              onClick={() => {
                setAktif(i);
                setBuka(false);
              }}
              aria-pressed={i === aktif}
            >
              <span className="bukti__rank">{i + 1}</span>
              <span className="bukti__badge">{x.urgensi}</span>
              <b>{x.judul}</b>
              <span className="bukti__sub">
                {x.agregat.keluhan} dari 66 ulasan · skor {x.skor}
              </span>
            </button>
          ))}
          <button type="button" className="btn btn--primary bukti__tombol" onClick={() => setBuka(true)}>
            Bagaimana angka ini dihitung? →
          </button>
        </div>

        <div className={`bukti__jejak ${buka ? "is-buka" : ""}`} aria-live="polite">
          {!buka ? (
            <div className="bukti__tunggu">
              <p>
                Pilih kartu, lalu tekan <b>"Bagaimana angka ini dihitung?"</b> - persis tombol yang ada di
                setiap kartu di dalam aplikasi.
              </p>
            </div>
          ) : (
            <>
              <div className="bukti__langkah" style={{ "--d": "0ms" }}>
                <span className="bukti__no">1</span>
                <div>
                  <h4>Klausa yang terbaca model</h4>
                  <p className="bukti__ket">
                    Klasifikasi berjalan per klausa, bukan per ulasan. {k.klausaNegatif} klausa keluhan dari {k.klausaTotal} klausa
                    yang menyebut {k.aspek} - inilah yang memicu kartunya, apa adanya:
                  </p>
                  <ul className="bukti__klausa">
                    {k.klausa.map((c) => (
                      <li key={c}>
                        <span className="bukti__tag">keluhan</span>
                        {c}
                      </li>
                    ))}
                    <li className="bukti__lagi">+ {k.klausaNegatif - k.klausa.length} klausa keluhan lain, semuanya tampil di aplikasi</li>
                  </ul>
                </div>
              </div>

              <div className="bukti__langkah" style={{ "--d": "260ms" }}>
                <span className="bukti__no">2</span>
                <div>
                  <h4>Dijumlahkan menjadi agregat</h4>
                  <div className="bukti__agregat">
                    <span><b>{k.agregat.sebutan}</b> sebutan</span>
                    <span><b>{k.agregat.keluhan}</b> berisi keluhan</span>
                    <span><b>{k.agregat.positif}</b> positif</span>
                    <span><b>{k.agregat.netral}</b> netral</span>
                    <span>tren <b>{k.agregat.tren}</b></span>
                  </div>
                </div>
              </div>

              <div className="bukti__langkah" style={{ "--d": "520ms" }}>
                <span className="bukti__no">3</span>
                <div>
                  <h4>Komponen rumus prioritas</h4>
                  <code className="bukti__rumus">{RUMUS}</code>
                  <table className="bukti__tabel">
                    <thead>
                      <tr>
                        <th>Komponen</th>
                        <th>Nilai</th>
                        <th>Dari mana</th>
                      </tr>
                    </thead>
                    <tbody>
                      {k.faktor.map((f) => (
                        <tr key={f.k}>
                          <td>{f.k}</td>
                          <td className="bukti__nilai">{f.v}</td>
                          <td>{f.dari}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bukti__langkah bukti__langkah--akhir" style={{ "--d": "780ms" }}>
                <span className="bukti__no">4</span>
                <div>
                  <h4>Kalikan sendiri</h4>
                  <p className="bukti__hitung">
                    <code>{k.hitung}</code>
                    <span className="bukti__sama">=</span>
                    <b className="bukti__skor">{k.skor}</b>
                  </p>
                  <p className="bukti__ket">
                    inti {k.inti} × pengubah {k.pengubah} × 100 - angka yang sama dengan yang tertera di kartu.
                    Keyakinan model <em>dilaporkan</em> di jejak tetapi <em>tidak dikalikan</em>, karena belum terkalibrasi.
                  </p>
                </div>
              </div>

              <div className="bukti__cta">
                <button type="button" className="btn btn--outline" onClick={onStart}>
                  Coba pada ulasan Anda sendiri ›
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
