"""Read model investigasi: angka, urutan, dan deduplikasi bukti dihitung di server."""
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends

from . import store
from .auth import current_user
from .errors import DeciqoError
from .engine import decision, lexicon, pipeline, workspace

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
        out.sort(key=lambda i: -(i.get("support", 0) / (i.get("candidates_read") or i.get("denominator"))
                                if (i.get("candidates_read") or i.get("denominator")) else 0))
    elif order == "recent":
        out.sort(key=lambda i: i.get("updated_at", i.get("analysed_at")) or "", reverse=True)
    elif order == "product":
        out.sort(key=lambda i: i.get("product_title", i.get("title", "")).casefold())
    return out


def landscape(conn, user_id, items, start, today, evidence_by_channel):
    """Bahan peta dan grafik per kanal: volume ulasan harian, sebaran bintang, dan simpul produk-isu.

    Semua angka dihitung dari ulasan aktif akun ini saja; tidak ada nilai yang ditebak untuk
    ulasan tanpa tanggal atau tanpa bintang."""
    products = store.rows(conn.execute(
        "SELECT p.id, p.title, p.channel, p.image_url, COUNT(r.id) AS reviews, AVG(r.rating) AS rating "
        "FROM products p LEFT JOIN reviews r ON r.product_id = p.id AND r.deleted_at IS NULL "
        "WHERE p.user_id = ? GROUP BY p.id ORDER BY p.title", (user_id,)))
    volume, ratings, window_ratings = Counter(), {}, {}
    for row in store.rows(conn.execute(
            "SELECT p.channel, r.rating, r.review_time FROM reviews r JOIN products p ON p.id = r.product_id "
            "WHERE p.user_id = ? AND r.deleted_at IS NULL", (user_id,))):
        stars = row["rating"] if row["rating"] in (1, 2, 3, 4, 5) else None
        if stars:
            ratings.setdefault(row["channel"], [0] * 5)[stars - 1] += 1
        date = store.parse_time(row["review_time"])
        if date and start <= date.date() <= today:
            volume[(date.date().isoformat(), row["channel"])] += 1
            if stars:
                window_ratings.setdefault(row["channel"], [0] * 5)[stars - 1] += 1
    channels = sorted({p["channel"] for p in products})
    days = [(start + timedelta(days=i)).isoformat() for i in range((today - start).days + 1)]
    nodes = [{"id": i["id"], "product_id": i["product_id"], "product_title": i["product_title"],
              "channel": i["channel"], "attribute": i["attribute"], "attribute_local": i["attribute_local"],
              "finding_type": i["finding_type"], "severity": i["severity"], "bucket": i["bucket"],
              "support": i.get("support", 0), "denominator": i.get("denominator", 0),
              "aspect": _aspect(i["attribute"], i["attribute_local"])}
             for i in items if i["bucket"] not in {"dismissed", "not_detected"}]
    return {
        "channels": channels,
        "volume_by_channel": [{"date": d, **{c: volume[(d, c)] for c in channels}} for d in days],
        "evidence_by_channel": [{"date": d, **{c: evidence_by_channel[(d, c)] for c in channels}} for d in days],
        "ratings_by_channel": ratings, "ratings_window_by_channel": window_ratings,
        "map": {"products": [{**p, "rating": round(p["rating"], 2) if p["rating"] is not None else None}
                             for p in products], "findings": nodes},
    }


def _aspect(attribute, attribute_local):
    groups = sorted(lexicon.attribute_groups(attribute, attribute_local))
    return groups[0] if groups else "other"


# Rentang eksplisit paling panjang; "Semua" dibatasi terpisah agar seri harian tetap wajar.
MAX_SPAN_DAYS = 730
ALL_MAX_DAYS = 1825


