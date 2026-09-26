"""Rencana keputusan: heuristik yang bisa dijelaskan, semua driver dikembalikan."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.deciqo import ingest, store
from app.deciqo.engine import decision, llm, pipeline, triage


def _ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0).isoformat()


@pytest.fixture()
def db(tmp_path, monkeypatch):
    path = tmp_path / "d.sqlite3"
    monkeypatch.setenv("DECIQO_DB_PATH", str(path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    triage.set_text_adapter(None)
    llm.reset_rejection()
    store.migrate(path)
    with store.database(path) as conn:
        conn.execute("INSERT INTO users(email, name, password_hash, created_at) VALUES('d@x.id', 'D', 'x', ?)",
                     (store.now(),))
    return path


def _product(path, sid, title, listing, reviews, channel="manual", units=None):
    with store.database(path) as conn:
        stats = ingest.upsert_catalog(1, channel, [{"source_item_id": sid, "title": title, "description": listing,
                                                    "units_sold": units, "reviews": reviews}], conn=conn)
    pipeline.analyse(stats.products[0], db_path=path)
    return stats.products[0]


BAG_REVIEWS = [
    {"id": "a", "rating": 5, "text": "Bagus tapi agak sempit buat laptop 14 inch.", "review_time": _ago(5)},
    {"id": "b", "rating": 2, "text": "Laptop 14 inch saya tidak muat.", "review_time": _ago(10)},
    {"id": "c", "rating": 2, "text": "Kantong dalamnya sempit.", "review_time": _ago(20)},
    {"id": "d", "rating": 5, "text": "Warnanya bagus.", "review_time": _ago(200)},
]


def test_urutan_skor_dan_driver(db):
    _product(db, "tas", "Tas laptop kanvas", "Tas kanvas muat laptop 14 inch.", BAG_REVIEWS, units=300)
    _product(db, "krs", "Kursi lipat camping", "Kursi rangka besi.",
             [{"id": "x", "rating": 2, "text": "Pengiriman lama sekali.", "review_time": _ago(3)},
              {"id": "y", "rating": 5, "text": "Kokoh.", "review_time": _ago(4)}])
    with store.database(db) as conn:
        plan = decision.plan(conn, 1)
    assert plan["score_kind"] == "heuristic"
    first, *rest = plan["decisions"]
    assert first["attribute_local"] == "ukuran kompartemen dalam"
    assert first["next_step"] == "confirm_fact"
    keys = {d["key"] for d in first["drivers"]}
    assert {"reach", "hidden", "effort"} <= keys
    reach = next(d for d in first["drivers"] if d["key"] == "reach")
    assert reach["support"] == 3 and 0 < reach["confident_share"] < reach["share"]
    effort = next(d for d in first["drivers"] if d["key"] == "effort")
    assert effort["minutes"] == 10 and effort["measured"] is False
    assert all(first["score"] >= d["score"] for d in rest)


def test_satu_laporan_diberi_penalti(db):
    _product(db, "krs", "Kursi lipat camping", "Kursi rangka besi.",
             [{"id": "x", "rating": 2, "text": "Pengiriman lama sekali.", "review_time": _ago(3)},
              {"id": "y", "rating": 5, "text": "Kokoh.", "review_time": _ago(4)}])
    with store.database(db) as conn:
        [only] = decision.plan(conn, 1)["decisions"]
    assert any(d["key"] == "single_report" for d in only["drivers"])


def test_isu_yang_dipantau_atau_diabaikan_tidak_masuk_rencana(db):
    pid = _product(db, "tas", "Tas laptop kanvas", "Tas kanvas muat laptop 14 inch.", BAG_REVIEWS)
    with store.database(db) as conn:
        conn.execute("UPDATE findings SET state = 'dismissed' WHERE product_id = ?", (pid,))
        assert decision.plan(conn, 1)["decisions"] == []


def test_pola_lintas_produk_dan_channel_adalah_kandidat(db):
    _product(db, "tas", "Tas laptop kanvas 14 inch", "Tas kanvas muat laptop 14 inch.", BAG_REVIEWS, channel="manual")
    _product(db, "tas2", "Tas laptop kanvas 14 inci hitam", "Tas kanvas.", BAG_REVIEWS, channel="tokopedia")
    with store.database(db) as conn:
        plan = decision.plan(conn, 1)
    assert plan["patterns"] and plan["patterns"][0]["products"] == 2
    assert plan["cross_channel"] and plan["cross_channel"][0]["similarity"] >= 0.5
    assert plan["cross_channel"][0]["kind"] == "candidate"
