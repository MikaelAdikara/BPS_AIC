"""Fine-tuning IndoBERT untuk NLP-01 (blueprint bagian 18, 26.1 langkah 13).

Arsitektur: SATU encoder IndoBERT dengan DUA HEAD TERPISAH - head aspek (multi-label, 11 kelas)
dan head sentimen (3 kelas). Ini pembacaan langsung bagian 18.1 yang memilih "dua head terpisah
(aspect classifier + sentiment classifier)" dan menolak "multi-task dalam satu head". Encoder
dibagi karena bagian 17.1 menargetkan Text Intelligence ~500MB RAM - dua model IndoBERT terpisah
akan menghabiskan hampir dua kali lipat anggaran itu di laptop juri.

Training memakai GPU bila tersedia; TARGET DEPLOYMENT TETAP CPU-ONLY (bagian 30.3). Training
bersifat offline dan tidak menjadi bagian runtime.

CARA MEMBACA ANGKANYA: label aspek dan sebagian label sentimen berasal dari labeling function
(ADR-015), sehingga metrik pada split silver mengukur kecocokan terhadap LF, bukan akurasi
sebenarnya. Angka untuk proposal menunggu gold test set.

Pemakaian:
    python ml/text/finetune.py                 # latih + evaluasi
    python ml/text/finetune.py --epochs 2 --batch-size 16
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import classification_report, f1_score
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lexicon import ALL_ASPECTS  # noqa: E402
from model import MODEL_NAME, SENTIMENTS, DualHeadClassifier  # noqa: E402
from preprocess import normalize  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = REPO_ROOT / "data" / "processed"
RAW = REPO_ROOT / "data" / "raw"
EVAL_OUT = REPO_ROOT / "ml" / "evaluation"
MODEL_OUT = REPO_ROOT / "models" / "indobert-nlp01"

SEED = 42
ASPECT_COLS = [f"asp_{a}" for a in ALL_ASPECTS]


def set_seed(seed: int = SEED) -> None:
    """Bagian 26.1 langkah 18: seed di-fix dan dicatat agar hasil dapat direproduksi."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


class ClauseDataset(Dataset):
    """Menyimpan teks mentah; tokenisasi dilakukan per batch oleh `Collator`.

    Klausa ulasan sangat pendek - median 5 token, p99 18 token. Mem-padding setiap
    contoh ke panjang tetap membuat sebagian besar komputasi attention terbuang pada
    token padding. Karena itu padding dilakukan DINAMIS per batch (sepanjang contoh
    terpanjang di batch itu saja), bukan ke `max_len`.
    """

    def __init__(self, df: pd.DataFrame):
        self.texts = df["clause_text"].fillna("").astype(str).tolist()
        self.aspects = df[ASPECT_COLS].values.astype("float32")
        self.sentiments = df["sentiment"].map({s: i for i, s in enumerate(SENTIMENTS)}).values

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> tuple[str, np.ndarray, int]:
        return self.texts[idx], self.aspects[idx], int(self.sentiments[idx])


class Collator:
    """Tokenisasi + padding dinamis per batch."""

    def __init__(self, tokenizer, max_len: int = 32):
        self.tokenizer = tokenizer
        self.max_len = max_len  # batas atas pengaman; 32 sudah menampung 99,9% klausa

    def __call__(self, batch: list[tuple[str, np.ndarray, int]]) -> dict:
        texts, aspects, sentiments = zip(*batch)
        enc = self.tokenizer(
            list(texts),
            truncation=True,
            max_length=self.max_len,
            padding=True,  # pad ke contoh terpanjang di batch ini saja
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "aspect_labels": torch.tensor(np.array(aspects), dtype=torch.float32),
            "sentiment_label": torch.tensor(sentiments, dtype=torch.long),
        }


def _pos_weight(train: pd.DataFrame) -> torch.Tensor:
    """Bobot kelas positif per aspek - aspek minoritas (rasa, kelengkapan) sangat jarang."""
    counts = train[ASPECT_COLS].sum().values.astype("float32")
    n = len(train)
    weights = (n - counts) / np.clip(counts, 1, None)
    return torch.tensor(np.clip(weights, 1.0, 50.0), dtype=torch.float32)


