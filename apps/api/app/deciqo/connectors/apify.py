"""Lazada lewat Apify (actor bayar per hasil).

Halaman Lazada menolak sebagian besar request otomatis, jadi pengambilan dilakukan actor Apify
dengan proxy residensial. Biaya dijaga dua lapis: `maxTotalChargeUsd` per run, dan anggaran
server `DECIQO_APIFY_BUDGET_USD` yang dihitung dari ledger (provider `apify`). Tanpa token,
fetch live dinonaktifkan dengan alasan yang jelas; snapshot bertanggal di `data/` tetap bisa dimuat.

Nama/handle reviewer tidak pernah disalin ke katalog.
"""

from __future__ import annotations

import html
import logging
import re
import time
from urllib.parse import urlparse

import httpx

from .. import settings, store
from ..errors import DeciqoError
from .woo import clean_html

log = logging.getLogger("deciqo.lazada")

API = "https://api.apify.com/v2"
ACTOR = "lergassy~lazada-scraper"
MAX_URLS = 12
# Satu run melayani paling banyak sekian URL; lebih dari itu dipecah supaya tidak kena batas waktu.
URLS_PER_RUN = 4
MAX_CHARGE_PER_RUN = 1.0
REVIEWS_PER_PRODUCT = 30
RUN_WAIT_SECONDS = 240

_PRODUCT_PATH = re.compile(r"^/products/[\w%.\-]*-i(\d+)(?:-s\d+)?\.html$")
_LAZADA_HOST = re.compile(r"^(?:www\.)?lazada\.(?:co\.id|com\.my|sg|co\.th|vn|com\.ph)$")


def product_item_id(url: str) -> str:
    """Id item Lazada dari URL produk, atau 422 `not_lazada_url`."""
    parsed = urlparse((url or "").strip())
    match = _PRODUCT_PATH.match(parsed.path or "")
    if parsed.scheme != "https" or not _LAZADA_HOST.match(parsed.hostname or "") or not match:
        raise DeciqoError(422, "not_lazada_url",
                          "Use a Lazada product link like https://www.lazada.co.id/products/...-i123.html.")
    return match.group(1)


def spent_usd(conn) -> float:
    return conn.execute(
        "SELECT COALESCE(SUM(MAX(cost_usd, reserved_usd)), 0) FROM ledger WHERE provider = 'apify'").fetchone()[0]


GALLERY_FIELDS = ("images", "imageUrls", "gallery", "galleryImages", "imageList")
MAX_GALLERY = 7


def gallery(item: dict) -> list[str]:
    """Galeri gambar produk dari record actor (nama field berbeda antar versi actor)."""
    urls: list[str] = []
    for name in GALLERY_FIELDS:
        values = item.get(name)
        for value in values if isinstance(values, list) else []:
            if isinstance(value, dict):
                value = value.get("url") or value.get("src") or value.get("image")
            if not isinstance(value, str):
                continue
            url = value.strip()
            if url.startswith("//"):
                url = "https:" + url
            if url.lower().startswith(("http://", "https://")) and url not in urls and url != item.get("imageUrl"):
                urls.append(url)
    return urls[:MAX_GALLERY]


