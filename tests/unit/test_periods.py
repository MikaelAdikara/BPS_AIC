"""Unit test build_period_history() (apps/api/app/tools/periods.py).

Fokusnya pada keputusan yang mudah salah tanpa terlihat salah: bulan berlubang yang diam-diam
dirapatkan, periode satu ulasan yang dilaporkan "100% negatif", dan granularitas yang tidak
menyesuaikan rentang data.
"""

from datetime import datetime

import pytest

from app.schemas import (
    Aspect,
    AspectPrediction,
    Category,
    Granularity,
    ProcessedReview,
    Sentiment,
    Severity,
    TextPrediction,
)
from app.tools import build_period_history


def _review(review_id: str, stamp: datetime | None, rating: int = 5) -> ProcessedReview:
    return ProcessedReview(
        review_id=review_id,
        clean_text="teks uji",
        pii_redacted=False,
        rating=rating,
        category=Category.FASHION,
        has_image=False,
        timestamp=stamp,
    )


def _prediction(review_id: str, *aspects: Aspect) -> TextPrediction:
    return TextPrediction(
        review_id=review_id,
        predictions=[
            AspectPrediction(
                aspect=a,
                sentiment=Sentiment.NEGATIF,
                severity=Severity.SEDANG,
                confidence=0.8,
                source_sentence="klausa uji",
            )
            for a in aspects
        ],
        model_version="test-v1",
    )


def _spread(months: dict[int, int], year: int = 2026) -> tuple[list, list]:
    """Bangun ulasan sebanyak `jumlah` pada tiap `bulan` yang disebutkan."""
    reviews, predictions = [], []
    for month, count in months.items():
        for i in range(count):
            rid = f"r{month}_{i}"
            reviews.append(_review(rid, datetime(year, month, 5)))
            predictions.append(_prediction(rid))
    return reviews, predictions


def test_tanpa_tanggal_melaporkan_sebabnya_bukan_larik_kosong():
    """Bagian yang hilang tanpa alasan terbaca sebagai kerusakan, bukan sebagai keterbatasan."""
    reviews = [_review("r1", None), _review("r2", None)]
    predictions = [_prediction("r1"), _prediction("r2")]

    hasil = build_period_history(reviews, predictions)

    assert hasil.granularity is Granularity.TIDAK_CUKUP
    assert hasil.buckets == []
    assert hasil.reviews_undated == 2
    assert "tidak memuat kolom tanggal" in hasil.note


def test_rentang_terlalu_pendek_menolak_membelah():
    """Dua batang bukan riwayat - dan riwayat palsu lebih buruk daripada tidak ada riwayat."""
    reviews = [
        _review("r1", datetime(2026, 7, 1)),
        _review("r2", datetime(2026, 7, 8)),
    ]
    predictions = [_prediction("r1"), _prediction("r2")]

    hasil = build_period_history(reviews, predictions)

    assert hasil.granularity is Granularity.TIDAK_CUKUP
    assert "7 hari" in hasil.note


def test_rentang_menengah_dibelah_per_minggu():
    reviews = [
        _review("r1", datetime(2026, 6, 1)),
        _review("r2", datetime(2026, 7, 1)),
    ]
    predictions = [_prediction("r1"), _prediction("r2")]

    assert build_period_history(reviews, predictions).granularity is Granularity.MINGGUAN


def test_rentang_panjang_dibelah_per_bulan():
    reviews, predictions = _spread({1: 3, 6: 3})

    assert build_period_history(reviews, predictions).granularity is Granularity.BULANAN


def test_bulan_kosong_tetap_digambar():
    """Lubang di garis waktu wajib terlihat sebagai lubang.

    Data contoh Shopee tidak punya satu pun ulasan di Februari 2026. Merapatkannya membuat
    kenaikan antara Januari dan Maret tampak seperti kenaikan bulan-ke-bulan, padahal ada satu
    bulan penuh di antaranya.
    """
    reviews, predictions = _spread({1: 3, 2: 0, 3: 3, 4: 3, 5: 3})

    hasil = build_period_history(reviews, predictions)
    labels = [b.label for b in hasil.buckets]
    kosong = [b for b in hasil.buckets if b.empty]

    assert labels == ["Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "Mei 2026"]
    assert [b.label for b in kosong] == ["Feb 2026"]
    assert kosong[0].total_reviews == 0


def test_periode_tipis_ditandai_bukan_dipersentasekan_diam_diam():
    """Satu ulasan negatif adalah "100% negatif" secara aritmetika, dan itu menyesatkan."""
    reviews, predictions = _spread({1: 1, 5: 5})

    hasil = build_period_history(reviews, predictions)
    januari = next(b for b in hasil.buckets if b.label == "Jan 2026")
    mei = next(b for b in hasil.buckets if b.label == "Mei 2026")

    assert januari.sparse is True
    assert mei.sparse is False
    assert "belum bisa dipercaya" in hasil.note


def test_bulan_kosong_tidak_ikut_disebut_tipis():
    """`empty` dan `sparse` dua keadaan berbeda dan dibedakan di layar."""
    reviews, predictions = _spread({1: 3, 2: 0, 3: 3, 4: 3, 5: 3})

    februari = next(
        b for b in build_period_history(reviews, predictions).buckets if b.label == "Feb 2026"
    )

    assert februari.empty is True
    assert februari.sparse is False


def test_ulasan_tanpa_tanggal_dilaporkan_terpisah():
    reviews, predictions = _spread({1: 3, 5: 3})
    reviews.append(_review("tanpa", None))
    predictions.append(_prediction("tanpa"))

    hasil = build_period_history(reviews, predictions)

    assert hasil.reviews_dated == 6
    assert hasil.reviews_undated == 1
    assert "1 ulasan tidak punya tanggal" in hasil.note


def test_seri_aspek_sejajar_dengan_jumlah_ember():
    """Indeks seri dipakai frontend sebagai posisi pada sumbu yang sama dengan ember."""
    reviews, predictions = _spread({1: 3, 3: 3})
    predictions = [_prediction(p.review_id, Aspect.PENGIRIMAN) for p in predictions]

    hasil = build_period_history(reviews, predictions)

    assert hasil.series
    for seri in hasil.series:
        assert len(seri.counts) == len(hasil.buckets)
        assert seri.total == sum(seri.counts)


def test_satu_ulasan_dihitung_sekali_meski_mengeluhkan_banyak_aspek():
    reviews, predictions = _spread({1: 0, 5: 0})
    reviews = [
        _review("r1", datetime(2026, 1, 5)),
        _review("r2", datetime(2026, 5, 5)),
        _review("r3", datetime(2026, 5, 6)),
        _review("r4", datetime(2026, 5, 7)),
    ]
    predictions = [
        _prediction("r1", Aspect.PENGIRIMAN, Aspect.KEMASAN, Aspect.UKURAN_VARIAN),
        _prediction("r2"),
        _prediction("r3"),
        _prediction("r4"),
    ]

    januari = next(
        b for b in build_period_history(reviews, predictions).buckets if b.label == "Jan 2026"
    )

    assert januari.total_reviews == 1
    assert januari.negative_reviews == 1
    assert januari.pct_negative == pytest.approx(1.0)
