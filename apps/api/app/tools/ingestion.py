"""preprocess_reviews() — ING-01, tool contract bagian 27.3.

Titik masuk tunggal data ke sistem. Selalu berjalan pertama, dan selalu diikuti
`redact_personal_data()` sebelum model manapun melihat teksnya.

Kegagalan di sini ditangani dengan cara yang berbeda dari kegagalan model: baris yang rusak
DILEWATI dan dicatat sebagai peringatan, bukan menggagalkan seluruh analisis. Pengguna yang
mengunggah 200 ulasan tidak boleh kehilangan semuanya karena tiga baris bermasalah (bagian 35).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..schemas import Category, ProcessedReview, RawReview
from .privacy import redact_personal_data

# Di bawah ini teks dianggap tidak cukup untuk dianalisis.
MIN_TEXT_LENGTH = 3

# Ambang peringatan data kecil (bagian 22.2, 14.1) - hasil tetap ditampilkan, tetapi
# dengan peringatan bahwa ia indikasi awal, bukan kesimpulan.
MIN_REVIEWS_FOR_CONFIDENCE = 15


@dataclass
class PreprocessResult:
    reviews: list[ProcessedReview] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    skipped: int = 0
    pii_redacted_count: int = 0


def preprocess_reviews(raw: list[RawReview], now: datetime | None = None) -> PreprocessResult:
    """Validasi, redaksi PII, dan normalisasi batch ulasan mentah.

    Args:
        raw: hasil parsing unggahan pengguna
        now: dipakai untuk `retained_until` pada rujukan gambar; diekspos agar dapat diuji

    Returns:
        PreprocessResult - `warnings` memuat kode yang dipetakan frontend ke pesan
        Bahasa Indonesia sederhana (bagian 14 microcopy), bukan pesan teknis mentah.
    """
    result = PreprocessResult()
    seen_ids: set[str] = set()
    seen_texts: set[str] = set()

    for item in raw:
        text = (item.text or "").strip()

        if len(text) < MIN_TEXT_LENGTH and not item.image_paths:
            result.skipped += 1
            continue

        # Duplikat exact dibuang agar tidak menggandakan bobot satu keluhan pada statistik.
        normalized_key = text.lower()
        if normalized_key and normalized_key in seen_texts:
            result.skipped += 1
            continue
        seen_texts.add(normalized_key)

        # review_id ganda akan merusak penelusuran bukti - beri akhiran unik, jangan buang.
        review_id = item.review_id
        if review_id in seen_ids:
            review_id = f"{review_id}_{len(seen_ids)}"
        seen_ids.add(review_id)

        redaction = redact_personal_data(text)
        if redaction.redacted:
            result.pii_redacted_count += 1

        result.reviews.append(
            ProcessedReview(
                review_id=review_id,
                clean_text=redaction.text,
                pii_redacted=redaction.redacted,
                rating=item.rating,
                category=item.category or Category.OTHER,
                has_image=bool(item.image_paths),
                image_refs=list(item.image_paths),
                timestamp=item.timestamp,
            )
        )

    if result.skipped:
        result.warnings.append("baris_dilewati")
    if len(result.reviews) < MIN_REVIEWS_FOR_CONFIDENCE:
        result.warnings.append("data_kecil")
    if result.pii_redacted_count:
        result.warnings.append("pii_diredaksi")

    return result
