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
    Granularity,
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
    """Bagian 25.2 - hasil ING-01 + GOV-01, siap dilihat model.

    `product_id` dan `product_name` ditambahkan setelah Fase 0 (blueprint bagian 39.1).
    Keduanya sudah ada di `RawReview` sejak awal, tetapi dibuang di sini - akibatnya tidak ada
    satu pun tahap hilir yang bisa memecah hasil per produk, padahal kolomnya sudah diunggah
    pengguna dan sudah dipetakan di layar unggah. Penambahannya murni aditif dan bernilai
    `None` secara baku, jadi tidak ada pemanggil lama yang berubah perilakunya.
    """

    review_id: str
    clean_text: str
    pii_redacted: bool
    rating: int | None = Field(default=None, ge=1, le=5)
    category: Category
    has_image: bool
    image_refs: list[str] = Field(default_factory=list)
    timestamp: datetime | None = None
    product_id: str | None = None
    product_name: str | None = None


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
    """Bagian 25.10. `quote` adalah kutipan ASLI, tidak diparafrase.

    `rating` dan `timestamp` ikut dibawa agar pengguna dapat menimbang bobot tiap kutipan:
    keluhan bintang 1 dari minggu lalu tidak sama beratnya dengan bintang 3 dari enam bulan
    lalu. Tanpa keduanya, semua kutipan tampak sama pentingnya.
    """

    citation_id: str
    review_id: str
    quote: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    aspect: Aspect | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    timestamp: datetime | None = None


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
# Segmentasi - sebaran bintang, per produk, per periode
# --------------------------------------------------------------------------------------
# Tiga potongan di bawah menjawab pertanyaan yang sama dari tiga arah: keluhan yang sudah
# dihitung `calculate_aspect_statistics()` itu MILIK SIAPA - bintang berapa, produk mana,
# bulan kapan. Tidak ada model yang terlibat; ketiganya membelah prediksi yang sudah jadi.
#
# Satu aturan berlaku di ketiganya: irisan yang isinya terlalu sedikit ditandai `sparse`,
# tidak disembunyikan dan tidak dibulatkan. Satu ulasan negatif dalam satu bulan adalah
# "100% negatif" secara aritmetika, dan menampilkannya tanpa tanda sama saja mengarang
# keyakinan - hal yang sudah ditolak `_resolve_trend()` di tools/statistics.py.
SPARSE_THRESHOLD = 3


class AspectCount(_Base):
    """Satu aspek beserta jumlah keluhannya di dalam satu irisan."""

    aspect: Aspect
    count: int = Field(ge=0)


class RatingBand(_Base):
    """Satu pita bintang, beserta keluhan yang ada DI DALAMNYA.

    `complaints` adalah alasan potongan ini dibangun. Menyaring ulasan menurut bintang sudah
    dilakukan setiap dashboard marketplace; yang tidak dilakukan satu pun dari mereka adalah
    menyebutkan keluhan apa yang menghuni tiap pita. "Dua belas ulasan bintang satu Anda:
    delapan soal ukuran, tiga soal pengiriman" adalah kalimat yang tidak bisa disusun dari
    penyaring biasa.
    """

    rating: int = Field(ge=1, le=5)
    count: int = Field(ge=0)
    pct: float = Field(ge=0.0, le=1.0)
    complaints: list[AspectCount] = Field(default_factory=list)


class RatingBreakdown(_Base):
    """Sebaran bintang seluruh batch."""

    bands: list[RatingBand]
    total_rated: int = Field(ge=0)
    without_rating: int = Field(ge=0)
    average: float | None = None

    @model_validator(mode="after")
    def _five_bands_in_order(self) -> RatingBreakdown:
        # Pita berjumlah tetap lima dan selalu urut 1..5, termasuk yang kosong. Grafik batang
        # yang melewatkan pita tanpa isi menggeser pita di sebelahnya ke tempat yang salah,
        # dan bentuk sebarannya - satu-satunya hal yang dibaca dari grafik ini - jadi keliru.
        if [b.rating for b in self.bands] != [1, 2, 3, 4, 5]:
            raise ValueError("bands wajib memuat bintang 1..5 berurutan, termasuk yang kosong")
        return self


