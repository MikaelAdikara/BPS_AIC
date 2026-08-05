"""Unit test calculate_priority_score() (blueprint bagian 32 - formula prioritas bagian 22.2)."""

import pytest

from app.schemas import (
    Aspect,
    AspectAggregate,
    BenchmarkRecord,
    Category,
    ConfidenceLevel,
    Severity,
    Trend,
    Urgency,
)
from app.tools import calculate_priority_score
from app.tools.priority import MIN_REVIEWS_FOR_HIGH_URGENCY


def _aggregate(
    negative: int = 20,
    total: int = 30,
    severity: Severity = Severity.TINGGI,
    trend: Trend = Trend.MENINGKAT,
    confidence: float = 0.9,
) -> AspectAggregate:
    positive = total - negative
    return AspectAggregate(
        aspect=Aspect.UKURAN_VARIAN,
        total_mentions=total,
        negative_count=negative,
        positive_count=positive,
        neutral_count=0,
        pct_negative=negative / total,
        trend=trend,
        avg_confidence=confidence,
        dominant_severity=severity,
    )


def _benchmark(gap: float) -> BenchmarkRecord:
    """Bangun BenchmarkRecord dengan `gap` tertentu, kedua proporsi tetap valid 0-1."""
    baseline_pct = 0.10
    store_pct = min(max(baseline_pct + gap, 0.0), 1.0)
    return BenchmarkRecord(
        category=Category.FASHION,
        aspect=Aspect.UKURAN_VARIAN,
        store_pct=store_pct,
        baseline_pct=baseline_pct,
        baseline_sample_size=1000,
        confidence_level=ConfidenceLevel.TINGGI,
        gap=gap,
    )


def test_skor_selalu_dalam_rentang_0_100():
    for negative, total_reviews, sev, trend in [
        (0, 100, Severity.RENDAH, Trend.MENURUN),
        (100, 100, Severity.TINGGI, Trend.MENINGKAT),
        (50, 100, Severity.SEDANG, Trend.STABIL),
    ]:
        agg = _aggregate(negative=negative, total=max(negative, 1), severity=sev, trend=trend)
        result = calculate_priority_score(agg, total_reviews, _benchmark(0.5))
        assert 0.0 <= result.score <= 100.0


def test_frekuensi_lebih_tinggi_menaikkan_skor():
    rendah = calculate_priority_score(_aggregate(negative=5, total=5), 100)
    tinggi = calculate_priority_score(_aggregate(negative=40, total=40), 100)
    assert tinggi.score > rendah.score


def test_severity_lebih_tinggi_menaikkan_skor():
    ringan = calculate_priority_score(_aggregate(severity=Severity.RENDAH), 100)
    parah = calculate_priority_score(_aggregate(severity=Severity.TINGGI), 100)
    assert parah.score > ringan.score


def test_recency_dan_benchmark_hanya_modifier_bukan_pengali_inti():
    """Aspek yang jarang dan ringan tidak boleh menyalip aspek sering dan parah.

    Ini alasan formula memakai kombinasi (pengali inti x modifier), bukan perkalian mentah
    enam faktor yang menganggap semua faktor sama penting (bagian 22.2).
    """
    jarang_tapi_naik = calculate_priority_score(
        _aggregate(negative=2, total=2, severity=Severity.RENDAH, trend=Trend.MENINGKAT),
        total_reviews=100,
        benchmark=_benchmark(0.5),
    )
    sering_dan_parah = calculate_priority_score(
        _aggregate(negative=40, total=40, severity=Severity.TINGGI, trend=Trend.MENURUN),
        total_reviews=100,
    )
    assert sering_dan_parah.score > jarang_tapi_naik.score


def test_tren_tidak_cukup_data_tidak_memberi_dorongan():
    """Tanpa bukti tren, prioritas tidak boleh naik atas dasar dugaan."""
    tanpa_data = calculate_priority_score(_aggregate(trend=Trend.TIDAK_CUKUP_DATA), 100)
    menurun = calculate_priority_score(_aggregate(trend=Trend.MENURUN), 100)
    assert tanpa_data.score == menurun.score


def test_gap_benchmark_negatif_tidak_menurunkan_skor():
    """Toko yang lebih baik dari baseline tidak mendapat dorongan, tetapi juga tidak dihukum."""
    tanpa = calculate_priority_score(_aggregate(), 100)
    lebih_baik = calculate_priority_score(_aggregate(), 100, _benchmark(-0.3))
    assert lebih_baik.score == tanpa.score


def test_data_kecil_membatasi_urgensi_maksimal_sedang():
    """Bagian 22.2: pada sesi di bawah 15 ulasan, urgensi tidak pernah otomatis 'Tinggi'."""
    agg = _aggregate(negative=10, total=10, severity=Severity.TINGGI, trend=Trend.MENINGKAT)
    result = calculate_priority_score(agg, total_reviews=MIN_REVIEWS_FOR_HIGH_URGENCY - 1)
    assert result.capped_by_small_data is True
    assert result.urgency != Urgency.TINGGI
    assert "kurang dari" in result.reasoning


def test_data_cukup_tidak_dibatasi():
    agg = _aggregate(negative=40, total=40, severity=Severity.TINGGI, trend=Trend.MENINGKAT)
    result = calculate_priority_score(agg, total_reviews=100)
    assert result.capped_by_small_data is False
    assert result.urgency == Urgency.TINGGI


def test_reasoning_selalu_memuat_angka_konkret():
    """Prinsip anti-generik bagian 22.3: penjelasan wajib menyisipkan angka nyata."""
    result = calculate_priority_score(_aggregate(negative=18, total=52), 120)
    assert "18" in result.reasoning
    assert "120" in result.reasoning
    assert result.reasoning.endswith(".")


def test_sensitivity_bobot_dapat_diuji():
    """Bagian 22.2 mewajibkan uji sensitivity +-50% pada bobot 0,3 dan 0,2."""
    agg = _aggregate(trend=Trend.MENINGKAT)
    base = calculate_priority_score(agg, 100, _benchmark(0.4))
    turun = calculate_priority_score(agg, 100, _benchmark(0.4), w_recency=0.15, w_benchmark=0.10)
    naik = calculate_priority_score(agg, 100, _benchmark(0.4), w_recency=0.45, w_benchmark=0.30)
    assert turun.score < base.score < naik.score


def test_urutan_action_card_stabil_terhadap_pergeseran_bobot():
    """Yang penting bukan skor absolutnya, melainkan apakah URUTANNYA berubah drastis.

    Kalau peringkat berbalik hanya karena bobot digeser 50%, formula tidak dapat dipercaya
    sebagai dasar prioritas (bagian 22.2 sensitivity analysis).
    """
    aspek_besar = _aggregate(negative=40, total=40, severity=Severity.TINGGI, trend=Trend.STABIL)
    aspek_kecil = _aggregate(negative=6, total=6, severity=Severity.SEDANG, trend=Trend.MENINGKAT)

    for w_r, w_b in [(0.15, 0.10), (0.30, 0.20), (0.45, 0.30)]:
        besar = calculate_priority_score(aspek_besar, 100, w_recency=w_r, w_benchmark=w_b)
        kecil = calculate_priority_score(aspek_kecil, 100, w_recency=w_r, w_benchmark=w_b)
        assert besar.score > kecil.score, f"urutan berbalik pada bobot {w_r}/{w_b}"


def test_total_reviews_nol_tidak_membagi_nol():
    result = calculate_priority_score(_aggregate(), total_reviews=0)
    assert result.score == pytest.approx(0.0)
