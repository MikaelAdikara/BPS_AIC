"""Bahan toko WordPress demo: `docker/wordpress/catalog.json` dan gambar produk.

Katalog diekspor dari `demo_catalog.py` supaya toko WooCommerce asli dan akun demo Deciqo
memakai produk dan ulasan yang sama persis (id ikut sama). Gambar produk berupa ilustrasi datar
yang digambar di sini, bukan foto: semua isi toko demo buatan tim.

    .venv/Scripts/python.exe scripts/build_wp_store.py

`tests/unit/test_wp_store_catalog.py` gagal bila catalog.json tertinggal dari demo_catalog.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.deciqo import demo_catalog  # noqa: E402

OUT = ROOT / "docker" / "wordpress"

# Nama pengulas sintetis; Deciqo tidak pernah membaca nama pengulas.
AUTHORS = ["Rina", "Bagus", "Dewi", "Fajar", "Sari", "Yoga", "Maya", "Andi", "Putri", "Reza", "Lestari", "Dimas"]


def catalog() -> dict:
    products = []
    n = 0
    for product in demo_catalog.PRODUCTS:
        reviews = []
        for rid, rating, days, _variant, text in product["reviews"]:
            reviews.append({"id": rid, "rating": rating, "days_ago": days, "text": text,
                            "author": AUTHORS[n % len(AUTHORS)]})
            n += 1
        products.append({
            "id": product["id"], "sku": product["sku"], "name": product["name"], "price": product["price"],
            "description": product["description"], "attributes": product["attributes"], "reviews": reviews,
        })
    return {"_note": "Dibuat oleh scripts/build_wp_store.py dari demo_catalog.py. Jangan diedit manual.",
            "products": products}


def draw_images() -> None:
    from PIL import Image, ImageDraw, ImageFilter  # noqa: PLC0415

    size, s = 800, 2  # digambar 2x lalu diperkecil supaya tepinya halus
    w = size * s

    def canvas(bg):
        img = Image.new("RGB", (w, w), bg)
        return img, ImageDraw.Draw(img)

    def shadow(img, box):
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse(box, fill=(0, 0, 0, 60))
        img.paste(layer.filter(ImageFilter.GaussianBlur(28)), (0, 0), layer.filter(ImageFilter.GaussianBlur(28)))

    def p(*values):
        return [v * s for v in values]

    images = {}

    # Tas laptop kanvas
    img, d = canvas((232, 226, 214))
    shadow(img, p(170, 610, 630, 660))
    d = ImageDraw.Draw(img)
    d.arc(p(270, 150, 530, 420), 180, 360, fill=(52, 52, 56), width=22 * s)
    d.rounded_rectangle(p(160, 280, 640, 630), radius=40 * s, fill=(46, 48, 52))
    d.rounded_rectangle(p(160, 280, 640, 360), radius=40 * s, fill=(60, 62, 67))
    d.rectangle(p(160, 330, 640, 360), fill=(60, 62, 67))
    d.rounded_rectangle(p(250, 430, 550, 590), radius=24 * s, fill=(58, 60, 65))
    d.line(p(265, 450, 535, 450), fill=(150, 150, 150), width=4 * s)
    d.rounded_rectangle(p(385, 300, 415, 345), radius=6 * s, fill=(190, 160, 90))
    images["tas-knv-14"] = img

    # Kemeja linen
    img, d = canvas((222, 232, 238))
    shadow(img, p(190, 650, 610, 690))
    d = ImageDraw.Draw(img)
    body = (246, 240, 226)
    d.polygon(p(300, 170, 500, 170, 640, 250, 700, 430, 610, 460, 580, 360, 580, 660, 220, 660, 220, 360,
                190, 460, 100, 430, 160, 250), fill=body)
    d.polygon(p(300, 170, 400, 250, 500, 170, 470, 160, 400, 205, 330, 160), fill=(233, 225, 206))
    d.polygon(p(330, 160, 400, 205, 360, 245), fill=(255, 252, 244))
    d.polygon(p(470, 160, 400, 205, 440, 245), fill=(255, 252, 244))
    d.line(p(400, 230, 400, 660), fill=(220, 210, 190), width=3 * s)
    for y in (280, 350, 420, 490, 560):
        d.ellipse(p(392, y, 408, y + 16), fill=(200, 186, 160))
    d.rounded_rectangle(p(270, 300, 350, 370), radius=6 * s, outline=(220, 210, 190), width=3 * s)
    images["kmj-linen"] = img

    # Kursi lipat camping
    img, d = canvas((218, 232, 220))
    shadow(img, p(170, 650, 630, 700))
    d = ImageDraw.Draw(img)
    frame = (60, 66, 72)
    d.line(p(230, 660, 560, 380), fill=frame, width=16 * s)
    d.line(p(570, 660, 240, 380), fill=frame, width=16 * s)
    d.line(p(250, 150, 250, 420), fill=frame, width=16 * s)
    d.line(p(550, 150, 550, 420), fill=frame, width=16 * s)
    d.rounded_rectangle(p(240, 160, 560, 330), radius=12 * s, fill=(34, 110, 84))
    d.rounded_rectangle(p(220, 370, 580, 430), radius=14 * s, fill=(29, 95, 72))
    d.line(p(240, 230, 560, 230), fill=(44, 130, 100), width=6 * s)
    images["krs-lipat"] = img

    # Botol minum stainless
    img, d = canvas((236, 228, 222))
    shadow(img, p(290, 680, 510, 710))
    d = ImageDraw.Draw(img)
    for i in range(160):  # gradasi logam
        shade = int(150 + 80 * (1 - abs(i - 60) / 100))
        d.line(p(320 + i, 250, 320 + i, 680), fill=(shade, shade + 4, shade + 10), width=s)
    d.rounded_rectangle(p(320, 250, 480, 690), radius=40 * s, outline=(236, 228, 222), width=0)
    d.rounded_rectangle(p(335, 140, 465, 255), radius=20 * s, fill=(28, 70, 110))
    d.rounded_rectangle(p(360, 110, 440, 150), radius=10 * s, fill=(28, 70, 110))
    d.rectangle(p(320, 255, 480, 270), fill=(120, 124, 132))
    images["btl-750"] = img

    (OUT / "images").mkdir(parents=True, exist_ok=True)
    for name, img in images.items():
        img.resize((size, size), Image.LANCZOS).save(OUT / "images" / f"{name}.png", optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "catalog.json").write_text(json.dumps(catalog(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    draw_images()
    print(f"catalog.json dan {len(demo_catalog.PRODUCTS)} gambar ditulis ke {OUT}")


if __name__ == "__main__":
    main()
