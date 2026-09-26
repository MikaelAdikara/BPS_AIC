"""Verifier kutipan dan gerbang fakta: kode murni, tanpa model dan tanpa basis data.

Tiga pemeriksaan berbeda tinggal di sini:

- **Kutipan.** Kutipan diterima hanya bila merupakan substring teks sumber setelah normalisasi
  aman. Tidak ada pencocokan "mirip": toleransi 90% akan menerima kutipan yang ditambah "tidak" di
  depannya, dan itu membalik makna bukti.
- **Kuantitas di draf.** Setiap angka bersatuan di teks yang akan dilihat pembeli harus punya
  pasangan di sumber (fakta merchant atau listing yang tidak disengketakan): nilai sama setelah
  konversi satuan, dan lokasi/sumbu/varian tidak bertentangan. Angka yang ditulis pembeli di ulasan
  bukan sumber.
- **Klaim berisiko.** Daftar tetap klaim non-angka (tahan air, kulit asli, garansi, kompatibilitas,
  ...) wajib bersumber dengan polaritas yang sama. Klaim di luar daftar tidak diverifikasi.
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
# Dimensi dan faktor ke satuan dasar. W, V, A, mAh, dan Wh adalah dimensi berbeda; bulan/tahun
# dikonversi di antara keduanya saja, jam/hari/minggu di antara ketiganya saja.
UNIT_DIMENSION: dict[str, tuple[str, float]] = {
    "mm": ("length", 0.1), "cm": ("length", 1.0), "m": ("length", 100.0), "inch": ("length", 2.54),
    "mg": ("mass", 0.001), "g": ("mass", 1.0), "kg": ("mass", 1000.0),
    "ml": ("volume", 1.0), "l": ("volume", 1000.0),
    "mah": ("charge", 1.0), "wh": ("energy", 1.0), "w": ("power", 1.0), "v": ("voltage", 1.0),
    "a": ("current", 1.0), "mb": ("storage", 1 / 1024), "gb": ("storage", 1.0), "tb": ("storage", 1024.0),
    "hour": ("duration", 1.0), "day": ("duration", 24.0), "week": ("duration", 168.0),
    "month": ("calendar", 1.0), "year": ("calendar", 12.0),
}
_UNIT_RE = "|".join(sorted((re.escape(u) for u in UNIT_ALIASES), key=len, reverse=True))
_NUM = r"\d+(?:[.,]\d+)*"
_CHAIN = rf"{_NUM}(?:\s*[x×*]\s*{_NUM})*"
# "32 x 24 cm", "1,2 kg", "20.000 mAh"
_TRAILING = re.compile(rf"(?<![\w.,])(?P<nums>{_CHAIN})\s*(?P<unit>{_UNIT_RE})(?![a-z0-9])")
# "Panjang (cm): 32" - format tabel spesifikasi
_TABLE = re.compile(rf"\(\s*(?P<unit>{_UNIT_RE})\s*\)\s*:?\s*(?P<nums>{_CHAIN})")
_SPLIT_CHAIN = re.compile(r"\s*[x×*]\s*")

# Batas klausa untuk mengikat angka ke kata penanda terdekat: "bagian luar 32 cm, bagian dalam 30 cm".
_CLAUSE_BREAK = re.compile(r"[;\n]|[.,](?!\d)|\s(?:dan|and|serta)\s")
_LOCATION_WORDS = [
    ("inner", re.compile(r"\b(?:dalam|inner|inside|interior)\b")),
    ("outer", re.compile(r"\b(?:luar|outer|outside|exterior)\b")),
    ("folded", re.compile(r"\b(?:lipat|dilipat|folded)\b")),
    ("open", re.compile(r"\b(?:dibuka|terbuka|unfolded)\b")),
]
_AXIS_WORDS = [
    ("chest", r"lingkar dada|chest|bust"), ("waist", r"lingkar pinggang|pinggang|waist"),
    ("sleeve", r"panjang lengan|lengan|sleeve"), ("shoulder", r"lebar bahu|bahu|shoulder"),
    ("length", r"panjang|length|long"), ("width", r"lebar|width|wide"), ("height", r"tinggi|height|tall"),
    ("thickness", r"tebal|ketebalan|thickness|thick"), ("diameter", r"diameter"),
]
_AXIS_RE = re.compile("|".join(rf"(?P<{name}>\b(?:{pattern})\b)" for name, pattern in _AXIS_WORDS))
_VARIANT_RE = re.compile(r"(?:\b(?:ukuran|size|varian)\s+|^\s*)(xxxl|xxl|xl|xs|s|m|l)\b")


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str
    text: str
    start: int
    # Kualifier dari klausa yang sama: lokasi (inner/outer/folded/open), sumbu (length, width, ...),
    # dan varian ukuran (S/M/L...). Kosong berarti tidak disebut, dan kosong tidak pernah konflik.
    location: str = ""
    axis: str = ""
    variant: str = ""


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


def _qualifiers(norm: str, position: int) -> tuple[str, str, str]:
    """Lokasi, sumbu, dan varian dari klausa tempat kuantitas berada (penanda terdekat sebelumnya)."""
    begin = 0
    for brk in _CLAUSE_BREAK.finditer(norm, 0, position):
        begin = brk.end()
    clause = norm[begin:position]
    location = next((name for name, pattern in _LOCATION_WORDS if pattern.search(clause)), "")
    axes = [m.lastgroup for m in _AXIS_RE.finditer(clause)]
    variant = _VARIANT_RE.search(clause)
    return location, (axes[-1] if axes else ""), (variant.group(1) if variant else "")


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
            parts = _SPLIT_CHAIN.split(match.group("nums"))
            location, axis, variant = _qualifiers(norm, match.start())
            if len(parts) > 1:
                axis = ""  # "panjang 32 x 24 cm": sumbu tiap angka dalam rangkaian tidak diketahui
            for part in parts:
                value = parse_number(part)
                if value is not None:
                    found.append(Quantity(value, unit, f"{_fmt(value)} {unit}", match.start(),
                                          location, axis, variant))
    found.sort(key=lambda q: q.start)
    return found


def _same(a: Quantity, b: Quantity) -> bool:
    """Nilai sama setelah konversi ke satuan dasar dimensinya, dan kualifier tidak bertentangan."""
    da, db = UNIT_DIMENSION.get(a.unit), UNIT_DIMENSION.get(b.unit)
    if not da or not db or da[0] != db[0]:
        return False
    va, vb = a.value * da[1], b.value * db[1]
    if abs(va - vb) / max(abs(va), abs(vb), 1e-9) > 0.01:
        return False
    return all(not x or not y or x == y for x, y in ((a.location, b.location), (a.axis, b.axis),
                                                     (a.variant, b.variant)))


def unsupported_quantities(draft: str, sources: list[str]) -> list[Quantity]:
    """Kuantitas di draf tanpa pasangan di sumber mana pun. 14 inch mendukung 35,56 cm, tidak
    pernah 14 cm; "bagian luar 32 cm" tidak mendukung "bagian dalam 32 cm"."""
    available = [q for source in sources for q in extract_quantities(source)]
    return [q for q in extract_quantities(draft) if not any(_same(q, s) for s in available)]


_PLACEHOLDER = re.compile(r"\[\[[^\]]*\]\]")


def placeholders(text: str) -> list[str]:
    return _PLACEHOLDER.findall(text or "")


# --- klaim non-angka yang wajib bersumber ---------------------------------------------------------

# Daftar tetap. Klaim di luar daftar ini tidak diverifikasi, dan UI menyebutnya.
RISKY_CLAIMS: list[tuple[str, re.Pattern]] = [
    ("waterproof", re.compile(r"waterproof|kedap air|anti air\b")),
    ("water_resistant", re.compile(r"water ?resistant|tahan air|tahan cipratan|anti cipratan|splash ?proof|\bipx\d")),
    ("genuine_leather", re.compile(r"kulit asli|genuine leather|real leather|full grain")),
    ("warranty", re.compile(r"\bgaransi\b|\bwarranty\b|\bguarantee")),
    ("authenticity", re.compile(r"\b(?:original|ori|resmi|authentic|produk asli|barang asli)\b")),
    ("certification", re.compile(r"\b(?:bpom|halal|sni|iso(?: ?\d+)?|fda)\b")),
    ("safety", re.compile(r"food grade|bpa free|bebas bpa|non ?toxic|aman untuk (?:anak|bayi|makanan|kulit|balita)")),
    ("material", re.compile(r"\b(?:kanvas|canvas|katun|cotton|polyester|nylon|nilon|kulit|leather|stainless|kayu|wood|"
                            r"silikon|silicone|linen|denim|aluminium|aluminum|akrilik|acrylic)\b")),
]
_DEVICE = re.compile(r"\b(iphone|ipad|samsung galaxy|galaxy|samsung|redmi note|redmi|xiaomi|poco|oppo|vivo|realme|"
                     r"infinix|pixel|macbook|asus|lenovo)\s*([a-z]?\d{1,4}[a-z]?(?:\s?(?:pro max|pro|max|plus|mini|ultra|lite))?)")
_NEGATORS = {"tidak", "tak", "bukan", "gak", "ga", "nggak", "non", "not", "no", "belum", "tanpa", "without"}


@dataclass(frozen=True)
class Claim:
    kind: str
    positive: bool
    text: str
    identity: str = ""


def _negated(norm: str, start: int) -> bool:
    before = re.findall(r"[a-z]+", norm[max(0, start - 30):start])[-3:]
    return any(w in _NEGATORS for w in before)


def extract_claims(text: str) -> list[Claim]:
    norm = normalise(text)
    out = [Claim(kind, not _negated(norm, m.start()), m.group(0))
           for kind, pattern in RISKY_CLAIMS for m in pattern.finditer(norm)]
    out += [Claim("compatibility", not _negated(norm, m.start()), m.group(0),
                  f"{m.group(1)} {m.group(2).replace(' ', '')}") for m in _DEVICE.finditer(norm)]
    return out


def _covers(source: Claim, claim: Claim) -> bool:
    if source.positive != claim.positive:
        return False
    if claim.kind == "compatibility":
        return source.kind == "compatibility" and source.identity == claim.identity
    if claim.kind == "material":
        return source.kind == "material" and source.text == claim.text
    if source.kind == claim.kind:
        return True
    # Waterproof yang bersumber menutupi klaim tahan air yang lebih lemah, tidak sebaliknya.
    return claim.kind == "water_resistant" and claim.positive and source.kind == "waterproof"


def unsupported_claims(draft: str, sources: list[str]) -> list[Claim]:
    """Klaim berisiko di draf tanpa sumber berpolaritas sama. "tidak tahan air" tidak pernah
    mendukung "tahan air"; iPhone 12 tidak mendukung iPhone 15."""
    available = [c for source in sources for c in extract_claims(source)]
    return [c for c in extract_claims(draft) if not any(_covers(s, c) for s in available)]
