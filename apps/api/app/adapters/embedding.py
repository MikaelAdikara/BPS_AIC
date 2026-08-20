"""EmbeddingAdapter - pembungkus model embedding untuk RET-01 (blueprint bagian 17.4, 21).

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


# Batch lebih kecil dari 32 justru menguntungkan begitu batch-nya disusun menurut panjang:
# batch pendek selesai nyaris seketika, dan batch panjang tidak lagi menyeret teks pendek.
BATCH_SIZE = 16

# Plafon pemotongan. Nilainya tidak berubah; ia dipindahkan ke sini bersama batch_size supaya
# keduanya dapat diturunkan pada mesin yang lebih kecil tanpa menyentuh badan `encode`.
# Terukur pada dataset demo, ulasan terpanjang hanya 104 token - plafon ini praktis tidak
# pernah terpakai, dan setelah pengurutan menurut panjang ia juga tidak lagi menentukan biaya.
MAX_LENGTH = 256


class EmbeddingAdapter:
    """Menghasilkan vektor untuk teks. Turun tingkat secara otomatis bila model gagal dimuat."""

    def __init__(self, model_name: str | None = None, device: str | None = None):
        self.model = None
        self.model_name = "tfidf-fallback"
        self.mode = "fallback"
        self._tfidf = None
        self.batch_size = BATCH_SIZE
        self.max_length = MAX_LENGTH
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

        # Batch disusun menurut PANJANG teks, bukan menurut urutan datangnya.
        #
        # Biaya satu batch ditentukan teks TERPANJANG di dalamnya: seluruh isi batch di-padding
        # sampai sepanjang itu, dan padding tetap ikut dihitung penuh oleh attention. Pada 66
        # ulasan Shopee asli panjangnya 7-104 token dengan median 33 - artinya batch acak
        # berisi mayoritas token kosong. Terukur pada mesin pengembang: 22,0 detik menjadi
        # 12,2 detik, tanpa satu pun angka hasil yang berubah.
        #
        # Hasilnya identik karena padding sudah ditutup `attention_mask` dan mean pooling di
        # bawah hanya menjumlah token non-padding. Urutan keluaran dikembalikan ke urutan
        # masukan sebelum fungsi ini selesai - pemanggilnya memasangkan vektor dengan ulasan
        # berdasarkan posisi, jadi tertukarnya urutan berarti bukti yang salah tempel.
        order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
        vectors: list[np.ndarray] = [None] * len(texts)  # type: ignore[list-item]

        with torch.no_grad():
            for start in range(0, len(order), self.batch_size):
                idx = order[start : start + self.batch_size]
                enc = self.tokenizer(
                    [texts[i] for i in idx],
                    truncation=True,
                    max_length=self.max_length,
                    padding=True,
                    return_tensors="pt",
                ).to(self._device)
                out = self.model(**enc)
                # Mean pooling atas token non-padding, lalu normalisasi L2.
                mask = enc["attention_mask"].unsqueeze(-1).float()
                pooled = (out.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
                pooled = torch.nn.functional.normalize(pooled, p=2, dim=1).cpu().numpy()
                for slot, vector in zip(idx, pooled):
                    vectors[slot] = vector
        return np.vstack(vectors).astype("float32")
