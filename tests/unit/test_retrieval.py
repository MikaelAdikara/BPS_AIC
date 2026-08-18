"""Unit test RET-01 (blueprint bagian 21, 27.3).

Memakai EmbeddingAdapter jalur fallback TF-IDF supaya test berjalan cepat dan tanpa mengunduh
model - yang diuji di sini adalah LOGIKA retrieval, bukan kualitas model embedding.
"""

import numpy as np
import pytest

from app.schemas import Aspect
from app.tools import EvidenceIndex


class _StubAdapter:
    """Embedding TF-IDF sederhana; deterministic dan tidak butuh unduhan."""

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 4), min_df=1)
        self._fitted = False

    def encode(self, texts, corpus=None):
        if not self._fitted:
            self._vec.fit(corpus or texts)
            self._fitted = True
        m = self._vec.transform(texts).toarray().astype("float32")
        return m / np.clip(np.linalg.norm(m, axis=1, keepdims=True), 1e-9, None)


REVIEWS = [
    {"review_id": "r1", "text": "ukurannya kekecilan padahal sudah pesan size L",
     "aspects": ["ukuran_varian"], "product_id": "p1"},
    {"review_id": "r2", "text": "ukuran terlalu kecil tidak sesuai panduan ukuran",
     "aspects": ["ukuran_varian"], "product_id": "p2"},
    {"review_id": "r3", "text": "pengiriman sangat cepat sampai besoknya",
     "aspects": ["pengiriman"], "product_id": "p3"},
    {"review_id": "r4", "text": "kemasan rusak saat diterima kardusnya penyok",
     "aspects": ["kemasan"], "product_id": "p4"},
    {"review_id": "r5", "text": "ukuran mengecewakan jauh lebih kecil dari perkiraan",
     "aspects": ["ukuran_varian"], "product_id": "p5"},
]


@pytest.fixture
def index():
    idx = EvidenceIndex(_StubAdapter(), min_similarity=0.05)
    idx.build(REVIEWS)
    return idx


def test_mengembalikan_kutipan_asli_tanpa_parafrase(index):
    """Bagian 25.10: quote adalah kutipan ASLI - memparafrase merusak fungsinya sebagai bukti."""
    hits = index.retrieve("keluhan ukuran", aspect=Aspect.UKURAN_VARIAN, top_k=3)
    assert hits
    texts = {r["text"] for r in REVIEWS}
    for h in hits:
        assert h.quote in texts


def test_hasil_terurut_menurut_relevansi(index):
    hits = index.retrieve("ukuran kekecilan", aspect=Aspect.UKURAN_VARIAN, top_k=3)
    scores = [h.relevance_score for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_filter_aspek_mempersempit_kandidat(index):
    hits = index.retrieve("masalah kemasan", aspect=Aspect.KEMASAN, top_k=5)
    assert any(h.review_id == "r4" for h in hits)


def test_ambang_tidak_terlampaui_mengembalikan_kosong():
    """Bagian 21.3: menolak menjawab lebih baik daripada mengarang bukti.

    Daftar kosong adalah sinyal bagi pemanggil untuk menampilkan "data belum cukup" dan
    TIDAK memanggil LLM sama sekali.
    """
    idx = EvidenceIndex(_StubAdapter(), min_similarity=0.99)
    idx.build(REVIEWS)
    assert idx.retrieve("pertanyaan yang tidak ada hubungannya", top_k=5) == []


def test_indeks_kosong_tidak_error():
    idx = EvidenceIndex(_StubAdapter())
    idx.build([])
    assert idx.retrieve("apa pun") == []


def test_near_duplicate_tidak_memenuhi_hasil():
    """Top-k tidak boleh didominasi ulasan yang isinya nyaris sama (bagian 21.1)."""
    duplicates = [
        {"review_id": f"d{i}", "text": "ukurannya kekecilan padahal sudah pesan size L",
         "aspects": ["ukuran_varian"], "product_id": f"p{i}"}
        for i in range(5)
    ] + [{"review_id": "beda", "text": "pengiriman cepat sekali",
          "aspects": ["pengiriman"], "product_id": "px"}]

    idx = EvidenceIndex(_StubAdapter(), min_similarity=0.01)
    idx.build(duplicates)
    hits = idx.retrieve("ukuran kekecilan", top_k=5)
    assert len(hits) < 5, "near-duplicate seharusnya disaring"


def test_top_k_dihormati(index):
    assert len(index.retrieve("ukuran", aspect=Aspect.UKURAN_VARIAN, top_k=2)) <= 2


def test_relevance_score_dalam_rentang_valid(index):
    for h in index.retrieve("ukuran kekecilan", top_k=5):
        assert 0.0 <= h.relevance_score <= 1.0


def test_citation_id_unik(index):
    hits = index.retrieve("ukuran", aspect=Aspect.UKURAN_VARIAN, top_k=3)
    assert len({h.citation_id for h in hits}) == len(hits)
