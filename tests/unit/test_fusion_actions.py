"""Unit test FUS-01 dan ACT-01 (blueprint bagian 20.1, 22.1, 22.3)."""

import pytest

from app.schemas import (
    Aspect,
    AspectAggregate,
    AspectPrediction,
    FusedEvidenceType,
    Sentiment,
    Severity,
    TextPrediction,
    Trend,
    VisualLabel,
    VisualPrediction,
)
from app.tools import build_action_card, fuse_review, has_concrete_numbers
from app.tools.priority import calculate_priority_score


def _text(review_id="r1", sentiment=Sentiment.NEGATIF, confidence=0.9) -> TextPrediction:
    return TextPrediction(
        review_id=review_id,
        predictions=[
            AspectPrediction(
                aspect=Aspect.KUALITAS_PRODUK, sentiment=sentiment,
                severity=Severity.TINGGI, confidence=confidence, source_sentence="barang rusak",
            )
        ],
        model_version="test",
    )


def _visual(label=VisualLabel.PRODUK_RUSAK, abstain=False, confidence=0.8) -> VisualPrediction:
    return VisualPrediction(
        image_ref="img1", review_id="r1",
        label=None if abstain else label, abstain=abstain, confidence=confidence,
        abstain_reason="skor di bawah threshold semua kelas" if abstain else None,
        model_version="test",
    )


# ---------------------------------------------------------------- FUS-01


def test_tanpa_foto_jalur_visual_dilewati_bukan_error():
    """Kasus 5 bagian 20.1 - ketiadaan foto adalah keadaan normal, bukan kegagalan."""
    result = fuse_review("r1", _text(), [])
    assert result.fused_evidence_type == FusedEvidenceType.TEXT_ONLY
    assert result.contradiction_flag is False
    assert result.requires_human_review is False


def test_foto_abstain_tidak_menurunkan_confidence_teks():
    """Kasus 2 - ketidaktahuan model visual bukan bukti yang berlawanan."""
    tanpa_foto = fuse_review("r1", _text(confidence=0.88), [])
    dengan_abstain = fuse_review("r1", _text(confidence=0.88), [_visual(abstain=True)])
    assert dengan_abstain.combined_confidence == tanpa_foto.combined_confidence
    assert dengan_abstain.fused_evidence_type == FusedEvidenceType.VISUAL_ABSTAIN
    assert dengan_abstain.requires_human_review is False


def test_teks_dan_foto_sejalan_menaikkan_confidence():
    """Kasus 1 - keduanya menunjuk arah sama."""
    result = fuse_review("r1", _text(confidence=0.9), [_visual(confidence=0.7)])
    assert result.fused_evidence_type == FusedEvidenceType.TEXT_AND_VISUAL_AGREE
    assert result.display_note == "Didukung bukti visual"
    assert 0.7 < result.combined_confidence < 0.9  # rata-rata berbobot, condong ke teks


def test_teks_positif_foto_bermasalah_memicu_tinjauan_manusia():
    """Kasus 3 - sistem TIDAK PERNAH memutuskan siapa yang benar."""
    result = fuse_review("r1", _text(sentiment=Sentiment.POSITIF), [_visual()])
    assert result.fused_evidence_type == FusedEvidenceType.TEXT_VISUAL_CONTRADICTION
    assert result.contradiction_flag is True
    assert result.requires_human_review is True
    assert "ditinjau manual" in result.display_note


def test_teks_negatif_foto_normal_juga_kontradiksi():
    """Kasus 4 - arah berlawanan tetap ditandai, apa pun sisi yang 'positif'."""
    result = fuse_review("r1", _text(), [_visual(label=VisualLabel.NORMAL)])
    assert result.contradiction_flag is True
    assert result.requires_human_review is True


def test_hanya_foto_tanpa_teks_menyebut_keterbatasan_konteks():
    """Kasus 6 - visual tetap diproses, keterbatasannya disebut eksplisit."""
    kosong = TextPrediction(review_id="r1", predictions=[], model_version="test")
    result = fuse_review("r1", kosong, [_visual()])
    assert result.fused_evidence_type == FusedEvidenceType.VISUAL_ONLY
    assert "tanpa teks" in result.display_note


def test_foto_paling_yakin_yang_dipakai():
    lemah = VisualPrediction(
        image_ref="a", review_id="r1", label=VisualLabel.NORMAL, abstain=False,
        confidence=0.55, model_version="test",
    )
    kuat = VisualPrediction(
        image_ref="b", review_id="r1", label=VisualLabel.PRODUK_RUSAK, abstain=False,
        confidence=0.92, model_version="test",
    )
    result = fuse_review("r1", _text(), [lemah, kuat])
    # Foto terkuat menunjukkan masalah dan teks juga negatif -> sejalan, bukan kontradiksi.
    assert result.fused_evidence_type == FusedEvidenceType.TEXT_AND_VISUAL_AGREE


