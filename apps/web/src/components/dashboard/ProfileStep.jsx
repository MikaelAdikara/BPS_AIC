/** Langkah pertama: siapa yang bertanya, dan apa yang ingin ia ketahui.
 *
 * Versi sebelumnya cuma satu baris radio kategori, dan bermasalah di dua tingkat sekaligus.
 *
 * Yang terlihat: kotaknya `<fieldset>`, dan gaya baku browser memberi fieldset margin 2px di
 * kiri dan kanan yang tidak pernah ditimpa. Setiap blok lain di kolom ini selebar 560px; yang
 * ini 556px, menjorok masuk dua piksel di kedua sisi. Cukup untuk membuatnya terbaca sebagai
 * sesuatu yang tertempel belakangan, tidak cukup untuk langsung ketahuan sebabnya.
 *
 * Yang lebih dalam: letaknya di ANTARA bilah tab dan panel milik tab itu. Bilah tab yang
 * dipisahkan dari isinya oleh kotak lain berhenti terbaca sebagai satu perkakas - dan bagi
 * pembaca layar hubungan itu memang tidak pernah ada, karena tidak ada `tabpanel` sama sekali.
 * Karena itu kategori pindah ke atas: memilih kategori adalah keterangan tentang TOKO,
 * sedangkan tab adalah cara ulasannya masuk. Dua pertanyaan berbeda, dua blok berbeda.
 *
 * Sekalian ditumbuhkan. Satu radio kategori adalah keterangan yang terlalu sedikit untuk
 * disebut profil, dan pengguna tidak punya satu pun tempat untuk menyebut apa yang sebenarnya
 * ingin ia ketahui. Sekarang ada empat isian - tiga di antaranya opsional - dan tiap isian
 * menyebut sendiri akibatnya tepat di bawah kolomnya. Isian yang tidak mengubah apa pun adalah
 * cara tercepat membuat orang berhenti mengisi formulir; janji yang tidak ditepati lebih cepat
 * lagi. Apa yang diubah masing-masing, dan apa yang TIDAK, ada di `lib/profile.js`.
 *
 * Yang opsional dilipat di balik `<details>`, dan itu bukan sekadar penghematan ruang. Terbuka
 * semua, layar unggah jadi 1300px sebelum tombol analisis - dua layar penuh di laptop, lebih
 * lagi di ponsel. Orang yang dilayani produk ini membuka aplikasi malam hari setelah tutup toko
 * untuk satu pertanyaan; kalau jalan tercepatnya adalah menempel lalu menekan tombol, jalan itu
 * tidak boleh dihalangi tiga pertanyaan yang boleh ia lewati. Ringkasan di kepala lipatan
 * menyebutkan apa yang sudah terisi, sehingga isian yang tersembunyi tidak pernah menjadi isian
 * yang terlupakan.
 *
 * `<details>` bawaan, bukan buka-tutup buatan sendiri: keyboard, pembaca layar, dan pencarian
 * dalam halaman sudah mengerti elemen ini. Tingginya sengaja tidak dianimasikan -
 * `interpolate-size` baru jalan di sebagian browser, dan lipatan yang menganimasi diri hanya di
 * satu browser adalah dua produk yang berbeda.
 */

import { useId } from "react";

import { CATEGORIES, aspectLabel } from "../../lib/format.js";
import { MAX_FOKUS, aspekUntuk, pilihFokus, ubahProfil } from "../../lib/profile.js";

/* Apa yang sebenarnya dilakukan kategori. Kalimat lama berjanji ia "menyembunyikan aspek yang
 * tidak relevan bagi toko seperti milik Anda", dan itu tidak terjadi: pipeline analisisnya
 * memakai kategori HANYA untuk memilih baseline pembanding. Janji yang tidak ditepati di layar
 * pertama membuat seluruh angka sesudahnya ikut dicurigai. */
const GUNA_KATEGORI =
  "Hasil Anda dibandingkan terhadap rata-rata kategori ini dari data publik, dan daftar fokus " +
  "di bawah menyesuaikan diri dengannya.";

/* Peringatan cakupan data, per kategori. Hanya satu kategori yang punya, dan justru karena itu
 * ia bermakna: catatan yang muncul di semua pilihan terbaca sebagai penafian rutin, bukan
 * sebagai keterangan yang perlu dibaca. */
const CATATAN = {
  food_beverage:
    "Data latih kami paling tipis di sini - 196 dari sekitar 40.000 ulasan. Aspek rasa dan " +
    "pembandingnya lemah buktinya.",
};

/** Ringkasan isian opsional, dibaca saat lipatannya tertutup. */
function ringkas({ store, product, focus }) {
  const terisi = [
    store.trim(),
    product.trim(),
    focus.length ? `${focus.length} fokus` : "",
  ].filter(Boolean);
  return terisi.length ? terisi.join(" · ") : "Opsional";
}

