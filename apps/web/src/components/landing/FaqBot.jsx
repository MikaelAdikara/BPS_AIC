/** Kotak FAQ mengambang di halaman pemasaran.
 *
 * Yang dijawabnya pertanyaan tentang PRODUK - ini aplikasi apa, cara pakainya bagaimana, data
 * saya disimpan atau tidak. Bukan pertanyaan tentang ulasan pengguna; itu pekerjaan tab Tanya
 * Jawab di dalam dashboard, yang memang menjalankan model dan menyertakan kutipan.
 *
 * Ia TIDAK menebak. Basis pengetahuannya 39 entri di content/faq.js, dan pertanyaan yang tak
 * ada padanannya dijawab apa adanya - lengkap dengan topik terdekat sebagai jalan keluar.
 * Menebak jawaban yang terdengar masuk akal justru pola yang paling merusak kepercayaan.
 *
 * Empat alasan diam dibedakan, masing-masing dengan kalimatnya sendiri (lihat `BALASAN`):
 * pertanyaannya di luar topik, topiknya benar tetapi jawabannya belum ditulis, yang diketik
 * bukan pertanyaan, atau yang diketik berupa perintah alih-alih pertanyaan. Menyodorkan tiga
 * topik terdekat kepada penanya cuaca terasa seperti tidak menyimak.
 *
 * Kotak ini TIDAK dipasang di dashboard. Dua kolom percakapan di satu produk, yang satu
 * menjawab dari daftar dan yang lain dari model, adalah cara tercepat membuat pengguna salah
 * paham soal mana yang sedang bekerja.
 */

import { useEffect, useId, useRef, useState } from "react";

import { FAQ, PEMBUKA } from "../../content/faq.js";
import { cari, JENIS } from "../../lib/faq-search.js";
import { goTo } from "../../lib/hooks.js";
import { BotMark } from "../Brand.jsx";

// Jeda sebelum jawaban muncul. Pencocokannya sendiri selesai di bawah satu milidetik, jadi ini
// murni soal keterbacaan: gelembung yang muncul di frame yang sama dengan pertanyaannya terbaca
// sebagai satu blok teks, bukan sebagai jawaban atas sesuatu. Sependek ini juga tidak sempat
// terasa sebagai menunggu.
const JEDA_MS = 380;

const sapaan = {
  id: "salam",
  peran: "bot",
  teks: [
    "Halo! Ada yang ingin ditanyakan soal Ulasin?",
    "Ketik pertanyaan Anda, atau pilih salah satu di bawah ini.",
  ],
  usul: PEMBUKA.map((id) => FAQ.find((e) => e.id === id)).filter(Boolean),
};

/* Balasan saat pertanyaannya tidak dijawab, satu per alasan. Dibedakan dengan sengaja:
 * menyodorkan tiga topik terdekat kepada penanya cuaca terasa seperti tidak menyimak, dan
 * membalas ketukan asal dengan "belum ada jawaban tertulis" terdengar seolah pertanyaannya
 * wajar padahal tidak ada pertanyaan sama sekali. */
const BALASAN = {
  [JENIS.belumAda]: [
    "Belum ada jawaban tertulis untuk pertanyaan itu, jadi saya tidak akan menebak.",
    "Yang paling dekat ada di bawah ini. Kalau tidak ada yang cocok, jawabannya mungkin ada di README repositori proyek.",
  ],
  [JENIS.diluarTopik]: [
    "Sepertinya itu di luar urusan saya - saya hanya bisa menjawab soal Ulasin: cara pakainya, hasilnya, datanya, dan biayanya.",
    "Beberapa yang sering ditanyakan:",
  ],
  [JENIS.takJelas]: [
    "Maaf, saya belum menangkap maksudnya. Coba tulis ulang dengan kalimat biasa, misalnya “cara pakainya gimana” atau “data saya disimpan tidak”.",
  ],
  [JENIS.perintah]: [
    "Saya membaca yang Anda ketik sebagai pertanyaan, bukan sebagai perintah - dan saya memang tidak punya apa pun untuk dibocorkan: kotak ini hanya mencocokkan pertanyaan ke daftar jawaban yang sudah ditulis.",
    "Kalau ada yang ingin ditanyakan soal produknya, silakan:",
  ],
};

function Aksi({ aksi, onTutup }) {
  if (aksi.ke === "dashboard") {
    return (
      <button
        type="button"
        className="btn btn--primary faqbot__aksi"
        onClick={() => {
          onTutup();
          goTo("dashboard");
        }}
      >
        {aksi.label} ›
      </button>
    );
  }
  return (
    <a className="btn btn--outline faqbot__aksi" href={aksi.ke} onClick={onTutup}>
      {aksi.label}
    </a>
  );
}