def _sentiment_weight(train: pd.DataFrame) -> torch.Tensor:
    """Class weighting untuk sentimen (bagian 26.1 langkah 8: bukan oversampling naif)."""
    counts = train["sentiment"].value_counts()
    total = len(train)
    weights = [total / (len(SENTIMENTS) * max(int(counts.get(s, 1)), 1)) for s in SENTIMENTS]
    return torch.tensor(weights, dtype=torch.float32)


@torch.no_grad()
def predict(model, loader, device) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    aspect_probs, sentiment_preds = [], []
    for batch in loader:
        ids = batch["input_ids"].to(device)
        mask = batch["attention_mask"].to(device)
        asp_logits, sent_logits = model(ids, mask)
        aspect_probs.append(torch.sigmoid(asp_logits).cpu().numpy())
        sentiment_preds.append(sent_logits.argmax(-1).cpu().numpy())
    return np.vstack(aspect_probs), np.concatenate(sentiment_preds)


def tune_threshold(probs: np.ndarray, y_true: np.ndarray) -> float:
    """Pilih satu ambang global dari validation set, bukan 0,5 asal pakai.

    Ambang per-kelas sengaja dihindari: dengan aspek yang support-nya hanya puluhan baris,
    ambang per-kelas mudah overfit ke validation.
    """
    best_t, best_f1 = 0.5, -1.0
    for t in np.arange(0.10, 0.71, 0.05):
        f1 = f1_score(y_true, (probs >= t).astype(int), average="macro", zero_division=0)
        if f1 > best_f1:
            best_t, best_f1 = float(t), float(f1)
    return round(best_t, 2)


def eval_aspects(probs: np.ndarray, y_true: np.ndarray, threshold: float) -> dict:
    pred = (probs >= threshold).astype(int)
    return {
        "threshold": threshold,
        "macro_f1": round(float(f1_score(y_true, pred, average="macro", zero_division=0)), 4),
        "micro_f1": round(float(f1_score(y_true, pred, average="micro", zero_division=0)), 4),
        "per_class": {
            a: {
                "f1": round(float(f1_score(y_true[:, i], pred[:, i], zero_division=0)), 4),
                "support": int(y_true[:, i].sum()),
            }
            for i, a in enumerate(ALL_ASPECTS)
        },
    }


