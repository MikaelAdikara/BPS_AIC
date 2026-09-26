"""Bangun paket demo per channel di data/marketplace/ (tombol "Load demo pack").

| Paket | Sumber | data_origin |
|---|---|---|
| tokopedia-2019 | Dataset publik Tokopedia Product Reviews 2019 (Apache-2.0), di data/raw | public_dataset |
| shopee-team | data/samples/demo_shopee_asli.csv (ulasan nyata dikumpulkan tim, sudah diredaksi) | team_collected |
| tiktok-sintetis, blibli-sintetis | Ditulis tim untuk menunjukkan format impor dengan listing | synthetic |

Dataset Tokopedia tidak membawa teks listing, jadi produknya tampil sebagai kebutuhan pembeli
sampai merchant menempel listing. Produk dipilih dengan aturan tetap (≥25 ulasan, porsi ulasan
bintang ≤3 tertinggi, kategori elektronik/handphone/fashion), bukan dipilih tangan satu per satu.

Jalankan:
    python scripts/download_datasets.py   # bila data/raw/tokopedia_reviews_2019 belum ada
    python scripts/build_channel_packs.py
"""

from __future__ import annotations

import csv
import html
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "apps" / "api"))

from app.deciqo.ingest import redact  # noqa: E402

OUT = REPO / "data" / "marketplace"
TOKOPEDIA_CSV = REPO / "data" / "raw" / "tokopedia_reviews_2019" / "tokopedia-product-reviews-2019.csv"
TOKOPEDIA_PRODUCTS = 6
TOKOPEDIA_MAX_REVIEWS = 60
TOKOPEDIA_CATEGORIES = {"elektronik", "handphone", "fashion"}


def write(name: str, pack: dict) -> None:
    path = OUT / f"{name}.json"
    path.write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    reviews = sum(len(p["reviews"]) for p in pack["products"])
    print(f"{path.relative_to(REPO)}: {len(pack['products'])} produk, {reviews} ulasan")


def tokopedia() -> None:
    if not TOKOPEDIA_CSV.exists():
        print(f"lewati tokopedia: {TOKOPEDIA_CSV.relative_to(REPO)} belum ada")
        return
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in csv.DictReader(TOKOPEDIA_CSV.open(encoding="utf-8")):
        if row["category"] in TOKOPEDIA_CATEGORIES:
            grouped[row["product_id"]].append(row)
    ranked = []
    for pid, rows in grouped.items():
        if len(rows) < 25:
            continue
        low = sum(1 for r in rows if int(float(r["rating"])) <= 3)
        ranked.append((low / len(rows), len(rows), pid))
    ranked.sort(reverse=True)
    products = []
    for _share, _n, pid in ranked[:TOKOPEDIA_PRODUCTS]:
        rows = grouped[pid]
        # Urutan asli dataset dipertahankan; dipotong di 60 ulasan pertama tanpa menyaring bintang.
        reviews = []
        for i, row in enumerate(rows[:TOKOPEDIA_MAX_REVIEWS]):
            text, _ = redact(html.unescape(row["text"]).strip())
            reviews.append({"id": f"tp{pid}-{i}", "rating": int(float(row["rating"])), "text": text})
        products.append({
            "source_item_id": pid,
            "title": html.unescape(rows[0]["product_name"]).strip(),
            "url": rows[0].get("product_url") or "",
            "description": "",
            "reviews": reviews,
        })
    write("tokopedia-2019", {
        "channel": "tokopedia", "data_origin": "public_dataset", "captured_at": "2019-12-31T00:00:00+00:00",
        "label": "Tokopedia Product Reviews 2019 (public dataset)",
        "source": "HuggingFace farhamu/tokopedia-product-reviews-2019, Apache-2.0",
        "sampling": "6 products with at least 25 reviews and the highest share of 1-3 star reviews "
                    "(electronics, phones, fashion); first 60 reviews per product in dataset order. "
                    "The dataset has no review dates and no listing text.",
        "products": products,
    })


