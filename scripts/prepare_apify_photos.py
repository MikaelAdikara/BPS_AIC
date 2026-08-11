"""Ubah hasil ekspor Apify menjadi paket foto siap-label (dossier bagian 21B.6.4).

Masukan  : berkas JSON hasil "Shopee Product Reviews Scraper" (zen-studio).
Keluaran : data/raw/review_photos/  berisi foto terunduh
           data/annotation/visual_labeling_task.csv  siap diisi manusia

**Anonimisasi berjalan sebelum apa pun disimpan.** Ulasan Shopee memuat nama akun, dan untuk
kategori fesyen kerap memuat tinggi/berat badan pembeli. Kewajiban UU PDP berlaku sama baik
data berasal dari Kaggle maupun dari scraping sendiri (dossier 21B.6.3), sehingga nama akun
tidak pernah ikut tersimpan dan teks ulasannya melewati penyaring PII yang sama dengan yang
dipakai aplikasi.

Jalankan:
    python scripts/prepare_apify_photos.py path/ke/dataset_apify.json
    python scripts/prepare_apify_photos.py path/ke/dataset_apify.json --max 300
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "apps" / "api"))

from app.tools.privacy import redact_personal_data  # noqa: E402

PHOTO_DIR = REPO / "data" / "raw" / "review_photos"
TASK_CSV = REPO / "data" / "annotation" / "visual_labeling_task.csv"

# Kelas dari configs/visual_classes.yaml — status FROZEN, jangan ditambah di sini.
CLASSES = ["produk_rusak", "salah_kirim", "kemasan_rusak", "normal"]

# Kunci yang mungkin dipakai actor untuk hal yang sama. Ekspor scraper kerap berganti nama
# field antarversi, dan gagal hanya karena satu nama kunci berbeda tidak sepadan.
KEYS = {
    "images": ["images", "image_urls", "imageUrls", "media", "photos"],
    "text": ["comment", "text", "review", "content", "reviewText"],
    "rating": ["rating", "star", "ratingStar", "score"],
    "product": ["productName", "product_name", "product", "itemName"],
}


def pick(row: dict, names: list[str]):
    for n in names:
        if row.get(n) not in (None, "", []):
            return row[n]
    return None


def as_urls(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    out = []
    for item in value or []:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            url = item.get("url") or item.get("src") or item.get("image")
            if url:
                out.append(url)
    return [u for u in out if str(u).startswith("http")]


def load_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = next((v for v in data.values() if isinstance(v, list)), [])
    return [r for r in data if isinstance(r, dict)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("export", type=Path, help="berkas JSON hasil ekspor Apify")
    ap.add_argument("--max", type=int, default=300, help="batas jumlah foto (default 300)")
    args = ap.parse_args()

    if not args.export.exists():
        print(f"Berkas tidak ditemukan: {args.export}", file=sys.stderr)
        return 1

    rows = load_rows(args.export)
    print(f"{len(rows)} ulasan terbaca dari ekspor.")

    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    TASK_CSV.parent.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    manifest: list[dict] = []
    gagal = 0

    for row in rows:
        urls = as_urls(pick(row, KEYS["images"]))
        if not urls:
            continue

        raw_text = str(pick(row, KEYS["text"]) or "")
        redaction = redact_personal_data(raw_text)

        for url in urls:
            if len(manifest) >= args.max:
                break
            # Nama berkas dari hash URL: tidak membocorkan id pengguna, dan menjadikan
            # ulang-jalan skrip ini idempoten alih-alih menggandakan unduhan.
            key = hashlib.sha256(url.encode()).hexdigest()[:16]
            if key in seen:
                continue
            seen.add(key)

            ext = ".jpg" if ".png" not in url.lower() else ".png"
            dest = PHOTO_DIR / f"{key}{ext}"
            if not dest.exists():
                try:
                    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urlopen(req, timeout=30) as resp:
                        dest.write_bytes(resp.read())
                except Exception as exc:  # noqa: BLE001
                    gagal += 1
                    print(f"  gagal unduh {key}: {exc}", file=sys.stderr)
                    continue

            manifest.append({
                "image_file": dest.name,
                # Nama akun TIDAK ikut. Teks disimpan sudah teredaksi.
                "review_text": redaction.text,
                "rating": pick(row, KEYS["rating"]) or "",
                "product_name": pick(row, KEYS["product"]) or "",
                "pii_redacted": "ya" if redaction.redacted else "tidak",
                # Kolom yang diisi manusia. Dikosongkan sengaja — mengisinya otomatis akan
                # membuat label ini tidak sah sebagai penengah performa model visual.
                "label_manusia": "",
                "sulit_dinilai": "",
                "catatan": "",
            })
            if len(manifest) % 50 == 0:
                print(f"  {len(manifest)} foto…", flush=True)

        if len(manifest) >= args.max:
            break

    if not manifest:
        print("Tidak ada foto yang berhasil diambil. Periksa apakah ekspor memuat field "
              "gambar, dan apakah actor dijalankan dengan contentFilter='with media'.",
              file=sys.stderr)
        return 1

    with TASK_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)

    diredaksi = sum(1 for m in manifest if m["pii_redacted"] == "ya")
    print(f"\n{len(manifest)} foto tersimpan di {PHOTO_DIR}")
    print(f"Daftar pelabelan  : {TASK_CSV}")
    print(f"Teks yang memuat PII dan sudah disamarkan: {diredaksi}")
    if gagal:
        print(f"Gagal diunduh: {gagal}")
    print(f"\nIsi kolom 'label_manusia' dengan salah satu: {', '.join(CLASSES)}")
    print("Kosongkan label dan isi 'sulit_dinilai' dengan 'ya' bila foto memang ambigu — "
          "foto ambigu adalah data yang sah untuk mengukur abstention, bukan baris rusak.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
