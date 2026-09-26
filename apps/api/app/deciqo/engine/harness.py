"""Menjalankan engine in-process atas satu bundle kasus, tanpa server HTTP.

Dipakai runner evaluasi. Jalurnya sama dengan API: ingest satu pintu (redaksi PII), `pipeline.analyse`,
`facts.save`, dan `draft.build`, pada berkas SQLite yang diberikan pemanggil dengan akun evaluasi
sendiri, sehingga basis data demo tidak tersentuh.
"""

from __future__ import annotations

from pathlib import Path

from .. import ingest, store
from ..errors import DeciqoError
from . import PIPELINE_VERSION, VERIFIER_VERSION, draft, facts, pipeline

EVAL_EMAIL = "eval@deciqo.local"


def _eval_user(conn) -> int:
    found = conn.execute("SELECT id FROM users WHERE email = ?", (EVAL_EMAIL,)).fetchone()
    if found:
        return found["id"]
    cur = conn.execute("INSERT INTO users(email, name, password_hash, created_at) VALUES(?, 'Eval', '!', ?)",
                       (EVAL_EMAIL, store.now()))
    return cur.lastrowid


def _review_time(value: str | None) -> str | None:
    if not value:
        return None
    parsed = store.parse_time(value if "T" in value else f"{value}T00:00:00+00:00")
    return parsed.isoformat() if parsed else None


def _target(findings: list[dict], words: list[str]) -> dict | None:
    """Temuan yang dijawab fakta: yang butuh fakta dan paling cocok dengan kata target."""
    needing = [f for f in findings if f["finding_type"] in pipeline.FACT_REQUIRED
               or f["finding_type"] == "expectation_mismatch"]
    if not needing:
        return None
    lowered = [w.lower() for w in words or []]

    def score(f: dict) -> tuple[int, int]:
        hay = f"{f['attribute']} {f['attribute_local']} {f['attribute_key']}".lower()
        return (sum(1 for w in lowered if w and w in hay), f["support"])

    return max(needing, key=score)


def run_bundle(bundle: dict, *, db_path: str | Path, engine: str = "ai") -> dict:
    """`bundle`: title, listing, reviews[{id, rating, text, date?, variant?}], fact?, fact_target_words?.

    Mengembalikan temuan beserta status draf per temuan, versi engine, dan usage."""
    db_path = Path(db_path)
    store.migrate(db_path)
    errors: list[str] = []
    with store.database(db_path) as conn:
        user_id = _eval_user(conn)
        product = {
            "source_item_id": bundle.get("case_id") or store.digest(bundle.get("title", ""))[:12],
            "title": bundle.get("title", ""),
            "description": bundle.get("listing") or "",
            "reviews": [{"id": r.get("id"), "rating": r.get("rating"), "text": r.get("text", ""),
                         "variant": r.get("variant") or "", "review_time": _review_time(r.get("date"))}
                        for r in bundle.get("reviews", [])],
        }
        stats = ingest.upsert_catalog(user_id, "manual", [product], data_origin="synthetic", conn=conn)
    pid = stats.products[0]

    result: dict = {}
    try:
        result = pipeline.analyse(pid, force=True, engine="rules" if engine == "rules" else None, db_path=db_path)
    except pipeline.AnalysisFailed:
        # A provider failure is an error output, not a successful analysis with zero findings.
        raise

    with store.database(db_path) as conn:
        rows = store.rows(conn.execute(
            "SELECT * FROM findings WHERE product_id = ? AND not_detected_at IS NULL ORDER BY support DESC", (pid,)))
        fact_target = None
        if bundle.get("fact"):
            fact_target = _target(rows, bundle.get("fact_target_words") or [])
            if fact_target is None:
                errors.append("fact_not_applied: no finding needs a fact")
            else:
                try:
                    facts.save(conn, fact_target, bundle["fact"], user_id=user_id)
                except DeciqoError as exc:
                    # Gerbang fakta menolak jawaban ini; draf tetap ditahan dan alasannya tercatat.
                    errors.append(f"fact_rejected:{exc.code}")
        drafted = draft.build(conn, pid)
        analysis = store.row(conn.execute("SELECT engine FROM analyses WHERE product_id = ?", (pid,))) or {}
    sections = {s["finding_id"]: s for s in drafted.get("sections", [])}
    findings = []
    for f in rows:
        evidence = pipeline.read_evidence(f["evidence_json"])
        section = sections.get(f["id"])
        findings.append({
            "id": f["id"], "attribute": f["attribute"], "attribute_local": f["attribute_local"],
            "buyer_expectation": f["buyer_expectation"], "finding_type": f["finding_type"],
            "merchant_question": f["merchant_question"], "severity": f["severity"],
            "support_ids": [i["review_id"] for i in evidence["items"]],
            "contradict_ids": [i["review_id"] for i in evidence["contradicting"]],
            # Label model yang disisihkan verifier/juri, supaya kehilangan recall bisa diatribusikan.
            "set_aside": [{"review_id": x.get("review_id"), "reason": x.get("reason"),
                           "model_label": x.get("model_label", "")}
                          for x in store.loads(f.get("rejected_json"), [])],
            "metrics": evidence["metrics"],
            "listing_status": store.loads(f["listing_check_json"], {}).get("status"),
            "fact_applied": bool(fact_target and fact_target["id"] == f["id"]),
            "draft": {"status": section["status"], "text": section["text"], "reasons": section["reasons"]}
            if section else {"status": "route", "text": "", "reasons": []},
        })
    usage = result.get("usage") or {}
    return {
        "findings": findings, "engine": analysis.get("engine") or result.get("engine"),
        "engine_note": result.get("note", ""), "draft_status": drafted.get("status"),
        "pipeline_version": PIPELINE_VERSION, "verifier_version": VERIFIER_VERSION,
        "usage": usage, "cost_usd": usage.get("cost_usd", 0.0), "trace": result.get("trace", []),
        "errors": errors,
    }
