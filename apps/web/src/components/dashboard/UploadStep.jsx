/** Langkah pertama dashboard: menyebutkan konteks toko, memasukkan ulasan, lalu menganalisis.
 *
 * Dua blok, dalam urutan yang orang pikirkan: siapa saya dan apa yang saya cari (ProfileStep),
 * lalu dari mana ulasannya datang (bilah tab dan panelnya). Sebelumnya kategori duduk di
 * antara bilah tab dan panel milik tab itu; catatan lengkap soal kenapa itu dipindah ada di
 * kepala `ProfileStep.jsx`.
 */

import { useId } from "react";

import { FileInput, PasteInput, ScreenshotInput } from "./inputs.jsx";
import { ProfileStep } from "./ProfileStep.jsx";

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
  profile,
  onProfile,
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

      <ProfileStep profile={profile} onChange={onProfile} />

      <h2 className="sec-title sec-title--rapat">Ulasan yang mau dianalisis</h2>

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

      <p className="meta" style={{ marginTop: 20 }}>
        Data Anda hanya diproses selama sesi ini dan tidak disimpan permanen. Nomor telepon dan data
        pribadi yang terdeteksi disamarkan sebelum dianalisis. Gambar yang Anda unggah dibaca
        teksnya lalu dibuang; menyimpulkan kondisi barang dari foto belum didukung.
      </p>
    </>
  );
}
