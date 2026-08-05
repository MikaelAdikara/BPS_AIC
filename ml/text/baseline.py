"""Baseline TF-IDF + Logistic Regression (blueprint bagian 26.1 langkah 12, bagian 34 #3).

Baseline ini WAJIB dijalankan dan dicatat SEBELUM ada klaim bahwa model fine-tuned lebih baik.
Ia juga menjadi fallback deterministic runtime untuk NLP-01 saat model neural gagal dimuat
(bagian 17.1, 20 blueprint).

Dua task terpisah, sesuai keputusan dua head terpisah pada bagian 18.1:
  1. Aspek   - multi-label, 11 kelas (One-vs-Rest)
  2. Sentimen - 3 kelas (positif/negatif/netral)

CARA MEMBACA ANGKANYA:
  - `silver_test`        : diukur pada label silver. Mengukur KECOCOKAN TERHADAP LABELING
                           FUNCTION, bukan akurasi sebenarnya. TIDAK BOLEH masuk proposal
                           sebagai klaim akurasi.
  - `silver_test_unseen` : subset silver_test yang teks klausanya tidak pernah muncul di train.
                           Menghilangkan efek hafalan frasa generik ("barang bagus").
  - `stress_challange`   : sentimen pada challange.json (4.840 baris, label bukan dari LF kita).
                           Ini satu-satunya angka di file ini yang labelnya independen.

Angka final untuk proposal baru tersedia setelah gold test set berlabel manusia selesai
(lihat make_gold_task.py).

Pemakaian:
    python ml/text/baseline.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lexicon import ALL_ASPECTS  # noqa: E402
from preprocess import normalize  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = REPO_ROOT / "data" / "processed"
RAW = REPO_ROOT / "data" / "raw"
EVAL_OUT = REPO_ROOT / "ml" / "evaluation"

SEED = 42
ASPECT_COLS = [f"asp_{a}" for a in ALL_ASPECTS]


def _vectorizer() -> TfidfVectorizer:
    # Karakter n-gram ikut dipakai karena Bahasa Indonesia informal penuh typo dan singkatan
    # sehingga token utuh sering meleset ("bagusss", "pngiriman").
    return TfidfVectorizer(
        analyzer="char_wb", ngram_range=(3, 5), min_df=3, max_features=200_000, sublinear_tf=True
    )


def _fit_sentiment(train: pd.DataFrame) -> Pipeline:
    pipe = Pipeline([
        ("tfidf", _vectorizer()),
        ("clf", LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=SEED, n_jobs=-1
        )),
    ])
    pipe.fit(train["clause_text"], train["sentiment"])
    return pipe


def _fit_aspects(train: pd.DataFrame) -> Pipeline:
    pipe = Pipeline([
        ("tfidf", _vectorizer()),
        ("clf", OneVsRestClassifier(
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED),
            n_jobs=-1,
        )),
    ])
    pipe.fit(train["clause_text"], train[ASPECT_COLS].values)
    return pipe


def _eval_sentiment(pipe: Pipeline, df: pd.DataFrame, label: str) -> dict:
    pred = pipe.predict(df["clause_text"])
    rep = classification_report(df["sentiment"], pred, output_dict=True, zero_division=0)
    return {
        "n": int(len(df)),
        "macro_f1": round(float(f1_score(df["sentiment"], pred, average="macro", zero_division=0)), 4),
        "per_class_f1": {
            k: round(float(v["f1-score"]), 4)
            for k, v in rep.items()
            if k in ("positif", "negatif", "netral")
        },
        "support": {
            k: int(v["support"]) for k, v in rep.items() if k in ("positif", "negatif", "netral")
        },
        "_label": label,
    }


def _eval_aspects(pipe: Pipeline, df: pd.DataFrame, label: str) -> dict:
    y_true = df[ASPECT_COLS].values
    y_pred = pipe.predict(df["clause_text"])
    per_class = {}
    for i, aspect in enumerate(ALL_ASPECTS):
        per_class[aspect] = {
            "f1": round(float(f1_score(y_true[:, i], y_pred[:, i], zero_division=0)), 4),
            "support": int(y_true[:, i].sum()),
        }
    return {
        "n": int(len(df)),
        "macro_f1": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "micro_f1": round(float(f1_score(y_true, y_pred, average="micro", zero_division=0)), 4),
        "per_class": per_class,
        "_label": label,
    }


def _load_stress_set() -> pd.DataFrame | None:
    """challange.json sebagai stress test sentimen (ADR-016)."""
    path = RAW / "ecommerce_sentiment" / "challange.json"
    if not path.exists():
        return None
    df = pd.DataFrame(json.loads(path.read_text(encoding="utf-8")))
    df["clause_text"] = df["comment"].map(normalize)
    df["sentiment"] = df["sentiment"].map(
        {"positive": "positif", "negative": "negatif", "neutral": "netral"}
    )
    return df[df["clause_text"].str.len() >= 3][["clause_text", "sentiment", "category"]]


def main() -> int:
    if not (PROCESSED / "clauses_train.csv").exists():
        print("Jalankan ml/text/build_dataset.py lebih dulu.", file=sys.stderr)
        return 1

    train = pd.read_csv(PROCESSED / "clauses_train.csv")
    test = pd.read_csv(PROCESSED / "clauses_test_silver.csv")
    for frame in (train, test):
        frame["clause_text"] = frame["clause_text"].fillna("").astype(str)

    # Subset "unseen": klausa yang teksnya tidak pernah muncul di train. Angka pada subset ini
    # lebih jujur karena bebas dari hafalan frasa generik yang berulang lintas produk.
    seen = set(train["clause_text"])
    unseen = test[~test["clause_text"].isin(seen)].reset_index(drop=True)

    results: dict[str, object] = {
        "seed": SEED,
        "model": "TF-IDF(char_wb 3-5) + LogisticRegression(class_weight=balanced)",
        "train_clauses": int(len(train)),
        "label_warning": (
            "silver_* diukur pada label labeling function (ADR-015), BUKAN akurasi sebenarnya. "
            "Hanya stress_challange yang labelnya independen dari LF kita."
        ),
    }

    print("melatih baseline sentimen ...")
    t0 = time.time()
    sent_pipe = _fit_sentiment(train)
    results["sentiment_fit_seconds"] = round(time.time() - t0, 1)
    results["sentiment"] = {
        "silver_test": _eval_sentiment(sent_pipe, test, "silver_test"),
        "silver_test_unseen": _eval_sentiment(sent_pipe, unseen, "silver_test_unseen"),
    }

    stress = _load_stress_set()
    if stress is not None:
        overall = _eval_sentiment(sent_pipe, stress, "stress_challange")
        by_phenomenon = {}
        for phenomenon, group in stress.groupby("category"):
            if len(group) >= 25:
                by_phenomenon[phenomenon] = _eval_sentiment(
                    sent_pipe, group, f"stress::{phenomenon}"
                )["macro_f1"]
        overall["by_phenomenon_macro_f1"] = dict(sorted(by_phenomenon.items(), key=lambda x: x[1]))
        results["sentiment"]["stress_challange"] = overall  # type: ignore[index]

    print("melatih baseline aspek (multi-label, 11 kelas) ...")
    t0 = time.time()
    asp_pipe = _fit_aspects(train)
    results["aspect_fit_seconds"] = round(time.time() - t0, 1)
    results["aspect"] = {
        "silver_test": _eval_aspects(asp_pipe, test, "silver_test"),
        "silver_test_unseen": _eval_aspects(asp_pipe, unseen, "silver_test_unseen"),
    }

    EVAL_OUT.mkdir(parents=True, exist_ok=True)
    out = EVAL_OUT / "baseline_results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    s, a = results["sentiment"], results["aspect"]  # type: ignore[index]
    print("\n--- SENTIMEN (macro F1)")
    print(f"  silver_test        : {s['silver_test']['macro_f1']}  (n={s['silver_test']['n']})")
    print(f"  silver_test_unseen : {s['silver_test_unseen']['macro_f1']}  (n={s['silver_test_unseen']['n']})")
    if "stress_challange" in s:
        print(f"  stress_challange   : {s['stress_challange']['macro_f1']}  (n={s['stress_challange']['n']})  <- label independen")
    print("\n--- ASPEK (macro F1 multi-label)")
    print(f"  silver_test        : {a['silver_test']['macro_f1']}  (micro {a['silver_test']['micro_f1']})")
    print(f"  silver_test_unseen : {a['silver_test_unseen']['macro_f1']}  (micro {a['silver_test_unseen']['micro_f1']})")
    print(f"\nhasil: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
