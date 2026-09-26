"""Endpoint engine dan read model: urutan inbox, bucket per state, keputusan, 404 lintas akun."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.deciqo import app as deciqo_app
from app.deciqo import auth, ingest, store
from app.deciqo.engine import llm, pipeline, triage

BAG = {"source_item_id": "tas", "title": "Tas laptop kanvas 14 inci",
       "description": "Tas kanvas tebal, muat laptop hingga 14 inch.",
       "reviews": [{"id": "r1", "rating": 2, "text": "Laptop 14 inch saya tidak muat."},
                   {"id": "r2", "rating": 3, "text": "Kantong dalamnya sempit, laptop harus dipaksa masuk."},
                   {"id": "r3", "rating": 5, "text": "Bagus, tapi agak sempit buat laptop 14 inch."},
                   {"id": "r4", "rating": 2, "text": "Pengiriman lama sekali, hampir dua minggu."}]}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "r.sqlite3"))
    monkeypatch.setenv("DECIQO_ALLOW_SIGNUP", "true")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    auth._failures.clear()
    triage.set_text_adapter(None)
    llm.reset_rejection()
    store.migrate()
    app = FastAPI()
    deciqo_app.include(app)
    return TestClient(app, raise_server_exceptions=False)


def _signup(client, email):
    r = client.post("/api/v1/auth/register", json={"email": email, "password": "rahasia123", "name": "M"})
    assert r.status_code == 201
    return r.json()["id"]


def _seed(user_id):
    stats = ingest.upsert_catalog(user_id, "manual", [BAG], data_origin="synthetic")
    pipeline.analyse(stats.products[0])
    return stats.products[0]


def test_inbox_urut_dan_bucket(client):
    uid = _signup(client, "a@x.id")
    _seed(uid)
    items = client.get("/api/v1/deciqo/inbox").json()["items"]
    assert [i["bucket"] for i in items] == ["needs_fact", "to_do"]
    size, delivery = items
    assert size["next"] == "fact" and size["draft_status"] == "needs_merchant_fact"
    assert size["support"] == 3 and size["denominator"] == 4
    assert delivery["next"] == "route" and delivery["draft_status"] is None
    summary = client.get("/api/v1/deciqo/summary").json()
    assert summary["buckets"]["needs_fact"] == 1 and summary["findings_open"] == 2
    assert summary["engine"] == "rules"


def test_fakta_lalu_draf_siap_dan_keputusan(client):
    uid = _signup(client, "b@x.id")
    pid = _seed(uid)
    size = client.get("/api/v1/deciqo/inbox").json()["items"][0]
    r = client.post(f"/api/v1/deciqo/findings/{size['id']}/fact", json={"value": "32 x 24", "unit": "cm"})
    assert r.status_code == 200 and r.json()["unit"] == "cm"
    draft = client.post(f"/api/v1/deciqo/products/{pid}/draft").json()
    assert draft["status"] == "ready"
    assert draft["sections"][0]["text"] == "Ukuran kompartemen dalam: 32 x 24 cm."
    item = next(i for i in client.get("/api/v1/deciqo/inbox").json()["items"] if i["id"] == size["id"])
    assert item["bucket"] == "to_do" and item["next"] == "apply"

    r = client.post(f"/api/v1/deciqo/findings/{size['id']}/decision", json={"decision": "acted"})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "note_required"
    r = client.post(f"/api/v1/deciqo/findings/{size['id']}/decision",
                    json={"decision": "acted", "note": "Menambah ukuran dalam 32 x 24 cm"})
    assert r.status_code == 200
    body = r.json()
    assert body["bucket"] == "monitoring" and body["follow_up"]["state"] == "insufficient_data"

    ops = next(i for i in client.get("/api/v1/deciqo/inbox").json()["items"] if i["bucket"] == "to_do")
    r = client.post(f"/api/v1/deciqo/findings/{ops['id']}/decision", json={"decision": "dismissed"})
    assert r.json()["detail"]["code"] == "reason_required"
    r = client.post(f"/api/v1/deciqo/findings/{ops['id']}/decision",
                    json={"decision": "dismissed", "reason": "wont_fix"})
    assert r.json()["bucket"] == "dismissed"


def test_fakta_kosong_ditolak(client):
    uid = _signup(client, "c@x.id")
    _seed(uid)
    size = client.get("/api/v1/deciqo/inbox").json()["items"][0]
    r = client.post(f"/api/v1/deciqo/findings/{size['id']}/fact", json={"value": "  "})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "not_a_fact"


def test_data_akun_lain_404(client):
    owner = _signup(client, "d@x.id")
    pid = _seed(owner)
    fid = client.get("/api/v1/deciqo/inbox").json()["items"][0]["id"]
    client.post("/api/v1/auth/logout")
    _signup(client, "e@x.id")
    assert client.get(f"/api/v1/deciqo/products/{pid}").status_code == 404
    assert client.post(f"/api/v1/deciqo/findings/{fid}/fact", json={"value": "32 cm"}).status_code == 404
    assert client.post(f"/api/v1/deciqo/findings/{fid}/decision",
                       json={"decision": "acted", "note": "x"}).status_code == 404
    assert client.get("/api/v1/deciqo/inbox").json()["items"] == []


def test_product_view_bentuk_kontrak(client):
    uid = _signup(client, "f@x.id")
    pid = _seed(uid)
    view = client.get(f"/api/v1/deciqo/products/{pid}").json()
    assert view["product"]["listing_provided"] is True
    assert view["analysis"]["engine"] == "rules"
    finding = view["findings"][0]
    for key in ("listing_check", "metrics", "evidence", "contradicting", "rejected", "merchant_question"):
        assert key in finding
    assert finding["listing_check"]["status"] in {"verification_failed", "not_found_in_checked_content",
                                                  "evidence_found"}
    assert client.get("/api/v1/deciqo/channels").json()["channels"][0]["key"] == "manual"


def test_tanpa_sesi_401(client):
    assert client.get("/api/v1/deciqo/inbox").status_code == 401


def test_bucket_dan_next_mengikuti_status_draf(client):
    # expectation_mismatch butuh keterangan merchant sebelum draf; inbox tidak boleh menyuruh
    # "draft" sementara draf sendiri berstatus needs_merchant_fact.
    uid = _signup(client, "g@x.id")
    stats = ingest.upsert_catalog(uid, "manual", [{
        "source_item_id": "sepatu", "title": "Sepatu sneakers", "description": "Sepatu kanvas warna oranye.",
        "reviews": [{"id": "a", "rating": 2, "text": "Warnanya tidak sesuai dengan foto, beda jauh."},
                    {"id": "b", "rating": 1, "text": "Barang tidak sesuai gambar."}]}], data_origin="synthetic")
    pipeline.analyse(stats.products[0])
    items = client.get("/api/v1/deciqo/inbox").json()["items"]
    held = [i for i in items if i["draft_status"] == "needs_merchant_fact"]
    assert held
    assert all(i["bucket"] == "needs_fact" and i["next"] == "fact" for i in held)


def test_endpoint_rencana_keputusan(client):
    assert client.get("/api/v1/deciqo/decisions").status_code == 401
    uid = _signup(client, "h@x.id")
    _seed(uid)
    body = client.get("/api/v1/deciqo/decisions").json()
    assert body["score_kind"] == "heuristic" and body["total"] == len(body["decisions"]) == 2
    assert body["decisions"][0]["next_step"] == "confirm_fact"


def test_pembanding_chatbot_umum_tanpa_key_503(client):
    uid = _signup(client, "i@x.id")
    pid = _seed(uid)
    r = client.post(f"/api/v1/deciqo/products/{pid}/generic")
    assert r.status_code == 503 and r.json()["detail"]["code"] == "generic_unavailable"
    assert client.get(f"/api/v1/deciqo/products/{pid}").json()["generic_draft"] is None