def eval_sentiment(pred_idx: np.ndarray, y_true_idx: np.ndarray) -> dict:
    y_true = [SENTIMENTS[i] for i in y_true_idx]
    y_pred = [SENTIMENTS[i] for i in pred_idx]
    rep = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    return {
        "macro_f1": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "per_class_f1": {
            s: round(float(rep[s]["f1-score"]), 4) for s in SENTIMENTS if s in rep
        },
        "support": {s: int(rep[s]["support"]) for s in SENTIMENTS if s in rep},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--max-len", type=int, default=32)
    parser.add_argument("--limit-train", type=int, default=0, help="0 = pakai semua")
    args = parser.parse_args()

    if not (PROCESSED / "clauses_train.csv").exists():
        print("Jalankan ml/text/build_dataset.py lebih dulu.", file=sys.stderr)
        return 1

    set_seed()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device: {device}")

    train = pd.read_csv(PROCESSED / "clauses_train.csv")
    val = pd.read_csv(PROCESSED / "clauses_val.csv")
    test = pd.read_csv(PROCESSED / "clauses_test_silver.csv")
    for frame in (train, val, test):
        frame["clause_text"] = frame["clause_text"].fillna("").astype(str)
    if args.limit_train:
        train = train.sample(args.limit_train, random_state=SEED).reset_index(drop=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = DualHeadClassifier().to(device)

    collate = Collator(tokenizer, args.max_len)
    train_loader = DataLoader(
        ClauseDataset(train), batch_size=args.batch_size, shuffle=True, collate_fn=collate
    )
    val_loader = DataLoader(ClauseDataset(val), batch_size=128, collate_fn=collate)
    test_loader = DataLoader(ClauseDataset(test), batch_size=128, collate_fn=collate)

    aspect_loss_fn = nn.BCEWithLogitsLoss(pos_weight=_pos_weight(train).to(device))
    sentiment_loss_fn = nn.CrossEntropyLoss(weight=_sentiment_weight(train).to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    total_steps = len(train_loader) * args.epochs
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=args.lr, total_steps=total_steps, pct_start=0.1
    )
    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    y_val_aspect = val[ASPECT_COLS].values.astype(int)
    y_val_sent = val["sentiment"].map({s: i for i, s in enumerate(SENTIMENTS)}).values

    # Model selection berdasar validation F1 terbaik, BUKAN training loss terendah
    # (bagian 26.1 langkah 16 - menghindari overfitting).
    best = {"score": -1.0, "epoch": -1, "state": None, "threshold": 0.5}
    history = []
    t_start = time.time()

    for epoch in range(1, args.epochs + 1):
        model.train()
        running = 0.0
        for step, batch in enumerate(train_loader, 1):
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            y_asp = batch["aspect_labels"].to(device)
            y_sent = batch["sentiment_label"].to(device)

            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=use_amp):
                asp_logits, sent_logits = model(ids, mask)
                loss = aspect_loss_fn(asp_logits, y_asp) + sentiment_loss_fn(sent_logits, y_sent)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            running += loss.item()
            if step % 200 == 0:
                # flush=True wajib: saat stdout diarahkan ke file, Python memakai block
                # buffering sehingga progres training tidak terlihat sampai proses berakhir.
                print(
                    f"  epoch {epoch} step {step}/{len(train_loader)} loss {running/step:.4f}",
                    flush=True,
                )

        probs, sent_pred = predict(model, val_loader, device)
        threshold = tune_threshold(probs, y_val_aspect)
        asp_metrics = eval_aspects(probs, y_val_aspect, threshold)
        sent_metrics = eval_sentiment(sent_pred, y_val_sent)
        score = (asp_metrics["macro_f1"] + sent_metrics["macro_f1"]) / 2
        history.append({
            "epoch": epoch,
            "train_loss": round(running / len(train_loader), 4),
            "val_aspect_macro_f1": asp_metrics["macro_f1"],
            "val_sentiment_macro_f1": sent_metrics["macro_f1"],
            "val_combined": round(score, 4),
            "aspect_threshold": threshold,
        })
        print(
            f"epoch {epoch}: val aspek {asp_metrics['macro_f1']} | "
            f"val sentimen {sent_metrics['macro_f1']} | gabungan {score:.4f}",
            flush=True,
        )

        if score > best["score"]:
            best = {
                "score": score,
                "epoch": epoch,
                "state": {k: v.detach().cpu().clone() for k, v in model.state_dict().items()},
                "threshold": threshold,
            }
            # Checkpoint ditulis ke disk SETIAP kali membaik, bukan hanya di akhir.
            # Dua run sebelumnya mati di tengah jalan tanpa traceback dan seluruh hasil
            # training hilang - menyimpan per epoch membuat kegagalan itu hanya memakan
            # satu epoch, bukan semuanya.
            MODEL_OUT.mkdir(parents=True, exist_ok=True)
            torch.save(
                {"state_dict": best["state"], "aspect_threshold": threshold,
                 "aspects": list(ALL_ASPECTS), "sentiments": SENTIMENTS,
                 "base_model": MODEL_NAME, "epoch": epoch, "val_combined": score},
                MODEL_OUT / "model.pt",
            )
            tokenizer.save_pretrained(MODEL_OUT)
            print(f"  checkpoint disimpan (epoch {epoch})", flush=True)

    train_seconds = round(time.time() - t_start, 1)
    print(f"\nmemuat checkpoint terbaik: epoch {best['epoch']} (val gabungan {best['score']:.4f})")
    model.load_state_dict(best["state"])

    # ---------------- Evaluasi ----------------
    probs, sent_pred = predict(model, test_loader, device)
    y_test_aspect = test[ASPECT_COLS].values.astype(int)
    y_test_sent = test["sentiment"].map({s: i for i, s in enumerate(SENTIMENTS)}).values
    threshold = best["threshold"]

    results: dict = {
        "seed": SEED,
        "model": MODEL_NAME,
        "architecture": "encoder bersama + dua head terpisah (aspek multi-label, sentimen 3 kelas)",
        "hyperparameters": {
            "epochs": args.epochs, "batch_size": args.batch_size, "lr": args.lr,
            "max_len": args.max_len, "optimizer": "AdamW", "scheduler": "OneCycleLR",
            "train_clauses": int(len(train)),
        },
        "device": str(device),
        "train_seconds": train_seconds,
        "best_epoch": best["epoch"],
        "history": history,
        "label_warning": (
            "Metrik silver_* mengukur kecocokan terhadap labeling function (ADR-015), BUKAN "
            "akurasi sebenarnya. Angka proposal menunggu gold test set berlabel manusia."
        ),
        "aspect": {"silver_test": eval_aspects(probs, y_test_aspect, threshold)},
        "sentiment": {"silver_test": eval_sentiment(sent_pred, y_test_sent)},
    }

    # Subset klausa yang teksnya tak pernah muncul di train - bebas efek hafalan frasa.
    seen = set(train["clause_text"])
    unseen_mask = (~test["clause_text"].isin(seen)).values
    results["aspect"]["silver_test_unseen"] = eval_aspects(
        probs[unseen_mask], y_test_aspect[unseen_mask], threshold
    )
    results["sentiment"]["silver_test_unseen"] = eval_sentiment(
        sent_pred[unseen_mask], y_test_sent[unseen_mask]
    )

    # Stratifikasi menurut ASAL label sentimen. Klausa berlabel `review_prior` mewarisi sentimen
    # tingkat ulasan dan diduga lebih berderau - kalau performa di sana jauh lebih rendah,
    # itu bukti derau label, bukan kegagalan model.
    for origin in ("clause_polarity", "review_prior"):
        mask = (test["sentiment_origin"] == origin).values
        if mask.sum() > 50:
            results["sentiment"][f"silver_test_by_origin::{origin}"] = eval_sentiment(
                sent_pred[mask], y_test_sent[mask]
            )

    # Stress test sentimen (label diturunkan dari rating - lihat validate_lf.py).
    stress_path = RAW / "ecommerce_sentiment" / "challange.json"
    if stress_path.exists():
        stress = pd.DataFrame(json.loads(stress_path.read_text(encoding="utf-8")))
        stress["clause_text"] = stress["comment"].map(normalize)
        stress["sentiment"] = stress["sentiment"].map(
            {"positive": "positif", "negative": "negatif", "neutral": "netral"}
        )
        stress = stress[stress["clause_text"].str.len() >= 3].reset_index(drop=True)
        for col in ASPECT_COLS:
            stress[col] = 0
        stress_loader = DataLoader(ClauseDataset(stress), batch_size=128, collate_fn=collate)
        _, stress_pred = predict(model, stress_loader, device)
        y_stress = stress["sentiment"].map({s: i for i, s in enumerate(SENTIMENTS)}).values
        overall = eval_sentiment(stress_pred, y_stress)
        overall["note"] = (
            "Label diturunkan dari rating (98,3%), bukan penilaian independen atas teks. "
            "Dipakai sebagai diagnostik per fenomena, bukan ground truth."
        )
        by_phenomenon = {}
        for phenomenon, group in stress.groupby("category"):
            idx = group.index.values
            if len(idx) >= 25:
                by_phenomenon[phenomenon] = eval_sentiment(stress_pred[idx], y_stress[idx])["macro_f1"]
        overall["by_phenomenon_macro_f1"] = dict(sorted(by_phenomenon.items(), key=lambda x: x[1]))
        results["sentiment"]["stress_challange"] = overall

    EVAL_OUT.mkdir(parents=True, exist_ok=True)
    out = EVAL_OUT / "finetune_results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    MODEL_OUT.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"state_dict": model.state_dict(), "aspect_threshold": threshold,
         "aspects": list(ALL_ASPECTS), "sentiments": SENTIMENTS, "base_model": MODEL_NAME},
        MODEL_OUT / "model.pt",
    )
    tokenizer.save_pretrained(MODEL_OUT)

    a, s = results["aspect"], results["sentiment"]
    print("\n--- ASPEK (macro F1 multi-label)")
    print(f"  silver_test        : {a['silver_test']['macro_f1']}  (micro {a['silver_test']['micro_f1']}, thr {threshold})")
    print(f"  silver_test_unseen : {a['silver_test_unseen']['macro_f1']}")
    print("--- SENTIMEN (macro F1)")
    print(f"  silver_test        : {s['silver_test']['macro_f1']}   per-kelas {s['silver_test']['per_class_f1']}")
    print(f"  silver_test_unseen : {s['silver_test_unseen']['macro_f1']}")
    for origin in ("clause_polarity", "review_prior"):
        key = f"silver_test_by_origin::{origin}"
        if key in s:
            print(f"  by origin {origin:16s}: {s[key]['macro_f1']}")
    if "stress_challange" in s:
        print(f"  stress_challange   : {s['stress_challange']['macro_f1']}")
    print(f"\nhasil : {out.relative_to(REPO_ROOT)}")
    print(f"model : {MODEL_OUT.relative_to(REPO_ROOT)} (tidak di-commit)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
