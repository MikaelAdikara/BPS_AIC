"""Gerbang fakta dan verifier kutipan: fungsi murni, tanpa basis data."""

from __future__ import annotations

from app.deciqo.engine import verify


# --- normalisasi & kutipan ----------------------------------------------------------------


def test_normalisasi_menyamakan_huruf_spasi_dan_tanda_kutip():
    assert verify.normalise("  Laptop “14”   INCH\n") == 'laptop "14" inch'


def test_kutipan_persis_diterima_walau_beda_huruf_dan_spasi():
    source = "Laptop 14 inch saya tidak muat, resletingnya gak bisa ditutup rapat."
    assert verify.quote_in("laptop 14 inch  saya TIDAK muat", source)


def test_kutipan_boleh_tanpa_tanda_baca_lunak():
    source = "Laptop 14 inch saya tidak muat, resletingnya gak bisa ditutup rapat."
    assert verify.quote_in("tidak muat resletingnya gak bisa", source)


def test_kutipan_yang_menambah_negasi_ditolak():
    source = "Ukurannya pas untuk laptop 13 inch saya, masuk dengan mudah."
    assert not verify.quote_in("tidak masuk dengan mudah", source)


def test_kutipan_parafrasa_ditolak_tanpa_fuzzy():
    source = "Kantong dalamnya sempit, laptop 14 inci harus dipaksa masuk."
    assert not verify.quote_in("kantong dalam sempit sekali", source)


def test_kutipan_terlalu_pendek_ditolak():
    assert not verify.quote_in("muat", "Laptop tidak muat")


def test_pemisah_desimal_tidak_diabaikan():
    source = "Tebal 1,5 cm dan lebar 30 cm"
    assert verify.quote_in("tebal 1,5 cm", source)
    assert not verify.quote_in("tebal 15 cm", source)


def test_check_quote_memberi_alasan_penolakan():
    ok, reason = verify.check_quote("tidak ada di sana sama sekali", "teks ulasan lain")
    assert not ok and reason == "quote_not_verbatim"
    ok, reason = verify.check_quote("abc", "abc def")
    assert not ok and reason == "quote_too_short"


# --- kuantitas ------------------------------------------------------------------------------


def test_ekstraksi_angka_bersatuan_dimensi_dan_desimal():
    found = verify.extract_quantities("Ukuran 32 x 24 x 3 cm, berat 1,2 kg, baterai 20.000 mAh")
    pairs = [(q.value, q.unit) for q in found]
    assert (32.0, "cm") in pairs and (24.0, "cm") in pairs and (3.0, "cm") in pairs
    assert (1.2, "kg") in pairs
    assert (20000.0, "mah") in pairs


def test_ekstraksi_format_tabel_satuan_dalam_kurung():
    pairs = [(q.value, q.unit) for q in verify.extract_quantities("Panjang (cm): 32")]
    assert pairs == [(32.0, "cm")]


def test_angka_tanpa_satuan_tidak_dianggap_kuantitas():
    assert verify.extract_quantities("Bintang 5, beli 2 kali") == []


def test_kuantitas_draf_yang_ada_di_sumber_diterima():
    assert verify.unsupported_quantities("Ukuran dalam: 32 x 24 cm.", ["ukuran dalam 32 x 24 cm"]) == []


def test_kuantitas_draf_yang_tidak_ada_di_sumber_ditolak():
    bad = verify.unsupported_quantities("Ukuran dalam: 34 x 24 cm.", ["ukuran dalam 32 x 24 cm"])
    assert [q.text for q in bad] == ["34 cm"]


def test_angka_sama_satuan_beda_ditolak():
    # "14 inch" di sumber tidak pernah mendukung "14 cm" di draf.
    bad = verify.unsupported_quantities("Muat laptop 14 cm.", ["Muat laptop hingga 14 inch"])
    assert len(bad) == 1


def test_placeholder_terdeteksi():
    assert verify.placeholders("Ukuran dalam: [[ukuran dalam]] cm") == ["[[ukuran dalam]]"]
    assert verify.placeholders("Ukuran dalam: 32 cm") == []
