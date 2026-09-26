"""Orkestrasi analisis satu produk: dari ulasan tersimpan ke temuan berbukti yang tersimpan.

    triage → discovery (AI) atau analyser aturan → membership (AI) → verifier kutipan
    → juri relevansi → pemeriksaan listing → metrik & severity (kode) → simpan + rekonsiliasi

Model mengusulkan, kode memutuskan: label model tidak pernah dihitung apa adanya. Setiap pasangan
(ulasan, temuan) dari jalur mana pun melewati verifier dan juri relevansi yang sama, dan semua
angka (support, denominator, share, severity) dihitung di sini dari ulasan tersimpan.

Transaksi basis data sengaja dipecah: baca → panggil model TANPA memegang kunci tulis → tulis.
"""

from __future__ import annotations

import logging
import math
import re
from datetime import datetime, timedelta, timezone

from .. import store
from . import PIPELINE_VERSION, VERIFIER_VERSION, lexicon, listing_check, relevance, rules, triage, verify

log = logging.getLogger("deciqo.engine")

LISTING_FIXABLE = {"missing_fact", "unclear_fact", "conflicting_fact", "expectation_mismatch"}
FACT_REQUIRED = {"missing_fact", "unclear_fact", "conflicting_fact"}
FINDING_TYPES = LISTING_FIXABLE | {"product_quality", "operational"}
MEMBERSHIP_LIMIT = 150
ACTIVE_STATES = {"open", "investigating", "reopened"}


class AnalysisFailed(Exception):
    """Analisis gagal (mis. provider error). Temuan tersimpan tidak diubah."""


# --- identitas temuan -----------------------------------------------------------------------

_KEY_STOP = {"the", "of", "a", "an", "and", "or", "for", "to", "in", "on", "with", "product", "item",
             "info", "information", "detail", "details", "details", "spec", "specs", "specification",
             "issue", "problem", "missing", "unclear", "actual", "real", "listed", "stated"}
_KEY_SYNONYMS = {
    "dimension": "size", "dimensions": "size", "measurement": "size", "measurements": "size",
    "sizing": "size", "sizes": "size", "ukuran": "size", "dimensi": "size",
    "inside": "inner", "interior": "inner", "internal": "inner",
    "folding": "folded", "fold": "folded", "colour": "color", "colors": "color",
    "shipping": "delivery", "shipment": "delivery", "packing": "packaging", "package": "packaging",
    "responsiveness": "response", "responses": "response", "reply": "response", "replies": "response",
    "compartments": "compartment", "batteries": "battery",
}


def attribute_key(attribute: str) -> str:
    """Atribut dinormalisasi: parafrasa model ("inner size" / "interior dimensions") → kunci sama."""
    words = re.findall(r"[a-z0-9]+", verify.normalise(attribute))
    kept = {_KEY_SYNONYMS.get(w, w) for w in words if w not in _KEY_STOP}
    return " ".join(sorted(kept)) or "general"


def finding_id(product_id: str, key: str) -> str:
    return store.short_id("f", product_id, key)


# --- blob bukti: satu fungsi baca, satu bentuk ------------------------------------------------


def read_evidence(raw) -> dict:
    blob = store.loads(raw, None) if isinstance(raw, str) or raw is None else raw
    if isinstance(blob, list):  # bentuk lama: daftar item saja
        blob = {"items": blob}
    blob = blob if isinstance(blob, dict) else {}
    return {"items": blob.get("items") or [], "contradicting": blob.get("contradicting") or [],
            "uncertain": int(blob.get("uncertain") or 0), "metrics": blob.get("metrics") or {}}


def write_evidence(items: list, contradicting: list, uncertain: int, metrics: dict) -> str:
    return store.dumps({"items": items, "contradicting": contradicting, "uncertain": uncertain,
                        "metrics": metrics})


# --- data produk ----------------------------------------------------------------------------


def load_reviews(conn, product_id: str) -> list[dict]:
    return store.rows(conn.execute(
        "SELECT * FROM reviews WHERE product_id = ? AND deleted_at IS NULL ORDER BY review_time, id",
        (product_id,)))