# ---------------------------------------------------------------- ACT-01


def _aggregate(aspect=Aspect.UKURAN_VARIAN, negative=25, total=41) -> AspectAggregate:
    return AspectAggregate(
        aspect=aspect, total_mentions=total, negative_count=negative,
        positive_count=total - negative, neutral_count=0,
        pct_negative=negative / total, trend=Trend.MENINGKAT,
        avg_confidence=0.8, dominant_severity=Severity.SEDANG,
    )


def _card(aspect=Aspect.UKURAN_VARIAN, total_reviews=120):
    aggregate = _aggregate(aspect=aspect)
    priority = calculate_priority_score(aggregate, total_reviews)
    return build_action_card("ACT-001", aggregate, priority, total_reviews)


def test_rekomendasi_selalu_memuat_angka_konkret():
    """Prinsip anti-generik bagian 22.3 - kalimat tanpa angka dianggap cacat."""
    for aspect in Aspect:
        card = _card(aspect=aspect)
        assert has_concrete_numbers(card), f"rekomendasi {aspect.value} tidak memuat angka"


def test_judul_memakai_kata_kerja_yang_dapat_dikerjakan():
    card = _card()
    assert card.title[0].isupper()
    # Judul harus menyebut tindakan, bukan istilah abstrak seperti "optimasi listing".
    assert any(k in card.title.lower() for k in ("perbaiki", "periksa", "tinjau", "tambahkan"))


def test_user_action_selalu_kosong_saat_dibuat():
    """ADR-013 - sistem tidak pernah mengeksekusi atau menyetujui sendiri."""
    assert _card().user_action is None


def test_risiko_bila_rekomendasi_keliru_selalu_ada():
    """Setiap kartu wajib mengakui kemungkinan dirinya salah."""
    card = _card()
    assert len(card.risk_if_recommendation_wrong) > 20


def test_tren_meningkat_disebut_di_rekomendasi():
    assert "meningkat" in _card().recommended_action


def test_kontradiksi_banyak_mengalihkan_ke_kategori_investigasi():
    from app.schemas import ActionCategory, MultimodalEvidence

    contradictions = [
        MultimodalEvidence(
            review_id=f"r{i}", fused_evidence_type=FusedEvidenceType.TEXT_VISUAL_CONTRADICTION,
            combined_confidence=0.5, contradiction_flag=True,
            display_note="perlu ditinjau manual", requires_human_review=True,
        )
        for i in range(4)
    ]
    aggregate = _aggregate()
    priority = calculate_priority_score(aggregate, 120)
    card = build_action_card("ACT-002", aggregate, priority, 120, contradictions=contradictions)
    assert card.action_category == ActionCategory.INVESTIGATION_NEEDED
    assert "4" in card.recommended_action


def test_setiap_aspek_punya_kategori_tindakan():
    from app.tools.actions import ASPECT_TO_CATEGORY

    assert set(ASPECT_TO_CATEGORY) == set(Aspect), "ada aspek tanpa pemetaan kategori tindakan"


def test_kartu_berbeda_aspek_menghasilkan_rekomendasi_berbeda():
    """Kartu yang seragam adalah gejala template generik (bagian 22.3)."""
    texts = {_card(aspect=a).recommended_action for a in Aspect}
    assert len(texts) >= 5, "terlalu banyak aspek menghasilkan kalimat rekomendasi identik"


def test_tidak_ada_dua_kartu_berjudul_sama():
    """Judul kembar pada satu layar hasil terbaca sebagai sistem yang rusak.

    Sebuah kategori dapat mencakup beberapa aspek (PACKAGING mencakup kemasan DAN
    pengiriman), sehingga judul yang tidak memuat {label} akan menghasilkan dua kartu
    yang tampak identik padahal membahas hal berbeda.
    """
    from app.tools.actions import ASPECT_LABEL, ASPECT_TO_CATEGORY, CATEGORY_TEMPLATE

    judul = {}
    for aspek, kategori in ASPECT_TO_CATEGORY.items():
        t = CATEGORY_TEMPLATE[kategori]["title"].format(label=ASPECT_LABEL[aspek])
        assert t not in judul, (
            f"aspek {aspek.value} dan {judul[t].value} menghasilkan judul sama: {t!r}"
        )
        judul[t] = aspek
