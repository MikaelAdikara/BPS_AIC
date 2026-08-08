"""OPP-01 dan ING-05 — temuan positif dan skor kualitas data (blueprint bagian 8.2, 22.3).

**OPP-01 menyajikan sinyal, bukan menulis materi promosi.** Blueprint bagian 3.1 menegaskan
produk ini sengaja BUKAN generator konten marketing: ia menunjukkan aspek apa yang benar-benar
dipuji pelanggan beserta kutipannya, lalu pemilik toko yang memutuskan cara memakainya.

**ING-05 menampilkan seberapa layak hasil ini dipercaya.** Tanpanya pengguna menerima angka apa
adanya tanpa tahu bahwa batch-nya kecil, tanpa rating, atau tanpa tanggal — padahal ketiga hal
itu langsung membatasi apa yang dapat disimpulkan.
"""

from __future__ import annotations

from ..schemas import AspectAggregate, DataQuality, EvidenceCitation, Opportunity

# Aspek baru disebut "dipuji" bila porsi positifnya melewati ini DAN cukup sering disebut.
# Tanpa ambang ganda, aspek yang disebut dua kali dan keduanya positif akan terlihat seolah
# kekuatan utama toko.
MIN_POSITIVE_RATIO = 0.70
MIN_MENTIONS = 5
MAX_OPPORTUNITIES = 3

ASPECT_HIGHLIGHT = {
    "pengiriman": "Kecepatan pengiriman Anda konsisten dipuji pembeli",
    "pelayanan_penjual": "Pelayanan Anda konsisten dipuji pembeli",
    "kemasan": "Cara Anda mengemas pesanan konsisten dipuji pembeli",
    "kualitas_produk": "Kualitas produk Anda konsisten dipuji pembeli",
    "harga_value": "Pembeli menilai harga Anda sepadan dengan yang diterima",
    "keaslian": "Pembeli percaya produk Anda asli",
    "ukuran_varian": "Ukuran dan varian Anda dinilai sesuai oleh pembeli",
    "kesesuaian_deskripsi": "Produk Anda dinilai sesuai dengan deskripsinya",
    "rasa_kualitas_makanan": "Rasa produk Anda konsisten dipuji pembeli",
    "kelengkapan": "Kelengkapan isi paket Anda dinilai baik",
    "kemudahan_penggunaan": "Produk Anda dinilai mudah dipakai",
}


def find_opportunities(
    aggregates: list[AspectAggregate],
    total_reviews: int,
    evidence_by_aspect: dict | None = None,
) -> list[Opportunity]:
    """Temukan aspek yang justru menjadi kekuatan toko."""
    evidence_by_aspect = evidence_by_aspect or {}
    found: list[Opportunity] = []

    for agg in aggregates:
        if agg.total_mentions < MIN_MENTIONS or not agg.positive_count:
            continue
        ratio = agg.positive_count / agg.total_mentions
        if ratio < MIN_POSITIVE_RATIO:
            continue

        found.append(
            Opportunity(
                aspect=agg.aspect,
                positive_count=agg.positive_count,
                total_reviews=total_reviews,
                pct_positive=round(ratio, 4),
                highlight=ASPECT_HIGHLIGHT.get(
                    agg.aspect.value, f"Aspek {agg.aspect.value} konsisten dipuji pembeli"
                ),
                evidence_quotes=evidence_by_aspect.get(agg.aspect, [])[:2],
            )
        )

    found.sort(key=lambda o: (o.positive_count, o.pct_positive), reverse=True)
    return found[:MAX_OPPORTUNITIES]


def score_data_quality(
    total_uploaded: int,
    used: int,
    skipped: int,
    with_rating: int,
    with_timestamp: int,
    pii_redacted: int,
) -> DataQuality:
    """Skor 0-100 beserta catatan yang menjelaskan apa yang membatasinya.

    Skor sengaja disertai `notes`: angka tunggal tanpa penjelasan tidak membantu pengguna
    memutuskan apa pun. Yang berguna adalah mengetahui BAGIAN MANA yang kurang.
    """
    notes: list[str] = []
    score = 100

    if used < 15:
        score -= 35
        notes.append(
            f"Hanya {used} ulasan yang dapat dianalisis — anggap hasil ini indikasi awal, "
            "bukan kesimpulan."
        )
    elif used < 50:
        score -= 15
        notes.append(f"{used} ulasan sudah cukup untuk melihat pola, tetapi belum kuat.")

    if used and with_rating / used < 0.5:
        score -= 20
        notes.append(
            "Sebagian besar ulasan tidak menyertakan rating, sehingga tingkat keparahan "
            "keluhan hanya dapat diperkirakan kasar."
        )

    if used and with_timestamp / used < 0.5:
        score -= 20
        notes.append(
            "Sebagian besar ulasan tidak menyertakan tanggal, sehingga tren naik-turun "
            "keluhan tidak dapat dihitung."
        )

    if total_uploaded and skipped / total_uploaded > 0.2:
        score -= 10
        notes.append(f"{skipped} baris dilewati karena kosong atau terduplikasi.")

    if pii_redacted:
        notes.append(
            f"{pii_redacted} ulasan memuat data pribadi dan sudah disamarkan sebelum dianalisis."
        )

    score = max(0, min(100, score))
    level = "baik" if score >= 75 else "cukup" if score >= 45 else "terbatas"
    if not notes:
        notes.append("Data Anda lengkap — hasil analisis dapat dibaca dengan percaya diri.")

    return DataQuality(
        score=score,
        level=level,
        total_uploaded=total_uploaded,
        used=used,
        skipped=skipped,
        with_rating=with_rating,
        with_timestamp=with_timestamp,
        pii_redacted=pii_redacted,
        notes=notes,
    )
