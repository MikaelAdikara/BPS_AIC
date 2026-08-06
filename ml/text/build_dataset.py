"""Harmonisasi dataset + labeling function weak supervision (blueprint bagian 26.1, ADR-015).

Menghasilkan dataset klausa berlabel SILVER untuk melatih NLP-01:

    data/processed/clauses_train.csv
    data/processed/clauses_val.csv
    data/processed/clauses_test_silver.csv
    data/processed/build_report.json

PERINGATAN METODOLOGIS: label pada seluruh file di atas adalah SILVER (dihasilkan labeling
function), bukan label manusia. Metrik apa pun yang diukur pada `clauses_test_silver.csv`
mengukur KECOCOKAN TERHADAP LABELING FUNCTION, bukan akurasi sebenarnya. Angka yang boleh
masuk proposal hanya yang diukur pada gold test set berlabel manusia
(lihat `make_gold_task.py`).

Pemakaian:
    python ml/text/build_dataset.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lexicon import (  # noqa: E402
    ALL_ASPECTS,
    ASPECT_PATTERNS,
    FALLBACK_ASPECT,
    FALLBACK_PATTERN,
)
from preprocess import normalize, polarity_score, split_clauses  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW = REPO_ROOT / "data" / "raw"
OUT = REPO_ROOT / "data" / "processed"

SEED = 42  # bagian 26.1 langkah 18: seed di-fix dan dicatat eksplisit

# Pemetaan kategori sumber -> enum kategori kita (schema bagian 25.1, taxonomy FROZEN)
PRDECT_CATEGORY_MAP = {
    "Women's Fashion": "fashion", "Men's Fashion": "fashion",
    "Muslim Fashion": "fashion", "Kids and Baby Fashion": "fashion",
    "Food and Drink": "food_beverage",
    "Party Supplies and Craft": "craft", "Carpentry": "craft",
    "Computers and Laptops": "electronics", "Electronics": "electronics",
    "Phones and Tablets": "electronics", "Camera": "electronics", "Gaming": "electronics",
}
TOKOPEDIA_CATEGORY_MAP = {
    "elektronik": "electronics", "handphone": "electronics",
    "fashion": "fashion", "pertukangan": "craft", "olahraga": "other",
}


def _load_prdect() -> pd.DataFrame:
    path = RAW / "prdect_id" / "PRDECT-ID Dataset.csv"
    df = pd.read_csv(path)
    return pd.DataFrame({
        "source": "prdect_id",
        "raw_text": df["Customer Review"],
        "rating": df["Customer Rating"],
        "product_key": "prdect::" + df["Product Name"].astype(str),
        "category": df["Category"].map(PRDECT_CATEGORY_MAP).fillna("other"),
        # Label sentimen manusia (biner) - dipakai sebagai prior tingkat ulasan.
        "review_sentiment": df["Sentiment"].str.lower().map(
            {"positive": "positif", "negative": "negatif"}
        ),
        "review_sentiment_origin": "human_label",
    })


def _load_tokopedia() -> pd.DataFrame:
    path = RAW / "tokopedia_reviews_2019" / "tokopedia-product-reviews-2019.csv"
    df = pd.read_csv(path)
    # Tidak ada label sentimen - diturunkan dari rating (weak label, didokumentasikan).
    sentiment = pd.cut(
        df["rating"], bins=[0, 2, 3, 5], labels=["negatif", "netral", "positif"]
    ).astype(str)
    return pd.DataFrame({
        "source": "tokopedia_2019",
        "raw_text": df["text"],
        "rating": df["rating"],
        "product_key": "tokopedia::" + df["product_id"].astype(str),
        "category": df["category"].map(TOKOPEDIA_CATEGORY_MAP).fillna("other"),
        "review_sentiment": sentiment,
        "review_sentiment_origin": "derived_from_rating",
    })


def _clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Bersihkan baris kosong/rusak dan buang duplikat (bagian 26.1 langkah 5)."""
    before = len(df)
    df = df[df["raw_text"].notna()].copy()
    df["text"] = df["raw_text"].astype(str).map(normalize)
    df = df[df["text"].str.len() >= 5]
    empty_removed = before - len(df)

    before_dedupe = len(df)
    # Dedupe pada teks TERNORMALISASI, bukan mentah - menangkap near-duplicate yang hanya
    # berbeda kapitalisasi/huruf berulang/slang.
    df = df.drop_duplicates(subset=["source", "text"], keep="first")
    dup_removed = before_dedupe - len(df)

    df = df.reset_index(drop=True)
    df["review_id"] = [f"r{i:06d}" for i in range(len(df))]
    return df, {"empty_or_short_removed": empty_removed, "duplicates_removed": dup_removed}


