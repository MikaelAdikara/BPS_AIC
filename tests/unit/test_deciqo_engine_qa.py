"""Regresi dari QA engine atas ulasan marketplace nyata (snapshot Lazada di data/marketplace).

Setiap kasus di sini diambil dari ulasan yang benar-benar salah dinilai. Teks disalin dari
snapshot (atau dipersingkat tanpa mengubah kata kunci). Kasus yang belum diperbaiki ditandai
`xfail(strict=True)`: begitu perbaikannya masuk, tes akan lulus tak terduga dan penandanya wajib
dilepas, sehingga daftar ini selalu jujur tentang apa yang masih gagal.
"""

from __future__ import annotations

import pytest

from app.deciqo.engine import lexicon, relevance, rules

QUALITY = {"attribute": "product quality", "attribute_local": "kualitas produk"}
STITCHING = {"attribute": "stitching quality", "attribute_local": "kualitas jahitan"}
DELIVERY = {"attribute": "delivery time", "attribute_local": "waktu pengiriman"}
SIZE = {"attribute": "product size", "attribute_local": "ukuran produk"}
BATTERY = {"attribute": "battery life", "attribute_local": "daya tahan baterai"}
WRONG = {"attribute": "wrong variant sent", "attribute_local": "varian yang dikirim salah"}

open_issue = pytest.mark.xfail(strict=True, reason="QA: belum diperbaiki")


# --- pujian terbaca sebagai keluhan ------------------------------------------------------------


@pytest.mark.parametrize("text", ["Tahan lama dan awet", "Konstruksi yang tahan lama dan kokoh"])
def test_qa01_tahan_lama_adalah_pujian(text):
    assert relevance.judge(text, QUALITY).label != relevance.SUPPORTS


def test_qa01_daya_tahan_baterai_lama_adalah_pujian():
    assert relevance.judge("Daya Tahan Baterai:Daya tahan baterai yang lama", BATTERY).label != relevance.SUPPORTS


# --- salah kirim ------------------------------------------------------------------------------


@pytest.mark.parametrize("text", [
    "terimakasih pesanan udah sampai",
    "Alhamdulillah pesanannya sudah sampai",
    "Terima kasih pesanan telah sampai",
    "ALHAMDULILLAH SUDAH SAMPAI DENGAN SELAMAT SESUAI PESANAN KEREN, SEKARANG CEKOUT BESOK NYA SAMPAI",
    "Mantraaap sesuai pesanan, produk presisi semoga awet sampai Kakek Nenek...",
    "pesanan sudah sampai pengiriman ke pulau sulawesi hanya 5 Hari",
])
def test_qa02_pesanan_sampai_bukan_salah_kirim(text):
    assert not lexicon.is_wrong_item(text)


def test_qa02_barang_rusak_dikirim_bukan_salah_kirim():
    assert not lexicon.is_wrong_item("kecewa udah beli mahal mahal malah dikirim barang rusak")


@pytest.mark.parametrize("text", [
    "PESAN WARNA BIRU DIKASIH HITAM TANPA KONFIRMASI PULA",
    "order 13pro mlh dikirim yg 13 biasa",
    "saya pesan nya BLACK yang datang NAVY",
    "pesan e 38 kenapa datang 39",
    "Salah kirim",
])
def test_qa02_salah_kirim_nyata_tetap_terdeteksi(text):
    assert lexicon.is_wrong_item(text)


# --- kata umum terbaca sebagai atribut ukuran ------------------------------------------------


@pytest.mark.parametrize("text", [
    "sayangnya eggk hidup satu handset 'y eggk masuk di cas 🔋Daya Tahan Baterai:Daya tahan baterai yang lama",
    "Kapasitas besar untuk penggunaan yang lebih lama",
    "cuman yang R nih longgar pas pengisian nya",
])
def test_qa03_bukan_keluhan_ukuran(text):
    assert relevance.judge(text, SIZE).label != relevance.SUPPORTS


# --- keluhan kualitas yang menyebut "dikirim" -------------------------------------------------


