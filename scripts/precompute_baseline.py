"""Hitung baseline kategori untuk BEN-01 (blueprint bagian 24.1, ADR-012).

Dijalankan SEKALI saat persiapan, bukan saat pengguna membuka hasil. Keluarannya artifact
statis `data/processed/category_baseline.json` yang dimuat backend saat startup - tidak ada
panggilan keluar apa pun saat analisis berjalan.

Unit pengukuran adalah ULASAN, bukan klausa: "berapa persen ulasan pada kategori ini yang
mengeluhkan aspek X". Ini penyebut yang sama dipakai `store_pct` pada sisi pengguna, sehingga
kedua angka benar-benar sebanding.

KETERBATASAN YANG MELEKAT: baseline dihitung dari label silver (ADR-015), sehingga mewarisi
kualitas labeling function. Ia juga historis dan statis - bukan pemantauan pasar real-time.
Keduanya wajib disebut saat angka ini ditampilkan (bagian 24.1).

Pemakaian:
    python scripts/precompute_baseline.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "ml" / "text"))

from lexicon import ALL_ASPECTS  # noqa: E402

PROCESSED = REPO_ROOT / "data" / "processed"
OUT_PATH = PROCESSED / "category_baseline.json"

# Kategori dengan ulasan lebih sedikit dari ini tetap dihitung tetapi ditandai jelas -
# menyembunyikannya akan membuat pengguna mengira kategorinya tidak didukung.
MIN_REVIEWS_TO_REPORT = 30


def load_all_clauses() -> pd.DataFrame:
    frames = []
    for name in ("clauses_train.csv", "clauses_val.csv", "clauses_test_silver.csv"):
        path = PROCESSED / name
        if path.exists():
            frames.append(pd.read_csv(path))
    if not frames:
        print("data/processed kosong - jalankan ml/text/build_dataset.py lebih dulu.", file=sys.stderr)
        raise SystemExit(1)
    return pd.concat(frames, ignore_index=True)


def compute_baseline(clauses: pd.DataFrame) -> dict:
    categories: dict[str, dict] = {}

    for category, group in clauses.groupby("category"):
        total_reviews = group["review_id"].nunique()
        aspects: dict[str, dict] = {}

        for aspect in ALL_ASPECTS:
            col = f"asp_{aspect}"
            if col not in group.columns:
                continue

            negative = group[(group[col] == 1) & (group["sentiment"] == "negatif")]
            reviews_with_complaint = negative["review_id"].nunique()

            mentioned = group[group[col] == 1]
            reviews_mentioning = mentioned["review_id"].nunique()

            aspects[aspect] = {
                "pct_negative": round(reviews_with_complaint / total_reviews, 4) if total_reviews else 0.0,
                "pct_mentioned": round(reviews_mentioning / total_reviews, 4) if total_reviews else 0.0,
                "reviews_with_complaint": int(reviews_with_complaint),
                "sample_size": int(total_reviews),
            }

        categories[str(category)] = {
            "sample_size": int(total_reviews),
            "sufficient": bool(total_reviews >= MIN_REVIEWS_TO_REPORT),
            "aspects": aspects,
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "unit": "proporsi ULASAN yang memuat keluhan pada aspek tersebut",
        "label_source": "SILVER - labeling function (ADR-015), bukan label manusia",
        "limitations": [
            "Baseline bersifat historis dan statis, bukan pemantauan pasar real-time.",
            "Dataset publik cenderung berasal dari toko besar/aktif sehingga belum tentu "
            "mewakili UMKM mikro (dossier bagian 14.2).",
            "Kualitas baseline terikat pada kualitas labeling function yang membuatnya.",
        ],
        "min_reviews_to_report": MIN_REVIEWS_TO_REPORT,
        "categories": categories,
    }


def main() -> int:
    clauses = load_all_clauses()
    baseline = compute_baseline(clauses)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(baseline, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"baseline kategori -> {OUT_PATH.relative_to(REPO_ROOT)}")
    for category, data in sorted(
        baseline["categories"].items(), key=lambda kv: -kv[1]["sample_size"]
    ):
        flag = "" if data["sufficient"] else "  [sampel kecil]"
        print(f"\n  {category}  (n={data['sample_size']} ulasan){flag}")
        top = sorted(data["aspects"].items(), key=lambda kv: -kv[1]["pct_negative"])[:5]
        for aspect, entry in top:
            print(f"     {aspect:24s} keluhan {entry['pct_negative']:6.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
