export function FootCta({ onStart }) {
  return (
    <div className="foot">
      <div className="foot-card">
        <div className="glow" />
        <h2>
          Berhenti Menggulir Ulasan. <span className="accent">Mulai Perbaiki Bisnis Anda.</span>
        </h2>
        <p>
          Masukkan ulasan toko Anda, dan lihat daftar prioritas pertama dari apa yang pelanggan Anda
          minta untuk diperbaiki.
        </p>
        <div className="cta-row">
          <button className="btn btn--primary btn--lg" onClick={onStart}>
            Mulai Analisis ›
          </button>
          <a className="btn btn--ondark btn--lg" href="#cara-kerja">
            Lihat Cara Kerjanya
          </a>
        </div>
      </div>
      <div className="foot-note">
        © 2026 Ulasin · Dibuat untuk pelaku usaha yang peduli setiap ulasan
      </div>
    </div>
  );
}
