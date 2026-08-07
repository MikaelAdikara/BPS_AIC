"""EmbeddingAdapter — pembungkus model embedding untuk RET-01 (blueprint bagian 17.4, 21).

Model utama BGE-M3 (ADR-005), dipilih karena kuat pada bahasa low-resource. Fallback
Multilingual E5-base bila BGE-M3 terlalu berat untuk lingkungan yang menjalankan.

Lapisan terakhir fallback adalah TF-IDF: kualitas retrieval-nya lebih rendah, tetapi sistem
tetap dapat menampilkan kutipan bukti alih-alih gagal total. Bukti adalah fondasi kepercayaan
produk ini (bagian 8.1 RET-01) - kehilangan bukti jauh lebih merusak daripada bukti yang
peringkatnya kurang optimal.
"""

from __future__ import annotations

import numpy as np

PRIMARY_MODEL = "BAAI/bge-m3"
FALLBACK_MODEL = "intfloat/multilingual-e5-base"


class EmbeddingAdapter:
    """Menghasilkan vektor untuk teks. Turun tingkat secara otomatis bila model gagal dimuat."""

    def __init__(self, model_name: str | None = None, device: str | None = None):
        self.model = None
        self.model_name = "tfidf-fallback"
        self.mode = "fallback"
        self._tfidf = None
        self._load(model_name, device)

    def _load(self, model_name: str | None, device: str | None) -> None:
        candidates = [model_name] if model_name else [PRIMARY_MODEL, FALLBACK_MODEL]
        for candidate in candidates:
            try:
                import torch  # noqa: PLC0415
                from transformers import AutoModel, AutoTokenizer  # noqa: PLC0415

                self._torch = torch
                self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
                self.tokenizer = AutoTokenizer.from_pretrained(candidate)
                self.model = AutoModel.from_pretrained(candidate).to(self._device).eval()
                self.model_name = candidate
                self.mode = "full"
                return
            except Exception as exc:  # pragma: no cover - jalur degradasi
                print(f"[EmbeddingAdapter] {candidate} gagal dimuat: {exc}")
        print("[EmbeddingAdapter] memakai fallback TF-IDF - kualitas retrieval lebih rendah")

    def _fit_tfidf(self, corpus: list[str]) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: PLC0415

        self._tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
        self._tfidf.fit(corpus)

    def encode(self, texts: list[str], corpus: list[str] | None = None) -> np.ndarray:
        """Ubah teks menjadi vektor ternormalisasi (cocok untuk cosine similarity)."""
        if self.model is None:
            if self._tfidf is None:
                self._fit_tfidf(corpus or texts)
            matrix = self._tfidf.transform(texts).toarray().astype("float32")
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            return matrix / np.clip(norms, 1e-9, None)

        torch = self._torch
        vectors = []
        with torch.no_grad():
            for start in range(0, len(texts), 32):
                batch = texts[start : start + 32]
                enc = self.tokenizer(
                    batch, truncation=True, max_length=256, padding=True, return_tensors="pt"
                ).to(self._device)
                out = self.model(**enc)
                # Mean pooling atas token non-padding, lalu normalisasi L2.
                mask = enc["attention_mask"].unsqueeze(-1).float()
                pooled = (out.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
                pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
                vectors.append(pooled.cpu().numpy())
        return np.vstack(vectors).astype("float32")