def to_catalog(items: list[dict]) -> list[dict]:
    """Keluaran actor (record product_detail + review) ke bentuk `ingest.upsert_catalog`."""
    reviews: dict[str, list[dict]] = {}
    seen_reviews: set[str] = set()
    for item in items:
        if item.get("type") != "review" or str(item.get("reviewId")) in seen_reviews:
            continue
        seen_reviews.add(str(item.get("reviewId")))
        text = (item.get("text") or "").strip()
        reviews.setdefault(str(item.get("itemId")), []).append({
            "id": str(item.get("reviewId")),
            "rating": item.get("rating"),
            "text": text,
            "variant": item.get("variant") or "",
            "review_time": item.get("reviewTime"),
            "images": [u for u in (item.get("images") or []) if isinstance(u, str)][:6],
        })
    catalog = []
    seen_products: set[str] = set()
    for item in items:
        if item.get("type") != "product_detail" or str(item.get("itemId")) in seen_products:
            continue
        item_id = str(item.get("itemId"))
        seen_products.add(item_id)
        specs = {}
        raw_specs = item.get("specs")
        if isinstance(raw_specs, list):
            for spec in raw_specs:
                if isinstance(spec, dict) and spec.get("name"):
                    specs[spec["name"]] = str(spec.get("value", ""))
        elif isinstance(raw_specs, dict):
            specs = {k: str(v) for k, v in raw_specs.items()}
        variants = []
        for variant in item.get("variants") or []:
            values = [f"{v.get('name')}: {v.get('value')}" for v in (variant.get("values") or []) if isinstance(v, dict)]
            if values:
                variants.append(", ".join(values))
        # `description` kadang berisi HTML yang di-escape ("&lt;html&gt;...") atau kerangka HTML kosong;
        # di-unescape dulu supaya tag ikut dibuang dan listing kosong tetap terbaca kosong.
        description = (clean_html(item.get("descriptionHtml"))
                       or clean_html(html.unescape(item.get("description") or "")))
        highlights = item.get("highlights")
        if isinstance(highlights, list) and highlights:
            description = (" ".join(str(h) for h in highlights) + "\n" + description).strip()
        catalog.append({
            "source_item_id": item_id,
            "title": item.get("title") or "",
            "url": item.get("url") or "",
            "description": description,
            "specs": specs,
            "variants": variants[:30],
            "image_url": item.get("imageUrl"),
            "images": gallery(item),
            "price": _float(item.get("price") or item.get("currentPrice")),
            "units_sold": _int(item.get("sold") or item.get("itemSold")),
            "captured_at": item.get("scrapedAt"),
            "reviews": reviews.get(item_id, []),
        })
    return catalog


def _float(value) -> float | None:
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _int(value) -> int | None:
    digits = re.sub(r"[^\d]", "", str(value or ""))
    return int(digits) if digits else None


def run_actor(payload: dict, *, max_charge: float, user_id: int | None, ref: str,
              client: httpx.Client | None = None) -> list[dict]:
    """Jalankan actor sampai selesai dan kembalikan item dataset. Biaya dicatat di ledger."""
    tokens = settings.apify_tokens()
    if not tokens:
        raise DeciqoError(503, "fetch_unconfigured", "Live Lazada fetch is not configured on this server.")
    http = client or httpx.Client(timeout=httpx.Timeout(RUN_WAIT_SECONDS + 30, connect=10))
    started = time.monotonic()
    last_error = "fetch_failed"
    for token in tokens:
        headers = {"Authorization": f"Bearer {token}"}
        with store.database() as conn:
            cur = conn.execute(
                "INSERT INTO ledger(user_id, provider, purpose, model, status, reserved_usd, ref, created_at) "
                "VALUES(?, 'apify', 'lazada_fetch', ?, 'reserved', ?, ?, ?)",
                (user_id, ACTOR, max_charge, ref, store.now()))
            ledger_id = cur.lastrowid
        try:
            response = http.post(
                f"{API}/acts/{ACTOR}/runs", headers=headers, json=payload,
                params={"memory": 1024, "timeout": RUN_WAIT_SECONDS, "waitForFinish": RUN_WAIT_SECONDS,
                        "maxTotalChargeUsd": round(max_charge, 2)})
            if response.status_code in (401, 402, 403):
                last_error = "fetch_token_rejected"
                _close_ledger(ledger_id, "rejected", 0.0, started)
                continue
            response.raise_for_status()
            run = response.json()["data"]
            run = _wait(http, headers, run)
            # Biaya final baru lengkap sesaat setelah run berhenti; baca ulang sekali.
            run = http.get(f"{API}/actor-runs/{run['id']}", headers=headers).json().get("data", run)
            cost = float(run.get("usageTotalUsd") or 0.0)
            items = http.get(f"{API}/datasets/{run['defaultDatasetId']}/items", headers=headers,
                             params={"clean": "true", "format": "json"}).json()
            items = items if isinstance(items, list) else []
            if run.get("status") != "SUCCEEDED" and not items:
                _close_ledger(ledger_id, f"run_{str(run.get('status')).lower()}", cost, started)
                raise DeciqoError(502, "fetch_failed", "Lazada fetch did not finish. Try again or load the dated snapshot.")
            # Run yang berhenti karena batas waktu tetap menyimpan item yang sudah diambil;
            # dipakai apa adanya dan ditandai `partial` di ledger.
            _close_ledger(ledger_id, "ok" if run.get("status") == "SUCCEEDED" else "partial", cost, started)
            return items
        except httpx.HTTPError as exc:
            # Tanpa angka biaya dari Apify, reservasi tetap dihitung (bukan nol).
            _close_ledger(ledger_id, f"unknown:{type(exc).__name__}", None, started)
            last_error = "fetch_failed"
            log.warning(f"apify gagal: {type(exc).__name__}")
    raise DeciqoError(502, last_error, "Lazada fetch failed. Load the dated snapshot instead.")


