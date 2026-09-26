"""gap-v1.18: pengelompokan antar-temuan dan satu klausa satu temuan.

Kasus diambil dari audit data Lazada nyata di checkpoint 3 §5: "Poto nya beda" masuk ke temuan ukuran
tas, keluhan voucher/refund tergabung ke temuan kurir, dan klausa yang sama ("sampai 11 jam tak
kunjung full") terhitung di dua temuan sekaligus.
"""

from __future__ import annotations

import pytest

from app.deciqo.engine import pipeline

SIZE = {"attribute": "product dimensions / perceived size", "attribute_local": "dimensi produk / ukuran yang terlihat",
        "finding_type": "missing_fact"}
COURIER = {"attribute": "courier service / delivery handling", "attribute_local": "layanan kurir / penanganan pengiriman",
           "finding_type": "operational"}
HDMI = {"attribute": "HDMI refresh rate at 4K", "attribute_local": "refresh rate HDMI 4K", "finding_type": "missing_fact"}


def test_dispute_quote_about_another_attribute_is_vetoed():
    ok, reason = pipeline._second_read_accepts("dispute", "tidak sesuai dengan gambar", "tidak sesuai dengan gambar", SIZE)
    assert not ok and reason == "quote_about_other_attribute"


def test_orphan_photo_complaint_is_not_size_evidence():
    ok, _ = pipeline._second_read_accepts("orphan", "Poto nya beda", "Poto nya beda", SIZE)
    assert not ok


def test_voucher_refund_complaint_is_not_courier_evidence():
    text = "iya uangnya diganti, tapi koin sama voucer nya mh ngga .."
    ok, _ = pipeline._second_read_accepts("orphan", text, "iya uangnya diganti, tapi koin sama voucer nya mh ngga", COURIER)
    assert not ok


def test_refund_attribute_routes_to_operations():
    proposal = {"attribute": "refund / voucher compensation", "attribute_local": "pengembalian dana / voucher",
                "finding_type": "missing_fact"}
    assert pipeline.code_route(proposal)["finding_type"] == "operational"


def test_unknown_vocabulary_without_other_attribute_is_still_accepted():
    # Kehilangan recall yang ditemukan holdout kedua: kosakata yang tidak dikenal leksikon.
    text = "kirain 4K 60 ternyata mentok 30, harusnya ditulis di deskripsi"
    ok, _ = pipeline._second_read_accepts("dispute", text, "kirain 4K 60 ternyata mentok 30", HDMI)
    assert ok


def _entry(proposal, supports):
    return {"proposal": proposal,
            "judged": {"supports": {rid: {"quote": q} for rid, q in supports.items()}, "contradicting": {},
                       "uncertain": {}, "rejected": {}, "wrong_item": set()}}


def _counted(built):
    return {k: set(e["judged"]["supports"]) - set(e["judged"]["uncertain"]) for k, e in built.items()}


FAST = {"attribute": "fast charging / output current", "attribute_local": "pengisian cepat / arus output",
        "finding_type": "missing_fact"}
INPUT = {"attribute": "charging input compatibility / required charger",
         "attribute_local": "kompatibilitas input pengisian / charger yang diperlukan", "finding_type": "missing_fact"}
MATERIAL = {"attribute": "material quality (spunbond)", "attribute_local": "kualitas bahan (spunbond)",
            "finding_type": "product_quality"}
SERVICE = {"attribute": "seller response speed / customer service",
           "attribute_local": "kecepatan respon penjual / layanan pelanggan", "finding_type": "operational"}
FIT = {"attribute": "usable inner size / fit", "attribute_local": "ukuran dalam yang dapat digunakan / kecocokan",
       "finding_type": "missing_fact"}


def test_same_clause_is_counted_in_one_finding_only():
    text = "sampai 11 jam tak kunjung full"
    reviews = [{"id": "x", "text": text}, {"id": "y", "text": "gak fast charging ya"},
               {"id": "z", "text": "Ternyata tidak fast charging, beda sama klaimnya."}]
    built = {"fast": _entry(FAST, {"x": text, "y": "gak fast charging ya", "z": "Ternyata tidak fast charging"}),
             "input": _entry(INPUT, {"x": text})}
    moved = pipeline.exclusive_clauses(built, reviews)
    counted = _counted(built)
    assert moved == 1
    assert ("x" in counted["fast"]) != ("x" in counted["input"])
    loser = "input" if "x" in counted["fast"] else "fast"
    assert built[loser]["judged"]["uncertain"]["x"] == "clause_counted_in_other_finding"


