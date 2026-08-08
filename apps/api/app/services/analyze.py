"""AnalyzeService — orkestrasi satu request analisis (blueprint bagian 27.2, sequence 7.5–7.9).

Satu titik orkestrasi per request. Ia memanggil tool sesuai urutan pada sequence diagram dan
TIDAK menghitung apa pun sendiri — seluruh angka berasal dari tool (ADR-011).

Dua sifat yang menentukan bentuk kode ini:

1. **Sinkron.** Tidak ada background job (batas MVP rulebook bagian 2.4). Satu request masuk,
   satu AnalysisResult keluar.
2. **Tidak boleh gagal total.** Kegagalan model visual menurunkan alur ke jalur teks-saja;
   kegagalan orchestrator memicu FALLBACK MODE. Yang menghentikan analisis hanyalah kegagalan
   tool wajib di hulu — dan itupun dengan pesan yang dapat ditindaklanjuti (bagian 25.13).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from ..schemas import (
    AnalysisMode,
    AnalysisResult,
    AnalysisSummary,
    Category,
    RawReview,
)
from ..tools import (
    EvidenceIndex,
    build_action_card,
    calculate_aspect_statistics,
    calculate_priority_score,
    compare_category_baseline,
    fuse_all,
    load_baseline,
    preprocess_reviews,
)

MAX_ACTION_CARDS = 5
EVIDENCE_PER_CARD = 3


class AnalyzeService:
    """Menjalankan pipeline analisis penuh untuk satu batch ulasan."""

    def __init__(
        self, text_adapter, embedding_adapter=None, orchestrator=None, baseline=None,
        min_similarity: float | None = None,
    ):
        self.text_adapter = text_adapter
        self.embedding_adapter = embedding_adapter
        self.orchestrator = orchestrator
        self.baseline = baseline if baseline is not None else load_baseline()
        # Ambang relevansi bukti dapat dikonfigurasi (configs/config.yaml retrieval.min_similarity)
        # karena nilainya bergantung model embedding yang dipakai - ambang yang cocok untuk
        # BGE-M3 belum tentu cocok untuk fallback TF-IDF.
        self.min_similarity = min_similarity

    def _dominant_category(self, reviews) -> Category:
        if not reviews:
            return Category.OTHER
        counts: dict[Category, int] = {}
        for r in reviews:
            counts[r.category] = counts.get(r.category, 0) + 1
        return max(counts, key=counts.get)

    def _build_evidence_index(self, reviews, predictions) -> EvidenceIndex | None:
        if self.embedding_adapter is None:
            return None
        aspects_by_review = {
            p.review_id: [item.aspect.value for item in p.predictions] for p in predictions
        }
        negative_by_review = {
            p.review_id: [
                item.aspect.value for item in p.predictions if item.sentiment.value == "negatif"
            ]
            for p in predictions
        }
        index = (
            EvidenceIndex(self.embedding_adapter, min_similarity=self.min_similarity)
            if self.min_similarity is not None
            else EvidenceIndex(self.embedding_adapter)
        )
        index.build([
            {
                "review_id": r.review_id,
                "text": r.clean_text,
                "aspects": aspects_by_review.get(r.review_id, []),
                "negative_aspects": negative_by_review.get(r.review_id, []),
                "rating": r.rating,
            }
            for r in reviews
        ])
        return index

    def _executive_summary(self, aggregates, total: int, mode: AnalysisMode) -> str:
        """Ringkasan eksekutif. Pada FALLBACK MODE disusun template dari angka yang sama."""
        if not aggregates:
            return f"Dari {total} ulasan, belum ditemukan pola masalah yang cukup jelas."
        top = aggregates[0]
        pct = top.negative_count / total if total else 0.0
        base = (
            f"Dari {total} ulasan, {len([a for a in aggregates if a.negative_count])} aspek "
            f"memuat keluhan. Yang paling sering adalah {top.aspect.value.replace('_', ' ')} "
            f"— {top.negative_count} ulasan ({pct:.0%})."
        )
        if self.orchestrator is not None and mode == AnalysisMode.FULL:
            try:
                return self.orchestrator.summarize(aggregates, total)
            except Exception:
                pass  # jatuh ke template; mode sudah ditandai FALLBACK oleh pemanggil
        return base

    def analyze(self, raw_reviews: list[RawReview], now: datetime | None = None) -> AnalysisResult:
        pre = preprocess_reviews(raw_reviews, now=now)
        reviews = pre.reviews
        warnings = list(pre.warnings)

        if not reviews:
            return AnalysisResult(
                analysis_id=f"an_{uuid.uuid4().hex[:12]}",
                summary=AnalysisSummary(
                    total_reviews=0, reviews_with_image=0,
                    executive_summary_text="Tidak ada ulasan yang dapat dianalisis dari data ini.",
                ),
                warnings=warnings + ["data_kosong"],
                mode=AnalysisMode.FALLBACK,
                model_versions={},
            )

        predictions = self.text_adapter.classify(reviews)

        # Jalur visual dilewati bila tidak ada foto — ini keadaan normal, bukan error.
        visual_predictions: list = []
        fused = fuse_all(predictions, visual_predictions)
        contradictions = [f for f in fused if f.contradiction_flag]

        reference = now or max(
            (r.timestamp for r in reviews if r.timestamp), default=datetime.now()
        )
        aggregates = calculate_aspect_statistics(predictions, reviews, now=reference)

        category = self._dominant_category(reviews)
        benchmarks = compare_category_baseline(
            aggregates, category, len(reviews), baseline=self.baseline
        )
        benchmark_by_aspect = {b.aspect: b for b in benchmarks}

        index = self._build_evidence_index(reviews, predictions)

        scored = [
            (a, calculate_priority_score(a, len(reviews), benchmark_by_aspect.get(a.aspect)))
            for a in aggregates
            if a.negative_count > 0
        ]
        scored.sort(key=lambda x: x[1].score, reverse=True)

        mode = AnalysisMode.FULL if self.orchestrator is not None else AnalysisMode.FALLBACK
        cards = []
        for rank, (aggregate, priority) in enumerate(scored[:MAX_ACTION_CARDS], start=1):
            evidence = []
            if index is not None:
                evidence = index.retrieve(
                    query=aggregate.aspect.value.replace("_", " "),
                    aspect=aggregate.aspect,
                    top_k=EVIDENCE_PER_CARD,
                    negative_only=True,  # kartu keluhan wajib dibuktikan kutipan keluhan
                )
            cards.append(
                build_action_card(
                    action_id=f"ACT-{rank:03d}",
                    aggregate=aggregate,
                    priority=priority,
                    total_reviews=len(reviews),
                    evidence=evidence,
                    benchmark=benchmark_by_aspect.get(aggregate.aspect),
                    contradictions=contradictions,
                )
            )

        if mode == AnalysisMode.FALLBACK:
            warnings.append("mode_sederhana")

        return AnalysisResult(
            analysis_id=f"an_{uuid.uuid4().hex[:12]}",
            summary=AnalysisSummary(
                total_reviews=len(reviews),
                reviews_with_image=sum(1 for r in reviews if r.has_image),
                executive_summary_text=self._executive_summary(aggregates, len(reviews), mode),
            ),
            top_actions=cards,
            aspect_aggregates=aggregates,
            visual_findings=visual_predictions,
            benchmark=benchmarks,
            warnings=warnings,
            mode=mode,
            model_versions={
                "text": self.text_adapter.model_version,
                "embedding": getattr(self.embedding_adapter, "model_name", "tidak aktif"),
                "orchestrator": "tidak aktif" if self.orchestrator is None else "aktif",
            },
        )
