"""Evaluasi pada GOLD TEST SET — satu-satunya angka NLP-01 yang layak dikutip.

Membandingkan tiga pendekatan pada label gold yang sama (blueprint bagian 34 baseline #2 dan #3):

    1. Labeling function leksikon  — pendekatan rule-based
    2. TF-IDF + Logistic Regression — baseline statistik
    3. IndoBERT fine-tuned          — model utama

ASAL-USUL LABEL GOLD, dibaca apa adanya (ADR-017):
Label berasal dari pembacaan semantik LLM atas 500 klausa, lalu ditinjau dan disetujui tim.
Untuk 302 baris yang leksikon dan LLM berbeda, tim memutuskan kolom LLM yang benar; 198 baris
sisanya sudah disepakati kedua sumber sejak awal.

Konsekuensinya harus disebut terang-terangan: seluruh label gold berasal dari satu sumber
pembacaan yang sama, disetujui manusia — BUKAN anotasi manusia independen dari nol. Angka di
bawah karena itu mengukur kesesuaian model terhadap pembacaan tersebut. Ia jauh lebih bermakna
daripada metrik silver (yang sirkular terhadap leksikon), tetapi tidak setara dengan gold yang
dianotasi manusia secara independen.

Pemakaian:
    python ml/text/evaluate_gold.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO_ROOT / "data" / "annotation"))

from _preannotation_raw import ANNOTATIONS  # noqa: E402
from lexicon import ALL_ASPECTS, ASPECT_PATTERNS, FALLBACK_ASPECT, FALLBACK_PATTERN  # noqa: E402
from preprocess import polarity_score  # noqa: E402

ANNOT = REPO_ROOT / "data" / "annotation"
PROCESSED = REPO_ROOT / "data" / "processed"
EVAL_OUT = REPO_ROOT / "ml" / "evaluation"
CHECKPOINT = REPO_ROOT / "models" / "indobert-nlp01" / "model.pt"

SEED = 42
SENTIMENTS = ["negatif", "netral", "positif"]
ASPECT_CODE = {
    "kp": "kualitas_produk", "kd": "kesesuaian_deskripsi", "hv": "harga_value",
    "km": "kemasan", "pg": "pengiriman", "pp": "pelayanan_penjual",
    "uv": "ukuran_varian", "rm": "rasa_kualitas_makanan", "kl": "kelengkapan",
    "ka": "keaslian", "ku": "kemudahan_penggunaan",
}
SENTIMENT_CODE = {"p": "positif", "n": "negatif", "e": "netral"}
SEVERITY_CODE = {"r": "rendah", "s": "sedang", "t": "tinggi", "": ""}


def build_gold() -> pd.DataFrame:
    """Susun gold set 500 baris dan simpan sebagai artifact yang di-commit."""
    task = pd.read_csv(ANNOT / "gold_annotation_task.csv")
    rows = []
    for i, row in task.iterrows():
        aspects, sentiment, severity = ANNOTATIONS[i].split(";")
        rows.append({
            "clause_id": row.clause_id,
            "clause_text": row.clause_text,
            "category_produk": row.category_produk,
            **{f"asp_{a}": 0 for a in ALL_ASPECTS},
            "sentimen": SENTIMENT_CODE[sentiment],
            "severity": SEVERITY_CODE[severity],
        })
        for code in aspects.split(","):
            if code:
                rows[-1][f"asp_{ASPECT_CODE[code]}"] = 1
    gold = pd.DataFrame(rows)
    gold.to_csv(ANNOT / "gold_labels.csv", index=False, encoding="utf-8")
    return gold


def predict_lexicon(texts: list[str]) -> tuple[np.ndarray, list[str]]:
    """Pendekatan rule-based murni — pembanding wajib bagian 34 baseline #2."""
    aspect_pred = np.zeros((len(texts), len(ALL_ASPECTS)), dtype=int)
    sentiments = []
    for i, text in enumerate(texts):
        low = text.lower()
        found = [a for a, pat in ASPECT_PATTERNS.items() if pat.search(low)]
        if not found and FALLBACK_PATTERN.search(low):
            found = [FALLBACK_ASPECT]
        for a in found:
            aspect_pred[i, ALL_ASPECTS.index(a)] = 1
        pos, neg = polarity_score(low)
        sentiments.append("positif" if pos > neg else "negatif" if neg > pos else "netral")
    return aspect_pred, sentiments


def predict_tfidf(train: pd.DataFrame, texts: list[str]) -> tuple[np.ndarray, list[str]]:
    aspect_cols = [f"asp_{a}" for a in ALL_ASPECTS]
    vec = lambda: TfidfVectorizer(  # noqa: E731
        analyzer="char_wb", ngram_range=(3, 5), min_df=3, max_features=200_000, sublinear_tf=True
    )
    asp = Pipeline([("t", vec()), ("c", OneVsRestClassifier(
        LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED)))])
    asp.fit(train["clause_text"], train[aspect_cols].values)

    sent = Pipeline([("t", vec()), ("c", LogisticRegression(
        max_iter=2000, class_weight="balanced", random_state=SEED))])
    sent.fit(train["clause_text"], train["sentiment"])
    return asp.predict(texts), list(sent.predict(texts))


