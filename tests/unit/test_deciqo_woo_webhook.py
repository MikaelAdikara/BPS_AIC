"""Toko WordPress demo lokal: webhook WooCommerce, mode sambung `local`, pulse, dan katalog seed."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.deciqo import alerts, auth, demo_catalog, jobs, store
from app.deciqo import app as deciqo_app
from app.deciqo.connectors import woo
from app.deciqo.errors import DeciqoError

ROOT = Path(__file__).resolve().parents[2]
SECRET = "rahasia-uji"


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "t.sqlite3"))
    monkeypatch.setenv("WOO_WEBHOOK_SECRET", SECRET)
    monkeypatch.setenv("WOO_LOCAL_URL", "http://wordpress")
    auth._failures.clear()
    store.migrate()
    real_start = jobs.start
    monkeypatch.setattr(jobs, "start", lambda *a, **k: real_start(*a, **{**k, "run_inline": True}))
    from app.deciqo import routes_sources

    calls: list[int] = []

    def fake_sync(ctx, user_id, *, analyse=True):
        calls.append(user_id)
        return {"stats": {"inserted": 1}, "products": 1, "analysis": {}}

    monkeypatch.setattr(routes_sources, "sync_woo", fake_sync)
    return calls


def _client() -> TestClient:
    app = FastAPI()
    deciqo_app.include(app)
    return TestClient(app, raise_server_exceptions=False)


def _user_with_store(email: str, base_url: str) -> int:
    with store.database() as conn:
        user = auth.create_user(conn, email, "panjang123", "U")
        conn.execute("INSERT INTO woo_connections(user_id, base_url, consumer_key, consumer_secret, is_demo, "
                     "created_at) VALUES(?, ?, 'k', 's', 1, ?)", (user["id"], base_url, store.now()))
    return user["id"]


def _signed(body: bytes, secret: str = SECRET) -> dict:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    return {"X-WC-Webhook-Signature": base64.b64encode(digest).decode(),
            "X-WC-Webhook-Source": "http://localhost:8081/", "X-WC-Webhook-Topic": "action.comment_post"}


BODY = json.dumps({"action": "comment_post", "arg": 1045}).encode()


def test_webhook_bertanda_tangan_memicu_sinkron_toko_lokal(env):
    local = _user_with_store("a@x.io", "http://wordpress")
    _user_with_store("b@x.io", "https://toko-lain.example.com")
    r = _client().post("/api/v1/deciqo/woo/webhook", content=BODY, headers=_signed(BODY))
    assert r.status_code == 202, r.text
    assert r.json()["accounts"] == 1
    assert env == [local]


def test_webhook_tanda_tangan_salah_atau_hilang_ditolak(env):
    _user_with_store("a@x.io", "http://wordpress")
    client = _client()
    assert client.post("/api/v1/deciqo/woo/webhook", content=BODY,
                       headers=_signed(BODY, "salah")).status_code == 401
    assert client.post("/api/v1/deciqo/woo/webhook", content=BODY).status_code == 401
    assert env == []


def test_ping_aktivasi_webhook_diterima_tanpa_sinkron(env):
    _user_with_store("a@x.io", "http://wordpress")
    r = _client().post("/api/v1/deciqo/woo/webhook", content=b"webhook_id=7",
                       headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert r.status_code == 202 and r.json()["ping"] is True
    assert env == []


def test_webhook_saat_sinkron_berjalan_diulang_bukan_hilang(env, monkeypatch):
    from app.deciqo import routes_sources

    user_id = _user_with_store("a@x.io", "http://wordpress")
    rounds: list[int] = []

    def sync_with_new_review(ctx, uid, *, analyse=True):
        rounds.append(uid)
        if len(rounds) == 1:
            # Ulasan kedua masuk ketika sinkron pertama masih berjalan.
            assert routes_sources.queue_webhook_sync(uid) is None
        return {"stats": {"inserted": 1}, "products": 1}

    monkeypatch.setattr(routes_sources, "sync_woo", sync_with_new_review)
    job_id = routes_sources.queue_webhook_sync(user_id)
    job = jobs.get(user_id, job_id)
    assert job["status"] == "done", job
    assert job["result"]["rounds"] == 2 and rounds == [user_id, user_id]
    # Setelah selesai, webhook berikutnya memulai job baru lagi.
    assert routes_sources.queue_webhook_sync(user_id) is not None


def test_url_toko_lokal_diizinkan_tetapi_host_privat_lain_tidak(env):
    assert woo.validate_store_url("http://wordpress") == "http://wordpress"
    with pytest.raises(DeciqoError):
        woo.validate_store_url("http://intranet")


def test_sambung_mode_lokal_dan_alat_demo_sintetis_ditolak(env, monkeypatch):
    monkeypatch.setattr(woo.WooClient, "_get", lambda self, path, params: ([], {}))
    client = _client()
    client.post("/api/v1/auth/register", json={"email": "l@x.io", "password": "panjang123"})
    r = client.post("/api/v1/deciqo/woo/connect", json={"mode": "local"})
    assert r.status_code == 200, r.text
    assert r.json()["local"] is True and r.json()["synthetic"] is True
    assert r.json()["label"] == "WooCommerce (local demo store)"
    status = client.get("/api/v1/deciqo/woo/local").json()
    assert status["connected"] is True and status["storefront_url"] == "http://localhost:8081"
    # Tombol ulasan simulasi hanya untuk toko sintetis; di toko lokal ulasan ditulis di storefront.
    assert client.post("/api/v1/deciqo/demo/live").status_code == 409


def test_pulse_membawa_job_aktif_dan_alert_terbaru(env):
    client = _client()
    client.post("/api/v1/auth/register", json={"email": "p@x.io", "password": "panjang123"})
    assert client.get("/api/v1/deciqo/pulse").json() == {"jobs": [], "latest_alert": None}
    with store.database() as conn:
        uid = conn.execute("SELECT id FROM users WHERE email = 'p@x.io'").fetchone()[0]
    alerts.enqueue_event(uid, "reopened", finding_id="f1", synthetic=True,
                         payload={"product": "Kursi lipat camping", "attribute_local": "layanan penjual"})
    latest = client.get("/api/v1/deciqo/pulse?lang=id").json()["latest_alert"]
    assert latest["kind"] == "reopened" and "Kursi lipat camping" in latest["message"]


def test_katalog_toko_wordpress_sama_dengan_demo_catalog():
    data = json.loads((ROOT / "docker" / "wordpress" / "catalog.json").read_text(encoding="utf-8"))
    ours = {p["id"]: p for p in data["products"]}
    assert set(ours) == {p["id"] for p in demo_catalog.PRODUCTS}
    for product in demo_catalog.PRODUCTS:
        mine = ours[product["id"]]
        assert (mine["name"], mine["price"], mine["description"]) == (
            product["name"], product["price"], product["description"])
        assert [(r["id"], r["rating"], r["days_ago"], r["text"]) for r in mine["reviews"]] == [
            (rid, rating, days, text) for rid, rating, days, _v, text in product["reviews"]
        ], "catalog.json tertinggal: jalankan scripts/build_wp_store.py"
        assert (ROOT / "docker" / "wordpress" / "images" / f"{product['sku'].lower()}.png").is_file()


def test_gambar_lokal_tidak_dikirim_ke_model_vision():
    from app.deciqo.engine import vision

    urls = vision._urls(["http://localhost:8081/wp-content/uploads/a.png", "http://wordpress/x.png",
                         "http://192.168.1.5/y.png", "https://cdn.example.com/z.png"])
    assert urls == ["https://cdn.example.com/z.png"]


def test_reset_workspace_toko_lokal_mereset_toko_dan_tetap_tersambung(env, monkeypatch):
    from app.deciqo import routes_sources, samples

    user_id = _user_with_store("r@x.io", "http://wordpress")
    posted: list[str] = []

    class Answer:
        def raise_for_status(self):
            return None

    monkeypatch.setattr(routes_sources.httpx, "post", lambda url, **kw: posted.append(url) or Answer())

    class Client:
        def catalog(self):
            return demo_catalog.as_catalog()

    monkeypatch.setattr(routes_sources, "_local_client", lambda: Client())
    populated: list[dict] = []
    monkeypatch.setattr(samples, "populate_demo", lambda ctx, uid, **kw: populated.append(kw) or {"ok": True})
    job_id = routes_sources.jobs.start(user_id, "workspace_reset",
                                       lambda ctx: routes_sources._reset_local_store(ctx, user_id))
    assert jobs.get(user_id, job_id)["status"] == "done"
    assert posted == ["http://wordpress/wp-json/deciqo/v1/reset"]
    assert populated[0]["connection"][0] == "http://wordpress" and populated[0]["catalog"]


def test_hapus_workspace_jalan_di_skema_lama_telegram_not_null(env):
    from app.deciqo import samples

    with store.database() as conn:
        user = auth.create_user(conn, "o@x.io", "panjang123", "U")
        conn.execute("UPDATE users SET telegram_chat_id = '123' WHERE id = ?", (user["id"],))
        samples.delete_workspace(conn, user["id"])
        assert not conn.execute("SELECT telegram_chat_id FROM users WHERE id = ?", (user["id"],)).fetchone()[0]
