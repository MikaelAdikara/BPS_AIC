"""Verifier kutipan dan gerbang fakta: kode murni, tanpa model dan tanpa basis data.

Dua pemeriksaan berbeda tinggal di sini:

- **Kutipan.** Kutipan diterima hanya bila merupakan substring teks sumber setelah normalisasi
  aman. Tidak ada pencocokan "mirip": toleransi 90% akan menerima kutipan yang ditambah "tidak" di
  depannya, dan itu membalik makna bukti.
- **Kuantitas di draf.** Setiap angka bersatuan di teks yang akan dilihat pembeli harus punya
  pasangan di sumber (fakta merchant atau listing yang tidak disengketakan). Angka yang ditulis
  pembeli di ulasan bukan sumber.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

MIN_QUOTE_CHARS = 6

_QUOTES = str.maketrans({
    "“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
    "‘": "'", "’": "'", "‚": "'", "`": "'", "´": "'",
})
# Tanda baca lunak yang boleh diabaikan saat mencocokkan kutipan. Titik dan koma di antara dua
# angka TIDAK dibuang: "1,5 cm" dan "15 cm" adalah nilai yang berbeda.
_SOFT_PUNCT = re.compile(r"(?<!\d)[.,](?!\d)|(?<=\d)[.,](?!\d)|(?<!\d)[.,](?=\d)|[;:!?()\[\]\"'…\-–—/]")
_SPACES = re.compile(r"\s+")


def normalise(text: str) -> str:
    """NFKC, huruf kecil, tanda kutip disamakan, spasi dirapikan. Tanda baca dipertahankan."""
    text = unicodedata.normalize("NFKC", text or "").translate(_QUOTES).lower()
    return _SPACES.sub(" ", text).strip()


def _loose(text: str) -> str:
    """Bentuk pencocokan kutipan: `normalise` lalu tanda baca lunak dibuang."""
    return _SPACES.sub(" ", _SOFT_PUNCT.sub(" ", normalise(text))).strip()


def check_quote(quote: str, source: str) -> tuple[bool, str]:
    """(diterima, alasan). Alasan kosong bila diterima."""
    q = _loose(quote)
    if len(q) < MIN_QUOTE_CHARS:
        return False, "quote_too_short"
    s = _loose(source)
    # Batas kata di kedua ujung: "sempit" tidak boleh cocok di tengah "kesempitan".
    if re.search(rf"(?<!\w){re.escape(q)}(?!\w)", s):
        return True, ""
    return False, "quote_not_verbatim"


def quote_in(quote: str, source: str) -> bool:
    return check_quote(quote, source)[0]


# --- kuantitas -------------------------------------------------------------------------------

# Satuan yang dikenali, ditulis dalam bentuk kanonisnya. Bentuk panjang didahulukan saat
# dikompilasi supaya "mah" tidak terbaca sebagai "m".
UNIT_ALIASES: dict[str, str] = {
    "mm": "mm", "cm": "cm", "m": "m", "meter": "m", "inch": "inch", "inci": "inch", "in": "inch",
    "kg": "kg", "g": "g", "gr": "g", "gram": "g", "mg": "mg",
    "ml": "ml", "l": "l", "liter": "l", "litre": "l", "ltr": "l",
    "mah": "mah", "wh": "wh", "w": "w", "watt": "w", "v": "v", "volt": "v", "a": "a", "ampere": "a",
    "gb": "gb", "tb": "tb", "mb": "mb",
    "jam": "hour", "hari": "day", "minggu": "week", "bulan": "month", "tahun": "year",
}
_UNIT_RE = "|".join(sorted((re.escape(u) for u in UNIT_ALIASES), key=len, reverse=True))
_NUM = r"\d+(?:[.,]\d+)*"
_CHAIN = rf"{_NUM}(?:\s*[x×*]\s*{_NUM})*"
# "32 x 24 cm", "1,2 kg", "20.000 mAh"
_TRAILING = re.compile(rf"(?<![\w.,])(?P<nums>{_CHAIN})\s*(?P<unit>{_UNIT_RE})(?![a-z0-9])")
# "Panjang (cm): 32" - format tabel spesifikasi
_TABLE = re.compile(rf"\(\s*(?P<unit>{_UNIT_RE})\s*\)\s*:?\s*(?P<nums>{_CHAIN})")
_SPLIT_CHAIN = re.compile(r"\s*[x×*]\s*")


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str
    text: str
    start: int


def parse_number(raw: str) -> float | None:
    """Angka gaya Indonesia: koma desimal, titik ribuan ("20.000"). Titik yang tidak membentuk
    kelompok ribuan dibaca sebagai desimal ("1.5")."""
    raw = raw.strip()
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", raw):
        raw = raw.replace(".", "")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+,\d+", raw):
        raw = raw.replace(".", "").replace(",", ".")
    else:
        raw = raw.replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _fmt(value: float) -> str:
    return f"{value:g}".replace(".", ",")


def extract_quantities(text: str) -> list[Quantity]:
    """Semua angka bersatuan dalam teks. Dimensi "32 x 24 cm" menghasilkan satu kuantitas per angka."""
    norm = normalise(text)
    found: list[Quantity] = []
    taken: list[tuple[int, int]] = []
    for pattern in (_TABLE, _TRAILING):
        for match in pattern.finditer(norm):
            if any(match.start() < end and start < match.end() for start, end in taken):
                continue
            taken.append((match.start(), match.end()))
            unit = UNIT_ALIASES[match.group("unit")]
            for part in _SPLIT_CHAIN.split(match.group("nums")):
                value = parse_number(part)
                if value is not None:
                    found.append(Quantity(value, unit, f"{_fmt(value)} {unit}", match.start()))
    found.sort(key=lambda q: q.start)
    return found


def _same(a: Quantity, b: Quantity) -> bool:
    if a.unit != b.unit:
        return False
    scale = max(abs(a.value), abs(b.value), 1e-9)
    return abs(a.value - b.value) / scale <= 0.01


def unsupported_quantities(draft: str, sources: list[str]) -> list[Quantity]:
    """Kuantitas di draf yang tidak punya pasangan (nilai dan satuan yang sama) di sumber mana pun."""
    available = [q for source in sources for q in extract_quantities(source)]
    return [q for q in extract_quantities(draft) if not any(_same(q, s) for s in available)]


_PLACEHOLDER = re.compile(r"\[\[[^\]]*\]\]")


def placeholders(text: str) -> list[str]:
    return _PLACEHOLDER.findall(text or "")