@pytest.mark.parametrize("text", [
    "KLw Memang Rusak Jngn Dikirim Dong",
    "barang cacat dikirim aowkwkwkwkwkekkekeke",
    "ada yang cacat harusnya di qc dulu sebelum dikirim",
])
def test_qa04_cacat_yang_dikirim_bukan_keluhan_pengiriman(text):
    assert relevance.judge(text, DELIVERY).label != relevance.SUPPORTS


def test_qa04_keluhan_pengiriman_nyata_tetap_mendukung():
    assert relevance.judge("pengiriman lama", DELIVERY).label == relevance.SUPPORTS
    assert relevance.judge("9hari nungguin pas dateng paket nye cacat", DELIVERY).label != relevance.CONTRADICTS


# --- ulasan berformat templat Lazada ("Label:isi" + emoji) ---------------------------------


def test_qa05_templat_lazada_dipecah_per_label():
    text = "🎧Kualitas Suara:sangat jernih bagus 🎧Kenyamanan:nyaman sekali 🔋Daya Tahan Baterai:cukup lama"
    assert len(lexicon.clauses(text)) >= 3


# --- ejaan negasi informal ---------------------------------------------------------------------


@pytest.mark.parametrize("text", ["barang tida sesuay ukurannya", "ukurannya GX sesuai", "ukuran eggk sesuai"])
def test_qa06_negasi_informal(text):
    assert relevance.judge(text, SIZE).label == relevance.SUPPORTS


# --- analyser aturan ---------------------------------------------------------------------------


def test_qa07_jahitan_tidak_menyalin_bukti_kualitas_umum():
    text = "jangan mau beli di toko ini barang tida sesuay dan cepat rusak baru 1 hari"
    assert relevance.judge(text, STITCHING).label != relevance.SUPPORTS


def test_qa08_soft_case_laptop_dikenali_sebagai_tas():
    assert rules.product_kind('Soft Case Laptop 14" ASUS. LENOVO. HP. ACER') == "bag"


def test_qa09_kata_depan_terpisah_tetap_salah_kirim():
    assert lexicon.is_wrong_item('order magnetic malah di kirim polos bening kecewa bat ga amanah')


def test_qa09_mengisi_daya_bukan_keluhan_pengiriman():
    text = "Saya pakai baru berapa hari doang dicas sampai 6 -7 jam malah pas dipakai gak sampai 5 menit"
    assert relevance.judge(text, DELIVERY).label != relevance.SUPPORTS


# --- label AI dinilai pada klausa yang dikutip, bukan seluruh ulasan ------------------------

CAPACITY = {"attribute": "battery capacity (mAh)", "attribute_local": "kapasitas baterai"}


def test_qa10_pujian_di_klausa_lain_tidak_membatalkan_keluhan_yang_dikutip():
    text = ("quick charge nya berfungsi dengan baik, dipakai untuk charge Redmi Note 10s dengan kapasitas "
            "baterai 5000mah dari 37% sampai 100%, jadi sepertinya baterai tidak real 20.000mah")
    verdict = relevance.judge_span(text, "jadi sepertinya baterai tidak real 20.000mah", CAPACITY)
    assert verdict.label == relevance.SUPPORTS


def test_qa10_negasi_di_luar_kutipan_tetap_terbaca():
    # Kutipan yang memotong negasi tidak boleh mengubah makna: klausa utuh yang dinilai.
    verdict = relevance.judge_span("Ukurannya tidak kekecilan kok, pas.", "kekecilan kok", SIZE)
    assert verdict.label != relevance.SUPPORTS


@pytest.mark.parametrize("text", [
    "baru datang aja udh kembung sebelah",
    "batrai nya mudah bengkak dan gembung setelah beberapa kali di cas",
    "ngisi 1 hp ajah ga penuh , powerbank nya cepat lobet",
    "tp untuk super fast charging gk bsa",
])
def test_qa11_keluhan_baterai_elektronik(text):
    assert relevance.judge(text, BATTERY).label == relevance.SUPPORTS


@pytest.mark.parametrize("text", [
    "tidak sesuai pesanan.....tokonya kurang rekomendate",
    "merek tidak sesuai",
    "di deskripsi mizuno dusnya juga mizuno isinya nike kocak",
    "Barang tidak sesuai yang dipesan, merk nya saja sudah beda.",
])
def test_qa12_tidak_sesuai_pesanan_adalah_salah_kirim(text):
    assert lexicon.is_wrong_item(text)


