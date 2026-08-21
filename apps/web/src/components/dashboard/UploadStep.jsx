/** Langkah pertama dashboard: memasukkan ulasan, lalu menganalisis. Itu saja.
 *
 * Layar ini pernah dibuka oleh sebuah formulir profil - nama toko, produk yang dianalisis,
 * kategori, dan tiga aspek "yang paling ingin Anda tahu". Keempatnya dicabut, dan alasan
 * masing-masing tercatat di kepala `lib/aspects.js`. Yang berlaku untuk keempatnya sekaligus:
 * pertanyaan itu diajukan tepat pada saat pengguna paling sedikit tahu - sebelum ia melihat
 * satu pun hasil - dan tiga dari empat jawabannya sudah ada di dalam berkas yang sedang ia
 * unggah pada detik yang sama.
 *
 * Yang tersisa adalah satu pertanyaan: dari mana ulasannya datang. Jalan tercepat dari membuka
 * halaman ke melihat hasil sekarang benar-benar dua langkah - tempel, lalu tekan.
 */

import { useId } from "react";

import { FileInput, PasteInput, ScreenshotInput } from "./inputs.jsx";

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

      {/* Menjelaskan apa yang dibaca sistem dari berkasnya menggantikan pertanyaan yang dulu
          diajukan di sini. Bedanya: yang ini keterangan, bukan pekerjaan - pengguna boleh
          melewatinya begitu saja dan tetap sampai ke hasil yang sama. */}
      <p className="meta" style={{ marginTop: 20 }}>
        Kolom produk, rating, dan tanggal terbaca otomatis kalau ada di berkas Anda - masing-masing
        membuka bagiannya sendiri di laporan. Kategori toko ditebak dari isi ulasan, dan tebakannya
        bisa Anda ganti di kepala laporan.
      </p>

      <p className="meta" style={{ marginTop: 10 }}>
        Data Anda hanya diproses selama sesi ini dan tidak disimpan permanen. Nomor telepon dan data
        pribadi yang terdeteksi disamarkan sebelum dianalisis. Gambar yang Anda unggah dibaca
        teksnya lalu dibuang; menyimpulkan kondisi barang dari foto belum didukung.
      </p>
    </>
  );
}
