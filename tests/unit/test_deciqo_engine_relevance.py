"""Juri relevansi: apakah kutipan asli benar-benar mendukung temuan ini. Kode, tanpa model."""

from __future__ import annotations

import pytest

from app.deciqo.engine import lexicon, relevance

SIZE = {"attribute": "inner compartment size", "attribute_local": "ukuran kompartemen dalam"}
DELIVERY = {"attribute": "delivery time", "attribute_local": "waktu pengiriman"}


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
