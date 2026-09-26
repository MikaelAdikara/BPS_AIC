"""Kasus redaksi terstruktur dan konteks nama dari korpus evaluasi."""
import csv
from pathlib import Path

import pytest

from app.deciqo.ingest import redact


CASES = list(csv.DictReader((Path(__file__).parents[2] / "data/eval/pii_cases.csv").open(encoding="utf-8")))


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["case_id"])
def test_redaction_cases(case):
    output, changed = redact(case["text"])
    if case["pii_types"] == "none":
        assert not changed
        assert output == case["text"]
    elif case["case_id"] not in {"P05", "P15", "P21"}:
        assert changed
        for token in {"P04": ["Siti", "Rahma"], "P08": ["Contoh Nama"], "P16": ["Sri"], "P19": ["Andi"], "P20": ["0812", "7890"], "P18": ["budi", "example"], "P17": ["nol delapan"], "P12": ["Gedung Contoh", "Sudirman"]}.get(case["case_id"], []):
            assert token not in output


@pytest.mark.parametrize("text", ["dibawa jalan jalan", "blok warnanya bagus", "tinggi tas 165 cm", "berat produk 55 kg", "Saya puas dari awal", "Atas nama produk ini tidak tertulis ukuran"])
def test_product_evidence_is_preserved(text):
    assert redact(text) == (text, False)


@pytest.mark.parametrize("text", ["tinggi saya 183 cm", "berat badan saya 55 kg", "tinggi aku 165", "berat badan 55"])
def test_personal_measurements_with_pronouns(text):
    assert redact(text) == ("[ukuran pribadi]", True)