const Chevron = () => (
  <svg
    className="lanjut__panah"
    width="13"
    height="13"
    viewBox="0 0 24 24"
    fill="none"
    aria-hidden="true"
  >
    <path
      d="m6 9 6 6 6-6"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

function Kolom({ label, hint, value, onChange, placeholder, maxLength }) {
  const id = useId();
  return (
    <div className="kolom">
      <label className="kolom__label" htmlFor={id}>
        {label} <em>opsional</em>
      </label>
      <input
        id={id}
        className="kolom__input"
        type="text"
        value={value}
        maxLength={maxLength}
        autoComplete="off"
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
      <p className="meta kolom__hint">{hint}</p>
    </div>
  );
}

export function ProfileStep({ profile, onChange }) {
  const aspek = aspekUntuk(profile.category);
  const penuh = profile.focus.length >= MAX_FOKUS;

  return (
    <section className="panel profil">
      <h2 className="panel-title">Tentang toko Anda</h2>

      {/* Radio sungguhan di balik pilnya, bukan tombol ber-`aria-checked`: navigasi panah
          antar-pilihan dan pengumuman "1 dari 5" oleh pembaca layar sudah benar tanpa kode
          tambahan. `fieldset` di sini tidak digayakan sebagai kotak - ia cuma pengelompok,
          jadi tidak ada kartu di dalam kartu. */}
      <fieldset className="grup">
        <legend className="grup__label">Kategori produk</legend>
        <div className="picker__row">
          {CATEGORIES.map(([id, label]) => (
            <label key={id} className={`pick ${profile.category === id ? "pick--on" : ""}`}>
              <input
                type="radio"
                name="category"
                value={id}
                checked={profile.category === id}
                onChange={() => onChange(ubahProfil(profile, { category: id }))}
                className="sr-only"
              />
              {label}
            </label>
          ))}
        </div>
        <p className="meta grup__hint">{GUNA_KATEGORI}</p>
        {CATATAN[profile.category] && <p className="grup__catatan">{CATATAN[profile.category]}</p>}
      </fieldset>

      <details className="lanjut">
        {/* Judul dan ringkasan dibungkus bersama supaya keduanya boleh pindah baris tanpa
            menyeret chevron ikut turun. Di lebar ponsel, judulnya sendiri sudah menghabiskan
            satu baris, dan ringkasan yang dipaksa ikut di baris itu tersisa 28px - terpangkas
            jadi elipsis, padahal justru ringkasan itulah gunanya lipatan yang tertutup. */}
        <summary className="lanjut__kepala">
          <span className="lanjut__teks">
            <span className="lanjut__judul">Beri tahu lebih banyak soal toko Anda</span>
            <span className="lanjut__nilai">{ringkas(profile)}</span>
          </span>
          <Chevron />
        </summary>

        <div className="profil__duo">
          <Kolom
            label="Nama toko"
            value={profile.store}
            maxLength={40}
            placeholder="Toko Bu Rina"
            onChange={(store) => onChange(ubahProfil(profile, { store }))}
            hint="Dipakai untuk menyapa Anda di layar hasil. Tidak ikut dikirim ke server."
          />
          <Kolom
            label="Produk yang dianalisis"
            value={profile.product}
            maxLength={60}
            placeholder="Kemeja linen lengan panjang"
            onChange={(product) => onChange(ubahProfil(profile, { product }))}
            hint="Menempel pada ulasan yang belum menyebut produknya sendiri, jadi kutipan buktinya ikut menyebut ini."
          />
        </div>

        {/* Checkbox, bukan radio: fokus boleh lebih dari satu. Pilihan keempat tidak
            disembunyikan melainkan dinonaktifkan - chip yang lenyap saat yang ketiga dipilih
            terbaca sebagai kesalahan, sedangkan chip yang meredup terbaca sebagai batas. */}
        <fieldset className="grup">
          <legend className="grup__label">
            Yang paling ingin Anda tahu <em>maksimal {MAX_FOKUS}</em>
          </legend>
          <div className="picker__row">
            {aspek.map((id) => {
              const on = profile.focus.includes(id);
              return (
                <label key={id} className={`pick pick--kecil ${on ? "pick--on" : ""}`}>
                  <input
                    type="checkbox"
                    checked={on}
                    disabled={!on && penuh}
                    onChange={() => onChange(pilihFokus(profile, id))}
                    className="sr-only"
                  />
                  {aspectLabel(id)}
                </label>
              );
            })}
          </div>
          <p className="meta grup__hint">
            Menyusun pertanyaan di tab Tanya Jawab, dan menjaga aspek ini tetap tampil di grafik
            sebaran meski jarang disebut. Urutan prioritas tidak ikut berubah - urutan itu datang
            dari angka, bukan dari yang sudah Anda curigai.
          </p>
        </fieldset>
      </details>
    </section>
  );
}
