"""Fungsi in-process untuk evaluasi: bundle kasus → temuan + status draf, pada SQLite terpisah."""

from __future__ import annotations

import pytest

from app.deciqo.engine import harness, triage

BUNDLE = {
    "case_id": "t01",
    "title": "Sleeve Laptop Neoprene 14 Inch",
    "listing": "Sleeve laptop bahan neoprene tebal, cocok untuk laptop 14 inch. Ukuran luar 36 x 26 cm.",
    "reviews": [
        {"id": "r1", "rating": 2, "date": "2026-08-30", "text": "laptop 14 inch aku ga muat, resletingnya ga bisa ditutup"},
        {"id": "r2", "rating": 5, "date": "2026-09-02", "text": "bagus sih bahannya tebel tapi agak sempit buat asus 14 inch aku"},
        {"id": "r3", "rating": 3, "date": "2026-09-05", "text": "ukurannya pas buat macbook air 13, sesuai deskripsi"},
        {"id": "r4", "rating": 4, "date": "2026-09-10", "text": "pengiriman cepat, packing rapi"},
    ],
}


@pytest.fixture(autouse=True)
def _no_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    triage.set_text_adapter(None)


def test_sebelum_fakta_draf_ditahan(tmp_path):
    out = harness.run_bundle(BUNDLE, db_path=tmp_path / "a.sqlite3", engine="rules")
    assert out["engine"] == "rules"
    assert out["pipeline_version"] and out["verifier_version"]
    [size] = [f for f in out["findings"] if f["finding_type"] == "missing_fact"]
    assert sorted(size["support_ids"]) == ["r1", "r2"]
    assert size["contradict_ids"] == ["r3"]
    assert size["draft"]["status"] == "needs_merchant_fact"
    assert size["draft"]["text"] == ""


def test_setelah_fakta_draf_dirender_dari_fakta(tmp_path):
    bundle = {**BUNDLE, "fact": "ukuran dalam 34 x 24 cm", "fact_target_words": ["ukuran dalam", "inner"]}
    out = harness.run_bundle(bundle, db_path=tmp_path / "b.sqlite3", engine="rules")
    [size] = [f for f in out["findings"] if f["fact_applied"]]
    assert size["draft"]["status"] == "ready"
    assert "34 x 24 cm" in size["draft"]["text"]


def test_db_terpisah_per_kasus(tmp_path):
    harness.run_bundle(BUNDLE, db_path=tmp_path / "c.sqlite3", engine="rules")
    again = harness.run_bundle(BUNDLE, db_path=tmp_path / "c.sqlite3", engine="rules")
    assert len({f["id"] for f in again["findings"]}) == len(again["findings"])


def test_provider_failure_is_not_success_with_no_findings(tmp_path, monkeypatch):
    from app.deciqo.engine import pipeline
    def fail(*args, **kwargs):
        raise pipeline.AnalysisFailed("provider unavailable")
    monkeypatch.setattr(pipeline, "analyse", fail)
    with pytest.raises(pipeline.AnalysisFailed, match="provider unavailable"):
        harness.run_bundle(BUNDLE, db_path=tmp_path / "failed.sqlite3", engine="ai")