def listing_parts(product: dict) -> tuple[str, bool]:
    """Teks listing yang diperiksa (deskripsi + spesifikasi) dan apakah listing sudah diberikan."""
    specs = store.loads(product.get("specs_json"), {}) or {}
    spec_text = "\n".join(f"{k}: {v}" for k, v in specs.items()) if isinstance(specs, dict) else ""
    body = "\n".join(p for p in [(product.get("description") or "").strip(), spec_text.strip()] if p)
    return body, bool(body)


# --- metrik & severity ----------------------------------------------------------------------


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def compute_metrics(support_ids: set[str], contradicting: int, reviews: list[dict],
                    candidates_read: int, finding_type: str) -> dict:
    by_id = {r["id"]: r for r in reviews}
    supporters = [by_id[i] for i in support_ids if i in by_id]
    support = len(supporters)
    ratings = [r["rating"] for r in reviews if r.get("rating")]
    others = [r["rating"] for r in reviews if r.get("rating") and r["id"] not in support_ids]
    variants = []
    all_variants: dict[str, int] = {}
    for r in reviews:
        if r.get("variant"):
            all_variants[r["variant"]] = all_variants.get(r["variant"], 0) + 1
    if all_variants and support:
        counted: dict[str, int] = {}
        for r in supporters:
            if r.get("variant"):
                counted[r["variant"]] = counted.get(r["variant"], 0) + 1
        for name, n in sorted(all_variants.items()):
            variants.append({"variant": name, "complaints": counted.get(name, 0),
                             "complaint_share": round(counted.get(name, 0) / support, 3),
                             "review_share": round(n / len(reviews), 3), "exploratory": support < 5})
    return {
        "support": support,
        "denominator": len(reviews),
        "candidates_read": candidates_read,
        "support_is_minimum": candidates_read < len(reviews),
        "share": round(support / candidates_read, 4) if candidates_read else 0.0,
        "contradicting": contradicting,
        "hidden_high_star": sum(1 for r in supporters if (r.get("rating") or 0) >= 4),
        "with_photos": sum(1 for r in supporters if store.loads(r.get("images_json"), [])),
        "rating_now": _mean(ratings),
        "rating_without": _mean(others),
        "variants": variants,
    }


def severity(metrics: dict, finding_type: str) -> str:
    """Oleh kode: satu laporan tetap `low` seberapa pun keras kata-katanya."""
    support = metrics["support"]
    weight = support + 0.5 * metrics["hidden_high_star"] + (0.5 if finding_type in {"missing_fact", "conflicting_fact"} else 0)
    if support >= 3 and (weight >= 4 or metrics["share"] >= 0.08):
        return "high"
    if support >= 2:
        return "medium"
    return "low"


def wilson_lower(k: int, n: int, z: float = 1.96) -> float:
    if n <= 0:
        return 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (centre - margin) / denom)


# --- menilai pasangan (ulasan, temuan) ------------------------------------------------------


