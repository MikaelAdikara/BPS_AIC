"""Angka Overview: deduplikasi per produk, rentang waktu, filter, dan isolasi akun."""
from datetime import datetime, timezone
from contextlib import nullcontext

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.deciqo import insights, store
from app.deciqo.engine import pipeline


def test_overview_accepts_query_string_ranges(monkeypatch):
    app = FastAPI()
    app.include_router(insights.router)
    app.dependency_overrides[insights.current_user] = lambda: {"id": 1}
    monkeypatch.setattr(insights.store, "database", lambda: nullcontext(None))
    monkeypatch.setattr(insights, "overview_data", lambda conn, uid, days: {"days": days})
    with TestClient(app) as client:
        for days in (7, 30, 90):
            response = client.get(f"/api/v1/deciqo/overview?days={days}")
            assert response.status_code == 200
            assert response.json() == {"days": days}
        assert client.get("/api/v1/deciqo/overview?days=31").status_code == 422


def test_unique_product_review_pairs_dates_and_account_isolation(tmp_path):
    path = tmp_path / "insights.sqlite3"
    store.migrate(path)
    conn = store.connect(path)
    conn.execute("INSERT INTO users(id,email,password_hash,created_at) VALUES (1,'a@x.test','hash',''),(2,'b@x.test','hash','')")
    for pid, uid in [("p1",1),("p2",1),("private",2)]:
        conn.execute("INSERT INTO products(id,user_id,channel,source_item_id,title) VALUES (?,?, 'manual',?,?)",(pid,uid,pid,pid))
        for rid,time in [("r1","2026-09-26T01:00:00Z"),("r2",None),("r3","2026-09-01T01:00:00Z")]:
            conn.execute("INSERT INTO reviews(product_id,id,rating,text,version_hash,review_time) VALUES (?,?,4,'bukti keluhan','h',?)",(pid,rid,time))
        evidence = [{"review_id":"r1","quote":"bukti keluhan"},{"review_id":"r2","quote":"bukti keluhan"},{"review_id":"r3","quote":"bukti keluhan"}]
        for suffix in ("a","b"):
            blob = pipeline.write_evidence(evidence,[],0,{"support":3,"denominator":3,"candidates_read":3,"share":1,"hidden_high_star":3})
            conn.execute("INSERT INTO findings(id,product_id,attribute,attribute_local,finding_type,evidence_json,support,denominator,candidates_read) VALUES (?,?, 'delivery','pengiriman','operational',?,3,3,3)",(pid+suffix,pid,blob))
    data = insights.overview_data(conn,1,7,datetime(2026,9,26,tzinfo=timezone.utc))
    assert data["total"] == 2
    assert data["undated"] == 2
    assert data["affected_products"] == 2
    assert data["average_rating"] == 4
    assert len(data["series"]) == 7 and data["series"][-1]["count"] == 2
    assert data["open"] == 4
    assert all(item["product_id"] != "private" for item in data["plan"])
    assert data["ranking_channels"] == [{"key":"manual","count":4}]
    conn.close()


def test_server_filter_and_sort_preserve_priority_by_default():
    rows=[{"id":"a","product_title":"Tas","channel":"manual","finding_type":"operational","severity":"low","bucket":"to_do","support":1,"denominator":2},
          {"id":"b","product_title":"Kursi","channel":"woocommerce","finding_type":"missing_fact","severity":"high","bucket":"needs_fact","support":3,"denominator":4}]
    assert [row["id"] for row in insights.filter_items(rows)] == ["a","b"]
    assert [row["id"] for row in insights.filter_items(rows,order="share")] == ["b","a"]
    assert [row["id"] for row in insights.filter_items(rows,q="kursi",channel="woocommerce",kind="missing_fact",severity="high")] == ["b"]
    assert insights.filter_items(rows,q="tidak ada") == []
    rows[0]["candidates_read"] = 1
    assert [row["id"] for row in insights.filter_items(rows,order="share")] == ["a","b"]


def test_empty_overview_has_zero_series_and_no_invented_rating(tmp_path):
    path=tmp_path/"empty.sqlite3"
    store.migrate(path)
    conn=store.connect(path)
    data=insights.overview_data(conn,99,30)
    assert len(data["series"]) == 30
    assert data["total"] == 0 and data["plan"] == []
    assert data["average_rating"] is None
    conn.close()
