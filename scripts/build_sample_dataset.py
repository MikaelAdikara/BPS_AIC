"""Susun dataset demo bawaan (ING-04) sesuai komposisi blueprint bagian 42.1.

Dataset ini DI-COMMIT ke repository supaya siapa pun dapat mencoba sistem tanpa menyiapkan
data sendiri. Karena itu ia dikurasi, bukan diambil acak: satu batch tunggal harus mampu
memicu SELURUH kapabilitas sistem dalam sekali jalan.

Target komposisi (bagian 42.1):
  - keluhan berulang pada satu aspek dengan frekuensi tinggi -> memicu Action Card urgensi tinggi
  - pujian jelas pada aspek lain                             -> memicu promotion highlight
  - beberapa aspek berbeda terwakili                         -> aspect aggregate bermakna
  - minimal 30% baris berbahasa informal                     -> menguji ketahanan slang/typo
  - kategori yang punya baseline benchmark (fesyen)          -> BEN-01 dapat tampil
  - slot foto                                                -> diisi pada Fase 3

Teks diambil APA ADANYA dari ulasan nyata (bukan hasil normalisasi) supaya demo menunjukkan
bahasa asli pengguna, termasuk typo dan singkatannya.

Pemakaian:
    python scripts/build_sample_dataset.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "ml" / "text"))

from lexicon import ASPECT_PATTERNS  # noqa: E402
from preprocess import polarity_score  # noqa: E402

RAW = REPO_ROOT / "data" / "raw"
OUT_DIR = REPO_ROOT / "data" / "samples"

SEED = 42
TARGET_TOTAL = 120

# Pola PII - baris yang cocok DIBUANG, bukan diredaksi. Untuk berkas kecil yang di-commit,
# membuang lebih aman daripada mengandalkan redaksi yang mungkin tidak sempurna.
PII_PATTERNS = re.compile(
    r"(?:\+62|08)\d{7,}"          # nomor telepon Indonesia
    r"|[\w.\-]+@[\w\-]+\.\w+"   # email
    r"|\b(?:jl\.?|jalan)\s+\w+"   # alamat jalan
    r"|\b\d{16}\b",             # nomor identitas/kartu
    re.IGNORECASE,
)

INFORMAL = re.compile(
    r"\b(?:bgt|banget|gak|ga|nggak|udah|udh|aja|sih|nih|deh|kak|gan|sis|mantul|dong|bgs|"
    r"cpt|brg|tp|yg|klo|kalo|bikin|kayak|kaya|emang|bener|blm|udahlah)\b",
    re.IGNORECASE,
)


def _aspects_of(text: str) -> list[str]:
    return [a for a, pat in ASPECT_PATTERNS.items() if pat.search(text.lower())]


def _load_fashion_reviews() -> pd.DataFrame:
    path = RAW / "tokopedia_reviews_2019" / "tokopedia-product-reviews-2019.csv"
    if not path.exists():
        print("data/raw kosong - jalankan scripts/download_datasets.py.", file=sys.stderr)
        raise SystemExit(1)

    df = pd.read_csv(path)
    df = df[df["category"] == "fashion"].copy()
    df["text"] = df["text"].astype(str).str.strip()

    df = df[df["text"].str.len().between(15, 300)]
    df = df[~df["text"].str.contains(PII_PATTERNS, regex=True, na=False)]
    df = df.drop_duplicates(subset=["text"])

    df["aspects"] = df["text"].map(_aspects_of)
    polarity = df["text"].map(lambda t: polarity_score(t.lower()))
    df["pos"] = [p for p, _ in polarity]
    df["neg"] = [n for _, n in polarity]
    df["informal"] = df["text"].str.contains(INFORMAL, regex=True, na=False)
    return df.reset_index(drop=True)


def _pick(pool: pd.DataFrame, mask, n: int, used: set) -> pd.DataFrame:
    candidates = pool[mask & (~pool.index.isin(used))]
    taken = candidates.sample(min(n, len(candidates)), random_state=SEED)
    used.update(taken.index)
    return taken


def curate(df: pd.DataFrame) -> pd.DataFrame:
    used: set = set()
    parts = []

    has = lambda a: df["aspects"].apply(lambda xs: a in xs)  # noqa: E731

    # 1. Keluhan ukuran berulang - kisah utama demo ("revisi size chart")
    parts.append(_pick(df, has("ukuran_varian") & (df["neg"] > df["pos"]), 26, used))
    # 2. Pujian pengiriman - memicu promotion highlight / opportunity
    parts.append(_pick(df, has("pengiriman") & (df["pos"] > df["neg"]), 24, used))
    # 3. Aspek lain supaya aspect aggregate tidak timpang
    for aspect, n in [
        ("kualitas_produk", 16), ("kesesuaian_deskripsi", 14), ("kemasan", 10),
        ("pelayanan_penjual", 10), ("harga_value", 8), ("keaslian", 5),
    ]:
        parts.append(_pick(df, has(aspect), n, used))
    # 4. Keluhan kualitas parah - menguji severity tinggi
    parts.append(_pick(df, has("kualitas_produk") & (df["neg"] > df["pos"]), 7, used))

    sample = pd.concat(parts).drop_duplicates(subset=["text"])

    # Pastikan kuota bahasa informal minimal 30% terpenuhi
    informal_share = sample["informal"].mean()
    if informal_share < 0.30:
        need = int(0.32 * len(sample)) - int(sample["informal"].sum())
        sample = pd.concat([sample, _pick(df, df["informal"], max(need, 0), used)])

    return sample.drop_duplicates(subset=["text"]).head(TARGET_TOTAL).reset_index(drop=True)


def to_raw_review_schema(sample: pd.DataFrame) -> pd.DataFrame:
    """Petakan ke schema Raw Review (blueprint bagian 25.1).

    `timestamp` DISINTESIS - dataset sumber tidak memuat tanggal. Keluhan ukuran sengaja
    dipadatkan pada 30 hari terakhir agar fitur tren dapat didemonstrasikan. Sifat sintetik
    ini dicatat eksplisit di data/samples/README.md; tanpa catatan itu, angka tren pada demo
    akan menyesatkan.
    """
    base = pd.Timestamp("2026-08-01")
    rows = []
    for i, r in enumerate(sample.itertuples(index=False)):
        is_size_complaint = "ukuran_varian" in r.aspects and r.neg > r.pos
        # keluhan ukuran -> 0-30 hari lalu; sisanya tersebar 30-90 hari lalu
        offset = (i * 7) % 30 if is_size_complaint else 30 + ((i * 11) % 60)
        rows.append({
            "review_id": f"demo_{i + 1:03d}",
            "text": r.text,
            "rating": int(r.rating),
            "timestamp": (base - pd.Timedelta(days=offset)).strftime("%Y-%m-%dT%H:%M:%S"),
            "product_id": str(r.product_id),
            "product_name": str(r.product_name)[:80],
            "category": "fashion",
            "variant": "",
            "image_paths": "",  # diisi pada Fase 3 setelah foto validasi tersedia
            "source": "sample_dataset",
        })
    return pd.DataFrame(rows)


def main() -> int:
    df = _load_fashion_reviews()
    sample = curate(df)
    out = to_raw_review_schema(sample)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_DIR / "demo_reviews.csv", index=False, encoding="utf-8")

    aspect_counts = {}
    for aspects in sample["aspects"]:
        for a in aspects:
            aspect_counts[a] = aspect_counts.get(a, 0) + 1
    stats = {
        "total_reviews": int(len(out)),
        "informal_share": round(float(sample["informal"].mean()), 3),
        "rating_distribution": {str(k): int(v) for k, v in out["rating"].value_counts().sort_index().items()},
        "aspect_mentions": dict(sorted(aspect_counts.items(), key=lambda x: -x[1])),
        "reviews_with_image": 0,
    }
    (OUT_DIR / "composition.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"dataset demo: {len(out)} ulasan -> {(OUT_DIR / 'demo_reviews.csv').relative_to(REPO_ROOT)}")
    print(f"  bahasa informal : {stats['informal_share']:.0%}")
    print("  penyebutan aspek:")
    for a, n in stats["aspect_mentions"].items():
        print(f"    {a:24s} {n}")
    print("  foto            : 0 (slot diisi pada Fase 3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
