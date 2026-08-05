"""TextModelAdapter - pembungkus model teks NLP-01 (blueprint bagian 27.2).

Adapter memisahkan service layer dari model konkret, sehingga mengganti kandidat model
(bagian 17.2) tidak menyentuh logika bisnis. Ia juga tempat FALLBACK deterministic dipasang:
jika checkpoint neural gagal dimuat, sistem turun ke jalur leksikon, bukan gagal total.

Model dimuat SEKALI saat startup, bukan per-request (bagian 27.2 model warm-up).
Inferensi berjalan CPU-only secara default - GPU hanya dipakai bila kebetulan tersedia.
"""

from __future__ import annotations

import sys
from pathlib import Path

from ..schemas import (
    Aspect,
    AspectPrediction,
    ProcessedReview,
    Sentiment,
    Severity,
    TextPrediction,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CHECKPOINT = REPO_ROOT / "models" / "indobert-nlp01" / "model.pt"
ML_TEXT = REPO_ROOT / "ml" / "text"

SENTIMENTS = ["negatif", "netral", "positif"]


def _segment(text: str) -> list[str]:
    """Segmentasi klausa memakai modul yang sama dengan pipeline training.

    Memakai ulang kode training di sini disengaja: perbedaan sekecil apa pun antara cara teks
    dipecah saat latih dan saat inferensi akan menggeser distribusi input model.
    """
    if str(ML_TEXT) not in sys.path:
        sys.path.insert(0, str(ML_TEXT))
    from preprocess import normalize, split_clauses  # noqa: PLC0415

    return split_clauses(normalize(text))


def _severity_from(sentiment: Sentiment, rating: int | None) -> Severity:
    """Heuristik severity yang sama dengan pelabelan Fase 1 - konsisten latih vs inferensi."""
    if sentiment != Sentiment.NEGATIF:
        return Severity.RENDAH
    if rating is None:
        return Severity.SEDANG
    if rating <= 2:
        return Severity.TINGGI
    if rating == 3:
        return Severity.SEDANG
    return Severity.RENDAH


class TextModelAdapter:
    """Memuat checkpoint IndoBERT dua head; jatuh ke leksikon bila gagal."""

    def __init__(self, checkpoint: Path | None = None, device: str | None = None):
        self.checkpoint_path = checkpoint or DEFAULT_CHECKPOINT
        self.model = None
        self.tokenizer = None
        self.threshold = 0.5
        self.model_version = "lexicon-fallback"
        self.mode = "fallback"
        self._device = device
        self._load()

    def _load(self) -> None:
        if not self.checkpoint_path.exists():
            return
        try:
            import torch  # noqa: PLC0415
            from transformers import AutoTokenizer  # noqa: PLC0415

            if str(ML_TEXT) not in sys.path:
                sys.path.insert(0, str(ML_TEXT))
            from finetune import DualHeadClassifier  # noqa: PLC0415

            bundle = torch.load(self.checkpoint_path, map_location="cpu", weights_only=False)
            model = DualHeadClassifier(bundle["base_model"])
            model.load_state_dict(bundle["state_dict"])
            model.eval()

            device = self._device or ("cuda" if torch.cuda.is_available() else "cpu")
            self.model = model.to(device)
            self._torch = torch
            self._device = device
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.checkpoint_path.parent))
            self.threshold = float(bundle.get("aspect_threshold", 0.5))
            self.aspects = [Aspect(a) for a in bundle["aspects"]]
            self.model_version = f"indobert-nlp01@thr{self.threshold}"
            self.mode = "full"
        except Exception as exc:  # pragma: no cover - jalur degradasi
            # Kegagalan memuat model TIDAK boleh menjatuhkan sistem (prinsip failure-tolerant).
            print(f"[TextModelAdapter] checkpoint gagal dimuat, memakai leksikon: {exc}")
            self.model = None
            self.mode = "fallback"

    def _predict_neural(self, clauses: list[str]) -> list[tuple[list[Aspect], Sentiment]]:
        torch = self._torch
        enc = self.tokenizer(
            clauses, truncation=True, max_length=32, padding=True, return_tensors="pt"
        ).to(self._device)
        with torch.no_grad():
            aspect_logits, sentiment_logits = self.model(enc["input_ids"], enc["attention_mask"])
            aspect_probs = torch.sigmoid(aspect_logits).cpu().numpy()
            sentiment_idx = sentiment_logits.argmax(-1).cpu().numpy()

        results = []
        for probs, sent_i in zip(aspect_probs, sentiment_idx):
            aspects = [a for a, p in zip(self.aspects, probs) if p >= self.threshold]
            results.append((aspects, Sentiment(SENTIMENTS[int(sent_i)])))
        return results

    def _predict_lexicon(self, clauses: list[str]) -> list[tuple[list[Aspect], Sentiment]]:
        """Jalur fallback deterministic (bagian 17.1) - akurasi lebih rendah, tetap berjalan."""
        if str(ML_TEXT) not in sys.path:
            sys.path.insert(0, str(ML_TEXT))
        from lexicon import ASPECT_PATTERNS, FALLBACK_ASPECT, FALLBACK_PATTERN  # noqa: PLC0415
        from preprocess import polarity_score  # noqa: PLC0415

        results = []
        for clause in clauses:
            aspects = [Aspect(a) for a, pat in ASPECT_PATTERNS.items() if pat.search(clause)]
            if not aspects and FALLBACK_PATTERN.search(clause):
                aspects = [Aspect(FALLBACK_ASPECT)]
            pos, neg = polarity_score(clause)
            sentiment = (
                Sentiment.POSITIF if pos > neg else Sentiment.NEGATIF if neg > pos else Sentiment.NETRAL
            )
            results.append((aspects, sentiment))
        return results

    def classify(self, reviews: list[ProcessedReview]) -> list[TextPrediction]:
        """classify_text_aspects() - tool contract bagian 27.3."""
        predictions: list[TextPrediction] = []

        for review in reviews:
            clauses = _segment(review.clean_text)
            if not clauses:
                predictions.append(
                    TextPrediction(review_id=review.review_id, predictions=[],
                                   model_version=self.model_version)
                )
                continue

            per_clause = (
                self._predict_neural(clauses) if self.model is not None
                else self._predict_lexicon(clauses)
            )

            items: list[AspectPrediction] = []
            for clause, (aspects, sentiment) in zip(clauses, per_clause):
                for aspect in aspects:
                    items.append(
                        AspectPrediction(
                            aspect=aspect,
                            sentiment=sentiment,
                            severity=_severity_from(sentiment, review.rating),
                            # Confidence tetap perlu dikalibrasi (Fase 8); nilai ini adalah
                            # placeholder yang jujur, bukan probabilitas terkalibrasi.
                            confidence=0.80 if self.model is not None else 0.60,
                            source_sentence=clause,
                        )
                    )
            predictions.append(
                TextPrediction(review_id=review.review_id, predictions=items,
                               model_version=self.model_version)
            )

        return predictions
