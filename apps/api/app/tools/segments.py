"""Pembelahan hasil menurut bintang dan menurut produk.

Dua fungsi di berkas ini tidak menghitung apa pun yang baru. Keduanya membelah prediksi yang
sudah dihasilkan `classify_text_aspects()` menurut kolom yang dibawa ulasannya sendiri -
`rating` dan `product_name`. Tetap deterministic dan idempotent seperti tool lain: input sama,
keluaran sama, tanpa model di dalamnya.

Kenapa keduanya sekamar: keduanya menjawab pertanyaan "keluhan ini milik siapa" dan keduanya
memakai penghitung irisan yang sama persis (`_tally`). Memisahkannya jadi dua berkas berarti
menyalin penghitung itu dua kali, dan salinan kedua adalah tempat pertama yang menyimpang saat
definisi "ulasan negatif" berubah.
"""

from __future__ import annotations

from collections import defaultdict

from ..schemas import (
    SPARSE_THRESHOLD,
    Aspect,
    AspectCount,
    ProcessedReview,
    RatingBand,
    RatingBreakdown,
    ProductSummary,
    Sentiment,
    TextPrediction,
)

# Berapa aspek keluhan teratas yang dibawa tiap irisan. Tiga cukup untuk menyebutkan bentuk
# masalahnya ("delapan soal ukuran, tiga soal pengiriman") dan masih muat satu baris di layar
# ponsel. Daftar sebelas aspek per irisan bukan ringkasan, itu tabel kedua.
TOP_COMPLAINTS = 3

# Nama pengganti saat ulasan tidak membawa nama produk sama sekali. Ulasan semacam ini TIDAK
# dibuang dari ringkasan per produk - membuangnya membuat jumlah baris di tabel produk tidak
# lagi berjumlah total ulasan, dan pengguna yang menjumlahkan sendiri akan menemukan selisih
# yang tidak dijelaskan di mana pun.
TANPA_NAMA = "Tanpa nama produk"


def _negative_aspects(prediction: TextPrediction) -> list[Aspect]:
    """Aspek yang dikeluhkan di satu ulasan, tanpa duplikat.

    Duplikat dibuang karena satu ulasan yang menyebut ukuran tiga kali tetaplah SATU ulasan
    yang mengeluhkan ukuran. Tanpa ini, irisan bintang satu bisa melaporkan lebih banyak
    keluhan ukuran daripada jumlah ulasannya sendiri - angka yang langsung terbaca salah.
    """
    seen: list[Aspect] = []
    for item in prediction.predictions:
        if item.sentiment == Sentiment.NEGATIF and item.aspect not in seen:
            seen.append(item.aspect)
    return seen


def _tally(
    review_ids: list[str], negatives: dict[str, list[Aspect]]
) -> tuple[int, list[AspectCount]]:
    """Hitung berapa ulasan yang berkeluhan di satu irisan, dan keluhan apa saja isinya.

    Returns:
        (jumlah ulasan yang memuat >=1 keluhan, aspek terbanyak menurun)
    """
    counts: dict[Aspect, int] = defaultdict(int)
    with_complaint = 0
    for review_id in review_ids:
        aspects = negatives.get(review_id, [])
        if aspects:
            with_complaint += 1
        for aspect in aspects:
            counts[aspect] += 1

    top = sorted(counts.items(), key=lambda kv: (kv[1], kv[0].value), reverse=True)
    return with_complaint, [
        AspectCount(aspect=aspect, count=count) for aspect, count in top[:TOP_COMPLAINTS]
    ]


def _negatives_by_review(predictions: list[TextPrediction]) -> dict[str, list[Aspect]]:
    return {p.review_id: _negative_aspects(p) for p in predictions}


