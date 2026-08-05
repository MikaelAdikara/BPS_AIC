"""Unit test calculate_aspect_statistics() (blueprint bagian 32 - matematika agregasi aspek)."""

from datetime import datetime, timedelta

import pytest

from app.schemas import (
    Aspect,
    AspectPrediction,
    Category,
    ProcessedReview,
    Sentiment,
    Severity,
    TextPrediction,
    Trend,
)
from app.tools import calculate_aspect_statistics

NOW = datetime(2026, 8, 5, 12, 0, 0)


def _prediction(review_id: str, *items: tuple[Aspect, Sentiment, Severity, float]) -> TextPrediction:
    return TextPrediction(
        review_id=review_id,
        predictions=[
            AspectPrediction(
                aspect=a, sentiment=s, severity=sev, confidence=c, source_sentence="klausa uji"
            )
            for a, s, sev, c in items
        ],
        model_version="test-v1",
    )


def _review(review_id: str, days_ago: int) -> ProcessedReview:
    return ProcessedReview(
        review_id=review_id,
        clean_text="teks uji",
        pii_redacted=True,
        rating=3,
        category=Category.FASHION,
        has_image=False,
        timestamp=NOW - timedelta(days=days_ago),
    )


def test_menghitung_jumlah_dan_persentase_per_aspek():
    predictions = [
        _prediction("r1", (Aspect.UKURAN_VARIAN, Sentiment.NEGATIF, Severity.TINGGI, 0.9)),
        _prediction("r2", (Aspect.UKURAN_VARIAN, Sentiment.NEGATIF, Severity.SEDANG, 0.8)),
        _prediction("r3", (Aspect.UKURAN_VARIAN, Sentiment.POSITIF, Severity.RENDAH, 0.7)),
        _prediction("r4", (Aspect.PENGIRIMAN, Sentiment.POSITIF, Severity.RENDAH, 0.6)),
    ]
    result = {a.aspect: a for a in calculate_aspect_statistics(predictions)}

    ukuran = result[Aspect.UKURAN_VARIAN]
    assert ukuran.total_mentions == 3
    assert ukuran.negative_count == 2
    assert ukuran.positive_count == 1
    assert ukuran.pct_negative == pytest.approx(2 / 3, abs=1e-4)
    assert ukuran.avg_confidence == pytest.approx(0.8, abs=1e-4)
    # Severity aspek = rata-rata peringkat keluhannya, dibulatkan. Di sini [tinggi, sedang]
    # -> rata-rata 1,5 -> dibulatkan ke atas menjadi tinggi.
    assert ukuran.dominant_severity == Severity.TINGGI


def test_severity_memakai_rata_rata_bukan_terparah():
    """Satu keluhan berat di antara banyak keluhan ringan tidak boleh mengangkat seluruh aspek.

    Kalau severity diambil dari yang terparah, satu ulasan bintang satu cukup membuat SETIAP
    aspek berlabel 'tinggi' - faktor severity lalu konstan dan berhenti membedakan prioritas.
    """
    predictions = [
        _prediction("r1", (Aspect.KEMASAN, Sentiment.NEGATIF, Severity.TINGGI, 0.9)),
        *[
            _prediction(f"r{i}", (Aspect.KEMASAN, Sentiment.NEGATIF, Severity.RENDAH, 0.9))
            for i in range(2, 8)
        ],
    ]
    result = calculate_aspect_statistics(predictions)
    assert result[0].dominant_severity == Severity.RENDAH


def test_severity_naik_saat_keluhan_berat_mendominasi():
    predictions = [
        _prediction(f"r{i}", (Aspect.KEMASAN, Sentiment.NEGATIF, Severity.TINGGI, 0.9))
        for i in range(5)
    ] + [_prediction("r9", (Aspect.KEMASAN, Sentiment.NEGATIF, Severity.RENDAH, 0.9))]
    result = calculate_aspect_statistics(predictions)
    assert result[0].dominant_severity == Severity.TINGGI


def test_diurutkan_menurun_berdasarkan_keluhan():
    predictions = [
        _prediction("r1", (Aspect.KEMASAN, Sentiment.NEGATIF, Severity.RENDAH, 0.5)),
        _prediction("r2", (Aspect.PENGIRIMAN, Sentiment.NEGATIF, Severity.RENDAH, 0.5)),
        _prediction("r3", (Aspect.PENGIRIMAN, Sentiment.NEGATIF, Severity.RENDAH, 0.5)),
    ]
    result = calculate_aspect_statistics(predictions)
    assert result[0].aspect == Aspect.PENGIRIMAN
    assert result[0].negative_count == 2


