"""Demo publik: kunci acak + Cloudflare quick tunnel untuk storefront WooCommerce dan Deciqo.

    .venv/Scripts/python.exe scripts/demo_tunnel.py keys          # sekali: ganti kunci demo bawaan di .env
    .venv/Scripts/python.exe scripts/demo_tunnel.py up            # nyalakan semua + tunnel, cetak URL & QR
    .venv/Scripts/python.exe scripts/demo_tunnel.py urls          # cetak ulang URL tunnel yang sedang jalan
    .venv/Scripts/python.exe scripts/demo_tunnel.py down          # matikan tunnel saja (app tetap jalan lokal)
    .venv/Scripts/python.exe scripts/demo_tunnel.py keys --show   # tampilkan kunci di terminal ini

`keys` hanya mengisi kunci yang kosong atau masih bernilai bawaan publik (`--rotate` mengganti
semuanya). Nilai tidak pernah dicetak kecuali dengan `--show`; semuanya tersimpan di `.env`
(tidak ikut git). Pendaftaran akun baru dimatikan karena Deciqo jadi bisa dibuka publik.

Quick tunnel tidak butuh akun; URL-nya acak dan berganti setiap tunnel dinyalakan ulang.
"""

from __future__ import annotations

import re
import secrets
import string
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"
OUT = ROOT / "tmp" / "demo-tunnel"
PROFILES = ["--profile", "store", "--profile", "tunnel"]
URL = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")
ALNUM = string.ascii_letters + string.digits


def _token(n: int) -> str:
    return "".join(secrets.choice(ALNUM) for _ in range(n))


# nama → (pembuat nilai, nilai bawaan publik yang wajib diganti)
KEYS = {
    "WOO_WEBHOOK_SECRET": (lambda: secrets.token_urlsafe(32), {"", "deciqo-local-webhook-secret"}),
    "WOO_LOCAL_ADMIN_PASSWORD": (lambda: _token(20), {"", "deciqo-demo-2026"}),
    # Application password WordPress hanya boleh huruf dan angka.
    "WOO_LOCAL_API_PASSWORD": (lambda: _token(32), {"", "deciqoLocalStoreKey2026"}),
    "DECIQO_DEMO_PASSWORD": (lambda: _token(16), {"", "deciqo-demo"}),
}
FIXED = {"DECIQO_ALLOW_SIGNUP": "false"}


def _read_env() -> list[str]:
    return ENV.read_text(encoding="utf-8").splitlines() if ENV.exists() else []


def _get(lines: list[str], name: str) -> str | None:
    for line in lines:
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip()
    return None


def _set(lines: list[str], name: str, value: str) -> None:
    for i, line in enumerate(lines):
        if line.startswith(name + "="):
            lines[i] = f"{name}={value}"
            return
    lines.append(f"{name}={value}")


def keys(rotate: bool = False, show: bool = False) -> None:
    lines = _read_env()
    changed = []
    for name, (make, defaults) in KEYS.items():
        current = _get(lines, name)
        if rotate or current is None or current in defaults:
            _set(lines, name, make())
            changed.append(name)
    for name, value in FIXED.items():
        if _get(lines, name) != value:
            _set(lines, name, value)
            changed.append(name)
    if changed:
        ENV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Kunci diperbarui: {', '.join(changed) or 'tidak ada (sudah acak)'}")
    print("Semua tersimpan di .env. Jalankan `demo_tunnel.py up` supaya api dan toko memakainya.")
    if show:
        for name in KEYS:
            print(f"  {name}={_get(lines, name)}")
    else:
        print("Tampilkan nilainya dengan: demo_tunnel.py keys --show")


def _compose(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["docker", "compose", *PROFILES, *args], cwd=ROOT, check=not capture,
                          capture_output=capture, text=True, encoding="utf-8", errors="replace")


def _tunnel_urls(timeout: float = 90) -> dict[str, str]:
    deadline = time.time() + timeout
    found: dict[str, str] = {}
    while time.time() < deadline and len(found) < 2:
        for service in ("tunnel-store", "tunnel-app"):
            if service in found:
                continue
            logs = _compose("logs", "--no-log-prefix", service, capture=True).stdout or ""
            urls = URL.findall(logs)
            if urls:
                found[service] = urls[-1]  # setelah restart, URL terbaru ada di akhir log
        if len(found) < 2:
            time.sleep(2)
    return found


def _qr(url: str, name: str) -> Path | None:
    try:
        import segno  # noqa: PLC0415
    except ImportError:
        return None
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.png"
    segno.make(url, error="m").save(path, scale=10, border=2)
    return path


def urls() -> None:
    found = _tunnel_urls()
    if len(found) < 2:
        print("URL tunnel belum muncul. Cek: docker compose --profile store --profile tunnel logs tunnel-store")
        sys.exit(1)
    store, app = found["tunnel-store"], found["tunnel-app"]
    lines = [
        f"Storefront (untuk juri) : {store}",
        f"  produk demo           : {store}/product/kursi-lipat-camping/",
        f"  admin WordPress       : {store}/wp-admin",
        f"Deciqo                  : {app}",
    ]
    qr = [p for p in (_qr(f"{store}/product/kursi-lipat-camping/", "storefront-qr"), _qr(app, "deciqo-qr")) if p]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "links.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if qr:
        print("QR:", ", ".join(str(p.relative_to(ROOT)) for p in qr))
    else:
        print("QR belum dibuat: pasang dulu `.venv/Scripts/python.exe -m pip install segno`.")
    print("Login Deciqo: akun demo dengan DECIQO_DEMO_PASSWORD dari .env (tombol 'Coba demo' memakai "
          "password bawaan, jadi tidak berlaku setelah `keys`).")


def up() -> None:
    lines = _read_env()
    weak = [n for n, (_, defaults) in KEYS.items() if (_get(lines, n) or "") in defaults]
    if weak:
        print(f"Kunci masih bawaan publik: {', '.join(weak)}. Jalankan `demo_tunnel.py keys` dulu.")
        sys.exit(1)
    # Recreate api dan toko: nilai .env baru (kunci) hanya terbaca saat container dibuat.
    _compose("up", "-d", "--build", "--force-recreate", "api", "wordpress")
    _compose("up", "-d", "--build")
    urls()


def down() -> None:
    _compose("stop", "tunnel-store", "tunnel-app")
    print("Tunnel dimatikan. Deciqo dan toko tetap jalan di localhost:3000 dan localhost:8081.")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "up"
    flags = set(sys.argv[2:])
    if command == "keys":
        keys(rotate="--rotate" in flags, show="--show" in flags)
    elif command == "up":
        up()
    elif command == "urls":
        urls()
    elif command == "down":
        down()
    else:
        print(__doc__)
        sys.exit(2)
