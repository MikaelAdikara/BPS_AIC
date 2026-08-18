"""Evaluasi sentimen pada dataset berlabel MANUSIA yang sudah ada - tanpa anotasi tambahan.

Menjawab pertanyaan "apakah kita bisa memakai data berlabel yang sudah ada saja?".

Untuk SENTIMEN: bisa, dan dipakai di sini. Dua sumber, keduanya berlabel manusia dan sepenuhnya
independen dari labeling function kita:

  1. NusaX-senti (indonlp) - anotasi expert-generated, CC-BY-SA-4.0. Mencakup Bahasa Indonesia,
     Inggris, dan bahasa daerah (Jawa, Sunda, Minang). Inilah satu-satunya cara menguji dua klaim
     yang selama ini tidak pernah bisa kita uji: ketahanan terhadap campuran bahasa daerah
     (blueprint bagian 42.1) dan terhadap bahasa Inggris.
  2. PRDECT-ID - kolom `Sentiment` berlabel manusia (biner), dari makalah Data in Brief.
     Dievaluasi HANYA pada split test agar produknya terpisah dari data latih.

Untuk ASPEK: tidak bisa. Penelusuran delapan variasi kueri di HuggingFace tidak menemukan dataset
ABSA Bahasa Indonesia domain e-commerce yang berlisensi jelas. CASA (ulasan mobil) dan HoASA
(hotel) memakai skema aspek yang tidak sepadan. Validasi aspek tetap bergantung gold set kita.

CATATAN DOMAIN: NusaX berasal dari teks media sosial, bukan ulasan e-commerce. Hasil di sini
mengukur GENERALISASI lintas domain, bukan performa in-domain. Keduanya berguna, tetapi tidak
boleh ditukar penyebutannya.

Pemakaian:
    python ml/text/evaluate_external.py
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.pipeline import Pipeline

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lexicon import ALL_ASPECTS  # noqa: E402  (dipakai untuk kolom dummy adapter)
from preprocess import normalize, polarity_score, split_clauses  # noqa: E402

RAW = REPO_ROOT / "data" / "raw"
PROCESSED = REPO_ROOT / "data" / "processed"
EVAL_OUT = REPO_ROOT / "ml" / "evaluation"
CHECKPOINT = REPO_ROOT / "models" / "indobert-nlp01" / "model.pt"

SEED = 42
SENTIMENTS = ["negatif", "netral", "positif"]
NUSAX_BASE = (
    "https://huggingface.co/datasets/indonlp/NusaX-senti/resolve/"
    "refs%2Fconvert%2Fparquet/{lang}/test/0000.parquet"
)
LANGS = {"ind": "Indonesia", "eng": "Inggris", "jav": "Jawa", "sun": "Sunda", "min": "Minang"}


def load_nusax(lang: str) -> pd.DataFrame:
    cache = RAW / "nusax_senti" / f"{lang}_test.parquet"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if not cache.exists():
        with urlopen(NUSAX_BASE.format(lang=lang), timeout=120) as resp:
            cache.write_bytes(resp.read())
    df = pd.read_parquet(io.BytesIO(cache.read_bytes()))
    df = df.rename(columns={"text": "clause_text"})
    df["gold"] = df["label"].map({0: "negatif", 1: "netral", 2: "positif"})
    return df[["clause_text", "gold"]].dropna()


def load_prdect_test() -> pd.DataFrame:
    """Ulasan PRDECT-ID pada split test, dengan label sentimen manusia aslinya."""
    src = pd.read_csv(RAW / "prdect_id" / "PRDECT-ID Dataset.csv")
    src["clause_text"] = src["Customer Review"].astype(str)
    src["gold"] = src["Sentiment"].str.lower().map({"positive": "positif", "negative": "negatif"})
    src["product_key"] = "prdect::" + src["Product Name"].astype(str)

    test_products = set(pd.read_csv(PROCESSED / "clauses_test_silver.csv")["product_key"])
    held_out = src[src["product_key"].isin(test_products)]
    return held_out[["clause_text", "gold"]].dropna()


def predict_lexicon(texts: list[str]) -> list[str]:
    out = []
    for text in texts:
        pos, neg = polarity_score(normalize(text))
        out.append("positif" if pos > neg else "negatif" if neg > pos else "netral")
    return out


def predict_tfidf(train: pd.DataFrame, texts: list[str]) -> list[str]:
    pipe = Pipeline([
        ("t", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3,
                              max_features=200_000, sublinear_tf=True)),
        ("c", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED)),
    ])
    pipe.fit(train["clause_text"], train["sentiment"])
    return list(pipe.predict([normalize(t) for t in texts]))


def predict_indobert(texts: list[str]) -> list[str] | None:
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

    # Model dilatih pada KLAUSA, sementara dataset eksternal berisi kalimat/dokumen penuh.
    # Setiap teks disegmentasi dengan cara yang sama seperti saat latih, lalu sentimen dokumen
    # diambil dari mayoritas klausanya - menyamakan unit analisis, bukan memaksa model membaca
    # input yang bentuknya tidak pernah ia lihat.
    out = []
    with torch.no_grad():
        for text in texts:
            clauses = split_clauses(normalize(text)) or [normalize(text)]
            enc = tokenizer(clauses, truncation=True, max_length=32, padding=True,
                            return_tensors="pt").to(device)
            _, sent_logits = model(enc["input_ids"], enc["attention_mask"])
            votes = [SENTIMENTS[i] for i in sent_logits.argmax(-1).cpu().numpy()]
            non_neutral = [v for v in votes if v != "netral"]
            out.append(max(set(non_neutral or votes), key=(non_neutral or votes).count))
    return out


def score(gold: list[str], pred: list[str]) -> dict:
    rep = classification_report(gold, pred, output_dict=True, zero_division=0)
    return {
        "macro_f1": round(float(f1_score(gold, pred, average="macro", zero_division=0)), 4),
        "per_class": {s: round(float(rep[s]["f1-score"]), 4) for s in SENTIMENTS if s in rep},
        "n": len(gold),
    }


def main() -> int:
    train = pd.read_csv(PROCESSED / "clauses_train.csv")
    train["clause_text"] = train["clause_text"].fillna("").astype(str)

    datasets: dict[str, pd.DataFrame] = {}
    for lang, label in LANGS.items():
        try:
            datasets[f"nusax_{lang} ({label})"] = load_nusax(lang)
        except Exception as exc:  # pragma: no cover
            print(f"  lewati nusax {lang}: {exc}", file=sys.stderr)
    datasets["prdect_test (label manusia)"] = load_prdect_test()

    results: dict = {
        "catatan": (
            "Seluruh label di sini dibuat MANUSIA dan independen dari labeling function kita. "
            "NusaX berdomain media sosial sehingga mengukur generalisasi lintas domain, bukan "
            "performa in-domain. PRDECT-ID berlabel biner (tanpa kelas netral)."
        ),
        "sumber": {
            "nusax": "indonlp/NusaX-senti, expert-generated, CC-BY-SA-4.0",
            "prdect": "ZakyF/PRDECT-ID kolom Sentiment, CC-BY-4.0, hanya split test",
        },
        "hasil": {},
    }

    for name, df in datasets.items():
        texts = df["clause_text"].astype(str).tolist()
        gold = df["gold"].tolist()
        entry = {
            "lexicon_rule_based": score(gold, predict_lexicon(texts)),
            "tfidf_logreg": score(gold, predict_tfidf(train, texts)),
        }
        ib = predict_indobert(texts)
        if ib is not None:
            entry["indobert_finetuned"] = score(gold, ib)
        results["hasil"][name] = entry
        print(f"selesai: {name}  (n={len(gold)})")

    EVAL_OUT.mkdir(parents=True, exist_ok=True)
    (EVAL_OUT / "external_results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n{'dataset':30s} {'leksikon':>10s} {'TF-IDF':>10s} {'IndoBERT':>10s}")
    print("-" * 64)
    for name, entry in results["hasil"].items():
        row = [entry[k]["macro_f1"] if k in entry else float("nan")
               for k in ("lexicon_rule_based", "tfidf_logreg", "indobert_finetuned")]
        print(f"{name:30s} {row[0]:10.4f} {row[1]:10.4f} {row[2]:10.4f}")
    print(f"\nhasil: {(EVAL_OUT / 'external_results.json').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