def test_tanpa_timestamp_tren_tidak_ditebak():
    """Tanpa timestamp, tren WAJIB `tidak_cukup_data` - bukan `stabil`.

    Menebak "stabil" akan menyiratkan sistem sudah memeriksa dan tidak menemukan perubahan,
    padahal ia tidak punya dasar sama sekali untuk menyimpulkan itu.
    """
    predictions = [_prediction("r1", (Aspect.PENGIRIMAN, Sentiment.NEGATIF, Severity.RENDAH, 0.9))]
    result = calculate_aspect_statistics(predictions)
    assert result[0].trend == Trend.TIDAK_CUKUP_DATA


def test_tren_meningkat_terdeteksi_dari_proporsi():
    # Jendela lama: 1 dari 4 negatif (25%). Jendela baru: 4 dari 4 negatif (100%).
    predictions, reviews = [], []
    for i in range(4):
        rid = f"old{i}"
        sentiment = Sentiment.NEGATIF if i == 0 else Sentiment.POSITIF
        predictions.append(_prediction(rid, (Aspect.UKURAN_VARIAN, sentiment, Severity.RENDAH, 0.8)))
        reviews.append(_review(rid, days_ago=60))
    for i in range(4):
        rid = f"new{i}"
        predictions.append(
            _prediction(rid, (Aspect.UKURAN_VARIAN, Sentiment.NEGATIF, Severity.TINGGI, 0.8))
        )
        reviews.append(_review(rid, days_ago=5))

    result = calculate_aspect_statistics(predictions, reviews, now=NOW)
    assert result[0].trend == Trend.MENINGKAT


def test_tren_memakai_proporsi_bukan_jumlah_mentah():
    """Batch terbaru yang lebih besar tidak boleh terlihat sebagai tren memburuk.

    Kedua jendela punya proporsi keluhan 50%, tetapi jendela baru jumlahnya dua kali lipat.
    Perbandingan berbasis jumlah mentah akan salah melaporkan "meningkat".
    """
    predictions, reviews = [], []
    for i in range(4):  # lama: 2 dari 4 negatif
        rid = f"old{i}"
        s = Sentiment.NEGATIF if i < 2 else Sentiment.POSITIF
        predictions.append(_prediction(rid, (Aspect.KEMASAN, s, Severity.RENDAH, 0.8)))
        reviews.append(_review(rid, days_ago=60))
    for i in range(8):  # baru: 4 dari 8 negatif
        rid = f"new{i}"
        s = Sentiment.NEGATIF if i < 4 else Sentiment.POSITIF
        predictions.append(_prediction(rid, (Aspect.KEMASAN, s, Severity.RENDAH, 0.8)))
        reviews.append(_review(rid, days_ago=5))

    result = calculate_aspect_statistics(predictions, reviews, now=NOW)
    assert result[0].trend == Trend.STABIL


def test_jendela_terlalu_sedikit_tidak_menghasilkan_tren():
    predictions = [
        _prediction("r1", (Aspect.PENGIRIMAN, Sentiment.NEGATIF, Severity.RENDAH, 0.9)),
        _prediction("r2", (Aspect.PENGIRIMAN, Sentiment.NEGATIF, Severity.RENDAH, 0.9)),
    ]
    reviews = [_review("r1", 60), _review("r2", 5)]
    result = calculate_aspect_statistics(predictions, reviews, now=NOW)
    assert result[0].trend == Trend.TIDAK_CUKUP_DATA


def test_input_kosong_menghasilkan_daftar_kosong():
    assert calculate_aspect_statistics([]) == []


def test_idempotent():
    """Bagian 27.3: seluruh tool deterministic wajib idempotent."""
    predictions = [
        _prediction("r1", (Aspect.HARGA_VALUE, Sentiment.NEGATIF, Severity.SEDANG, 0.77)),
        _prediction("r2", (Aspect.HARGA_VALUE, Sentiment.POSITIF, Severity.RENDAH, 0.55)),
    ]
    assert calculate_aspect_statistics(predictions) == calculate_aspect_statistics(predictions)
