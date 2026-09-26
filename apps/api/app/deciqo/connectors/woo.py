"""Klien WooCommerce REST `wc/v3` read-only.

Hanya membaca produk dan ulasan yang sudah disetujui; identitas reviewer tidak pernah diambil.

URL toko diperlakukan sebagai input tidak tepercaya (SSRF): hanya HTTPS, tanpa kredensial atau
port aneh di URL, semua alamat hasil DNS harus publik, dicek ulang di setiap request (DNS bisa
berubah di antara dua request), redirect tidak diikuti, dan ukuran respons dibatasi. Satu-satunya
pengecualian adalah host toko sintetis internal, dan hanya bila `WOO_DEMO_MODE` aktif.
"""

from __future__ import annotations

import html
import ipaddress
import re
import socket
from urllib.parse import urlparse

import httpx

from .. import settings
from ..errors import DeciqoError

API_PATH = "/wp-json/wc/v3"
TIMEOUT = httpx.Timeout(10.0, connect=5.0)
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_PAGES = 50

_TAGS = re.compile(r"<[^>]+>")


class WooError(Exception):
    """Kegagalan membaca toko. `code` stabil untuk UI dan status sumber."""

    def __init__(self, code: str, message: str, status: int | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


def demo_host() -> str | None:
    return urlparse(settings.woo_base_url()).hostname


def is_demo_url(url: str) -> bool:
    parsed = urlparse(url)
    return settings.woo_demo_mode() and parsed.hostname is not None and parsed.hostname == demo_host()


def _public_addresses(host: str, port: int) -> None:
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise DeciqoError(422, "invalid_store_url", "The store address could not be found.") from exc
    if not infos:
        raise DeciqoError(422, "invalid_store_url", "The store address could not be found.")
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global or address.is_multicast:
            raise DeciqoError(422, "store_not_public", "The store must be reachable on the public internet.")


def validate_store_url(url: str) -> str:
    """URL toko yang aman dipanggil, dinormalisasi tanpa garis miring di akhir."""
    raw = (url or "").strip()
    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.hostname:
        raise DeciqoError(422, "invalid_store_url", "Enter the full store address, e.g. https://shop.example.com.")
    if is_demo_url(raw):
        return raw.rstrip("/")
    if parsed.scheme != "https":
        raise DeciqoError(422, "invalid_store_url", "The store address must start with https://.")
    if parsed.username or parsed.password:
        raise DeciqoError(422, "invalid_store_url", "Remove the user name or password from the address.")
    if parsed.port not in (None, 443):
        raise DeciqoError(422, "invalid_store_url", "Use the store's standard HTTPS address without a port.")
    if parsed.query or parsed.fragment:
        raise DeciqoError(422, "invalid_store_url", "Remove anything after ? or # from the address.")
    _public_addresses(parsed.hostname, 443)
    return f"https://{parsed.hostname}{parsed.path.rstrip('/')}"


def clean_html(value: str | None) -> str:
    text = _TAGS.sub(" ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


class WooClient:
    def __init__(self, base_url: str, consumer_key: str, consumer_secret: str,
                 transport: httpx.BaseTransport | None = None):
        self.base_url = base_url.rstrip("/")
        self.auth = (consumer_key, consumer_secret)
        self._transport = transport

    def _get(self, path: str, params: dict) -> tuple[list, dict]:
        # Validasi ulang per request: alamat DNS bisa berubah setelah koneksi disimpan.
        validate_store_url(self.base_url)
        url = f"{self.base_url}{API_PATH}{path}"
        try:
            with httpx.Client(timeout=TIMEOUT, follow_redirects=False, transport=self._transport) as client:
                with client.stream("GET", url, params=params, auth=self.auth,
                                   headers={"Accept": "application/json"}) as response:
                    if response.status_code in (401, 403):
                        raise WooError("store_auth_failed", "The store rejected the API key.", response.status_code)
                    if 300 <= response.status_code < 400:
                        raise WooError("store_redirected", "The store redirected the request; use its final address.",
                                       response.status_code)
                    if response.status_code >= 400:
                        raise WooError("store_unavailable", f"The store answered with HTTP {response.status_code}.",
                                       response.status_code)
                    body = b""
                    for chunk in response.iter_bytes():
                        body += chunk
                        if len(body) > MAX_RESPONSE_BYTES:
                            raise WooError("store_response_too_large", "The store response was too large.")
                    headers = {k.lower(): v for k, v in response.headers.items()}
        except httpx.HTTPError as exc:
            raise WooError("store_unavailable", "The store could not be reached.") from exc
        try:
            import json  # noqa: PLC0415

            data = json.loads(body or b"[]")
        except ValueError as exc:
            raise WooError("store_bad_response", "The store did not answer with WooCommerce data.") from exc
        if not isinstance(data, list):
            raise WooError("store_bad_response", "The store did not answer with WooCommerce data.")
        return data, headers

    def _paged(self, path: str, params: dict) -> list[dict]:
        items: list[dict] = []
        page = 1
        per_page = settings.woo_page_size()
        while page <= MAX_PAGES:
            batch, headers = self._get(path, {**params, "page": page, "per_page": per_page})
            items.extend(batch)
            try:
                total_pages = int(headers.get("x-wp-totalpages", "1"))
            except ValueError:
                total_pages = 1
            if page >= total_pages or not batch:
                break
            page += 1
        return items

    def products(self) -> list[dict]:
        return self._paged("/products", {"status": "publish"})

    def reviews(self) -> list[dict]:
        return self._paged("/products/reviews", {"status": "approved"})

    def catalog(self) -> list[dict]:
        """Produk + ulasan dalam bentuk `ingest.upsert_catalog`."""
        by_product: dict[str, list[dict]] = {}
        for review in self.reviews():
            if review.get("status", "approved") != "approved":
                continue
            by_product.setdefault(str(review.get("product_id")), []).append({
                "id": str(review.get("id")),
                "rating": review.get("rating"),
                "text": clean_html(review.get("review")),
                "review_time": _gmt(review.get("date_created_gmt")),
                # Nama/email reviewer sengaja tidak diambil sama sekali.
            })
        catalog = []
        for product in self.products():
            pid = str(product.get("id"))
            attributes = product.get("attributes") or []
            images = product.get("images") or []
            description = clean_html(product.get("description")) or clean_html(product.get("short_description"))
            catalog.append({
                "source_item_id": pid,
                "title": clean_html(product.get("name")),
                "url": product.get("permalink") or "",
                "description": description,
                "specs": {a.get("name", ""): ", ".join(a.get("options") or []) for a in attributes if a.get("name")},
                "variants": next((a.get("options") or [] for a in attributes
                                  if (a.get("name") or "").lower() in {"ukuran", "size"}), []),
                "image_url": images[0].get("src") if images else None,
                "price": _float(product.get("price")),
                "units_sold": product.get("total_sales"),
                "reviews": by_product.get(pid, []),
            })
        return catalog


def _gmt(value: str | None) -> str | None:
    if not value:
        return None
    return value if ("+" in value[10:] or value.endswith("Z")) else f"{value}+00:00"


def _float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
