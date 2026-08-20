/** Langkah pertama dashboard: memilih kategori, memasukkan ulasan, lalu menganalisis. */

import { CATEGORIES } from "../../lib/format.js";
import { FileInput, PasteInput, ScreenshotInput } from "./inputs.jsx";

const TABS = [
  ["paste", "Tempel teks"],
  ["file", "Unggah berkas"],
  ["shot", "Tangkapan layar"],
];

function CategoryPicker({ value, onChange }) {
  return (
    <fieldset className="panel picker">
      <legend className="panel-title">Kategori produk</legend>
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
      <p className="meta" style={{ marginTop: 12 }}>
        Dipakai untuk membandingkan hasil Anda dengan rata-rata kategori sejenis, dan untuk
        menyembunyikan aspek yang tidak relevan bagi toko seperti milik Anda.
      </p>
    </fieldset>
  );
}

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

      <div className="tabs tabs--block" role="tablist" aria-label="Cara memasukkan ulasan">
        {TABS.map(([id, label]) => (
          <button
            key={id}
            role="tab"
            aria-selected={tab === id}
            className={`tab ${tab === id ? "tab--active" : ""}`}
            onClick={() => onTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      <CategoryPicker value={category} onChange={onCategory} />

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

      <p className="meta" style={{ marginTop: 20 }}>
        Data Anda hanya diproses selama sesi ini dan tidak disimpan permanen. Nomor telepon dan data
        pribadi yang terdeteksi disamarkan sebelum dianalisis. Gambar yang Anda unggah dibaca
        teksnya lalu dibuang; menyimpulkan kondisi barang dari foto belum didukung.
      </p>
    </>
  );
}