def _judge_pairs(proposal: dict, reviews: list[dict], engine: str, labels: list[dict]) -> dict:
    """Terapkan verifier + juri relevansi pada semua pasangan untuk satu temuan usulan.

    `labels`: `{review_id, label, quote, via}` dari discovery/membership. Pada mode aturan
    daftarnya kosong dan juri menilai SEMUA ulasan tersimpan langsung."""
    by_id = {r["id"]: r for r in reviews}
    supports: dict[str, dict] = {}
    contradicting: dict[str, dict] = {}
    uncertain: dict[str, str] = {}
    rejected: dict[str, str] = {}
    wrong_item: set[str] = set()

    if engine == "rules":
        for review in reviews:
            verdict = relevance.judge(review["text"], proposal, review.get("rating"))
            if verdict.label == relevance.SUPPORTS:
                supports[review["id"]] = {"quote": verdict.clause}
            elif verdict.label == relevance.CONTRADICTS:
                contradicting[review["id"]] = {"quote": verdict.clause}
            elif verdict.label == relevance.UNCERTAIN and verdict.reason != "mentions_attribute_without_complaint":
                uncertain[review["id"]] = verdict.reason
            if verdict.reason in {"wrong_item_routes_to_operations", "also_reports_wrong_variant"}:
                wrong_item.add(review["id"])
        return {"supports": supports, "contradicting": contradicting, "uncertain": uncertain,
                "rejected": rejected, "wrong_item": wrong_item}

    model_labels: dict[str, set[str]] = {}
    quotes: dict[str, str] = {}
    for item in labels:
        rid = str(item.get("review_id", ""))
        review = by_id.get(rid)
        if review is None:
            rejected[rid] = "unknown_review_id"
            continue
        ok, reason = verify.check_quote(item.get("quote", ""), review["text"])
        if not ok:
            rejected.setdefault(rid, reason)
            continue
        model_labels.setdefault(rid, set()).add(item.get("label", "supports"))
        quotes.setdefault(rid, item.get("quote", ""))
    for rid, said in model_labels.items():
        rejected.pop(rid, None)
        review = by_id[rid]
        verdict = relevance.judge(review["text"], proposal, review.get("rating"))
        if verdict.reason in {"wrong_item_routes_to_operations", "also_reports_wrong_variant"}:
            wrong_item.add(rid)
        if len(said) > 1:
            uncertain[rid] = "labelled_both_ways"
        elif "supports" in said:
            if verdict.label == relevance.SUPPORTS:
                supports[rid] = {"quote": quotes[rid]}
            elif verdict.label == relevance.CONTRADICTS:
                uncertain[rid] = "labelled_both_ways"
            elif verdict.label == relevance.UNCERTAIN:
                uncertain[rid] = verdict.reason
            else:
                rejected[rid] = verdict.reason or "complaint_not_about_this_attribute"
        elif "contradicts" in said:
            if verdict.label == relevance.SUPPORTS:
                uncertain[rid] = "labelled_both_ways"
            elif verdict.label in {relevance.CONTRADICTS, relevance.UNCERTAIN}:
                contradicting[rid] = {"quote": quotes[rid]}
            else:
                rejected[rid] = verdict.reason or "not_about_this_attribute"
    return {"supports": supports, "contradicting": contradicting, "uncertain": uncertain,
            "rejected": rejected, "wrong_item": wrong_item}


def _wrong_item_proposal() -> dict:
    return next({**p, "evidence": []} for p in _rules_topics() if p["topic"] == "wrong_item")


def _rules_topics() -> list[dict]:
    return [{"topic": key, "attribute": a, "attribute_local": al, "finding_type": ft, "fix_type": fx,
             "buyer_expectation": be, "merchant_question": mq, "listing_evidence": ""}
            for key, a, al, ft, fx, be, mq in rules._OTHER_TOPICS]


# --- analisis ---------------------------------------------------------------------------------


def _engine_choice(requested: str | None, user_id: int | None) -> tuple[str, str]:
    """('ai'|'rules', catatan). Mode aturan bila tanpa key, key ditolak, atau diminta."""
    if requested == "rules":
        return "rules", "requested"
    try:
        from . import llm  # noqa: PLC0415
    except ImportError:
        return "rules", "llm_unavailable"
    ok, reason = llm.available(user_id)
    return ("ai", "") if ok else ("rules", reason)


def _input_hash(reviews: list[dict], product: dict, engine: str, model: str) -> str:
    return store.digest(sorted(r["version_hash"] for r in reviews), product.get("snapshot_hash", ""),
                        PIPELINE_VERSION, VERIFIER_VERSION, engine, model)


