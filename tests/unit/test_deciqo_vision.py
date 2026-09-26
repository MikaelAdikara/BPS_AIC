"""Vision lewat LLM dengan klien palsu: cek foto pembeli, OCR gambar produk, cache, dan skip.

Tidak ada panggilan OpenAI sungguhan: klien dipasang lewat `llm.set_client`.
"""

from __future__ import annotations

import json
import threading
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.deciqo import app as deciqo_app
from app.deciqo import auth, ingest, store
from app.deciqo.connectors import apify
from app.deciqo.engine import listing_check, llm, pipeline, triage, vision, workspace

IMG_MAIN = "https://img.example/main.jpg"
IMG_GALLERY = ["https://img.example/g1.jpg", IMG_MAIN, "https://img.example/g2.jpg"]
BAG = {"source_item_id": "tas", "title": "Tas laptop kanvas 14 inci",
       "description": "Tas kanvas tebal, muat laptop hingga 14 inch.",
       "image_url": IMG_MAIN, "images": IMG_GALLERY,
       "reviews": [{"id": "r1", "rating": 2, "text": "Laptop 14 inch saya tidak muat.",
                    "variant": "Hitam", "images": ["https://img.example/r1a.jpg", "https://img.example/r1b.jpg"]},
                   {"id": "r2", "rating": 3, "text": "Kantong dalamnya sempit, laptop harus dipaksa masuk.",
                    "images": ["https://img.example/r2.jpg", "https://img.example/r2b.jpg"]},
                   {"id": "r3", "rating": 5, "text": "Bagus, tapi agak sempit buat laptop 14 inch.",
                    "images": ["https://img.example/r3.jpg"]},
                   {"id": "r4", "rating": 2, "text": "Pengiriman lama sekali, hampir dua minggu."}]}

DISCOVERY = {"findings": [{
    "attribute": "inner compartment size", "attribute_local": "ukuran kompartemen dalam",
    "finding_type": "missing_fact", "buyer_expectation": "Buyers need the inner size.",
    "evidence": [{"review_id": "r1", "quote": "Laptop 14 inch saya tidak muat"},
                 {"review_id": "r2", "quote": "Kantong dalamnya sempit"}],
    "listing_evidence": "", "merchant_question": "Berapa ukuran dalam tas?",
    "fix_type": "add_fact", "severity": "high"}], "praised_attributes": []}
MEMBERSHIP = {"labels": [
    {"review_id": "r1", "finding": 0, "label": "supports", "quote": "Laptop 14 inch saya tidak muat"},
    {"review_id": "r2", "finding": 0, "label": "supports", "quote": "Kantong dalamnya sempit"}]}


def _response(payload):
    return SimpleNamespace(status="completed", output_text=json.dumps(payload), incomplete_details=None,
                           usage=SimpleNamespace(input_tokens=900, output_tokens=60,
                                                 input_tokens_details=SimpleNamespace(cached_tokens=0)))


class FakeClient:
    def __init__(self, verdict="supports", lines=("20000mAh", "Fast Charging 22.5W")):
        self.verdict = verdict
        self.lines = list(lines)
        self.calls: list[str] = []
        self.kwargs: list[dict] = []
        self.responses = self
        self._lock = threading.Lock()

    def create(self, **kw):
        name = kw["text"]["format"]["name"]
        with self._lock:
            self.calls.append(name)
            self.kwargs.append(kw)
        if name == "buyer_photo_check":
            return _response({"verdict": self.verdict, "reason": "Foto memperlihatkan laptop tidak masuk."})
        if name == "product_image_ocr":
            return _response({"lines": self.lines})
        return _response(DISCOVERY if name == "discovery" else MEMBERSHIP)

    def vision_calls(self):
        return [c for c in self.calls if c in {"buyer_photo_check", "product_image_ocr"}]


class NoCallClient:
    responses = property(lambda self: (_ for _ in ()).throw(AssertionError("model dipanggil")))


