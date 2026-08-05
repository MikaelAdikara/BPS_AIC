"""Sepuluh tool contract (blueprint bagian 27.3).

Tool di paket ini adalah SATU-SATUNYA sumber angka dalam sistem. Foundation model tidak pernah
menghitung sendiri - ia memanggil tool ini dan menyusun narasi dari hasilnya (ADR-011).

Status implementasi:
    preprocess_reviews()            - Fase 5
    redact_personal_data()          - Fase 5
    classify_text_aspects()         - Fase 5 (adapter ke model Fase 2)
    classify_review_image()         - Fase 5 (adapter ke model Fase 3)
    retrieve_evidence()             - Fase 4 (menyusul)
    calculate_aspect_statistics()   - selesai
    calculate_priority_score()      - selesai
    compare_category_baseline()     - selesai
    generate_action_recommendations() - selesai (template); versi LLM pada Fase 5
    answer_review_question()        - Fase 5
"""

from .actions import build_action_card, has_concrete_numbers
from .benchmark import compare_category_baseline, load_baseline
from .fusion import fuse_all, fuse_review
from .priority import PriorityResult, calculate_priority_score
from .statistics import calculate_aspect_statistics

__all__ = [
    "build_action_card",
    "fuse_all",
    "fuse_review",
    "has_concrete_numbers",
    "calculate_aspect_statistics",
    "calculate_priority_score",
    "compare_category_baseline",
    "load_baseline",
    "PriorityResult",
]
