"""Gerbang v2: konversi satuan, lokasi/sumbu/varian, dan klaim non-angka berpolaritas."""

from __future__ import annotations

import pytest

from app.deciqo.engine import verify


def bad(draft: str, *sources: str) -> list[str]:
    return [q.text for q in verify.unsupported_quantities(draft, list(sources))]


# --- satuan -----------------------------------------------------------------------------------


def test_14_inch_bukan_14_cm():
    assert bad("Muat laptop 14 cm.", "Muat laptop hingga 14 inch") == ["14 cm"]


def test_14_inch_sama_dengan_35_56_cm():
    assert bad("Muat laptop hingga 35,56 cm.", "Muat laptop hingga 14 inch") == []


@pytest.mark.parametrize("draft, source", [("Berat 1500 g.", "berat 1,5 kg"), ("Isi 750 ml.", "kapasitas 0,75 liter"),
                                           ("Panjang 120 mm.", "panjang 12 cm")])
def test_konversi_dalam_satu_dimensi(draft, source):
    assert bad(draft, source) == []


def test_dimensi_listrik_tidak_saling_menggantikan():
    assert bad("Output 20 W.", "output 20 V") == ["20 w"]
    assert bad("Kapasitas 5000 mAh.", "baterai 5000 Wh") == ["5000 mah"]


def test_bulan_dan_tahun_dengan_konversi():
    assert bad("Garansi 12 bulan.", "garansi 1 tahun") == []
    assert bad("Garansi 12 tahun.", "garansi 12 bulan") == ["12 year"]


# --- lokasi, sumbu, varian ----------------------------------------------------------------------


def test_ukuran_luar_tidak_mendukung_ukuran_dalam():
    assert bad("Ukuran bagian dalam 32 cm.", "Ukuran bagian luar 32 x 24 cm") == ["32 cm"]


def test_tanpa_penanda_tidak_konflik():
    assert bad("Panjang 32 cm.", "32 x 24 cm") == []


def test_sumbu_berbeda_ditolak():
    assert bad("Lebar 24 cm.", "panjang 24 cm, tinggi 10 cm") == ["24 cm"]


def test_varian_ukuran_berbeda_ditolak():
    assert bad("Lingkar dada ukuran M 100 cm.", "L: lingkar dada 100 cm; M: lingkar dada 96 cm") == ["100 cm"]
    assert bad("Lingkar dada ukuran M 96 cm.", "L: lingkar dada 100 cm; M: lingkar dada 96 cm") == []


# --- klaim non-angka ---------------------------------------------------------------------------


def claims(draft: str, *sources: str) -> list[str]:
    return [c.kind for c in verify.unsupported_claims(draft, list(sources))]


def test_tidak_tahan_air_tidak_mendukung_tahan_air():
    assert claims("Tas ini tahan air.", "Tas ini tidak tahan air.") == ["water_resistant"]
    assert claims("Tas ini tidak tahan air.", "Bahan tidak tahan air, hindari hujan.") == []


def test_waterproof_menutupi_water_resistant_tapi_tidak_sebaliknya():
    assert claims("Casing tahan air.", "Casing waterproof hingga 1 meter") == []
    assert claims("Casing waterproof.", "Casing tahan cipratan air") == ["waterproof"]


def test_kompatibilitas_harus_perangkat_yang_sama():
    assert claims("Kompatibel dengan iPhone 15.", "Kompatibel dengan iPhone 12 dan iPhone 13") == ["compatibility"]
    assert claims("Cocok untuk iPhone 13.", "Kompatibel dengan iPhone 12 dan iPhone 13") == []


@pytest.mark.parametrize("draft, kind", [("Bahan kulit asli.", "genuine_leather"), ("Garansi resmi toko.", "warranty"),
                                         ("Produk original.", "authenticity"), ("Sudah BPOM.", "certification"),
                                         ("Aman untuk anak, BPA free.", "safety"), ("Bahan kanvas tebal.", "material")])
def test_klaim_berisiko_tanpa_sumber_ditolak(draft, kind):
    assert kind in claims(draft, "Tas harian warna hitam.")


def test_klaim_bersumber_diterima():
    assert claims("Bahan kanvas.", "Tas bahan kanvas tebal") == []
