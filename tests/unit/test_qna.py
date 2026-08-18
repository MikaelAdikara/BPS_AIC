"""Test QNA-01 (blueprint bagian 30.2)."""

from __future__ import annotations

import time

from app.schemas import Aspect, AspectAggregate, EvidenceCitation, Severity, Trend
from app.tools import QnAContext, QnAStore, answer_question
from app.tools.qna import _stem, is_out_of_domain


class StubIndex:
    """Mengembalikan kutipan tetap, atau kosong bila diminta bersikap tidak menemukan apa pun."""

    def __init__(self, empty: bool = False):
        self.empty = empty
        self.last_query = None

    def retrieve(self, query, aspect=None, top_k=3, **kw):
        self.last_query = query
        if self.empty:
            return []
        return [
            EvidenceCitation(
                citation_id="c1", review_id="r1", quote="paketnya telat seminggu",
                relevance_score=0.8, aspect=aspect,
            )
        ]


def _agg(aspect=Aspect.PENGIRIMAN, positive=2, negative=8) -> AspectAggregate:
    total = positive + negative
    return AspectAggregate(
        aspect=aspect, total_mentions=total, negative_count=negative, positive_count=positive,
        neutral_count=0, pct_negative=negative / total, trend=Trend.STABIL,
        avg_confidence=0.8, dominant_severity=Severity.SEDANG,
    )


# Sentinel, karena `index=None` adalah nilai yang justru ingin diuji (retrieval mati).
_DEFAULT = object()


def _ctx(index=_DEFAULT, aggregates=None, vocabulary=None) -> QnAContext:
    return QnAContext(
        index=StubIndex() if index is _DEFAULT else index,
        aggregates=aggregates if aggregates is not None else [_agg()],
        total_reviews=40,
        # StubIndex tidak punya korpus, sedangkan penjaga domain menolak SEMUA pertanyaan bila
        # kosakatanya kosong. Kosakata diberikan eksplisit agar test menguji perilaku menjawab,
        # bukan menguji penjaga yang sudah punya testnya sendiri di bawah.
        vocabulary=REVIEW_WORDS if vocabulary is None else vocabulary,
    )


# ---------------------------------------------------------------- grounding


def test_jawaban_selalu_membawa_kutipan():
    """Jawaban tanpa kutipan tidak dapat diperiksa pengguna - dan itu yang produk ini hindari."""
    res = answer_question(_ctx(), "kenapa pengiriman lama?")
    assert res.no_answer is False
    assert res.citations


def test_tanpa_bukti_sistem_menolak_menjawab():
    res = answer_question(_ctx(index=StubIndex(empty=True)), "apakah warnanya bagus?")
    assert res.no_answer is True
    assert res.no_answer_reason
    assert res.answer == ""


def test_tanpa_index_ditolak_dengan_alasan_jelas():
    res = answer_question(_ctx(index=None), "keluhan apa yang paling sering?")
    assert res.no_answer is True
    assert "bukti" in res.no_answer_reason.lower()


def test_pertanyaan_diarahkan_ke_aspek_yang_ditanyakan():
    res = answer_question(_ctx(), "bagaimana soal pengiriman dan kurirnya?")
    assert "pengiriman" in res.answer
    assert "8" in res.answer  # jumlah keluhan yang benar-benar dihitung


def test_pertanyaan_umum_dijawab_dengan_keluhan_terbanyak():
    aggs = [_agg(Aspect.PENGIRIMAN, 2, 3), _agg(Aspect.KEMASAN, 1, 9)]
    res = answer_question(_ctx(aggregates=aggs), "apa masalah terbesar toko saya?")
    assert "kemasan" in res.answer


def test_aspek_tanpa_keluhan_tidak_dilaporkan_seolah_bermasalah():
    res = answer_question(_ctx(aggregates=[_agg(Aspect.PENGIRIMAN, 10, 0)]), "soal pengiriman?")
    assert "tidak ada yang berisi keluhan" in res.answer


def test_angka_jawaban_berasal_dari_agregat_bukan_dikarang():
    res = answer_question(_ctx(aggregates=[_agg(Aspect.KEMASAN, 5, 15)]), "kemasan bagaimana?")
    assert "20" in res.answer and "15" in res.answer


# ---------------------------------------------------------------- penyimpanan sesi


def test_konteks_dapat_diambil_kembali():
    store = QnAStore()
    store.put("an_1", _ctx())
    assert store.get("an_1") is not None