class ProductSummary(_Base):
    """Satu produk di dalam batch yang diunggah.

    Dikelompokkan menurut `product_name`, bukan `product_id`: berkas ekspor marketplace kerap
    membawa nama tanpa id, dan pengguna mengenali produknya lewat nama.
    """

    product_name: str
    total_reviews: int = Field(ge=0)
    negative_reviews: int = Field(ge=0)
    pct_negative: float = Field(ge=0.0, le=1.0)
    avg_rating: float | None = None
    ratings: list[int] = Field(default_factory=list)  # lima angka, bintang 1..5
    complaints: list[AspectCount] = Field(default_factory=list)
    sparse: bool = False


class PeriodBucket(_Base):
    """Satu periode pada riwayat waktu.

    `empty` dan `sparse` dua hal berbeda dan keduanya perlu dibedakan di layar. `empty` berarti
    tidak ada ulasan sama sekali pada periode itu - ia tetap digambar, karena garis waktu yang
    diam-diam merapatkan bulan kosong memampatkan sumbunya dan membuat kenaikan tampak lebih
    curam daripada yang terjadi. `sparse` berarti ada isinya tetapi terlalu sedikit untuk
    dipersentasekan dengan jujur.
    """

    period: str  # "2026-07" atau "2026-W28" - kunci urut, bukan untuk dibaca manusia
    label: str  # "Jul 2026" atau "1 Jul" - yang dibaca manusia
    total_reviews: int = Field(ge=0)
    negative_reviews: int = Field(ge=0)
    pct_negative: float = Field(ge=0.0, le=1.0)
    avg_rating: float | None = None
    sparse: bool = False
    empty: bool = False


class AspectSeries(_Base):
    """Lintasan satu aspek sepanjang seluruh ember, sejajar indeksnya dengan `buckets`."""

    aspect: Aspect
    counts: list[int] = Field(default_factory=list)
    total: int = Field(ge=0)


class PeriodHistory(_Base):
    """Riwayat antar periode DARI SATU BERKAS.

    Perlu dibaca dengan batasnya: ini bukan riwayat lintas sesi. Tidak ada yang disimpan
    setelah halaman ditutup (ADR-010). Yang dilakukan di sini adalah membelah berkas yang
    baru saja diunggah menurut kolom tanggalnya sendiri - dan berkas ekspor marketplace
    biasanya memuat berbulan-bulan sekaligus, sehingga perbandingan antar bulan sebenarnya
    ada di dalam data yang sudah ada di tangan.
    """

    granularity: Granularity
    buckets: list[PeriodBucket] = Field(default_factory=list)
    series: list[AspectSeries] = Field(default_factory=list)
    reviews_dated: int = Field(ge=0)
    reviews_undated: int = Field(ge=0)
    span_days: int = Field(ge=0)
    note: str | None = None


class CategoryGuess(_Base):
    """Kategori yang ditebak sistem, beserta dasar tebakannya.

    Ditebak, lalu DITAMPILKAN - tidak dipakai diam-diam. Kategori menentukan baseline
    pembanding, dan baseline itu muncul di layar sebagai selisih persen yang terbaca seperti
    fakta. Menebaknya salah tanpa memberi tahu siapa pun berarti menaruh angka keliru di
    tempat yang paling dipercaya, jadi tebakannya dipasang di kepala laporan sebagai sesuatu
    yang bisa diganti pengguna dalam satu klik.
    """

    category: Category
    confidence: ConfidenceLevel
    matched_reviews: int = Field(ge=0)
    total_reviews: int = Field(ge=0)
    basis: str  # "nama produk" | "teks ulasan" | "bawaan"


# --------------------------------------------------------------------------------------
# 25.11 - 25.13  Keluaran API
# --------------------------------------------------------------------------------------
class Opportunity(_Base):
    """OPP-01 - aspek yang justru DIPUJI pelanggan (blueprint bagian 8.2, 22.3).

    Disajikan sebagai sinyal untuk materi promosi, BUKAN sebagai teks iklan yang ditulis
    sistem (bagian 3.1: produk ini sengaja bukan generator konten marketing).
    """

    aspect: Aspect
    positive_count: int = Field(ge=0)
    total_reviews: int = Field(ge=0)
    pct_positive: float = Field(ge=0.0, le=1.0)
    highlight: str
    evidence_quotes: list[EvidenceCitation] = Field(default_factory=list)


class DataQuality(_Base):
    """ING-05 - skor kualitas data batch yang diunggah.

    Ditampilkan supaya pengguna tahu seberapa jauh hasil ini layak dipercaya, alih-alih
    menerima angka apa adanya tanpa konteks.
    """

    score: int = Field(ge=0, le=100)
    level: str  # baik | cukup | terbatas
    total_uploaded: int = Field(ge=0)
    used: int = Field(ge=0)
    skipped: int = Field(ge=0)
    with_rating: int = Field(ge=0)
    with_timestamp: int = Field(ge=0)
    pii_redacted: int = Field(ge=0)
    notes: list[str] = Field(default_factory=list)


