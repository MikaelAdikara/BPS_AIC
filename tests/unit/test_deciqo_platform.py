"""Platform Deciqo: migrasi, versi, akun, sesi, dan isolasi."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.deciqo import app as deciqo_app
from app.deciqo import auth, store


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "t.sqlite3"))
    monkeypatch.setenv("DECIQO_ALLOW_SIGNUP", "true")
    auth._failures.clear()
    store.migrate()
    app = FastAPI()
    deciqo_app.include(app)
    return TestClient(app, raise_server_exceptions=False)


def test_migrasi_idempoten(tmp_path):
    path = tmp_path / "m.sqlite3"
    store.migrate(path)
    store.migrate(path)
    conn = store.connect(path)
    tables = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert set(store.SCHEMA) <= tables


def test_migrasi_menambah_kolom_yang_hilang(tmp_path):
    path = tmp_path / "old.sqlite3"
    conn = store.connect(path)
    conn.execute("CREATE TABLE kv_state (key TEXT PRIMARY KEY)")
    conn.close()
    store.migrate(path)
    cols = {r["name"] for r in store.connect(path).execute("PRAGMA table_info(kv_state)")}
    assert "value" in cols


def test_version(client):
    body = client.get("/api/v1/version").json()
    assert body["app"] == "deciqo"
    assert body["pipeline"] and body["verifier"]
    assert body["commit"]


def test_register_me_logout(client):
    r = client.post("/api/v1/auth/register", json={"email": "A@x.io", "password": "rahasia123", "name": "A"})
    assert r.status_code == 201
    assert r.json()["email"] == "a@x.io"
    assert "httponly" in r.headers["set-cookie"].lower()
    assert client.get("/api/v1/auth/me").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 204
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 401
    assert me.json()["detail"]["code"] == "not_signed_in"


def test_register_errors(client, monkeypatch):
    r = client.post("/api/v1/auth/register", json={"email": "b@x.io", "password": "short"})
    assert r.json()["detail"]["code"] == "weak_password"
    client.post("/api/v1/auth/register", json={"email": "b@x.io", "password": "panjang123"})
    client.cookies.clear()
    r = client.post("/api/v1/auth/register", json={"email": "B@x.io", "password": "panjang123"})
    assert r.status_code == 409 and r.json()["detail"]["code"] == "email_taken"
    monkeypatch.setenv("DECIQO_ALLOW_SIGNUP", "false")
    r = client.post("/api/v1/auth/register", json={"email": "c@x.io", "password": "panjang123"})
    assert r.status_code == 403 and r.json()["detail"]["code"] == "signup_closed"


def test_login_throttle(client):
    client.post("/api/v1/auth/register", json={"email": "t@x.io", "password": "panjang123"})
    client.cookies.clear()
    for _ in range(auth.THROTTLE_MAX):
        assert client.post("/api/v1/auth/login", json={"email": "t@x.io", "password": "salah!!!"}).status_code == 401
    r = client.post("/api/v1/auth/login", json={"email": "t@x.io", "password": "panjang123"})
    assert r.status_code == 429


def test_login_dan_patch_me(client):
    client.post("/api/v1/auth/register", json={"email": "p@x.io", "password": "panjang123"})
    client.cookies.clear()
    assert client.post("/api/v1/auth/login", json={"email": "p@x.io", "password": "panjang123"}).status_code == 200
    r = client.patch("/api/v1/auth/me", json={"channels": ["woocommerce", "lazada"], "phone": "0812-3456-7890"})
    assert r.json()["channels"] == ["woocommerce", "lazada"]
    assert r.json()["phone"] == "081234567890"
    r = client.patch("/api/v1/auth/me", json={"channels": ["myspace"]})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "unknown_channel"


def test_validasi_memakai_bentuk_error_deciqo(client):
    r = client.post("/api/v1/auth/login", json={"email": "x@x.io"})
    assert r.status_code == 422
    assert r.json()["detail"]["code"] == "invalid_input"


def test_password_hash_bergaram():
    a, b = auth.hash_password("sama-sama"), auth.hash_password("sama-sama")
    assert a != b
    assert auth.verify_password("sama-sama", a) and not auth.verify_password("beda", a)
