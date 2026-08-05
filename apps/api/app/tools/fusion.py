"""FUS-01 - penggabungan bukti teks dan visual (blueprint bagian 20).

Mekanismenya RULE-GUIDED dan CONFIDENCE-AWARE, bukan neural fusion. Setiap keputusan gabungan
dapat ditelusuri ke satu baris aturan di bawah dan dijelaskan ke pengguna maupun juri - itulah
alasan pendekatan ini dipilih meski neural fusion terlihat lebih canggih.

Prinsip yang tidak bisa ditawar: **sistem tidak pernah memutuskan siapa yang benar antara teks
dan foto.** Saat keduanya bertentangan, keduanya ditampilkan apa adanya dan ditandai untuk
ditinjau manusia.
"""

from __future__ import annotations

from ..schemas import (
    FusedEvidenceType,
    MultimodalEvidence,
    Sentiment,
    TextPrediction,
    VisualPrediction,
)

# Kelas visual yang menandakan ada masalah fisik pada produk atau kemasannya.
PROBLEM_LABELS = {"produk_rusak", "salah_kirim", "kemasan_rusak"}

# Bobot teks saat teks dan visual sejalan. Teks diberi porsi lebih besar karena ialah satu-satunya
# lapisan yang benar-benar di-fine-tune pada domain ini; visual masih zero-shot dan belum lolos
# go/no-go gate (bagian 19.3).
TEXT_WEIGHT_ON_AGREEMENT = 0.6

# Confidence gabungan saat teks dan visual bertentangan. Sengaja ditahan di tengah: sistem tidak
# tahu mana yang benar, dan angka tinggi akan menyiratkan keyakinan yang tidak dimilikinya.
CONTRADICTION_CONFIDENCE = 0.5


def _text_signal(prediction: TextPrediction | None) -> tuple[bool, float]:
    """Ringkas prediksi teks satu ulasan menjadi (ada keluhan?, confidence tertinggi)."""
    if prediction is None or not prediction.predictions:
        return False, 0.0
    negatives = [p for p in prediction.predictions if p.sentiment == Sentiment.NEGATIF]
    if negatives:
        return True, max(p.confidence for p in negatives)
    return False, max(p.confidence for p in prediction.predictions)


def fuse_review(
    review_id: str,
    text_prediction: TextPrediction | None,
    visual_predictions: list[VisualPrediction] | None = None,
) -> MultimodalEvidence:
    """Gabungkan bukti teks dan visual untuk SATU ulasan (delapan kasus bagian 20.1)."""
    visuals = visual_predictions or []
    has_text = text_prediction is not None and bool(text_prediction.predictions)
    text_negative, text_conf = _text_signal(text_prediction)

    # Kasus 5 - hanya teks. Jalur visual dilewati sepenuhnya, ini BUKAN error.
    if not visuals:
        return MultimodalEvidence(
            review_id=review_id,
            fused_evidence_type=FusedEvidenceType.TEXT_ONLY,
            combined_confidence=round(text_conf, 4),
            contradiction_flag=False,
            display_note=None,
            requires_human_review=False,
        )

    confident = [v for v in visuals if not v.abstain and v.label is not None]

    # Kasus 2 - foto ada tetapi tidak dapat disimpulkan. Visual TIDAK menurunkan confidence teks;
    # ketidaktahuan bukan bukti yang berlawanan.
    if not confident:
        return MultimodalEvidence(
            review_id=review_id,
            fused_evidence_type=FusedEvidenceType.VISUAL_ABSTAIN,
            combined_confidence=round(text_conf, 4),
            contradiction_flag=False,
            display_note="Tidak dapat menyimpulkan kondisi produk dari foto ini",
            requires_human_review=False,
        )

    strongest = max(confident, key=lambda v: v.confidence)
    visual_problem = strongest.label.value in PROBLEM_LABELS

    # Kasus 6 - hanya foto, teks kosong atau terlalu pendek untuk dinilai.
    if not has_text:
        return MultimodalEvidence(
            review_id=review_id,
            fused_evidence_type=FusedEvidenceType.VISUAL_ONLY,
            combined_confidence=round(strongest.confidence, 4),
            contradiction_flag=False,
            display_note="Ulasan ini hanya memuat foto tanpa teks yang cukup untuk dinilai",
            requires_human_review=False,
        )

    # Kasus 3 & 4 - teks dan foto bertentangan arah.
    if text_negative != visual_problem:
        note = (
            "Ulasan menyebut puas namun foto menunjukkan indikasi masalah - perlu ditinjau manual"
            if visual_problem
            else "Ulasan menyebut ada masalah namun foto tampak normal - perlu ditinjau manual"
        )
        return MultimodalEvidence(
            review_id=review_id,
            fused_evidence_type=FusedEvidenceType.TEXT_VISUAL_CONTRADICTION,
            combined_confidence=CONTRADICTION_CONFIDENCE,
            contradiction_flag=True,
            display_note=note,
            requires_human_review=True,  # dipaksa juga oleh validator schema
        )

    # Kasus 1, 7, 8 - teks dan foto sejalan.
    combined = (
        TEXT_WEIGHT_ON_AGREEMENT * text_conf
        + (1 - TEXT_WEIGHT_ON_AGREEMENT) * strongest.confidence
    )
    return MultimodalEvidence(
        review_id=review_id,
        fused_evidence_type=FusedEvidenceType.TEXT_AND_VISUAL_AGREE,
        combined_confidence=round(combined, 4),
        contradiction_flag=False,
        display_note="Didukung bukti visual" if visual_problem else None,
        requires_human_review=False,
    )


def fuse_all(
    text_predictions: list[TextPrediction],
    visual_predictions: list[VisualPrediction] | None = None,
) -> list[MultimodalEvidence]:
    """Jalankan fusion untuk seluruh ulasan pada sesi."""
    by_review: dict[str, list[VisualPrediction]] = {}
    for visual in visual_predictions or []:
        by_review.setdefault(visual.review_id, []).append(visual)

    text_by_review = {t.review_id: t for t in text_predictions}
    review_ids = list(text_by_review) + [r for r in by_review if r not in text_by_review]

    return [
        fuse_review(review_id, text_by_review.get(review_id), by_review.get(review_id))
        for review_id in review_ids
    ]
