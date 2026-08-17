"""Unduh checkpoint IndoBERT dari HuggingFace Hub.

Inilah satu-satunya langkah manual yang dibutuhkan juri sebelum menjalankan sistem penuh.
Tanpa berkas ini sistem TETAP berjalan memakai jalur leksikon dan menyatakan keterbatasannya
di `/api/v1/readiness` — tetapi yang berjalan bukan sistem yang dijelaskan proposal.

Jalankan:
    python scripts/download_checkpoint.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEST = REPO / "models" / "indobert-nlp01"

# Diperbarui setelah publish_checkpoint.py dijalankan.
CHECKPOINT_REPO = "MikaelAdi/insightulasan-nlp01"


def main() -> int:
    if (DEST / "model.pt").exists():
        print(f"Checkpoint sudah ada di {DEST} — tidak ada yang perlu diunduh.")
        return 0

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("Pasang dulu: pip install huggingface_hub", file=sys.stderr)
        return 1

    print(f"Mengunduh {CHECKPOINT_REPO} (~499 MB)…", flush=True)
    snapshot_download(repo_id=CHECKPOINT_REPO, local_dir=str(DEST))
    print(f"Selesai: {DEST}")
    print("Jalankan ulang API agar checkpoint terbaca.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
