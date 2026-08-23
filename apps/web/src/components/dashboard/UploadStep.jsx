/** Langkah pertama dashboard: pilih kategori, masukkan ulasan, lalu analisis.
 *
 * Layar ini pernah dibuka oleh formulir profil berisi empat isian - nama toko, produk yang
 * dianalisis, kategori, dan tiga aspek "yang paling ingin Anda tahu". Tiga di antaranya
 * dicabut dan tidak kembali; alasan masing-masing tercatat di kepala `lib/aspects.js`.
 *
 * Kategori kembali, dan itu koreksi atas percobaan sebelumnya. Ia sempat dipindah ke kepala
 * laporan sebagai tebakan yang bisa diganti - masalahnya, di sana ia jadi kontrol yang MENGUBAH
 * angka di layar yang sedang dibaca, duduk di antara angka-angka yang justru tidak boleh
 * berubah sendiri. Pembaca laporan tidak sedang menyiapkan analisis, ia sedang membacanya, dan
 * kendali penyiapan yang muncul di tengah bacaan terbaca sebagai rancu.
 *
 * Kategori memang keterangan penyiapan: ia memilih baseline pembanding sebelum apa pun
 * dihitung. Jadi tempatnya di sini, sebelum tombol analisis - satu pertanyaan yang jawabannya
 * benar-benar cuma diketahui pemilik toko, dan tidak ada di dalam berkas mana pun.
 */

import { useId } from "react";
import { FirstRunGuide } from "./FirstRunGuide.jsx";

import { CATEGORIES } from "../../lib/format.js";
import { FileInput, PasteInput, ScreenshotInput } from "./inputs.jsx";

/* Apa yang sebenarnya dilakukan kategori. Copy lama pernah berjanji ia "menyembunyikan aspek
 * yang tidak relevan bagi toko seperti milik Anda", dan itu tidak terjadi: pipeline analisisnya
 * memakai kategori HANYA untuk memilih baseline pembanding. Janji yang tidak ditepati di layar
 * pertama membuat seluruh angka sesudahnya ikut dicurigai. */
const GUNA_KATEGORI =
  "Menentukan rata-rata kategori yang dipakai membandingkan hasil Anda. Seluruh aspek tetap " +
  "dianalisis apa pun pilihannya.";

/* Peringatan cakupan data, per kategori. Hanya satu kategori yang punya, dan justru karena itu
 * ia bermakna: catatan yang muncul di semua pilihan terbaca sebagai penafian rutin, bukan
 * sebagai keterangan yang perlu dibaca. */
const CATATAN = {
  food_beverage:
    "Data latih kami paling tipis di sini - 196 dari sekitar 40.000 ulasan. Aspek rasa dan " +
    "pembandingnya lemah buktinya.",
};

/** Pemilih kategori.
 *
 * Radio sungguhan di balik pilnya, bukan tombol ber-`aria-checked`: navigasi panah antar
 * pilihan dan pengumuman "1 dari 5" oleh pembaca layar sudah benar tanpa kode tambahan.
 * `fieldset` dipakai karena `<legend>` adalah satu-satunya cara memberi nama pada sekumpulan
 * radio yang dibacakan pembaca layar sebagai nama grupnya - gaya bawaannya dinetralkan di
 * `.grup` supaya tidak muncul kotak di dalam kotak.
 */
function CategoryPicker({ value, onChange }) {
  return (
    <section className="panel">
      <fieldset className="grup">
        <legend className="grup__label">Kategori produk Anda</legend>
        <div className="picker__row">
          {CATEGORIES.map(([id, label]) => (
            <label key={id} className={`pick ${value === id ? "pick--on" : ""}`}>
              <input
                type="radio"
                name="category"
                value={id}
                checked={value === id}
                onChange={() => onChange(id)}
                className="sr-only"
              />
              {label}
            </label>
          ))}
        </div>
        <p className="meta grup__hint">{GUNA_KATEGORI}</p>
        {CATATAN[value] && <p className="grup__catatan">{CATATAN[value]}</p>}
      </fieldset>
    </section>
  );
}

const TABS = [
  ["paste", "Tempel teks"],
  ["file", "Unggah berkas"],
  ["shot", "Tangkapan layar"],
];