def shopee() -> None:
    rows = list(csv.DictReader((REPO / "data" / "samples" / "demo_shopee_asli.csv").open(encoding="utf-8-sig")))
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["produk"]].append(row)
    products = []
    for name, items in grouped.items():
        products.append({
            "source_item_id": name,
            "title": f"Shopee listing {name.split('-')[-1]}",
            "description": "",
            "reviews": [{"id": r["review_id"], "rating": int(r["rating"]), "text": redact(r["ulasan"].strip())[0],
                         "variant": r.get("varian") or "",
                         "review_time": f"{r['tanggal']}T00:00:00+00:00" if r.get("tanggal") else None}
                        for r in items],
        })
    write("shopee-team", {
        "channel": "shopee", "data_origin": "team_collected", "captured_at": "2026-08-31T00:00:00+00:00",
        "label": "Shopee reviews collected by the team",
        "source": "Two public Shopee listings, reviews Oct 2025 - Aug 2026, collected by the team",
        "sampling": "All collected reviews, not filtered. Product names were anonymised; account names "
                    "and body measurements were not kept.",
        "products": products,
    })


# (rating, hari lalu, varian, teks)
TIKTOK = [{
    "source_item_id": "tt-pb-mag-10k",
    "title": "Powerbank magnetik 10000 mAh",
    "description": "Powerbank magnetik 10000 mAh, pengisian nirkabel 15W. Kompatibel iPhone 12, 13, 14. "
                   "Tebal 1,6 cm, berat 190 gram. Garansi toko 7 hari.",
    "reviews": [
        (2, 12, "Hitam", "Di iPhone 15 Pro saya magnetnya lemah, sering lepas kalau di saku."),
        (3, 10, "Putih", "Magnetnya kurang kuat buat iPhone 15, harus dipegangin."),
        (2, 8, "Hitam", "Pakai case tebal jadi tidak nempel sama sekali, harusnya ditulis butuh case magsafe."),
        (5, 6, "Hitam", "Ngecas iPhone 13 lancar, tipis enak dibawa."),
        (4, 4, "Putih", "Bagus, cuma agak panas waktu ngecas sambil main game."),
        (5, 2, "Hitam", "Pengiriman cepat, barang sesuai deskripsi."),
    ],
}]
BLIBLI = [{
    "source_item_id": "bb-rc-18",
    "title": "Rice cooker digital 1,8 liter",
    "description": "Rice cooker digital kapasitas 1,8 liter, panci anti lengket, 8 menu masak, "
                   "timer 24 jam. Daya 400 watt.",
    "reviews": [
        (2, 20, "", "Lapisan anti lengketnya mulai mengelupas setelah sebulan pemakaian."),
        (3, 16, "", "Anti lengketnya sudah baret padahal pakai centong bawaan."),
        (3, 12, "", "Kapasitas 1,8 liter itu air atau beras? Masak beras 1,5 liter jadi luber."),
        (5, 9, "", "Nasinya pulen, menu bubur juga enak."),
        (4, 5, "", "Timernya berguna, tapi bunyi bip-nya keras sekali."),
        (5, 3, "", "Sesuai deskripsi, pengemasan rapi."),
    ],
}]


def synthetic(name: str, channel: str, label: str, products: list[dict]) -> None:
    from datetime import datetime, timedelta, timezone  # noqa: PLC0415

    now = datetime.now(timezone.utc).replace(hour=3, minute=0, second=0, microsecond=0)
    out = []
    for product in products:
        out.append({**product, "reviews": [
            {"id": f"{product['source_item_id']}-{i}", "rating": rating, "variant": variant, "text": text,
             "review_time": (now - timedelta(days=days)).isoformat()}
            for i, (rating, days, variant, text) in enumerate(product["reviews"], start=1)]})
    write(name, {"channel": channel, "data_origin": "synthetic", "captured_at": now.isoformat(),
                 "label": label, "source": "Written by the team to show the import format with a listing",
                 "sampling": "Synthetic example, not customer data.", "products": out})


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tokopedia()
    shopee()
    synthetic("tiktok-sintetis", "tiktok", "TikTok Shop synthetic example", TIKTOK)
    synthetic("blibli-sintetis", "blibli", "Blibli synthetic example", BLIBLI)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
