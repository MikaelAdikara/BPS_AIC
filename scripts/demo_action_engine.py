"""Jalankan rantai deterministic Fase 4 pada dataset demo (spot-check gate Fase 4).

Alur: demo_reviews.csv -> classify_text_aspects() -> calculate_aspect_statistics()
      -> compare_category_baseline() -> calculate_priority_score()

Ini bukan aplikasi; ia pemeriksaan bahwa angka yang keluar dari rantai deterministic masuk akal
SEBELUM lapisan retrieval, narasi, dan API dibangun di atasnya. Gate Fase 4 berbunyi "Action
Card lolos spot-check anti-generik" - output script ini adalah bahan spot-check itu.

Pemakaian:
    python scripts/demo_action_engine.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

from app.adapters.text_model import TextModelAdapter  # noqa: E402
from app.schemas import Category, ProcessedReview  # noqa: E402
from app.tools import (  # noqa: E402
    build_action_card,
    calculate_aspect_statistics,
    calculate_priority_score,
    compare_category_baseline,
    fuse_all,
    has_concrete_numbers,
)

DEMO_PATH = REPO_ROOT / "data" / "samples" / "demo_reviews.csv"


def load_demo() -> list[ProcessedReview]:
    if not DEMO_PATH.exists():
        print("dataset demo belum ada - jalankan scripts/build_sample_dataset.py.", file=sys.stderr)
        raise SystemExit(1)

    df = pd.read_csv(DEMO_PATH)
    return [
        ProcessedReview(
            review_id=row.review_id,
            # Redaksi PII (GOV-01) belum diimplementasikan; dataset demo sudah disaring saat
            # kurasi, sehingga flag ini jujur menyatakan belum ada redaksi yang dijalankan.
            clean_text=str(row.text),
            pii_redacted=False,
            rating=int(row.rating) if pd.notna(row.rating) else None,
            category=Category(row.category),
            has_image=False,
            timestamp=datetime.fromisoformat(row.timestamp) if pd.notna(row.timestamp) else None,
        )
        for row in df.itertuples(index=False)
    ]


def main() -> int:
    reviews = load_demo()
    now = max((r.timestamp for r in reviews if r.timestamp), default=datetime.now())

    adapter = TextModelAdapter()
    print(f"model teks : {adapter.model_version}  (mode {adapter.mode})")
    print(f"ulasan     : {len(reviews)}\n")

    predictions = adapter.classify(reviews)
    aggregates = calculate_aspect_statistics(predictions, reviews, now=now)
    benchmarks = compare_category_baseline(aggregates, Category.FASHION, len(reviews))
    benchmark_by_aspect = {b.aspect: b for b in benchmarks}

    print("=== AGREGAT ASPEK ===")
    print(f"{'aspek':24s} {'sebut':>6s} {'neg':>5s} {'%neg':>7s} {'tren':>18s} {'severity':>10s}")
    for a in aggregates:
        print(
            f"{a.aspect.value:24s} {a.total_mentions:6d} {a.negative_count:5d} "
            f"{a.pct_negative:6.1%} {a.trend.value:>18s} {a.dominant_severity.value:>10s}"
        )

    print("\n=== BENCHMARK KATEGORI (fashion) ===")
    print(f"{'aspek':24s} {'toko':>7s} {'baseline':>9s} {'gap':>8s} {'+/-':>7s} {'keyakinan':>10s}")
    for b in benchmarks[:6]:
        print(
            f"{b.aspect.value:24s} {b.store_pct:6.1%} {b.baseline_pct:8.1%} "
            f"{b.gap:+7.1%} {b.margin_of_error:6.1%} {b.confidence_level.value:>10s}"
        )

    print("\n=== PRIORITAS ===")
    scored = [
        (a, calculate_priority_score(a, len(reviews), benchmark_by_aspect.get(a.aspect)))
        for a in aggregates
    ]
    scored.sort(key=lambda x: x[1].score, reverse=True)

    for rank, (aggregate, result) in enumerate(scored[:5], start=1):
        print(f"\n#{rank}  {aggregate.aspect.value}   skor {result.score}  [{result.urgency.value}]")
        print(f"    {result.reasoning}")
        print(f"    faktor: {result.factors}")

    print("\n=== UJI SENSITIVITAS BOBOT (bagian 22.2) ===")
    print("Apakah urutan prioritas berubah saat bobot digeser +-50%?")
    orders = {}
    for label, (w_r, w_b) in {
        "-50%": (0.15, 0.10), "dasar": (0.30, 0.20), "+50%": (0.45, 0.30)
    }.items():
        ranked = sorted(
            aggregates,
            key=lambda a: calculate_priority_score(
                a, len(reviews), benchmark_by_aspect.get(a.aspect), w_recency=w_r, w_benchmark=w_b
            ).score,
            reverse=True,
        )
        orders[label] = [a.aspect.value for a in ranked]
        print(f"  {label:6s} -> {', '.join(orders[label][:4])}")

    stable = orders["-50%"][:3] == orders["dasar"][:3] == orders["+50%"][:3]
    print(f"\n  tiga teratas stabil terhadap pergeseran bobot: {'YA' if stable else 'TIDAK'}")
    if not stable:
        print("  -> formula perlu ditinjau ulang sebelum dianggap final (bagian 22.2)")

    # ---- Action Card versi template deterministic (jalur FALLBACK MODE) ----
    print("\n\n=== ACTION CARD (narasi template deterministic, tanpa LLM) ===")
    fused = fuse_all(predictions)
    contradictions = [f for f in fused if f.contradiction_flag]
    print(f"kontradiksi teks-visual terdeteksi: {len(contradictions)} "
          f"(nol karena dataset demo belum punya foto)\n")

    generic = 0
    for rank, (aggregate, result) in enumerate(scored[:3], start=1):
        card = build_action_card(
            action_id=f"ACT-DEMO-{rank:03d}",
            aggregate=aggregate,
            priority=result,
            total_reviews=len(reviews),
            benchmark=benchmark_by_aspect.get(aggregate.aspect),
        )
        if not has_concrete_numbers(card):
            generic += 1

        print(f"┌─ #{rank}  [{card.urgency.value.upper()}]  skor {card.priority_score}")
        print(f"│  {card.title}")
        print(f"│  {card.one_line_summary}")
        print(f"│")
        print(f"│  Rekomendasi : {card.recommended_action}")
        print(f"│  Hasil       : {card.expected_outcome}")
        print(f"│  Usaha       : {card.estimated_effort}")
        print(f"│  Pelaksana   : {card.suggested_owner}")
        print(f"│  Bila salah  : {card.risk_if_recommendation_wrong}")
        print(f"│  Kategori    : {card.action_category.value}")
        print(f"└─ user_action: {card.user_action}  (selalu None - keputusan milik manusia)\n")

    print(f"pemeriksaan anti-generik (bagian 22.3): "
          f"{'LULUS - semua rekomendasi memuat angka' if not generic else f'{generic} kartu tanpa angka'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
