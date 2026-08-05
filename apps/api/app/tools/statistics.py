"""calculate_aspect_statistics() - tool contract bagian 27.3.

Salah satu dari sepuluh tool yang menjadi SATU-SATUNYA sumber angka di sistem. Foundation model
tidak pernah menghitung sendiri; ia hanya menerima keluaran fungsi ini dan menyusun narasi.

Deterministic dan idempotent: input sama selalu menghasilkan keluaran sama.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from ..schemas import (
    Aspect,
    AspectAggregate,
    ProcessedReview,
    Sentiment,
    Severity,
    TextPrediction,
    Trend,
)

# Jendela pembanding tren: 30 hari terakhir vs sebelumnya (bagian 22.1 "meningkat_30_hari_terakhir")
TREND_WINDOW_DAYS = 30
# Selisih proporsi minimum sebelum tren disebut berubah. Di bawah ini disebut "stabil" -
# tanpa ambang, fluktuasi kecil pada data sedikit akan selalu terlihat sebagai tren.
TREND_MIN_DELTA = 0.05
# Di bawah ini, tren tidak dihitung sama sekali - terlalu sedikit untuk bermakna.
TREND_MIN_MENTIONS_PER_WINDOW = 3

SEVERITY_RANK = {Severity.RENDAH: 0, Severity.SEDANG: 1, Severity.TINGGI: 2}


RANK_TO_SEVERITY = {0: Severity.RENDAH, 1: Severity.SEDANG, 2: Severity.TINGGI}


def _dominant_severity(severities: list[Severity]) -> Severity:
    """Severity tipikal aspek, dihitung dari RATA-RATA peringkat seluruh keluhannya.

    Dua alternatif yang lebih sederhana ditolak setelah diuji pada data nyata:

    - **Terparah (max)** terlihat paling aman, tetapi satu ulasan bintang satu cukup untuk
      membuat SETIAP aspek berlabel "tinggi". Faktor severity lalu menjadi konstan dan berhenti
      membedakan aspek mana yang lebih mendesak - persis kegunaannya yang hilang.
    - **Modus** membuang distribusi. Aspek dengan campuran keluhan ringan dan berat dipaksa
      masuk satu keranjang, sehingga keluhan berat di dalamnya tidak berbekas sama sekali.

    Rata-rata peringkat memakai seluruh informasi: keluhan berat menaikkan nilai tanpa harus
    mendominasi, dan keluhan ringan tidak terhapus. Pembulatan ke atas pada nilai tepat di
    tengah membuat sistem condong ke pembacaan yang lebih hati-hati saat bukti berimbang.

    Catatan keterbatasan: severity saat ini diturunkan dari rating ulasan, sehingga keluhan
    nyata yang muncul di ulasan berbintang tinggi ("bagus, tapi kekecilan") tercatat ringan.
    Ini proksi, bukan ukuran dampak sebenarnya - tercatat di docs/LIMITATIONS.md.
    """
    if not severities:
        return Severity.RENDAH
    mean_rank = sum(SEVERITY_RANK[s] for s in severities) / len(severities)
    return RANK_TO_SEVERITY[min(int(mean_rank + 0.5), 2)]


def _resolve_trend(
    recent_neg: int, recent_total: int, earlier_neg: int, earlier_total: int
) -> Trend:
    """Bandingkan proporsi keluhan pada dua jendela waktu.

    Dibandingkan adalah PROPORSI, bukan jumlah mentah: batch yang lebih besar di periode
    terakhir akan selalu punya jumlah keluhan lebih banyak tanpa berarti keadaannya memburuk.
    """
    if recent_total < TREND_MIN_MENTIONS_PER_WINDOW or earlier_total < TREND_MIN_MENTIONS_PER_WINDOW:
        return Trend.TIDAK_CUKUP_DATA

    delta = (recent_neg / recent_total) - (earlier_neg / earlier_total)
    if delta > TREND_MIN_DELTA:
        return Trend.MENINGKAT
    if delta < -TREND_MIN_DELTA:
        return Trend.MENURUN
    return Trend.STABIL


def calculate_aspect_statistics(
    predictions: list[TextPrediction],
    reviews: list[ProcessedReview] | None = None,
    now: datetime | None = None,
) -> list[AspectAggregate]:
    """Hitung frekuensi, persentase, tren, dan confidence rata-rata per aspek.

    Args:
        predictions: keluaran classify_text_aspects()
        reviews: dipakai HANYA untuk timestamp saat menghitung tren. Tanpa ini - atau tanpa
            timestamp di dalamnya - tren dilaporkan `tidak_cukup_data`, bukan ditebak.
        now: titik acuan jendela tren; default waktu sekarang. Diekspos supaya hasil dapat
            direproduksi pada pengujian.

    Returns:
        Daftar AspectAggregate terurut menurun berdasarkan jumlah keluhan negatif.
    """
    now = now or datetime.now()
    cutoff = now - timedelta(days=TREND_WINDOW_DAYS)
    timestamps = {r.review_id: r.timestamp for r in (reviews or []) if r.timestamp}

    counts: dict[Aspect, dict[str, int]] = defaultdict(
        lambda: {"pos": 0, "neg": 0, "net": 0, "recent_neg": 0, "recent_all": 0,
                 "earlier_neg": 0, "earlier_all": 0}
    )
    confidences: dict[Aspect, list[float]] = defaultdict(list)
    severities: dict[Aspect, list[Severity]] = defaultdict(list)

    for prediction in predictions:
        ts = timestamps.get(prediction.review_id)
        for item in prediction.predictions:
            bucket = counts[item.aspect]
            confidences[item.aspect].append(item.confidence)

            is_negative = item.sentiment == Sentiment.NEGATIF
            if is_negative:
                bucket["neg"] += 1
                severities[item.aspect].append(item.severity)
            elif item.sentiment == Sentiment.POSITIF:
                bucket["pos"] += 1
            else:
                bucket["net"] += 1

            if ts is not None:
                window = "recent" if ts >= cutoff else "earlier"
                bucket[f"{window}_all"] += 1
                if is_negative:
                    bucket[f"{window}_neg"] += 1

    aggregates: list[AspectAggregate] = []
    for aspect, bucket in counts.items():
        total = bucket["pos"] + bucket["neg"] + bucket["net"]
        if total == 0:
            continue

        dominant = _dominant_severity(severities[aspect])
        aggregates.append(
            AspectAggregate(
                aspect=aspect,
                total_mentions=total,
                negative_count=bucket["neg"],
                positive_count=bucket["pos"],
                neutral_count=bucket["net"],
                pct_negative=round(bucket["neg"] / total, 4),
                trend=_resolve_trend(
                    bucket["recent_neg"], bucket["recent_all"],
                    bucket["earlier_neg"], bucket["earlier_all"],
                ),
                avg_confidence=round(sum(confidences[aspect]) / len(confidences[aspect]), 4),
                dominant_severity=dominant,
            )
        )

    return sorted(aggregates, key=lambda a: (a.negative_count, a.total_mentions), reverse=True)