def analyse(product_id: str, force: bool = False, *, engine: str | None = None,
            db_path=None) -> dict:
    """Analisis satu produk dan simpan hasilnya. Mengembalikan ringkasan (engine, temuan, trace)."""
    # 1. baca
    with store.database(db_path) as conn:
        product = store.row(conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)))
        if product is None:
            raise KeyError(product_id)
        user = store.row(conn.execute("SELECT id, is_demo FROM users WHERE id = ?", (product["user_id"],))) or {}
        reviews = load_reviews(conn, product_id)
        previous = store.row(conn.execute("SELECT * FROM analyses WHERE product_id = ?", (product_id,)))
        candidates, triage_trace = triage.candidates(reviews, conn)

    mode, note = _engine_choice(engine, product["user_id"])
    model_name = ""
    if mode == "ai":
        from . import llm  # noqa: PLC0415

        model_name = llm.model_name()
    input_hash = _input_hash(reviews, product, mode, model_name)
    if (not force and previous and previous["status"] == "ready" and previous["input_hash"] == input_hash):
        return {"product_id": product_id, "engine": previous["engine"], "status": "unchanged",
                "trace": store.loads(previous["trace_json"], [])}

    listing, provided = listing_parts(product)
    trace = [triage_trace]
    usage: dict = {}
    ai_output = None
    ai_hash = ""

    # 2. usulan temuan (tanpa memegang kunci tulis)
    if mode == "ai":
        from . import discovery, llm  # noqa: PLC0415

        membership_reviews = reviews[-MEMBERSHIP_LIMIT:]
        ai_hash = discovery.ai_hash(product, listing, provided, candidates, membership_reviews, len(reviews))
        cached = store.loads(previous["summary_json"], {}) if previous else {}
        if not force and cached.get("ai_hash") == ai_hash and cached.get("ai_output"):
            ai_output = cached["ai_output"]
            trace.append({"stage": "discovery", "cached": True, "proposed": len(ai_output["proposals"])})
        else:
            try:
                ai_output = discovery.run_all(product, listing, provided, candidates, membership_reviews,
                                              len(reviews), user_id=product["user_id"], ref=product_id)
            except llm.KeyRejected as exc:
                mode, note = "rules", f"key_rejected:{exc.reason}"
            except llm.LLMError as exc:
                _record_failure(product_id, previous, exc, db_path)
                raise AnalysisFailed(str(exc)) from exc
            else:
                trace.extend(ai_output.get("trace", []))
                usage = ai_output.get("usage", {})

    if mode == "rules":
        proposals, rules_trace = rules.analyse(product["title"], listing, reviews)
        trace.append({**rules_trace, "note": note or rules_trace.get("note")})
        labels_by_index: dict[int, list[dict]] = {}
        candidates_read = len(reviews)
    else:
        proposals = ai_output["proposals"]
        labels_by_index = {}
        for i, p in enumerate(proposals):
            labels_by_index.setdefault(i, []).extend(
                {"review_id": e.get("review_id"), "label": "supports", "quote": e.get("quote", ""), "via": "discovery"}
                for e in p.get("evidence", []))
        for label in ai_output.get("labels", []):
            labels_by_index.setdefault(int(label.get("finding", -1)), []).append({**label, "via": "membership"})
        candidates_read = min(len(reviews), MEMBERSHIP_LIMIT)

    # 3. verifier + relevansi + metrik
    built: dict[str, dict] = {}
    wrong_item_ids: set[str] = set()
    quotes_rejected = dropped = 0
    for index, proposal in enumerate(proposals):
        if proposal.get("finding_type") not in FINDING_TYPES:
            proposal = {**proposal, "finding_type": "missing_fact"}
        judged = _judge_pairs(proposal, reviews, mode, labels_by_index.get(index, []))
        quotes_rejected += sum(1 for r in judged["rejected"].values() if r.startswith("quote_"))
        wrong_item_ids |= judged["wrong_item"]
        key = attribute_key(proposal.get("attribute", ""))
        if key in built:  # parafrasa atribut yang sama: satukan, jangan membuat isu baru
            target = built[key]["judged"]
            for part in ("supports", "contradicting", "uncertain", "rejected"):
                for rid, value in judged[part].items():
                    target[part].setdefault(rid, value)
            continue
        built[key] = {"proposal": proposal, "judged": judged}

    if wrong_item_ids and not any(lexicon.attribute_groups(b["proposal"]["attribute"]) == {"wrong_item"}
                                  for b in built.values()):
        proposal = _wrong_item_proposal()
        judged = _judge_pairs(proposal, [r for r in reviews if r["id"] in wrong_item_ids], "rules", [])
        built[attribute_key(proposal["attribute"])] = {"proposal": proposal, "judged": judged}

    findings = []
    for key, entry in built.items():
        proposal, judged = entry["proposal"], entry["judged"]
        # Dukungan yang juga dibantah pada pasangan yang sama tidak dihitung.
        support_ids = set(judged["supports"]) - set(judged["uncertain"])
        if not support_ids:
            dropped += 1
            continue
        metrics = compute_metrics(support_ids, len(judged["contradicting"]), reviews, candidates_read,
                                  proposal["finding_type"])
        check = listing_check.check(proposal, listing, provided)
        findings.append({"key": key, "proposal": proposal, "judged": judged, "support_ids": support_ids,
                         "metrics": metrics, "severity": severity(metrics, proposal["finding_type"]),
                         "listing_check": check})
    trace.append({"stage": "verifier", "kept": len(findings), "dropped": dropped,
                  "quotes_rejected": quotes_rejected})
    trace.append({"stage": "gate", "need_fact": sum(1 for f in findings if f["proposal"]["finding_type"] in FACT_REQUIRED),
                  "needs_listing": sum(1 for f in findings if f["proposal"]["finding_type"] in LISTING_FIXABLE and not provided)})

    # 4. tulis
    summary = {"ai_hash": ai_hash, "ai_output": ai_output, "engine_note": note, "usage": usage,
               "findings": len(findings), "denominator": len(reviews), "candidates_read": candidates_read,
               "triage_model": triage.model_version()}
    with store.database(db_path) as conn:
        saved = _persist(conn, product, user, reviews, findings, mode, input_hash)
        conn.execute(
            "INSERT INTO analyses(product_id, input_hash, ai_hash, engine, pipeline_version, verifier_version, "
            "status, summary_json, trace_json, created_at) VALUES(?, ?, ?, ?, ?, ?, 'ready', ?, ?, ?) "
            "ON CONFLICT(product_id) DO UPDATE SET input_hash = excluded.input_hash, ai_hash = excluded.ai_hash, "
            "engine = excluded.engine, pipeline_version = excluded.pipeline_version, "
            "verifier_version = excluded.verifier_version, status = 'ready', summary_json = excluded.summary_json, "
            "trace_json = excluded.trace_json, created_at = excluded.created_at",
            (product_id, input_hash, ai_hash, mode, PIPELINE_VERSION, VERIFIER_VERSION,
             store.dumps(summary), store.dumps(trace), store.now()))
    return {"product_id": product_id, "engine": mode, "status": "ready", "findings": saved,
            "trace": trace, "usage": usage, "note": note}


