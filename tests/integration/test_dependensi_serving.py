"""Menjaga agar jalur inferensi tidak menarik dependensi pelatihan.

Bug yang mendasari test ini adalah yang paling mahal sejauh ini justru karena ia sunyi:
`apps/api` meng-import DualHeadClassifier dari `ml/text/finetune.py`, yang meng-import pandas
di level modul. Image API sengaja tidak memasang pandas (apps/api/requirements.txt), sehingga
import gagal, tertangkap penanganan fallback, dan sistem menjawab "siap" sambil menjalankan
jalur leksikon. Model yang menjadi inti produk tidak pernah aktif di Docker, dan satu-satunya
petunjuknya adalah satu baris di stdout.

Test dijalankan dalam subprocess dengan paket pelatihan diblokir, meniru isi image API.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ML_TEXT = REPO / "ml" / "text"

# Paket PELATIHAN milik proyek ini yang tidak ikut ke image API.
#
# `accelerate` sengaja TIDAK didaftarkan meski juga absen dari image: ia extra opsional milik
# transformers, bukan dependensi proyek. Transformers memeriksa keberadaannya lebih dulu, jadi
# di image ia memang tidak pernah di-import - sudah diverifikasi langsung di container. Yang
# terjadi bila ia diblokir di sini hanyalah venv pengembang (tempat accelerate terpasang)
# mengambil jalur berbeda lalu gagal, yaitu menguji kondisi yang tidak pernah ada.
HANYA_PELATIHAN = ["pandas", "datasets", "matplotlib", "seaborn"]

PROBE = textwrap.dedent("""
    import sys

    class Penghalang:
        def find_module(self, nama, path=None):
            return self if nama.split(".")[0] in TERLARANG else None
        def load_module(self, nama):
            raise ImportError(f"{nama} tidak ada di image API")

    TERLARANG = set(sys.argv[2].split(","))
    sys.meta_path.insert(0, Penghalang())
    sys.path.insert(0, sys.argv[1])

    from model import DualHeadClassifier  # noqa: F401
    print("OK")
""")


def test_kelas_model_dapat_diimport_tanpa_paket_pelatihan():
    hasil = subprocess.run(
        [sys.executable, "-c", PROBE, str(ML_TEXT), ",".join(HANYA_PELATIHAN)],
        capture_output=True, text=True, cwd=REPO,
    )
    assert "OK" in hasil.stdout, (
        "ml/text/model.py menarik dependensi pelatihan; jalur serving akan diam-diam "
        f"jatuh ke leksikon.\n{hasil.stderr[-1200:]}"
    )


def test_probe_memang_memblokir_sesuatu():
    """Tanpa ini, test di atas lolos bahkan bila penghalangnya tidak berfungsi."""
    bukti = textwrap.dedent("""
        import sys
        class Penghalang:
            def find_module(self, nama, path=None):
                return self if nama.split(".")[0] in TERLARANG else None
            def load_module(self, nama):
                raise ImportError("diblokir")
        TERLARANG = {"pandas"}
        sys.meta_path.insert(0, Penghalang())
        try:
            import pandas  # noqa: F401
        except ImportError:
            print("TERBLOKIR")
    """)
    hasil = subprocess.run([sys.executable, "-c", bukti], capture_output=True, text=True)
    assert "TERBLOKIR" in hasil.stdout


def test_adapter_melaporkan_alasan_saat_jatuh_ke_leksikon():
    """Fallback yang bisu adalah separuh dari bug ini - alasannya wajib dapat dibaca."""
    from app.adapters.text_model import TextModelAdapter

    adapter = TextModelAdapter(checkpoint=Path("/jalur/yang/tidak/ada/model.pt"))
    assert adapter.mode == "fallback"
    assert adapter.fallback_reason
    assert "checkpoint" in adapter.fallback_reason.lower()


@pytest.mark.skipif(
    not (REPO / "models" / "indobert-nlp01" / "model.pt").exists(),
    reason="checkpoint tidak tersedia di mesin ini",
)
def test_adapter_tidak_melaporkan_alasan_saat_model_aktif():
    from app.adapters.text_model import TextModelAdapter

    adapter = TextModelAdapter()
    assert adapter.mode == "full"
    assert adapter.fallback_reason is None


def test_probe_ini_memang_menangkap_bug_aslinya():
    """Bukti bahwa penjaganya bukan hiasan: import lewat `finetune` - bentuk kode SEBELUM
    perbaikan - tetap gagal pada probe yang sama."""
    probe = PROBE.replace("from model import DualHeadClassifier",
                          "from finetune import DualHeadClassifier")
    hasil = subprocess.run(
        [sys.executable, "-c", probe, str(ML_TEXT), ",".join(HANYA_PELATIHAN)],
        capture_output=True, text=True, cwd=REPO,
    )
    assert "OK" not in hasil.stdout
    assert "pandas" in hasil.stderr
