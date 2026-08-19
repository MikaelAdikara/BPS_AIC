"""Menjaga agar repositori hasil clone benar-benar dapat di-build.

Dua kegagalan yang sudah benar-benar terjadi dan pesannya sama-sama menyesatkan:

1. api.Dockerfile menyalin data/processed/category_baseline.json, tetapi .gitignore
   mengecualikan seluruh data/processed/*, sehingga berkasnya tidak pernah ikut ter-commit.
2. api.Dockerfile menyalin data/samples/demo_shopee_asli.csv, tetapi .dockerignore
   mengecualikan seluruh data/ dan hanya mengizinkan dua berkas per nama.

Keduanya melaporkan "not found" - padahal berkasnya jelas ada di disk pengembang. Yang hilang
adalah jalurnya menuju konteks build. Test ini murah dan berjalan tanpa Docker.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOCKERFILE = REPO / "docker" / "api.Dockerfile"


def _jalur_data_yang_disalin() -> list[str]:
    jalur = []
    for baris in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        bagian = baris.split()
        if len(bagian) >= 2 and bagian[0] == "COPY" and bagian[1].startswith("data/"):
            jalur.append(bagian[1])
    return jalur


def test_dockerfile_memang_menyalin_sesuatu_dari_data():
    """Kalau daftarnya kosong, dua test di bawah lolos tanpa memeriksa apa pun."""
    assert _jalur_data_yang_disalin()


@pytest.mark.parametrize("jalur", _jalur_data_yang_disalin())
def test_berkas_yang_disalin_ada_di_disk(jalur):
    assert (REPO / jalur).exists(), f"{jalur} dirujuk api.Dockerfile tetapi tidak ada"


@pytest.mark.parametrize("jalur", _jalur_data_yang_disalin())
def test_berkas_yang_disalin_ikut_ter_commit(jalur):
    """Yang ada di disk pengembang belum tentu ada pada orang yang meng-clone."""
    hasil = subprocess.run(
        ["git", "ls-files", "--error-unmatch", jalur],
        cwd=REPO, capture_output=True, text=True,
    )
    assert hasil.returncode == 0, f"{jalur} tidak dilacak git - periksa .gitignore"


@pytest.mark.parametrize("jalur", _jalur_data_yang_disalin())
def test_berkas_yang_disalin_lolos_dockerignore(jalur):
    """.dockerignore membuang data/ seluruhnya; tiap COPY butuh baris pengecualiannya sendiri."""
    baris = (REPO / ".dockerignore").read_text(encoding="utf-8").splitlines()
    assert f"!{jalur}" in baris, f"tambahkan '!{jalur}' ke .dockerignore"