@pytest.fixture()
def db(tmp_path, monkeypatch):
    path = tmp_path / "vision.sqlite3"
    monkeypatch.setenv("DECIQO_DB_PATH", str(path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DECIQO_VISION", raising=False)
    monkeypatch.setenv("DECIQO_AI_BUDGET_USD", "5")
    triage.set_text_adapter(None)
    llm.reset_rejection()
    store.migrate(path)
    with store.database(path) as conn:
        conn.execute("INSERT INTO users(email, name, password_hash, lang, created_at) VALUES('a@x.id', 'A', 'x', 'id', ?)",
                     (store.now(),))
        stats = ingest.upsert_catalog(1, "manual", [BAG], conn=conn)
    pid = stats.products[0]
    pipeline.analyse(pid, db_path=path)  # mode aturan: temuan ukuran (r1, r2, r3) + operasional (r4)
    yield path, pid
    llm.set_client(None)
    llm.reset_rejection()


def _with_key(monkeypatch, client):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    llm.set_client(client)


def _product(path, pid):
    with store.database(path) as conn:
        return store.row(conn.execute("SELECT * FROM products WHERE id = ?", (pid,)))


def _view(path, pid):
    product = _product(path, pid)
    with store.database(path) as conn:
        return workspace.product_view(conn, product)


def _findings(path, pid):
    with store.database(path) as conn:
        return store.rows(conn.execute("SELECT * FROM findings WHERE product_id = ? ORDER BY id", (pid,)))


# --- prompt & parsing ------------------------------------------------------------------------


def test_parse_verdict_abstain_bila_di_luar_enum():
    assert vision.parse_verdict({"verdict": "supports", "reason": "  jelas   terlihat "}) == {
        "verdict": "supports", "reason": "jelas terlihat"}
    assert vision.parse_verdict({"verdict": "yes", "reason": "x"})["verdict"] == "inconclusive"
    assert vision.parse_verdict(None) == {"verdict": "inconclusive", "reason": ""}
    assert len(vision.parse_verdict({"verdict": "contradicts", "reason": "a" * 999})["reason"]) == 240


def test_prompt_spesifik_ke_temuan():
    finding = {"attribute": "battery capacity", "attribute_local": "kapasitas baterai",
               "buyer_expectation": "20000mAh sungguhan"}
    item = {"review_id": "r1", "quote": "cepat habis", "rating": 2, "variant": "Putih"}
    text = vision.photo_prompt({"title": "Powerbank"}, finding, item, None)
    assert "Does this buyer photo show the problem: kapasitas baterai?" in text
    assert '"cepat habis"' in text and "Putih" in text and "20000mAh sungguhan" in text
    assert "inconclusive" in vision.PHOTO_SYSTEM and "battery capacity" in vision.PHOTO_SYSTEM


def test_parse_ocr_verbatim_unik():
    assert vision.parse_ocr({"lines": [" 20000mAh ", "20000mAh", "Fast  Charging 22.5W", ""]}) == \
        "20000mAh\nFast Charging 22.5W"
    assert vision.parse_ocr({}) == ""


def test_call_json_mengirim_gambar_detail_low_dan_reservasi_per_gambar(db, monkeypatch):
    path, _ = db
    client = FakeClient()
    _with_key(monkeypatch, client)
    kwargs = dict(purpose="vision", system="s", user="u", schema=vision.PHOTO_SCHEMA,
                  schema_name="buyer_photo_check", max_output_tokens=100, db_path=path)
    llm.call_json(**kwargs)
    llm.call_json(**kwargs, images=["https://img.example/a.jpg", "https://img.example/b.jpg"])
    content = client.kwargs[1]["input"][1]["content"]
    assert content[0] == {"type": "input_text", "text": "u"}
    assert content[1:] == [{"type": "input_image", "image_url": "https://img.example/a.jpg", "detail": "low"},
                           {"type": "input_image", "image_url": "https://img.example/b.jpg", "detail": "low"}]
    assert client.kwargs[0]["input"][1]["content"] == "u"
    with store.database(path) as conn:
        plain, imaged = [r["reserved_usd"] for r in conn.execute("SELECT reserved_usd FROM ledger ORDER BY id")]
        assert {r[0] for r in conn.execute("SELECT purpose FROM ledger")} == {"vision"}
    extra = 2 * llm.IMAGE_RESERVE_TOKENS * llm.prices()["in"] / 1_000_000
    assert imaged - plain == pytest.approx(extra)


# --- skip ------------------------------------------------------------------------------------


def test_tanpa_key_dilewati_tanpa_exception_dan_tanpa_panggilan(db):
    path, pid = db
    llm.set_client(NoCallClient())
    result = vision.run_all(pid, db_path=path)
    assert result["ocr"]["status"] == "skipped" and result["ocr"]["reason"] == "no_api_key"
    assert result["photos"]["status"] == "skipped" and result["photos"]["reason"] == "no_api_key"
    view = _view(path, pid)
    assert view["product"]["image_ocr"] == {"status": "skipped", "images_read": 0, "images_total": 3,
                                            "reason": "no_api_key"}
    size = next(f for f in view["findings"] if f["vision_summary"])
    assert size["vision_summary"]["checked"] == 0 and size["vision_summary"]["skipped_reason"] == "no_api_key"


def test_anggaran_habis_berstatus_budget(db, monkeypatch):
    path, pid = db
    client = FakeClient()
    _with_key(monkeypatch, client)
    monkeypatch.setenv("DECIQO_AI_BUDGET_USD", "0")
    result = vision.run_all(pid, db_path=path)
    assert client.calls == []
    assert result["ocr"]["reason"] == "budget" and result["photos"]["reason"] == "budget"


def test_vision_off_dilewati(db, monkeypatch):
    path, pid = db
    _with_key(monkeypatch, NoCallClient())
    monkeypatch.setenv("DECIQO_VISION", "off")
    assert vision.run_photo_checks(pid, db_path=path)["reason"] == "disabled"


# --- cek foto pembeli ------------------------------------------------------------------------


def test_cek_foto_dicache_dan_tidak_mengubah_temuan(db, monkeypatch):
    path, pid = db
    before = _findings(path, pid)
    client = FakeClient()
    _with_key(monkeypatch, client)
    first = vision.run_photo_checks(pid, db_path=path)
    # Temuan ukuran: bukti rating ≤3 dengan foto = r1 (2 foto) + r2 (2 foto) → dibatasi 3 foto.
    # r3 (rating 5) dan r4 (tanpa foto) tidak diperiksa.
    assert first["status"] == "done" and first["checked"] == 3
    assert client.calls == ["buyer_photo_check"] * 3
    sent = {kw["input"][1]["content"][1]["image_url"] for kw in client.kwargs}
    assert "https://img.example/r3.jpg" not in sent and len(sent) == 3
    assert "Bahasa Indonesia" in client.kwargs[0]["input"][0]["content"]
    second = vision.run_photo_checks(pid, db_path=path)
    assert len(client.calls) == 3 and second["cached"] == 3 and second["checked"] == 0
    after = _findings(path, pid)
    assert before == after  # vision hanya bukti: tidak mengubah temuan apa pun
    with store.database(path) as conn:
        rows = store.rows(conn.execute("SELECT * FROM vision_checks"))
    assert len(rows) == 3 and all(r["verdict"] == "supports" and r["user_id"] == 1 for r in rows)
    assert all(r["prompt_version"] == f"{vision.PHOTO_PROMPT_VERSION}:id" for r in rows)


class BadRequestError(Exception):
    pass


class UnreadableClient(FakeClient):
    def create(self, **kw):
        if kw["text"]["format"]["name"] == "buyer_photo_check":
            with self._lock:
                self.calls.append("buyer_photo_check")
            raise BadRequestError("image url could not be downloaded")
        return super().create(**kw)


def test_foto_tak_terbaca_dicatat_tidak_jelas_bukan_error(db, monkeypatch):
    path, pid = db
    client = UnreadableClient()
    _with_key(monkeypatch, client)
    first = vision.run_photo_checks(pid, db_path=path)
    assert first["status"] == "done" and first["checked"] == 3 and not first.get("reason")
    with store.database(path) as conn:
        rows = store.rows(conn.execute("SELECT verdict, reason FROM vision_checks"))
    assert rows and all(r["verdict"] == "inconclusive" and r["reason"] == vision.UNREADABLE["id"] for r in rows)
    vision.run_photo_checks(pid, db_path=path)
    assert len(client.calls) == 3  # sudah dicatat: tidak dicoba ulang


def test_bentuk_evidence_dan_ringkasan_vision(db, monkeypatch):
    path, pid = db
    _with_key(monkeypatch, FakeClient(verdict="inconclusive"))
    vision.run_all(pid, db_path=path)
    view = _view(path, pid)
    product = view["product"]
    assert product["images"] == [IMG_MAIN, "https://img.example/g1.jpg", "https://img.example/g2.jpg"]
    assert product["image_ocr"] == {"status": "done", "images_read": 3, "images_total": 3}
    by_id = {r["id"]: r for r in view["reviews"]}
    assert by_id["r1"]["images"] == BAG["reviews"][0]["images"] and by_id["r4"]["images"] == []
    size = next(f for f in view["findings"] if f["vision_summary"])
    for item in size["evidence"]:
        assert isinstance(item["images"], list)
        assert item["vision"] is None or set(item["vision"]) == {"verdict", "reason", "model", "checked_at"}
    r1 = next(i for i in size["evidence"] if i["review_id"] == "r1")
    assert r1["vision"]["verdict"] == "inconclusive" and r1["vision"]["model"] == llm.model_name()
    r3 = next((i for i in size["evidence"] if i["review_id"] == "r3"), None)
    if r3:
        assert r3["images"] == ["https://img.example/r3.jpg"] and r3["vision"] is None
    assert size["vision_summary"] == {"checked": 2, "supports": 0, "contradicts": 0, "inconclusive": 2}
    delivery = next(f for f in view["findings"] if f is not size)
    assert delivery["vision_summary"] is None  # tidak ada foto layak diperiksa


# --- OCR gambar produk -----------------------------------------------------------------------


def test_ocr_masuk_listing_parts_dan_cakupan(db, monkeypatch):
    path, pid = db
    client = FakeClient()
    _with_key(monkeypatch, client)
    result = vision.run_ocr(pid, db_path=path)
    assert result == {"status": "done", "reason": None, "images_read": 3, "images_total": 3, "changed": True}
    assert client.calls == ["product_image_ocr"] * 3
    product = _product(path, pid)
    listing, provided = pipeline.listing_parts(product)
    assert provided
    assert listing.startswith("Tas kanvas tebal")
    assert "\n\nText on product images:\n20000mAh\nFast Charging 22.5W" in listing
    assert vision.ocr_counts(product) == (3, 3)
    check = listing_check.check({"finding_type": "missing_fact", "attribute": "battery capacity",
                                 "listing_evidence": "20000mAh"}, listing, provided, images=(3, 3))
    assert check["status"] == "evidence_found" and check["quote"] == "20000mAh"
    assert check["coverage"]["images_read"] == 3 and check["coverage"]["images_total"] == 3
    # Run kedua: semua dari cache, tidak ada panggilan baru, teks tidak berubah.
    again = vision.run_ocr(pid, db_path=path)
    assert len(client.calls) == 3 and again["changed"] is False


def test_analisis_ai_menjalankan_ocr_sebelum_listing_dan_cek_foto_di_akhir(db, monkeypatch):
    path, pid = db
    client = FakeClient()
    _with_key(monkeypatch, client)
    result = pipeline.analyse(pid, db_path=path, force=True)
    assert result["engine"] == "ai"
    assert client.calls[:3] == ["product_image_ocr"] * 3  # OCR sebelum discovery
    assert client.calls[-1] == "buyer_photo_check"
    assert result["vision"]["status"] == "done"
    [f] = [f for f in _findings(path, pid) if f["not_detected_at"] is None and f["finding_type"] == "missing_fact"]
    coverage = store.loads(f["listing_check_json"])["coverage"]
    assert coverage["images_read"] == 3 and coverage["images_total"] == 3
    discovery_kw = next(kw for kw in client.kwargs if kw["text"]["format"]["name"] == "discovery")
    assert "Text on product images:" in discovery_kw["input"][1]["content"]
    calls = len(client.calls)
    again = pipeline.analyse(pid, db_path=path)
    assert again["status"] == "unchanged" and len(client.calls) == calls  # semuanya dari cache


def test_vision_error_tidak_menggagalkan_analisis(db, monkeypatch):
    path, pid = db
    client = FakeClient()
    _with_key(monkeypatch, client)
    monkeypatch.setattr(vision, "run_photo_checks", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    result = pipeline.analyse(pid, db_path=path, force=True)
    assert result["status"] == "ready" and result["vision"] == {"status": "skipped", "reason": "error"}


# --- data gambar -----------------------------------------------------------------------------


def test_apify_menyimpan_galeri_produk():
    items = [{"type": "product_detail", "itemId": 7, "title": "Powerbank", "imageUrl": "https://x/main.jpg",
              "images": ["https://x/main.jpg", "//x/2.jpg", {"url": "https://x/3.jpg"}, 5],
              "imageUrls": ["https://x/2.jpg", "https://x/4.jpg"]},
             {"type": "review", "itemId": 7, "reviewId": 1, "rating": 2, "text": "cepat habis",
              "images": ["https://x/r.jpg"]}]
    [product] = apify.to_catalog(items)
    assert product["images"] == ["https://x/2.jpg", "https://x/3.jpg", "https://x/4.jpg"]
    assert product["reviews"][0]["images"] == ["https://x/r.jpg"]


def test_impor_tanpa_kunci_images_mempertahankan_galeri(db):
    path, pid = db
    with store.database(path) as conn:
        ingest.upsert_catalog(1, "manual", [{"source_item_id": "tas", "title": BAG["title"], "image_url": IMG_MAIN}],
                              conn=conn)
    assert vision.product_images(_product(path, pid)) == [IMG_MAIN, "https://img.example/g1.jpg",
                                                         "https://img.example/g2.jpg"]


# --- endpoint --------------------------------------------------------------------------------


def test_endpoint_vision_milik_sendiri_dan_skip_tanpa_key(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "r.sqlite3"))
    monkeypatch.setenv("DECIQO_ALLOW_SIGNUP", "true")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    auth._failures.clear()
    triage.set_text_adapter(None)
    llm.reset_rejection()
    llm.set_client(NoCallClient())
    store.migrate()
    app = FastAPI()
    deciqo_app.include(app)
    client = TestClient(app, raise_server_exceptions=False)
    r = client.post("/api/v1/auth/register", json={"email": "a@x.id", "password": "rahasia123", "name": "M"})
    uid = r.json()["id"]
    pid = ingest.upsert_catalog(uid, "manual", [BAG]).products[0]
    pipeline.analyse(pid)
    body = client.post(f"/api/v1/deciqo/products/{pid}/vision").json()
    assert body["job_id"] is None
    assert body["vision_run"]["photos"]["reason"] == "no_api_key"
    assert body["product"]["image_ocr"]["status"] == "skipped"
    assert all("vision_summary" in f for f in body["findings"])
    client.post("/api/v1/auth/logout")
    client.post("/api/v1/auth/register", json={"email": "b@x.id", "password": "rahasia123", "name": "B"})
    assert client.post(f"/api/v1/deciqo/products/{pid}/vision").status_code == 404
    llm.set_client(None)
