"""Telegram: tautan lewat kode sekali pakai atau kontak sendiri, dan perintah tanpa teks ulasan."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.deciqo import app as deciqo_app
from app.deciqo import auth, ingest, store, telegram


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "t.sqlite3"))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    auth._failures.clear()
    store.migrate()
    app = FastAPI()
    deciqo_app.include(app)
    c = TestClient(app, raise_server_exceptions=False)
    c.post("/api/v1/auth/register", json={"email": "t@x.io", "password": "panjang123", "name": "Toko"})
    c.patch("/api/v1/auth/me", json={"lang": "id"})
    return c


def _msg(text="", chat_id=555, contact=None, sender=555):
    message = {"chat": {"id": chat_id, "type": "private"}, "from": {"id": sender, "language_code": "id"}, "text": text}
    if contact:
        message["contact"] = contact
    return {"update_id": 1, "message": message}


def _linked_chat() -> str | None:
    with store.database() as conn:
        return conn.execute("SELECT telegram_chat_id FROM users WHERE email = 't@x.io'").fetchone()[0]


def test_tautan_kode_sekali_pakai(client):
    code = client.post("/api/v1/deciqo/telegram/link").json()["code"]
    assert "Terhubung" in telegram.handle_update(_msg(f"/start {code}"))
    assert _linked_chat() == "555"
    # Kode yang sama tidak bisa dipakai chat lain.
    assert "tidak valid" in telegram.handle_update(_msg(f"/start {code}", chat_id=777, sender=777))
    assert client.get("/api/v1/auth/me").json()["telegram_linked"] is True


def test_kode_bisa_diketik_tanpa_start(client):
    code = client.post("/api/v1/deciqo/telegram/link").json()["code"]
    telegram.handle_update(_msg(code.lower()))
    assert _linked_chat() == "555"


def test_kontak_terusan_ditolak(client):
    client.patch("/api/v1/auth/me", json={"phone": "081234567890"})
    forwarded = {"phone_number": "+6281234567890", "user_id": 999}
    assert "sendiri" in telegram.handle_update(_msg(contact=forwarded))
    assert _linked_chat() is None
    own = {"phone_number": "+6281234567890", "user_id": 555}
    telegram.handle_update(_msg(contact=own))
    assert _linked_chat() == "555"


def test_perintah_tanpa_teks_ulasan(client):
    code = client.post("/api/v1/deciqo/telegram/link").json()["code"]
    telegram.handle_update(_msg(f"/start {code}"))
    with store.database() as conn:
        uid = conn.execute("SELECT id FROM users WHERE email = 't@x.io'").fetchone()[0]
    stats = ingest.upsert_catalog(uid, "manual", [{"title": "Tas laptop", "reviews": [
        {"text": "RAHASIA laptop tidak muat"}]}])
    with store.database() as conn:
        conn.execute("INSERT INTO findings(id, product_id, attribute_local, severity, support, denominator, state) "
                     "VALUES('f_1', ?, 'ukuran dalam', 'high', 1, 1, 'open')", (stats.products[0],))
    issues = telegram.handle_update(_msg("/isu"))
    assert "Tas laptop" in issues and "1 dari 1" in issues and "RAHASIA" not in issues
    assert "1 isu aktif" in telegram.handle_update(_msg("/status"))
    assert "diputus" in telegram.handle_update(_msg("/putus"))
    assert _linked_chat() is None


def test_chat_belum_tertaut(client):
    assert "belum terhubung" in telegram.handle_update(_msg("/status"))


def test_uji_kirim_tanpa_bot(client):
    assert client.post("/api/v1/deciqo/telegram/test").json()["status"] == "unconfigured"


def test_perintah_id_menampilkan_chat_sendiri(client):
    assert telegram.handle_update(_msg("/id", chat_id=4242, sender=4242)) == "Chat ID: 4242"


def test_chat_operator_hanya_untuk_akun_demo(client, monkeypatch):
    from datetime import datetime, timezone

    from app.deciqo import alerts, samples

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "111111, 222222 ,bukan-angka")
    sent = []
    monkeypatch.setattr(alerts, "_send_telegram", lambda base, token, chat, text, fid: sent.append((base, chat)) or {"message_id": 1})
    with store.database() as conn:
        demo = samples.ensure_demo_user(conn)
        other = conn.execute("SELECT id FROM users WHERE email = 't@x.io'").fetchone()[0]
        alerts.enqueue_event(demo["id"], "new_issue", finding_id="f_d", synthetic=True, payload={"product": "Tas"}, conn=conn)
        alerts.enqueue_event(other, "new_issue", finding_id="f_o", synthetic=True, payload={"product": "Tas"}, conn=conn)
    alerts.dispatch_once(datetime.now(timezone.utc))
    real = [chat for base, chat in sent if base.startswith("https://api.telegram.org")]
    assert real == ["111111", "222222"]
    with store.database() as conn:
        statuses = dict(conn.execute("SELECT finding_id, status FROM alert_events").fetchall())
    assert statuses == {"f_d": "sent", "f_o": "simulated"}
