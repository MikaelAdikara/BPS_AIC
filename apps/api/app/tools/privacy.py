"""redact_personal_data() — GOV-01, tool contract bagian 27.3.

Redaksi PII WAJIB berjalan sebelum data mencapai model manapun (bagian 27.3, 36.1). Ini bukan
langkah kebersihan opsional: ulasan dan chat pelanggan memuat nomor telepon dan alamat, dan
pemiliknya secara hukum bertanggung jawab atas data itu (UU PDP, dossier bagian 22.2).

Prinsip: **mengganti, bukan menghapus.** Teks yang diredaksi tetap terbaca sebagai kalimat
sehingga tetap berguna sebagai kutipan bukti, dan penggantinya menunjukkan jenis data yang
disembunyikan — pengguna dapat memverifikasi bahwa sistem benar-benar meredaksi.

Batas yang harus disebut jujur: regex tidak akan pernah menangkap 100% PII. Ia menangkap pola
terstruktur (nomor, email, alamat) dengan andal, tetapi tidak menangkap nama orang yang ditulis
biasa. Karena itu redaksi ini dipasangkan dengan kebijakan session-only (ADR-010), bukan
diandalkan sendirian.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Urutan penting: pola yang lebih spesifik didahulukan agar tidak dipotong pola yang lebih umum.
# Contoh: email harus diproses sebelum angka, kalau tidak "user123@mail.com" tercabik.
PII_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b", re.I), "[email]"),
    (
        "telepon",
        # Nomor Indonesia: +62/62/0 diikuti 8-13 digit, boleh disela spasi/strip.
        re.compile(r"(?:\+?62|0)[\s-]?8[\d\s-]{7,13}\d"),
        "[nomor telepon]",
    ),
    (
        "nomor_panjang",
        # Rekening/kartu/NIK - deretan 10+ digit yang berdiri sendiri.
        re.compile(r"\b\d{10,}\b"),
        "[nomor]",
    ),
    (
        "alamat",
        re.compile(
            r"\b(?:jl\.?|jalan|gg\.?|gang|perum(?:ahan)?|blok)\s+[\w.\s/-]{3,40}",
            re.I,
        ),
        "[alamat]",
    ),
    (
        "media_sosial",
        # Username diawali @ - umum pada chat pelanggan.
        re.compile(r"(?<![\w/])@[A-Za-z][\w.]{2,}"),
        "[akun]",
    ),
    (
        "url",
        re.compile(r"https?://\S+|www\.\S+", re.I),
        "[tautan]",
    ),
]


@dataclass(frozen=True)
class RedactionResult:
    text: str
    redacted: bool
    counts: dict[str, int]


def redact_personal_data(text: str) -> RedactionResult:
    """Ganti PII terstruktur dengan penanda jenisnya.

    Returns:
        RedactionResult dengan teks hasil redaksi, penanda apakah ada yang diganti, dan
        jumlah per jenis. Jumlah itu dipakai MON-01 untuk melaporkan berapa banyak PII
        ditemukan tanpa pernah mencatat isinya (bagian 37.1: log tidak memuat PII).
    """
    if not isinstance(text, str) or not text:
        return RedactionResult(text="", redacted=False, counts={})

    counts: dict[str, int] = {}
    result = text
    for name, pattern, replacement in PII_PATTERNS:
        result, n = pattern.subn(replacement, result)
        if n:
            counts[name] = counts.get(name, 0) + n

    return RedactionResult(text=result, redacted=bool(counts), counts=counts)


def contains_pii(text: str) -> bool:
    """Pemeriksaan cepat tanpa mengubah teks — dipakai test coverage (bagian 35 FMEA)."""
    return any(pattern.search(text or "") for _, pattern, _ in PII_PATTERNS)
