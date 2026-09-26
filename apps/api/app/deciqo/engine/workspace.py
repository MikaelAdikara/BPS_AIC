"""Read model: satu sumber angka untuk web, Telegram, dan eval.

Bucket, langkah berikutnya, urutan inbox, status draf, dan tindak lanjut diturunkan di sini dari
data tersimpan. Frontend hanya menampilkan; ia tidak menghitung share, severity, atau urutan.
"""

from __future__ import annotations

from .. import ingest, settings, store
from . import draft, facts, lexicon, llm, pipeline, vision

BUCKET_ORDER = ["recurrence", "needs_fact", "to_do", "monitoring", "dismissed", "not_detected"]
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
OPEN_BUCKETS = {"recurrence", "needs_fact", "to_do"}


def engine_mode() -> str:
    return "ai" if llm.available()[0] else "rules"


def bucket_of(finding: dict, has_fact: bool, listing_provided: bool, draft_status: str | None = None) -> str:
    state = finding["state"]
    if state == "reopened":
        return "recurrence"
    if state == "acted":
        return "monitoring"
    if state == "dismissed":
        return "dismissed"
    if finding.get("not_detected_at"):
        return "not_detected"
    if listing_provided and not has_fact and draft_status == "needs_merchant_fact":
        # Mengikuti gerbang draf: apa pun yang ditahan draf karena menunggu merchant ada di sini,
        # sehingga inbox tidak menyuruh "tulis draf" untuk isu yang drafnya sedang ditahan.
        return "needs_fact"
    return "to_do"


def next_step(bucket: str, finding: dict, draft_status: str | None, listing_provided: bool) -> str | None:
    if bucket == "recurrence":
        return "recurrence"
    if bucket == "needs_fact":
        return "fact"
    if bucket == "monitoring":
        return "monitoring"
    if bucket != "to_do":
        return None
    if finding["finding_type"] not in pipeline.LISTING_FIXABLE:
        return "route"
    if not listing_provided:
        return "paste_listing"
    return "apply" if draft_status == "ready" else "draft"


class ProductContext:
    """Data satu produk yang dipakai berulang saat merakit banyak temuan."""

    def __init__(self, conn, product: dict):
        self.product = product
        self.listing, self.provided = pipeline.listing_parts(product)
        self.reviews = pipeline.load_reviews(conn, product["id"])
        self.reviews_by_id = {r["id"]: r for r in self.reviews}
        self.conn = conn
        # Hasil cek foto pembeli (vision) dimuat sekali per produk; hanya menambah bukti.
        self.vision_checks = vision.load_checks(conn, product)
        self.vision_state = vision.run_state(product)

    def finding_view(self, finding: dict, full: bool = False) -> dict:
        conn = self.conn
        fact_row = facts.active_fact(conn, finding["id"])
        evidence = pipeline.read_evidence(finding["evidence_json"])
        metrics = evidence["metrics"] or {"support": finding["support"], "denominator": finding["denominator"],
                                          "candidates_read": finding["candidates_read"],
                                          "support_is_minimum": finding["candidates_read"] < finding["denominator"]}
        fixable = finding["finding_type"] in pipeline.LISTING_FIXABLE
        section = (draft.section(finding, fact_row, self.listing, self.provided,
                                 store.loads(finding["listing_check_json"], {})) if fixable else None)
        draft_status = section["status"] if section else None
        bucket = bucket_of(finding, bool(fact_row), self.provided, draft_status)
        acted_at = pipeline.latest_acted_at(conn, finding["id"]) if finding["state"] in {"acted", "reopened"} else None
        follow = pipeline.follow_up(evidence["items"], self.reviews, acted_at) if acted_at else None
        base = {
            "id": finding["id"], "product_id": self.product["id"], "attribute": finding["attribute"],
            "attribute_local": finding["attribute_local"], "finding_type": finding["finding_type"],
            "fix_type": finding["fix_type"], "severity": finding["severity"], "state": finding["state"],
            "bucket": bucket, "next": next_step(bucket, finding, draft_status, self.provided),
            "engine": finding["engine"], "listing_fixable": fixable,
            "needs_fact": draft_status == "needs_merchant_fact",
            "needs_listing": fixable and not self.provided, "fact": facts.public(fact_row),
            "draft_status": draft_status, "updated_at": finding["updated_at"], "follow_up": follow,
            "acted_at": acted_at,
        }
        if not full:
            return {**base, "product_title": self.product["title"], "channel": self.product["channel"],
                    "synthetic": self.product["data_origin"] == "synthetic", "image_url": self.product.get("image_url"),
                    "support": metrics.get("support", finding["support"]),
                    "denominator": metrics.get("denominator", finding["denominator"]),
                    "candidates_read": metrics.get("candidates_read", finding["candidates_read"]),
                    "support_is_minimum": metrics.get("support_is_minimum", False),
                    "example": evidence["items"][0]["quote"] if evidence["items"] else ""}
        groups = lexicon.attribute_groups(finding["attribute"], finding["attribute_local"])
        items, vision_summary = vision.enrich(finding, evidence["items"], self.reviews_by_id, self.vision_checks,
                                              self.vision_state, self.product.get("user_id"))
        return {
            **base,
            "buyer_expectation": finding["buyer_expectation"], "merchant_question": finding["merchant_question"],
            "needs_measurement": "size" in groups or "battery" in groups,
            "listing_check": store.loads(finding["listing_check_json"], {}) or {"status": "pending"},
            "metrics": metrics, "evidence": items, "vision_summary": vision_summary,
            "contradicting": evidence["contradicting"],
            "rejected": [r for r in store.loads(finding["rejected_json"], []) if r.get("reason")],
            "uncertain": evidence["uncertain"],
            "not_detected_at": finding["not_detected_at"],
        }


