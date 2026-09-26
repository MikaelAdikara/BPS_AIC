"""Analyser aturan: cadangan tanpa AI, dengan bentuk output yang sama dengan discovery.

Cakupannya sempit dan disebut apa adanya. Ukuran didiagnosis untuk tas (ukuran kompartemen
dalam), pakaian (tabel ukuran), dan furnitur lipat (ukuran lipat). Topik lain (pengiriman,
kemasan, layanan penjual, salah kirim, kualitas, beda dengan foto) hanya dikelompokkan per topik
tanpa diagnosis lebih jauh. Analyser ini tidak pernah menulis copy listing.

Hasilnya tetap melewati verifier, juri relevansi, metrik, dan gerbang yang sama dengan jalur AI.
"""

from __future__ import annotations

import re

from . import lexicon, relevance, verify

COVERAGE_NOTE = "AI is off: the rule engine covers size, delivery, packaging and quality complaints only."

_BAG = re.compile(r"\b(tas|ransel|backpack|bag|koper|pouch|sleeve|totebag|tote|soft ?case laptop|laptop ?(?:case|sleeve)|case laptop)\b", re.I)
_CLOTHING = re.compile(r"\b(kemeja|kaos|baju|celana|dress|gaun|jaket|hoodie|rok|shirt|blouse|kaus|sweater|cardigan|piyama|jersey)\b", re.I)
_FOLDING = re.compile(r"\b(lipat|folding|foldable)\b", re.I)

# (kunci topik, attribute EN, attribute ID, finding_type, fix_type, harapan pembeli, pertanyaan)
_SIZE_TOPICS = {
    "bag": ("inner compartment size", "ukuran kompartemen dalam",
            "Buyers need the inner compartment size to know whether their device fits.",
            "Berapa ukuran kompartemen dalam (panjang x lebar x tinggi, cm)?", "dalam"),
    "clothing": ("size chart measurements", "ukuran detail per size",
                 "Buyers need body measurements for each size to pick the right one.",
                 "Berapa lingkar dada dan panjang badan untuk setiap ukuran (cm)?", "lingkar"),
    "folding": ("folded size", "ukuran saat dilipat",
                "Buyers need the folded size to know whether it fits their vehicle or storage.",
                "Berapa ukuran saat dilipat (panjang x lebar x tinggi, cm)?", "lipat"),
    "generic": ("product size", "ukuran produk",
                "Buyers need the actual product dimensions.",
                "Berapa ukuran produk (panjang x lebar x tinggi, cm)?", ""),
}
_OTHER_TOPICS = [
    ("wrong_item", "wrong variant sent", "varian yang dikirim salah", "operational", "fix_operations",
     "Buyers expect to receive the variant they ordered.", "Bagaimana proses pengecekan varian sebelum dikirim?"),
    ("delivery", "delivery time", "waktu pengiriman", "operational", "fix_operations",
     "Buyers expect the parcel to arrive within the estimate.", "Kapan pesanan biasanya dikirim setelah dibayar?"),
    ("packaging", "packaging", "kemasan", "operational", "fix_operations",
     "Buyers expect the item to arrive undamaged and well packed.", "Bagaimana barang dikemas sebelum dikirim?"),
    ("service", "seller responsiveness", "respons penjual", "operational", "fix_operations",
     "Buyers expect questions in chat to be answered.", "Berapa lama rata-rata chat pembeli dibalas?"),
    ("appearance", "appearance versus photos", "kesesuaian dengan foto", "expectation_mismatch", "set_expectation",
     "Buyers expect the product to look like the photos.", "Bagian mana yang berbeda dari foto (warna, bentuk, bahan)?"),
    ("quality", "product quality", "kualitas produk", "product_quality", "fix_product",
     "Buyers expect the product to work and last.", "Apa cacat yang paling sering dilaporkan dan dari batch mana?"),
    ("stitching", "stitching quality", "kualitas jahitan", "product_quality", "fix_product",
     "Buyers expect seams that hold.", "Bagian jahitan mana yang lepas?"),
]


def product_kind(title: str) -> str:
    if _FOLDING.search(title or ""):
        return "folding"
    if _BAG.search(title or ""):
        return "bag"
    if _CLOTHING.search(title or ""):
        return "clothing"
    return "generic"


def _size_fact_present(listing: str, marker: str) -> bool:
    """Listing sudah memuat ukuran untuk lokasi yang ditanyakan (mis. "dalam", "lipat")."""
    for clause in lexicon.clauses(listing):
        has_length = any(q.unit in {"cm", "mm", "m", "inch"} for q in verify.extract_quantities(clause.text))
        if has_length and (not marker or marker in clause.tokens or any(t.startswith(marker) for t in clause.tokens)):
            return True
    return False


def _size_proposal(title: str, listing: str) -> dict:
    kind = product_kind(title)
    attribute, local, expectation, question, marker = _SIZE_TOPICS[kind]
    lengths_anywhere = _size_fact_present(listing, "")
    present = _size_fact_present(listing, marker)
    finding_type = "unclear_fact" if (present or (lengths_anywhere and not marker)) else "missing_fact"
    return {"topic": "size", "attribute": attribute, "attribute_local": local, "finding_type": finding_type,
            "fix_type": "add_fact" if finding_type == "missing_fact" else "clarify_wording",
            "buyer_expectation": expectation, "merchant_question": question, "listing_evidence": ""}


def analyse(title: str, listing: str, reviews: list[dict]) -> tuple[list[dict], dict]:
    """Temuan usulan dari SEMUA ulasan tersimpan. Bukti = klausa asli yang lolos juri relevansi."""
    proposals = [_size_proposal(title, listing)]
    for key, attribute, local, ftype, fix, expectation, question in _OTHER_TOPICS:
        proposals.append({"topic": key, "attribute": attribute, "attribute_local": local, "finding_type": ftype,
                          "fix_type": fix, "buyer_expectation": expectation, "merchant_question": question,
                          "listing_evidence": ""})
    out = []
    claimed: set[str] = set()
    for proposal in proposals:
        evidence = []
        for review in reviews:
            verdict = relevance.judge(review["text"], proposal, review.get("rating"))
            if verdict.label == relevance.SUPPORTS and verdict.clause:
                evidence.append({"review_id": review["id"], "quote": verdict.clause})
        # Kualitas umum hanya mengambil ulasan yang belum diklaim topik lain yang lebih spesifik.
        if proposal["topic"] == "quality":
            evidence = [e for e in evidence if e["review_id"] not in claimed]
        if evidence:
            claimed.update(e["review_id"] for e in evidence)
            out.append({**proposal, "evidence": evidence[:15]})
    return out, {"stage": "discovery", "engine": "rules", "proposed": len(out),
                 "note": "Rule engine read every stored review"}
