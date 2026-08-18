"""QNA-01 - tanya jawab yang ter-ground pada ulasan pengguna (blueprint bagian 30.2).

Jawaban di sini **diekstraksi, bukan dikarang**. Setiap kalimat jawaban disusun dari angka yang
sudah dihitung tool lain, dan setiap jawaban wajib membawa kutipan aslinya. Ketika bukti tidak
ditemukan, sistem mengatakan tidak tahu - persis perilaku yang dijanjikan bagian 30.2.

Konsekuensinya jawaban terdengar seperti template. Itu pertukaran yang disengaja: pada produk
yang seluruh nilainya bersandar pada kepercayaan terhadap angka, jawaban yang enak dibaca tetapi
tidak dapat ditelusuri jauh lebih berbahaya daripada jawaban yang kaku.
"""

from __future__ import annotations

import re
import time
from collections import OrderedDict
from dataclasses import dataclass, field

from ..schemas import Aspect, AspectAggregate, EvidenceCitation, QnAResponse

# Kata kunci untuk MENGARAHKAN pertanyaan ke aspek - bukan untuk melabeli ulasan. Pelabelan
# ditangani model; daftar ini hanya menebak topik yang sedang ditanyakan pengguna.
QUESTION_KEYWORDS: dict[Aspect, list[str]] = {
    Aspect.PENGIRIMAN: ["kirim", "pengiriman", "ongkir", "kurir", "sampai", "telat", "lama"],
    Aspect.KEMASAN: ["kemasan", "packing", "bungkus", "dus", "box"],
    Aspect.KUALITAS_PRODUK: ["kualitas", "mutu", "rusak", "cacat", "awet", "bagus"],
    Aspect.HARGA_VALUE: ["harga", "mahal", "murah", "worth", "value"],
    Aspect.PELAYANAN_PENJUAL: ["pelayanan", "penjual", "seller", "respon", "admin", "cs"],
    Aspect.UKURAN_VARIAN: ["ukuran", "size", "varian", "warna", "model"],
    Aspect.KESESUAIAN_DESKRIPSI: ["deskripsi", "sesuai", "gambar", "foto", "beda"],
    Aspect.KEASLIAN: ["asli", "ori", "original", "palsu", "kw"],
    Aspect.RASA_KUALITAS_MAKANAN: ["rasa", "enak", "basi", "expired", "kadaluarsa"],
    Aspect.KELENGKAPAN: ["lengkap", "kurang", "hilang", "isi"],
    Aspect.KEMUDAHAN_PENGGUNAAN: ["mudah", "ribet", "susah", "pakai", "instruksi"],
}

MAX_SESSIONS = 50
SESSION_TTL_SECONDS = 60 * 60
MAX_CITATIONS = 3

# --------------------------------------------------------------------------------------
# Penjaga pertanyaan di luar domain
# --------------------------------------------------------------------------------------
# Retrieval SELALU mengembalikan tetangga terdekat, bahkan untuk pertanyaan yang datanya tidak
# mungkin menjawab. "Berapa harga saham Telkom besok?" mengenai kata "harga", lalu terjawab
# dengan statistik harga produk - lengkap dengan kutipan, sehingga tampak sah. Kegagalan seperti
# itu lebih berbahaya daripada menolak, karena pengguna tidak punya cara menyadarinya.
#
# Penjaganya: berapa banyak kata isi pertanyaan yang sama sekali asing bagi data pengguna.
# Diukur pada korpus contoh (120 ulasan, 467 kata unik) atas 14 pertanyaan - pertanyaan yang
# wajar berhenti di 0.50, pertanyaan di luar domain mulai dari 0.75. Ambang 0.65 duduk di celah
# itu dengan jarak ke kedua sisi.
MAX_UNKNOWN_RATIO = 0.65

# Kata tata bahasa tidak membawa topik, sehingga tidak boleh ikut dihitung.
GRAMMAR_WORDS = {
    "apa", "apakah", "bagaimana", "kenapa", "mengapa", "berapa", "yang", "dan", "itu", "ini",
    "dari", "untuk", "dengan", "saya", "ada", "pada", "tentang", "soal", "paling", "sering",
    "banyak", "mana", "atau", "bisa", "dapat", "juga", "lebih", "kurang", "saja", "sudah",
    "belum", "akan", "harus", "semua", "setiap", "antara", "tersebut", "dalam", "adalah",
    "seperti", "bagi", "oleh", "kalau", "jika", "tapi", "tetapi",
}

