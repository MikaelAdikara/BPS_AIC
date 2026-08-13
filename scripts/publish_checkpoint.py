"""Unggah checkpoint IndoBERT ke HuggingFace Hub (Fase 9, distribusi model).

Bobot berukuran 499 MB dan tidak masuk git. Tanpa jalur distribusi, juri yang meng-clone
repositori hanya mendapat jalur leksikon — sistemnya berjalan, tetapi bukan sistem yang
dijelaskan proposal.

HF Hub dipilih daripada GitHub Release karena unduhannya dapat dijalankan program:
`huggingface_hub.snapshot_download()` bekerja tanpa langkah manual, sedangkan aset Release
menuntut juri mengunduh dan menaruh berkas sendiri di tempat yang tepat.

Jalankan:
    huggingface-cli login          # sekali saja
    python scripts/publish_checkpoint.py --repo NAMA_ANDA/insightulasan-nlp01
    python scripts/publish_checkpoint.py --repo NAMA_ANDA/insightulasan-nlp01 --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CKPT_DIR = REPO / "models" / "indobert-nlp01"

# Kartu model yang ikut terbit di Hub. Ditulis di sini, bukan disalin manual, supaya batas
# klaimnya tidak terpisah dari bobotnya — siapa pun yang mengunduh model ini langsung
# membaca apa yang boleh dan tidak boleh disimpulkan darinya.
CARD = """---
license: apache-2.0
language: [id]
base_model: indobenchmark/indobert-base-p1
tags: [aspect-based-sentiment-analysis, indonesian, e-commerce, umkm]
---

# InsightUlasan NLP-01

IndoBERT yang di-fine-tune untuk klasifikasi aspek dan sentimen pada ulasan e-commerce
Bahasa Indonesia informal. Dibangun untuk AIC COMPFEST 18.

Dua kepala di atas satu encoder bersama: multi-label aspek (11 kelas) dan sentimen tiga kelas.

## Batas klaim — baca sebelum memakai

**Sentimen: tervalidasi.** Pada label manusia independen (NusaX-senti, PRDECT-ID) macro F1
0,730 berbanding 0,700 milik baseline leksikon. Kelas netral membaik dari 0,021 ke 0,645.

**Aspek: BELUM tervalidasi.** Label aspek pada data latih berasal dari labeling function yang
ditulis tim sendiri, sehingga metrik aspek mengukur kesepakatan dengan aturan itu — bukan
akurasi. Angka aspek tidak boleh dikutip sebagai capaian.

**Kelemahan yang diketahui:** model kurang memanggil kelas negatif. Pada PRDECT-ID, 128 dari
420 ulasan berlabel negatif tidak dikenali. Penyebabnya bukan aturan keputusan di batas
ambang — 88% di antaranya diprediksi dengan probabilitas negatif di bawah 0,10, artinya model
yakin ketika ia salah.

Rincian lengkap: <https://github.com/patrick12354/BPS_AIC> (docs/MODEL_CARD.md, LIMITATIONS.md)

## Pemakaian

Model ini memerlukan kelas `DualHeadClassifier` dari repositori di atas; ia bukan checkpoint
`AutoModel` standar.

```python
from huggingface_hub import snapshot_download
snapshot_download(repo_id="{repo_id}", local_dir="models/indobert-nlp01")
```
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="mis. namaanda/insightulasan-nlp01")
    ap.add_argument("--dry-run", action="store_true", help="periksa saja, jangan unggah")
    args = ap.parse_args()

    if not CKPT_DIR.exists():
        print(f"Checkpoint tidak ada: {CKPT_DIR}", file=sys.stderr)
        return 1

    berkas = sorted(p for p in CKPT_DIR.rglob("*") if p.is_file())
    total = sum(p.stat().st_size for p in berkas)
    print(f"{len(berkas)} berkas · {total / 1e6:.0f} MB")
    for p in berkas:
        print(f"  {p.relative_to(CKPT_DIR)}  ({p.stat().st_size / 1e6:.1f} MB)")

    card_path = CKPT_DIR / "README.md"
    card_path.write_text(CARD.replace("{repo_id}", args.repo), encoding="utf-8")
    print(f"\nKartu model ditulis ke {card_path}")

    if args.dry_run:
        print("\n--dry-run: tidak ada yang diunggah.")
        return 0

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Pasang dulu: pip install huggingface_hub", file=sys.stderr)
        return 1

    api = HfApi()
    api.create_repo(args.repo, repo_type="model", exist_ok=True)
    api.upload_folder(folder_path=str(CKPT_DIR), repo_id=args.repo, repo_type="model")
    print(f"\nTerbit: https://huggingface.co/{args.repo}")
    print("Perbarui CHECKPOINT_REPO di scripts/download_checkpoint.py bila namanya berbeda.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