def _sort_key(item: dict):
    return (BUCKET_ORDER.index(item["bucket"]), SEVERITY_ORDER.get(item["severity"], 3), -item.get("support", 0))


def _products(conn, user_id: int) -> list[dict]:
    return store.rows(conn.execute("SELECT * FROM products WHERE user_id = ? ORDER BY title", (user_id,)))


def inbox(conn, user_id: int) -> list[dict]:
    items = []
    for product in _products(conn, user_id):
        rows = store.rows(conn.execute("SELECT * FROM findings WHERE product_id = ?", (product["id"],)))
        if not rows:
            continue
        ctx = ProductContext(conn, product)
        items.extend(ctx.finding_view(f) for f in rows)
    items.sort(key=_sort_key)
    return items


def summary(conn, user_id: int) -> dict:
    items = inbox(conn, user_id)
    buckets = {b: 0 for b in BUCKET_ORDER}
    for item in items:
        buckets[item["bucket"]] += 1
    reviews = conn.execute(
        "SELECT COUNT(*) FROM reviews r JOIN products p ON p.id = r.product_id "
        "WHERE p.user_id = ? AND r.deleted_at IS NULL", (user_id,)).fetchone()[0]
    return {"products": len(_products(conn, user_id)), "reviews": reviews,
            "findings_open": sum(buckets[b] for b in OPEN_BUCKETS), "buckets": buckets,
            "top": [i for i in items if i["bucket"] in OPEN_BUCKETS][:3], "engine": engine_mode()}


