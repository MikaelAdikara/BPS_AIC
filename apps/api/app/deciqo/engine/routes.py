"""Endpoint engine: katalog, analisis, temuan, fakta, draf, keputusan, dan read model.

Setiap endpoint memeriksa kepemilikan; data akun lain dijawab 404, bukan 403.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from .. import analysis, ingest, jobs, store
from ..auth import current_user
from ..errors import DeciqoError, not_found
from . import decision, draft, facts, generic, vision, workspace

router = APIRouter(prefix="/api/v1/deciqo", tags=["deciqo-engine"])

DISMISS_REASONS = {"false_positive", "not_relevant", "wont_fix"}


def _own_product(conn, user_id: int, product_id: str) -> dict:
    product = store.row(conn.execute("SELECT * FROM products WHERE id = ? AND user_id = ?", (product_id, user_id)))
    if product is None:
        raise not_found("product")
    return product


def _own_finding(conn, user_id: int, finding_id: str) -> tuple[dict, dict]:
    finding = store.row(conn.execute(
        "SELECT f.* FROM findings f JOIN products p ON p.id = f.product_id WHERE f.id = ? AND p.user_id = ?",
        (finding_id, user_id)))
    if finding is None:
        raise not_found("issue")
    product = store.row(conn.execute("SELECT * FROM products WHERE id = ?", (finding["product_id"],)))
    return finding, product


def _analyse_job(user_id: int, product_ids: list[str], *, force: bool, kind: str, target: str) -> str:
    return jobs.start(user_id, kind, lambda ctx: analysis.analyse_products(ctx, product_ids, force=force),
                      target=target)


# --- read model ------------------------------------------------------------------------------


@router.get("/channels")
def get_channels(user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        return {"channels": workspace.channels(conn, user["id"])}


@router.get("/summary")
def get_summary(user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        return workspace.summary(conn, user["id"])


@router.get("/inbox")
def get_inbox(q: str = Query(default="", max_length=300), channel: str = "", kind: str = "", severity: str = "",
              status: str = "", order: Literal["priority", "reviews", "share", "recent", "product"] = "priority",
              user: dict = Depends(current_user)) -> dict:
    from ..insights import filter_items
    with store.database() as conn:
        return {"items": filter_items(workspace.inbox(conn, user["id"]), q, channel, kind, severity, status, order)}


@router.get("/decisions")
def get_decisions(user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        return decision.plan(conn, user["id"])


@router.get("/ledger")
def get_ledger(user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        return workspace.ledger(conn, user["id"])


# --- katalog & analisis ---------------------------------------------------------------------


@router.get("/products")
def list_products(q: str = Query(default="", max_length=300), channel: str = "", status: str = "",
                  order: Literal["priority", "reviews", "recent", "product"] = "priority",
                  user: dict = Depends(current_user)) -> dict:
    from ..insights import filter_items
    with store.database() as conn:
        return {"products": filter_items(workspace.products(conn, user["id"]), q=q, channel=channel, status=status, order=order)}


@router.get("/products/{product_id}")
def get_product(product_id: str, user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        return workspace.product_view(conn, _own_product(conn, user["id"], product_id))


class ListingBody(BaseModel):
    listing: str = Field(max_length=20000)


@router.put("/products/{product_id}/listing")
def put_listing(product_id: str, body: ListingBody, user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        _own_product(conn, user["id"], product_id)
        changed = ingest.set_listing(conn, product_id, body.listing)
    job_id = _analyse_job(user["id"], [product_id], force=False, kind="analyse", target=product_id) if changed else None
    with store.database() as conn:
        view = workspace.product_view(conn, _own_product(conn, user["id"], product_id))
    return {**view, "job_id": job_id}


class AnalyseBody(BaseModel):
    force: bool = False


@router.post("/products/{product_id}/analyse", status_code=202)
def analyse_product(product_id: str, body: AnalyseBody | None = None, user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        _own_product(conn, user["id"], product_id)
    force = bool(body and body.force)
    return {"job_id": _analyse_job(user["id"], [product_id], force=force, kind="analyse", target=product_id)}


@router.post("/analyse-all", status_code=202)
def analyse_all(user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        ids = [r["id"] for r in conn.execute("SELECT id FROM products WHERE user_id = ? ORDER BY title", (user["id"],))]
    return {"job_id": _analyse_job(user["id"], ids, force=False, kind="analyse_all", target="all")}


@router.post("/products/{product_id}/vision")
def run_vision(product_id: str, user: dict = Depends(current_user)) -> dict:
    """OCR gambar produk + cek foto pembeli untuk produk ini, lalu read model terbaru.

    Vision hanya menambah bukti. Tanpa key / anggaran habis: bagian itu `skipped` dengan alasan,
    bukan error. Bila teks gambar berubah, listing yang diperiksa ikut berubah, jadi analisis
    ulang dijalankan sebagai job (`job_id`); tanpa perubahan `job_id` bernilai null."""
    with store.database() as conn:
        _own_product(conn, user["id"], product_id)
    result = vision.run_all(product_id)
    job_id = (_analyse_job(user["id"], [product_id], force=False, kind="analyse", target=product_id)
              if result["ocr"].get("changed") else None)
    with store.database() as conn:
        view = workspace.product_view(conn, _own_product(conn, user["id"], product_id))
    return {**view, "vision_run": result, "job_id": job_id}


@router.post("/products/{product_id}/draft")
def make_draft(product_id: str, user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        _own_product(conn, user["id"], product_id)
        return draft.build(conn, product_id)


@router.post("/products/{product_id}/generic")
def make_generic(product_id: str, user: dict = Depends(current_user)) -> dict:
    """Pembanding chatbot umum dengan bundle dan pemeriksa yang sama (lihat engine/generic.py)."""
    with store.database() as conn:
        _own_product(conn, user["id"], product_id)
    return generic.run(product_id)


# --- fakta & keputusan -----------------------------------------------------------------------


class FactBody(BaseModel):
    value: str = Field(max_length=500)
    unit: str = Field(default="", max_length=20)
    variant: str = Field(default="", max_length=60)


@router.post("/findings/{finding_id}/fact")
def post_fact(finding_id: str, body: FactBody, user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        finding, _ = _own_finding(conn, user["id"], finding_id)
        return facts.save(conn, finding, body.value, body.unit, body.variant, user_id=user["id"])


class DecisionBody(BaseModel):
    decision: Literal["acted", "dismissed", "reopened"]
    note: str = Field(default="", max_length=1000)
    reason: str = Field(default="", max_length=40)


@router.post("/findings/{finding_id}/decision")
def post_decision(finding_id: str, body: DecisionBody, user: dict = Depends(current_user)) -> dict:
    note = body.note.strip()
    if body.decision == "acted" and not note:
        raise DeciqoError(422, "note_required", "Write what you changed before marking this as applied.")
    if body.decision == "dismissed" and body.reason not in DISMISS_REASONS:
        raise DeciqoError(422, "reason_required", "Choose why you are dismissing this issue.")
    now = store.now()
    with store.database() as conn:
        finding, product = _own_finding(conn, user["id"], finding_id)
        conn.execute("INSERT INTO decisions(finding_id, decision, reason, note, acted_at, created_at) "
                     "VALUES(?, ?, ?, ?, ?, ?)",
                     (finding_id, body.decision, body.reason if body.decision == "dismissed" else "", note,
                      now if body.decision == "acted" else None, now))
        state = body.decision
        if body.decision == "reopened":
            # Dibuka lagi manual bukan "muncul lagi": kembali ke kerja aktif, bukan bucket recurrence.
            state = "investigating" if facts.active_fact(conn, finding_id) else "open"
        conn.execute("UPDATE findings SET state = ?, updated_at = ? WHERE id = ?", (state, now, finding_id))
        finding = store.row(conn.execute("SELECT * FROM findings WHERE id = ?", (finding_id,)))
        return workspace.ProductContext(conn, product).finding_view(finding, full=True)