def test_analisis_yang_tidak_dikenal_tidak_error():
    assert QnAStore().get("an_tidak_ada") is None


def test_sesi_lama_dibuang_saat_melewati_batas():
    """Batas ini menjaga janji privasi di layar pertama, bukan sekadar hemat memori."""
    store = QnAStore(max_sessions=2)
    for i in range(3):
        store.put(f"an_{i}", _ctx())
    assert store.get("an_0") is None
    assert store.get("an_2") is not None


def test_sesi_kedaluwarsa_hilang_dengan_sendirinya():
    store = QnAStore(ttl=0)
    store.put("an_1", _ctx())
    time.sleep(0.01)
    assert store.get("an_1") is None


# ---------------------------------------------------------------- penjaga luar domain


def _vocab(*words) -> set:
    return {_stem(w) for w in words}


REVIEW_WORDS = _vocab(
    "pengiriman", "kirim", "paket", "telat", "kemasan", "packing", "ukuran", "kekecilan",
    "harga", "murah", "mahal", "seller", "respon", "bagus", "rusak", "sesuai", "warna",
)


def test_pertanyaan_di_luar_data_ditolak_meski_ada_kata_yang_cocok():
    """Retrieval selalu punya tetangga terdekat; tanpa penjaga ini pertanyaan harga saham
    terjawab oleh statistik harga produk - lengkap dengan kutipan, sehingga tampak sah."""
    assert is_out_of_domain("Berapa harga saham Telkom besok?", REVIEW_WORDS) is True


def test_pertanyaan_wajar_tentang_ulasan_diterima():
    for q in [
        "Apa keluhan yang paling sering muncul?",
        "Bagaimana pendapat pembeli tentang pengiriman?",
        "Apakah ada masalah dengan ukuran atau varian?",
        "Aspek mana yang paling banyak dikeluhkan?",
    ]:
        assert is_out_of_domain(q, REVIEW_WORDS) is False, q


def test_pertanyaan_yang_jelas_asing_ditolak():
    for q in [
        "Siapa presiden Indonesia sekarang?",
        "Tolong tuliskan puisi tentang kucing",
        "Bagaimana cuaca di Jakarta minggu depan?",
        "Buatkan kode python untuk sorting",
    ]:
        assert is_out_of_domain(q, REVIEW_WORDS) is True, q


def test_pertanyaan_kosong_ditolak():
    assert is_out_of_domain("???", set()) is True


def test_penjaga_ikut_berlaku_pada_jawaban_utuh():
    ctx = QnAContext(index=StubIndex(), aggregates=[_agg()], total_reviews=40,
                     vocabulary=REVIEW_WORDS)
    res = answer_question(ctx, "Berapa harga saham Telkom besok?")
    assert res.no_answer is True
    assert res.citations == []


def test_kosakata_dibangun_dari_teks_terindeks():
    """Kosakata diambil dari clean_text yang sudah diredaksi, bukan teks mentah."""
    class Item:
        text = "pengiriman paketnya telat sekali"

    class Idx(StubIndex):
        items = [Item()]

    ctx = QnAContext(index=Idx(), aggregates=[_agg()], total_reviews=10)
    assert _stem("paketnya") in ctx.vocabulary
    assert "telat" in ctx.vocabulary


def test_stemmer_konsisten_antara_pertanyaan_dan_korpus():
    """Yang dibutuhkan penjaga domain adalah konsistensi, bukan kebenaran morfologis.

    "pengiriman" memang tidak kembali menjadi "kirim" (peluluhan tidak dapat dipulihkan), tetapi
    selama bentuk yang sama menghasilkan hasil yang sama, pencocokan kosakata tetap sahih.
    """
    assert _stem("pengiriman") == _stem("pengiriman")
    assert is_out_of_domain("bagaimana pengiriman?", {_stem("pengiriman")}) is False


def test_tanpa_korpus_pertanyaan_topikal_ditolak():
    """Arah kegagalan yang disengaja: tanpa korpus, klaim topikal tidak dapat dibuktikan.

    Pertanyaan analitis tetap lolos karena kosakatanya memang bukan berasal dari ulasan -
    pembeli menulis "paketnya telat", bukan "aspek pengiriman bersentimen negatif".
    """
    assert is_out_of_domain("kenapa pengiriman lama sekali?", set()) is True
    assert is_out_of_domain("apa keluhan pembeli?", set()) is False
