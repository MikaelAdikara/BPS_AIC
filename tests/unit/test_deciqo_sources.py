"""Sumber data: ingest, impor, redaksi PII, sinkron Woo sintetis, isolasi, dan hapus workspace."""

from __future__ import annotations

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.deciqo import app as deciqo_app
from app.deciqo import alerts, auth, demo_catalog, ingest, jobs, mock_woo, samples, store
from app.deciqo.connectors import woo


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "t.sqlite3"))
    monkeypatch.setenv("DECIQO_MOCK_DB_PATH", str(tmp_path / "woo.sqlite3"))
    monkeypatch.setenv("WOO_BASE_URL", "http://woo-demo:8080")
    monkeypatch.setenv("WOO_PAGE_SIZE", "2")
    auth._failures.clear()
    store.migrate()
    # Toko sintetis dijalankan in-process: klien Woo memakai transport TestClient-nya.
    store_client = TestClient(mock_woo.app)

    def handler(request):
        answer = store_client.request(request.method, str(request.url), headers=request.headers,
                                      content=request.content)
        return httpx.Response(answer.status_code, headers=answer.headers, content=answer.content)

    transport = httpx.MockTransport(handler)
    original = woo.WooClient.__init__

    def init(self, base_url, key, secret, transport_=None):
        original(self, base_url, key, secret, transport=transport)

    monkeypatch.setattr(woo.WooClient, "__init__", init)
    from app.deciqo import routes_sources

    monkeypatch.setattr(routes_sources.httpx, "post",
                        lambda url, **kw: store_client.post(url.replace("http://woo-demo:8080", ""), json=kw.get("json")))
    # Job dijalankan langsung supaya tes deterministik.
    real_start = jobs.start
    monkeypatch.setattr(jobs, "start", lambda *a, **k: real_start(*a, **{**k, "run_inline": True}))
    return tmp_path


def _client() -> TestClient:
    app = FastAPI()
    deciqo_app.include(app)
    return TestClient(app, raise_server_exceptions=False)


def _login(client: TestClient, email: str) -> None:
    client.post("/api/v1/auth/register", json={"email": email, "password": "panjang123"})


def test_redaksi_pii_sebelum_simpan(env):
    with store.database() as conn:
        user = auth.create_user(conn, "r@x.io", "panjang123", "R")
    stats = ingest.upsert_catalog(user["id"], "manual", [{
        "title": "Tas", "reviews": [
            {"text": "Hubungi saya di 0812-3456-7890 atau budi@mail.com ya"},
            {"text": "Enak dibawa jalan jalan, blok warnanya bagus"},
        ]}])
    assert stats.redacted == 1
    with store.database() as conn:
        texts = [r["text"] for r in conn.execute("SELECT text FROM reviews ORDER BY text")]
    assert not any("0812" in t or "budi@" in t for t in texts)
    # Kata umum di ulasan tidak dianggap alamat.
    assert "Enak dibawa jalan jalan, blok warnanya bagus" in texts


def test_impor_ulang_tidak_menggandakan(env):
    client = _client()
    _login(client, "i@x.io")
    body = {"channel": "tokopedia", "product_title": "Kemeja", "reviews_text": "2 | kekecilan\nBagus\nBagus\n\n"}
    first = client.post("/api/v1/deciqo/import", json=body).json()
    assert first["stats"] == {"received": 3, "inserted": 3, "updated": 0, "unchanged": 0,
                              "skipped_empty": 0, "deleted": 0, "redacted": 0}
    second = client.post("/api/v1/deciqo/import", json=body).json()
    assert second["stats"]["unchanged"] == 3 and second["stats"]["inserted"] == 0
    with store.database() as conn:
        assert conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0] == 3
        rating = conn.execute("SELECT rating FROM reviews WHERE text = 'kekecilan'").fetchone()[0]
    assert rating == 2
    job = client.get(f"/api/v1/deciqo/jobs/{second['job_id']}").json()
    assert job["status"] == "done"


