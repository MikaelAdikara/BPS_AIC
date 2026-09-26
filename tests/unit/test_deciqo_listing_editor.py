"""Deskripsi yang diedit tidak menggandakan spesifikasi sumber."""
from app.deciqo import auth, ingest, store
from app.deciqo.engine import workspace


def test_editor_text_round_trip_and_full_text_compatibility(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "editor.sqlite3"))
    store.migrate()
    with store.database() as conn:
        user = auth.create_user(conn, "editor@x.test", "rahasia123", "M")
        stats = ingest.upsert_catalog(user["id"], "manual", [{"source_item_id":"bag", "title":"Tas", "description":"Tas kanvas.", "specs":{"Bahan":"Kanvas"}, "reviews":[]}], conn=conn)
        pid = stats.products[0]
        def view():
            product = store.row(conn.execute("SELECT * FROM products WHERE id=?", (pid,)))
            return workspace.product_view(conn, product)["product"]
        before = view()
        assert before["listing_edit_text"] == "Tas kanvas."
        assert before["listing_text"] == "Tas kanvas.\nBahan: Kanvas"
        assert not ingest.set_listing(conn, pid, before["listing_text"])
        assert not ingest.set_listing(conn, pid, before["listing_edit_text"])
        assert ingest.set_listing(conn, pid, "Tas kanvas dengan saku depan.")
        after = view()
        assert after["listing_text"] == "Tas kanvas dengan saku depan.\nBahan: Kanvas"
        assert after["listing_text"].count("Bahan: Kanvas") == 1
        assert not ingest.set_listing(conn, pid, after["listing_edit_text"])
