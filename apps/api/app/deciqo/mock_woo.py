"""Toko WooCommerce sintetis untuk demo (service `woo-demo`).

Meniru potongan REST `wc/v3` yang dibaca konektor (produk dan ulasan, dengan paginasi dan
autentikasi key), sehingga jalur klien yang sama dipakai untuk toko nyata. Semua isi toko ini
sintetis dan diberi label begitu di aplikasi.
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Deciqo synthetic Woo store", docs_url=None, redoc_url=None)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "synthetic": True}
