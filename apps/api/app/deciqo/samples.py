"""Akun demo, isi workspace demo, dan penghapusan workspace.

Akun demo dibuat otomatis saat API pertama menyala dan diisi katalog toko Woo SINTETIS. Idempoten:
restart tidak menggandakan apa pun, dan akun yang sudah punya data tidak ditimpa. "Reset to demo
data" menghapus isi workspace akun (akun tetap) lalu mengisinya ulang.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timedelta, timezone

from . import analysis, auth, demo_catalog, ingest, settings, store
from .jobs import JobContext

log = logging.getLogger("deciqo.samples")

DEMO_NAME = "Demo Merchant"
DEMO_CHANNELS = ["woocommerce", "lazada", "tokopedia"]

# Urutan penghapusan: anak dulu, induk belakangan. Tabel dengan FK CASCADE ikut terhapus
# lewat produk, tetapi dihapus eksplisit juga supaya tidak bergantung pada PRAGMA foreign_keys.
_PRODUCT_CHILDREN = ("facts", "decisions")
_PRODUCT_TABLES = ("drafts", "generic_drafts", "analyses", "reviews")
_USER_TABLES = ("alert_events", "jobs", "telegram_links", "woo_connections", "sources", "ledger")


def delete_workspace(conn: sqlite3.Connection, user_id: int, *, keep_job: str | None = None) -> dict:
    """Hapus semua data milik akun di semua tabel. Akun dan sesinya tetap ada."""
    counts: dict[str, int] = {}
    product_ids = [r["id"] for r in conn.execute("SELECT id FROM products WHERE user_id = ?", (user_id,))]
    finding_ids = []
    for pid in product_ids:
        finding_ids += [r["id"] for r in conn.execute("SELECT id FROM findings WHERE product_id = ?", (pid,))]
    for table in _PRODUCT_CHILDREN:
        n = 0
        for fid in finding_ids:
            n += conn.execute(f"DELETE FROM {table} WHERE finding_id = ?", (fid,)).rowcount
        counts[table] = n
    counts["findings"] = sum(
        conn.execute("DELETE FROM findings WHERE product_id = ?", (pid,)).rowcount for pid in product_ids)
    for table in _PRODUCT_TABLES:
        counts[table] = sum(
            conn.execute(f"DELETE FROM {table} WHERE product_id = ?", (pid,)).rowcount for pid in product_ids)
    counts["products"] = conn.execute("DELETE FROM products WHERE user_id = ?", (user_id,)).rowcount
    for table in _USER_TABLES:
        if table == "jobs" and keep_job:
            counts[table] = conn.execute(
                "DELETE FROM jobs WHERE user_id = ? AND id != ?", (user_id, keep_job)).rowcount
        else:
            counts[table] = conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,)).rowcount
    # '' bukan NULL: database lama membuat kolom ini `NOT NULL DEFAULT ''`, dan semua pembaca hanya
    # memeriksa truthy, jadi keduanya berarti "belum terhubung".
    conn.execute("UPDATE users SET telegram_chat_id = '' WHERE id = ?", (user_id,))
    return counts


def ensure_demo_user(conn: sqlite3.Connection) -> dict:
    email = settings.demo_email()
    user = store.row(conn.execute("SELECT * FROM users WHERE email = ?", (email,)))
    if user is None:
        user = auth.create_user(conn, email, settings.demo_password(), DEMO_NAME,
                                is_demo=True, channels=DEMO_CHANNELS)
    elif not auth.verify_password(settings.demo_password(), user["password_hash"]):
        # Password demo diganti lewat env: ikuti env supaya kredensial di README tetap benar.
        conn.execute("UPDATE users SET password_hash = ?, is_demo = 1 WHERE id = ?",
                     (auth.hash_password(settings.demo_password()), user["id"]))
    return user


def load_demo_catalog(conn: sqlite3.Connection, user_id: int, *, catalog: list[dict] | None = None,
                      connection: tuple[str, str, str] | None = None) -> ingest.ImportStats:
    """Isi katalog demo dan hubungkan akun ke tokonya.

    Default: toko Woo sintetis. Dengan `catalog` + `connection` (url, user, password), katalog yang
    sudah dibaca dari toko WordPress demo lokal dipakai dan akun tetap tersambung ke toko itu."""
    stats = ingest.upsert_catalog(user_id, "woocommerce", catalog or demo_catalog.as_catalog(),
                                  data_origin="synthetic", sampling="complete", conn=conn)
    base_url, key, secret = connection or (settings.woo_base_url(), settings.DEMO_WOO_KEY, settings.DEMO_WOO_SECRET)
    conn.execute(
        "INSERT INTO woo_connections(user_id, base_url, consumer_key, consumer_secret, is_demo, created_at) "
        "VALUES(?, ?, ?, ?, 1, ?) ON CONFLICT(user_id) DO UPDATE SET base_url = excluded.base_url, "
        "consumer_key = excluded.consumer_key, consumer_secret = excluded.consumer_secret, is_demo = 1",
        (user_id, base_url, key, secret, store.now()),
    )
    conn.execute("UPDATE sources SET label = ? WHERE id = ?",
                 ("WooCommerce (local demo store)" if connection else "WooCommerce (synthetic demo store)",
                  f"{user_id}:woocommerce"))
    return stats


def _find_finding(conn: sqlite3.Connection, user_id: int, sku: str, hints: tuple[str, ...]) -> dict | None:
    pid = ingest.product_id(user_id, "woocommerce", str(
        next(p["id"] for p in demo_catalog.PRODUCTS if p["sku"] == sku)))
    for finding in store.rows(conn.execute("SELECT * FROM findings WHERE product_id = ?", (pid,))):
        haystack = " ".join([finding["attribute_key"], finding["attribute"], finding["attribute_local"]]).lower()
        if any(h in haystack for h in hints):
            return finding
    return None


def apply_demo_state(conn: sqlite3.Connection, user_id: int) -> dict:
    """Setelah analisis: simpan fakta dan keputusan contoh pada kursi lipat.

    Bergantung pada temuan yang dihasilkan engine; bila temuan yang dicari belum ada (mis. engine
    belum menghasilkan atribut itu), langkah ini dilewati dan dicatat, bukan dipaksakan."""
    applied = {"facts": 0, "decisions": 0, "missing": []}
    now = datetime.now(timezone.utc).replace(microsecond=0)
    for fact in demo_catalog.CONFIRMED_FACTS:
        finding = _find_finding(conn, user_id, fact["product_sku"], fact["attribute_hint"])
        if not finding:
            applied["missing"].append(f"fact:{fact['product_sku']}")
            continue
        if conn.execute("SELECT 1 FROM facts WHERE finding_id = ? AND active = 1", (finding["id"],)).fetchone():
            continue
        conn.execute(
            "INSERT INTO facts(finding_id, attribute, raw_value, value, unit, location, source_kind, "
            "confirmed_by, confirmed_at, active) VALUES(?, ?, ?, ?, ?, ?, 'merchant_fact', ?, ?, 1)",
            (finding["id"], finding["attribute"], f"{fact['value']} {fact['unit']}", fact["value"],
             fact["unit"], fact["location"], user_id, (now - timedelta(days=2)).isoformat()),
        )
        if finding["state"] == "open":
            conn.execute("UPDATE findings SET state = 'investigating', updated_at = ? WHERE id = ?",
                         (store.now(), finding["id"]))
        applied["facts"] += 1
    for decision in demo_catalog.SEED_DECISIONS:
        finding = _find_finding(conn, user_id, decision["product_sku"], decision["attribute_hint"])
        if not finding:
            applied["missing"].append(f"decision:{decision['product_sku']}")
            continue
        if conn.execute("SELECT 1 FROM decisions WHERE finding_id = ?", (finding["id"],)).fetchone():
            continue
        acted_at = (now - timedelta(days=decision["days_ago"])).isoformat()
        conn.execute(
            "INSERT INTO decisions(finding_id, decision, note, acted_at, created_at) VALUES(?, ?, ?, ?, ?)",
            (finding["id"], decision["decision"], decision["note"], acted_at, acted_at),
        )
        conn.execute("UPDATE findings SET state = ?, updated_at = ? WHERE id = ?",
                     (decision["decision"], store.now(), finding["id"]))
        applied["decisions"] += 1
    if applied["missing"]:
        log.warning(f"status demo belum lengkap: {applied['missing']}")
    return applied


def populate_demo(ctx: JobContext | None, user_id: int, *, catalog: list[dict] | None = None,
                  connection: tuple[str, str, str] | None = None) -> dict:
    """Katalog → analisis → fakta/keputusan contoh. Dipakai seed startup dan reset demo."""
    with store.database() as conn:
        stats = load_demo_catalog(conn, user_id, catalog=catalog, connection=connection)
    result = {"stats": stats.public()}
    result["analysis"] = analysis.analyse_products(ctx, stats.products)
    with store.database() as conn:
        result["demo_state"] = apply_demo_state(conn, user_id)
    return result


def seed_demo() -> None:
    """Hook startup: akun demo ada dan berisi. Tidak menyentuh akun demo yang sudah punya data."""
    with store.database() as conn:
        user = ensure_demo_user(conn)
        has_data = conn.execute("SELECT 1 FROM products WHERE user_id = ? LIMIT 1", (user["id"],)).fetchone()
    from . import jobs  # noqa: PLC0415

    if has_data:
        # Katalog sudah ada tetapi belum pernah dianalisis (engine baru tersedia setelah seed
        # sebelumnya): lengkapi analisis dan status demo tanpa mengisi ulang katalog.
        with store.database() as conn:
            pending = [r["id"] for r in conn.execute(
                "SELECT p.id FROM products p LEFT JOIN analyses a ON a.product_id = p.id "
                "WHERE p.user_id = ? AND a.product_id IS NULL", (user["id"],))]
        if pending and analysis.available():
            def finish(ctx):
                result = analysis.analyse_products(ctx, pending)
                with store.database() as conn:
                    result["demo_state"] = apply_demo_state(conn, user["id"])
                return result
            jobs.start(user["id"], "seed_demo", finish, target="demo")
        return

    # Di thread terpisah: analisis AI bisa memakan puluhan detik dan startup tidak boleh menunggu.
    jobs.start(user["id"], "seed_demo", lambda ctx: populate_demo(ctx, user["id"]), target="demo")