def test_impor_csv_header_fleksibel(env):
    client = _client()
    _login(client, "c@x.io")
    csv_text = "Ulasan;Bintang;Tanggal;Varian\nterlalu kecil;2;2026-09-01;M\n;5;;\n"
    r = client.post("/api/v1/deciqo/import", json={"channel": "shopee", "product_title": "Kaos", "csv_text": csv_text})
    assert r.status_code == 202
    assert r.json()["stats"]["inserted"] == 1 and r.json()["stats"]["skipped_empty"] == 1
    r = client.post("/api/v1/deciqo/import", json={"channel": "shopee", "product_title": "Kaos", "csv_text": "a,b\n1,2"})
    assert r.json()["detail"]["code"] == "csv_missing_review_column"


def test_impor_kosong_ditolak(env):
    client = _client()
    _login(client, "e@x.io")
    r = client.post("/api/v1/deciqo/import", json={"channel": "manual", "product_title": "X"})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "no_reviews"


def test_sinkron_woo_sintetis_dan_paginasi(env):
    client = _client()
    _login(client, "w@x.io")
    r = client.post("/api/v1/deciqo/woo/connect", json={"mode": "demo"})
    assert r.status_code == 200, r.text
    job_id = client.post("/api/v1/deciqo/woo/sync").json()["job_id"]
    job = client.get(f"/api/v1/deciqo/jobs/{job_id}").json()
    assert job["status"] == "done", job
    total_reviews = sum(len(p["reviews"]) for p in demo_catalog.PRODUCTS)
    assert job["result"]["stats"]["inserted"] == total_reviews
    assert job["result"]["products"] == len(demo_catalog.PRODUCTS)
    # Sinkron kedua: tidak ada yang berubah.
    job2 = client.get(f"/api/v1/deciqo/jobs/{client.post('/api/v1/deciqo/woo/sync').json()['job_id']}").json()
    assert job2["result"]["stats"]["unchanged"] == total_reviews


def test_seed_demo_lalu_sinkron_tidak_menggandakan(env):
    with store.database() as conn:
        user = samples.ensure_demo_user(conn)
        samples.load_demo_catalog(conn, user["id"])
    from app.deciqo import routes_sources

    result = routes_sources.sync_woo(None, user["id"], analyse=False)
    assert result["stats"]["inserted"] == 0
    assert result["stats"]["unchanged"] == sum(len(p["reviews"]) for p in demo_catalog.PRODUCTS)


def test_ulasan_demo_baru_masuk_lewat_sinkron(env):
    client = _client()
    _login(client, "d@x.io")
    client.post("/api/v1/deciqo/woo/connect", json={"mode": "demo"})
    client.post("/api/v1/deciqo/woo/sync")
    with store.database() as conn:
        pid = conn.execute("SELECT id FROM products WHERE source_item_id = '103'").fetchone()[0]
    r = client.post("/api/v1/deciqo/demo/reviews", json={"product_id": pid, "text": "Chat tidak dibalas", "rating": 2})
    job = client.get(f"/api/v1/deciqo/jobs/{r.json()['job_id']}").json()
    assert job["status"] == "done" and job["result"]["stats"]["inserted"] == 1


def test_isolasi_akun_404(env):
    a, b = _client(), _client()
    _login(a, "a@x.io")
    _login(b, "b@x.io")
    job_id = a.post("/api/v1/deciqo/import", json={"channel": "manual", "product_title": "T",
                                                   "reviews_text": "sempit"}).json()["job_id"]
    assert b.get(f"/api/v1/deciqo/jobs/{job_id}").status_code == 404
    assert _client().get("/api/v1/deciqo/status").status_code == 401


def test_hapus_workspace_lengkap(env):
    client = _client()
    _login(client, "h@x.io")
    client.post("/api/v1/deciqo/woo/connect", json={"mode": "demo"})
    client.post("/api/v1/deciqo/woo/sync")
    with store.database() as conn:
        uid = conn.execute("SELECT id FROM users WHERE email = 'h@x.io'").fetchone()[0]
        pid = conn.execute("SELECT id FROM products LIMIT 1").fetchone()[0]
        conn.execute("INSERT INTO findings(id, product_id, attribute_key) VALUES('f_1', ?, 'size')", (pid,))
        conn.execute("INSERT INTO decisions(finding_id, decision) VALUES('f_1', 'acted')")
        alerts.enqueue_event(uid, "new_issue", finding_id="f_1", payload={"product": "T"}, conn=conn)
    assert client.delete("/api/v1/deciqo/workspace").status_code == 204
    with store.database() as conn:
        for table in ("products", "reviews", "findings", "decisions", "alert_events", "jobs", "sources", "woo_connections"):
            assert conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0, table
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
    assert client.get("/api/v1/auth/me").status_code == 200


