"""Pemeriksaan listing per temuan, dengan status eksplisit.

Gagal mengekstrak kutipan listing TIDAK sama dengan listing tidak menyebutnya. UI mengikuti
status di sini, bukan apakah string kutipannya kosong.
"""

from __future__ import annotations

from . import lexicon, relevance, verify

LISTING_LIMIT = 9000  # karakter listing yang dikirim ke model dan diperiksa

NOT_PROVIDED = "not_provided"
PENDING = "pending"
EVIDENCE_FOUND = "evidence_found"
NOT_FOUND = "not_found_in_checked_content"
VERIFICATION_FAILED = "verification_failed"
INCOMPLETE_SOURCE = "incomplete_source"
CONFLICTING = "conflicting"
# Temuan operasional/kualitas tidak diperbaiki lewat listing, jadi listing tidak diperiksa.
NOT_APPLICABLE = "not_applicable"
LISTING_FIXABLE = {"missing_fact", "unclear_fact", "conflicting_fact", "expectation_mismatch"}


def related_text(finding: dict, listing: str, limit: int = 3) -> list[str]:
    """Klausa listing (verbatim) yang menyebut kata atribut temuan."""
    groups, extra = relevance.finding_scope(finding)
    if groups == {"wrong_item"} or groups & lexicon.OPERATIONAL_GROUPS:
        return []
    return [c.text for c in lexicon.clauses(listing) if lexicon.mentions(c.tokens, groups, extra)][:limit]


def check(finding: dict, listing: str, provided: bool, images: tuple[int, int] = (0, 0)) -> dict:
    """Status pemeriksaan listing untuk satu temuan.

    Model hanya membaca `LISTING_LIMIT` karakter pertama (keputusan sistem, tercatat di cakupan),
    tetapi pemeriksaan ini kode dan membaca listing utuh. Teks terkait yang hanya ada di luar
    jendela model berarti temuannya disusun tanpa melihat bagian itu: `incomplete_source`.

    `images`: (gambar produk yang teksnya sudah dibaca OCR dan ikut di `listing`, total gambar)."""
    listing = listing or ""
    total = len(listing)
    coverage = {"chars_checked": total, "chars_total": total, "model_chars": min(total, LISTING_LIMIT),
                "images_read": int(images[0]), "images_total": int(images[1])}
    if finding.get("finding_type") not in LISTING_FIXABLE:
        return {"status": NOT_APPLICABLE, "quote": "", "related": [], "coverage": coverage}
    if not provided:
        return {"status": NOT_PROVIDED, "quote": "", "related": [], "coverage": coverage}
    proposed = (finding.get("listing_evidence") or "").strip()
    related = related_text(finding, listing)
    in_window = related_text(finding, listing[:LISTING_LIMIT])
    if related and not in_window:
        return {"status": INCOMPLETE_SOURCE, "quote": "", "related": related, "coverage": coverage,
                "reason": "related_text_beyond_model_window"}
    if proposed:
        if verify.quote_in(proposed, listing):
            status = CONFLICTING if finding.get("finding_type") == "conflicting_fact" else EVIDENCE_FOUND
            return {"status": status, "quote": proposed, "related": related, "coverage": coverage}
        return {"status": VERIFICATION_FAILED, "quote": "", "related": related, "coverage": coverage,
                "reason": "listing_quote_not_verbatim"}
    if related:
        # Listing memuat kata terkait yang tidak dikutip: jangan klaim listing diam soal ini.
        return {"status": VERIFICATION_FAILED, "quote": "", "related": related, "coverage": coverage,
                "reason": "related_text_not_quoted"}
    return {"status": NOT_FOUND, "quote": "", "related": [], "coverage": coverage}
