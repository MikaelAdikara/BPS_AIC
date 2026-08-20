"""Unit test ING-10 - pembacaan teks ulasan dari tangkapan layar.

Yang diuji di sini adalah bagian yang benar-benar dapat salah dan merugikan pengguna:
**pengelompokan baris menjadi ulasan** dan **penyaringan perabot antarmuka**. Keduanya logika
murni yang tidak menyentuh Tesseract, sehingga test ini berjalan di mesin mana pun, termasuk CI
yang tidak memasang biner OCR.

Akurasi Tesseract itu sendiri tidak diuji di sini - itu properti mesin OCR pihak ketiga, bukan
properti kode ini, dan menguji ulang akan berarti menguji Tesseract, bukan Ulasin.
"""

import pytest

from app.tools.ocr import (
    MIN_REVIEW_CHARS,
    OcrLine,
    _is_chrome,
    _pecah_pada_jurang,
    _rating_dari,
    bersihkan_baris,
    group_lines_into_drafts,
)


def _baris(teks: str, top: int, height: int = 20, conf: float = 90.0) -> OcrLine:
    return OcrLine(text=teks, top=top, height=height, conf=conf)


# ---------------------------------------------------------------- penyaring perabot


@pytest.mark.parametrize(
    "teks",
    [
        "Balas",
        "Bermanfaat",
        "Lihat Balasan",
        "Varian: Hitam, L",
        "Warna: Navy",
        "12 Mei 2024",
        "2024-05-12",
        "3 hari lalu",
        "kemarin",
        "b*****a",
        "★★★★★",
        "   ",
        "12345",
    ],
)
def test_perabot_antarmuka_dibuang(teks):
    assert _is_chrome(teks), f"{teks!r} seharusnya dikenali sebagai perabot antarmuka"


@pytest.mark.parametrize(
    "teks",
    [
        "ukurannya kekecilan padahal udah pesan size L",
        "pengiriman cepat, packing rapi banget",
        "Barangnya bagus tapi warnanya beda dari foto",
    ],
)
def test_kalimat_ulasan_tidak_ikut_terbuang(teks):
    assert not _is_chrome(teks)


def test_kata_balas_di_tengah_kalimat_bukan_perabot():
    """Penyaring mencocokkan baris UTUH, bukan substring.

    Kalau tidak, ulasan yang kebetulan memuat kata "balas" ikut hilang - dan justru keluhan
    soal penjual yang lambat membalas adalah aspek yang paling sering perlu ditindaklanjuti.
    """
    assert not _is_chrome("chat gak dibalas sampai 2 hari")


# ---------------------------------------------------------------- pengelompokan


def test_jarak_vertikal_besar_memisahkan_dua_ulasan():
    baris = [
        _baris("ukurannya kekecilan padahal sudah pesan L", 100),
        _baris("mau tukar tapi ribet prosesnya", 124),
        # Jarak jauh lebih besar dari tinggi baris - batas antar-ulasan.
        _baris("pengiriman cepat dan packing sangat rapi", 260),
    ]
    drafts = group_lines_into_drafts(baris)
    assert len(drafts) == 2
    assert "kekecilan" in drafts[0].text and "ribet" in drafts[0].text
    assert "packing" in drafts[1].text


def test_baris_terbungkus_disambung_jadi_satu_ulasan():
    """Satu ulasan yang terpotong lebar kolom harus kembali menjadi satu paragraf."""
    baris = [
        _baris("barangnya sesuai deskripsi, bahannya adem", 100),
        _baris("dan jahitannya rapi. recommended seller", 124),
        _baris("bakal beli lagi kalau restock", 148),
    ]
    drafts = group_lines_into_drafts(baris)
    assert len(drafts) == 1
    assert drafts[0].lines == 3
    assert "adem dan jahitannya" in drafts[0].text


def test_ambang_pisah_ikut_skala_gambar():
    """Ambangnya relatif terhadap tinggi baris, bukan piksel tetap.

    Tangkapan layar 4K punya baris dua kali lebih tinggi DAN jarak dua kali lebih lebar. Ambang
    tetap akan memecah setiap baris menjadi ulasan tersendiri di layar besar.
    """
    besar = [
        _baris("ukurannya kekecilan padahal sudah pesan L", 200, height=48),
        _baris("mau tukar tapi ribet prosesnya", 258, height=48),
    ]
    assert len(group_lines_into_drafts(besar)) == 1


def test_perabot_di_antara_dua_ulasan_tidak_menggabungkannya():
    baris = [
        _baris("sepatunya nyaman dipakai seharian", 100),
        _baris("Balas", 128),
        _baris("Bermanfaat", 152),
        _baris("r***i", 300),
        _baris("warna aslinya jauh lebih pudar dari foto", 330),
    ]
    drafts = group_lines_into_drafts(baris)
    assert len(drafts) == 2
    assert "Balas" not in drafts[0].text
    assert "pudar" in drafts[1].text


