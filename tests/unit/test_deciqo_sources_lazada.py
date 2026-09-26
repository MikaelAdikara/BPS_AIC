"""Lazada: validasi URL, normalisasi keluaran actor tanpa identitas reviewer, dan anggaran fetch."""

from __future__ import annotations

import httpx
import pytest

from app.deciqo import store
from app.deciqo.connectors import apify
from app.deciqo.errors import DeciqoError

ITEMS = [
    {"type": "product_detail", "itemId": "111", "title": "Powerbank 20000mAh", "url": "https://www.lazada.co.id/products/pb-i111.html",
     "descriptionHtml": "<p>Kapasitas <b>20000mAh</b></p>", "variants": [{"values": [{"name": "Warna", "value": "Hitam"}]}],
     "imageUrl": "https://img/x.jpg", "scrapedAt": "2026-09-26T02:00:00Z"},
    {"type": "review", "itemId": "111", "reviewId": "r1", "rating": 2, "text": "Cuma kuat 2x ngecas",
     "variant": "Warna:Hitam", "reviewer": "Budi Santoso", "reviewTime": "2026-09-12T02:43:38Z"},
]


def test_url_lazada_divalidasi():
    assert apify.product_item_id("https://www.lazada.co.id/products/tas-laptop-i6402408647-s12139872565.html") == "6402408647"
    for bad in ("https://www.tokopedia.com/x", "http://www.lazada.co.id/products/a-i1.html",
                "https://lazada.co.id.evil.com/products/a-i1.html", "https://www.lazada.co.id/catalog/?q=tas"):
        with pytest.raises(DeciqoError):
            apify.product_item_id(bad)


def test_normalisasi_tanpa_nama_reviewer():
    catalog = apify.to_catalog(ITEMS)
    assert catalog[0]["description"] == "Kapasitas 20000mAh"
    assert catalog[0]["variants"] == ["Warna: Hitam"]
    review = catalog[0]["reviews"][0]
    assert review["text"] == "Cuma kuat 2x ngecas" and review["rating"] == 2
    assert "Budi" not in str(catalog)


def test_fetch_menolak_saat_anggaran_habis(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "t.sqlite3"))
    monkeypatch.setenv("APIFY_TOKEN", "t1")
    monkeypatch.setenv("DECIQO_APIFY_BUDGET_USD", "1")
    store.migrate()
    with store.database() as conn:
        conn.execute("INSERT INTO ledger(provider, cost_usd, created_at) VALUES('apify', 0.99, '')")
    with pytest.raises(DeciqoError) as err:
        apify.fetch_products(["https://www.lazada.co.id/products/pb-i111.html"], user_id=None)
    assert err.value.code == "fetch_budget_exhausted"


def test_fetch_mencatat_biaya_di_ledger(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "t.sqlite3"))
    monkeypatch.setenv("APIFY_TOKEN", "t1")
    store.migrate()

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/runs"):
            assert request.url.params["maxTotalChargeUsd"] == "1.0"
            return httpx.Response(201, json={"data": {"id": "run1", "status": "SUCCEEDED",
                                                      "usageTotalUsd": 0.042, "defaultDatasetId": "ds1"}})
        if "/actor-runs/" in request.url.path:
            return httpx.Response(200, json={"data": {"id": "run1", "status": "SUCCEEDED",
                                                      "usageTotalUsd": 0.042, "defaultDatasetId": "ds1"}})
        return httpx.Response(200, json=ITEMS)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    catalog = apify.fetch_products(["https://www.lazada.co.id/products/pb-i111.html"], user_id=None, client=client)
    assert len(catalog) == 1
    with store.database() as conn:
        row = store.row(conn.execute("SELECT * FROM ledger WHERE provider = 'apify'"))
    assert row["cost_usd"] == pytest.approx(0.042) and row["status"] == "ok" and row["reserved_usd"] == 0


def test_tanpa_token_fetch_nonaktif(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "")
    with pytest.raises(DeciqoError) as err:
        apify.run_actor({}, max_charge=0.1, user_id=None, ref="")
    assert err.value.code == "fetch_unconfigured"
