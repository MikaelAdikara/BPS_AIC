"""Unit test GOV-01 dan ING-01 (blueprint bagian 27.3, 32, 35).

Redaksi PII masuk daftar test WAJIB pada bagian 32 — bukan karena rapi, tetapi karena kebocoran
data pelanggan adalah risiko hukum bagi UMKM yang memakai sistem ini (UU PDP).
"""

from datetime import datetime

from app.schemas import Category, RawReview, ReviewSource
from app.tools.ingestion import MIN_REVIEWS_FOR_CONFIDENCE, preprocess_reviews
from app.tools.privacy import contains_pii, redact_personal_data


def _raw(review_id: str, text: str, **kw) -> RawReview:
    return RawReview(review_id=review_id, text=text, source=ReviewSource.MANUAL_UPLOAD, **kw)


# ---------------------------------------------------------------- GOV-01


def test_nomor_telepon_indonesia_diredaksi():
    for text in [
        "hubungi saya di 081234567890",
        "wa +62 812-3456-7890 ya",
        "nomor 0812 3456 7890",
    ]:
        out = redact_personal_data(text)
        assert out.redacted, text
        assert "[nomor telepon]" in out.text
        assert "81234567890" not in out.text.replace(" ", "").replace("-", "")


def test_email_diredaksi():
    out = redact_personal_data("kirim ke budi.santoso@gmail.com dong")
    assert "[email]" in out.text
    assert "gmail" not in out.text


def test_alamat_diredaksi():
    out = redact_personal_data("alamat saya Jl. Merdeka No 45 Bandung")
    assert "[alamat]" in out.text
    assert "Merdeka" not in out.text


def test_username_dan_tautan_diredaksi():
    out = redact_personal_data("cek @tokosayaofficial atau https://toko.example.com/abc")
    assert "[akun]" in out.text
    assert "[tautan]" in out.text


def test_teks_tanpa_pii_tidak_diubah():
    """Redaksi tidak boleh merusak ulasan biasa - itu justru menghilangkan nilai buktinya."""
    text = "ukurannya kekecilan padahal sudah pesan size L"
    out = redact_personal_data(text)
    assert out.text == text
    assert out.redacted is False


def test_hasil_redaksi_tetap_terbaca_sebagai_kalimat():
    """Mengganti, bukan menghapus - kutipan harus tetap berguna sebagai bukti."""
    out = redact_personal_data("barang bagus, hubungi 081234567890 untuk restock")
    assert "barang bagus" in out.text
    assert "untuk restock" in out.text


def test_jumlah_per_jenis_dicatat_tanpa_isinya():
    """MON-01 melaporkan berapa banyak PII ditemukan, tidak pernah isinya (bagian 37.1)."""
    out = redact_personal_data("email a@b.com dan telp 081234567890")
    assert out.counts.get("email") == 1
    assert out.counts.get("telepon") == 1
    assert "a@b.com" not in str(out.counts)


def test_contains_pii_konsisten_dengan_redaksi():
    for text in ["telp 081234567890", "email x@y.co", "ulasan biasa saja"]:
        assert contains_pii(text) == redact_personal_data(text).redacted


def test_input_kosong_tidak_error():
    assert redact_personal_data("").text == ""
    assert redact_personal_data(None).redacted is False  # type: ignore[arg-type]


# ---------------------------------------------------------------- ING-01


def test_redaksi_berjalan_sebelum_hasil_keluar():
    """Bagian 27.3: PII harus hilang SEBELUM data mencapai model manapun."""
    result = preprocess_reviews([_raw("r1", "bagus, wa saya 081234567890")])
    assert result.reviews[0].pii_redacted is True
    assert "081234567890" not in result.reviews[0].clean_text


def test_baris_rusak_dilewati_bukan_menggagalkan_seluruh_batch():
    """Bagian 35: 200 ulasan tidak boleh hilang karena tiga baris bermasalah."""
    raw = [_raw("r1", "ukuran kekecilan"), _raw("r2", ""), _raw("r3", "pengiriman cepat")]
    result = preprocess_reviews(raw)
    assert len(result.reviews) == 2
    assert result.skipped == 1
    assert "baris_dilewati" in result.warnings


def test_entri_tanpa_teks_tetap_diproses_bila_ada_foto():
    """Foto opsional per entri - entri hanya-foto tetap sah (bagian 20.1 kasus 6)."""
    result = preprocess_reviews([_raw("r1", "", image_paths=["img1.jpg"])])
    assert len(result.reviews) == 1
    assert result.reviews[0].has_image is True


def test_duplikat_dibuang_agar_tidak_menggandakan_bobot():
    raw = [_raw("r1", "barang bagus"), _raw("r2", "Barang Bagus"), _raw("r3", "lainnya")]
    result = preprocess_reviews(raw)
    assert len(result.reviews) == 2


def test_review_id_ganda_diberi_akhiran_bukan_dibuang():
    """Membuang akan menghilangkan bukti; menimpa akan merusak penelusuran."""
    raw = [_raw("sama", "ulasan pertama"), _raw("sama", "ulasan kedua")]
    result = preprocess_reviews(raw)
    assert len(result.reviews) == 2
    assert len({r.review_id for r in result.reviews}) == 2


def test_peringatan_data_kecil_muncul():
    result = preprocess_reviews([_raw(f"r{i}", f"ulasan nomor {i}") for i in range(5)])
    assert "data_kecil" in result.warnings


def test_data_cukup_tidak_memicu_peringatan():
    raw = [_raw(f"r{i}", f"ulasan nomor {i} tentang produk") for i in range(MIN_REVIEWS_FOR_CONFIDENCE + 5)]
    assert "data_kecil" not in preprocess_reviews(raw).warnings


def test_metadata_dipertahankan():
    raw = [_raw("r1", "ukuran kekecilan", rating=2, category=Category.FASHION,
                timestamp=datetime(2026, 7, 14))]
    review = preprocess_reviews(raw).reviews[0]
    assert review.rating == 2
    assert review.category == Category.FASHION
    assert review.timestamp == datetime(2026, 7, 14)


def test_batch_kosong_tidak_error():
    result = preprocess_reviews([])
    assert result.reviews == []
