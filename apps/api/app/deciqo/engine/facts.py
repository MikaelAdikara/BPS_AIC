"""Fakta merchant: jawaban atas pertanyaan temuan, disimpan terstruktur.

Fakta adalah pernyataan merchant, bukan pengukuran oleh Deciqo. Satu fakta aktif per temuan;
versi lama disimpan dengan `active = 0`.
"""

from __future__ import annotations

import re

from .. import store
from ..errors import DeciqoError
from . import verify

UNITS = ("cm", "mm", "inch", "kg", "g", "ml", "l", "mah", "w", "v")
_LOCATIONS = [
    ("inner", re.compile(r"\b(dalam|inner|inside|interior)\b", re.I)),
    ("outer", re.compile(r"\b(luar|outer|outside|exterior)\b", re.I)),
    ("folded", re.compile(r"\b(lipat|dilipat|folded)\b", re.I)),
    ("open", re.compile(r"\b(dibuka|terbuka|unfolded|open)\b", re.I)),
]


def detect_location(text: str) -> str:
    for name, pattern in _LOCATIONS:
        if pattern.search(text or ""):
            return name
    return ""


def parse(raw: str, unit: str = "") -> dict:
    """Pisahkan nilai, satuan, dan lokasi dari jawaban merchant. Tidak memvalidasi."""
    text = " ".join(f"{raw or ''} {unit or ''}".split())
    quantities = verify.extract_quantities(text)
    if quantities:
        unit_found = quantities[0].unit
        same = [q for q in quantities if q.unit == unit_found]
        value = " x ".join(q.text.rsplit(" ", 1)[0] for q in same)
    else:
        unit_found, value = (unit or "").lower(), (raw or "").strip()
    return {"raw_value": (raw or "").strip(), "value": value, "unit": unit_found, "location": detect_location(raw)}


def validate(finding: dict, raw: str, unit: str = "") -> dict:
    """Jawaban kosong ditolak. Kembalikan fakta terurai."""
    if not (raw or "").strip():
        raise DeciqoError(422, "not_a_fact", "Write the actual value (for example 32 x 24 cm), not a confirmation.")
    return parse(raw, unit)


def active_fact(conn, finding_id: str) -> dict | None:
    return store.row(conn.execute(
        "SELECT * FROM facts WHERE finding_id = ? AND active = 1 ORDER BY id DESC LIMIT 1", (finding_id,)))


def save(conn, finding: dict, raw: str, unit: str = "", variant: str = "", user_id: int | None = None) -> dict:
    parsed = validate(finding, raw, unit)
    snapshot = conn.execute("SELECT snapshot_hash FROM products WHERE id = ?", (finding["product_id"],)).fetchone()
    conn.execute("UPDATE facts SET active = 0 WHERE finding_id = ?", (finding["id"],))
    now = store.now()
    conn.execute(
        "INSERT INTO facts(finding_id, attribute, raw_value, value, unit, location, variant, source_kind, "
        "listing_snapshot_hash, confirmed_by, confirmed_at, active) VALUES(?, ?, ?, ?, ?, ?, ?, 'merchant_fact', ?, ?, ?, 1)",
        (finding["id"], finding.get("attribute", ""), parsed["raw_value"], parsed["value"], parsed["unit"],
         parsed["location"], variant or "", snapshot["snapshot_hash"] if snapshot else "", user_id, now))
    if finding.get("state") == "open":
        conn.execute("UPDATE findings SET state = 'investigating', updated_at = ? WHERE id = ?", (now, finding["id"]))
    return public(active_fact(conn, finding["id"]))


def public(fact: dict | None) -> dict | None:
    if not fact:
        return None
    return {"value": fact["value"], "unit": fact["unit"], "raw_value": fact["raw_value"],
            "location": fact["location"], "variant": fact["variant"], "source": fact["source_kind"],
            "confirmed_at": fact["confirmed_at"]}