def _wait(http: httpx.Client, headers: dict, run: dict) -> dict:
    deadline = time.monotonic() + RUN_WAIT_SECONDS
    while run.get("status") in ("READY", "RUNNING") and time.monotonic() < deadline:
        time.sleep(5)
        run = http.get(f"{API}/actor-runs/{run['id']}", headers=headers).json()["data"]
    return run


def _close_ledger(ledger_id: int, status: str, cost: float | None, started: float) -> None:
    with store.database() as conn:
        if cost is None:
            conn.execute("UPDATE ledger SET status = ?, latency_ms = ? WHERE id = ?",
                         (status, int((time.monotonic() - started) * 1000), ledger_id))
        else:
            conn.execute("UPDATE ledger SET status = ?, cost_usd = ?, reserved_usd = 0, latency_ms = ? WHERE id = ?",
                         (status, cost, int((time.monotonic() - started) * 1000), ledger_id))


def fetch_products(urls: list[str], *, user_id: int | None, reviews_per_product: int = REVIEWS_PER_PRODUCT,
                   client: httpx.Client | None = None) -> list[dict]:
    """Ambil listing + ulasan untuk URL produk Lazada, dalam batas anggaran server."""
    if not urls:
        raise DeciqoError(422, "not_lazada_url", "Add at least one Lazada product link.")
    if len(urls) > MAX_URLS:
        raise DeciqoError(422, "too_many_urls", f"Fetch at most {MAX_URLS} products at a time.")
    clean = []
    for url in urls:
        product_item_id(url)
        clean.append(url.strip().split("?")[0])
    with store.database() as conn:
        remaining = settings.apify_budget_usd() - spent_usd(conn)
    if remaining <= 0.05:
        raise DeciqoError(402, "fetch_budget_exhausted", "The Lazada fetch budget on this server is used up.")
    items: list[dict] = []
    for start in range(0, len(clean), URLS_PER_RUN):
        batch = clean[start:start + URLS_PER_RUN]
        with store.database() as conn:
            remaining = settings.apify_budget_usd() - spent_usd(conn)
        if remaining <= 0.05:
            break
        payload = {"mode": "product_reviews", "startUrls": batch, "maxReviewsPerProduct": reviews_per_product,
                   "enrichProducts": True, "reviewsRating": "all"}
        items += run_actor(payload, max_charge=min(MAX_CHARGE_PER_RUN, remaining), user_id=user_id,
                           ref=",".join(product_item_id(u) for u in batch), client=client)
    return to_catalog(items)
