"""Draf dari fakta dan dari listing: teks memuat seluruh nilai yang dinyatakan merchant, dan isu
yang sudah dijawab listing tidak ditahan menunggu fakta."""

from __future__ import annotations

from app.deciqo.engine import draft, triage


def _finding(ftype="missing_fact", local="ukuran kompartemen dalam", attribute="inner compartment size"):
    return {"id": "f", "finding_type": ftype, "attribute": attribute, "attribute_local": local}


def _fact(raw, value="", unit=""):
    return {"raw_value": raw, "value": value, "unit": unit, "confirmed_at": "2026-09-26T03:00:00+00:00"}


def test_tabel_ukuran_per_varian_tidak_dirangkai_jadi_satu_dimensi():
    raw = "S: lingkar dada 96 cm, panjang 68 cm; M: lingkar dada 102 cm, panjang 70 cm"
    sec = draft.section(_finding(local="tabel ukuran"), _fact(raw, "96 x 68 x 102 x 70", "cm"), "Kaos katun.", True)
    assert sec["status"] == "ready"
    assert "S: lingkar dada 96 cm" in sec["text"] and "M: lingkar dada 102 cm" in sec["text"]
    assert "96 x 68" not in sec["text"]


def test_keterangan_fakta_tidak_hilang():
    sec = draft.section(_finding(local="ukuran HP maksimal"), _fact("tebal HP maksimal 1,2 cm termasuk case", "1,2", "cm"),
                        "Holder HP motor.", True)
    assert "tebal HP maksimal 1,2 cm termasuk case" in sec["text"]


def test_semua_besaran_listrik_dipertahankan():
    sec = draft.section(_finding(local="output port USB"), _fact("port USB 9V 2,2A (20W)", "9", "v"), "Charger.", True)
    assert sec["status"] == "ready"
    assert "2,2A" in sec["text"] and "20W" in sec["text"]


def test_prefiks_yang_mengulang_label_dibuang_bila_sisanya_angka():
    sec = draft.section(_finding(), _fact("ukuran dalam 30 x 22 cm", "30 x 22", "cm"), "Tas.", True)
    assert sec["text"] == "Ukuran kompartemen dalam: 30 x 22 cm."


def test_satuan_dari_form_ikut_dirender():
    sec = draft.section(_finding(), _fact("30 x 22", "30 x 22", "cm"), "Tas.", True)
    assert sec["text"] == "Ukuran kompartemen dalam: 30 x 22 cm."


def test_listing_sudah_menyatakan_atribut_tidak_ditahan():
    check = {"status": "evidence_found", "quote": "Tahan cipratan air (IPX4), tidak untuk berenang"}
    sec = draft.section(_finding("expectation_mismatch", "ketahanan air", "water resistance"), None,
                        "Earphone. Tahan cipratan air (IPX4), tidak untuk berenang.", True, listing_check=check)
    assert sec["status"] == "ready"
    assert sec["rendered_from"] == "listing"
    assert "tidak untuk berenang" in sec["text"]


def test_listing_yang_dibantah_bukan_sumber():
    check = {"status": "conflicting", "quote": "Kapasitas 20000 mAh"}
    sec = draft.section(_finding("conflicting_fact", "kapasitas baterai", "battery capacity"), None,
                        "Powerbank. Kapasitas 20000 mAh.", True, listing_check=check)
    assert sec["status"] == "needs_merchant_fact"


def test_produk_kecil_semua_ulasan_dikirim_ke_discovery():
    triage.set_text_adapter(None)
    reviews = [{"id": str(i), "text": t, "rating": 5, "version_hash": str(i)} for i, t in enumerate(
        ["lampunya kurang terang di malam hari", "cahaya nya remang2 aja", "Mantap, suka."])]
    picked, trace = triage.candidates(reviews)
    assert {r["id"] for r in picked} == {"0", "1", "2"}
    assert trace["kept"] == 3


def test_gerbang_menolak_klaim_berisiko_tanpa_sumber():
    status, reasons, unsupported = draft.gate("Bahan kulit asli, garansi 1 tahun.", ["Tas bahan kanvas", "garansi 1 tahun"])
    assert status == "blocked" and "unsupported_claim" in reasons
    assert any("kulit asli" in u for u in unsupported)


def test_gerbang_menerima_klaim_bersumber_dengan_polaritas_sama():
    assert draft.gate("Tidak untuk berenang.", ["Tahan cipratan, tidak untuk berenang."])[0] == "ready"


def test_listing_yang_dibantah_tidak_menjadi_sumber_angka():
    check = {"status": "conflicting", "quote": "Kapasitas 20000 mAh"}
    fact = _fact("kapasitas terukur 9800 mAh", "9800", "mah")
    sec = draft.section(_finding("conflicting_fact", "kapasitas baterai", "battery capacity"), fact,
                        "Powerbank. Kapasitas 20000 mAh.", True, listing_check=check)
    assert sec["status"] == "ready" and "20000" not in sec["text"]
    assert draft.sources_for(fact, "Powerbank. Kapasitas 20000 mAh.", check) == ["kapasitas terukur 9800 mAh", "9800 mah"]
