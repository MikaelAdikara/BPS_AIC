"""Pipeline engine end-to-end pada SQLite sementara (mode aturan, tanpa panggilan model)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.deciqo import ingest, store
from app.deciqo.engine import pipeline, triage


def _ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0).isoformat()


BAG = {
    "source_item_id": "tas-1",
    "title": "Tas laptop kanvas 14 inci",
    "description": "Tas laptop bahan kanvas tebal, muat laptop hingga 14 inch. Warna hitam.",
    "reviews": [
        {"id": "r1", "rating": 2, "text": "Laptop 14 inch saya tidak muat, resletingnya gak bisa ditutup rapat.", "review_time": _ago(20)},
        {"id": "r2", "rating": 3, "text": "Kantong dalamnya sempit, laptop 14 inci harus dipaksa masuk.", "review_time": _ago(15)},
        {"id": "r3", "rating": 5, "text": "Bahannya bagus dan jahitannya rapi, tapi agak sempit buat laptop 14 inch saya.", "review_time": _ago(9)},
        {"id": "r4", "rating": 5, "text": "Ukurannya pas untuk laptop 13 inch saya, masuk dengan mudah.", "review_time": _ago(6)},
    ],
}


@pytest.fixture()
def db(tmp_path, monkeypatch):
    path = tmp_path / "engine.sqlite3"
    monkeypatch.setenv("DECIQO_DB_PATH", str(path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    triage.set_text_adapter(None)
    store.migrate(path)
    with store.database(path) as conn:
        conn.execute("INSERT INTO users(email, name, password_hash, created_at) VALUES('e@x.id', 'E', 'x', ?)",
                     (store.now(),))
    return path


def _ingest(path, product, user_id=1):
    with store.database(path) as conn:
        stats = ingest.upsert_catalog(user_id, "manual", [product], data_origin="synthetic", conn=conn)
    return stats.products[0]


def _findings(path, pid):
    with store.database(path) as conn:
        return store.rows(conn.execute("SELECT * FROM findings WHERE product_id = ?", (pid,)))


def test_attribute_key_menyatukan_parafrasa():
    assert pipeline.attribute_key("Inner compartment dimensions") == pipeline.attribute_key("inside compartment size")
    assert pipeline.attribute_key("Size of the product") == pipeline.attribute_key("product sizing")


def test_triage_recomputes_cached_signal_after_lexicon_change(db):
    review = {"id": "r-cache", "text": "Jahitan berantakan.", "version_hash": "same"}
    old = {"v": "same", "model": triage.LEXICON_ONLY, "lexicon": False, "neg_aspects": [],
           "lexicon_version": "lexicon-old"}
    signal = triage.signals([{**review, "triage_json": store.dumps(old)}])["r-cache"]
    assert signal["lexicon"] is True
    from app.deciqo.engine import lexicon
    assert signal["lexicon_version"] == lexicon.LEXICON_VERSION


def test_analisis_aturan_menghitung_dukungan_dari_kode(db):
    pid = _ingest(db, BAG)
    result = pipeline.analyse(pid, db_path=db)
    assert result["engine"] == "rules"
    [finding] = [f for f in _findings(db, pid) if "size" in f["attribute_key"]]
    assert finding["support"] == 3
    assert finding["denominator"] == 4
    assert finding["contradicting"] == 1
    evidence = pipeline.read_evidence(finding["evidence_json"])
    assert evidence["metrics"]["hidden_high_star"] == 1
    for item in evidence["items"]:
        text = next(r["text"] for r in BAG["reviews"] if r["id"] == item["review_id"])
        assert item["quote"] in text
    assert finding["severity"] == "high"


def test_id_temuan_stabil_dan_denominator_ikut_berubah(db):
    pid = _ingest(db, BAG)
    pipeline.analyse(pid, db_path=db)
    first = {f["id"] for f in _findings(db, pid)}
    extra = {**BAG, "reviews": BAG["reviews"] + [{"id": "r5", "rating": 5, "text": "Warna hitamnya elegan."}]}
    _ingest(db, extra)
    pipeline.analyse(pid, db_path=db)
    findings = _findings(db, pid)
    assert {f["id"] for f in findings} == first
    assert all(f["denominator"] == 5 for f in findings)


def test_pujian_saja_tidak_menghasilkan_temuan(db):
    pid = _ingest(db, {"source_item_id": "btl", "title": "Botol minum stainless 750 ml",
                       "description": "Botol 750 ml, tutup ulir anti bocor.",
                       "reviews": [{"id": "a", "rating": 5, "text": "Ukuran sesuai, pas dibawa ke kantor."},
                                   {"id": "b", "rating": 3, "text": "Ukurannya pas di tas, airnya tetap dingin."},
                                   {"id": "c", "rating": 4, "text": "Tutupnya rapat, tidak bocor di dalam tas."}]})
    pipeline.analyse(pid, db_path=db)
    assert _findings(db, pid) == []


def test_salah_kirim_dirutekan_ke_operasional(db):
    pid = _ingest(db, {"source_item_id": "kmj", "title": "Kemeja linen", "description": "Ukuran S, M, L, XL.",
                       "reviews": [{"id": "a", "rating": 2, "text": "Ukuran L kekecilan di dada."},
                                   {"id": "b", "rating": 1, "text": "Pesan ukuran L yang datang malah M, kecewa."}]})
    pipeline.analyse(pid, db_path=db)
    findings = {f["finding_type"]: f for f in _findings(db, pid)}
    size = next(f for f in findings.values() if "size" in f["attribute_key"])
    assert [i["review_id"] for i in pipeline.read_evidence(size["evidence_json"])["items"]] == ["a"]
    ops = findings["operational"]
    assert [i["review_id"] for i in pipeline.read_evidence(ops["evidence_json"])["items"]] == ["b"]


def test_hasil_kosong_merekonsiliasi_temuan_lama(db):
    pid = _ingest(db, BAG)
    pipeline.analyse(pid, db_path=db)
    with store.database(db) as conn:
        conn.execute("UPDATE reviews SET deleted_at = ? WHERE product_id = ? AND id IN ('r1','r2','r3')",
                     (store.now(), pid))
    pipeline.analyse(pid, db_path=db)
    assert all(f["not_detected_at"] for f in _findings(db, pid))


def test_analisis_ulang_setelah_acted_dan_dismissed_tidak_crash(db):
    pid = _ingest(db, BAG)
    pipeline.analyse(pid, db_path=db)
    [f] = [f for f in _findings(db, pid) if "size" in f["attribute_key"]]
    with store.database(db) as conn:
        conn.execute("UPDATE findings SET state = 'dismissed', evidence_json = '[]' WHERE id = ?", (f["id"],))
    pipeline.analyse(pid, force=True, db_path=db)
    [again] = [x for x in _findings(db, pid) if x["id"] == f["id"]]
    assert again["state"] == "dismissed"
    assert pipeline.read_evidence(again["evidence_json"])["metrics"]["support"] == 3


def test_reopen_hanya_dari_ulasan_setelah_tindakan(db):
    pid = _ingest(db, BAG)
    pipeline.analyse(pid, db_path=db)
    [f] = [f for f in _findings(db, pid) if "size" in f["attribute_key"]]
    acted_at = _ago(3)
    with store.database(db) as conn:
        conn.execute("INSERT INTO decisions(finding_id, decision, note, acted_at, created_at) "
                     "VALUES(?, 'acted', 'tambah ukuran dalam', ?, ?)", (f["id"], acted_at, acted_at))
        conn.execute("UPDATE findings SET state = 'acted' WHERE id = ?", (f["id"],))
    # Ulasan lama yang baru diimpor (ditulis sebelum tindakan) tidak membuka isu.
    old = {**BAG, "reviews": BAG["reviews"] + [
        {"id": "r6", "rating": 2, "text": "Tidak muat untuk laptop 14 inch.", "review_time": _ago(10)}]}
    _ingest(db, old)
    pipeline.analyse(pid, db_path=db)
    assert next(x for x in _findings(db, pid) if x["id"] == f["id"])["state"] == "acted"
    new = {**old, "reviews": old["reviews"] + [
        {"id": "r7", "rating": 2, "text": "Laptop 14 inch tetap tidak muat.", "review_time": _ago(0)}]}
    _ingest(db, new)
    pipeline.analyse(pid, db_path=db)
    assert next(x for x in _findings(db, pid) if x["id"] == f["id"])["state"] == "reopened"


def test_listing_kosong_berstatus_not_provided(db):
    pid = _ingest(db, {"source_item_id": "x", "title": "Tas ransel", "reviews": BAG["reviews"]})
    pipeline.analyse(pid, db_path=db)
    [f] = [f for f in _findings(db, pid) if "size" in f["attribute_key"]]
    assert store.loads(f["listing_check_json"])["status"] == "not_provided"
