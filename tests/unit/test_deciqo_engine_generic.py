"""Pembanding chatbot umum: bundle yang sama, pemeriksa yang sama, kalimat terblokir ditampilkan."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.deciqo import ingest, store
from app.deciqo.engine import generic, llm, triage

TEXT = ("Tas laptop kanvas tebal, muat laptop hingga 14 inch. Ukuran kompartemen dalam 34 x 24 cm. "
        "Bahan kulit asli dan garansi 1 tahun. Warna hitam.")


class Client:
    def __init__(self):
        self.calls = 0
        self.responses = self

    def create(self, **kw):
        self.calls += 1
        payload = {"problems": [{"problem": "Tas sempit untuk laptop 14 inch", "suggestion": "Tulis ukuran dalam"}],
                   "listing_text": TEXT}
        return SimpleNamespace(status="completed", output_text=json.dumps(payload), incomplete_details=None,
                               usage=SimpleNamespace(input_tokens=500, output_tokens=200,
                                                     input_tokens_details=SimpleNamespace(cached_tokens=0)))


@pytest.fixture()
def product(tmp_path, monkeypatch):
    path = tmp_path / "g.sqlite3"
    monkeypatch.setenv("DECIQO_DB_PATH", str(path))
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    triage.set_text_adapter(None)
    llm.reset_rejection()
    store.migrate(path)
    with store.database(path) as conn:
        conn.execute("INSERT INTO users(email, name, password_hash, created_at) VALUES('g@x.id', 'G', 'x', ?)",
                     (store.now(),))
        stats = ingest.upsert_catalog(1, "manual", [{
            "source_item_id": "tas", "title": "Tas laptop kanvas",
            "description": "Tas laptop bahan kanvas tebal, muat laptop hingga 14 inch. Warna hitam.",
            "reviews": [{"id": "r1", "rating": 2, "text": "Laptop 14 inch saya tidak muat."}]}], conn=conn)
    yield path, stats.products[0]
    llm.set_client(None)


def test_kalimat_tanpa_sumber_diblokir_dan_ditampilkan_terpisah(product):
    path, pid = product
    llm.set_client(Client())
    result = generic.run(pid, db_path=path)
    blocked = [s for s in result["sentences"] if s["status"] == "blocked"]
    assert {r for s in blocked for r in s["reasons"]} == {"unsupported_quantity", "unsupported_claim"}
    assert "34 x 24 cm" not in result["passed_text"] and "kulit asli" not in result["passed_text"]
    assert "Warna hitam." in result["passed_text"]
    assert result["counts"] == {"sentences": 4, "blocked": 2}
    assert result["system"] == "generic_chatbot" and result["same_bundle"] is True


def test_hasil_di_cache_per_input(product):
    path, pid = product
    client = Client()
    llm.set_client(client)
    generic.run(pid, db_path=path)
    generic.run(pid, db_path=path)
    assert client.calls == 1


def test_tanpa_key_tidak_tersedia(product, monkeypatch):
    path, pid = product
    monkeypatch.delenv("OPENAI_API_KEY")
    with pytest.raises(Exception) as info:
        generic.run(pid, db_path=path)
    assert getattr(info.value, "code", "") == "generic_unavailable"