def _day(value: str | None, field: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise DeciqoError(422, "invalid_range", f"{field} must be a date in YYYY-MM-DD form.") from None


def oldest_review_day(conn, user_id) -> date | None:
    days = [t.date() for row in conn.execute(
        "SELECT r.review_time FROM reviews r JOIN products p ON p.id = r.product_id "
        "WHERE p.user_id = ? AND r.deleted_at IS NULL AND r.review_time IS NOT NULL", (user_id,))
        if (t := store.parse_time(row[0]))]
    return min(days) if days else None


def resolve_range(conn, user_id, days=None, start=None, end=None, all_time=False, today=None):
    """Rentang inklusif (start, end, all). `days` lama tetap berlaku bila start/end/all kosong.

    Akhir rentang dipotong ke hari ini; "Semua" dimulai dari ulasan bertanggal tertua akun ini."""
    today = today or datetime.now(timezone.utc).date()
    first, last = _day(start, "start"), _day(end, "end")
    last = min(last or today, today)
    if all_time:
        oldest = oldest_review_day(conn, user_id) if conn is not None else None
        first = max(min(oldest or last, last), last - timedelta(days=ALL_MAX_DAYS - 1))
        return first, last, True
    if first is None:
        first = last - timedelta(days=int(days or 30) - 1)
    if first > last:
        raise DeciqoError(422, "invalid_range", "The end date must be on or after the start date.")
    if (last - first).days + 1 > MAX_SPAN_DAYS:
        raise DeciqoError(422, "invalid_range", f"A range can cover at most {MAX_SPAN_DAYS} days.")
    return first, last, False


@router.get("/overview")
def overview(days: Literal["7", "30", "90"] | None = None, start: str | None = None,
             end: str | None = None, all: bool = False, user: dict = Depends(current_user)):
    with store.database() as conn:
        if not (start or end or all):
            return overview_data(conn, user["id"], int(days or 30))
        first, last, everything = resolve_range(conn, user["id"], days, start, end, all)
        return overview_data(conn, user["id"], start=first, end=last, all_time=everything)


def overview_data(conn, user_id, days=30, now=None, start=None, end=None, all_time=False):
    now = now or datetime.now(timezone.utc)
    today = end or now.date()
    start = start or today - timedelta(days=days-1)
    days = (today - start).days + 1
    before = start - timedelta(days=days)
    items = workspace.inbox(conn, user_id)
    open_items = [i for i in items if i["bucket"] in workspace.OPEN_BUCKETS]
    evidence_reviews, in_range = {}, set()
    for item in items:
        finding = store.row(conn.execute("SELECT * FROM findings WHERE id = ?", (item["id"],)))
        blob = pipeline.read_evidence(finding["evidence_json"])
        if item["bucket"] not in {"dismissed", "not_detected"}:
            for evidence in blob["items"]:
                key = (item["product_id"], evidence["review_id"])
                review = store.row(conn.execute("SELECT * FROM reviews WHERE product_id=? AND id=? AND deleted_at IS NULL", key))
                if review:
                    evidence_reviews[key] = review
                    stamp = store.parse_time(review["review_time"])
                    if stamp and start <= stamp.date() <= today:
                        in_range.add(item["id"])
    channel_of = {p["id"]: p["channel"] for p in store.rows(conn.execute(
        "SELECT id, channel FROM products WHERE user_id = ?", (user_id,)))}
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
    # Pola berulang: temuan terbuka dengan bukti bertanggal di rentang ini. "Semua" tidak memfilter,
    # sehingga temuan yang buktinya tanpa tanggal tetap terhitung.
    def group(rows, label, attribute):
        return {"label": label, "attribute": attribute, "items": rows,
                "products": len({r["product_id"] for r in rows}),
                "reviews": sum(r.get("support", 0) for r in rows)}
    def patterns(ranged: bool) -> list[dict]:
        out = []
        for pattern in ranked["patterns"]:
            rows = [item for item in open_items if item["product_id"] in pattern["product_ids"]
                    and conn.execute("SELECT attribute_key FROM findings WHERE id=?", (item["id"],)).fetchone()[0]
                    == pattern["attribute_key"] and (not ranged or item["id"] in in_range)]
            if len({r["product_id"] for r in rows}) > 1:
                out.append(group(rows, rows[0]["attribute_local"], rows[0]["attribute"]))
        return out

    # Pola lintas produk jarang punya bukti di jendela pendek; bila rentang kosong, pakai semua ulasan
    # tersimpan dan beri tahu lewat patterns_scope supaya kartunya tidak hilang diam-diam.
    candidates = patterns(ranged=not all_time)
    patterns_scope = "all" if all_time else "range"
    if not candidates and not all_time:
        candidates, patterns_scope = patterns(ranged=False), "all"
    matches = []
    for pair in ranked["cross_channel"]:
        rows = [item for item in open_items if item["product_id"] in pair["product_ids"]]
        if rows:
            matches.append(group(rows, rows[0]["product_title"], rows[0]["product_title"]))
    evidence_by_channel = Counter()
    for (product_id, _), review in evidence_reviews.items():
        date = store.parse_time(review["review_time"])
        if date and start <= date.date() <= today:
            evidence_by_channel[(date.date().isoformat(), channel_of.get(product_id, ""))] += 1
    return {**landscape(conn, user_id, items, start, today, evidence_by_channel),
            "days": days, "range": {"start": start.isoformat(), "end": today.isoformat(), "days": days,
                                     "all": bool(all_time)},
            "patterns_scope": patterns_scope, "series": series, "total": sum(current.values()), "previous": previous,
            "delta": sum(current.values())-previous, "undated": undated, "affected_products": len(affected),
            "average_rating": round(sum(ratings)/len(ratings), 2) if ratings else None,
            "open": len(open_items), "plan": plan,
            "ranking_channels": [{"key": k, "count": n} for k,n in sorted(by_channel.items(), key=lambda row:(-row[1],row[0]))],
            "ranking_types": [{"key": k, "count": n} for k,n in sorted(by_type.items(), key=lambda row:(-row[1],row[0]))],
            "one_fix_candidates": candidates, "same_product_candidates": matches,
            "heuristic": ranked["score_kind"], "scope": "unique_review_product_pairs_in_current_findings"}