function Gelembung({ pesan, onPilih, onTutup }) {
  if (pesan.peran === "user") {
    return <p className="faqbot__bubble faqbot__bubble--user">{pesan.teks}</p>;
  }

  return (
    <div className="faqbot__baris">
      <BotMark size={24} className="faqbot__ava" />
      <div className="faqbot__bubble faqbot__bubble--bot">
        {pesan.entri && <b className="faqbot__judul">{pesan.entri.q}</b>}
        {(pesan.entri?.a ?? pesan.teks).map((paragraf, i) => (
          <p key={i}>{paragraf}</p>
        ))}
        {pesan.entri?.aksi && <Aksi aksi={pesan.entri.aksi} onTutup={onTutup} />}
        {pesan.usul?.length > 0 && (
          <div className="faqbot__usul">
            <span className="faqbot__usul-label">
              {pesan.entri ? "Lanjut ke" : "Yang bisa saya jawab"}
            </span>
            {pesan.usul.map((entri) => (
              <button
                key={entri.id}
                type="button"
                className="faqbot__chip"
                onClick={() => onPilih(entri)}
              >
                {entri.q}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function FaqBot() {
  const [buka, setBuka] = useState(false);
  const [pesan, setPesan] = useState([sapaan]);
  const [ketikan, setKetikan] = useState("");
  const [menunggu, setMenunggu] = useState(false);

  const panel = useRef(null);
  const kolom = useRef(null);
  const utas = useRef(null);
  const nomor = useRef(0);
  const judulId = useId();

  // Gulir sampai PUNCAK pesan terbaru menempel di atas kolom percakapan - bukan sampai dasar
  // seperti kebanyakan kotak obrolan.
  //
  // Bedanya terasa pada jawaban panjang. Menggulir ke dasar menaruh pengguna di kalimat
  // penutup, dan ia harus menggulir balik ke atas untuk membaca jawaban yang baru saja
  // dimintanya. Jawaban pendek tidak dirugikan: posisi gulirnya toh sudah terjepit di dasar,
  // dan browser memangkas kelebihannya sendiri.
  //
  // Dua hal yang sengaja TIDAK dipakai di sini, keduanya karena sudah gagal saat diuji:
  //
  //   `behavior: "smooth"` - pada sebagian mesin ia diam saja tanpa error, dan gulirannya
  //   tidak pernah terjadi sama sekali. Posisi gulir adalah syarat fungsi, bukan hiasan, jadi
  //   ia tidak boleh bergantung pada jalur yang bisa mangkir tanpa suara. Gerak yang menandai
  //   "ada yang baru" dipindahkan ke animasi masuk gelembungnya, yang tidak menentukan apa
  //   pun kalau ia tidak jalan.
  //
  //   `getBoundingClientRect()` - gelembungnya sedang menganimasikan `transform` tepat saat
  //   efek ini berjalan, dan rect ikut membaca geseran animasi itu, sehingga sasarannya
  //   meleset sejauh jarak animasinya. `offsetTop` mengabaikan transform.
  useEffect(() => {
    const kotak = utas.current;
    if (!buka || !kotak) return;

    // Anak terakhir selalu penanda ekor setinggi nol, jadi yang dicari yang sebelumnya.
    const terakhir = kotak.children[kotak.children.length - 2];
    if (!terakhir) return;

    // Keduanya diukur dari offsetParent yang sama, jadi selisihnya adalah jarak anak itu dari
    // puncak isi kolom - angka yang persis sama satuannya dengan scrollTop.
    kotak.scrollTop = terakhir.offsetTop - kotak.offsetTop - kotak.clientTop - 10;
  }, [pesan, menunggu, buka]);

  useEffect(() => {
    if (buka) kolom.current?.focus();
  }, [buka]);

  // Esc menutup panel, dan klik di luar panel juga - keduanya perilaku yang sudah diharapkan
  // orang dari kotak mengambang. Panel ini TIDAK modal: halaman di belakangnya tetap boleh
  // digulir dan diklik, jadi tidak ada fokus yang dikurung.
  useEffect(() => {
    if (!buka) return;
    function onTombol(e) {
      if (e.key === "Escape") setBuka(false);
    }
    function onKlik(e) {
      if (!panel.current?.contains(e.target)) setBuka(false);
    }
    document.addEventListener("keydown", onTombol);
    // Ditunda satu putaran event loop: tanpa itu, klik yang MEMBUKA panel ikut tertangkap
    // penutupnya sendiri dan panelnya tertutup pada frame yang sama.
    const timer = setTimeout(() => document.addEventListener("mousedown", onKlik), 0);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("keydown", onTombol);
      document.removeEventListener("mousedown", onKlik);
    };
  }, [buka]);

  function jawab(pertanyaan, entriLangsung) {
    const tanya = pertanyaan.trim();
    if (!tanya || menunggu) return;

    nomor.current += 1;
    setPesan((lama) => [...lama, { id: `q${nomor.current}`, peran: "user", teks: tanya }]);
    setKetikan("");
    setMenunggu(true);

    // Chip yang diklik sudah membawa entrinya; hanya ketikan bebas yang perlu dicocokkan.
    const hasil = entriLangsung
      ? {
          jenis: JENIS.jawab,
          entri: entriLangsung,
          usul: (entriLangsung.usul ?? []).map((id) => FAQ.find((e) => e.id === id)).filter(Boolean),
        }
      : cari(tanya);

    setTimeout(() => {
      nomor.current += 1;
      setPesan((lama) => [
        ...lama,
        {
          id: `a${nomor.current}`,
          peran: "bot",
          entri: hasil.entri,
          teks: hasil.entri ? null : BALASAN[hasil.jenis] ?? BALASAN[JENIS.belumAda],
          usul: hasil.usul,
        },
      ]);
      setMenunggu(false);
    }, JEDA_MS);
  }

  return (
    <div className="faqbot" ref={panel}>
      {buka && (
        <section
          className="faqbot__panel"
          role="dialog"
          aria-labelledby={judulId}
        >
          <header className="faqbot__head">
            <BotMark size={34} />
            <div className="faqbot__head-teks">
              <h2 id={judulId}>Tanya soal Ulasin</h2>
              {/* Label ini bukan basa-basi hukum - ia yang membedakan kotak ini dari asisten
                  AI, dan karena itu ia berdiri di kepala panel, bukan di catatan kaki. */}
              <p>Pertanyaan umum seputar produk</p>
            </div>
            <button
              type="button"
              className="faqbot__tutup"
              onClick={() => setBuka(false)}
              aria-label="Tutup kotak FAQ"
            >
              ✕
            </button>
          </header>

          <div className="faqbot__thread" ref={utas} aria-live="polite" aria-atomic="false">
            {pesan.map((p) => (
              <Gelembung
                key={p.id}
                pesan={p}
                onPilih={(entri) => jawab(entri.q, entri)}
                onTutup={() => setBuka(false)}
              />
            ))}
            {menunggu && (
              <div className="faqbot__baris">
                <BotMark size={24} className="faqbot__ava" />
                <p className="faqbot__bubble faqbot__bubble--bot faqbot__ketik">
                  <i />
                  <i />
                  <i />
                  <span className="sr-only">Mencari jawaban</span>
                </p>
              </div>
            )}
            {/* Penanda ekor. Efek gulir di atas mengandalkan letaknya sebagai anak terakhir. */}
            <div />
          </div>

          <form
            className="faqbot__form"
            onSubmit={(e) => {
              e.preventDefault();
              jawab(ketikan);
            }}
          >
            <label className="sr-only" htmlFor="faqbot-input">
              Tulis pertanyaan Anda tentang Ulasin
            </label>
            <input
              id="faqbot-input"
              ref={kolom}
              value={ketikan}
              maxLength={200}
              autoComplete="off"
              onChange={(e) => setKetikan(e.target.value)}
              placeholder="Misalnya: cara pakainya gimana?"
            />
            <button
              className="btn btn--primary"
              type="submit"
              disabled={menunggu || !ketikan.trim()}
            >
              Kirim
            </button>
          </form>
        </section>
      )}

      <button
        type="button"
        className={`faqbot__pemicu ${buka ? "faqbot__pemicu--buka" : ""}`}
        onClick={() => setBuka((b) => !b)}
        aria-expanded={buka}
        aria-label={buka ? "Tutup kotak FAQ" : "Buka kotak FAQ tentang Ulasin"}
      >
        {/* Maskotnya duduk di atas cakram putih, bukan langsung di atas pil biru: badannya
            biru juga, dan biru di atas biru meninggalkan siluet yang harus ditebak. Cakramnya
            sekaligus membuat tombol ini terbaca sebagai avatar - "ada yang bisa diajak
            bicara" - alih-alih sebagai ikon aksi. */}
        <span className="faqbot__pemicu-ava">
          <BotMark size={24} />
        </span>
        <span className="faqbot__pemicu-teks">Tanya soal Ulasin</span>
      </button>
    </div>
  );
}
