"""Identitas temuan lintas analisis: parafrasa model tidak boleh membuat isu baru atau memutus
keputusan lama, dan dua usulan untuk keluhan yang sama menjadi satu isu."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.deciqo import ingest, store
from app.deciqo.engine import discovery, llm, pipeline, triage


def _ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0).isoformat()


REVIEWS = [
    {"id": "r1", "rating": 1, "text": "Penjual tidak membalas chat waktu saya tanya soal garansi.", "review_time": _ago(28)},
    {"id": "r2", "rating": 2, "text": "Chat ke penjual dicuekin, responnya lama sekali.", "review_time": _ago(26)},
    {"id": "r3", "rating": 5, "text": "Kursinya kokoh, enak buat mancing.", "review_time": _ago(10)},
]
NEW = {"id": "r4", "rating": 2, "text": "Chat ke penjual tidak dibalas lagi, padahal mau tanya.", "review_time": _ago(0)}


def _finding(attribute, local, ids_quotes, ftype="operational"):
    return {"attribute": attribute, "attribute_local": local, "finding_type": ftype,
            "buyer_expectation": "x", "evidence": [{"review_id": r, "quote": q} for r, q in ids_quotes],
            "listing_evidence": "", "merchant_question": "?", "fix_type": "fix_operations", "severity": "low"}


class ScriptedClient:
    """Mengembalikan discovery berikutnya dari daftar; membership mengulang bukti discovery."""

    def __init__(self, discoveries):
        self.discoveries = list(discoveries)
        self.prompts = []
        self.responses = self
        self.last = None

    def create(self, **kw):
        name = kw["text"]["format"]["name"]
        self.prompts.append((name, kw["input"][1]["content"]))
        if name == "discovery":
            self.last = self.discoveries.pop(0)
            payload = {"findings": self.last, "praised_attributes": []}
        else:
            payload = {"labels": [{"review_id": e["review_id"], "finding": i, "label": "supports", "quote": e["quote"]}
                                  for i, f in enumerate(self.last) for e in f["evidence"]]}
        return SimpleNamespace(status="completed", output_text=json.dumps(payload), incomplete_details=None,
                               usage=SimpleNamespace(input_tokens=100, output_tokens=50,
                                                     input_tokens_details=SimpleNamespace(cached_tokens=0)))


@pytest.fixture()
def db(tmp_path, monkeypatch):
    path = tmp_path / "id.sqlite3"
    monkeypatch.setenv("DECIQO_DB_PATH", str(path))
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    triage.set_text_adapter(None)
    llm.reset_rejection()
    store.migrate(path)
    with store.database(path) as conn:
        conn.execute("INSERT INTO users(email, name, password_hash, created_at) VALUES('a@x.id', 'A', 'x', ?)",
                     (store.now(),))
        stats = ingest.upsert_catalog(1, "manual", [{"source_item_id": "krs", "title": "Kursi lipat camping",
                                                     "description": "Kursi lipat rangka besi.", "reviews": REVIEWS}],
                                      conn=conn)
    yield path, stats.products[0]
    llm.set_client(None)
    llm.reset_rejection()


def _rows(path, pid):
    with store.database(path) as conn:
        return store.rows(conn.execute("SELECT * FROM findings WHERE product_id = ?", (pid,)))


def test_parafrasa_atribut_memakai_isu_lama_dan_membuka_lagi(db):
    path, pid = db
    first = [_finding("seller response time", "respon penjual / waktu balasan",
                      [("r1", "Penjual tidak membalas chat"), ("r2", "Chat ke penjual dicuekin")])]
    second = [_finding("seller chat responsiveness", "respon penjual pada chat",
                       [("r1", "Penjual tidak membalas chat"), ("r2", "Chat ke penjual dicuekin"),
                        ("r4", "Chat ke penjual tidak dibalas lagi")])]
    client = ScriptedClient([first, second])
    llm.set_client(client)
    pipeline.analyse(pid, db_path=path)
    [old] = _rows(path, pid)
    acted_at = _ago(5)
    with store.database(path) as conn:
        conn.execute("INSERT INTO decisions(finding_id, decision, note, acted_at, created_at) VALUES(?, 'acted', 'balas otomatis', ?, ?)",
                     (old["id"], acted_at, acted_at))
        conn.execute("UPDATE findings SET state = 'acted' WHERE id = ?", (old["id"],))
        ingest.upsert_catalog(1, "manual", [{"source_item_id": "krs", "title": "Kursi lipat camping",
                                             "reviews": REVIEWS + [NEW]}], conn=conn)
    pipeline.analyse(pid, db_path=path)
    rows = _rows(path, pid)
    assert [r["id"] for r in rows] == [old["id"]]
    assert rows[0]["state"] == "reopened"
    assert rows[0]["not_detected_at"] is None
    assert rows[0]["attribute_local"] == "respon penjual / waktu balasan"  # label stabil untuk merchant
    # Discovery kedua melihat atribut isu yang sudah ada.
    second_prompt = [p for name, p in client.prompts if name == "discovery"][1]
    assert "seller response time" in second_prompt


def test_dua_usulan_dengan_bukti_sama_menjadi_satu_isu(db):
    path, pid = db
    same = [("r1", "Penjual tidak membalas chat"), ("r2", "Chat ke penjual dicuekin")]
    llm.set_client(ScriptedClient([[_finding("seller responsiveness", "respons penjual", same),
                                    _finding("chat reply speed", "kecepatan balas chat", same)]]))
    pipeline.analyse(pid, db_path=path)
    rows = _rows(path, pid)
    assert len(rows) == 1 and rows[0]["support"] == 2


def test_dedupe_hanya_menggabung_rute_yang_sama():
    def entry(ftype, ids):
        return {"proposal": {"attribute": ftype, "finding_type": ftype},
                "judged": {"supports": {i: {"quote": "q"} for i in ids}, "contradicting": {}, "uncertain": {},
                           "rejected": {}, "wrong_item": set()}}
    built = {"a": entry("missing_fact", ["r1", "r2", "r3"]), "b": entry("unclear_fact", ["r1", "r2", "r3"]),
             "c": entry("product_quality", ["r1", "r2", "r3"]), "d": entry("missing_fact", ["r1", "r9"])}
    merged = pipeline.dedupe(built)
    assert set(merged) == {"a", "c", "d"}  # b ikut a (rute listing sama); c rute kualitas; d tumpang tindih < 80%


def test_prompt_discovery_memuat_isu_lama():
    text = discovery.build_user("t", "l", True, [], 0, existing=[{"attribute": "folded size", "attribute_local": "ukuran lipat"}])
    assert "folded size" in text and "ukuran lipat" in text
