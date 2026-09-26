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


def test_landscape_splits_volume_ratings_and_map_by_channel(tmp_path):
    path=tmp_path/"map.sqlite3"
    store.migrate(path)
    conn=store.connect(path)
    conn.execute("INSERT INTO users(id,email,password_hash,created_at) VALUES (1,'a@x.test','hash',''),(2,'b@x.test','hash','')")
    for pid,uid,channel in [("p1",1,"lazada"),("p2",1,"tokopedia"),("x",2,"lazada")]:
        conn.execute("INSERT INTO products(id,user_id,channel,source_item_id,title) VALUES (?,?,?,?,?)",(pid,uid,channel,pid,pid))
    rows=[("p1","r1",5,"2026-09-26T01:00:00Z"),("p1","r2",1,"2026-09-25T01:00:00Z"),("p2","r3",None,"2026-09-26T02:00:00Z"),
          ("p2","r4",3,None),("x","r5",1,"2026-09-26T01:00:00Z")]
    for pid,rid,rating,time in rows:
        conn.execute("INSERT INTO reviews(product_id,id,rating,text,version_hash,review_time) VALUES (?,?,?,'teks','h',?)",(pid,rid,rating,time))
    blob=pipeline.write_evidence([{"review_id":"r2","quote":"teks"}],[],0,{"support":1,"denominator":2,"candidates_read":2})
    conn.execute("INSERT INTO findings(id,product_id,attribute,attribute_local,finding_type,evidence_json,support,denominator,candidates_read) VALUES ('f1','p1','delivery','pengiriman','operational',?,1,2,2)",(blob,))
    data=insights.overview_data(conn,1,7,datetime(2026,9,26,tzinfo=timezone.utc))
    assert data["channels"] == ["lazada","tokopedia"]
    assert data["volume_by_channel"][-1] == {"date":"2026-09-26","lazada":1,"tokopedia":1}
    assert data["evidence_by_channel"][-2] == {"date":"2026-09-25","lazada":1,"tokopedia":0}
    assert data["ratings_by_channel"] == {"lazada":[1,0,0,0,1],"tokopedia":[0,0,1,0,0]}
    assert data["ratings_window_by_channel"] == {"lazada":[1,0,0,0,1]}
    assert {p["id"] for p in data["map"]["products"]} == {"p1","p2"}
    assert [f["id"] for f in data["map"]["findings"]] == ["f1"]
    assert data["map"]["findings"][0]["aspect"] == "delivery"
    conn.close()


def test_channels_report_units_sold_and_sampling(tmp_path):
    from app.deciqo.engine import workspace
    path=tmp_path/"channels.sqlite3"
    store.migrate(path)
    conn=store.connect(path)
    conn.execute("INSERT INTO users(id,email,password_hash,created_at) VALUES (1,'a@x.test','hash','')")
    for pid,channel,units,sampling in [("a","tokopedia",120,"skewed"),("b","tokopedia",30,"unknown"),("c","lazada",None,"skewed")]:
        conn.execute("INSERT INTO products(id,user_id,channel,source_item_id,title,units_sold,sampling) VALUES (?,1,?,?,?,?,?)",(pid,channel,pid,pid,units,sampling))
    rows={c["key"]:c for c in workspace.channels(conn,1)}
    assert rows["tokopedia"]["units_sold"] == 150 and rows["tokopedia"]["samplings"] == ["skewed","unknown"]
    assert rows["lazada"]["units_sold"] is None and rows["lazada"]["samplings"] == ["skewed"]
    conn.close()


def test_resolve_range_parses_validates_and_clamps():
    import pytest
    from datetime import date
    from app.deciqo.errors import DeciqoError
    today = date(2026, 9, 26)
    assert insights.resolve_range(None, 1, start="2026-08-28", end="2026-09-26", today=today) == (date(2026, 8, 28), today, False)
    # Akhir di masa depan dipotong ke hari ini; start kosong memakai `days`.
    assert insights.resolve_range(None, 1, days="7", end="2026-12-01", today=today) == (date(2026, 9, 20), today, False)
    assert insights.resolve_range(None, 1, start="2026-09-26", end="2026-09-26", today=today)[:2] == (today, today)
    for bad in [dict(start="2026-09-10", end="2026-09-01"), dict(start="26/09/2026"), dict(start="2020-01-01", end="2026-09-26")]:
        with pytest.raises(DeciqoError) as error:
            insights.resolve_range(None, 1, today=today, **bad)
        assert error.value.code == "invalid_range"


