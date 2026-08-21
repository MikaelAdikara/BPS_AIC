"""Unit test detect_category() (apps/api/app/tools/category.py).

Deteksi ini menggantikan satu-satunya pertanyaan wajib di layar unggah, jadi yang diuji bukan
sekadar "apakah tebakannya benar" melainkan apakah ia tahu KAPAN ia sedang menebak: nama produk
didahulukan atas teks ulasan, hasil yang berimbang menolak memilih, dan kecocokan tipis turun
ke keyakinan rendah alih-alih dinyatakan sebagai temuan.
"""

from datetime import datetime

from app.schemas import Category, ConfidenceLevel, ProcessedReview
from app.tools import detect_category


def _review(
    review_id: str, text: str = "barangnya oke", product: str | None = None
) -> ProcessedReview:
    return ProcessedReview(
        review_id=review_id,
        clean_text=text,
        pii_redacted=False,
        rating=5,
        category=Category.OTHER,
        has_image=False,
        timestamp=datetime(2026, 7, 1),
        product_name=product,
    )


def _many(count: int, **kwargs) -> list[ProcessedReview]:
    return [_review(f"r{i}", **kwargs) for i in range(count)]


def test_batch_kosong_jatuh_ke_bawaan():
    hasil = detect_category([])

    assert hasil.category is Category.OTHER
    assert hasil.basis == "bawaan"
    assert hasil.confidence is ConfidenceLevel.RENDAH


def test_nama_produk_dipakai_lebih_dulu():
    reviews = _many(10, product="Sepatu Sneakers Pria", text="dikirim bareng kopi pesanan sebelah")

    hasil = detect_category(reviews)

    assert hasil.category is Category.FASHION
    assert hasil.basis == "nama produk"


def test_teks_ulasan_dipakai_saat_nama_produk_tidak_menyebut_apa_apa():
    """Keadaan nyata: ekspor Shopee yang dianonimkan memuat nama seperti "Produk-1481"."""
    reviews = _many(10, product="Produk-1481", text="kopinya harum, rasanya pas tidak terlalu manis")

    hasil = detect_category(reviews)

    assert hasil.category is Category.FOOD_BEVERAGE
    assert hasil.basis == "teks ulasan"


def test_tanpa_penanda_sama_sekali_jatuh_ke_bawaan():
    reviews = _many(10, text="mantap gan, terima kasih")

    hasil = detect_category(reviews)

    assert hasil.category is Category.OTHER
    assert hasil.basis == "bawaan"


def test_kecocokan_luas_menghasilkan_keyakinan_tinggi():
    reviews = _many(10, product="Kemeja Linen Lengan Panjang")

    assert detect_category(reviews).confidence is ConfidenceLevel.TINGGI


def test_kecocokan_tipis_turun_ke_keyakinan_rendah():
    """Dua dari dua puluh bukan temuan; layar hasil harus memintanya dipastikan sendiri."""
    reviews = _many(18, product="Barang Serbaguna") + [
        _review("x1", product="Kemeja Linen"),
        _review("x2", product="Kemeja Katun"),
    ]

    hasil = detect_category(reviews)

    assert hasil.category is Category.FASHION
    assert hasil.confidence is ConfidenceLevel.RENDAH
    assert hasil.matched_reviews == 2
    assert hasil.total_reviews == 20


def test_dua_kategori_berimbang_menolak_memilih():
    """Toko yang produknya benar-benar campur tidak boleh dilempar koin lalu disebut temuan."""
    reviews = [_review(f"f{i}", product="Kemeja Linen") for i in range(5)]
    reviews += [_review(f"e{i}", product="Charger Laptop") for i in range(5)]

    hasil = detect_category(reviews)

    assert hasil.category is Category.OTHER
    assert hasil.basis == "bawaan"


def test_penanda_dicocokkan_sebagai_kata_utuh():
    """Tanpa batas kata, "tas" cocok di dalam "batas" dan "kue" di dalam "kuesioner"."""
    reviews = _many(10, product="Barang serbaguna", text="sesuai batas waktu, isi kuesioner")

    assert detect_category(reviews).basis == "bawaan"


def test_penanda_berklitik_tetap_cocok():
    """Bentuk berklitik justru yang lazim ditulis orang di ulasan.

    "sepatunya kekecilan" harus terbaca sebagai fesyen. Kalau tidak, deteksi dari teks ulasan
    gagal tepat pada korpus yang paling membutuhkannya - berkas yang nama produknya sudah
    dianonimkan sehingga teks adalah satu-satunya sumber yang tersisa.
    """
    reviews = _many(10, product="Produk-1481", text="sepatunya kekecilan, tapi bajunya pas")

    hasil = detect_category(reviews)

    assert hasil.category is Category.FASHION
    assert hasil.basis == "teks ulasan"
