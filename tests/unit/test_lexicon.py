"""Test regresi labeling function — mengunci bug yang ditemukan lewat error analysis pada gold.

Setiap test di berkas ini mewakili kekeliruan NYATA yang pernah terjadi dan sempat merusak
label silver. Test-nya ada supaya perbaikan itu tidak diam-diam kembali saat leksikon disunting.
"""

import sys
from pathlib import Path

import pytest

ML_TEXT = Path(__file__).resolve().parents[2] / "ml" / "text"
if str(ML_TEXT) not in sys.path:
    sys.path.insert(0, str(ML_TEXT))

from lexicon import ASPECT_PATTERNS, FALLBACK_ASPECT, FALLBACK_PATTERN  # noqa: E402
from preprocess import normalize, polarity_score, split_clauses  # noqa: E402


def aspects_of(text: str) -> set[str]:
    """Tiru logika pelabelan aspek pada build_dataset.py."""
    clause = normalize(text)
    found = {a for a, pat in ASPECT_PATTERNS.items() if pat.search(clause)}
    if not found and FALLBACK_PATTERN.search(clause):
        found = {FALLBACK_ASPECT}
    return found


def sentiment_of(text: str) -> str:
    pos, neg = polarity_score(normalize(text))
    return "positif" if pos > neg else "negatif" if neg > pos else "netral"


# ---------------------------------------------------------------- bug aspek


@pytest.mark.parametrize("text", ["enak dipakai", "enak dimainin", "enak d pake ngegame"])
def test_enak_tidak_memicu_aspek_rasa_di_konteks_non_makanan(text):
    """Kata "enak" dulu memicu rasa_kualitas_makanan — 22 kasus over-label pada gold."""
    assert "rasa_kualitas_makanan" not in aspects_of(text)


@pytest.mark.parametrize("text", ["rasanya enak", "rasa nya manis banget", "kuenya asem"])
def test_konteks_makanan_yang_sebenarnya_tetap_terdeteksi(text):
    assert "rasa_kualitas_makanan" in aspects_of(text)


def test_barang_sudah_diterima_adalah_pengiriman_bukan_kualitas():
    """Dulu tidak terdeteksi apa pun lalu jatuh ke aturan cadangan dan salah jadi kualitas."""
    found = aspects_of("barang sudah di terima")
    assert "pengiriman" in found
    assert "kualitas_produk" not in found


def test_variasi_kata_sampai_terdeteksi():
    """"lama banget sampenya" dulu tidak terdeteksi karena leksikon hanya memuat "sampai"."""
    assert "pengiriman" in aspects_of("lama banget sampenya")


def test_nyaman_dipakai_adalah_kualitas_bukan_kemudahan():
    """Bentuk telanjang "dipakai" dulu memicu kemudahan_penggunaan secara keliru."""
    found = aspects_of("nyaman banget dipakai")
    assert "kualitas_produk" in found
    assert "kemudahan_penggunaan" not in found


def test_kemudahan_penggunaan_tetap_terdeteksi_saat_eksplisit():
    for text in ["mudah dipakai", "pemasangan gampang", "ribet banget settingannya"]:
        assert "kemudahan_penggunaan" in aspects_of(text), text


def test_aturan_cadangan_hanya_berlaku_saat_tidak_ada_aspek_lain():
    assert aspects_of("barangnya oke") == {"kualitas_produk"}
    assert "kualitas_produk" not in aspects_of("barang dikirim cepat")


# ---------------------------------------------------------------- bug sentimen


def test_negasi_bahasa_inggris_membalik_polaritas():
    """Tanpa "not" sebagai penanda negasi, klausa ini terbaca POSITIF — bug nyata."""
    assert sentiment_of("kualitas not oke") == "negatif"
    assert sentiment_of("not good at all") == "negatif"


def test_negasi_bahasa_indonesia_tetap_bekerja():
    assert sentiment_of("barang tidak bagus") == "negatif"
    assert sentiment_of("bukan barang jelek kok") == "positif"


def test_frasa_multi_kata_terdeteksi():
    """Pencocokan per token tidak akan pernah melihat "terima kasih" sebagai satu kesatuan."""
    assert sentiment_of("terima kasih") == "positif"
    assert sentiment_of("makasih gan") == "positif"


def test_istilah_inggris_terdeteksi():
    assert sentiment_of("working just great") == "positif"
    assert sentiment_of("item was damaged") == "negatif"


def test_klausa_tanpa_muatan_penilaian_adalah_netral():
    """Aturan cadangan: sentimen adalah properti klausa, bukan warisan rating ulasan."""
    for text in ["belum dibuka", "pesan yang warna putih", "sudah dipasang"]:
        assert sentiment_of(text) == "netral", text


# ---------------------------------------------------------------- segmentasi


def test_konjungsi_kontras_memisahkan_klausa():
    """"bagus tapi lama" harus jadi dua klausa; kalau tidak, sentimennya saling menghapus."""
    clauses = split_clauses(normalize("barangnya bagus tapi pengirimannya lama"))
    assert len(clauses) >= 2
    assert sentiment_of(clauses[0]) == "positif"
    assert sentiment_of(clauses[1]) == "negatif"
