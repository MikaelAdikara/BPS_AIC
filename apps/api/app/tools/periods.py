"""build_period_history() - riwayat antar periode dari SATU berkas.

Perlu dibaca bersama batasnya. Tidak ada yang disimpan antar sesi (ADR-010), jadi ini bukan
"riwayat toko Anda" - ini pembelahan berkas yang baru saja diunggah menurut kolom tanggalnya
sendiri. Bedanya penting dan disebut apa adanya di layar.

Yang membuatnya tetap berguna: berkas ekspor marketplace hampir selalu memuat berbulan-bulan
sekaligus. Ekspor Shopee pada data contoh membentang sepuluh bulan atas 66 ulasan. Perbandingan
antar bulan sudah ada di dalam data yang dipegang pengguna; yang belum ada selama ini hanyalah
yang membelahnya.

Hubungannya dengan `trend` di tools/statistics.py: fungsi itu membandingkan DUA jendela (30
hari terakhir vs sebelumnya) dan mengeluarkan satu putusan per aspek. Yang di sini membelah
seluruh rentang menjadi banyak ember dan menyimpan lintasannya. Keduanya tidak saling
menggantikan - satu untuk memutuskan, satu untuk melihat bentuknya.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from ..schemas import (
    SPARSE_THRESHOLD,
    Aspect,
    AspectSeries,
    Granularity,
    PeriodBucket,
    PeriodHistory,
    ProcessedReview,
    Sentiment,
    TextPrediction,
)

# Rentang minimum sebelum data dibelah per bulan. Di bawah ini ember bulanan menghasilkan satu
# atau dua batang, dan dua batang bukan riwayat - itu perbandingan yang sudah dikerjakan
# `_resolve_trend()` dengan lebih hati-hati.
MIN_SPAN_MONTHLY = 75

# Rentang minimum sebelum data dibelah per minggu.
MIN_SPAN_WEEKLY = 21

# Ember terbanyak yang digambar. Ekspor tiga tahun per minggu menghasilkan 150 batang, yang
# di layar selebar apa pun berubah jadi arsiran. Saat terlampaui, granularitasnya dinaikkan.
MAX_BUCKETS = 26

BULAN = [
    "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des",
]

# Berapa aspek yang lintasannya disimpan. Sebelas garis di atas satu grafik tidak terbaca;
# yang dicari pengguna adalah aspek yang BERGERAK, dan itu selalu ada di antara yang teratas.
TOP_SERIES = 5


def _month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def _month_label(d: date) -> str:
    return f"{BULAN[d.month - 1]} {d.year}"


def _week_start(d: date) -> date:
    """Senin pada minggu yang memuat `d`."""
    return d - timedelta(days=d.weekday())


def _week_key(d: date) -> str:
    start = _week_start(d)
    return f"{start.year:04d}-W{start.isocalendar()[1]:02d}"


def _week_label(d: date) -> str:
    start = _week_start(d)
    return f"{start.day} {BULAN[start.month - 1]}"


def _next_month(d: date) -> date:
    return date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)


def _month_slots(first: date, last: date) -> list[date]:
    """Setiap bulan dari yang pertama sampai yang terakhir, TERMASUK yang tidak berisi ulasan.

    Bulan kosong sengaja ikut. Garis waktu yang diam-diam merapatkan bulan tanpa data
    memampatkan sumbunya, dan kenaikan antara dua bulan yang sebenarnya terpisah satu kuartal
    akan tampak seperti kenaikan bulan-ke-bulan. Data contoh punya lubang tepat di Februari
    2026, jadi ini bukan kehati-hatian teoretis.
    """
    slots, cursor = [], date(first.year, first.month, 1)
    end = date(last.year, last.month, 1)
    while cursor <= end:
        slots.append(cursor)
        cursor = _next_month(cursor)
    return slots


def _week_slots(first: date, last: date) -> list[date]:
    slots, cursor = [], _week_start(first)
    end = _week_start(last)
    while cursor <= end:
        slots.append(cursor)
        cursor += timedelta(days=7)
    return slots


def _choose_granularity(span_days: int) -> Granularity:
    if span_days >= MIN_SPAN_MONTHLY:
        return Granularity.BULANAN
    if span_days >= MIN_SPAN_WEEKLY:
        return Granularity.MINGGUAN
    return Granularity.TIDAK_CUKUP


def build_period_history(
    reviews: list[ProcessedReview], predictions: list[TextPrediction]
) -> PeriodHistory:
    """Belah batch menurut tanggalnya, lalu hitung ulang tiap ember.

    Args:
        reviews: keluaran preprocess_reviews(); yang tanpa timestamp dihitung terpisah dan
            dilaporkan, tidak diam-diam dibuang
        predictions: keluaran classify_text_aspects()

    Returns:
        PeriodHistory. Bila tanggal tidak ada atau rentangnya terlalu pendek, granularitasnya
        `tidak_cukup` dan `note` menyebutkan sebabnya - bukan larik kosong tanpa penjelasan,
        karena bagian yang hilang tanpa alasan terbaca sebagai kerusakan.
    """
    dated = [r for r in reviews if r.timestamp is not None]
    undated = len(reviews) - len(dated)

    if not dated:
        return PeriodHistory(
            granularity=Granularity.TIDAK_CUKUP,
            reviews_dated=0,
            reviews_undated=undated,
            span_days=0,
            note=(
                "Data Anda tidak memuat kolom tanggal, jadi perubahan antar periode tidak "
                "dapat dihitung. Sertakan kolom tanggal pada ekspor berikutnya."
            ),
        )

    days = [r.timestamp.date() for r in dated]
    first, last = min(days), max(days)
    span_days = (last - first).days
    granularity = _choose_granularity(span_days)

    if granularity is Granularity.TIDAK_CUKUP:
        return PeriodHistory(
            granularity=granularity,
            reviews_dated=len(dated),
            reviews_undated=undated,
            span_days=span_days,
            note=(
                f"Seluruh ulasan Anda berasal dari rentang {span_days} hari. Terlalu rapat "
                "untuk dibandingkan antar periode - perbandingan baru bermakna mulai sekitar "
                f"{MIN_SPAN_WEEKLY} hari."
            ),
        )

    # Terlalu banyak ember pada granularitas mingguan dinaikkan ke bulanan, bukan dipotong.
    # Memotong berarti membuang periode paling lama tanpa mengatakannya.
    if granularity is Granularity.MINGGUAN and len(_week_slots(first, last)) > MAX_BUCKETS:
        granularity = Granularity.BULANAN

    if granularity is Granularity.BULANAN:
        slots = _month_slots(first, last)
        key_of, label_of = _month_key, _month_label
    else:
        slots = _week_slots(first, last)
        key_of, label_of = _week_key, _week_label

    # Ember bulanan yang jumlahnya masih melewati batas dipangkas ke yang TERBARU, dan itu
    # disebutkan di `note`. Pemangkasan yang tidak diberitahukan membuat grafik terbaca
    # seolah data pengguna memang hanya sepanjang itu.
    trimmed = 0
    if len(slots) > MAX_BUCKETS:
        trimmed = len(slots) - MAX_BUCKETS
        slots = slots[-MAX_BUCKETS:]

    order = {key_of(slot): i for i, slot in enumerate(slots)}

    negatives: dict[str, set[Aspect]] = {
        p.review_id: {
            item.aspect for item in p.predictions if item.sentiment == Sentiment.NEGATIF
        }
        for p in predictions
    }

    totals = [0] * len(slots)
    negative_counts = [0] * len(slots)
    rating_sums = [0] * len(slots)
    rating_counts = [0] * len(slots)
    per_aspect: dict[Aspect, list[int]] = defaultdict(lambda: [0] * len(slots))

    for review in dated:
        index = order.get(key_of(review.timestamp.date()))
        if index is None:  # ember yang dipangkas di atas
            continue
        totals[index] += 1
        if review.rating is not None:
            rating_sums[index] += review.rating
            rating_counts[index] += 1
        aspects = negatives.get(review.review_id) or set()
        if aspects:
            negative_counts[index] += 1
        for aspect in aspects:
            per_aspect[aspect][index] += 1

    buckets = [
        PeriodBucket(
            period=key_of(slot),
            label=label_of(slot),
            total_reviews=totals[i],
            negative_reviews=negative_counts[i],
            pct_negative=round(negative_counts[i] / totals[i], 4) if totals[i] else 0.0,
            avg_rating=(
                round(rating_sums[i] / rating_counts[i], 2) if rating_counts[i] else None
            ),
            sparse=0 < totals[i] < SPARSE_THRESHOLD,
            empty=totals[i] == 0,
        )
        for i, slot in enumerate(slots)
    ]

    series = sorted(
        (
            AspectSeries(aspect=aspect, counts=counts, total=sum(counts))
            for aspect, counts in per_aspect.items()
            if sum(counts)
        ),
        key=lambda s: (s.total, s.aspect.value),
        reverse=True,
    )[:TOP_SERIES]

    notes = []
    if undated:
        notes.append(f"{undated} ulasan tidak punya tanggal dan tidak ikut dalam grafik ini.")
    if trimmed:
        notes.append(f"{trimmed} periode terlama tidak digambar agar grafiknya tetap terbaca.")
    if any(b.sparse for b in buckets):
        notes.append(
            "Periode bergaris miring berisi kurang dari "
            f"{SPARSE_THRESHOLD} ulasan - persentasenya belum bisa dipercaya."
        )

    return PeriodHistory(
        granularity=granularity,
        buckets=buckets,
        series=series,
        reviews_dated=len(dated),
        reviews_undated=undated,
        span_days=span_days,
        note=" ".join(notes) or None,
    )
