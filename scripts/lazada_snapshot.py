"""Ambil snapshot publik Lazada bertanggal ke data/marketplace/.

Mencari kandidat per kata kunci, memilih produk dengan ulasan terbanyak, lalu mengambil listing +
hingga 30 ulasan per produk lewat actor Apify yang sama dengan fetch live. Nama reviewer tidak
disalin, dan PII di teks ulasan diredaksi SEBELUM berkas ditulis (berkas ini masuk repo).

Jalankan (butuh APIFY_TOKEN di environment):
    python scripts/lazada_snapshot.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "apps" / "api"))

os.environ.setdefault("DECIQO_DB_PATH", str(REPO / "tmp" / "snapshot-ledger.sqlite3"))

from app.deciqo import ingest  # noqa: E402
from app.deciqo.connectors import apify  # noqa: E402

# Kategori yang listingnya membuat klaim yang bisa dibantah ulasan: ukuran, kapasitas, bahan,
# daya tahan, kompatibilitas.
QUERIES = {
    "tas laptop 14 inch": 2,
    "powerbank 20000mah": 2,
    "kemeja pria lengan panjang": 2,
    "earphone bluetooth tws": 2,
    "sepatu sneakers pria": 1,
    "casing hp iphone": 1,
}
PER_QUERY_CANDIDATES = 6


def main() -> int:
    candidates = apify.run_actor(
        {"mode": "search", "country": "ID", "searchTerms": list(QUERIES), "maxItems": PER_QUERY_CANDIDATES,
         "sortBy": "relevance"},
        max_charge=0.2, user_id=None, ref="snapshot-search")
    chosen: list[str] = []
    for query, take in QUERIES.items():
        cards = [c for c in candidates if (c.get("searchTerm") or c.get("keyword") or c.get("query")) == query] \
            or [c for c in candidates if query.split()[0] in (c.get("title") or "").lower()]
        cards.sort(key=lambda c: int(c.get("reviewCount") or c.get("reviews") or 0), reverse=True)
        for card in cards:
            url = (card.get("url") or "").split("?")[0]
            try:
                apify.product_item_id(url)
            except Exception:  # noqa: BLE001
                continue
            if url not in chosen:
                chosen.append(url)
                take -= 1
            if take == 0:
                break
    print(f"{len(chosen)} produk dipilih")
    catalog = apify.fetch_products(chosen, user_id=None)
    for product in catalog:
        product["description"], _ = ingest.redact(product["description"])
        for review in product["reviews"]:
            review["text"], _ = ingest.redact(review["text"])
    captured = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    day = captured[:10]
    pack = {
        "channel": "lazada",
        "data_origin": "public_snapshot",
        "captured_at": captured,
        "label": f"Lazada public snapshot ({day})",
        "source": "Public Lazada product pages via Apify actor " + apify.ACTOR,
        "removed": "Reviewer names and profile data are not copied; phone numbers, emails and handles in review text are redacted.",
        "sampling": "Per product: the 30 newest reviews plus up to 10 reviews each at 1, 2 and 3 stars. The star mix "
                    "is therefore NOT the product's real rating distribution.",
        # Bintang rendah sengaja diperbanyak: share keluhan tidak boleh diproyeksikan ke unit terjual.
        "sampling_kind": "skewed",
        "products": catalog,
    }
    out = REPO / "data" / "marketplace" / f"lazada-snapshot-{day}.json"
    out.write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    reviews = sum(len(p["reviews"]) for p in catalog)
    print(f"{out.relative_to(REPO)}: {len(catalog)} produk, {reviews} ulasan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