# Kosakata untuk BERTANYA tentang analisis. Kata-kata ini jarang muncul di dalam ulasan itu
# sendiri - pembeli menulis "paketnya telat", bukan "aspek pengiriman bersentimen negatif" -
# sehingga tanpa daftar ini pertanyaan analitis yang wajar akan ikut tertolak.
ANALYSIS_WORDS = [
    "keluhan", "masalah", "aspek", "pembeli", "pelanggan", "ulasan", "review", "toko", "produk",
    "barang", "komplain", "positif", "negatif", "puas", "kecewa", "tren", "dikeluhkan",
    "pendapat", "penilaian", "rating", "bintang", "sentimen", "dipuji", "muncul",
]

_PREFIXES = ("meng", "meny", "mem", "men", "ber", "ter", "peng", "pem", "per", "di", "ke", "se",
             "me", "pe")
_SUFFIXES = ("kannya", "annya", "nya", "kan", "an", "i")


def _stem(word: str) -> str:
    """Pemenggal imbuhan seadanya - cukup untuk MENCOCOKKAN kosakata, bukan analisis morfologi.

    Tanpa ini "dikeluhkan" pada pertanyaan tidak akan bertemu "keluhan" pada daftar di atas,
    dan pertanyaan yang sepenuhnya wajar akan tertolak.

    Peluluhan bunyi tidak ditangani: "pengiriman" menjadi "irim", bukan "kirim", karena huruf
    yang luluh tidak dapat dipulihkan tanpa menebak ("mengambil" berasal dari "ambil", bukan
    "kambil"). Yang dibutuhkan penjaga domain hanyalah KONSISTENSI - kata yang sama pada
    pertanyaan dan pada ulasan menghasilkan bentuk yang sama - sehingga kekeliruan linguistik
    ini tidak merugikan. Efeknya hanya sebagian bentuk berimbuhan tidak bertemu bentuk dasarnya,
    dan itu membuat penjaga sedikit lebih mudah menolak, arah kegagalan yang memang diinginkan.
    """
    for prefix in _PREFIXES:
        if word.startswith(prefix) and len(word) - len(prefix) >= 3:
            word = word[len(prefix):]
            break
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            break
    return word


_ANALYSIS_STEMS = {_stem(w) for w in ANALYSIS_WORDS}


def is_out_of_domain(question: str, corpus_vocabulary: set[str]) -> bool:
    """True bila sebagian besar isi pertanyaan tidak ada dalam data pengguna."""
    content = [
        _stem(w)
        for w in re.findall(r"[a-z]{3,}", question.lower())
        if w not in GRAMMAR_WORDS
    ]
    if not content:
        return True
    unknown = [w for w in content if w not in corpus_vocabulary and w not in _ANALYSIS_STEMS]
    return len(unknown) / len(content) > MAX_UNKNOWN_RATIO


@dataclass
class QnAContext:
    """Bahan menjawab untuk satu analisis. Disimpan di memori saja, tidak pernah ke disk."""

    index: object | None
    aggregates: list[AspectAggregate]
    total_reviews: int
    created_at: float = field(default_factory=time.time)
    vocabulary: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        # Kosakata diambil dari teks yang SUDAH diredaksi (index dibangun dari clean_text),
        # sehingga tidak ada PII yang ikut tersimpan di sini.
        if not self.vocabulary and self.index is not None:
            texts = [item.text for item in getattr(self.index, "items", [])]
            self.vocabulary = {
                _stem(w) for t in texts for w in re.findall(r"[a-z]{3,}", t.lower())
            }


