"""Normalisasi teks dan segmentasi klausa (blueprint bagian 18.3).

Segmentasi klausa diperlukan karena 54% ulasan PRDECT-ID menyebut >=2 aspek, dan aspek-aspek
itu sering berlawanan sentimen ("barangnya bagus tapi pengirimannya lama"). Melabeli sentimen
di tingkat ulasan akan salah untuk salah satu aspek. Klausa juga mengisi field `source_sentence`
yang diwajibkan schema Text Prediction (bagian 25.4) untuk traceability.
"""

from __future__ import annotations

import re

from lexicon import (
    CONTRAST_MARKERS,
    NEGATION_PATTERN,
    NEGATION_WINDOW,
    NEGATIVE_PATTERN,
    POSITIVE_PATTERN,
    SLANG_MAP,
)

_WS = re.compile(r"\s+")
_REPEAT_CHAR = re.compile(r"(.)\1{2,}")  # "baguuuus" -> "bagus"
_URL = re.compile(r"https?://\S+|www\.\S+")
_PUNCT_SPLIT = re.compile(r"[.!?;\n\r]+|\.{2,}")
_CONTRAST_SPLIT = re.compile(
    r"(?<!\w)(?:" + "|".join(re.escape(m) for m in CONTRAST_MARKERS) + r")(?!\w)",
    re.IGNORECASE,
)
_TOKEN = re.compile(r"\w+", re.UNICODE)


def normalize(text: str) -> str:
    """Lowercase, buang URL, rapikan huruf berulang, dan bakukan slang.

    Normalisasi slang berjalan per-token supaya penanda negasi ("ga", "gak", "nggak")
    seragam menjadi "tidak" sebelum deteksi negasi dijalankan.
    """
    if not isinstance(text, str):
        return ""
    text = _URL.sub(" ", text.lower())
    text = _REPEAT_CHAR.sub(r"\1", text)
    tokens = text.split()
    tokens = [SLANG_MAP.get(tok.strip(".,!?"), tok) for tok in tokens]
    return _WS.sub(" ", " ".join(tokens)).strip()


def split_clauses(text: str, min_chars: int = 3) -> list[str]:
    """Pecah teks menjadi klausa pada tanda baca, koma, dan konjungsi kontras."""
    clauses: list[str] = []
    for chunk in _PUNCT_SPLIT.split(text):
        for part in chunk.split(","):
            for piece in _CONTRAST_SPLIT.split(part):
                piece = piece.strip()
                if len(piece) >= min_chars:
                    clauses.append(piece)
    return clauses or ([text.strip()] if len(text.strip()) >= min_chars else [])


def polarity_score(clause: str) -> tuple[int, int]:
    """Hitung (jumlah sinyal positif, jumlah sinyal negatif) dengan penanganan negasi.

    Kata polaritas yang berada dalam NEGATION_WINDOW token sesudah penanda negasi
    dibalik arahnya - "tidak bagus" dihitung sebagai sinyal negatif, bukan positif.
    """
    tokens = _TOKEN.findall(clause)
    negated_until = -1
    pos = neg = 0

    for idx, token in enumerate(tokens):
        if NEGATION_PATTERN.fullmatch(token):
            negated_until = idx + NEGATION_WINDOW
            continue

        is_pos = bool(POSITIVE_PATTERN.fullmatch(token))
        is_neg = bool(NEGATIVE_PATTERN.fullmatch(token))
        if not (is_pos or is_neg):
            continue

        if idx <= negated_until:
            is_pos, is_neg = is_neg, is_pos  # negasi membalik arah
        pos += int(is_pos)
        neg += int(is_neg)

    return pos, neg