def channels(conn, user_id: int) -> list[dict]:
    sources = {s["channel"]: s for s in store.rows(conn.execute("SELECT * FROM sources WHERE user_id = ?", (user_id,)))}
    counts = {r["channel"]: r for r in store.rows(conn.execute(
        "SELECT p.channel, COUNT(DISTINCT p.id) AS products, "
        "MAX(CASE WHEN p.data_origin = 'synthetic' THEN 1 ELSE 0 END) AS synthetic, "
        "SUM(p.units_sold) AS units_sold, GROUP_CONCAT(DISTINCT p.sampling) AS samplings "
        "FROM products p WHERE p.user_id = ? GROUP BY p.channel", (user_id,)))}
    review_counts = {r["channel"]: r["n"] for r in store.rows(conn.execute(
        "SELECT p.channel, COUNT(*) AS n FROM reviews r JOIN products p ON p.id = r.product_id "
        "WHERE p.user_id = ? AND r.deleted_at IS NULL GROUP BY p.channel", (user_id,)))}
    active: dict[str, int] = {}
    for item in inbox(conn, user_id):
        if item["bucket"] in OPEN_BUCKETS:
            active[item["channel"]] = active.get(item["channel"], 0) + 1
    out = []
    for channel in sorted(set(sources) | set(counts), key=lambda c: ingest.CHANNELS.index(c) if c in ingest.CHANNELS else 99):
        source = sources.get(channel, {})
        count = counts.get(channel, {})
        connected = channel == "woocommerce" and bool(conn.execute(
            "SELECT 1 FROM woo_connections WHERE user_id = ?", (user_id,)).fetchone())
        out.append({
            "key": channel, "label": source.get("label") or ingest.CHANNEL_LABEL.get(channel, channel),
            "mode": ingest.CHANNEL_KIND.get(channel, "import"),
            "connected": connected if channel == "woocommerce" else bool(count),
            "synthetic": bool(count.get("synthetic")), "status": source.get("status") or "no_data",
            "last_success_at": source.get("last_success_at"), "last_error": source.get("last_error"),
            "products": count.get("products", 0), "reviews": review_counts.get(channel, 0),
            "active_findings": active.get(channel, 0),
            # Jumlah unit terjual yang diketahui (None bila tidak satu produk pun membawanya) dan
            # cara ulasan diambil; keduanya menentukan boleh tidaknya proyeksi pembeli terdampak.
            "units_sold": count.get("units_sold"),
            "samplings": sorted(filter(None, (count.get("samplings") or "").split(","))),
        })
    return out


def _analysis(conn, product_id: str) -> dict | None:
    return store.row(conn.execute("SELECT * FROM analyses WHERE product_id = ?", (product_id,)))


def _stale(conn, product: dict, analysis: dict | None) -> bool:
    if not analysis or analysis["status"] != "ready":
        return True
    if (product.get("updated_at") or "") > (analysis["created_at"] or ""):
        return True
    return bool(conn.execute(
        "SELECT 1 FROM reviews WHERE product_id = ? AND (created_at > ? OR fetched_at > ?) AND triage_json IS NULL LIMIT 1",
        (product["id"], analysis["created_at"], analysis["created_at"])).fetchone())


def products(conn, user_id: int) -> list[dict]:
    out = []
    for p in _products(conn, user_id):
        stats = conn.execute("SELECT COUNT(*) AS n, AVG(rating) AS avg FROM reviews WHERE product_id = ? "
                             "AND deleted_at IS NULL", (p["id"],)).fetchone()
        rows = store.rows(conn.execute("SELECT finding_type, state, not_detected_at FROM findings WHERE product_id = ?",
                                       (p["id"],)))
        active = [f for f in rows if f["state"] in pipeline.ACTIVE_STATES and not f["not_detected_at"]]
        analysis = _analysis(conn, p["id"])
        out.append({"id": p["id"], "title": p["title"], "channel": p["channel"], "data_origin": p["data_origin"],
                    "synthetic": p["data_origin"] == "synthetic", "captured_at": p["captured_at"],
                    "image_url": p.get("image_url"),
                    "reviews": stats["n"], "rating": round(stats["avg"], 2) if stats["avg"] else None,
                    "findings": len(active),
                    "fixable": sum(1 for f in active if f["finding_type"] in pipeline.LISTING_FIXABLE),
                    "analysed_at": analysis["created_at"] if analysis else None,
                    "engine": analysis["engine"] if analysis else None,
                    "analysis_status": analysis["status"] if analysis else "pending",
                    "stale": _stale(conn, p, analysis)})
    return out