def test_potongan_terlalu_pendek_dibuang():
    baris = [_baris("oke", 100), _baris("sip", 400)]
    assert group_lines_into_drafts(baris) == []
    assert MIN_REVIEW_CHARS > 3


def test_masukan_kosong_menghasilkan_daftar_kosong():
    assert group_lines_into_drafts([]) == []


def test_keyakinan_rendah_ditandai_perlu_diperiksa():
    """Blok yang dibaca dengan ragu harus ditandai, bukan disembunyikan maupun didiamkan."""
    baris = [_baris("brangnya lumyan bgus tapi warnnya beda", 100, conf=52.0)]
    (draft,) = group_lines_into_drafts(baris)
    assert draft.confidence_level == "rendah"


# ---------------------------------------------------------------- rating


@pytest.mark.parametrize(
    "teks,harapan",
    [
        ("5/5 mantap", 5),
        ("bintang 2 aja", 2),
        ("cuma layak 3 bintang", 3),
        ("rating 4 untuk produk ini", 4),
    ],
)
def test_rating_terbaca_bila_ditulis_sebagai_teks(teks, harapan):
    """Perhatikan bahwa semuanya KALIMAT, bukan angka yang berdiri sendiri.

    Bentuk telanjang seperti "3 bintang" sengaja tidak dihitung - lihat
    `test_chip_penyaring_bukan_rating_ulasan`.
    """
    assert _rating_dari(teks) == harapan


def test_chip_penyaring_bukan_rating_ulasan():
    """"5 Bintang" di kepala halaman adalah penyaring yang sedang aktif, bukan penilaian.

    Mengambilnya sebagai rating berarti memberi SETIAP ulasan di layar itu nilai yang sama -
    dan rating ikut menentukan severity, jadi kekeliruannya merambat ke daftar prioritas.
    """
    assert _rating_dari("5 Bintang") is None
    assert _rating_dari("Bintang 4") is None
    assert _is_chrome("5 Bintang")
    # Di dalam kalimat, angkanya memang ditulis pembeli.
    assert _rating_dari("aku kasih 5 bintang deh buat seller ini") == 5


# ---------------------------------------------------------------- pembersihan dalam baris


def test_tanggal_dan_varian_yang_menempel_dibuang():
    """Tesseract menggabungkan apa pun yang sebaris.

    Baris gabungan "12 Mei 2024 | Varian: Hitam, L" tidak cocok dengan pola perabot mana pun
    kalau dicocokkan utuh, sehingga ia harus dipecah dulu pada pemisahnya.
    """
    assert bersihkan_baris("12 Mei 2024 | Varian: Hitam, L") == ""


def test_potongan_yang_bukan_perabot_tetap_tinggal():
    hasil = bersihkan_baris("3 hari lalu | barangnya bagus banget suka")
    assert hasil == "barangnya bagus banget suka"


def test_tombol_dengan_hitungan_tetap_dikenali():
    """"Bermanfaat (3)" adalah tombol yang sama dengan "Bermanfaat"."""
    assert _is_chrome("Bermanfaat (3)")
    assert _is_chrome("Lihat Balasan (12)")
    assert bersihkan_baris("Balas   Bermanfaat (3)") == ""


def test_angka_di_akhir_kalimat_ulasan_tidak_membuatnya_dibuang():
    """Pelepasan angka ekor hanya berlaku bila SISANYA memang nama tombol."""
    assert not _is_chrome("harganya cuma 50000")
    assert bersihkan_baris("dikirim 2 hari, sesuai pesanan 3") != ""


# ---------------------------------------------------------------- pemecahan mendatar


def _kata(teks, left, width, top=100, height=20, conf=90.0):
    return {
        "text": teks,
        "left": left,
        "right": left + width,
        "top": top,
        "height": height,
        "conf": conf,
    }


def test_dua_tombol_berjauhan_dipecah():
    """"Balas" di kiri dan "Bermanfaat" di tengah adalah dua elemen, bukan satu kalimat."""
    kata = [_kata("Balas", 56, 90), _kata("Bermanfaat", 269, 150)]
    potongan = _pecah_pada_jurang(kata)
    assert len(potongan) == 2


def test_kata_dalam_kalimat_tidak_dipecah():
    kata = [
        _kata("ukurannya", 56, 110),
        _kata("kekecilan", 176, 105),
        _kata("banget", 291, 80),
    ]
    assert len(_pecah_pada_jurang(kata)) == 1


def test_rating_tidak_ditebak_bila_hanya_ikon():
    """Bintang yang digambar sebagai ikon tidak punya huruf untuk dibaca.

    None adalah jawaban yang benar di sini. Menebak angka dari nada kalimat akan mengarang
    rating yang lalu ikut terhitung ke dalam severity - dan severity memang sudah diturunkan
    dari rating (lihat docs/LIMITATIONS.md), jadi tebakannya akan berlipat.
    """
    assert _rating_dari("barangnya bagus banget, suka sekali") is None
    assert _rating_dari("harga 50000 dapat 2 pcs") is None
