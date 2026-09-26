"""Pemeriksaan listing: status eksplisit dan cakupan, termasuk listing yang lebih panjang dari
jendela baca model."""

from __future__ import annotations

from app.deciqo.engine import listing_check

SIZE = {"attribute": "inner pocket size", "attribute_local": "ukuran saku dalam", "finding_type": "missing_fact",
        "listing_evidence": ""}


def test_teks_terkait_di_luar_jendela_model_berstatus_incomplete_source():
    filler = "Ransel harian warna hitam, cocok untuk kerja. " * 220  # > 9.000 karakter tanpa kata ukuran
    listing = filler + "Detail: saku dalam berukuran 26 x 18 cm."
    check = listing_check.check(SIZE, listing, True)
    assert check["status"] == "incomplete_source"
    assert any("26 x 18 cm" in r for r in check["related"])
    assert check["coverage"]["chars_checked"] == len(listing)
    assert check["coverage"]["model_chars"] == listing_check.LISTING_LIMIT


def test_listing_pendek_tanpa_kata_atribut_tidak_ditemukan():
    check = listing_check.check(SIZE, "Ransel warna hitam, bahan polyester.", True)
    assert check["status"] == "not_found_in_checked_content"


def test_listing_belum_ada():
    assert listing_check.check(SIZE, "", False)["status"] == "not_provided"
