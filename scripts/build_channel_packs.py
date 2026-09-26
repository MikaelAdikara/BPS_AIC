"""Bangun paket demo per channel di data/marketplace/ (tombol "Load demo pack").

| Paket | Sumber | data_origin |
|---|---|---|
| tokopedia-2019 | Dataset publik Tokopedia Product Reviews 2019 (Apache-2.0), di data/raw | public_dataset |
| tokopedia-prdect | Dataset publik PRDECT-ID (Tokopedia, CC-BY-4.0), di data/raw: harga dan jumlah terjual | public_dataset |
| shopee-team | data/samples/demo_shopee_asli.csv (ulasan nyata dikumpulkan tim, sudah diredaksi) | team_collected |
| tiktok-sintetis, blibli-sintetis | Ditulis tim untuk menunjukkan format impor dengan listing | synthetic |

Kedua dataset Tokopedia tidak membawa teks listing dan tanggal ulasan, jadi produknya tampil sebagai
kebutuhan pembeli sampai merchant menempel listing. Produk dipilih dengan aturan tetap, bukan dipilih
tangan satu per satu (lihat konstanta TOKOPEDIA_* dan PRDECT_*).

`sampling_kind` tiap paket menentukan boleh tidaknya rencana keputusan memproyeksikan share keluhan
ke unit terjual: hanya `complete`/`random`. Kedua dataset Tokopedia memperbanyak ulasan negatif atau
tidak mendokumentasikan cara ambilnya, jadi hanya menampilkan batas bawah "setidaknya N pembeli".

Jalankan:
    python scripts/download_datasets.py   # bila data/raw/tokopedia_reviews_2019 atau prdect_id belum ada
    python scripts/build_channel_packs.py
"""

from __future__ import annotations

import csv
import hashlib
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
PRDECT_CSV = REPO / "data" / "raw" / "prdect_id" / "PRDECT-ID Dataset.csv"
PRDECT_PRODUCTS = 23
PRDECT_MIN_REVIEWS = 10
# Di bawah harga ini isinya item tambahan (dus, bubble wrap, hang tag), bukan produk yang diulas.
PRDECT_MIN_PRICE = 10_000
PRDECT_PER_CATEGORY = 2


def write(name: str, pack: dict) -> None:
    path = OUT / f"{name}.json"
    path.write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
    reviews = sum(len(p["reviews"]) for p in pack["products"])
    print(f"{path.relative_to(REPO)}: {len(pack['products'])} produk, {reviews} ulasan")


def sold_count(value: str) -> int | None:
    """Angka terjual gaya Tokopedia: "787", "2,9rb" (dibulatkan ke bawah oleh Tokopedia), "12rb"."""
    value = (value or "").strip().lower()
    if value.endswith("rb"):
        try:
            return int(float(value[:-2].replace(",", ".")) * 1000)
        except ValueError:
            return None
    return int(value) if value.isdigit() else None


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
            "units_sold": sold_count(rows[0].get("sold", "")),
            "reviews": reviews,
        })
    write("tokopedia-2019", {
        "channel": "tokopedia", "data_origin": "public_dataset", "captured_at": "2019-12-31T00:00:00+00:00",
        "label": "Tokopedia Product Reviews 2019 (public dataset)",
        "source": "HuggingFace farhamu/tokopedia-product-reviews-2019, Apache-2.0",
        "sampling": "6 products with at least 25 reviews and the highest share of 1-3 star reviews "
                    "(electronics, phones, fashion); first 60 reviews per product in dataset order. "
                    "The dataset has no review dates and no listing text. Units sold is the dataset's "
                    "rounded-down Tokopedia counter.",
        # Produk dipilih karena porsi bintang rendahnya tertinggi, dan cara dataset mengambil ulasan
        # tidak didokumentasikan: tidak diproyeksikan ke unit terjual.
        "sampling_kind": "unknown",
        "products": products,
    })


