"""Draf teks listing per temuan, dirender dari fakta terstruktur dan diperiksa gerbang fakta.

Teks siap dirender dari fakta yang sudah dikonfirmasi merchant (template per atribut). Temuan yang
butuh fakta dan belum punya fakta DITAHAN di sini, di backend, apa pun isi teksnya.

Status "ready" berarti "Ready for your review", bukan "benar".
"""

from __future__ import annotations

import re

from .. import store
from . import VERIFIER_VERSION, facts, pipeline, verify

# Urutan dari yang paling lemah; status draf keseluruhan = section terlemah.
STATUS_RANK = ["blocked", "needs_merchant_fact", "needs_listing", "needs_review", "ready"]


_PURE_QUANTITY = re.compile(r"^[\d\s.,x×*]+(?:[a-z]{1,4})?\.?$", re.I)


_LABEL_QUANTITY = re.compile(r"\s*\(?\b\d+(?:[.,]\d+)?[\s-]*(?:inch|inci|in|cm|mm|kg|g|ml|l|mah|w|v|a)\b\)?", re.I)


def _label(finding: dict) -> str:
    """Label atribut untuk kalimat draf. Label ditulis model, jadi hanya bagian utamanya yang dipakai
    ("ukuran saku dalam / muat untuk tablet 11 inch" → "Ukuran saku dalam") dan angka bersatuan di
    dalamnya dibuang: angka di draf hanya boleh datang dari fakta."""
    label = (finding.get("attribute_local") or finding.get("attribute") or "").strip()
    label = re.split(r"\s+/\s+|\s*\(", label)[0].strip() or label
    label = _LABEL_QUANTITY.sub("", label).strip(" ,-")
    return label[:1].upper() + label[1:]


def fact_body(finding: dict, fact: dict) -> str:
    """Isi kalimat dari jawaban merchant apa adanya.

    Jawaban dipakai utuh supaya varian, sumbu, dan keterangan tidak hilang ("S: lingkar dada 96 cm;
    M: ...", "lebar maksimal 8,5 cm termasuk case", "9V 2,2A (20W)"). Satu-satunya yang dibuang
    adalah awalan yang hanya mengulang label bila sisanya murni angka dan satuan ("ukuran dalam
    30 x 22 cm" di bawah label "Ukuran kompartemen dalam"). Satuan dari pilihan form ditambahkan
    bila jawabannya hanya angka."""
    raw = " ".join((fact.get("raw_value") or fact.get("value") or "").split()).rstrip(".")
    unit = fact.get("unit") or ""
    if unit and not verify.extract_quantities(raw) and verify.extract_quantities(f"{raw} {unit}"):
        raw = f"{raw} {unit}"
    label_words = set(re.findall(r"[a-z]+", _label(finding).lower()))
    words = raw.split(" ")
    cut = 0
    while cut < len(words) and words[cut].lower().strip(":") in label_words:
        cut += 1
    rest = " ".join(words[cut:])
    if cut and rest and _PURE_QUANTITY.match(rest):
        raw = rest
    return raw


def render(finding: dict, fact: dict) -> str:
    return f"{_label(finding)}: {fact_body(finding, fact)}."


def gate(text: str, sources: list[str]) -> tuple[str, list[str], list[str]]:
    """(status, alasan, hal tanpa sumber) untuk teks yang sudah terisi. Urutan: placeholder →
    kuantitas tanpa sumber → klaim berisiko tanpa sumber berpolaritas sama → ready."""
    if verify.placeholders(text):
        return "needs_merchant_fact", ["placeholder_left"], []
    bad = verify.unsupported_quantities(text, sources)
    if bad:
        return "blocked", ["unsupported_quantity"], [q.text for q in bad]
    claims = verify.unsupported_claims(text, sources)
    if claims:
        return "blocked", ["unsupported_claim"], [("not " if not c.positive else "") + c.text for c in claims]
    return "ready", [], []


def sources_for(fact: dict, listing: str, listing_check: dict | None) -> list[str]:
    """Sumber draf: fakta merchant, ditambah listing KECUALI listing sedang dibantah pembeli. Listing
    yang menyatakan 20000 mAh dan dibantah tidak boleh membenarkan angka itu lagi."""
    out = [fact.get("raw_value", ""), f"{fact['value']} {fact['unit']}".strip()]
    if (listing_check or {}).get("status") != "conflicting":
        out.append(listing)
    return out


