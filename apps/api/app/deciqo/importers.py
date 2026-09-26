"""Parser impor tempel dan CSV untuk channel tanpa konektor langsung.

Tokopedia, Shopee, TikTok Shop, Blibli, dan tempel manual masuk lewat sini. Hasilnya berbentuk
katalog yang sama dengan konektor lain lalu diserahkan ke `ingest.upsert_catalog`.

- Tempel: satu ulasan per baris; `4 | teks` menambahkan rating; baris kosong diabaikan.
- CSV: header fleksibel (review/ulasan/text, rating/bintang, date/tanggal, variant/varian,
  product/produk), UTF-8, maksimal 5 MB. Kolom produk membuat satu produk per nilai.
"""

from __future__ import annotations

import csv
import io
import re

from .errors import DeciqoError

MAX_CSV_BYTES = 5 * 1024 * 1024
MAX_REVIEWS = 2000
IMPORT_CHANNELS = ("tokopedia", "shopee", "tiktok", "blibli", "manual")

HEADERS = {
    "text": ("review", "ulasan", "text", "teks", "comment", "komentar", "content", "isi"),
    "rating": ("rating", "bintang", "star", "stars", "score", "nilai"),
    "review_time": ("date", "tanggal", "time", "waktu", "created_at", "review_time", "timestamp"),
    "variant": ("variant", "varian", "variasi", "size", "ukuran"),
    "product": ("product", "produk", "product_name", "nama_produk", "item"),
    "id": ("id", "review_id", "id_ulasan"),
}

_RATED_LINE = re.compile(r"^\s*([1-5])(?:[.,]0)?\s*(?:\||★|\*|/5\s*\|?)\s*(.+)$")
_DATE_FORMATS = (
    (re.compile(r"^(\d{4})-(\d{2})-(\d{2})"), ("y", "m", "d")),
    (re.compile(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})"), ("d", "m", "y")),
)


def parse_paste(text: str) -> list[dict]:
    reviews = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        match = _RATED_LINE.match(line)
        if match:
            reviews.append({"rating": int(match.group(1)), "text": match.group(2).strip()})
        else:
            reviews.append({"rating": None, "text": line})
    return reviews


def _normalise_header(name: str) -> str:
    return re.sub(r"[^a-z_]", "", (name or "").strip().lower().replace(" ", "_"))


def _column_map(fieldnames: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    normalised = {_normalise_header(f): f for f in fieldnames if f}
    for key, aliases in HEADERS.items():
        for alias in aliases:
            if alias in normalised:
                mapping[key] = normalised[alias]
                break
    return mapping


def parse_date(value: str | None) -> str | None:
    """Tanggal ke ISO UTC. Format yang tidak dikenali menjadi None (dihitung sebagai tanpa
    tanggal), bukan ditebak: tindak lanjut bergantung pada urutan waktu yang benar."""
    value = (value or "").strip()
    if not value:
        return None
    for pattern, order in _DATE_FORMATS:
        match = pattern.match(value)
        if not match:
            continue
        parts = dict(zip(order, (int(g) for g in match.groups())))
        try:
            from datetime import datetime, timezone  # noqa: PLC0415

            return datetime(parts["y"], parts["m"], parts["d"], tzinfo=timezone.utc).isoformat()
        except ValueError:
            return None
    return None


def parse_csv(text: str) -> tuple[dict[str, list[dict]], int]:
    """Ulasan dikelompokkan per nama produk ('' bila tidak ada kolom produk), dan jumlah baris."""
    if len(text.encode("utf-8")) > MAX_CSV_BYTES:
        raise DeciqoError(413, "file_too_large", "The CSV is larger than 5 MB.")
    text = text.lstrip("﻿")
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    mapping = _column_map(reader.fieldnames or [])
    if "text" not in mapping:
        raise DeciqoError(422, "csv_missing_review_column",
                          "The CSV needs a review column (review, ulasan, or text).")
    grouped: dict[str, list[dict]] = {}
    count = 0
    for row in reader:
        count += 1
        if count > MAX_REVIEWS:
            raise DeciqoError(413, "too_many_reviews", f"Import at most {MAX_REVIEWS} reviews at a time.")
        product = (row.get(mapping.get("product", ""), "") or "").strip()
        grouped.setdefault(product, []).append({
            "id": (row.get(mapping.get("id", ""), "") or "").strip() or None,
            "text": row.get(mapping["text"], "") or "",
            "rating": row.get(mapping.get("rating", ""), None),
            "variant": row.get(mapping.get("variant", ""), "") or "",
            "review_time": parse_date(row.get(mapping.get("review_time", ""), "")),
        })
    return grouped, count


def build_catalog(*, channel: str, product_title: str, product_url: str = "", listing: str = "",
                  reviews_text: str = "", csv_text: str = "") -> list[dict]:
    """Satu permintaan impor → daftar produk untuk ingest."""
    if channel not in IMPORT_CHANNELS:
        raise DeciqoError(422, "unknown_channel", "Choose Tokopedia, Shopee, TikTok Shop, Blibli, or Manual.")
    title = (product_title or "").strip()
    reviews: list[dict] = parse_paste(reviews_text) if reviews_text.strip() else []
    per_product: dict[str, list[dict]] = {}
    if csv_text.strip():
        grouped, _ = parse_csv(csv_text)
        for name, items in grouped.items():
            if name and name != title:
                per_product[name] = items
            else:
                reviews += items
    if len(reviews) > MAX_REVIEWS:
        raise DeciqoError(413, "too_many_reviews", f"Import at most {MAX_REVIEWS} reviews at a time.")
    if not title and not per_product:
        raise DeciqoError(422, "product_title_required", "Enter the product name.")
    if not reviews and not per_product and not listing.strip():
        raise DeciqoError(422, "no_reviews", "Paste at least one review or the listing text.")
    catalog = []
    if title:
        catalog.append({"source_item_id": product_url.strip() or "", "title": title,
                        "url": product_url.strip(), "description": listing.strip() or None,
                        "reviews": reviews})
    for name, items in per_product.items():
        catalog.append({"source_item_id": "", "title": name, "reviews": items})
    return catalog
