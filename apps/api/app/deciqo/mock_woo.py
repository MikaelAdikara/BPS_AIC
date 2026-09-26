"""Toko WooCommerce sintetis untuk demo (service `woo-demo`).

Meniru potongan REST `wc/v3` yang dibaca konektor (produk dan ulasan, dengan paginasi dan
autentikasi key), sehingga jalur klien yang sama dipakai untuk toko nyata. Semua isi toko ini
sintetis dan diberi label begitu di aplikasi.

Endpoint demo tambahan:
- `POST /demo/reviews`  menambah ulasan (bertanggal sekarang) agar isu bisa muncul lagi di depan juri
- `POST /demo/reset`    menghapus ulasan tambahan
- `POST /bot<token>/sendMessage` + `GET /demo/telegram/messages`  sink Telegram simulasi
"""

from __future__ import annotations

import math
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from . import demo_catalog, settings

app = FastAPI(title="Deciqo synthetic Woo store", docs_url=None, redoc_url=None)

_lock = threading.Lock()
_started = datetime.now(timezone.utc)


def _db() -> sqlite3.Connection:
    path = Path(os.getenv("DECIQO_MOCK_DB_PATH") or Path(__file__).resolve().parents[3] / "tmp" / "woo-demo.sqlite3")
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE IF NOT EXISTS extra_reviews (id INTEGER PRIMARY KEY, product_id INTEGER, "
                 "rating INTEGER, review TEXT, date_created_gmt TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS telegram (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, "
                 "text TEXT, created_at TEXT)")
    return conn


def _gmt(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).replace(tzinfo=None, microsecond=0).isoformat()


def _check_auth(request: Request) -> None:
    key = request.query_params.get("consumer_key")
    secret = request.query_params.get("consumer_secret")
    header = request.headers.get("authorization", "")
    if header.lower().startswith("basic "):
        import base64  # noqa: PLC0415

        try:
            key, _, secret = base64.b64decode(header[6:]).decode().partition(":")
        except ValueError:
            key = secret = None
    if key != settings.DEMO_WOO_KEY or secret != settings.DEMO_WOO_SECRET:
        raise HTTPException(401, {"code": "woocommerce_rest_cannot_view", "message": "Sorry, you cannot list resources."})


def _page(items: list, request: Request, response: Response) -> list:
    try:
        page = max(1, int(request.query_params.get("page", "1")))
        per_page = max(1, min(100, int(request.query_params.get("per_page", "10"))))
    except ValueError:
        page, per_page = 1, 10
    response.headers["X-WP-Total"] = str(len(items))
    response.headers["X-WP-TotalPages"] = str(max(1, math.ceil(len(items) / per_page)))
    return items[(page - 1) * per_page: page * per_page]


def _products() -> list[dict]:
    return [{
        "id": p["id"], "name": p["name"], "sku": p["sku"], "status": "publish",
        "permalink": f"https://woo-demo.deciqo.app/product/{p['sku'].lower()}",
        "description": f"<p>{p['description']}</p>", "short_description": "",
        "price": p["price"], "total_sales": 0, "attributes": p["attributes"], "images": [],
    } for p in demo_catalog.PRODUCTS]


def _reviews() -> list[dict]:
    items = []
    for product in demo_catalog.PRODUCTS:
        for rid, rating, days, _variant, text in product["reviews"]:
            items.append({
                "id": rid, "product_id": product["id"], "status": "approved", "rating": rating,
                "review": f"<p>{text}</p>",
                "date_created_gmt": _gmt(datetime.fromisoformat(demo_catalog.review_time(days, _started))),
            })
    with _lock:
        conn = _db()
        for row in conn.execute("SELECT * FROM extra_reviews ORDER BY id"):
            items.append({"id": row["id"], "product_id": row["product_id"], "status": "approved",
                          "rating": row["rating"], "review": f"<p>{row['review']}</p>",
                          "date_created_gmt": row["date_created_gmt"]})
        conn.close()
    return items


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "synthetic": True}


@app.get("/wp-json/wc/v3/products")
def products(request: Request, response: Response) -> list:
    _check_auth(request)
    return _page(_products(), request, response)


@app.get("/wp-json/wc/v3/products/reviews")
def reviews(request: Request, response: Response) -> list:
    _check_auth(request)
    items = _reviews()
    product = request.query_params.get("product")
    if product:
        items = [r for r in items if str(r["product_id"]) == product]
    return _page(items, request, response)


class DemoReview(BaseModel):
    product_id: int
    text: str = Field(min_length=1, max_length=2000)
    rating: int = Field(ge=1, le=5)


@app.post("/demo/reviews", status_code=201)
def add_review(body: DemoReview) -> dict:
    if body.product_id not in {p["id"] for p in demo_catalog.PRODUCTS}:
        raise HTTPException(404, "unknown product")
    with _lock:
        conn = _db()
        next_id = 9000 + conn.execute("SELECT COUNT(*) FROM extra_reviews").fetchone()[0] + 1
        conn.execute("INSERT INTO extra_reviews(id, product_id, rating, review, date_created_gmt) VALUES(?, ?, ?, ?, ?)",
                     (next_id, body.product_id, body.rating, body.text, _gmt(datetime.now(timezone.utc))))
        conn.commit()
        conn.close()
    return {"id": next_id}


@app.post("/demo/reset")
def reset() -> dict:
    with _lock:
        conn = _db()
        removed = conn.execute("DELETE FROM extra_reviews").rowcount
        conn.execute("DELETE FROM telegram")
        conn.commit()
        conn.close()
    return {"removed": removed}


class TelegramMessage(BaseModel):
    chat_id: str | int
    text: str
    parse_mode: str | None = None
    reply_markup: dict | None = None


@app.post("/bot{token}/sendMessage")
def telegram_send(token: str, body: TelegramMessage) -> dict:
    with _lock:
        conn = _db()
        cur = conn.execute("INSERT INTO telegram(chat_id, text, created_at) VALUES(?, ?, ?)",
                           (str(body.chat_id), body.text, _gmt(datetime.now(timezone.utc))))
        conn.commit()
        message_id = cur.lastrowid
        conn.close()
    return {"ok": True, "result": {"message_id": message_id, "simulated": True}}


@app.get("/demo/telegram/messages")
def telegram_messages() -> dict:
    with _lock:
        conn = _db()
        rows = [dict(r) for r in conn.execute("SELECT * FROM telegram ORDER BY id DESC LIMIT 50")]
        conn.close()
    return {"messages": rows}