def section(finding: dict, fact: dict | None, listing: str, listing_provided: bool,
            listing_check: dict | None = None) -> dict:
    base = {"finding_id": finding["id"], "status": "", "text": "", "rendered_from": None,
            "held_suggestion": None, "reasons": [], "unsupported": [], "sources": []}
    # Tanpa listing, temuan adalah kebutuhan pembeli: draf menunggu listing ditempel dulu, dan
    # merchant tidak diminta fakta untuk listing yang belum ada (sama dengan bucket/next di inbox).
    if not listing_provided:
        return {**base, "status": "needs_listing", "reasons": ["listing_not_provided"]}
    needs_fact = finding["finding_type"] in pipeline.FACT_REQUIRED or finding["finding_type"] == "expectation_mismatch"
    check = listing_check or {}
    if needs_fact and not fact:
        # Listing tidak pernah dirender menjadi teks draf: kutipan usulan model bisa berupa seluruh
        # listing atau hal yang hanya terkait ("ukuran luar" untuk pertanyaan ukuran dalam). Hanya
        # ekspektasi yang sudah dinyatakan listing (pembeli salah tangkap) yang tidak ditahan:
        # merchant diminta meninjau penekanannya, tanpa teks baru.
        quote = (check.get("quote") or "").strip()
        if (finding["finding_type"] == "expectation_mismatch" and check.get("status") == "evidence_found"
                and quote and verify.quote_in(quote, listing)):
            return {**base, "status": "needs_review", "reasons": ["already_in_listing"],
                    "sources": [{"kind": "listing", "quote": quote}]}
        return {**base, "status": "needs_merchant_fact", "reasons": ["missing_fact"]}
    text = render(finding, fact) if fact else ""
    if not text:
        return {**base, "status": "needs_review", "reasons": ["nothing_rendered"]}
    status, reasons, unsupported = gate(text, sources_for(fact, listing, check))
    return {**base, "status": status, "text": text if status != "blocked" else "", "rendered_from": "merchant_fact",
            "reasons": reasons, "unsupported": unsupported,
            "sources": [{"kind": "merchant_fact", "confirmed_at": fact.get("confirmed_at")}]}


def weakest(statuses: list[str]) -> str:
    if not statuses:
        return "nothing_to_draft"
    return min(statuses, key=STATUS_RANK.index)


def build(conn, product_id: str) -> dict:
    """Draf produk dari temuan aktif yang bisa diperbaiki lewat listing. Di-cache per input."""
    product = store.row(conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)))
    listing, provided = pipeline.listing_parts(product)
    findings = [f for f in store.rows(conn.execute(
        "SELECT * FROM findings WHERE product_id = ? AND not_detected_at IS NULL "
        "AND state IN ('open', 'investigating', 'reopened', 'acted') ORDER BY support DESC", (product_id,)))
        if f["finding_type"] in pipeline.LISTING_FIXABLE]
    fact_rows = {f["id"]: facts.active_fact(conn, f["id"]) for f in findings}
    key = store.digest([(f["id"], f["updated_at"], f["finding_type"], f["listing_check_json"]) for f in findings],
                       [(k, v["id"] if v else None) for k, v in fact_rows.items()],
                       product["snapshot_hash"], VERIFIER_VERSION)
    cached = conn.execute("SELECT result_json FROM drafts WHERE product_id = ? AND input_hash = ?",
                          (product_id, key)).fetchone()
    if cached:
        return store.loads(cached["result_json"], {})
    sections = [section(f, fact_rows[f["id"]], listing, provided, store.loads(f["listing_check_json"], {}))
                for f in findings]
    result = {"status": weakest([s["status"] for s in sections]), "gate_version": VERIFIER_VERSION,
              "sections": sections, "title_suggestion": {"text": "", "status": "unchanged"}}
    conn.execute("INSERT OR REPLACE INTO drafts(product_id, input_hash, result_json, created_at) VALUES(?, ?, ?, ?)",
                 (product_id, key, store.dumps(result), store.now()))
    return result