def prdect() -> None:
    if not PRDECT_CSV.exists():
        print(f"lewati prdect: {PRDECT_CSV.relative_to(REPO)} belum ada")
        return
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in csv.DictReader(PRDECT_CSV.open(encoding="utf-8")):
        grouped[row["Product Name"].strip()].append(row)
    ranked = []
    for name, rows in grouped.items():
        if len(rows) < PRDECT_MIN_REVIEWS or float(rows[0]["Price"]) < PRDECT_MIN_PRICE:
            continue
        low = sum(1 for r in rows if int(r["Customer Rating"]) <= 3)
        ranked.append((-low, -len(rows), name))
    ranked.sort()
    per_category: dict[str, int] = defaultdict(int)
    products = []
    for _low, _n, name in ranked:
        rows = grouped[name]
        category = rows[0]["Category"]
        if per_category[category] >= PRDECT_PER_CATEGORY:
            continue
        per_category[category] += 1
        sid = "pd-" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:12]
        reviews = []
        for i, row in enumerate(rows):
            text, _ = redact(html.unescape(row["Customer Review"]).strip())
            reviews.append({"id": f"{sid}-{i}", "rating": int(row["Customer Rating"]), "text": text})
        products.append({
            "source_item_id": sid,
            "title": html.unescape(name),
            "description": "",
            # Nilai listing di dataset; konsisten per produk kecuali selisih kecil antar waktu ambil.
            "price": float(rows[0]["Price"]),
            "units_sold": int(float(rows[0]["Number Sold"])),
            "reviews": reviews,
        })
        if len(products) == PRDECT_PRODUCTS:
            break
    write("tokopedia-prdect", {
        "channel": "tokopedia", "data_origin": "public_dataset", "captured_at": "2022-12-31T00:00:00+00:00",
        "label": "Tokopedia reviews, PRDECT-ID (public dataset)",
        "source": "PRDECT-ID, Sutoyo et al., Data in Brief (2022); HuggingFace ZakyF/PRDECT-ID, CC-BY-4.0",
        "sampling": f"{PRDECT_PRODUCTS} products with at least {PRDECT_MIN_REVIEWS} reviews and a price of at "
                    f"least Rp{PRDECT_MIN_PRICE:,}, ranked by the number of 1-3 star reviews, at most "
                    f"{PRDECT_PER_CATEGORY} per category; all reviews the dataset holds for each product. "
                    "The dataset over-represents negative reviews (a third are 1 star while listings average "
                    "4.7-4.9), so complaint shares are not projected to units sold. Price and units sold are "
                    "the listing figures in the dataset. Collection dates are not published; 2022 is the "
                    "publication year. No review dates and no listing text.",
        "sampling_kind": "skewed",
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
        "sampling_kind": "unknown",
        "products": products,
    })


# (rating, hari lalu, varian, teks)
TIKTOK = [{
    "source_item_id": "tt-pb-mag-10k",
    "title": "Powerbank magnetik 10000 mAh",
    "units_sold": 1240,
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
}, {
    "source_item_id": "tt-kaos-os-24s",
    "title": "Kaos oversize cotton combed 24s",
    "units_sold": 3150,
    "description": "Kaos oversize bahan cotton combed 24s, jahitan rantai. Ukuran M, L, XL. Lebar dada L 60 cm, "
                   "panjang badan 72 cm. Warna tidak luntur.",
    "reviews": [
        (2, 25, "Hitam / L", "Lebar dada L saya ukur cuma 55 cm, jauh dari 60 cm di deskripsi."),
        (3, 21, "Putih / XL", "Bahannya tipis, lebih mirip 30s daripada 24s."),
        (4, 18, "Hitam / L", "Adem dan jahitannya rapi, tapi ukurannya lebih kecil dari tabel."),
        (2, 14, "Navy / M", "Luntur waktu cucian pertama, air rendamannya biru."),
        (5, 11, "Putih / L", "Nyaman banget dipakai harian, pengiriman cepat."),
        (4, 8, "Hitam / XL", "Bagus, cuma lingkar dadanya pas-pasan, harusnya ambil satu ukuran lebih besar."),
        (5, 5, "Navy / L", "Warnanya sesuai foto."),
        (3, 2, "Hitam / L", "Bahan oke tapi L-nya kekecilan, lebar dada tidak sampai 60."),
    ],
}]
BLIBLI = [{
    "source_item_id": "bb-rc-18",
    "title": "Rice cooker digital 1,8 liter",
    "units_sold": 870,
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
}, {
    "source_item_id": "bb-steamer-1200",
    "title": "Setrika uap genggam 1200 watt",
    "units_sold": 460,
    "description": "Setrika uap genggam 1200 watt, tangki air 250 ml, siap dipakai dalam 30 detik. "
                   "Bisa dipakai tegak untuk gorden dan kemeja yang digantung.",
    "reviews": [
        (2, 22, "", "Panasnya lebih dari satu menit, bukan 30 detik seperti di deskripsi."),
        (3, 18, "", "Waktu dipakai tegak airnya netes ke kemeja."),
        (4, 15, "", "Uapnya kencang dan praktis, tapi tangkinya cepat habis, sekitar 5 menit."),
        (2, 12, "", "Dipakai tegak untuk gorden malah menetes, bajunya jadi basah bercak."),
        (5, 9, "", "Ringan, cocok buat kemeja kerja pagi-pagi."),
        (5, 6, "", "Pengiriman cepat, barang aman."),
        (3, 3, "", "Tunggu panasnya lama, hampir satu setengah menit."),
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
                 "sampling": "Synthetic example, not customer data. Every review of each synthetic product "
                             "is included; units sold is part of the example.",
                 # Toko karangan: seluruh ulasannya ada di paket, jadi sampelnya lengkap by construction.
                 "sampling_kind": "complete", "products": out})


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tokopedia()
    prdect()
    shopee()
    synthetic("tiktok-sintetis", "tiktok", "TikTok Shop synthetic example", TIKTOK)
    synthetic("blibli-sintetis", "blibli", "Blibli synthetic example", BLIBLI)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
