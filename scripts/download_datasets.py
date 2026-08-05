"""Unduh dataset publik untuk fine-tuning model teks (blueprint bagian 26.1 langkah 1-2).

Dataset TIDAK di-commit ke repository (alasan lisensi + ukuran, bagian 31.1) - script ini
mengunduh ulang dari sumber resmi ke `data/raw/`.

Pemakaian:
    python scripts/download_datasets.py              # unduh semua
    python scripts/download_datasets.py --list       # tampilkan sumber + lisensi saja
    python scripts/download_datasets.py --only prdect_id

Catatan lisensi (bagian 26.1 langkah 2, open question bagian 48): ketiga dataset diverifikasi
punya lisensi eksplisit di halaman sumbernya - lihat DATASETS di bawah dan docs/DATASET_CARD.md.
PRDECT-ID berlisensi CC-BY-4.0 sehingga ATRIBUSI WAJIB dicantumkan pada proposal dan model card.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"


@dataclass(frozen=True)
class DatasetSpec:
    key: str
    repo_id: str
    files: tuple[str, ...]
    license_id: str
    license_verified: bool
    role: str
    citation: str
    notes: str = ""
    mirrors: tuple[str, ...] = field(default_factory=tuple)


# Sumber kanonik dipilih dari beberapa mirror yang tersedia di HuggingFace.
# Kriteria: lisensi eksplisit, format file datar (CSV/JSON, bukan loading script yang
# memerlukan trust_remote_code), dan jumlah unduhan tertinggi sebagai proksi keterpakaian.
DATASETS: tuple[DatasetSpec, ...] = (
    DatasetSpec(
        key="prdect_id",
        repo_id="ZakyF/PRDECT-ID",
        files=("PRDECT-ID Dataset.csv",),
        license_id="cc-by-4.0",
        license_verified=True,
        role="training inti",
        citation=(
            "Sutoyo, R. et al. PRDECT-ID: Indonesian product reviews dataset for emotions "
            "classification tasks. Data in Brief (2022). arXiv:2406.10118"
        ),
        notes=(
            "CC-BY-4.0: ATRIBUSI WAJIB. Mirror alternatif SEACrowd/prdect_id memakai loading "
            "script (butuh trust_remote_code) - sengaja tidak dipakai."
        ),
        mirrors=("SEACrowd/prdect_id", "reyhanksatria05/PRDECT-ID_Dataset"),
    ),
    DatasetSpec(
        key="ecommerce_sentiment",
        repo_id="AIbnuHibban/e-commerce-sentiment-bahasa-indonesia",
        files=("simple.json", "challange.json"),
        license_id="mit",
        license_verified=True,
        role="training inti",
        citation="e-commerce-sentiment-bahasa-indonesia, HuggingFace Datasets (MIT).",
        notes=(
            "Dua file: 'simple' (kalimat lugas) dan 'challange' (sarkasme/ironi). Keduanya "
            "diunduh - subset challange berguna untuk error analysis bagian 26.1 langkah 15."
        ),
        mirrors=(
            "joyadriansyah/e-commerce-sentiment-bahasa-indonesia",
            "zhiaa/e-commerce-sentiment-bahasa-indonesia",
        ),
    ),
    DatasetSpec(
        key="tokopedia_reviews_2019",
        repo_id="farhamu/tokopedia-product-reviews-2019",
        files=("tokopedia-product-reviews-2019.csv",),
        license_id="apache-2.0",
        license_verified=True,
        role="training tambahan + domain testing",
        citation="Tokopedia Product Reviews 2019, HuggingFace Datasets (Apache-2.0).",
        notes=(
            "Sebagian disisihkan untuk DOMAIN TESTING (menguji generalisasi lintas sumber), "
            "bukan seluruhnya dipakai training - bagian 26.1."
        ),
    ),
)


def print_sources() -> None:
    print(f"{'key':24s} {'repo_id':52s} {'lisensi':12s} peran")
    print("-" * 110)
    for spec in DATASETS:
        mark = "OK" if spec.license_verified else "BELUM"
        print(f"{spec.key:24s} {spec.repo_id:52s} {spec.license_id:12s} {spec.role}  [{mark}]")
    print(
        "\nSeluruh dataset diunduh ke data/raw/ dan TIDAK di-commit (blueprint bagian 31.1).\n"
        "PRDECT-ID berlisensi CC-BY-4.0 - atribusi wajib pada proposal dan MODEL_CARD.md."
    )


def download(spec: DatasetSpec) -> list[Path]:
    from huggingface_hub import hf_hub_download

    target_dir = RAW_DIR / spec.key
    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for filename in spec.files:
        print(f"  - {filename} ... ", end="", flush=True)
        cached = hf_hub_download(
            repo_id=spec.repo_id,
            filename=filename,
            repo_type="dataset",
            local_dir=target_dir,
        )
        path = Path(cached)
        print(f"{path.stat().st_size / 1_048_576:.1f} MB")
        written.append(path)

    (target_dir / "SOURCE.json").write_text(
        json.dumps(
            {
                "key": spec.key,
                "repo_id": spec.repo_id,
                "source_url": f"https://huggingface.co/datasets/{spec.repo_id}",
                "license": spec.license_id,
                "license_verified": spec.license_verified,
                "role": spec.role,
                "citation": spec.citation,
                "notes": spec.notes,
                "files": list(spec.files),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="tampilkan sumber + lisensi, tanpa unduh")
    parser.add_argument("--only", help="unduh satu dataset saja (key)")
    args = parser.parse_args()

    if args.list:
        print_sources()
        return 0

    specs = DATASETS
    if args.only:
        specs = tuple(s for s in DATASETS if s.key == args.only)
        if not specs:
            print(f"Key tidak dikenal: {args.only}", file=sys.stderr)
            print_sources()
            return 1

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        print(f"\n{spec.key}  ({spec.repo_id}, {spec.license_id})")
        download(spec)

    print(f"\nSelesai. Data tersimpan di {RAW_DIR.relative_to(REPO_ROOT)}/ (tidak di-commit).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
