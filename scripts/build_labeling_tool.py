"""Bangun alat pelabelan visual dari daftar tugas CSV.

Mengedit CSV di spreadsheet memaksa pelabel berpindah-pindah antara berkas foto dan baris
tabel, dan satu baris tergeser sudah cukup membuat seluruh sisanya salah pasang. Alat ini
menampilkan foto bersama teks ulasannya dan menyimpan pilihan lewat satu ketukan - kekeliruan
pasang-baris menjadi tidak mungkin.

Halaman yang dihasilkan berjalan sepenuhnya lokal (dibuka dengan file://) dan tidak mengirim
apa pun ke mana pun. Foto ulasan pelanggan tidak boleh meninggalkan mesin ini.

Jalankan:
    python scripts/build_labeling_tool.py
    -> buka data/annotation/label.html di browser
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TASK_CSV = REPO / "data" / "annotation" / "visual_labeling_task.csv"
OUT_HTML = REPO / "data" / "annotation" / "label.html"

# Urutan ini menentukan tombol 1-4. Sama persis dengan configs/visual_classes.yaml.
CLASSES = [
    ("produk_rusak", "Produk rusak", "Barangnya sendiri rusak: robek, bolong, sobek, noda, lecet, jahitan lepas"),
    ("salah_kirim", "Salah kirim", "Yang datang berbeda dari yang dipesan: warna lain, model lain, jumlah kurang"),
    ("kemasan_rusak", "Kemasan rusak", "Bungkus/plastik/dus yang rusak - bukan barangnya"),
    ("normal", "Normal", "Tidak terlihat masalah pada foto ini"),
]


MASALAH = {"produk_rusak", "salah_kirim", "kemasan_rusak"}


def perlu_ditinjau(rows: list[dict]) -> dict[str, str]:
    """Foto yang layak dilihat ulang, beserta alasannya.

    Tiga tanda ini lahir dari pemeriksaan silang nyata, bukan dugaan: satu foto ulasan bintang
    lima berisi tiga kaos utuh ternyata terlabeli `produk_rusak`, dan dua dari tiga
    `kemasan_rusak` ternyata paket yang sepenuhnya utuh - foto yang MENAMPILKAN kemasan
    disangka kemasan yang rusak.
    """
    tandai: dict[str, str] = {}
    for r in rows:
        f, label, bintang = r["image_file"], r["label_manusia"], r["rating"]
        if bintang in ("4", "5") and label in MASALAH:
            tandai[f] = "Ulasan bintang tinggi tetapi dilabeli bermasalah"
        elif label == "kemasan_rusak":
            tandai[f] = "Pastikan BUNGKUSNYA yang rusak, bukan sekadar tampak di foto"
        elif bintang in ("1", "2", "3") and label == "normal":
            tandai[f] = "Ulasan mengeluh - pastikan fotonya memang tidak menunjukkan apa pun"
    return tandai


def main() -> int:
    if not TASK_CSV.exists():
        print(f"Belum ada {TASK_CSV}. Jalankan prepare_apify_photos.py lebih dulu.")
        return 1

    rows = list(csv.DictReader(TASK_CSV.open(encoding="utf-8")))
    tandai = perlu_ditinjau(rows)

    OUT_HTML.write_text(
        TEMPLATE.replace("__DATA__", json.dumps(rows, ensure_ascii=False))
        .replace("__CLASSES__", json.dumps(CLASSES, ensure_ascii=False))
        .replace("__FLAGS__", json.dumps(tandai, ensure_ascii=False)),
        encoding="utf-8",
    )
    print(f"{len(rows)} foto siap dilabeli.")
    if tandai:
        print(f"{len(tandai)} foto ditandai perlu ditinjau ulang:")
        for f, alasan in tandai.items():
            print(f"  {f}  - {alasan}")
    print(f"Buka: {OUT_HTML}")
    return 0


TEMPLATE = """<!doctype html>
<html lang="id"><head><meta charset="utf-8" />
<title>Pelabelan foto ulasan - Ulasin</title>
<style>
:root{--paper:#f7f7f5;--surface:#fff;--ink:#1a1d26;--muted:#5a6070;--rule:#e3e3de;
  --nila:#2b3a8f;--high:#b3261e;--med:#9c5d00;--pos:#1f6b4a;--abstain:#636774}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Plus Jakarta Sans",system-ui,-apple-system,sans-serif;font-size:16px}
header{position:sticky;top:0;background:rgba(247,247,245,.94);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--rule);padding:12px 20px;display:flex;gap:16px;align-items:center;z-index:5}
h1{font-size:1rem;margin:0}
.bar{flex:1;height:6px;background:#e3e3de;border-radius:3px;overflow:hidden;max-width:340px}
.bar i{display:block;height:100%;background:var(--nila);transition:width .2s}
.count{font-family:"IBM Plex Mono",monospace;font-size:.9rem;font-variant-numeric:tabular-nums}
main{max-width:860px;margin:0 auto;padding:22px 20px 90px}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:14px;padding:20px;
  box-shadow:0 4px 16px -6px rgba(20,22,30,.12)}
