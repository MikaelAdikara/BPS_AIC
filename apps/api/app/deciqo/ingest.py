"""Satu pintu masuk katalog untuk semua channel.

Woo, Lazada, impor CSV/tempel, dan paket contoh semuanya lewat `upsert_catalog`, sehingga:

- id produk dan ulasan stabil (impor ulang tidak menggandakan),
- PII diredaksi di satu tempat, SEBELUM disimpan dan sebelum teks mana pun mencapai model,
- statistik impor dihitung dari apa yang benar-benar tersimpan, bukan dari jumlah baris masuk.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from typing import Any

from ..tools.privacy import PII_PATTERNS
from . import store

CHANNELS = ("woocommerce", "lazada", "tokopedia", "shopee", "tiktok", "blibli", "manual", "sample")
CHANNEL_KIND = {
    "woocommerce": "api",
    "lazada": "fetch",
    "sample": "sample",
}
CHANNEL_LABEL = {
    "woocommerce": "WooCommerce",
    "lazada": "Lazada",
    "tokopedia": "Tokopedia",
    "shopee": "Shopee",
    "tiktok": "TikTok Shop",
    "blibli": "Blibli",
    "manual": "Manual",
    "sample": "Sample",
}
DATA_ORIGINS = (
    "synthetic", "public_snapshot", "public_live", "public_dataset", "team_collected", "channel",
)

# Pola alamat bawaan redaksi lama terlalu lebar untuk teks ulasan: "dibawa jalan jalan" atau
# "blok warnanya" ikut terhapus dan kutipan bukti jadi rusak. Di sini alamat hanya dikenali
# bila diikuti nama berhuruf kapital (Jl. Merdeka, Jalan Sudirman, Gg. Mawar).
_ADDRESS = re.compile(r"\b(?:[Jj]l\.?|[Jj]ln\.?|[Jj]alan|[Gg]g\.|[Gg]ang|[Pp]erum)\s+[A-Z][\w.]*(?:\s+[A-Z0-9][\w./-]*){0,4}")
_REDACTION = [(name, pattern, repl) for name, pattern, repl in PII_PATTERNS if name != "alamat"]
_REDACTION.append(("alamat", _ADDRESS, "[alamat]"))
_REDACTION.append(("alamat", re.compile(r"\bGedung\s+[A-Z][\w.]*(?:\s+Lt\.?\s*\d+)?"), "[alamat]"))


def redact(text: str) -> tuple[str, bool]:
    """Teks dengan PII terstruktur diganti penanda jenisnya, dan apakah ada yang diganti."""
    if not text:
        return "", False
    changed = False
    for _name, pattern, replacement in _REDACTION:
        text, n = pattern.subn(replacement, text)
        changed = changed or n > 0
    return text, changed


def normalise_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


@dataclass
class ImportStats:
    received: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped_empty: int = 0
    deleted: int = 0
    redacted: int = 0
    products: list[str] = field(default_factory=list)
    changed_products: list[str] = field(default_factory=list)

    def public(self) -> dict:
        return {
            "received": self.received, "inserted": self.inserted, "updated": self.updated,
            "unchanged": self.unchanged, "skipped_empty": self.skipped_empty,
            "deleted": self.deleted, "redacted": self.redacted,
        }

    def as_dict(self) -> dict:
        return {**self.public(), "products": self.products, "changed_products": self.changed_products}


def product_id(user_id: int, channel: str, source_item_id: str) -> str:
    return store.short_id("p", user_id, channel, str(source_item_id))


def listing_hash(product: dict) -> str:
    return store.digest(
        normalise_text(product.get("title", "")),
        normalise_text(product.get("description", "")),
        product.get("specs") or {},
        product.get("variants") or [],
    )


def _rating(value: Any) -> int | None:
    try:
        rating = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    return rating if 1 <= rating <= 5 else None


def touch_source(conn: sqlite3.Connection, user_id: int, channel: str, *, ok: bool,
                 error: str | None = None, status: str | None = None, label: str = "") -> None:
    """Catat hasil kontak terakhir dengan sumber. Gagal tidak menghapus data lama; statusnya
    menjadi `stale` (pernah sukses) atau `unavailable` (belum pernah)."""
    source_id = f"{user_id}:{channel}"
    now = store.now()
    existing = store.row(conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)))
    if existing is None:
        conn.execute(
            "INSERT INTO sources(id, user_id, channel, kind, label, status) VALUES(?, ?, ?, ?, ?, ?)",
            (source_id, user_id, channel, CHANNEL_KIND.get(channel, "import"),
             label or CHANNEL_LABEL.get(channel, channel), "not_checked"),
        )
        existing = {"last_success_at": None, "consecutive_failures": 0}
    if ok:
        conn.execute(
            "UPDATE sources SET status = ?, last_success_at = ?, last_attempt_at = ?, "
            "last_error = NULL, consecutive_failures = 0 WHERE id = ?",
            (status or "connected", now, now, source_id),
        )
    else:
        fallback = "stale" if existing.get("last_success_at") else "unavailable"
        conn.execute(
            "UPDATE sources SET status = ?, last_attempt_at = ?, last_error = ?, "
            "consecutive_failures = consecutive_failures + 1 WHERE id = ?",
            (status or fallback, now, (error or "")[:300], source_id),
        )


def upsert_catalog(
    user_id: int,
    channel: str,
    products: list[dict],
    *,
    data_origin: str = "channel",
    captured_at: str | None = None,
    full_sync: bool = False,
    role: str = "own",
    conn: sqlite3.Connection | None = None,
) -> ImportStats:
    """Simpan produk beserta ulasannya.

    Setiap produk: `source_item_id`, `title`, dan opsional `url`, `description`, `specs`,
    `variants`, `image_url`, `price`, `units_sold`, `reviews`. Setiap ulasan: `text`, dan opsional
    `id` (id di sumber), `rating`, `variant`, `images`, `review_time`.

    `full_sync=True` berarti daftar ulasan ini lengkap untuk produk tersebut: ulasan tersimpan
    yang tidak lagi muncul dikeluarkan dari bukti aktif. Hanya dipanggil setelah sinkron yang
    SUKSES penuh; sinkron gagal tidak pernah menghapus apa pun.
    """
    if channel not in CHANNELS:
        raise ValueError(f"unknown channel {channel}")
    if data_origin not in DATA_ORIGINS:
        raise ValueError(f"unknown data_origin {data_origin}")
    if conn is None:
        with store.database() as own:
            return upsert_catalog(user_id, channel, products, data_origin=data_origin,
                                  captured_at=captured_at, full_sync=full_sync, role=role, conn=own)

    stats = ImportStats()
    now = store.now()
    for item in products:
        source_item_id = str(item.get("source_item_id") or "").strip()
        if not source_item_id:
            source_item_id = store.digest(normalise_text(item.get("title", "")).lower())[:16]
        pid = product_id(user_id, channel, source_item_id)
        title, _ = redact(normalise_text(item.get("title", "")))
        existing = store.row(conn.execute(
            "SELECT snapshot_hash, updated_at, description FROM products WHERE id = ?", (pid,)))
        if item.get("description") is None and existing is not None:
            # Impor ulasan saja tidak menghapus listing yang sudah ditempel sebelumnya.
            description = existing["description"]
        else:
            description, _ = redact((item.get("description") or "").strip())
        snapshot = listing_hash({**item, "title": title, "description": description})
        listing_changed = existing is None or existing["snapshot_hash"] != snapshot
        if existing is None:
            conn.execute(
                "INSERT INTO products(id, user_id, channel, source_item_id, url, title, description, "
                "specs_json, variants_json, image_url, price, units_sold, snapshot_hash, data_origin, "
                "captured_at, fetched_at, role, created_at, updated_at) "
                "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (pid, user_id, channel, source_item_id, item.get("url") or "", title, description,
                 store.dumps(item.get("specs") or {}), store.dumps(item.get("variants") or []),
                 item.get("image_url"), item.get("price"), item.get("units_sold"), snapshot,
                 data_origin, captured_at or now, now, role, now, now),
            )
        else:
            conn.execute(
                "UPDATE products SET url = ?, title = ?, description = ?, specs_json = ?, "
                "variants_json = ?, image_url = ?, price = ?, units_sold = ?, snapshot_hash = ?, "
                "data_origin = ?, captured_at = ?, fetched_at = ?, updated_at = ? WHERE id = ?",
                (item.get("url") or "", title, description, store.dumps(item.get("specs") or {}),
                 store.dumps(item.get("variants") or []), item.get("image_url"), item.get("price"),
                 item.get("units_sold"), snapshot, data_origin, captured_at or now, now,
                 now if listing_changed else existing["updated_at"], pid),
            )
        stats.products.append(pid)
        reviews_changed = _upsert_reviews(conn, pid, item.get("reviews") or [], stats, now, full_sync)
        if listing_changed or reviews_changed:
            stats.changed_products.append(pid)
    touch_source(conn, user_id, channel, ok=True)
    return stats


def _upsert_reviews(conn: sqlite3.Connection, pid: str, reviews: list[dict], stats: ImportStats,
                    now: str, full_sync: bool) -> bool:
    changed = False
    seen: set[str] = set()
    occurrences: dict[str, int] = {}
    for review in reviews:
        stats.received += 1
        raw = normalise_text(review.get("text") or "")
        if not raw:
            stats.skipped_empty += 1
            continue
        text, was_redacted = redact(raw)
        if was_redacted:
            stats.redacted += 1
        rating = _rating(review.get("rating"))
        variant = normalise_text(review.get("variant") or "")
        rid = str(review.get("id") or "").strip()
        if not rid:
            # Tanpa id dari sumber (tempel/CSV): id dari teks + urutan kemunculannya, sehingga
            # dua ulasan "Bagus" yang berbeda tetap dua baris, dan impor ulang tetap cocok.
            key = raw.lower()
            occurrences[key] = occurrences.get(key, 0) + 1
            rid = store.short_id("r", pid, key, occurrences[key])
        if rid in seen:
            stats.unchanged += 1
            continue
        seen.add(rid)
        version = store.digest(text, rating, variant)
        existing = store.row(conn.execute(
            "SELECT version_hash, deleted_at FROM reviews WHERE product_id = ? AND id = ?", (pid, rid)))
        if existing is None:
            conn.execute(
                "INSERT INTO reviews(product_id, id, rating, text, variant, images_json, review_time, "
                "version_hash, fetched_at, created_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (pid, rid, rating, text, variant, store.dumps(review.get("images") or []),
                 review.get("review_time"), version, now, now),
            )
            stats.inserted += 1
            changed = True
        elif existing["version_hash"] != version or existing["deleted_at"]:
            conn.execute(
                "UPDATE reviews SET rating = ?, text = ?, variant = ?, images_json = ?, review_time = ?, "
                "version_hash = ?, triage_json = NULL, fetched_at = ?, deleted_at = NULL "
                "WHERE product_id = ? AND id = ?",
                (rating, text, variant, store.dumps(review.get("images") or []),
                 review.get("review_time"), version, now, pid, rid),
            )
            stats.updated += 1
            changed = True
        else:
            conn.execute("UPDATE reviews SET fetched_at = ? WHERE product_id = ? AND id = ?", (now, pid, rid))
            stats.unchanged += 1
    if full_sync:
        active = [r["id"] for r in conn.execute(
            "SELECT id FROM reviews WHERE product_id = ? AND deleted_at IS NULL", (pid,))]
        gone = [rid for rid in active if rid not in seen]
        for rid in gone:
            conn.execute("UPDATE reviews SET deleted_at = ? WHERE product_id = ? AND id = ?", (now, pid, rid))
        if gone:
            stats.deleted += len(gone)
            changed = True
    return changed


def set_listing(conn: sqlite3.Connection, pid: str, listing: str) -> bool:
    """Ganti teks listing yang ditempel merchant. True bila isinya berubah."""
    product = store.row(conn.execute("SELECT * FROM products WHERE id = ?", (pid,)))
    if product is None:
        return False
    description, _ = redact(listing.strip())
    from .engine.pipeline import listing_parts

    if description == listing_parts(product)[0]:
        return False
    snapshot = listing_hash({
        "title": product["title"], "description": description,
        "specs": store.loads(product["specs_json"], {}), "variants": store.loads(product["variants_json"], []),
    })
    if snapshot == product["snapshot_hash"]:
        return False
    conn.execute(
        "UPDATE products SET description = ?, snapshot_hash = ?, updated_at = ? WHERE id = ?",
        (description, snapshot, store.now(), pid),
    )
    return True
