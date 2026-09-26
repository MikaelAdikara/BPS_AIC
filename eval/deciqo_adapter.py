"""Jembatan runner ke engine Deciqo in-process (tanpa server HTTP).

Engine dijalankan pada berkas SQLite terpisah untuk setiap run eval, dengan akun evaluasi sendiri,
sehingga DB demo tidak tersentuh. Adapter ini hanya menormalkan bentuk hasil supaya skor bisa
dihitung; keputusan (temuan, hitungan, status draf) tetap milik engine.

Engine diharapkan menyediakan `app.deciqo.engine.harness.run_bundle(bundle, db_path=..., engine=...)`
yang mengembalikan dict berisi `findings` (lihat `normalise_result`). Bila fungsi itu belum ada,
`available()` mengembalikan alasan dan runner tidak menulis baris D.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
API_DIR = REPO / "apps" / "api"

LISTING_TYPES = {"missing_fact", "unclear_fact", "conflicting_fact", "expectation_mismatch"}
HELD_STATUSES = {"needs_merchant_fact", "needs_listing"}


def _import_harness():
    if str(API_DIR) not in sys.path:
        sys.path.insert(0, str(API_DIR))
    return importlib.import_module("app.deciqo.engine.harness")


def available() -> tuple[bool, str]:
    try:
        mod = _import_harness()
    except Exception as exc:  # modul belum ada atau gagal diimpor
        return False, f"engine harness tidak bisa diimpor: {type(exc).__name__}: {exc}"
    if not hasattr(mod, "run_bundle"):
        return False, "app.deciqo.engine.harness tidak punya run_bundle"
    return True, "ok"


def versions() -> dict:
    try:
        if str(API_DIR) not in sys.path:
            sys.path.insert(0, str(API_DIR))
        eng = importlib.import_module("app.deciqo.engine")
        return {"pipeline_version": getattr(eng, "PIPELINE_VERSION", None),
                "verifier_version": getattr(eng, "VERIFIER_VERSION", None)}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def route_of(finding_type: str | None) -> str:
    if finding_type in LISTING_TYPES:
        return "listing"
    if finding_type == "product_quality":
        return "quality"
    if finding_type == "operational":
        return "operations"
    return "unknown"


def normalise_result(raw: dict) -> dict:
    """Bentuk seragam: findings[{id, attribute, attribute_local, finding_type, route,
    support_ids, contradict_ids, listing_status, draft_status, draft_text, merchant_question}]."""
    findings = []
    for f in raw.get("findings", []) or []:
        draft = f.get("draft") or {}
        findings.append({
            "id": f.get("id"),
            "attribute": f.get("attribute", ""),
            "attribute_local": f.get("attribute_local", ""),
            "buyer_expectation": f.get("buyer_expectation", ""),
            "finding_type": f.get("finding_type"),
            "route": f.get("route") or route_of(f.get("finding_type")),
            "support_ids": sorted(set(f.get("support_ids") or f.get("supports") or [])),
            "contradict_ids": sorted(set(f.get("contradict_ids") or f.get("contradicts") or [])),
            "listing_status": f.get("listing_status"),
            "draft_status": draft.get("status") or f.get("draft_status"),
            "draft_text": draft.get("text") or f.get("draft_text") or "",
            "draft_reasons": draft.get("reasons") or [],
            "fact_applied": bool(f.get("fact_applied")),
            "merchant_question": f.get("merchant_question", ""),
        })
    return {
        "findings": findings,
        "engine": raw.get("engine"),
        "engine_note": raw.get("engine_note", ""),
        "draft_status": raw.get("draft_status"),
        "pipeline_version": raw.get("pipeline_version"),
        "verifier_version": raw.get("verifier_version"),
        "usage": raw.get("usage") or {},
        "cost_usd": float((raw.get("usage") or {}).get("cost_usd") or raw.get("cost_usd") or 0.0),
        "errors": raw.get("errors") or [],
        # Jejak langkah engine (triage, discovery, verifier) untuk menjelaskan hasil kosong.
        "trace": raw.get("trace") or [],
    }


def run(case: dict, phase: str, *, db_path: Path, engine: str) -> dict:
    """Jalankan satu kasus. Fase after memberi fakta merchant yang sama dengan baseline."""
    mod = _import_harness()
    bundle = {
        "case_id": case["id"],
        "title": case["title"],
        "listing": case.get("listing", ""),
        "reviews": case["reviews"],
        "fact": case.get("fact") if phase == "after" else None,
        # Sama seperti merchant yang memilih isu mana yang ia jawab: fakta dipasang ke temuan yang
        # atributnya cocok dengan kata ini. Engine tidak memakai kata ini untuk menemukan isu.
        "fact_target_words": case["gold"].get("attribute_words", []) if phase == "after" else [],
    }
    raw = mod.run_bundle(bundle, db_path=str(db_path), engine=engine)
    return normalise_result(raw)
