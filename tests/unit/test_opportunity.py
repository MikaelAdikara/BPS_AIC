"""Test OPP-01 dan ING-05 (blueprint bagian 8.2, 22.3)."""

from __future__ import annotations

import pytest

from app.schemas import Aspect, AspectAggregate, Severity, Trend
from app.tools import find_opportunities, score_data_quality


def _agg(aspect: Aspect, positive: int, negative: int = 0, neutral: int = 0) -> AspectAggregate:
    total = positive + negative + neutral
    return AspectAggregate(
        aspect=aspect,
        total_mentions=total,
        negative_count=negative,
        positive_count=positive,
        neutral_count=neutral,
        pct_negative=negative / total if total else 0.0,
        trend=Trend.STABIL,
        avg_confidence=0.8,
        dominant_severity=Severity.RENDAH,
    )


# ---------------------------------------------------------------- OPP-01


def test_aspek_yang_dominan_dipuji_menjadi_peluang():
    opps = find_opportunities([_agg(Aspect.PENGIRIMAN, positive=9, negative=1)], total_reviews=30)
    assert len(opps) == 1
    assert opps[0].aspect == Aspect.PENGIRIMAN
    assert opps[0].pct_positive == pytest.approx(0.9)


def test_aspek_yang_banyak_dikeluhkan_bukan_peluang():
    """Menyebut aspek bermasalah sebagai kekuatan akan menyesatkan pemilik toko."""
    assert find_opportunities([_agg(Aspect.PENGIRIMAN, positive=4, negative=6)], 30) == []


def test_pujian_yang_terlalu_jarang_tidak_diangkat():
    """Dua sebutan positif bukan bukti kekuatan — itu kebetulan."""
    assert find_opportunities([_agg(Aspect.KEMASAN, positive=2)], total_reviews=50) == []


def test_peluang_terurut_dari_yang_paling_sering_dipuji():
    opps = find_opportunities(
        [_agg(Aspect.KEMASAN, positive=6), _agg(Aspect.PENGIRIMAN, positive=20)], 40
    )
    assert [o.aspect for o in opps] == [Aspect.PENGIRIMAN, Aspect.KEMASAN]


def test_jumlah_peluang_dibatasi():
    """Layar hasil kehilangan fokus bila seluruh aspek positif ditampilkan sekaligus."""
    aggs = [_agg(a, positive=10) for a in list(Aspect)[:6]]
    assert len(find_opportunities(aggs, total_reviews=60)) == 3


def test_setiap_peluang_punya_kalimat_yang_dapat_dibaca():
    for opp in find_opportunities([_agg(Aspect.PELAYANAN_PENJUAL, positive=8)], 20):
        assert opp.highlight and not opp.highlight.endswith("_")


# ---------------------------------------------------------------- ING-05


def test_data_lengkap_mendapat_skor_penuh():
    q = score_data_quality(100, 100, 0, 100, 100, 0)
    assert q.score == 100
    assert q.level == "baik"
    assert q.notes  # tetap ada penjelasan, tidak pernah kosong


def test_data_sangat_sedikit_menurunkan_skor_drastis():
    q = score_data_quality(10, 8, 2, 8, 8, 0)
    assert q.score < 75
    assert any("indikasi awal" in n for n in q.notes)


def test_tanpa_rating_dan_tanggal_dijelaskan_batasannya():
    """Pengguna berhak tahu KENAPA angkanya turun, bukan hanya bahwa ia turun."""
    q = score_data_quality(100, 100, 0, 0, 0, 0)
    assert q.score == 60
    assert any("rating" in n for n in q.notes)
    assert any("tanggal" in n for n in q.notes)


def test_redaksi_pii_dilaporkan_tanpa_menghukum_skor():
    """Menyamarkan PII adalah perilaku benar sistem, bukan cacat data pengguna."""
    bersih = score_data_quality(100, 100, 0, 100, 100, 0)
    ada_pii = score_data_quality(100, 100, 0, 100, 100, 5)
    assert ada_pii.score == bersih.score
    assert any("data pribadi" in n for n in ada_pii.notes)


def test_skor_tidak_pernah_negatif():
    q = score_data_quality(100, 3, 60, 0, 0, 0)
    assert 0 <= q.score <= 100
    assert q.level == "terbatas"


def test_batch_kosong_tidak_membagi_nol():
    assert score_data_quality(0, 0, 0, 0, 0, 0).score >= 0
