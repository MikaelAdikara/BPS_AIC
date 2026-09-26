"""Juri relevansi: apakah kutipan asli benar-benar mendukung temuan ini. Kode, tanpa model."""

from __future__ import annotations

import pytest

from app.deciqo.engine import lexicon, relevance

SIZE = {"attribute": "inner compartment size", "attribute_local": "ukuran kompartemen dalam"}
DELIVERY = {"attribute": "delivery time", "attribute_local": "waktu pengiriman"}


@pytest.mark.parametrize("text", ["Adaptornya panas banget.", "Charger cepet panas."])
def test_overheating_matches_quality_attribute(text):
    finding = {"attribute": "overheating", "attribute_local": "suhu adaptor"}
    assert relevance.judge(text, finding).label == "supports"


@pytest.mark.parametrize("text", ["Adaptornya tidak panas.", "Charger tidak overheat."])
def test_negated_overheating_does_not_support(text):
    finding = {"attribute": "overheating", "attribute_local": "suhu adaptor"}
    assert relevance.judge(text, finding).label != "supports"


@pytest.mark.parametrize("text", ["Pesen XL dikirim L.", "Pesan merah dikirim biru."])
def test_direct_variant_swap(text):
    assert lexicon.is_wrong_item(text)
    assert relevance.judge(text, SIZE).reason == "wrong_item_routes_to_operations"


@pytest.mark.parametrize("text", ["Pesen XL dikirim XL.", "Pesan merah dikirim merah.",
                                  "Pesan kemarin dikirim hari ini.", "Pesan charger dikirim rusak."])
def test_direct_delivery_is_not_automatically_wrong_item(text):
    assert not lexicon.is_wrong_item(text)


def test_capacity_quote_is_related_without_repeating_attribute_name():
    finding = {"attribute": "capacity definition", "attribute_local": "definisi kapasitas"}
    result = relevance.judge("1,2 liter itu air atau beras?", finding)
    assert result.reason == "mentions_attribute_without_complaint"


def test_conflicting_ai_labels_can_resolve_only_with_unanimous_clause_verdicts():
    from app.deciqo.engine import pipeline
    finding = {"attribute": "capacity", "attribute_local": "kapasitas"}
    review = {"id": "r", "text": "Kapasitas tidak sesuai.", "rating": 4}
    labels = [{"review_id": "r", "quote": review["text"], "label": label}
              for label in ["supports", "contradicts"]]
    result = pipeline._judge_pairs(finding, [review], "ai", labels)
    assert set(result["supports"]) == {"r"}
    mixed = {**review, "text": "Kapasitas tidak sesuai. Kapasitas sesuai."}
    labels[1]["quote"] = "Kapasitas sesuai."
    result = pipeline._judge_pairs(finding, [mixed], "ai", labels)
    assert not result["supports"]
    assert result["uncertain"]["r"] == "labelled_both_ways"


def test_kelompok_atribut_dari_label_temuan():
    assert "size" in lexicon.attribute_groups(SIZE["attribute"], SIZE["attribute_local"])
    assert "delivery" in lexicon.attribute_groups(DELIVERY["attribute"], DELIVERY["attribute_local"])


def test_akhiran_nya_dikenali():
    assert lexicon.stem("baterainya") == "baterai"
    assert lexicon.stem("ukurannya") == "ukuran"


def test_keluhan_ukuran_mendukung():
    assert relevance.judge("Laptop 14 inch saya tidak muat, resletingnya gak bisa ditutup.", SIZE).label == "supports"


@pytest.mark.parametrize("text", [
    "Kantong dalamnya sempit, laptop harus dipaksa masuk.",
    "bajunya kegedean",
    "ukurannya kecilan dari biasanya",
    "ngga muat buat laptop saya",
])
def test_ejaan_informal_ukuran_mendukung(text):
    assert relevance.judge(text, SIZE).label == "supports"


def test_pujian_ukuran_membantah():
    assert relevance.judge("Ukurannya pas untuk laptop 13 inch saya, masuk dengan mudah.", SIZE).label == "contradicts"


def test_rating_tidak_mengubah_label():
    text = "Bahannya bagus dan jahitannya rapi, tapi agak sempit buat laptop 14 inch saya."
    assert relevance.judge(text, SIZE, rating=5).label == relevance.judge(text, SIZE, rating=1).label == "supports"
    praise = "Ukuran sesuai, pas dibawa ke kantor."
    assert relevance.judge(praise, SIZE, rating=3).label == relevance.judge(praise, SIZE, rating=5).label


def test_keluhan_yang_dinegasikan_bukan_keluhan():
    assert relevance.judge("Tidak kekecilan kok, pas.", SIZE).label == "contradicts"


def test_pujian_yang_dinegasikan_adalah_keluhan():
    assert relevance.judge("Ukurannya tidak sesuai tabel.", SIZE).label == "supports"


def test_keluhan_topik_lain_tidak_dihitung():
    verdict = relevance.judge("Pengiriman lama sekali, hampir dua minggu.", SIZE)
    assert verdict.label in {"unrelated", "uncertain"}
    assert relevance.judge("Pengiriman lama sekali, hampir dua minggu.", DELIVERY).label == "supports"


def test_salah_kirim_bukan_bukti_ukuran():
    verdict = relevance.judge("Pesan ukuran L yang datang malah M, kecewa.", SIZE)
    assert verdict.label == "unrelated"
    assert verdict.reason == "wrong_item_routes_to_operations"


def test_salah_kirim_plus_keluhan_ukuran_tidak_jelas():
    verdict = relevance.judge("Pesan L dikasih M, dan M nya pun kekecilan di dada.", SIZE)
    assert verdict.label == "uncertain"
    assert verdict.reason == "also_reports_wrong_variant"


def test_pujian_umum_tidak_mendukung_apa_pun():
    assert relevance.judge("Bagus, sesuai deskripsi.", SIZE).label in {"unrelated", "uncertain"}


def test_klausa_keluhan_ditemukan_verbatim():
    text = "Bahannya bagus dan jahitannya rapi, tapi agak sempit buat laptop 14 inch saya."
    verdict = relevance.judge(text, SIZE)
    assert verdict.clause and verdict.clause in text