export function UploadStep({
  ready,
  error,
  tab,
  onTab,
  category,
  onCategory,
  paste,
  onPaste,
  file,
  mapping,
  onPickFile,
  onMap,
  onClearFile,
  shots,
  drafts,
  ocrBusy,
  onPickShots,
  onEditDraft,
  onRemoveDraft,
  onClearShots,
  count,
  canAnalyze,
  onAnalyze,
  onSample,
}) {
  const tabId = useId();

  return (
    <>
      {!ready && (
        <div className="banner-grey">
          Sistem sedang menyiapkan model. Tombol analisis akan aktif setelah siap.
        </div>
      )}
      {error && (
        <div className="banner-error">
          <b>{error.message}</b>
          {error.action && <div style={{ marginTop: 4 }}>{error.action}</div>}
        </div>
      )}

      <FirstRunGuide />

      <CategoryPicker value={category} onChange={onCategory} />

      <h2 className="sec-title sec-title--rapat">Ulasan yang mau dianalisis</h2>
      <a href="#/panduan" className="dari-mana">
        <span aria-hidden="true">?</span> Dari mana saya mengambil ulasan? Panduan per aplikasi ›
      </a>

      {/* Bilah tab dan panelnya dirangkai betulan: tiap tab menunjuk panel lewat
          `aria-controls`, dan panelnya menyebut tab yang sedang aktif lewat `aria-labelledby`.
          Sebelumnya ada `role="tablist"` tanpa satu pun `tabpanel` - pembaca layar mengumumkan
          "tab 1 dari 3" lalu tidak punya apa pun untuk ditunjuk sebagai isinya. */}
      <div className="tabs tabs--block" role="tablist" aria-label="Cara memasukkan ulasan">
        {TABS.map(([id, label]) => (
          <button
            key={id}
            id={`${tabId}-${id}`}
            role="tab"
            aria-selected={tab === id}
            aria-controls={`${tabId}-panel`}
            className={`tab ${tab === id ? "tab--active" : ""}`}
            onClick={() => onTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      <div role="tabpanel" id={`${tabId}-panel`} aria-labelledby={`${tabId}-${tab}`}>
        {tab === "paste" && <PasteInput value={paste} onChange={onPaste} />}
        {tab === "file" && (
          <FileInput
            file={file}
            mapping={mapping}
            onPick={onPickFile}
            onMap={onMap}
            onClear={onClearFile}
          />
        )}
        {tab === "shot" && (
          <ScreenshotInput
            shots={shots}
            drafts={drafts}
            busy={ocrBusy}
            onPick={onPickShots}
            onEdit={onEditDraft}
            onRemove={onRemoveDraft}
            onClear={onClearShots}
          />
        )}
      </div>

      {/* Jumlahnya masuk ke label supaya tombolnya menyebut persis apa yang akan terjadi.
          Sebelum ada satu pun ulasan, angkanya dihilangkan seluruhnya - bukan dikosongkan,
          yang menyisakan spasi ganda di tengah kalimat. */}
      <button className="btn-cta" disabled={!canAnalyze} onClick={onAnalyze}>
        {count ? `Analisis ${count} ulasan ›` : "Analisis ulasan ›"}
      </button>

      {tab === "file" && file && !mapping.text && (
        <p className="meta" style={{ marginTop: 8 }}>
          Pilih kolom teks ulasan lebih dulu untuk mulai menganalisis.
        </p>
      )}

      <button
        className="btn btn--outline btn--block"
        disabled={!ready}
        onClick={onSample}
        style={{ marginTop: 10 }}
      >
        Coba dengan data contoh
      </button>

      {/* Menjelaskan apa yang dibaca sistem dari berkasnya menggantikan tiga pertanyaan yang
          dulu diajukan di sini. Bedanya: yang ini keterangan, bukan pekerjaan - pengguna boleh
          melewatinya begitu saja dan tetap sampai ke hasil yang sama. */}
      <p className="meta" style={{ marginTop: 20 }}>
        Kolom produk, rating, dan tanggal terbaca otomatis kalau ada di berkas Anda -
        masing-masing membuka bagiannya sendiri di laporan. Anda tidak perlu mengetiknya ulang.
      </p>

      <p className="meta" style={{ marginTop: 10 }}>
        Data Anda hanya diproses selama sesi ini dan tidak disimpan permanen. Nomor telepon dan data
        pribadi yang terdeteksi disamarkan sebelum dianalisis. Gambar yang Anda unggah dibaca
        teksnya lalu dibuang; menyimpulkan kondisi barang dari foto belum didukung.
      </p>
    </>
  );
}
