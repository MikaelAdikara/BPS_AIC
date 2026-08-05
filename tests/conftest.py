"""Konfigurasi pytest - membuat paket backend dapat diimpor tanpa instalasi."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))