def test_ssrf_url_toko_ditolak(env):
    from app.deciqo.errors import DeciqoError

    for bad in ("http://shop.example.com", "https://user:pw@shop.example.com", "https://127.0.0.1",
                "https://localhost", "https://10.0.0.5", "https://shop.example.com:8443"):
        with pytest.raises(DeciqoError):
            woo.validate_store_url(bad)
    assert woo.validate_store_url("http://woo-demo:8080/") == "http://woo-demo:8080"


def test_status_sumber_stale_saat_toko_gagal(env, monkeypatch):
    client = _client()
    _login(client, "s@x.io")
    client.post("/api/v1/deciqo/woo/connect", json={"mode": "demo"})
    client.post("/api/v1/deciqo/woo/sync")

    def boom(self):
        raise woo.WooError("store_unavailable", "The store could not be reached.")

    monkeypatch.setattr(woo.WooClient, "catalog", boom)
    for _ in range(2):
        job = client.get(f"/api/v1/deciqo/jobs/{client.post('/api/v1/deciqo/woo/sync').json()['job_id']}").json()
        assert job["status"] == "failed" and job["error"]["code"] == "store_unavailable"
    with store.database() as conn:
        source = conn.execute("SELECT status FROM sources WHERE channel = 'woocommerce'").fetchone()[0]
        kept = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        problem = conn.execute("SELECT COUNT(*) FROM alert_events WHERE kind = 'source_problem'").fetchone()[0]
    assert source == "stale" and kept > 0 and problem == 1


def test_job_terputus_ditandai_interrupted(env):
    with store.database() as conn:
        user = auth.create_user(conn, "j@x.io", "panjang123", "J")
        conn.execute("INSERT INTO jobs(id, user_id, kind, status, created_at, updated_at) "
                     "VALUES('j_x', ?, 'sync_analyse', 'running', '', '')", (user["id"],))
    assert jobs.recover() == 1
    assert jobs.get(user["id"], "j_x")["status"] == "interrupted"


def test_alert_tanpa_teks_ulasan_dan_dedupe(env):
    with store.database() as conn:
        user = auth.create_user(conn, "al@x.io", "panjang123", "A")
        first = alerts.enqueue_event(user["id"], "new_issue", finding_id="f_9", synthetic=True, version="v1",
                                     payload={"product": "Tas", "attribute_local": "ukuran", "count": 3, "total": 4,
                                              "review_text": "rahasia pelanggan"}, conn=conn)
        again = alerts.enqueue_event(user["id"], "new_issue", finding_id="f_9", version="v1",
                                     payload={"product": "Tas"}, conn=conn)
        event = store.row(conn.execute("SELECT * FROM alert_events WHERE id = ?", (first,)))
    assert first and again is None
    message = alerts.render(event, "id")
    assert message.startswith(alerts.DEMO_PREFIX) and "rahasia" not in message and "3 dari 4" in message


def test_snapshot_lazada_bertanggal_dimuat(env):
    from app.deciqo import routes_sources

    name = routes_sources.latest_lazada_snapshot()
    if name is None:
        pytest.skip("snapshot Lazada belum ada di data/marketplace")
    client = _client()
    _login(client, "lz@x.io")
    job = client.get(f"/api/v1/deciqo/jobs/{client.post('/api/v1/deciqo/lazada/snapshot').json()['job_id']}").json()
    assert job["status"] == "done", job
    with store.database() as conn:
        origins = {r[0] for r in conn.execute("SELECT DISTINCT data_origin FROM products")}
        captured = conn.execute("SELECT captured_at FROM products LIMIT 1").fetchone()[0]
    assert origins == {"public_snapshot"} and captured.startswith("2026-")
    assert job["result"]["stats"]["inserted"] > 100