def _average(values: list[int]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def build_rating_breakdown(
    reviews: list[ProcessedReview], predictions: list[TextPrediction]
) -> RatingBreakdown | None:
    """Sebaran bintang, dan keluhan apa yang menghuni tiap pita.

    Menyaring ulasan menurut bintang adalah fitur baku setiap dashboard marketplace. Yang
    ditambahkan di sini adalah isinya: tiap pita membawa aspek yang paling sering dikeluhkan
    DI DALAM pita itu, sehingga "bintang 1 saya kenapa" punya jawaban, bukan cuma daftar
    ulasan untuk dibaca satu per satu.

    Returns:
        None bila tidak satu pun ulasan membawa rating - bagiannya lalu tidak dirender sama
        sekali, alih-alih menggambar lima batang kosong yang terbaca sebagai "semua nol".
    """
    negatives = _negatives_by_review(predictions)

    per_band: dict[int, list[str]] = defaultdict(list)
    without_rating = 0
    for review in reviews:
        if review.rating is None:
            without_rating += 1
            continue
        per_band[review.rating].append(review.review_id)

    total_rated = sum(len(ids) for ids in per_band.values())
    if not total_rated:
        return None

    bands: list[RatingBand] = []
    for star in (1, 2, 3, 4, 5):
        ids = per_band.get(star, [])
        _, complaints = _tally(ids, negatives)
        bands.append(
            RatingBand(
                rating=star,
                count=len(ids),
                pct=round(len(ids) / total_rated, 4),
                complaints=complaints,
            )
        )

    return RatingBreakdown(
        bands=bands,
        total_rated=total_rated,
        without_rating=without_rating,
        average=_average([r.rating for r in reviews if r.rating is not None]),
    )


def summarize_products(
    reviews: list[ProcessedReview], predictions: list[TextPrediction]
) -> list[ProductSummary]:
    """Ringkasan per produk dari kolom produk yang diunggah pengguna.

    Dikelompokkan menurut NAMA, bukan id: berkas ekspor marketplace sering membawa salah satu
    saja, dan nama adalah yang dikenali pemilik toko.

    Produk dengan sedikit ulasan tidak dibuang, hanya ditandai `sparse`. Alasannya terlihat
    pada dua dataset contoh yang bentuknya berlawanan: ekspor Shopee asli memuat 2 produk atas
    66 ulasan - perbandingan yang bermakna - sedangkan berkas kurasi memuat 90 produk atas 120
    ulasan, hampir semuanya satu ulasan masing-masing. Membuang yang tipis akan menyembunyikan
    ekor panjang itu dari pengguna yang datanya memang berbentuk demikian, padahal justru
    bentuk itu yang perlu ia tahu sebelum menarik kesimpulan per produk.

    Returns:
        Terurut menurun menurut jumlah ulasan. Larik kosong bila tidak ada satu pun ulasan
        yang membawa nama produk - bagiannya lalu tidak dirender.
    """
    if not any(r.product_name for r in reviews):
        return []

    negatives = _negatives_by_review(predictions)

    grouped: dict[str, list[ProcessedReview]] = defaultdict(list)
    for review in reviews:
        grouped[review.product_name or TANPA_NAMA].append(review)

    summaries: list[ProductSummary] = []
    for name, group in grouped.items():
        ids = [r.review_id for r in group]
        negative_reviews, complaints = _tally(ids, negatives)
        ratings = [r.rating for r in group if r.rating is not None]

        # Lima keranjang bintang, selalu lengkap termasuk yang nol - dipakai frontend sebagai
        # batang mini di dalam baris tabel, dan batang yang jumlah keranjangnya berubah-ubah
        # antar baris tidak bisa dibandingkan sekilas antar produk.
        histogram = [sum(1 for r in ratings if r == star) for star in (1, 2, 3, 4, 5)]

        summaries.append(
            ProductSummary(
                product_name=name,
                total_reviews=len(group),
                negative_reviews=negative_reviews,
                pct_negative=round(negative_reviews / len(group), 4),
                avg_rating=_average(ratings),
                ratings=histogram,
                complaints=complaints,
                sparse=len(group) < SPARSE_THRESHOLD,
            )
        )

    return sorted(summaries, key=lambda p: (p.total_reviews, p.negative_reviews), reverse=True)