def product_view(conn, product: dict) -> dict:
    ctx = ProductContext(conn, product)
    rows = store.rows(conn.execute("SELECT * FROM findings WHERE product_id = ?", (product["id"],)))
    views = sorted((ctx.finding_view(f, full=True) for f in rows),
                   key=lambda v: (BUCKET_ORDER.index(v["bucket"]), SEVERITY_ORDER.get(v["severity"], 3),
                                  -v["metrics"].get("support", 0)))
    current = [v for v in views if v["bucket"] != "not_detected"]
    not_detected = [{"id": v["id"], "attribute_local": v["attribute_local"], "updated_at": v["updated_at"]}
                    for v in views if v["bucket"] == "not_detected"]
    ratings = [r["rating"] for r in ctx.reviews if r.get("rating")]
    hist = {str(i): sum(1 for r in ratings if r == i) for i in range(1, 6)}
    analysis = _analysis(conn, product["id"])
    source = store.row(conn.execute("SELECT status, last_success_at FROM sources WHERE user_id = ? AND channel = ?",
                                    (product["user_id"], product["channel"]))) or {}
    decisions = store.rows(conn.execute(
        "SELECT d.finding_id, d.decision, d.reason, d.note, d.acted_at, d.created_at FROM decisions d "
        "JOIN findings f ON f.id = d.finding_id WHERE f.product_id = ? ORDER BY d.id DESC", (product["id"],)))
    summary_json = store.loads(analysis["summary_json"], {}) if analysis else {}
    stored_generic = store.row(conn.execute(
        "SELECT result_json FROM generic_drafts WHERE product_id = ? ORDER BY created_at DESC LIMIT 1", (product["id"],)))
    stored_draft = store.row(conn.execute(
        "SELECT result_json FROM drafts WHERE product_id = ? ORDER BY created_at DESC LIMIT 1", (product["id"],)))
    return {
        "product": {"id": product["id"], "title": product["title"], "channel": product["channel"],
                    "url": product["url"], "listing_text": ctx.listing, "listing_edit_text": product.get("description") or "",
                    "listing_provided": ctx.provided,
                    "data_origin": product["data_origin"], "captured_at": product["captured_at"],
                    "synthetic": product["data_origin"] == "synthetic", "image_url": product.get("image_url"),
                    "images": vision.product_images(product), "image_ocr": vision.ocr_view(product)},
        "source": {"status": source.get("status"), "last_success_at": source.get("last_success_at")},
        "stats": {"reviews": len(ctx.reviews), "rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                  "rating_hist": hist,
                  "with_photos": sum(1 for r in ctx.reviews if store.loads(r.get("images_json"), []))},
        "analysis": {"engine": analysis["engine"], "status": analysis["status"], "created_at": analysis["created_at"],
                     "pipeline_version": analysis["pipeline_version"], "verifier_version": analysis["verifier_version"],
                     "note": summary_json.get("engine_note") or "", "error": (summary_json.get("last_error") or {}).get("error"),
                     "trace": store.loads(analysis["trace_json"], [])} if analysis else
                    {"engine": None, "status": "pending", "created_at": None, "trace": []},
        "findings": current,
        "not_detected": not_detected,
        "draft": store.loads(stored_draft["result_json"], None) if stored_draft else None,
        "generic_draft": store.loads(stored_generic["result_json"], None) if stored_generic else None,
        "decisions": decisions,
        "reviews": [{"id": r["id"], "rating": r["rating"], "text": r["text"], "variant": r["variant"],
                     "review_time": r["review_time"], "images": vision.review_images(r)} for r in ctx.reviews],
    }


def ledger(conn, user_id: int) -> dict:
    calls = store.rows(conn.execute(
        "SELECT id, provider, purpose, model, status, input_tokens, cached_tokens, output_tokens, cost_usd, "
        "reserved_usd, ref, latency_ms, created_at FROM ledger WHERE user_id = ? ORDER BY id DESC LIMIT 200", (user_id,)))
    by_purpose = store.rows(conn.execute(
        "SELECT provider, purpose, COUNT(*) AS calls, ROUND(SUM(CASE WHEN status = 'ok' THEN cost_usd ELSE 0 END), 6) AS cost_usd, "
        "ROUND(SUM(CASE WHEN status != 'ok' THEN reserved_usd ELSE 0 END), 6) AS unconfirmed_usd "
        "FROM ledger WHERE user_id = ? GROUP BY provider, purpose", (user_id,)))
    return {"calls": calls, "by_purpose": by_purpose, "budget_usd": settings.ai_budget_usd()}
