"""Validasi labeling function sentimen - DAN temuan bahwa validasi ini tidak dapat dipakai.

Maksud awal: baseline Fase 1 menunjukkan kelas `netral` runtuh pada label silver (F1 0,113)
namun wajar pada `challange.json` (F1 0,609), sehingga muncul dugaan aturan silver-lah yang
bermasalah. Script ini dibuat untuk membandingkan beberapa varian aturan terhadap label
`challange.json` yang diasumsikan independen.

HASIL PEMERIKSAAN: asumsi itu SALAH. Label sentimen `challange.json` ternyata 98,3% identik
dengan sentimen yang diturunkan langsung dari kolom `rating` (`simple.json` bahkan 100%).
Artinya label itu bukan penilaian independen atas teks, melainkan pemetaan rating.

Konsekuensinya, varian aturan yang ikut memakai rating sebagai prior akan tampak unggul secara
artifisial - ia sedang dinilai terhadap sumber yang sama dengan yang dipakainya. Perbandingan
varian di bawah karena itu TIDAK DIPAKAI sebagai dasar keputusan. Script tetap dipertahankan
karena pemeriksaan kontaminasinya sendiri berguna dan perlu dapat diulang.

Pemilihan aturan sentimen final ditunda sampai gold test set berlabel manusia selesai
(`data/annotation/gold_annotation_task.csv`).

Pemakaian:
    python ml/text/validate_lf.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import classification_report, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preprocess import normalize, polarity_score  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW = REPO_ROOT / "data" / "raw"
EVAL_OUT = REPO_ROOT / "ml" / "evaluation"


def _rating_sentiment(rating: float) -> str:
    if pd.isna(rating):
        return "netral"
    if rating >= 4:
        return "positif"
    if rating == 3:
        return "netral"
    return "negatif"


def variant_a(clause: str, rating: float) -> str:
    """A - aturan Fase 1: polaritas klausa, jika kosong pakai prior tingkat ulasan."""
    pos, neg = polarity_score(clause)
    if pos > neg:
        return "positif"
    if neg > pos:
        return "negatif"
    return _rating_sentiment(rating)


def variant_b(clause: str, rating: float) -> str:
    """B - klausa tanpa sinyal polaritas dianggap NETRAL, prior diabaikan.

    Dasar pemikiran: sentimen adalah properti klausa. Klausa yang tidak memuat penilaian
    ("paket sudah diterima") memang netral, terlepas dari rating keseluruhan ulasan.
    """
    pos, neg = polarity_score(clause)
    if pos > neg:
        return "positif"
    if neg > pos:
        return "negatif"
    return "netral"


def variant_c(clause: str, rating: float) -> str:
    """C - jalan tengah: prior hanya dipakai jika ulasan sangat terpolarisasi (1-2 atau 5).

    Rating 3-4 dianggap terlalu lemah untuk menyimpulkan sentimen sebuah klausa tanpa sinyal.
    """
    pos, neg = polarity_score(clause)
    if pos > neg:
        return "positif"
    if neg > pos:
        return "negatif"
    if pd.isna(rating):
        return "netral"
    if rating <= 2:
        return "negatif"
    if rating == 5:
        return "positif"
    return "netral"


VARIANTS = {
    "A_prior_penuh (Fase 1)": variant_a,
    "B_tanpa_sinyal_netral": variant_b,
    "C_prior_hanya_terpolarisasi": variant_c,
}


def main() -> int:
    path = RAW / "ecommerce_sentiment" / "challange.json"
    if not path.exists():
        print("challange.json tidak ada - jalankan scripts/download_datasets.py.", file=sys.stderr)
        return 1

    df = pd.DataFrame(json.loads(path.read_text(encoding="utf-8")))
    df["text"] = df["comment"].map(normalize)
    df["gold"] = df["sentiment"].map(
        {"positive": "positif", "negative": "negatif", "neutral": "netral"}
    )
    df = df[df["text"].str.len() >= 3].reset_index(drop=True)

    # --- Pemeriksaan kontaminasi: apakah label sekadar pemetaan dari rating? ---
    derived = df["rating"].apply(_rating_sentiment)
    contamination = float((df["gold"] == derived).mean())

    results = {
        "dataset": "challange.json",
        "n": int(len(df)),
        "contamination_check": {
            "label_vs_rating_derived_agreement": round(contamination, 4),
            "verdict": (
                "TERKONTAMINASI - label pada dasarnya adalah pemetaan rating, bukan penilaian "
                "independen atas teks"
                if contamination > 0.9
                else "label tampak independen dari rating"
            ),
        },
        "usable_for_variant_selection": contamination <= 0.9,
        "variants": {},
    }

    print(f"pemeriksaan kontaminasi: label vs sentimen-turunan-rating = {contamination:.1%}")
    if contamination > 0.9:
        print(
            "  -> label BUKAN penilaian independen atas teks.\n"
            "     Perbandingan varian di bawah tidak dipakai sebagai dasar keputusan:\n"
            "     varian yang memakai rating dinilai terhadap sumbernya sendiri.\n"
        )
    print(f"membandingkan varian aturan sentimen pada {len(df)} baris (untuk catatan saja)\n")
    for name, fn in VARIANTS.items():
        pred = [fn(t, r) for t, r in zip(df["text"], df["rating"])]
        rep = classification_report(df["gold"], pred, output_dict=True, zero_division=0)
        macro = float(f1_score(df["gold"], pred, average="macro", zero_division=0))
        per_class = {
            k: round(float(v["f1-score"]), 4)
            for k, v in rep.items()
            if k in ("positif", "negatif", "netral")
        }
        results["variants"][name] = {  # type: ignore[index]
            "macro_f1": round(macro, 4),
            "per_class_f1": per_class,
            "predicted_distribution": {
                k: int(v) for k, v in pd.Series(pred).value_counts().items()
            },
        }
        print(f"  {name:32s} macro F1 {macro:.4f}   per-kelas {per_class}")

    EVAL_OUT.mkdir(parents=True, exist_ok=True)
    out = EVAL_OUT / "lf_sentiment_validation.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nhasil: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