def _seed_patterns(conn):
    conn.execute("INSERT INTO users(id,email,password_hash,created_at) VALUES (1,'a@x.test','hash','')")
    for pid, time in [("p1", "2026-09-20T01:00:00Z"), ("p2", "2026-06-01T01:00:00Z")]:
        conn.execute("INSERT INTO products(id,user_id,channel,source_item_id,title) VALUES (?,1,'manual',?,?)", (pid, pid, pid))
        for rid in ("r1", "r2"):
            conn.execute("INSERT INTO reviews(product_id,id,rating,text,version_hash,review_time) VALUES (?,?,2,'bukti','h',?)", (pid, rid, time))
        blob = pipeline.write_evidence([{"review_id": "r1", "quote": "bukti"}, {"review_id": "r2", "quote": "bukti"}], [], 0,
                                       {"support": 2, "denominator": 2, "candidates_read": 2, "share": 1})
        conn.execute("INSERT INTO findings(id,product_id,attribute,attribute_local,attribute_key,finding_type,evidence_json,support,denominator,candidates_read) "
                     "VALUES (?,?,'packaging','kemasan','packaging','operational',?,2,2,2)", (pid + "f", pid, blob))


def test_overview_range_payload_previous_period_and_pattern_counts(tmp_path):
    from datetime import date
    path = tmp_path / "range.sqlite3"
    store.migrate(path)
    conn = store.connect(path)
    _seed_patterns(conn)
    data = insights.overview_data(conn, 1, start=date(2026, 9, 1), end=date(2026, 9, 26))
    assert data["range"] == {"start": "2026-09-01", "end": "2026-09-26", "days": 26, "all": False}
    assert len(data["series"]) == 26 and data["total"] == 2
    # Hanya p1 punya bukti di rentang ini: pola lintas produk kosong di rentang, jadi kartu jatuh ke
    # semua ulasan tersimpan dan menyebutnya lewat patterns_scope.
    assert data["patterns_scope"] == "all" and len(data["one_fix_candidates"]) == 1
    wide = insights.overview_data(conn, 1, start=date(2026, 5, 1), end=date(2026, 9, 26))
    assert wide["previous"] == 0 and wide["total"] == 4
    [group] = wide["one_fix_candidates"]
    assert (group["label"], group["attribute"], group["products"], group["reviews"]) == ("kemasan", "packaging", 2, 4)
    # Periode pembanding = panjang sama tepat sebelum start.
    later = insights.overview_data(conn, 1, start=date(2026, 7, 28), end=date(2026, 9, 26))
    assert later["total"] == 2 and later["previous"] == 2
    first, last, everything = insights.resolve_range(conn, 1, all_time=True, today=date(2026, 9, 26))
    assert (first, last, everything) == (date(2026, 6, 1), date(2026, 9, 26), True)
    everything_data = insights.overview_data(conn, 1, start=first, end=last, all_time=True)
    assert everything_data["range"]["all"] is True and everything_data["patterns_scope"] == "all"
    assert len(everything_data["one_fix_candidates"]) == 1
    conn.close()


def test_overview_route_accepts_start_end_and_all(monkeypatch):
    app = FastAPI()
    app.include_router(insights.router)
    app.dependency_overrides[insights.current_user] = lambda: {"id": 1}
    monkeypatch.setattr(insights.store, "database", lambda: nullcontext(None))
    seen = []
    monkeypatch.setattr(insights, "overview_data", lambda conn, uid, days=30, **kw: seen.append((days, kw)) or {"ok": True})
    with TestClient(app) as client:
        assert client.get("/api/v1/deciqo/overview?start=2026-09-01&end=2026-09-10").status_code == 200
        assert seen[-1][1]["start"].isoformat() == "2026-09-01" and seen[-1][1]["all_time"] is False
        assert client.get("/api/v1/deciqo/overview?all=true").status_code == 200
        assert seen[-1][1]["all_time"] is True
        response = client.get("/api/v1/deciqo/overview?start=2026-09-10&end=2026-09-01")
        assert response.status_code == 422 and response.json()["detail"]["code"] == "invalid_range"
        assert client.get("/api/v1/deciqo/overview").status_code == 200 and seen[-1][0] == 30
