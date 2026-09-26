"""Migrasi tabel berbasis store_id tanpa kehilangan baris atau menebak kepemilikan."""
from app.deciqo import store


def test_archive_preserves_rows_relations_and_recreates_active_indexes(tmp_path):
    path = tmp_path / "archive.sqlite3"
    conn = store.connect(path)
    conn.executescript("""
      CREATE TABLE products (store_id TEXT, id TEXT, title TEXT, PRIMARY KEY(store_id,id));
      CREATE TABLE reviews (store_id TEXT, id TEXT, product_id TEXT, text TEXT,
        PRIMARY KEY(store_id,id), FOREIGN KEY(store_id,product_id) REFERENCES products(store_id,id));
      CREATE TABLE facts (issue_id TEXT, name TEXT, value TEXT, PRIMARY KEY(issue_id,name));
      CREATE TABLE alert_events (id TEXT PRIMARY KEY, store_id TEXT, user_id INTEGER, created_at TEXT);
      CREATE INDEX ix_alerts_user ON alert_events(user_id,created_at);
      INSERT INTO products VALUES ('s1','p1','Produk tersimpan');
      INSERT INTO reviews VALUES ('s1','r1','p1','Ulasan tersimpan');
      INSERT INTO facts VALUES ('i1','ukuran','32 cm');
      INSERT INTO alert_events VALUES ('a1','s1',NULL,'');
    """)
    conn.close()
    store.migrate(path)
    store.migrate(path)
    conn = store.connect(path)
    assert conn.execute("SELECT title FROM deciqo_archive_products").fetchone()[0] == "Produk tersimpan"
    assert conn.execute("SELECT text FROM deciqo_archive_reviews").fetchone()[0] == "Ulasan tersimpan"
    assert conn.execute("SELECT value FROM deciqo_archive_facts").fetchone()[0] == "32 cm"
    assert conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    assert conn.execute("SELECT tbl_name FROM sqlite_master WHERE name='ix_alerts_user'").fetchone()[0] == "alert_events"
    conn.close()


def test_archive_keeps_accounts_and_sessions(tmp_path):
    path = tmp_path / "account.sqlite3"
    store.migrate(path)
    conn = store.connect(path)
    conn.execute("INSERT INTO users(email,password_hash,created_at) VALUES ('test@example.test','hash','')")
    conn.execute("INSERT INTO sessions VALUES ('token',1,'','expiry')")
    conn.execute("DROP TABLE facts")
    conn.execute("CREATE TABLE facts (issue_id TEXT, value TEXT)")
    conn.execute("INSERT INTO facts VALUES ('i1','32 cm')")
    conn.close()
    store.migrate(path)
    conn = store.connect(path)
    assert conn.execute("SELECT email FROM users").fetchone()[0] == "test@example.test"
    assert conn.execute("SELECT token_hash FROM sessions").fetchone()[0] == "token"
    assert conn.execute("SELECT value FROM deciqo_archive_facts").fetchone()[0] == "32 cm"
    conn.close()