class QnAStore:
    """Cache sesi terbatas: paling banyak 50 analisis dan kedaluwarsa dalam satu jam.

    Batas ini bukan optimasi memori, melainkan bagian dari janji privasi di layar pertama:
    data pengguna hidup selama sesi, lalu hilang dengan sendirinya (bagian 37.1).
    """

    def __init__(self, max_sessions: int = MAX_SESSIONS, ttl: int = SESSION_TTL_SECONDS):
        self._items: OrderedDict[str, QnAContext] = OrderedDict()
        self._max = max_sessions
        self._ttl = ttl

    def put(self, analysis_id: str, context: QnAContext) -> None:
        self._evict_expired()
        self._items[analysis_id] = context
        self._items.move_to_end(analysis_id)
        while len(self._items) > self._max:
            self._items.popitem(last=False)

    def get(self, analysis_id: str) -> QnAContext | None:
        self._evict_expired()
        return self._items.get(analysis_id)

    def _evict_expired(self) -> None:
        cutoff = time.time() - self._ttl
        for key in [k for k, v in self._items.items() if v.created_at < cutoff]:
            del self._items[key]


def _detect_aspect(question: str) -> Aspect | None:
    lowered = question.lower()
    best, best_hits = None, 0
    for aspect, keywords in QUESTION_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in lowered)
        if hits > best_hits:
            best, best_hits = aspect, hits
    return best


def _aspect_sentence(aggregate: AspectAggregate, total: int) -> str:
    name = aggregate.aspect.value.replace("_", " ")
    pct_neg = aggregate.negative_count / aggregate.total_mentions if aggregate.total_mentions else 0
    if aggregate.negative_count == 0:
        return (
            f"Dari {total} ulasan, {aggregate.total_mentions} membahas {name} dan tidak ada yang "
            f"berisi keluhan ({aggregate.positive_count} di antaranya positif)."
        )
    return (
        f"Dari {total} ulasan, {aggregate.total_mentions} membahas {name}. "
        f"{aggregate.negative_count} di antaranya berisi keluhan ({pct_neg:.0%}), "
        f"{aggregate.positive_count} positif."
    )


def _overall_sentence(aggregates: list[AspectAggregate], total: int) -> str:
    complained = [a for a in aggregates if a.negative_count]
    if not complained:
        return f"Dari {total} ulasan, tidak ditemukan aspek yang menonjol sebagai keluhan."
    top = max(complained, key=lambda a: a.negative_count)
    return (
        f"Dari {total} ulasan, keluhan terbanyak ada pada "
        f"{top.aspect.value.replace('_', ' ')} - {top.negative_count} ulasan."
    )


def answer_question(context: QnAContext, question: str) -> QnAResponse:
    """Jawab pertanyaan hanya dari data analisis yang bersangkutan."""
    if context.index is None:
        return QnAResponse(
            answer="", citations=[], no_answer=True,
            no_answer_reason=(
                "Pencarian bukti sedang tidak aktif, sehingga jawaban tidak dapat dibuktikan "
                "dengan kutipan. Angka pada hasil analisis tetap lengkap."
            ),
        )

    if is_out_of_domain(question, context.vocabulary):
        return QnAResponse(
            answer="", citations=[], no_answer=True,
            no_answer_reason=(
                "Pertanyaan ini membahas hal yang tidak ada di dalam ulasan Anda, sehingga "
                "tidak dapat dijawab dari data ini. Sistem hanya menjawab pertanyaan seputar "
                "isi ulasan yang Anda unggah."
            ),
        )

    aspect = _detect_aspect(question)
    citations: list[EvidenceCitation] = context.index.retrieve(
        query=question, aspect=aspect, top_k=MAX_CITATIONS
    )

    # Tanpa kutipan, tidak ada yang dapat diperiksa pengguna - dan jawaban yang tidak dapat
    # diperiksa adalah persis yang produk ini hindari.
    if not citations:
        return QnAResponse(
            answer="", citations=[], no_answer=True,
            no_answer_reason=(
                "Tidak ada ulasan Anda yang cukup relevan dengan pertanyaan ini, sehingga "
                "jawabannya tidak dapat dibuktikan. Coba tanyakan hal lain yang memang dibahas "
                "pembeli Anda."
            ),
        )

    by_aspect = {a.aspect: a for a in context.aggregates}
    if aspect is not None and aspect in by_aspect:
        answer = _aspect_sentence(by_aspect[aspect], context.total_reviews)
    else:
        answer = _overall_sentence(context.aggregates, context.total_reviews)

    return QnAResponse(
        answer=f"{answer} Kutipan pendukungnya ada di bawah.",
        citations=citations,
        no_answer=False,
    )