img{width:100%;max-height:56vh;object-fit:contain;background:#efefec;border-radius:10px;display:block}
.meta{font-family:"IBM Plex Mono",monospace;font-size:.78rem;color:var(--muted);margin:10px 0 4px}
.quote{background:#efefec;border-left:3px solid var(--nila);border-radius:0 8px 8px 0;
  padding:11px 14px;font-family:"IBM Plex Mono",monospace;font-size:.86rem;line-height:1.6;
  white-space:pre-wrap;margin:8px 0 0;max-height:12em;overflow:auto}
.opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;margin-top:18px}
button{font-family:inherit;font-size:1rem;cursor:pointer;border-radius:10px;padding:13px 14px;
  border:1px solid var(--rule);background:var(--surface);text-align:left;line-height:1.35}
button:hover{border-color:var(--nila)}
button b{display:block}
button small{color:var(--muted);font-size:.76rem}
button kbd{float:right;font-family:"IBM Plex Mono",monospace;font-size:.72rem;color:var(--muted);
  border:1px solid var(--rule);border-bottom-width:2px;border-radius:4px;padding:1px 5px}
.b1{border-left:4px solid var(--high)}.b2{border-left:4px solid var(--med)}
.b3{border-left:4px solid #8a5cd0}.b4{border-left:4px solid var(--pos)}
.b5{border-left:4px solid var(--abstain)}
.nav{display:flex;gap:10px;margin-top:14px;align-items:center}
.nav button{padding:9px 14px;font-size:.9rem}
.done{text-align:center;padding:60px 20px}
.done h2{font-size:1.4rem}
.dl{background:var(--nila);color:#fff;border:none;padding:14px 22px;border-radius:10px;
  font-weight:600;margin-top:18px;display:inline-block}
.tally{display:flex;gap:14px;flex-wrap:wrap;font-size:.82rem;color:var(--muted);margin-top:14px}
.tally span{font-family:"IBM Plex Mono",monospace}
.queue{background:#fdf0dc;border:1px solid #e8c98a;border-radius:12px;padding:13px 16px;
  margin-bottom:14px;font-size:.88rem;line-height:1.9}
.jump{font-family:"IBM Plex Mono",monospace;font-size:.75rem;padding:3px 8px;margin:0 5px 0 0;
  border-radius:6px;border:1px solid #e8c98a;background:#fff}
.jump.on{background:var(--med);color:#fff;border-color:var(--med)}
.flag{background:#fdf0dc;color:#6b3f00;border-radius:8px;padding:9px 12px;margin-bottom:12px;
  font-size:.85rem}
</style></head><body>
<header>
  <h1>Pelabelan foto ulasan</h1>
  <div class="bar"><i id="bar" style="width:0%"></i></div>
  <span class="count" id="count"></span>
  <button class="dl" style="margin:0;padding:8px 14px;font-size:.85rem" id="dl">Unduh CSV</button>
</header>
<main id="main"></main>
<script>
const ROWS = __DATA__;
const CLASSES = __CLASSES__;
const FLAGS = __FLAGS__;
const KEY = "insightulasan_label_v1";

// Label yang sudah ada di CSV menjadi titik mulai. Tanpa ini, membuka alat setelah mengunduh
// CSV akan terlihat seolah seluruh pekerjaan sebelumnya hilang.
let saved = JSON.parse(localStorage.getItem(KEY) || "null");
if (!saved) {
  saved = {};
  ROWS.forEach(r => {
    if (r.label_manusia || r.sulit_dinilai)
      saved[r.image_file] = {label: r.label_manusia || "", sulit: r.sulit_dinilai || ""};
  });
  localStorage.setItem(KEY, JSON.stringify(saved));
}

// Bila ada foto bertanda, mulailah dari situ - itu satu-satunya pekerjaan yang tersisa.
const ANTRE = ROWS.map((r, n) => [r.image_file, n]).filter(([f]) => FLAGS[f]).map(([, n]) => n);
let i = ANTRE.length ? ANTRE[0] : ROWS.findIndex(r => !saved[r.image_file]);
if (i < 0) i = ROWS.length;

function simpan(file, label, sulit){
  saved[file] = {label, sulit};
  localStorage.setItem(KEY, JSON.stringify(saved));
}
function hitung(){
  const t = {};
  Object.values(saved).forEach(v => { const k = v.sulit ? "sulit_dinilai" : v.label; t[k] = (t[k]||0)+1; });
  return t;
}
function render(){
  const n = Object.keys(saved).length;
  document.getElementById("bar").style.width = (n/ROWS.length*100) + "%";
  document.getElementById("count").textContent = n + " / " + ROWS.length;
  const main = document.getElementById("main");

  if (i >= ROWS.length){
    const t = hitung();
    main.innerHTML = `<div class="card done"><h2>Selesai - ${n} foto terlabeli</h2>
      <div class="tally" style="justify-content:center">` +
      Object.entries(t).map(([k,v]) => `<span>${k}: ${v}</span>`).join("") +
      `</div><p style="color:var(--muted);font-size:.9rem;margin-top:16px">
      Klik <b>Unduh CSV</b> di atas, lalu timpa
      <code>data/annotation/visual_labeling_task.csv</code>.</p>
      <button class="dl" onclick="i=0;render()">Tinjau ulang dari awal</button></div>`;
    return;
  }

  const r = ROWS[i], sudah = saved[r.image_file], alasan = FLAGS[r.image_file];
  main.innerHTML =
    (ANTRE.length ? `<div class="queue"><b>${ANTRE.length} foto perlu ditinjau ulang</b>
      - klik untuk melompat:<br />` +
      ANTRE.map(n => `<button class="jump ${n === i ? "on" : ""}" data-ke="${n}"
        >${ROWS[n].image_file.slice(0,8)}</button>`).join("") + `</div>` : "") +
    `<div class="card">
    ${alasan ? `<div class="flag">Ditandai: ${alasan}</div>` : ""}
    <img src="../raw/review_photos/${r.image_file}" alt="Foto ulasan ${i+1}" />
    <div class="meta">${r.image_file} · rating ${r.rating || "-"} · produk ${r.product_name || "-"}</div>
    ${r.review_text ? `<div class="quote">${r.review_text.replace(/</g,"&lt;")}</div>`
                    : `<div class="quote" style="color:var(--muted)">(ulasan tanpa teks)</div>`}
    <div class="opts">` +
      CLASSES.map(([id,nama,jelas],k) => `<button class="b${k+1}" data-pilih="${id}">
        <b>${nama}<kbd>${k+1}</kbd></b><small>${jelas}</small></button>`).join("") +
      `<button class="b5" data-sulit="1"><b>Sulit dinilai<kbd>S</kbd></b>
        <small>Foto buram, terpotong, atau memang tidak jelas - ini jawaban yang sah</small></button>
    </div>
    <div class="nav">
      <button id="prev" ${i===0?"disabled":""}>← Sebelumnya</button>
      <button id="next">Lewati →</button>
      ${sudah ? `<span style="color:var(--muted);font-size:.85rem">tersimpan:
        <b>${sudah.sulit ? "sulit dinilai" : sudah.label}</b></span>` : ""}
    </div></div>`;

  main.querySelectorAll("[data-pilih]").forEach(b =>
    b.onclick = () => { simpan(r.image_file, b.dataset.pilih, ""); i++; render(); });
  main.querySelector("[data-sulit]").onclick = () => { simpan(r.image_file, "", "ya"); i++; render(); };
  document.getElementById("prev").onclick = () => { if(i>0){ i--; render(); } };
  document.getElementById("next").onclick = () => { i++; render(); };
  main.querySelectorAll("[data-ke]").forEach(b =>
    b.onclick = () => { i = +b.dataset.ke; render(); });
}
document.addEventListener("keydown", e => {
  if (i >= ROWS.length) return;
  const r = ROWS[i];
  const k = CLASSES.findIndex((_,n) => String(n+1) === e.key);
  if (k >= 0){ simpan(r.image_file, CLASSES[k][0], ""); i++; render(); }
  else if (e.key.toLowerCase() === "s"){ simpan(r.image_file, "", "ya"); i++; render(); }
  else if (e.key === "ArrowLeft" && i > 0){ i--; render(); }
  else if (e.key === "ArrowRight"){ i++; render(); }
});
document.getElementById("dl").onclick = () => {
  const kolom = Object.keys(ROWS[0]);
  const esc = v => `"${String(v ?? "").replace(/"/g,'""')}"`;
  const baris = ROWS.map(r => {
    const s = saved[r.image_file] || {};
    return kolom.map(k => esc(k === "label_manusia" ? (s.label || "")
                            : k === "sulit_dinilai" ? (s.sulit || "") : r[k])).join(",");
  });
  const blob = new Blob([kolom.join(",") + "\\n" + baris.join("\\n")],
                        {type:"text/csv;charset=utf-8"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "visual_labeling_task.csv";
  a.click();
};
render();
</script></body></html>
"""

if __name__ == "__main__":
    raise SystemExit(main())
