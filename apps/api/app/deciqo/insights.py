"""Read model investigasi: angka, urutan, dan deduplikasi bukti dihitung di server."""
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends

from . import store
from .auth import current_user
from .engine import decision, pipeline, workspace

router = APIRouter(prefix="/api/v1/deciqo", tags=["deciqo-insights"])


def filter_items(items, q="", channel="", kind="", severity="", status="", order="priority"):
    needle = q.casefold().strip()
    out = [i for i in items if (not needle or needle in " ".join(str(i.get(k, "")) for k in
           ("product_title", "title", "attribute", "attribute_local")).casefold())
           and (not channel or i.get("channel") == channel)
           and (not kind or i.get("finding_type") == kind)
           and (not severity or i.get("severity") == severity)
           and (not status or i.get("bucket", i.get("analysis_status")) == status or
                (status == "stale" and i.get("stale")))]
    if order == "reviews":
        out.sort(key=lambda i: -i.get("support", i.get("reviews", 0)))
    elif order == "share":
        out.sort(key=lambda i: -(i.get("support", 0) / i["denominator"] if i.get("denominator") else 0))
    elif order == "recent":
        out.sort(key=lambda i: i.get("updated_at", i.get("analysed_at")) or "", reverse=True)
    elif order == "product":
        out.sort(key=lambda i: i.get("product_title", i.get("title", "")).casefold())
    return out


@router.get("/overview")
def overview(days: Literal["7", "30", "90"] = "30", user: dict = Depends(current_user)):
    with store.database() as conn:
        return overview_data(conn, user["id"], int(days))


def overview_data(conn, user_id, days=30, now=None):
    now = now or datetime.now(timezone.utc)
    today = now.date()
    start = today - timedelta(days=days-1)
    before = start - timedelta(days=days)
    items = workspace.inbox(conn, user_id)
    open_items = [i for i in items if i["bucket"] in workspace.OPEN_BUCKETS]
    evidence_reviews = {}
    for item in items:
        finding = store.row(conn.execute("SELECT * FROM findings WHERE id = ?", (item["id"],)))
        blob = pipeline.read_evidence(finding["evidence_json"])
        if item["bucket"] not in {"dismissed", "not_detected"}:
            for evidence in blob["items"]:
                key = (item["product_id"], evidence["review_id"])
                review = store.row(conn.execute("SELECT * FROM reviews WHERE product_id=? AND id=? AND deleted_at IS NULL", key))
                if review:
                    evidence_reviews[key] = review
    ranked = decision.plan(conn, user_id)
    by_id = {item["id"]: item for item in items}
    plan = []
    for row in ranked["decisions"]:
        drivers = {driver["key"]: driver for driver in row["drivers"]}
        reach = drivers["reach"]
        plan.append({**by_id[row["finding_id"]], "share": reach["share"],
                     "confidence_low": reach["confident_share"],
                     "hidden_high_star": drivers.get("hidden", {}).get("n", 0),
                     "estimated_minutes": drivers["effort"]["minutes"],
                     "score": row["score"], "next_step": row["next_step"], "drivers": row["drivers"]})
    current, previous, undated, ratings, affected = Counter(), 0, 0, [], set()
    for review in evidence_reviews.values():
        date = store.parse_time(review["review_time"])
        if not date:
            undated += 1
            continue
        day = date.date()
        if start <= day <= today:
            current[day.isoformat()] += 1
            affected.add(review["product_id"])
            if review["rating"]:
                ratings.append(review["rating"])
        elif before <= day < start:
            previous += 1
    series = [{"date": (start+timedelta(days=index)).isoformat(),
               "count": current[(start+timedelta(days=index)).isoformat()]} for index in range(days)]
    by_channel = Counter(i["channel"] for i in open_items)
    by_type = Counter(i["finding_type"] for i in open_items)
    candidates, matches = [], []
    for group in ranked["patterns"]:
        rows = [item for item in open_items if item["product_id"] in group["product_ids"]]
        if rows:
            candidates.append({"label": rows[0]["attribute_local"], "items": rows})
    for group in ranked["cross_channel"]:
        rows = [item for item in open_items if item["product_id"] in group["product_ids"]]
        if rows:
            matches.append({"label": rows[0]["product_title"], "items": rows})
    return {"days": days, "series": series, "total": sum(current.values()), "previous": previous,
            "delta": sum(current.values())-previous, "undated": undated, "affected_products": len(affected),
            "average_rating": round(sum(ratings)/len(ratings), 2) if ratings else None,
            "open": len(open_items), "plan": plan,
            "ranking_channels": [{"key": k, "count": n} for k,n in sorted(by_channel.items(), key=lambda row:(-row[1],row[0]))],
            "ranking_types": [{"key": k, "count": n} for k,n in sorted(by_type.items(), key=lambda row:(-row[1],row[0]))],
            "one_fix_candidates": candidates, "same_product_candidates": matches,
            "heuristic": ranked["score_kind"], "scope": "unique_review_product_pairs_in_current_findings"}
