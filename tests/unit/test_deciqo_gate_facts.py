"""Validasi jawaban fakta merchant: string tidak kosong bukan fakta.

Kalimat di sini ditulis sendiri (bukan salinan probe eval) supaya probe eval tetap menjadi alat ukur.
"""

from __future__ import annotations

import pytest

from app.deciqo.engine import facts
from app.deciqo.errors import DeciqoError

INNER = {"id": "f1", "product_id": "p", "attribute": "inner pocket size", "attribute_local": "ukuran saku dalam",
         "finding_type": "missing_fact", "merchant_question": "Berapa ukuran saku bagian dalam (panjang x lebar, cm)?"}
FOLDED = {"id": "f2", "product_id": "p", "attribute": "folded size", "attribute_local": "ukuran saat dilipat",
          "finding_type": "missing_fact", "merchant_question": "Berapa ukuran meja saat dilipat (cm)?"}
PHONE = {"id": "f3", "product_id": "p", "attribute": "supported phone models", "attribute_local": "HP yang didukung",
         "finding_type": "missing_fact", "merchant_question": "HP tipe apa saja yang pas dengan holder ini?"}
BATTERY = {"id": "f4", "product_id": "p", "attribute": "battery capacity", "attribute_local": "kapasitas baterai",
           "finding_type": "conflicting_fact", "merchant_question": "Berapa kapasitas baterai sebenarnya (mAh)?"}
MATERIAL = {"id": "f5", "product_id": "p", "attribute": "strap material", "attribute_local": "bahan tali",
            "finding_type": "missing_fact", "merchant_question": "Tali tas terbuat dari bahan apa?"}


def _code(finding, raw, unit=""):
    with pytest.raises(DeciqoError) as info:
        facts.validate(finding, raw, unit)
    return info.value.code


@pytest.mark.parametrize("raw", ["iya", "siap kak", "ok gan", "udah dicek", "ga tau", "kira kira segitu", "  "])
def test_konfirmasi_bukan_fakta(raw):
    assert _code(INNER, raw) == "not_a_fact"


def test_angka_tanpa_satuan_ditolak():
    assert _code(INNER, "30 x 20") == "unit_missing"
    assert _code(BATTERY, "10000") == "unit_missing"


def test_satuan_dari_pilihan_form_melengkapi_angka():
    parsed = facts.validate(INNER, "30 x 20", "cm")
    assert parsed["value"] == "30 x 20" and parsed["unit"] == "cm"


def test_pertanyaan_ukuran_tanpa_angka_ditolak():
    assert _code(INNER, "cukup besar untuk laptop") == "measurement_missing"


def test_nomor_model_bukan_pengukuran():
    assert _code(INNER, "muat iPhone 13") == "measurement_missing"


def test_lokasi_berbeda_ditolak():
    assert _code(INNER, "bagian luar 40 x 30 cm") == "wrong_location"
    assert _code(FOLDED, "saat dibuka 60 x 40 cm") == "wrong_location"


def test_jawaban_valid_diterima():
    assert facts.validate(INNER, "bagian dalam 30 x 20 x 4 cm")["location"] == "inner"
    assert facts.validate(FOLDED, "15 x 60 cm")["unit"] == "cm"
    assert facts.validate(BATTERY, "9.800 mAh")["unit"] == "mah"


def test_kompatibilitas_menerima_nomor_model():
    assert facts.validate(PHONE, "Samsung A54, Redmi Note 12")["raw_value"] == "Samsung A54, Redmi Note 12"
    assert _code(PHONE, "sip") == "not_a_fact"


def test_pertanyaan_non_ukuran_menerima_kata():
    assert facts.validate(MATERIAL, "nylon 600D")["raw_value"] == "nylon 600D"
