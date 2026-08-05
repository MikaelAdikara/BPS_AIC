"""Kontrak data internal dan API (blueprint bagian 25, 22.1).

Tiga belas skema di bawah dikunci sejak Fase 0 supaya frontend dapat mulai dengan mock data
sebelum backend selesai. Perubahan setelah titik ini membutuhkan persetujuan seluruh tim
(blueprint bagian 39.1).

Model domain sengaja dipisahkan dari model request/response API (bagian 27.2) - perubahan
bentuk API tidak boleh merembet ke logika inti.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .enums import (
    Aspect,
    ActionCategory,
    AnalysisMode,
    Category,
    ConfidenceLevel,
    ErrorCode,
    FusedEvidenceType,
    ImageQualityFlag,
    ReviewSource,
    Sentiment,
    Severity,
    Trend,
    Urgency,
    UserAction,
    VisualLabel,
)

class _Base(BaseModel):
    model_config = ConfigDict(use_enum_values=False, extra="forbid")


# --------------------------------------------------------------------------------------
# 25.1 - 25.3  Ingestion
# --------------------------------------------------------------------------------------
class RawReview(_Base):
    """Bagian 25.1. `text` boleh string kosong jika entri hanya berisi foto."""

    review_id: str
    text: str
    rating: int | None = Field(default=None, ge=1, le=5)
    timestamp: datetime | None = None
    product_id: str | None = None
    product_name: str | None = None
    category: Category = Category.OTHER
    variant: str | None = None
    image_paths: list[str] = Field(default_factory=list)
    source: ReviewSource
    metadata: dict = Field(default_factory=dict)


class ProcessedReview(_Base):
    """Bagian 25.2 - hasil ING-01 + GOV-01, siap dilihat model."""

    review_id: str
    clean_text: str
    pii_redacted: bool
    rating: int | None = Field(default=None, ge=1, le=5)
    category: Category
    has_image: bool
    image_refs: list[str] = Field(default_factory=list)
    timestamp: datetime | None = None


class ReviewImage(_Base):
    """Bagian 25.3. `image_ref` adalah rujukan sesi sementara, BUKAN path permanen."""

    image_ref: str
    review_id: str
    quality_flag: ImageQualityFlag
    retained_until: datetime


# --------------------------------------------------------------------------------------
# 25.4 - 25.6  Prediksi dan fusion
# --------------------------------------------------------------------------------------
class AspectPrediction(_Base):
    aspect: Aspect
    sentiment: Sentiment
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    source_sentence: str  # traceability - klausa asal prediksi ini


class TextPrediction(_Base):
    """Bagian 25.4."""

    review_id: str
    predictions: list[AspectPrediction] = Field(default_factory=list)
    model_version: str


class VisualPrediction(_Base):
    """Bagian 25.5. Abstention WAJIB saat confidence rendah (bagian 19.2)."""

    image_ref: str
    review_id: str
    label: VisualLabel | None = None
    abstain: bool
    confidence: float = Field(ge=0.0, le=1.0)
    abstain_reason: str | None = None
    model_version: str

    @model_validator(mode="after")
    def _abstain_consistency(self) -> VisualPrediction:
        if self.abstain:
            if self.label is not None:
                raise ValueError("abstain=True tidak boleh disertai label - itu memaksakan hasil")
            if not self.abstain_reason:
                raise ValueError("abstain=True wajib menyertakan abstain_reason")
        elif self.label is None:
            raise ValueError("abstain=False wajib menyertakan label")
        return self


class MultimodalEvidence(_Base):
    """Bagian 25.6 / 20.2 - keluaran FUS-01."""

    review_id: str
    fused_evidence_type: FusedEvidenceType
    combined_confidence: float = Field(ge=0.0, le=1.0)
    contradiction_flag: bool
    display_note: str | None = None
    requires_human_review: bool

    @model_validator(mode="after")
    def _contradiction_forces_review(self) -> MultimodalEvidence:
        # Bagian 20.3: sistem tidak pernah memutuskan siapa yang benar antara teks dan foto.
        if self.contradiction_flag and not self.requires_human_review:
            raise ValueError("contradiction_flag=True WAJIB memicu requires_human_review=True")
        return self


# --------------------------------------------------------------------------------------
# 25.7 - 25.10  Agregat, benchmark, evidence
# --------------------------------------------------------------------------------------
class AspectAggregate(_Base):
    """Bagian 25.7 - keluaran calculate_aspect_statistics()."""

    aspect: Aspect
    total_mentions: int = Field(ge=0)
    negative_count: int = Field(ge=0)
    positive_count: int = Field(ge=0)
    neutral_count: int = Field(default=0, ge=0)
    pct_negative: float = Field(ge=0.0, le=1.0)
    trend: Trend
    avg_confidence: float = Field(ge=0.0, le=1.0)
    dominant_severity: Severity = Severity.RENDAH

    @model_validator(mode="after")
    def _counts_consistent(self) -> AspectAggregate:
        total = self.negative_count + self.positive_count + self.neutral_count
        if total != self.total_mentions:
            raise ValueError(
                f"total_mentions ({self.total_mentions}) tidak sama dengan jumlah per sentimen ({total})"
            )
        return self


class BenchmarkRecord(_Base):
    """Bagian 25.8 - keluaran compare_category_baseline()."""

    category: Category
    aspect: Aspect
    store_pct: float = Field(ge=0.0, le=1.0)
    baseline_pct: float = Field(ge=0.0, le=1.0)
    baseline_sample_size: int = Field(ge=0)
    confidence_level: ConfidenceLevel
    gap: float
    margin_of_error: float = Field(default=0.0, ge=0.0)


class EvidenceCitation(_Base):
    """Bagian 25.10. `quote` adalah kutipan ASLI, tidak diparafrase."""

    citation_id: str
    review_id: str
    quote: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    aspect: Aspect | None = None


# --------------------------------------------------------------------------------------
# 22.1  Action Card
# --------------------------------------------------------------------------------------
class ActionCard(_Base):
    """Bagian 22.1 - novelty inti produk.

    `user_action` default None dan TIDAK PERNAH diisi sistem: rekomendasi menunggu keputusan
    manusia, tidak pernah dieksekusi otomatis (ADR-013).
    """

    action_id: str
    title: str
    one_line_summary: str
    aspect: Aspect
    frequency: int = Field(ge=0)
    frequency_total: int = Field(ge=0)
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    trend: Trend
    priority_score: float = Field(ge=0.0, le=100.0)
    urgency: Urgency
    evidence_quotes: list[EvidenceCitation] = Field(default_factory=list)
    visual_evidence: VisualPrediction | None = None
    priority_reasoning: str
    recommended_action: str
    action_category: ActionCategory
    expected_outcome: str
    estimated_effort: str
    suggested_owner: str
    risk_if_not_done: str
    risk_if_recommendation_wrong: str
    user_action: UserAction | None = None

    @field_validator("frequency_total")
    @classmethod
    def _total_ge_frequency(cls, v: int, info) -> int:
        freq = info.data.get("frequency")
        if freq is not None and v < freq:
            raise ValueError("frequency_total tidak boleh lebih kecil dari frequency")
        return v


# --------------------------------------------------------------------------------------
# 25.11 - 25.13  Keluaran API
# --------------------------------------------------------------------------------------
class AnalysisSummary(_Base):
    total_reviews: int = Field(ge=0)
    reviews_with_image: int = Field(ge=0)
    executive_summary_text: str


class AnalysisResult(_Base):
    """Bagian 25.11 - keluaran utama POST /api/v1/analyze."""

    analysis_id: str
    summary: AnalysisSummary
    top_actions: list[ActionCard] = Field(default_factory=list)
    aspect_aggregates: list[AspectAggregate] = Field(default_factory=list)
    visual_findings: list[VisualPrediction] = Field(default_factory=list)
    benchmark: list[BenchmarkRecord] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    mode: AnalysisMode
    model_versions: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _actions_sorted_by_priority(self) -> AnalysisResult:
        scores = [a.priority_score for a in self.top_actions]
        if scores != sorted(scores, reverse=True):
            raise ValueError("top_actions wajib terurut menurun berdasarkan priority_score")
        return self


class QnARequest(_Base):
    analysis_id: str
    question: str = Field(min_length=1, max_length=500)


class QnAResponse(_Base):
    """Bagian 25.12. Jika `no_answer` True, sistem menolak menjawab alih-alih mengarang."""

    answer: str
    citations: list[EvidenceCitation] = Field(default_factory=list)
    no_answer: bool
    no_answer_reason: str | None = None

    @model_validator(mode="after")
    def _no_answer_needs_reason(self) -> QnAResponse:
        if self.no_answer and not self.no_answer_reason:
            raise ValueError("no_answer=True wajib menyertakan no_answer_reason")
        return self


class ErrorResponse(_Base):
    """Bagian 25.13 - pesan dalam Bahasa Indonesia sederhana."""

    error_code: ErrorCode
    message: str
    recoverable: bool
    suggested_action: str | None = None