def _record_failure(product_id: str, previous: dict | None, exc: Exception, db_path) -> None:
    """Kegagalan provider tercatat di status analisis; temuan lama tidak disentuh."""
    detail = {"error": type(exc).__name__, "message": str(exc)[:200]}
    with store.database(db_path) as conn:
        if previous:
            summary = {**store.loads(previous["summary_json"], {}), "last_error": detail}
            conn.execute("UPDATE analyses SET status = 'failed', input_hash = '', summary_json = ?, created_at = ? "
                         "WHERE product_id = ?", (store.dumps(summary), store.now(), product_id))
        else:
            conn.execute("INSERT INTO analyses(product_id, status, summary_json, trace_json, created_at, "
                         "pipeline_version, verifier_version) VALUES(?, 'failed', ?, '[]', ?, ?, ?)",
                         (product_id, store.dumps({"last_error": detail}), store.now(), PIPELINE_VERSION,
                          VERIFIER_VERSION))


def _evidence_items(ids_quotes: dict[str, dict], reviews_by_id: dict[str, dict]) -> list[dict]:
    items = []
    for rid, value in ids_quotes.items():
        review = reviews_by_id.get(rid, {})
        items.append({"review_id": rid, "quote": value.get("quote", ""), "rating": review.get("rating"),
                      "review_time": review.get("review_time"), "variant": review.get("variant", ""),
                      "has_photo": bool(store.loads(review.get("images_json"), []))})
    items.sort(key=lambda i: (i["review_time"] or ""), reverse=True)
    return items