def _label_clause(clause: str, review_sentiment: str, rating: float) -> dict:
    """Labeling function: aspek multi-label + sentimen + severity untuk satu klausa."""
    aspects = [a for a, pat in ASPECT_PATTERNS.items() if pat.search(clause)]
    # Rujukan produk generik ("barangnya bagus") hanya memicu kualitas_produk bila tidak ada
    # aspek lain yang lebih spesifik terdeteksi - lihat catatan FALLBACK_TERMS di lexicon.py.
    if not aspects and FALLBACK_PATTERN.search(clause):
        aspects = [FALLBACK_ASPECT]

    pos, neg = polarity_score(clause)
    if pos > neg:
        sentiment, origin = "positif", "clause_polarity"
    elif neg > pos:
        sentiment, origin = "negatif", "clause_polarity"
    else:
        # Klausa tanpa sinyal polaritas dilabeli NETRAL, bukan mewarisi sentimen ulasan.
        #
        # Aturan lama (`review_prior`) terbukti merusak. Karena 84% ulasan berlabel positif,
        # hampir seluruh klausa tanpa sinyal ikut jadi positif - termasuk pernyataan datar
        # seperti "paket sudah diterima". Akibatnya kelas netral hanya 2,3% dari data latih,
        # model belajar bahwa netral nyaris tidak pernah benar, lalu berhenti memprediksinya
        # (F1 netral 0,02-0,28 di semua evaluasi Fase 2).
        #
        # Diukur pada gold: dengan aturan ini macro F1 leksikon 0,658, dibanding 0,497 bila
        # memakai prior ulasan. Sentimen adalah properti klausa - klausa tanpa muatan
        # penilaian memang netral, terlepas dari rating ulasannya.
        sentiment, origin = "netral", "no_polarity_signal"

    # Severity deterministic dari rating (heuristik, didokumentasikan di DATASET_CARD).
    if sentiment != "negatif":
        severity = "rendah"
    elif pd.isna(rating):
        severity = "sedang"
    elif rating <= 2:
        severity = "tinggi"
    elif rating == 3:
        severity = "sedang"
    else:
        severity = "rendah"

    return {
        "aspects": aspects,
        "sentiment": sentiment,
        "sentiment_origin": origin,
        "severity": severity,
        "pos_signals": pos,
        "neg_signals": neg,
    }


