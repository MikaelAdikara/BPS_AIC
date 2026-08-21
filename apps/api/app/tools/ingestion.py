"""preprocess_reviews() - ING-01, tool contract bagian 27.3.

Titik masuk tunggal data ke sistem. Selalu berjalan pertama, dan selalu diikuti
`redact_personal_data()` sebelum model manapun melihat teksnya.

Kegagalan di sini ditangani dengan cara yang berbeda dari kegagalan model: baris yang rusak
DILEWATI dan dicatat sebagai peringatan, bukan menggagalkan seluruh analisis. Pengguna yang
mengunggah 200 ulasan tidak boleh kehilangan semuanya karena tiga baris bermasalah (bagian 35).
"""

from __future__ import annotations

import html
import re
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


def _normalize_text(raw_text: str | None) -> str:
    """Rapikan teks mentah sebelum apa pun menyentuhnya.

    Entitas HTML wajib dipulihkan di sini. Ekspor marketplace kerap membawa `&#34;` atau `&amp;`
    apa adanya, dan karena kutipan bukti ditampilkan VERBATIM, entitas yang lolos akan muncul
    sebagai sampah di layar - tepat pada elemen yang paling menentukan kepercayaan pengguna.
    Memulihkannya di hulu juga membuat model melihat teks yang sama dengan yang dibaca manusia.
    """
    text = html.unescape(raw_text or "")
    # Surrogate lepas dibuang. Ini bukan kehati-hatian teoretis: emoji yang melewati konversi
    # encoding yang salah - hal biasa pada ekspor marketplace dan pada berkas yang pernah
    # dibuka di spreadsheet Windows - meninggalkan setengah pasangan surrogate. Tokenizer
    # HuggingFace ditulis dalam Rust dan menolak str semacam itu dengan TypeError, yang naik
    # sampai ke pengguna sebagai INTERNAL_ERROR tanpa satu pun petunjuk. Satu ulasan rusak
    # menggagalkan seluruh batch, jadi karakternya dibuang di sini alih-alih menjatuhkan
    # analisis atas 999 ulasan lain yang sehat.
    text = text.encode("utf-8", "ignore").decode("utf-8")
    # Ekspor CSV kerap menyisakan baris baru dan spasi ganda di tengah kalimat.
    return re.sub(r"\s+", " ", text).strip()


def _normalize_product(raw_name: str | None) -> str | None:
    """Rapikan nama produk dengan perlakuan yang sama seperti teks ulasan.

    Entitas HTML bukan kasus teoretis di sini - ekspor Shopee pada data contoh membawa nama
    seperti `WAKAI SM01618 TEIKYU Navy Men &#40;WAK0002406.C4913&#41;`. Tanpa dipulihkan,
    nama itu muncul apa adanya sebagai judul baris di tabel per produk, dan yang lebih buruk:
    dua ekspor dari toko yang sama dengan tingkat pelolosan entitas berbeda akan terhitung
    sebagai dua produk berbeda, memecah angkanya tanpa sebab yang terlihat.
    """
    name = html.unescape(raw_name or "").encode("utf-8", "ignore").decode("utf-8")
    return re.sub(r"\s+", " ", name).strip() or None


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
        text = _normalize_text(item.text)

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
                product_id=(item.product_id or None),
                product_name=_normalize_product(item.product_name),
            )
        )

    if result.skipped:
        result.warnings.append("baris_dilewati")
    if len(result.reviews) < MIN_REVIEWS_FOR_CONFIDENCE:
        result.warnings.append("data_kecil")
    if result.pii_redacted_count:
        result.warnings.append("pii_diredaksi")

    return result
