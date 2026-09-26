"""Endpoint sumber data: Woo, impor, contoh, sinkron, job, status, dan reset/hapus workspace.

Operasi yang bisa lama (sinkron, impor + analisis, reset) mengembalikan `202 {job_id}`; klien
mem-poll `GET /jobs/{id}`. Hasil job impor/sinkron memuat statistik impor yang dihitung dari baris
yang benar-benar tersimpan.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from . import alerts, analysis, demo_catalog, importers, ingest, jobs, samples, settings, store
from .auth import current_user
from .connectors import apify, woo
from .errors import DeciqoError, not_found

log = logging.getLogger("deciqo.sources")

router = APIRouter(prefix="/api/v1/deciqo", tags=["deciqo-sources"])

MARKETPLACE_DIR = Path(__file__).resolve().parents[4] / "data" / "marketplace"
LIVE_INTERVAL_SECONDS = 8


def _accepted(job_id: str, **extra) -> dict:
    return {"job_id": job_id, **extra}


# --- Woo --------------------------------------------------------------------------------


class WooConnectBody(BaseModel):
    mode: str = Field(pattern="^(demo|local|own|server)$")
    base_url: str | None = Field(default=None, max_length=300)
    consumer_key: str | None = Field(default=None, max_length=200)
    consumer_secret: str | None = Field(default=None, max_length=200)


def _woo_connection(conn, user_id: int) -> dict | None:
    return store.row(conn.execute("SELECT * FROM woo_connections WHERE user_id = ?", (user_id,)))


def public_source(conn, user_id: int, channel: str) -> dict:
    source = store.row(conn.execute("SELECT * FROM sources WHERE id = ?", (f"{user_id}:{channel}",)))
    if not source:
        return {"channel": channel, "status": "not_checked", "label": ingest.CHANNEL_LABEL.get(channel, channel),
                "last_success_at": None, "last_error": None}
    return {"channel": channel, "status": source["status"], "label": source["label"],
            "last_success_at": source["last_success_at"], "last_error": source["last_error"],
            "consecutive_failures": source["consecutive_failures"]}


@router.post("/woo/connect")
def woo_connect(body: WooConnectBody, user: dict = Depends(current_user)) -> dict:
    if body.mode == "demo":
        base_url, key, secret, is_demo = settings.woo_base_url(), settings.DEMO_WOO_KEY, settings.DEMO_WOO_SECRET, 1
        if not settings.woo_demo_mode():
            raise DeciqoError(409, "demo_store_disabled", "The demo store is turned off on this server.")
    elif body.mode == "local":
        # Toko WordPress demo lokal: WooCommerce asli, isinya data demo buatan tim.
        if not settings.woo_demo_mode():
            raise DeciqoError(409, "demo_store_disabled", "The demo store is turned off on this server.")
        base_url, key, secret, is_demo = (settings.woo_local_url(), settings.woo_local_user(),
                                          settings.woo_local_api_password(), 1)
    elif body.mode == "server":
        base_url, key, secret = settings.woo_base_url(), settings.woo_consumer_key(), settings.woo_consumer_secret()
        is_demo = int(woo.is_demo_url(base_url))
    else:
        if not (body.base_url and body.consumer_key and body.consumer_secret):
            raise DeciqoError(422, "store_fields_required", "Enter the store address, consumer key and consumer secret.")
        base_url, key, secret, is_demo = body.base_url, body.consumer_key.strip(), body.consumer_secret.strip(), 0
    base_url = woo.validate_store_url(base_url)
    if not is_demo:
        is_demo = int(woo.is_demo_url(base_url))
    # Coba satu request sebelum menyimpan: key salah ditolak di sini, bukan di sinkron pertama.
    try:
        woo.WooClient(base_url, key, secret)._get("/products", {"per_page": 1})
    except woo.WooError as exc:
        if exc.code == "store_auth_failed":
            raise DeciqoError(401, "store_auth_failed", "The store rejected this key. Use a key with Read access.") from exc
        raise DeciqoError(422, exc.code, exc.message) from exc
    with store.database() as conn:
        conn.execute(
            "INSERT INTO woo_connections(user_id, base_url, consumer_key, consumer_secret, is_demo, created_at) "
            "VALUES(?, ?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET base_url = excluded.base_url, "
            "consumer_key = excluded.consumer_key, consumer_secret = excluded.consumer_secret, is_demo = excluded.is_demo",
            (user["id"], base_url, key, secret, is_demo, store.now()),
        )
        ingest.touch_source(conn, user["id"], "woocommerce", ok=True, label=_woo_label(base_url, bool(is_demo)))
        return {**public_source(conn, user["id"], "woocommerce"), "synthetic": bool(is_demo),
                "base_url": base_url, "local": woo.is_local_url(base_url)}


def _woo_label(base_url: str, is_demo: bool) -> str:
    if woo.is_local_url(base_url):
        return "WooCommerce (local demo store)"
    return "WooCommerce (synthetic demo store)" if is_demo else "WooCommerce"


@router.delete("/woo/connect", status_code=204)
def woo_disconnect(user: dict = Depends(current_user)) -> Response:
    with store.database() as conn:
        conn.execute("DELETE FROM woo_connections WHERE user_id = ?", (user["id"],))
        conn.execute("UPDATE sources SET status = 'disconnected' WHERE id = ?", (f"{user['id']}:woocommerce",))
    return Response(status_code=204)


def sync_woo(ctx: jobs.JobContext | None, user_id: int, *, analyse: bool = True) -> dict:
    """Sinkron penuh dari toko Woo akun ini, lalu analisis produk yang berubah."""
    with store.database() as conn:
        connection = _woo_connection(conn, user_id)
    if not connection:
        raise jobs.JobFailed("store_not_connected", "Connect a WooCommerce store first.")
    if ctx:
        ctx.progress(stage="fetching")
    # Toko lokal selalu memakai kredensial terbaru dari env: kunci demo bisa diganti setelah
    # akun tersambung, dan baris sambungan lama tidak boleh membuat sinkron gagal autentikasi.
    client = (_local_client() if woo.is_local_url(connection["base_url"]) else
              woo.WooClient(connection["base_url"], connection["consumer_key"], connection["consumer_secret"]))
    try:
        catalog = client.catalog()
    except (woo.WooError, DeciqoError) as exc:
        code = getattr(exc, "code", "store_unavailable")
        message = getattr(exc, "message", None) or "The store could not be reached."
        with store.database() as conn:
            ingest.touch_source(conn, user_id, "woocommerce", ok=False, error=message,
                                status="unavailable" if code == "store_auth_failed" else None)
            source = store.row(conn.execute("SELECT * FROM sources WHERE id = ?", (f"{user_id}:woocommerce",)))
        alerts.on_source_problem(user_id, "woocommerce", code, source.get("consecutive_failures", 1),
                                 synthetic=bool(connection["is_demo"]))
        raise jobs.JobFailed(code, message) from exc
    if ctx:
        ctx.progress(stage="saving")
    origin = "synthetic" if connection["is_demo"] else "channel"
    # Sinkron penuh membaca semua ulasan yang disetujui, jadi sampelnya lengkap.
    stats = ingest.upsert_catalog(user_id, "woocommerce", catalog, data_origin=origin, full_sync=True,
                                  sampling="complete")
    result = {"stats": stats.public(), "products": len(stats.products)}
    if analyse:
        result["analysis"] = analysis.analyse_products(ctx, stats.changed_products)
    return result


@router.post("/woo/sync", status_code=202)
def woo_sync(user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        if not _woo_connection(conn, user["id"]):
            raise DeciqoError(409, "store_not_connected", "Connect a WooCommerce store first.")
    return _accepted(jobs.start(user["id"], "sync_analyse", lambda ctx: sync_woo(ctx, user["id"]), target="woo"))


def _local_client() -> woo.WooClient:
    return woo.WooClient(settings.woo_local_url(), settings.woo_local_user(), settings.woo_local_api_password())


@router.get("/woo/local")
def woo_local_status(user: dict = Depends(current_user)) -> dict:
    """Apakah toko WordPress demo lokal menyala, dan apakah akun ini tersambung ke sana."""
    reachable = False
    if settings.woo_demo_mode():
        try:
            _local_client()._get("/products", {"per_page": 1})
            reachable = True
        except (woo.WooError, DeciqoError):
            reachable = False
    with store.database() as conn:
        connection = _woo_connection(conn, user["id"])
    public = settings.woo_local_public_url()
    return {"reachable": reachable, "connected": bool(connection and woo.is_local_url(connection["base_url"])),
            "storefront_url": public, "admin_url": f"{public}/wp-admin/edit-comments.php?comment_type=review"}


# --- webhook WooCommerce ------------------------------------------------------------------
#
# Webhook bawaan WooCommerce (topik `action.comment_post` dkk.) memanggil endpoint ini setiap ada
# ulasan baru/diubah. Isi webhook tidak dipercaya sebagai data: ia hanya memicu sinkron penuh
# lewat REST, jalur yang sama dengan tombol Sync, sehingga data tetap dibaca dari sumbernya.

_webhook_lock = threading.Lock()
_webhook_running: set[int] = set()
_webhook_again: set[int] = set()


def _valid_signature(body: bytes, signature: str) -> bool:
    expected = base64.b64encode(hmac.new(settings.woo_webhook_secret().encode(), body, hashlib.sha256).digest())
    return hmac.compare_digest(expected.decode(), signature.strip())


def _webhook_users(source: str) -> list[int]:
    """Akun yang tersambung ke toko pengirim: toko lokal (webhook-nya kita pasang sendiri) atau
    toko yang host-nya sama dengan header `X-WC-Webhook-Source`."""
    source_host = urlparse(source or "").hostname
    with store.database() as conn:
        rows = store.rows(conn.execute("SELECT user_id, base_url FROM woo_connections"))
    return [r["user_id"] for r in rows
            if woo.is_local_url(r["base_url"]) or (source_host and urlparse(r["base_url"]).hostname == source_host)]


def queue_webhook_sync(user_id: int) -> str | None:
    """Sinkron karena webhook. Ulasan yang masuk saat sinkron berjalan tidak hilang: sinkron
    diulang sekali lagi setelah selesai, bukan dijalankan paralel."""
    with _webhook_lock:
        if user_id in _webhook_running:
            _webhook_again.add(user_id)
            return None
        _webhook_running.add(user_id)

    def run(ctx):
        rounds = []
        try:
            while True:
                result = sync_woo(ctx, user_id)
                rounds.append(result["stats"])
                with _webhook_lock:
                    if user_id not in _webhook_again:
                        _webhook_running.discard(user_id)
                        break
                    _webhook_again.discard(user_id)
            return {"trigger": "webhook", "rounds": len(rounds), "stats": rounds[-1],
                    "analysis": result.get("analysis")}
        except BaseException:
            with _webhook_lock:
                _webhook_running.discard(user_id)
                _webhook_again.discard(user_id)
            raise

    try:
        return jobs.start(user_id, "woo_webhook", run, target="woo")
    except DeciqoError:
        # Workspace sedang penuh; poller terjadwal tetap akan membaca ulasan ini.
        with _webhook_lock:
            _webhook_running.discard(user_id)
        return None


@router.post("/woo/webhook", status_code=202)
async def woo_webhook(request: Request) -> dict:
    body = await request.body()
    signature = request.headers.get("x-wc-webhook-signature")
    if not signature:
        # Ping aktivasi WooCommerce (`webhook_id=...`) tidak bertanda tangan dan tidak memicu apa pun.
        if body.startswith(b"webhook_id="):
            return {"ok": True, "ping": True}
        raise DeciqoError(401, "webhook_signature_missing", "Missing WooCommerce webhook signature.")
    if not _valid_signature(body, signature):
        raise DeciqoError(401, "webhook_signature_invalid", "The webhook signature does not match.")
    users = _webhook_users(request.headers.get("x-wc-webhook-source", ""))
    jobs_started = [job for job in (queue_webhook_sync(u) for u in users) if job]
    log.info(f"webhook woo {request.headers.get('x-wc-webhook-topic', '?')}: {len(users)} akun")
    return {"ok": True, "accounts": len(users), "jobs": jobs_started}


# --- demo tools (hanya untuk toko sintetis) ----------------------------------------------


class DemoReviewBody(BaseModel):
    product_id: str = Field(max_length=64)
    text: str = Field(min_length=1, max_length=2000)
    rating: int = Field(ge=1, le=5)


def _demo_connection(user_id: int) -> dict:
    with store.database() as conn:
        connection = _woo_connection(conn, user_id)
    if not connection or not connection["is_demo"] or woo.is_local_url(connection["base_url"]):
        # Toko WordPress lokal adalah WooCommerce asli: ulasan ditulis langsung di storefront-nya.
        raise DeciqoError(409, "demo_only", "This works only with the synthetic demo store connected.")
    return connection


def _post_demo_review(connection: dict, woo_product_id: str, text: str, rating: int) -> None:
    try:
        response = httpx.post(f"{connection['base_url']}/demo/reviews", timeout=5.0,
                              json={"product_id": int(woo_product_id), "text": text, "rating": rating})
        response.raise_for_status()
    except (httpx.HTTPError, ValueError) as exc:
        raise jobs.JobFailed("store_unavailable", "The demo store could not be reached.") from exc


@router.post("/demo/reviews", status_code=202)
def demo_review(body: DemoReviewBody, user: dict = Depends(current_user)) -> dict:
    connection = _demo_connection(user["id"])
    with store.database() as conn:
        product = store.row(conn.execute(
            "SELECT source_item_id FROM products WHERE id = ? AND user_id = ? AND channel = 'woocommerce'",
            (body.product_id, user["id"])))
    if not product:
        raise not_found("product")

    def run(ctx):
        ctx.progress(stage="posting")
        _post_demo_review(connection, product["source_item_id"], body.text.strip(), body.rating)
        return sync_woo(ctx, user["id"])

    return _accepted(jobs.start(user["id"], "demo_review", run, target=body.product_id))


@router.post("/demo/live", status_code=202)
def demo_live(user: dict = Depends(current_user)) -> dict:
    """Tiga ulasan masuk kira-kira 8 detik sekali, masing-masing disusul sinkron + analisis."""
    connection = _demo_connection(user["id"])

    def run(ctx):
        total = len(demo_catalog.LIVE_REVIEWS)
        results = []
        for i, (woo_id, rating, text) in enumerate(demo_catalog.LIVE_REVIEWS, start=1):
            if i > 1:
                time.sleep(LIVE_INTERVAL_SECONDS)
            ctx.progress(index=i, total=total, stage="posting")
            _post_demo_review(connection, str(woo_id), text, rating)
            results.append(sync_woo(None, user["id"])["stats"])
            ctx.progress(index=i, total=total, stage="analysed")
        return {"reviews_added": total, "syncs": results}

    return _accepted(jobs.start(user["id"], "demo_live", run, target="live"))


# --- impor tempel/CSV ---------------------------------------------------------------------


class ImportBody(BaseModel):
    channel: str = Field(max_length=20)
    product_title: str = Field(default="", max_length=300)
    product_url: str | None = Field(default="", max_length=500)
    listing: str | None = Field(default="", max_length=20000)
    reviews_text: str | None = Field(default="", max_length=500000)
    csv_text: str | None = Field(default="", max_length=6_000_000)


@router.post("/import", status_code=202)
def import_reviews(body: ImportBody, user: dict = Depends(current_user)) -> dict:
    catalog = importers.build_catalog(
        channel=body.channel, product_title=body.product_title, product_url=body.product_url or "",
        listing=body.listing or "", reviews_text=body.reviews_text or "", csv_text=body.csv_text or "")
    # Simpan langsung supaya statistik bisa langsung dipakai toast; analisis menyusul di job.
    stats = ingest.upsert_catalog(user["id"], body.channel, catalog, data_origin="channel")
    job_id = jobs.start(user["id"], "import_analyse",
                        lambda ctx: {"stats": stats.public(), "product_ids": stats.products,
                                     "analysis": analysis.analyse_products(ctx, stats.changed_products)},
                        target=",".join(stats.products))
    return _accepted(job_id, stats=stats.public(), product_ids=stats.products)


# --- Lazada -----------------------------------------------------------------------------------


class LazadaFetchBody(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=apify.MAX_URLS)


@router.post("/lazada/fetch", status_code=202)
def lazada_fetch(body: LazadaFetchBody, user: dict = Depends(current_user)) -> dict:
    if not settings.apify_tokens():
        raise DeciqoError(503, "fetch_unconfigured", "Live Lazada fetch is not configured on this server.")
    for url in body.urls:
        apify.product_item_id(url)

    def run(ctx):
        ctx.progress(index=0, total=len(body.urls), stage="fetching")
        try:
            catalog = apify.fetch_products(body.urls, user_id=user["id"])
        except DeciqoError as exc:
            with store.database() as conn:
                ingest.touch_source(conn, user["id"], "lazada", ok=False, error=exc.detail["message"])
            raise jobs.JobFailed(exc.code, exc.detail["message"]) from exc
        ctx.progress(stage="saving")
        stats = ingest.upsert_catalog(user["id"], "lazada", catalog, data_origin="public_live",
                                      captured_at=store.now())
        return {"stats": stats.public(), "products": len(catalog),
                "analysis": analysis.analyse_products(ctx, stats.changed_products)}

    return _accepted(jobs.start(user["id"], "lazada_fetch", run, target=",".join(sorted(body.urls))))


def latest_lazada_snapshot() -> str | None:
    names = [name for name, pack in list_packs().items()
             if pack["channel"] == "lazada" and pack["data_origin"] == "public_snapshot"]
    return sorted(names)[-1] if names else None


@router.post("/lazada/snapshot", status_code=202)
def lazada_snapshot(user: dict = Depends(current_user)) -> dict:
    name = latest_lazada_snapshot()
    if not name:
        raise DeciqoError(404, "unknown_sample", "No dated Lazada snapshot is available.")
    return load_sample(name, user)


# --- paket contoh ----------------------------------------------------------------------------


def list_packs() -> dict[str, dict]:
    packs = {}
    if MARKETPLACE_DIR.is_dir():
        for path in sorted(MARKETPLACE_DIR.glob("*.json")):
            try:
                meta = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            packs[path.stem] = {"name": path.stem, "channel": meta.get("channel"),
                                "data_origin": meta.get("data_origin"), "captured_at": meta.get("captured_at"),
                                "label": meta.get("label", path.stem), "products": len(meta.get("products", [])),
                                "sampling_kind": meta.get("sampling_kind", "unknown")}
    return packs


@router.get("/samples")
def samples_list(user: dict = Depends(current_user)) -> dict:
    return {"samples": list(list_packs().values())}


@router.post("/samples/{name}", status_code=202)
def load_sample(name: str, user: dict = Depends(current_user)) -> dict:
    if name == "demo-store":
        def run(ctx):
            return samples.populate_demo(ctx, user["id"])
        return _accepted(jobs.start(user["id"], "sample", run, target=name))
    if name not in list_packs():
        raise DeciqoError(404, "unknown_sample", "This sample pack does not exist.")
    pack = json.loads((MARKETPLACE_DIR / f"{name}.json").read_text(encoding="utf-8"))

    def run(ctx):
        ctx.progress(stage="saving")
        stats = ingest.upsert_catalog(user["id"], pack["channel"], pack["products"],
                                      data_origin=pack.get("data_origin", "synthetic"),
                                      captured_at=pack.get("captured_at"),
                                      sampling=pack.get("sampling_kind", "unknown"))
        return {"stats": stats.public(), "analysis": analysis.analyse_products(ctx, stats.changed_products)}

    return _accepted(jobs.start(user["id"], "sample", run, target=name))


# --- workspace --------------------------------------------------------------------------------


@router.post("/workspace/reset", status_code=202)
def workspace_reset(user: dict = Depends(current_user)) -> dict:
    """Kosongkan workspace lalu isi ulang data demo. Akun dan sesi tetap."""

    def run(ctx):
        ctx.progress(stage="clearing")
        with store.database() as conn:
            connection = _woo_connection(conn, user["id"])
            samples.delete_workspace(conn, user["id"], keep_job=ctx.id)
        if connection and woo.is_local_url(connection["base_url"]):
            # Toko WordPress lokal: hapus ulasan tambahan di toko, lalu isi ulang dari toko itu
            # supaya sambungan dan id-nya tetap, dan ulasan berikutnya langsung tersinkron.
            return _reset_local_store(ctx, user["id"])
        try:
            httpx.post(f"{settings.woo_base_url()}/demo/reset", timeout=5.0)
        except httpx.HTTPError:
            log.warning("toko demo tidak terjangkau saat reset; ulasan tambahan tetap ada")
        return samples.populate_demo(ctx, user["id"])

    return _accepted(jobs.start(user["id"], "workspace_reset", run, target="reset"))


def _reset_local_store(ctx, user_id: int) -> dict:
    connection = (settings.woo_local_url(), settings.woo_local_user(), settings.woo_local_api_password())
    try:
        httpx.post(f"{connection[0]}/wp-json/deciqo/v1/reset", auth=connection[1:], timeout=60.0).raise_for_status()
    except httpx.HTTPError as exc:
        log.warning(f"reset toko WordPress gagal ({type(exc).__name__}); ulasan tambahan tetap ada")
    try:
        catalog = _local_client().catalog()
    except (woo.WooError, DeciqoError):
        log.warning("toko WordPress tidak terjangkau saat reset; kembali ke toko sintetis")
        return samples.populate_demo(ctx, user_id)
    return samples.populate_demo(ctx, user_id, catalog=catalog, connection=connection)


@router.delete("/workspace", status_code=204)
def workspace_delete(user: dict = Depends(current_user)) -> Response:
    with store.database() as conn:
        samples.delete_workspace(conn, user["id"])
    return Response(status_code=204)


# --- job & status -------------------------------------------------------------------------------


@router.get("/jobs/{job_id}")
def job_status(job_id: str, user: dict = Depends(current_user)) -> dict:
    return jobs.get(user["id"], job_id)


def _llm_status(conn) -> dict:
    # Rumus yang sama dengan penjaga anggaran engine: biaya terkonfirmasi + reservasi yang belum
    # selesai atau gagal tanpa usage, supaya angka di layar sama dengan yang membatasi panggilan.
    spent = conn.execute(
        "SELECT COALESCE(SUM(CASE WHEN status = 'ok' THEN cost_usd ELSE reserved_usd END), 0) "
        "FROM ledger WHERE provider = 'openai'").fetchone()[0]
    # Status penolakan key dibaca dari engine (memori proses), bukan dari kv_state: nilai di kv
    # bertahan setelah restart walau key sudah diganti, sehingga layar menyebut mode aturan padahal
    # engine sudah kembali memakai AI.
    try:
        from .engine import llm  # noqa: PLC0415

        rejected = llm.key_rejected()
    except ImportError:
        rejected = None
    return {"configured": settings.openai_configured(), "key_rejected": rejected,
            "model": settings.llm_model(), "budget_usd": settings.ai_budget_usd(), "spent_usd": round(spent, 4)}


@router.get("/status")
def status(user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        llm = _llm_status(conn)
        fetch_spent = apify.spent_usd(conn)
        products = conn.execute("SELECT COUNT(*) FROM products WHERE user_id = ?", (user["id"],)).fetchone()[0]
        changed = conn.execute(
            "SELECT COUNT(*) FROM products p LEFT JOIN analyses a ON a.product_id = p.id "
            "WHERE p.user_id = ? AND (a.product_id IS NULL OR a.created_at < p.updated_at "
            "OR EXISTS (SELECT 1 FROM reviews r WHERE r.product_id = p.id AND r.fetched_at > a.created_at "
            "AND r.triage_json IS NULL))", (user["id"],)).fetchone()[0]
        per_product = conn.execute(
            "SELECT COALESCE(SUM(cost_usd) / NULLIF(COUNT(DISTINCT ref), 0), 0) FROM ledger "
            "WHERE provider = 'openai' AND purpose IN ('discovery', 'membership')").fetchone()[0]
    engine = "ai" if llm["configured"] and not llm["key_rejected"] else "rules"
    return {
        "engine": engine,
        "llm": llm,
        "fetch": {"configured": bool(settings.apify_tokens()), "budget_usd": settings.apify_budget_usd(),
                  "spent_usd": round(fetch_spent, 4), "max_urls": apify.MAX_URLS,
                  "max_charge_per_run_usd": apify.MAX_CHARGE_PER_RUN,
                  "reviews_per_product": apify.REVIEWS_PER_PRODUCT},
        "estimate": {"products": products, "changed": changed,
                     "analysis_per_product_usd": round(per_product, 4),
                     "analyse_all_usd": round(per_product * changed, 4)},
        "engine_ready": analysis.available(),
        "jobs": jobs.active_for(user["id"]),
    }


# Polling Woo terjadwal: sinkron manual selalu bisa; ini hanya menjaga data tidak basi.
_poller_started = threading.Event()


def start_poller() -> None:
    if _poller_started.is_set() or settings.poll_seconds() <= 0:
        return
    _poller_started.set()

    def loop():
        while True:
            time.sleep(settings.poll_seconds())
            try:
                with store.database() as conn:
                    users = [r["user_id"] for r in conn.execute("SELECT user_id FROM woo_connections")]
                for user_id in users:
                    try:
                        jobs.start(user_id, "sync_analyse", lambda ctx, u=user_id: sync_woo(ctx, u), target="woo")
                    except DeciqoError:
                        continue
            except Exception as exc:  # noqa: BLE001
                log.error(f"polling woo gagal: {type(exc).__name__}")

    threading.Thread(target=loop, name="woo-poller", daemon=True).start()