def _explode_clauses(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in df.itertuples(index=False):
        for idx, clause in enumerate(split_clauses(row.text)):
            label = _label_clause(clause, row.review_sentiment, row.rating)
            rows.append({
                "review_id": row.review_id,
                "clause_id": f"{row.review_id}_c{idx}",
                "source": row.source,
                "product_key": row.product_key,
                "category": row.category,
                "rating": row.rating,
                "clause_text": clause,
                "sentiment": label["sentiment"],
                "sentiment_origin": label["sentiment_origin"],
                "severity": label["severity"],
                "n_aspects": len(label["aspects"]),
                **{f"asp_{a}": int(a in label["aspects"]) for a in ALL_ASPECTS},
            })
    return pd.DataFrame(rows)


def _product_level_split(
    clauses: pd.DataFrame, seed: int = SEED
) -> dict[str, pd.DataFrame]:
    """Split 70/15/15 di tingkat PRODUK, bukan per baris (bagian 26.1 langkah 6).

    Ulasan dari produk yang sama tidak boleh tersebar ke lebih dari satu split - kalau
    tidak, kemiripan antar ulasan satu produk menciptakan kebocoran yang membuat metrik
    terlihat lebih baik dari kenyataannya.
    """
    products = pd.Series(clauses["product_key"].unique())
    products = products.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    n = len(products)
    n_train, n_val = int(n * 0.70), int(n * 0.15)
    assignment = {
        **{p: "train" for p in products[:n_train]},
        **{p: "val" for p in products[n_train : n_train + n_val]},
        **{p: "test" for p in products[n_train + n_val :]},
    }
    clauses = clauses.assign(split=clauses["product_key"].map(assignment))
    return {s: clauses[clauses["split"] == s].reset_index(drop=True) for s in ("train", "val", "test")}


def _verify_no_leakage(splits: dict[str, pd.DataFrame]) -> dict:
    """Verifikasi eksplisit tanpa leakage (bagian 26.1 langkah 7)."""
    findings: dict[str, object] = {}
    names = list(splits)

    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            shared_products = set(splits[a]["product_key"]) & set(splits[b]["product_key"])
            shared_reviews = set(splits[a]["review_id"]) & set(splits[b]["review_id"])
            shared_text = set(splits[a]["clause_text"]) & set(splits[b]["clause_text"])
            findings[f"{a}_vs_{b}"] = {
                "shared_products": len(shared_products),
                "shared_review_ids": len(shared_reviews),
                "identical_clause_texts": len(shared_text),
            }

    findings["product_leakage_clean"] = all(
        v["shared_products"] == 0 and v["shared_review_ids"] == 0  # type: ignore[index]
        for k, v in findings.items()
        if k != "product_leakage_clean"
    )
    return findings


def main() -> int:
    if not (RAW / "prdect_id").exists():
        print("data/raw kosong - jalankan scripts/download_datasets.py lebih dulu.", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    print("memuat dataset ...")
    reviews = pd.concat([_load_prdect(), _load_tokopedia()], ignore_index=True)
    reviews, clean_stats = _clean(reviews)
    print(f"  ulasan bersih: {len(reviews)}  ({clean_stats})")

    print("segmentasi klausa + labeling function ...")
    clauses = _explode_clauses(reviews)
    print(f"  klausa: {len(clauses)}")

    splits = _product_level_split(clauses)
    leakage = _verify_no_leakage(splits)

    filenames = {"train": "clauses_train.csv", "val": "clauses_val.csv", "test": "clauses_test_silver.csv"}
    for name, frame in splits.items():
        frame.to_csv(OUT / filenames[name], index=False, encoding="utf-8")
        print(f"  {filenames[name]}: {len(frame)} klausa, {frame['product_key'].nunique()} produk")

    aspect_counts = {a: int(clauses[f"asp_{a}"].sum()) for a in ALL_ASPECTS}
    report = {
        "seed": SEED,
        "label_type": "SILVER (labeling function, bukan label manusia) - lihat ADR-015",
        "reviews_after_cleaning": int(len(reviews)),
        "clauses_total": int(len(clauses)),
        "cleaning": clean_stats,
        "source_distribution": {k: int(v) for k, v in reviews["source"].value_counts().items()},
        "category_distribution": {k: int(v) for k, v in reviews["category"].value_counts().items()},
        "sentiment_distribution": {k: int(v) for k, v in clauses["sentiment"].value_counts().items()},
        "sentiment_origin": {k: int(v) for k, v in clauses["sentiment_origin"].value_counts().items()},
        "severity_distribution": {k: int(v) for k, v in clauses["severity"].value_counts().items()},
        "aspect_positive_counts": aspect_counts,
        "clauses_without_aspect": int((clauses["n_aspects"] == 0).sum()),
        "split_sizes": {k: int(len(v)) for k, v in splits.items()},
        "leakage_check": leakage,
    }
    (OUT / "build_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\nleakage check:", "BERSIH" if leakage["product_leakage_clean"] else "ADA MASALAH")
    for k, v in leakage.items():
        if k != "product_leakage_clean":
            print(f"  {k}: {v}")
    print(f"\nlaporan: {(OUT / 'build_report.json').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