class AnalysisSummary(_Base):
    """Angka kepala laporan - yang dibaca lebih dulu dari apa pun.

    `reviews_with_complaint` menghitung ULASAN, bukan sebutan. Satu ulasan yang mengeluhkan
    ukuran sekaligus pengiriman tetap satu ulasan yang berkeluhan. Bedanya penting karena
    angka ini duduk bersebelahan dengan `total_reviews` di layar, dan dua angka bersebelahan
    selalu dibaca sebagai pembilang dan penyebut - kalau pembilangnya menghitung sebutan, ia
    bisa melampaui penyebutnya, dan pembaca akan menyimpulkan sistemnya rusak.
    """

    total_reviews: int = Field(ge=0)
    reviews_with_image: int = Field(ge=0)
    reviews_with_complaint: int = Field(default=0, ge=0)
    period_start: datetime | None = None
    period_end: datetime | None = None
    executive_summary_text: str

    @model_validator(mode="after")
    def _complaints_cannot_exceed_total(self) -> AnalysisSummary:
        if self.reviews_with_complaint > self.total_reviews:
            raise ValueError(
                "reviews_with_complaint menghitung ulasan, bukan sebutan - "
                "nilainya tidak boleh melampaui total_reviews"
            )
        return self


class AnalysisResult(_Base):
    """Bagian 25.11 - keluaran utama POST /api/v1/analyze."""

    analysis_id: str
    summary: AnalysisSummary
    top_actions: list[ActionCard] = Field(default_factory=list)
    aspect_aggregates: list[AspectAggregate] = Field(default_factory=list)
    visual_findings: list[VisualPrediction] = Field(default_factory=list)
    benchmark: list[BenchmarkRecord] = Field(default_factory=list)
    opportunities: list[Opportunity] = Field(default_factory=list)
    data_quality: DataQuality | None = None
    # Segmentasi. Ketiganya boleh kosong tanpa membuat hasil cacat: batch tanpa kolom tanggal
    # tidak punya riwayat, batch satu produk tidak punya perbandingan antar produk. Frontend
    # menghilangkan bagiannya alih-alih menampilkan kerangka kosong.
    ratings: RatingBreakdown | None = None
    products: list[ProductSummary] = Field(default_factory=list)
    period_history: PeriodHistory | None = None
    category_guess: CategoryGuess | None = None
    # Baseline seluruh kategori, bukan hanya yang terdeteksi. `compare_category_baseline()`
    # cuma aritmetika atas tabel JSON yang sudah termuat, jadi kelimanya praktis gratis -
    # dan dengan begitu mengoreksi kategori di layar hasil tidak menuntut analisis ulang
    # yang memakan puluhan detik. Kuncinya nilai `Category`.
    benchmark_by_category: dict[str, list[BenchmarkRecord]] = Field(default_factory=dict)
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


# --------------------------------------------------------------------------------------
# ING-10  Pembacaan teks dari tangkapan layar
# --------------------------------------------------------------------------------------
class OcrDraftReview(_Base):
    """Satu calon ulasan hasil pembacaan gambar.

    Namanya menyebut DRAF dengan sengaja. Bentuk ini tidak dapat dikirim langsung ke
    `/analyze`; frontend menampilkannya untuk disunting lebih dulu, lalu menyusun `RawReview`
    dari teks yang sudah dikonfirmasi pengguna.
    """

    text: str
    rating: int | None = Field(default=None, ge=1, le=5)
    # Kata, bukan angka: "0,62" tidak berarti apa pun bagi pemilik toko, sedangkan
    # "perlu diperiksa" menyebut langsung apa yang harus ia lakukan.
    confidence_level: ConfidenceLevel
    source_image: str


class OcrResponse(_Base):
    """Bagian 25.14 - hasil pembacaan satu batch tangkapan layar."""

    images: list[str]
    reviews: list[OcrDraftReview]
    notes: list[str] = Field(default_factory=list)


class ErrorResponse(_Base):
    """Bagian 25.13 - pesan dalam Bahasa Indonesia sederhana."""

    error_code: ErrorCode
    message: str
    recoverable: bool
    suggested_action: str | None = None
