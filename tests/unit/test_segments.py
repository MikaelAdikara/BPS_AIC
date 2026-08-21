"""Unit test build_rating_breakdown() dan summarize_products() (apps/api/app/tools/segments.py).

Yang diuji di sini bukan "apakah angkanya keluar" melainkan tiga janji yang dibuat berkas itu:
pita bintang selalu lengkap lima meski ada yang kosong, satu ulasan tidak pernah dihitung dua
kali di dalam satu irisan, dan produk bersampel tipis ditandai alih-alih dibuang.
"""

from datetime import datetime

import pytest

from app.schemas import (
    Aspect,
    AspectPrediction,
    Category,
    ProcessedReview,
    Sentiment,
    Severity,
    TextPrediction,
)
from app.tools import build_rating_breakdown, summarize_products


def _review(
    review_id: str,
    rating: int | None = 5,
    product: str | None = None,
    text: str = "teks uji",
) -> ProcessedReview:
    return ProcessedReview(
        review_id=review_id,
        clean_text=text,
        pii_redacted=False,
        rating=rating,
        category=Category.FASHION,
        has_image=False,
        timestamp=datetime(2026, 7, 1),
        product_name=product,
    )


def _prediction(review_id: str, *items: tuple[Aspect, Sentiment]) -> TextPrediction:
    return TextPrediction(
        review_id=review_id,
        predictions=[
            AspectPrediction(
                aspect=a,
                sentiment=s,
                severity=Severity.SEDANG,
                confidence=0.8,
                source_sentence="klausa uji",
            )
            for a, s in items
        ],
        model_version="test-v1",
    )


# ---------------------------------------------------------------------------------------
# build_rating_breakdown()
# ---------------------------------------------------------------------------------------


def test_lima_pita_selalu_ada_meski_sebagian_kosong():
    """Pita tanpa ulasan tetap digambar.

    Grafik yang melewatkan pita kosong menggeser pita di sebelahnya ke posisi yang salah, dan
    bentuk sebaran - satu-satunya hal yang dibaca dari grafik ini - jadi keliru.
    """
    reviews = [_review("r1", 1), _review("r2", 5)]
    predictions = [_prediction("r1"), _prediction("r2")]

    hasil = build_rating_breakdown(reviews, predictions)

    assert [b.rating for b in hasil.bands] == [1, 2, 3, 4, 5]
    assert [b.count for b in hasil.bands] == [1, 0, 0, 0, 1]


def test_ulasan_tanpa_rating_dihitung_terpisah_bukan_dibuang():
    reviews = [_review("r1", 4), _review("r2", None), _review("r3", None)]
    predictions = [_prediction(r.review_id) for r in reviews]

    hasil = build_rating_breakdown(reviews, predictions)

    assert hasil.total_rated == 1
    assert hasil.without_rating == 2
    assert hasil.average == 4.0


def test_tanpa_rating_sama_sekali_mengembalikan_none():
    """Bukan lima batang nol - bagiannya tidak dirender sama sekali.

    Lima batang kosong terbaca sebagai "semua pembeli memberi nol bintang", yang tidak mungkin
    dan tidak dimaksudkan.
    """
    reviews = [_review("r1", None), _review("r2", None)]
    predictions = [_prediction(r.review_id) for r in reviews]

    assert build_rating_breakdown(reviews, predictions) is None


def test_keluhan_dilaporkan_per_pita_bukan_untuk_seluruh_batch():
    """Inti potongan ini: keluhan apa yang menghuni bintang berapa."""
    reviews = [_review("r1", 1), _review("r2", 1), _review("r3", 5)]
    predictions = [
        _prediction("r1", (Aspect.UKURAN_VARIAN, Sentiment.NEGATIF)),
        _prediction("r2", (Aspect.UKURAN_VARIAN, Sentiment.NEGATIF)),
        _prediction("r3", (Aspect.PENGIRIMAN, Sentiment.NEGATIF)),
    ]

    bands = {b.rating: b for b in build_rating_breakdown(reviews, predictions).bands}

    assert [(c.aspect, c.count) for c in bands[1].complaints] == [(Aspect.UKURAN_VARIAN, 2)]
    assert [(c.aspect, c.count) for c in bands[5].complaints] == [(Aspect.PENGIRIMAN, 1)]