def predict_indobert(texts: list[str]) -> tuple[np.ndarray, list[str]] | None:
    if not CHECKPOINT.exists():
        return None
    import torch  # noqa: PLC0415
    from transformers import AutoTokenizer  # noqa: PLC0415

    from finetune import DualHeadClassifier  # noqa: PLC0415

    bundle = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    model = DualHeadClassifier(bundle["base_model"])
    model.load_state_dict(bundle["state_dict"])
    model.eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    tokenizer = AutoTokenizer.from_pretrained(str(CHECKPOINT.parent))
    threshold = float(bundle.get("aspect_threshold", 0.5))
    order = [ALL_ASPECTS.index(a) for a in bundle["aspects"]]

    probs, sents = [], []
    with torch.no_grad():
        for start in range(0, len(texts), 128):
            batch = texts[start : start + 128]
            enc = tokenizer(batch, truncation=True, max_length=32, padding=True,
                            return_tensors="pt").to(device)
            asp_logits, sent_logits = model(enc["input_ids"], enc["attention_mask"])
            probs.append(torch.sigmoid(asp_logits).cpu().numpy())
            sents.extend(SENTIMENTS[i] for i in sent_logits.argmax(-1).cpu().numpy())
    prob = np.vstack(probs)
    aligned = np.zeros_like(prob)
    for src, dst in enumerate(order):
        aligned[:, dst] = prob[:, src]
    return (aligned >= threshold).astype(int), sents


def score(y_aspect, pred_aspect, y_sent, pred_sent) -> dict:
    per_class = {
        a: {
            "f1": round(float(f1_score(y_aspect[:, i], pred_aspect[:, i], zero_division=0)), 4),
            "support": int(y_aspect[:, i].sum()),
        }
        for i, a in enumerate(ALL_ASPECTS)
    }
    rep = classification_report(y_sent, pred_sent, output_dict=True, zero_division=0)
    return {
        "aspect_macro_f1": round(float(f1_score(y_aspect, pred_aspect, average="macro", zero_division=0)), 4),
        "aspect_micro_f1": round(float(f1_score(y_aspect, pred_aspect, average="micro", zero_division=0)), 4),
        "aspect_per_class": per_class,
        "sentiment_macro_f1": round(float(f1_score(y_sent, pred_sent, average="macro", zero_division=0)), 4),
        "sentiment_per_class": {
            s: round(float(rep[s]["f1-score"]), 4) for s in SENTIMENTS if s in rep
        },
    }


def main() -> int:
    gold = build_gold()
    texts = gold["clause_text"].astype(str).tolist()
    y_aspect = gold[[f"asp_{a}" for a in ALL_ASPECTS]].values
    y_sent = gold["sentimen"].tolist()

    train = pd.read_csv(PROCESSED / "clauses_train.csv")
    train["clause_text"] = train["clause_text"].fillna("").astype(str)

    results = {
        "gold_provenance": (
            "Pembacaan semantik LLM atas 500 klausa, ditinjau dan disetujui tim (ADR-017). "
            "Untuk 302 baris yang leksikon dan LLM berbeda, tim memutuskan kolom LLM benar. "
            "BUKAN anotasi manusia independen dari nol - seluruh label berasal dari satu sumber "
            "pembacaan yang sama."
        ),
        "n_gold": int(len(gold)),
        "aspect_label_density": round(float(y_aspect.sum() / len(gold)), 3),
        "sentiment_distribution": {k: int(v) for k, v in gold["sentimen"].value_counts().items()},
        "models": {},
    }

    print(f"gold set: {len(gold)} klausa\n")

    print("1/3 labeling function leksikon ...")
    a, s = predict_lexicon(texts)
    results["models"]["lexicon_rule_based"] = score(y_aspect, a, y_sent, s)

    print("2/3 TF-IDF + Logistic Regression ...")
    a, s = predict_tfidf(train, texts)
    results["models"]["tfidf_logreg"] = score(y_aspect, a, y_sent, s)

    print("3/3 IndoBERT fine-tuned ...")
    out = predict_indobert(texts)
    if out is None:
        print("   checkpoint tidak ditemukan - dilewati")
    else:
        a, s = out
        results["models"]["indobert_finetuned"] = score(y_aspect, a, y_sent, s)

    EVAL_OUT.mkdir(parents=True, exist_ok=True)
    (EVAL_OUT / "gold_results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n{'pendekatan':26s} {'aspek macro':>12s} {'aspek micro':>12s} {'sentimen macro':>15s}")
    print("-" * 70)
    for name, m in results["models"].items():
        print(f"{name:26s} {m['aspect_macro_f1']:12.4f} {m['aspect_micro_f1']:12.4f} "
              f"{m['sentiment_macro_f1']:15.4f}")

    print(f"\ngold set  : {(ANNOT / 'gold_labels.csv').relative_to(REPO_ROOT)}")
    print(f"hasil     : {(EVAL_OUT / 'gold_results.json').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
