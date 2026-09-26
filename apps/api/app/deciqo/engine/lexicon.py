"""Kosakata bersama engine: keluhan, pujian, negasi, dan kelompok atribut produk.

Dipakai triage (sinyal keluhan), analyser aturan, juri relevansi, dan pemeriksaan listing, supaya
"ulasan ini mengeluh soal ukuran" berarti hal yang sama di semua jalur.

Slang dasar diambil dari leksikon klasifier yang sudah ada (`ml/text/lexicon.py`) lalu ditambah
bentuk yang sering muncul di keluhan produk ("kegedean", "jaitan", "ngga"). Istilah topik dan
istilah polaritas tetap dipisah: "pas" adalah pujian, bukan penanda atribut ukuran.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .verify import normalise

_ML_TEXT = Path(__file__).resolve().parents[5] / "ml" / "text"


def _base_slang() -> dict[str, str]:
    try:
        if str(_ML_TEXT) not in sys.path:
            sys.path.insert(0, str(_ML_TEXT))
        from lexicon import SLANG_MAP  # noqa: PLC0415

        return dict(SLANG_MAP)
    except Exception:  # noqa: BLE001 - engine tetap jalan tanpa folder ml/
        return {}


# Negasi dipetakan ke "tidak" supaya pemeriksaan jendela negasi seragam.
NEGATIONS = {"tidak", "tak", "gak", "ga", "gk", "nggak", "ngga", "engga", "enggak", "kurang",
             "bukan", "belum", "tdk", "kagak", "no", "not", "never"}
SLANG = {k: v for k, v in _base_slang().items() if " " not in v}
SLANG.update({"gede": "besar", "gedean": "gedean", "jaitan": "jahitan", "baterai": "baterai",
              "batre": "baterai", "batrai": "baterai", "hp": "hp", "dtg": "datang", "dateng": "datang",
              "dapet": "dapat", "sampe": "sampai", "nyampe": "sampai", "cepet": "cepat"})
NEGATION_WINDOW = 3

COMPLAINT_TERMS = {
    # ukuran
    "kekecilan", "kebesaran", "kecilan", "kegedean", "gedean", "sempit", "longgar", "kependekan",
    "kepanjangan", "dipaksa", "kesempitan",
    # rusak / fungsi
    "rusak", "mati", "error", "bocor", "rembes", "lepas", "copot", "sobek", "robek", "cacat",
    "pecah", "patah", "retak", "lecet", "penyok", "macet", "luntur", "pudar", "berkarat", "bolong",
    # umum
    "jelek", "buruk", "kecewa", "mengecewakan", "tipis", "beda", "berbeda", "salah", "kotor",
    "bau", "susah", "ribet", "hilang", "zonk", "parah", "nyesel", "menyesal", "murahan", "rapuh",
    # pengiriman / layanan
    "lama", "telat", "terlambat", "lambat", "molor", "dicuekin", "cuek", "slow",
    # elektronik
    "habis", "boros", "panas", "lemot", "lelet", "putus", "drop", "ngelag", "lag", "overheat",
    # Inggris
    "broken", "damaged", "defective", "wrong", "missing", "bad", "poor", "late", "small", "tight",
}
PRAISE_TERMS = {
    "sesuai", "pas", "muat", "masuk", "bagus", "rapi", "cepat", "tebal", "awet", "nyala", "kuat",
    "rapat", "mantap", "nyaman", "kokoh", "enak", "suka", "puas", "mudah", "gampang", "ramah",
    "aman", "lengkap", "bisa", "cocok", "oke", "adem", "membalas", "dibalas", "balas", "responsif",
    "berfungsi", "jalan", "original", "asli", "good", "great", "fits", "fit", "perfect",
}

# Kosakata atribut per kelompok. Dipakai bersama juri relevansi dan pemeriksaan listing.
ATTRIBUTE_GROUPS: dict[str, set[str]] = {
    "size": {"ukuran", "size", "sizing", "muat", "masuk", "sempit", "longgar", "kekecilan", "kebesaran",
             "kecilan", "kegedean", "gedean", "kependekan", "kepanjangan", "panjang", "pendek",
             "lebar", "tinggi", "besar", "kecil", "dimensi", "lingkar", "dada", "pinggang", "bahu",
             "lengan", "lipat", "dilipat", "lipatan", "kompartemen", "kantong", "inch", "inci",
             "cm", "fit", "dimension", "dimensions", "measurement", "measurements", "folded",
             "inner", "compartment", "chart", "tabel", "kesempitan", "dipaksa", "length", "width",
             "height", "depth", "large", "tight", "loose", "small"},
    "color": {"warna", "color", "colour", "pudar"},
    "material": {"bahan", "kain", "material", "tebal", "tipis", "ketebalan", "kanvas", "katun",
                 "kulit", "fabric", "thickness", "gramasi", "leather"},
    "stitching": {"jahitan", "jahit", "obras", "stitching", "seam", "seams"},
    "water": {"air", "basah", "bocor", "rembes", "hujan", "berenang", "renang", "waterproof",
              "water", "resistant"},
    "battery": {"baterai", "battery", "mati", "nyala", "error", "charge", "cas", "daya", "mah",
                "power", "charging"},
    "compatibility": {"kompatibel", "compatible", "compatibility", "iphone", "samsung", "xiaomi",
                      "oppo", "vivo", "device", "perangkat"},
    "contents": {"isi", "kelengkapan", "aksesoris", "contents", "bonus", "included"},
    "delivery": {"kirim", "dikirim", "pengiriman", "kurir", "ekspedisi", "sampai", "estimasi",
                 "delivery", "shipping", "paket", "resi", "courier"},
    "packaging": {"kemasan", "packing", "bungkus", "dus", "kardus", "box", "bubble", "packaging"},
    "service": {"penjual", "seller", "chat", "respon", "balas", "dibalas", "membalas", "admin",
                "cs", "pelayanan", "dicuekin", "service", "responsiveness", "respons", "responsif"},
    "quality": {"kualitas", "rusak", "cacat", "kokoh", "quality", "defect", "defects",
                "durability", "awet", "rapuh"},
    "appearance": {"foto", "gambar", "photo", "photos", "tampilan", "appearance", "picture"},
}
OPERATIONAL_GROUPS = {"delivery", "packaging", "service", "wrong_item"}

_WRONG_ITEM = [
    re.compile(r"\b(?:pesan|order|beli|pilih)\w*\b.{0,40}?\b(?:yang datang|datang|dikasih|dikirim|dapat|yang sampai|sampai)\b(?:\s+(?:malah|justru|tapi|jadi))?", re.I),
    re.compile(r"\bsalah kirim\b|\bkirim(?:an)?(?:nya)? salah\b", re.I),
    re.compile(r"\b(?:yang )?(?:datang|dikirim|sampai)\b.{0,20}?\b(?:warna|ukuran|varian|size|model|tipe)\s+(?:lain|beda|berbeda)\b", re.I),
    re.compile(r"\bsalah (?:warna|ukuran|varian|size|model|tipe)\b", re.I),
    re.compile(r"\bwrong (?:item|size|colou?r|variant)\b", re.I),
]
_CLAUSE_SPLIT = re.compile(
    r"(?<!\d)[.,](?!\d)|(?<=\d)[.,](?!\d)|[;!?\n]+|\s(?=(?:tapi|tetapi|namun|sayangnya|padahal|cuma|hanya saja)\b)",
    re.I)
_WORD = re.compile(r"[a-z0-9]+")


def stem(word: str) -> str:
    """`-nya` dilepas ("baterainya" → "baterai"); slang dipetakan ke bentuk bakunya."""
    word = word.lower()
    if word.endswith("nya") and len(word) > 5:
        word = word[:-3]
    return SLANG.get(word, word)


def tokens(text: str) -> list[str]:
    return [stem(w) for w in _WORD.findall(normalise(text))]


@dataclass(frozen=True)
class Clause:
    text: str  # potongan ASLI dari teks sumber, aman dipakai sebagai kutipan verbatim
    start: int
    tokens: tuple[str, ...]


def clauses(text: str) -> list[Clause]:
    out: list[Clause] = []
    start = 0
    for match in list(_CLAUSE_SPLIT.finditer(text or "")) + [None]:
        end = match.start() if match else len(text or "")
        piece = (text or "")[start:end]
        stripped = piece.strip()
        if stripped:
            offset = start + piece.index(stripped)
            out.append(Clause(stripped, offset, tuple(tokens(stripped))))
        if match:
            start = match.end()
    return out


def polarity(toks: tuple[str, ...] | list[str]) -> str:
    """`complaint`, `praise`, atau `neutral` untuk satu klausa.

    Pujian yang dinegasikan ("tidak muat", "kurang pas") adalah keluhan; keluhan yang dinegasikan
    ("tidak kekecilan", "gak bocor") bukan keluhan."""
    complaint = praise = False
    for i, tok in enumerate(toks):
        negated = any(t in NEGATIONS for t in toks[max(0, i - NEGATION_WINDOW):i])
        if tok in COMPLAINT_TERMS:
            if negated:
                praise = True
            else:
                complaint = True
        elif tok in PRAISE_TERMS:
            if negated:
                complaint = True
            else:
                praise = True
    if complaint:
        return "complaint"
    return "praise" if praise else "neutral"


def mentions(toks, groups: set[str], extra: set[str] | None = None) -> bool:
    vocab = set().union(*(ATTRIBUTE_GROUPS.get(g, set()) for g in groups)) if groups else set()
    if extra:
        vocab |= extra
    return any(t in vocab for t in toks)


def groups_in(toks) -> set[str]:
    return {g for g, vocab in ATTRIBUTE_GROUPS.items() if any(t in vocab for t in toks)}


_WRONG_LABEL = re.compile(r"\b(?:wrong|salah)\b.*\b(?:variant|varian|item|barang|kirim|dikirim|sent|size|ukuran|warna|colou?r)\b"
                          r"|\b(?:variant|varian)\b.*\b(?:wrong|salah)\b", re.I)
_STOP = {"the", "of", "a", "an", "and", "product", "produk", "info", "information", "detail",
         "details", "yang", "dan", "di", "untuk", "barang", "item", "issue", "masalah"}


def attribute_groups(attribute: str, attribute_local: str = "") -> set[str]:
    label = f"{attribute} {attribute_local}"
    if _WRONG_LABEL.search(label):
        return {"wrong_item"}
    return groups_in(tokens(label))


def attribute_terms(attribute: str, attribute_local: str = "") -> set[str]:
    """Kata isi label atribut, cadangan bila label tidak masuk kelompok mana pun."""
    return {t for t in tokens(f"{attribute} {attribute_local}") if t not in _STOP and len(t) > 2}


def is_wrong_item(text: str) -> bool:
    return any(p.search(text or "") for p in _WRONG_ITEM)


def wrong_item_clause(clause: Clause) -> bool:
    return is_wrong_item(clause.text)


def complaint_signal(text: str) -> bool:
    """Ada klausa keluhan, atau laporan salah kirim. Bintang tidak ikut dinilai."""
    return is_wrong_item(text) or any(polarity(c.tokens) == "complaint" for c in clauses(text))