def test_qa12_sesuai_pesanan_bukan_salah_kirim():
    assert not lexicon.is_wrong_item("Barang sampai sesuai pesanan.. barang bagus sesuai harga.")


# --- paket Tokopedia 2019 / Shopee (tanpa listing, ulasan tanpa tanggal) ------------------------


def test_qa13_negasi_frasa_cepat_rusak_adalah_pujian():
    text = "Produk bekerja dengan baik, tidak cepat rusak walau sudah dipakai berkali-kali"
    assert relevance.judge(text, QUALITY).label != relevance.SUPPORTS


def test_qa13_tidak_cepat_tetap_keluhan_pengiriman():
    assert relevance.judge("pengirimannya tidak cepat", DELIVERY).label == relevance.SUPPORTS


def test_qa14_dua_kali_lipat_bukan_ukuran():
    assert relevance.judge("harga beda 2x lipat dgn yg asli", SIZE).label != relevance.SUPPORTS


@pytest.mark.parametrize("text", ["Barangnya pecah ketika sampai", "waktu sampai barang nya patah"])
def test_qa15_barang_pecah_saat_sampai_adalah_kualitas(text):
    assert relevance.judge(text, DELIVERY).label != relevance.SUPPORTS
    assert relevance.judge(text, QUALITY).label == relevance.SUPPORTS


def test_qa16_tp_memisah_klausa():
    text = "Sesuai dgn yg di gambar tp qo kurir'a lama ya kirim'a"
    appearance = {"attribute": "appearance versus photos", "attribute_local": "kesesuaian dengan foto"}
    assert relevance.judge(text, appearance).label != relevance.SUPPORTS


def test_qa17_tanpa_listing_draf_menunggu_listing():
    from app.deciqo.engine import draft

    finding = {"id": "f", "finding_type": "missing_fact", "attribute": "size", "attribute_local": "ukuran"}
    assert draft.section(finding, None, "", False)["status"] == "needs_listing"


# --- label AI yang benar tapi ditolak juri (paket Shopee/Tokopedia) -----------------------------

DEFECT = {"attribute": "damaged / holes / tears", "attribute_local": "barang rusak / bolong / robek"}
FAN = {"attribute": "fan rotation speed", "attribute_local": "kecepatan/rotasi kipas"}


@pytest.mark.parametrize("text", [
    "Kecewa baju nya bolong",  # sudah lulus sejak pecah/patah/retak/bolong masuk kelompok kualitas
    "Bahan:bagus tapi koyak",
    "barang nya robek tdk sesuai",
    "ada noda putih2 di baju",
])
def test_qa18_kata_cacat_di_label_temuan_menandai_atribut(text):
    assert relevance.judge(text, DEFECT).label == relevance.SUPPORTS


def test_qa18_kata_label_temuan_tanpa_kelompok_dipakai():
    assert relevance.judge("kipas muternya lambat", FAN).label == relevance.SUPPORTS


@pytest.mark.parametrize("text", [
    "pesen warna putih, yang dateng malah hitam.",
    "akuu mesennyaa warnaa maroon, tapi dikirimnya warna coklat",
    "Jelek bngt pesan warna lain yg dtng warna lain",
    "jelek njs psen Mahogany yg dtg item",
])
def test_qa19_ejaan_pesan_dan_akhiran_nya_salah_kirim(text):
    assert lexicon.is_wrong_item(text)


@pytest.mark.parametrize("text", [
    "Lapisan anti lengketnya mulai mengelupas setelah sebulan pemakaian.",
    "Anti lengketnya sudah baret padahal pakai centong bawaan.",
    "Kapasitas 1,8 liter itu air atau beras? Masak beras 1,5 liter jadi luber.",
    "Pakai case tebal jadi tidak nempel sama sekali, harusnya ditulis butuh case magsafe.",
])
def test_qa20_triage_menangkap_keluhan_dan_pertanyaan_spesifikasi(text):
    from app.deciqo.engine import triage

    triage.set_text_adapter(None)
    [picked], _ = triage.candidates([{"id": "a", "text": text, "rating": 5, "version_hash": "v"}])
    assert picked["id"] == "a"