def test_clause_goes_to_the_finding_it_names():
    text = "sesuai harga. lumayan agak tipis, seller respon lambat"
    reviews = [{"id": "s", "text": text}, {"id": "t", "text": "bahannya tipis"}, {"id": "u", "text": "bahan jelek"}]
    # Seluruh ulasan dikutip untuk dua temuan: masing-masing mendapat klausanya sendiri.
    built = {"material": _entry(MATERIAL, {"s": text, "t": "bahannya tipis", "u": "bahan jelek"}),
             "service": _entry(SERVICE, {"s": text})}
    moved = pipeline.exclusive_clauses(built, reviews)
    counted = _counted(built)
    assert moved == 0
    assert "s" in counted["material"] and "s" in counted["service"]
    assert built["service"]["judged"]["supports"]["s"]["quote"] == "seller respon lambat"
    assert built["material"]["judged"]["supports"]["s"]["quote"] == "lumayan agak tipis"


def test_two_problems_in_one_review_stay_in_both_findings():
    text = "lumayan lah. bahannya sedikit kasar. ukuran 14inc msih kegedean tasnya"
    reviews = [{"id": "k", "text": text}]
    built = {"material": _entry(MATERIAL, {"k": "bahannya sedikit kasar."}),
             "fit": _entry(FIT, {"k": "ukuran 14inc msih kegedean tasnya"})}
    assert pipeline.exclusive_clauses(built, reviews) == 0
    counted = _counted(built)
    assert "k" in counted["material"] and "k" in counted["fit"]


EARBUD = {"attribute": "earbud left/right not both working", "attribute_local": "earbud kiri/kanan tidak keduanya berfungsi",
          "finding_type": "product_quality"}


def test_attribute_outside_the_lexicon_is_not_vetoed():
    # "nyala" masuk kosakata baterai, tetapi atribut earbud tidak dikenal leksikon: kode tidak tahu apa yang "lain".
    text = "SebeLah NyaLa SebeLah Lagi Ga NyaLa"
    ok, _ = pipeline._second_read_accepts("dispute", text, text, EARBUD)
    assert ok


def test_quote_is_never_widened_to_another_clause():
    text = "tapi gak bisa di pakai karena desain gk sesuai kekecilan di badan, kain tipis"
    thick = {"attribute": "fabric thickness", "attribute_local": "ketebalan kain / nerawang", "finding_type": "product_quality"}
    reviews = [{"id": "w", "text": text}]
    built = {"thick": _entry(thick, {"w": "kain tipis"}), "fit": _entry(FIT, {"w": "kain tipis"})}
    pipeline.exclusive_clauses(built, reviews)
    quotes = {e["judged"]["supports"].get("w", {}).get("quote") for e in built.values()} - {None}
    assert quotes == {"kain tipis"}


def test_template_review_is_vetoed_only_by_the_quoted_words():
    text = "🎨Desain:cakep 🔋Kapasitas:lumayan Gak Pas Sama Laptop Saya"
    ok, _ = pipeline._second_read_accepts("dispute", text, "Gak Pas Sama Laptop Saya", FIT)
    assert ok


def test_whole_review_quote_is_split_between_sleeve_and_fabric():
    text = "lengennya kurang panjang, kain nya tipis bgt kecewa"
    sleeve = {"attribute": "sleeve length", "attribute_local": "panjang lengan", "finding_type": "missing_fact"}
    thick = {"attribute": "fabric thickness", "attribute_local": "ketebalan kain / nerawang", "finding_type": "product_quality"}
    built = {"sleeve": _entry(sleeve, {"v": text}), "thick": _entry(thick, {"v": text, "o": "kain tipis"})}
    assert pipeline.exclusive_clauses(built, [{"id": "v", "text": text}]) == 0
    assert built["sleeve"]["judged"]["supports"]["v"]["quote"].startswith("lengennya kurang panjang")
    assert built["thick"]["judged"]["supports"]["v"]["quote"].startswith("kain nya tipis")


# rc-v1.18: veto berbasis semua kelompok leksikon membuang bukti emas karena kelompoknya terlalu kasar
# ("nyala" = baterai, "air" = tahan air). Hanya keluhan foto/gambar dan kompensasi yang diveto.
@pytest.mark.parametrize(("text", "attribute", "local"), [
    ("kecemplung ember bentar udah ga nyala lagi", "water resistance / IPX rating", "ketahanan air / IPX"),
    ("kirain bisa buat ipad air terbaru, ternyata ga masuk", "model compatibility", "kompatibilitas model"),
    ("yang kanan mati setelah 2 minggu", "earbud durability / longevity", "ketahanan earbud"),
])
def test_coarse_lexicon_groups_do_not_veto_gold_evidence(text, attribute, local):
    proposal = {"attribute": attribute, "attribute_local": local, "finding_type": "missing_fact"}
    ok, _ = pipeline._second_read_accepts("dispute", text, text, proposal)
    assert ok
