"""Rencana keputusan: urutan isu yang layak diurus dulu, dengan alasan yang terlihat.

Ini heuristik yang bisa dijelaskan, bukan optimum atau prediksi profit. Setiap angka dihitung dari
ulasan tersimpan; menit usaha adalah konstanta per langkah, bukan waktu terukur. Skala dari units
sold adalah ilustrasi berlabel asumsi, tidak dijumlahkan antar isu, dan bukan rupiah.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timedelta, timezone

from .. import store
from . import pipeline, workspace

# Menit per langkah berikutnya. Konstanta, bukan pengukuran.
EFFORT_MINUTES = {"paste_listing": 2, "review_draft": 3, "edit_listing": 8, "confirm_fact": 10,
                  "change_process": 30, "talk_to_supplier": 45}
TREND_DAYS = 90
SIMILAR_TITLE = 0.5


def next_step(view: dict) -> str:
    step = view.get("next")
    if step == "paste_listing":
        return "paste_listing"
    if step == "draft":
        return "review_draft"
    if step == "apply":
        return "edit_listing"
    if step in {"fact", "recurrence"} and view["finding_type"] in pipeline.LISTING_FIXABLE:
        return "confirm_fact"
    return "talk_to_supplier" if view["finding_type"] == "product_quality" else "change_process"


def trend(items: list[dict], reviews: list[dict], now: datetime | None = None) -> dict | None:
    """Rasio keluhan 90 hari terakhir vs sebelumnya, hanya ulasan bertanggal."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=TREND_DAYS)
    support = {i["review_id"] for i in items}
    recent = [r for r in reviews if (t := store.parse_time(r.get("review_time"))) and t >= cutoff]
    before = [r for r in reviews if (t := store.parse_time(r.get("review_time"))) and t < cutoff]
    if not recent or not before:
        return None
    share_recent = sum(r["id"] in support for r in recent) / len(recent)
    share_before = sum(r["id"] in support for r in before) / len(before)
    direction = "rising" if share_recent > share_before * 1.5 and share_recent > 0 else (
        "falling" if share_recent < share_before * 0.5 else "flat")
    return {"recent": round(share_recent, 3), "before": round(share_before, 3), "direction": direction}


def _score(view: dict, reviews: list[dict], units_sold: int | None) -> tuple[float, list[dict]]:
    m = view["metrics"]
    support, read = m.get("support", 0), m.get("candidates_read") or m.get("denominator") or 0
    confident = pipeline.wilson_lower(support, read)
    drivers = [{"key": "reach", "support": support, "share": round(m.get("share", 0), 3),
                "confident_share": round(confident, 3)}]
    impact = confident * 100 + min(support, 30) * 1.5
    if m.get("hidden_high_star"):
        impact += m["hidden_high_star"] * 3
        drivers.append({"key": "hidden", "n": m["hidden_high_star"]})
    tr = trend(view["evidence"], reviews)
    if tr and tr["direction"] != "flat":
        impact += 12 if tr["direction"] == "rising" else -6
        drivers.append({"key": tr["direction"], "recent": tr["recent"], "before": tr["before"]})
    if view["bucket"] == "recurrence":
        impact += 15
        drivers.append({"key": "recurrence"})
    if units_sold:
        impact += math.log10(1 + units_sold) * 2
        drivers.append({"key": "units", "units_sold": units_sold,
                        "illustrative_buyers": round(units_sold * m.get("share", 0)), "assumption": True})
    if support <= 1:
        impact *= 0.3
        drivers.append({"key": "single_report"})
    step = next_step(view)
    minutes = EFFORT_MINUTES[step]
    drivers.append({"key": "effort", "step": step, "minutes": minutes, "measured": False})
    return round(max(impact, 0) / math.sqrt(minutes), 1), drivers


def _title_tokens(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", title.lower()) if len(w) > 2}


def _similarity(a: str, b: str) -> float:
    x, y = _title_tokens(a), _title_tokens(b)
    return len(x & y) / len(x | y) if x | y else 0.0


def plan(conn, user_id: int) -> dict:
    products = store.rows(conn.execute("SELECT * FROM products WHERE user_id = ?", (user_id,)))
    decisions = []
    by_key: dict[str, set[str]] = {}
    for product in products:
        rows = store.rows(conn.execute("SELECT * FROM findings WHERE product_id = ?", (product["id"],)))
        if not rows:
            continue
        ctx = workspace.ProductContext(conn, product)
        for finding in rows:
            view = ctx.finding_view(finding, full=True)
            if view["bucket"] not in workspace.OPEN_BUCKETS:
                continue
            by_key.setdefault(finding["attribute_key"], set()).add(product["id"])
            score, drivers = _score(view, ctx.reviews, product.get("units_sold"))
            decisions.append({
                "finding_id": finding["id"], "product_id": product["id"], "product_title": product["title"],
                "channel": product["channel"], "attribute_local": finding["attribute_local"],
                "bucket": view["bucket"], "next_step": next_step(view), "score": score, "drivers": drivers,
                "example": view["evidence"][0]["quote"] if view["evidence"] else "",
            })
    decisions.sort(key=lambda d: -d["score"])
    # "One fix, many listings": atribut yang sama di beberapa produk. Kandidat untuk dicek.
    patterns = [{"attribute_key": key, "products": len(ids), "product_ids": sorted(ids), "kind": "candidate"}
                for key, ids in by_key.items() if len(ids) > 1]
    # Produk mirip di channel berbeda (kemiripan judul >= 0,5). Kandidat, bukan identitas SKU.
    cross = []
    for i, a in enumerate(products):
        for b in products[i + 1:]:
            if a["channel"] != b["channel"] and (sim := _similarity(a["title"], b["title"])) >= SIMILAR_TITLE:
                cross.append({"product_ids": [a["id"], b["id"]], "channels": [a["channel"], b["channel"]],
                              "similarity": round(sim, 2), "kind": "candidate"})
    return {"decisions": decisions, "total": len(decisions), "patterns": patterns, "cross_channel": cross,
            "score_kind": "heuristic"}