def test_satu_ulasan_yang_menyebut_aspek_dua_kali_dihitung_sekali():
    """Ulasan yang mengeluhkan ukuran di dua klausa tetap SATU ulasan yang mengeluhkan ukuran.

    Tanpa penghapusan duplikat, satu pita bisa melaporkan lebih banyak keluhan daripada jumlah
    ulasan di dalamnya - angka yang langsung terbaca salah oleh siapa pun yang menjumlahkan.
    """
    reviews = [_review("r1", 2)]
    predictions = [
        _prediction(
            "r1",
            (Aspect.UKURAN_VARIAN, Sentiment.NEGATIF),
            (Aspect.UKURAN_VARIAN, Sentiment.NEGATIF),
        )
    ]

    band = build_rating_breakdown(reviews, predictions).bands[1]

    assert band.count == 1
    assert [c.count for c in band.complaints] == [1]


def test_sentimen_positif_tidak_masuk_daftar_keluhan():
    reviews = [_review("r1", 5)]
    predictions = [_prediction("r1", (Aspect.KEMASAN, Sentiment.POSITIF))]

    assert build_rating_breakdown(reviews, predictions).bands[4].complaints == []


# ---------------------------------------------------------------------------------------
# summarize_products()
# ---------------------------------------------------------------------------------------


def test_tanpa_kolom_produk_mengembalikan_larik_kosong():
    reviews = [_review("r1", 5), _review("r2", 4)]
    predictions = [_prediction(r.review_id) for r in reviews]

    assert summarize_products(reviews, predictions) == []


def test_dikelompokkan_per_nama_dan_terurut_menurun():
    reviews = [
        _review("r1", 5, "Kemeja Linen"),
        _review("r2", 4, "Kemeja Linen"),
        _review("r3", 3, "Celana Chino"),
    ]
    predictions = [_prediction(r.review_id) for r in reviews]

    hasil = summarize_products(reviews, predictions)

    assert [p.product_name for p in hasil] == ["Kemeja Linen", "Celana Chino"]
    assert [p.total_reviews for p in hasil] == [2, 1]


def test_produk_tipis_ditandai_bukan_dibuang():
    """Ekor panjang adalah bentuk data yang perlu pengguna lihat, bukan yang disembunyikan.

    Berkas kurasi memuat 90 produk atas 120 ulasan. Membuang yang tipis akan menyembunyikan
    kenyataan bahwa perbandingan per produk tidak bermakna pada data berbentuk seperti itu.
    """
    reviews = [
        _review("r1", 5, "Ramai"),
        _review("r2", 5, "Ramai"),
        _review("r3", 5, "Ramai"),
        _review("r4", 5, "Sepi"),
    ]
    predictions = [_prediction(r.review_id) for r in reviews]

    hasil = {p.product_name: p for p in summarize_products(reviews, predictions)}

    assert hasil["Ramai"].sparse is False
    assert hasil["Sepi"].sparse is True


def test_ulasan_tanpa_nama_produk_tetap_masuk_sebagai_kelompok_sendiri():
    """Jumlah baris tabel produk harus tetap berjumlah total ulasan.

    Kalau ulasan tanpa nama produk diam-diam hilang, pengguna yang menjumlahkan sendiri akan
    menemukan selisih yang tidak dijelaskan di mana pun.
    """
    reviews = [_review("r1", 5, "Kemeja Linen"), _review("r2", 4, None)]
    predictions = [_prediction(r.review_id) for r in reviews]

    hasil = summarize_products(reviews, predictions)

    assert sum(p.total_reviews for p in hasil) == 2
    assert "Tanpa nama produk" in {p.product_name for p in hasil}


def test_histogram_bintang_selalu_lima_keranjang_per_produk():
    """Batang mini antar baris tabel hanya bisa dibandingkan kalau panjangnya sama."""
    reviews = [_review("r1", 1, "Kemeja Linen"), _review("r2", 1, "Kemeja Linen")]
    predictions = [_prediction(r.review_id) for r in reviews]

    assert summarize_products(reviews, predictions)[0].ratings == [2, 0, 0, 0, 0]


def test_persentase_negatif_dihitung_per_ulasan_bukan_per_sebutan():
    reviews = [
        _review("r1", 2, "Kemeja Linen"),
        _review("r2", 5, "Kemeja Linen"),
    ]
    predictions = [
        _prediction(
            "r1",
            (Aspect.UKURAN_VARIAN, Sentiment.NEGATIF),
            (Aspect.KEMASAN, Sentiment.NEGATIF),
        ),
        _prediction("r2", (Aspect.KEMASAN, Sentiment.POSITIF)),
    ]

    hasil = summarize_products(reviews, predictions)[0]

    assert hasil.negative_reviews == 1
    assert hasil.pct_negative == pytest.approx(0.5)