def test_qa21_merek_lain_sebagai_pembanding_bukan_salah_kirim():
    assert not lexicon.is_wrong_item("sudah beberapa kali sy order PB merk lain, & baru kali ini sy menemukan PB yg cepat")
    assert lexicon.is_wrong_item("merek hp nya beda")


# --- bahasa Inggris dan kemasan (kalimat ditulis sendiri, bukan salinan data uji) --------------

PACKAGING = {"attribute": "packaging", "attribute_local": "kemasan"}


@pytest.mark.parametrize("text", [
    "The strap feels flimsy and cheap",
    "Lid was leaking all over my bag",
    "Shirt came stained on the collar",
    "Case arrived scratched on one side",
    "The handle broke after a week",
    "Not worth it for this price",
    "Totally not as described",
])
def test_qa22_keluhan_bahasa_inggris(text):
    assert any(lexicon.polarity(c.tokens) == "complaint" for c in lexicon.clauses(text))


@pytest.mark.parametrize("text", ["Seller never replied to my chat", "Admin not responsive at all"])
def test_qa22_keluhan_layanan_bahasa_inggris(text):
    service = {"attribute": "seller responsiveness", "attribute_local": "respons penjual"}
    assert relevance.judge(text, service).label == relevance.SUPPORTS


def test_qa22_litotes_bukan_keluhan():
    assert lexicon.polarity(lexicon.tokens("not bad at all")) != "complaint"


@pytest.mark.parametrize("text", [
    "Dusnya sobek di dua sudut",
    "kardusnya ringsek parah",  # sudah lulus: "parah" keluhan, kardus kemasan
    "The parcel box came crushed",
    "plastik pembungkusnya robek",
])
def test_qa23_kerusakan_kemasan_bukan_kualitas_produk(text):
    assert relevance.judge(text, PACKAGING).label == relevance.SUPPORTS
    assert relevance.judge(text, QUALITY).label != relevance.SUPPORTS


def test_qa23_barang_rusak_dan_dus_penyok_tetap_kualitas():
    assert relevance.judge("barangnya rusak, dusnya juga penyok", QUALITY).label == relevance.SUPPORTS


# --- label AI: kode memegang veto, bukan syarat leksikon lengkap --------------------------------


def _ai(proposal, reviews, labels):
    from app.deciqo.engine import pipeline

    return pipeline._judge_pairs(proposal, reviews, "ai", labels)


CAP = {"attribute": "battery capacity", "attribute_local": "kapasitas baterai", "finding_type": "conflicting_fact"}


def test_qa26_keluhan_tanpa_kata_leksikon_dihitung_bila_klausa_menyebut_atribut():
    reviews = [{"id": "a", "rating": 2, "text": "kapasitasnya gak nyampe 10rb, cuma kuat 1x ngecas"}]
    judged = _ai(CAP, reviews, [{"review_id": "a", "label": "supports", "quote": "kapasitasnya gak nyampe 10rb"}])
    assert set(judged["supports"]) == {"a"}


def test_qa26_pujian_tetap_diveto():
    reviews = [{"id": "b", "rating": 5, "text": "kapasitasnya mantap, sesuai deskripsi"}]
    judged = _ai(CAP, reviews, [{"review_id": "b", "label": "supports", "quote": "kapasitasnya mantap, sesuai deskripsi"}])
    assert "b" not in judged["supports"]


def test_qa26_keluhan_atribut_lain_tetap_diveto():
    reviews = [{"id": "c", "rating": 1, "text": "pengirimannya lama banget, seminggu baru sampai"}]
    judged = _ai(CAP, reviews, [{"review_id": "c", "label": "supports", "quote": "pengirimannya lama banget"}])
    assert "c" not in judged["supports"]


def test_qa26_klausa_tanpa_atribut_tetap_ditolak():
    reviews = [{"id": "d", "rating": 1, "text": "pokoknya nyesel beli di sini"}]
    judged = _ai(CAP, reviews, [{"review_id": "d", "label": "supports", "quote": "pokoknya nyesel beli di sini"}])
    assert "d" not in judged["supports"]