def _persist(conn, product: dict, user: dict, reviews: list[dict], findings: list[dict], engine: str,
             input_hash: str) -> list[str]:
    now = store.now()
    pid = product["id"]
    by_id = {r["id"]: r for r in reviews}
    existing = {f["id"]: f for f in store.rows(conn.execute("SELECT * FROM findings WHERE product_id = ?", (pid,)))}
    seen: list[str] = []
    for f in findings:
        fid = finding_id(pid, f["key"])
        seen.append(fid)
        p, judged, metrics = f["proposal"], f["judged"], f["metrics"]
        items = _evidence_items({rid: judged["supports"][rid] for rid in f["support_ids"]}, by_id)
        contra = _evidence_items(judged["contradicting"], by_id)
        rejected = [{"review_id": rid, "reason": reason} for rid, reason in judged["rejected"].items()]
        rejected += [{"review_id": rid, "reason": reason} for rid, reason in judged["uncertain"].items()]
        values = {
            "attribute": p.get("attribute", ""), "attribute_key": f["key"],
            "attribute_local": p.get("attribute_local", ""), "finding_type": p["finding_type"],
            "fix_type": p.get("fix_type", ""), "severity": f["severity"],
            "buyer_expectation": p.get("buyer_expectation", ""), "merchant_question": p.get("merchant_question", ""),
            "listing_check_json": store.dumps(f["listing_check"]),
            "evidence_json": write_evidence(items, contra, len(judged["uncertain"]), metrics),
            "rejected_json": store.dumps(rejected), "support": metrics["support"],
            "denominator": metrics["denominator"], "candidates_read": metrics["candidates_read"],
            "contradicting": metrics["contradicting"], "engine": engine, "analysis_hash": input_hash,
            "updated_at": now,
        }
        if fid in existing:
            sets = ", ".join(f"{k} = ?" for k in values)
            conn.execute(f"UPDATE findings SET {sets}, not_detected_at = NULL WHERE id = ?", (*values.values(), fid))
        else:
            cols = ", ".join(["id", "product_id", "state", "created_at", *values])
            marks = ", ".join("?" for _ in range(4 + len(values)))
            conn.execute(f"INSERT INTO findings({cols}) VALUES({marks})", (fid, pid, "open", now, *values.values()))
        _after_save(conn, product, user, fid, existing.get(fid), metrics, items, p)
    # Rekonsiliasi: analisis sukses (termasuk hasil kosong) menandai temuan yang tidak muncul lagi.
    for fid, old in existing.items():
        if fid not in seen and old["not_detected_at"] is None:
            conn.execute("UPDATE findings SET not_detected_at = ?, updated_at = ? WHERE id = ?", (now, now, fid))
    return seen


def latest_acted_at(conn, fid: str) -> str | None:
    found = conn.execute("SELECT acted_at FROM decisions WHERE finding_id = ? AND decision = 'acted' "
                         "ORDER BY id DESC LIMIT 1", (fid,)).fetchone()
    return found["acted_at"] if found else None


def follow_up(items: list[dict], reviews: list[dict], acted_at: str | None) -> dict | None:
    """Dihitung, tidak disimpan. Hanya ulasan yang DITULIS setelah tindakan yang dihitung."""
    acted = store.parse_time(acted_at)
    if acted is None:
        return None
    after = [r for r in reviews if (store.parse_time(r.get("review_time")) or acted) > acted]
    undated = sum(1 for r in reviews if not r.get("review_time"))
    support_ids = {i["review_id"] for i in items}
    complaints = sum(1 for r in after if r["id"] in support_ids)
    state = "insufficient_data" if not after else ("recurrence" if complaints else "no_recurrence_observed")
    return {"state": state, "acted_at": acted_at, "after": len(after), "complaints": complaints, "undated": undated}


def _alerts():
    try:
        from .. import alerts  # noqa: PLC0415

        return alerts
    except ImportError:
        return None


def _after_save(conn, product, user, fid, old, metrics, items, proposal) -> None:
    """Reopen otomatis dan alert isu baru. Pesan alert hanya metadata, tanpa teks ulasan."""
    alerts = _alerts()
    synthetic = product.get("data_origin") == "synthetic" or bool(user.get("is_demo"))
    payload = {"product": product["title"], "product_id": product["id"],
               "attribute_local": proposal.get("attribute_local") or proposal.get("attribute", ""),
               "total": metrics["candidates_read"]}
    state = old["state"] if old else "open"
    if state == "acted":
        acted_at = latest_acted_at(conn, fid)
        acted = store.parse_time(acted_at)
        new_after = [i for i in items if acted and (store.parse_time(i.get("review_time")) or acted) > acted]
        if new_after:
            conn.execute("UPDATE findings SET state = 'reopened', updated_at = ? WHERE id = ?", (store.now(), fid))
            if alerts:
                alerts.enqueue_event(product["user_id"], "reopened", finding_id=fid,
                                     payload={**payload, "count": len(new_after)}, synthetic=synthetic,
                                     version=store.digest(sorted(i["review_id"] for i in new_after))[:16], conn=conn)
        return
    if state in ACTIVE_STATES and alerts:
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        recent = [i for i in items if (store.parse_time(i.get("review_time")) or cutoff) > cutoff]
        high_gap = (proposal.get("finding_type") in LISTING_FIXABLE and metrics["support"] >= 3)
        if len(recent) >= 3 or high_gap:
            alerts.enqueue_event(product["user_id"], "new_issue", finding_id=fid,
                                 payload={**payload, "count": metrics["support"]}, synthetic=synthetic,
                                 version="new", conn=conn)
