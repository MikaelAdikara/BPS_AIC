"""Penyimpanan Deciqo: satu berkas SQLite, migrasi idempoten saat startup.

Satu proses API cukup untuk beban ini, jadi SQLite dengan WAL dipilih daripada server basis data
terpisah: tidak ada service tambahan di Compose, dan volume `deciqo-data` membuat data bertahan
melewati restart container.

Migrasi sengaja sederhana: `CREATE TABLE IF NOT EXISTS` lalu `ALTER TABLE ADD COLUMN` untuk kolom
yang belum ada. Menambah kolom baru cukup dengan menambah satu baris di `SCHEMA`; basis data lama
ikut diperbarui saat startup berikutnya tanpa tool migrasi.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "tmp" / "deciqo.sqlite3"

# (nama kolom, definisi SQL). Kolom pertama yang bertanda PRIMARY KEY menjadi kunci tabel;
# kunci gabungan ditulis di TABLE_CONSTRAINTS. Urutan kolom hanya berpengaruh saat tabel dibuat.
SCHEMA: dict[str, list[tuple[str, str]]] = {
    "users": [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("email", "TEXT NOT NULL UNIQUE"),
        ("name", "TEXT NOT NULL DEFAULT ''"),
        ("password_hash", "TEXT NOT NULL"),
        ("is_demo", "INTEGER NOT NULL DEFAULT 0"),
        ("phone", "TEXT NOT NULL DEFAULT ''"),
        ("channels_json", "TEXT NOT NULL DEFAULT '[]'"),
        ("lang", "TEXT NOT NULL DEFAULT 'en'"),
        ("telegram_chat_id", "TEXT"),
        ("created_at", "TEXT NOT NULL"),
    ],
    "sessions": [
        ("token_hash", "TEXT PRIMARY KEY"),
        ("user_id", "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE"),
        ("created_at", "TEXT NOT NULL"),
        ("expires_at", "TEXT NOT NULL"),
    ],
    "sources": [
        ("id", "TEXT PRIMARY KEY"),
        ("user_id", "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE"),
        ("channel", "TEXT NOT NULL"),
        ("kind", "TEXT NOT NULL DEFAULT 'import'"),
        ("label", "TEXT NOT NULL DEFAULT ''"),
        ("status", "TEXT NOT NULL DEFAULT 'not_checked'"),
        ("last_success_at", "TEXT"),
        ("last_attempt_at", "TEXT"),
        ("last_error", "TEXT"),
        ("consecutive_failures", "INTEGER NOT NULL DEFAULT 0"),
    ],
    "woo_connections": [
        ("user_id", "INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE"),
        ("base_url", "TEXT NOT NULL"),
        ("consumer_key", "TEXT NOT NULL"),
        ("consumer_secret", "TEXT NOT NULL"),
        ("is_demo", "INTEGER NOT NULL DEFAULT 0"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    "products": [
        ("id", "TEXT PRIMARY KEY"),
        ("user_id", "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE"),
        ("channel", "TEXT NOT NULL"),
        ("source_item_id", "TEXT NOT NULL"),
        ("url", "TEXT NOT NULL DEFAULT ''"),
        ("title", "TEXT NOT NULL DEFAULT ''"),
        ("description", "TEXT NOT NULL DEFAULT ''"),
        ("specs_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("variants_json", "TEXT NOT NULL DEFAULT '[]'"),
        ("image_url", "TEXT"),
        # Galeri gambar produk selain `image_url` (URL, sudah dibatasi jumlahnya saat ingest).
        ("images_json", "TEXT NOT NULL DEFAULT '[]'"),
        # Hasil OCR gambar produk terakhir: {status, reason?, items: [{url, text}], model, checked_at}.
        # Disalin dari cache `image_ocr` agar `listing_parts(product)` tidak butuh koneksi.
        ("image_ocr_json", "TEXT NOT NULL DEFAULT '{}'"),
        # Run cek foto pembeli terakhir: {status, reason?, checked, calls, checked_at}.
        ("vision_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("price", "REAL"),
        ("units_sold", "INTEGER"),
        # Cara ulasan tersimpan diambil: complete (semua ulasan sumber), random, skewed (sengaja
        # memperbanyak bintang rendah), unknown. Proyeksi ke unit terjual hanya untuk complete/random.
        ("sampling", "TEXT NOT NULL DEFAULT 'unknown'"),
        ("snapshot_hash", "TEXT NOT NULL DEFAULT ''"),
        ("data_origin", "TEXT NOT NULL DEFAULT 'channel'"),
        ("captured_at", "TEXT"),
        ("fetched_at", "TEXT"),
        ("role", "TEXT NOT NULL DEFAULT 'own'"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
        ("updated_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    "reviews": [
        ("product_id", "TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE"),
        ("id", "TEXT NOT NULL"),
        ("rating", "INTEGER"),
        ("text", "TEXT NOT NULL DEFAULT ''"),
        ("variant", "TEXT NOT NULL DEFAULT ''"),
        ("images_json", "TEXT NOT NULL DEFAULT '[]'"),
        ("review_time", "TEXT"),
        ("version_hash", "TEXT NOT NULL"),
        ("triage_json", "TEXT"),
        ("fetched_at", "TEXT"),
        # Terisi saat sinkron penuh yang sukses tidak lagi menemukan ulasan ini di sumber.
        # Barisnya tetap ada (riwayat), tetapi keluar dari bukti aktif.
        ("deleted_at", "TEXT"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    "analyses": [
        ("product_id", "TEXT PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE"),
        ("input_hash", "TEXT NOT NULL DEFAULT ''"),
        ("ai_hash", "TEXT NOT NULL DEFAULT ''"),
        ("engine", "TEXT NOT NULL DEFAULT 'rules'"),
        ("pipeline_version", "TEXT NOT NULL DEFAULT ''"),
        ("verifier_version", "TEXT NOT NULL DEFAULT ''"),
        ("status", "TEXT NOT NULL DEFAULT 'pending'"),
        ("summary_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("trace_json", "TEXT NOT NULL DEFAULT '[]'"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    "findings": [
        ("id", "TEXT PRIMARY KEY"),
        ("product_id", "TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE"),
        ("attribute", "TEXT NOT NULL DEFAULT ''"),
        ("attribute_key", "TEXT NOT NULL DEFAULT ''"),
        ("attribute_local", "TEXT NOT NULL DEFAULT ''"),
        ("finding_type", "TEXT NOT NULL DEFAULT ''"),
        ("fix_type", "TEXT NOT NULL DEFAULT ''"),
        ("severity", "TEXT NOT NULL DEFAULT 'low'"),
        ("buyer_expectation", "TEXT NOT NULL DEFAULT ''"),
        ("merchant_question", "TEXT NOT NULL DEFAULT ''"),
        ("listing_check_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("evidence_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("rejected_json", "TEXT NOT NULL DEFAULT '[]'"),
        ("support", "INTEGER NOT NULL DEFAULT 0"),
        ("denominator", "INTEGER NOT NULL DEFAULT 0"),
        ("candidates_read", "INTEGER NOT NULL DEFAULT 0"),
        ("contradicting", "INTEGER NOT NULL DEFAULT 0"),
        ("state", "TEXT NOT NULL DEFAULT 'open'"),
        ("engine", "TEXT NOT NULL DEFAULT 'rules'"),
        ("not_detected_at", "TEXT"),
        ("analysis_hash", "TEXT NOT NULL DEFAULT ''"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
        ("updated_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    "facts": [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("finding_id", "TEXT NOT NULL REFERENCES findings(id) ON DELETE CASCADE"),
        ("attribute", "TEXT NOT NULL DEFAULT ''"),
        ("raw_value", "TEXT NOT NULL DEFAULT ''"),
        ("value", "TEXT NOT NULL DEFAULT ''"),
        ("unit", "TEXT NOT NULL DEFAULT ''"),
        ("location", "TEXT NOT NULL DEFAULT ''"),
        ("variant", "TEXT NOT NULL DEFAULT ''"),
        ("source_kind", "TEXT NOT NULL DEFAULT 'merchant_fact'"),
        ("listing_snapshot_hash", "TEXT NOT NULL DEFAULT ''"),
        ("confirmed_by", "INTEGER"),
        ("confirmed_at", "TEXT NOT NULL DEFAULT ''"),
        # Satu fakta aktif per temuan; versi lama disimpan dengan active = 0.
        ("active", "INTEGER NOT NULL DEFAULT 1"),
    ],
    "drafts": [
        ("product_id", "TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE"),
        ("input_hash", "TEXT NOT NULL"),
        ("result_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    "generic_drafts": [
        ("product_id", "TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE"),
        ("input_hash", "TEXT NOT NULL"),
        ("result_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    "decisions": [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("finding_id", "TEXT NOT NULL REFERENCES findings(id) ON DELETE CASCADE"),
        ("decision", "TEXT NOT NULL"),
        ("reason", "TEXT NOT NULL DEFAULT ''"),
        ("note", "TEXT NOT NULL DEFAULT ''"),
        ("acted_at", "TEXT"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    "alert_events": [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("user_id", "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE"),
        ("finding_id", "TEXT"),
        ("kind", "TEXT NOT NULL"),
        ("fingerprint", "TEXT NOT NULL UNIQUE"),
        ("payload_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("synthetic", "INTEGER NOT NULL DEFAULT 0"),
        ("status", "TEXT NOT NULL DEFAULT 'pending'"),
        ("attempts", "INTEGER NOT NULL DEFAULT 0"),
        ("next_attempt_at", "TEXT"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
        ("sent_at", "TEXT"),
        ("delivery_json", "TEXT NOT NULL DEFAULT '{}'"),
    ],
    "jobs": [
        ("id", "TEXT PRIMARY KEY"),
        ("user_id", "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE"),
        ("kind", "TEXT NOT NULL"),
        ("status", "TEXT NOT NULL DEFAULT 'queued'"),
        ("dedupe_key", "TEXT NOT NULL DEFAULT ''"),
        ("detail_json", "TEXT NOT NULL DEFAULT '{}'"),
        ("result_json", "TEXT"),
        ("error", "TEXT"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
        ("updated_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    "ledger": [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("user_id", "INTEGER"),
        ("provider", "TEXT NOT NULL DEFAULT 'openai'"),
        ("purpose", "TEXT NOT NULL DEFAULT ''"),
        ("model", "TEXT NOT NULL DEFAULT ''"),
        ("status", "TEXT NOT NULL DEFAULT ''"),
        ("input_tokens", "INTEGER NOT NULL DEFAULT 0"),
        ("cached_tokens", "INTEGER NOT NULL DEFAULT 0"),
        ("output_tokens", "INTEGER NOT NULL DEFAULT 0"),
        ("price_in", "REAL NOT NULL DEFAULT 0"),
        ("price_cached", "REAL NOT NULL DEFAULT 0"),
        ("price_out", "REAL NOT NULL DEFAULT 0"),
        ("cost_usd", "REAL NOT NULL DEFAULT 0"),
        ("reserved_usd", "REAL NOT NULL DEFAULT 0"),
        ("ref", "TEXT NOT NULL DEFAULT ''"),
        ("latency_ms", "INTEGER NOT NULL DEFAULT 0"),
        ("created_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    # Cek foto pembeli per (foto, atribut temuan, versi prompt). Hanya bukti tambahan: tidak
    # pernah membuat, menghapus, atau mengubah bucket/state/severity temuan.
    "vision_checks": [
        ("user_id", "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE"),
        ("product_id", "TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE"),
        ("image_url", "TEXT NOT NULL"),
        ("attribute_key", "TEXT NOT NULL"),
        ("prompt_version", "TEXT NOT NULL"),
        ("finding_id", "TEXT NOT NULL DEFAULT ''"),
        ("review_id", "TEXT NOT NULL DEFAULT ''"),
        ("verdict", "TEXT NOT NULL DEFAULT 'inconclusive'"),
        ("reason", "TEXT NOT NULL DEFAULT ''"),
        ("model", "TEXT NOT NULL DEFAULT ''"),
        ("checked_at", "TEXT NOT NULL DEFAULT ''"),
    ],
    # Cache OCR per gambar produk. Isinya teks yang tercetak di gambar publik, bukan data akun,
    # jadi dipakai bersama; `user_id` hanya mencatat siapa yang membayar panggilannya.
    "image_ocr": [
        ("image_url", "TEXT NOT NULL"),
        ("prompt_version", "TEXT NOT NULL"),
        ("text", "TEXT NOT NULL DEFAULT ''"),
        ("model", "TEXT NOT NULL DEFAULT ''"),
        ("checked_at", "TEXT NOT NULL DEFAULT ''"),
        ("user_id", "INTEGER REFERENCES users(id) ON DELETE SET NULL"),
    ],
    "telegram_links": [
        ("code", "TEXT PRIMARY KEY"),
        ("user_id", "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE"),
        ("expires_at", "TEXT NOT NULL"),
    ],
    "kv_state": [
        ("key", "TEXT PRIMARY KEY"),
        ("value", "TEXT NOT NULL DEFAULT ''"),
    ],
}

TABLE_CONSTRAINTS: dict[str, str] = {
    "reviews": "PRIMARY KEY (product_id, id)",
    "drafts": "PRIMARY KEY (product_id, input_hash)",
    "generic_drafts": "PRIMARY KEY (product_id, input_hash)",
    "vision_checks": "PRIMARY KEY (user_id, image_url, attribute_key, prompt_version)",
    "image_ocr": "PRIMARY KEY (image_url, prompt_version)",
}

INDEXES: list[str] = [
    "CREATE INDEX IF NOT EXISTS ix_sessions_user ON sessions(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_sources_user ON sources(user_id)",
    "CREATE UNIQUE INDEX IF NOT EXISTS ux_products_source ON products(user_id, channel, source_item_id)",
    "CREATE INDEX IF NOT EXISTS ix_findings_product ON findings(product_id)",
    "CREATE INDEX IF NOT EXISTS ix_facts_finding ON facts(finding_id, active)",
    "CREATE INDEX IF NOT EXISTS ix_decisions_finding ON decisions(finding_id)",
    "CREATE INDEX IF NOT EXISTS ix_alerts_user ON alert_events(user_id, created_at)",
    "CREATE INDEX IF NOT EXISTS ix_jobs_user ON jobs(user_id, status)",
    "CREATE INDEX IF NOT EXISTS ix_ledger_user ON ledger(user_id, created_at)",
    "CREATE INDEX IF NOT EXISTS ix_vision_product ON vision_checks(product_id, prompt_version)",
]

_migrated_paths: set[str] = set()
_migrate_lock = threading.Lock()


def db_path() -> Path:
    return Path(os.getenv("DECIQO_DB_PATH") or DEFAULT_DB_PATH)


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    """Koneksi mentah. Pakai `database()` kecuali benar-benar butuh mengatur transaksi sendiri."""
    target = Path(path) if path else db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target, timeout=30, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


@contextmanager
def database(path: Path | str | None = None) -> Iterator[sqlite3.Connection]:
    """Satu transaksi: commit bila blok selesai normal, rollback bila melempar.

    `BEGIN IMMEDIATE` mengambil kunci tulis di awal sehingga dua job yang bersamaan tidak saling
    membatalkan di tengah jalan (`database is locked` saat upgrade kunci baca ke tulis)."""
    target = Path(path) if path else db_path()
    key = str(target)
    if key not in _migrated_paths:
        migrate(target)
    conn = connect(target)
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def migrate(path: Path | str | None = None) -> None:
    """Buat tabel yang belum ada dan tambahkan kolom yang belum ada. Aman dipanggil berulang."""
    target = Path(path) if path else db_path()
    with _migrate_lock:
        conn = connect(target)
        try:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("BEGIN IMMEDIATE")
            # Tabel berbasis store_id/issue_id memakai identitas yang berbeda. Simpan utuh
            # sebagai arsip agar tidak memberi baris tersebut kepemilikan akun secara tebakan.
            archive_markers = {
                "products": "store_id", "reviews": "store_id",
                "facts": "issue_id", "alert_events": "store_id",
            }
            for table, marker in archive_markers.items():
                column_names = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
                if marker not in column_names:
                    continue
                archive = f"deciqo_archive_{table}"
                conn.execute(f"ALTER TABLE {table} RENAME TO {archive}")
                for index in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = ? AND sql IS NOT NULL",
                    (archive,),
                ).fetchall():
                    quoted = index["name"].replace('"', '""')
                    conn.execute(f'DROP INDEX "{quoted}"')
            for table, columns in SCHEMA.items():
                parts = [f"{name} {ddl}" for name, ddl in columns]
                if table in TABLE_CONSTRAINTS:
                    parts.append(TABLE_CONSTRAINTS[table])
                conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(parts)})")
                existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
                for name, ddl in columns:
                    if name in existing:
                        continue
                    # SQLite menolak ADD COLUMN dengan PRIMARY KEY/UNIQUE; kolom seperti itu hanya
                    # ada sejak tabel dibuat, jadi cukup buang batasannya untuk kolom susulan.
                    safe = ddl.replace("PRIMARY KEY AUTOINCREMENT", "").replace("PRIMARY KEY", "")
                    safe = safe.replace("UNIQUE", "")
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {safe}")
            for statement in INDEXES:
                conn.execute(statement)
            conn.execute("COMMIT")
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
        _migrated_paths.add(str(target))


# --- helper kecil yang dipakai semua modul -------------------------------------------------


def now() -> str:
    """Waktu sekarang, ISO 8601 UTC dengan zona, presisi detik."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def digest(*parts: Any) -> str:
    """SHA-256 heksadesimal atas bagian-bagian yang diserialkan stabil (dict diurutkan)."""
    h = hashlib.sha256()
    for part in parts:
        if not isinstance(part, str):
            part = json.dumps(part, sort_keys=True, ensure_ascii=False, default=str)
        h.update(part.encode("utf-8"))
        h.update(b"\x1f")
    return h.hexdigest()


def short_id(prefix: str, *parts: Any, length: int = 12) -> str:
    """Id stabil yang terbaca, mis. `p_3f9a1c0b2d4e` untuk produk."""
    return f"{prefix}_{digest(*parts)[:length]}"


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def loads(value: str | None, default: Any = None) -> Any:
    if value in (None, ""):
        return default
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def rows(cursor: sqlite3.Cursor) -> list[dict]:
    return [dict(row) for row in cursor.fetchall()]


def row(cursor: sqlite3.Cursor) -> dict | None:
    found = cursor.fetchone()
    return dict(found) if found else None


def get_kv(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    found = conn.execute("SELECT value FROM kv_state WHERE key = ?", (key,)).fetchone()
    return found["value"] if found else default


def set_kv(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO kv_state(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
