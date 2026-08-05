"""Enum kontrak data (blueprint bagian 25).

Taksonomi aspek adalah SATU-SATUNYA enum yang nilainya juga hidup di luar kode, yaitu di
`configs/taxonomy.yaml` (status FROZEN sejak Fase 0). Blueprint bagian 18.2 mensyaratkan
taksonomi disimpan sebagai config, bukan di-hardcode, supaya kategori baru dapat ditambahkan
tanpa retraining.

Pydantic tetap membutuhkan enum statis untuk validasi, sehingga nilainya ditulis ulang di sini.
Agar dua sumber itu tidak diam-diam menyimpang, `verify_taxonomy_matches_config()` membandingkan
keduanya dan dipanggil saat startup backend - kalau berbeda, sistem gagal cepat dengan pesan
jelas, bukan berjalan dengan taksonomi yang tidak konsisten.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
TAXONOMY_PATH = REPO_ROOT / "configs" / "taxonomy.yaml"
VISUAL_CLASSES_PATH = REPO_ROOT / "configs" / "visual_classes.yaml"


class Aspect(str, Enum):
    """Sebelas aspek, dikunci pada Fase 0 (configs/taxonomy.yaml)."""

    KUALITAS_PRODUK = "kualitas_produk"
    KESESUAIAN_DESKRIPSI = "kesesuaian_deskripsi"
    HARGA_VALUE = "harga_value"
    KEMASAN = "kemasan"
    PENGIRIMAN = "pengiriman"
    PELAYANAN_PENJUAL = "pelayanan_penjual"
    UKURAN_VARIAN = "ukuran_varian"
    RASA_KUALITAS_MAKANAN = "rasa_kualitas_makanan"
    KELENGKAPAN = "kelengkapan"
    KEASLIAN = "keaslian"
    KEMUDAHAN_PENGGUNAAN = "kemudahan_penggunaan"


class Category(str, Enum):
    FASHION = "fashion"
    FOOD_BEVERAGE = "food_beverage"
    CRAFT = "craft"
    ELECTRONICS = "electronics"
    OTHER = "other"


class Sentiment(str, Enum):
    POSITIF = "positif"
    NEGATIF = "negatif"
    NETRAL = "netral"


class Severity(str, Enum):
    RENDAH = "rendah"
    SEDANG = "sedang"
    TINGGI = "tinggi"


class VisualLabel(str, Enum):
    """Empat kelas visual, dikunci pada Fase 0 (configs/visual_classes.yaml)."""

    PRODUK_RUSAK = "produk_rusak"
    SALAH_KIRIM = "salah_kirim"
    KEMASAN_RUSAK = "kemasan_rusak"
    NORMAL = "normal"


class ImageQualityFlag(str, Enum):
    OK = "ok"
    BLURRY = "blurry"
    LOW_LIGHT = "low_light"
    UNSUPPORTED_FORMAT = "unsupported_format"


class Trend(str, Enum):
    MENINGKAT = "meningkat"
    STABIL = "stabil"
    MENURUN = "menurun"
    TIDAK_CUKUP_DATA = "tidak_cukup_data"


class ConfidenceLevel(str, Enum):
    RENDAH = "rendah"
    SEDANG = "sedang"
    TINGGI = "tinggi"


class Urgency(str, Enum):
    RENDAH = "rendah"
    SEDANG = "sedang"
    TINGGI = "tinggi"


class ActionCategory(str, Enum):
    """Sembilan kategori tindakan (blueprint bagian 22.3)."""

    PRODUCT_QUALITY = "product_quality_action"
    PACKAGING = "packaging_action"
    SERVICE = "service_action"
    LISTING_CONTENT = "listing_content_action"
    PRICING_REVIEW = "pricing_review"
    PROMOTION_HIGHLIGHT = "promotion_highlight"
    RESTOCK_VARIANT = "restock_variant_review"
    CUSTOMER_COMMUNICATION = "customer_communication"
    INVESTIGATION_NEEDED = "investigation_needed"


class FusedEvidenceType(str, Enum):
    """Hasil fusion teks+visual (blueprint bagian 20.1-20.2)."""

    TEXT_ONLY = "text_only"
    TEXT_AND_VISUAL_AGREE = "text_and_visual_agree"
    TEXT_VISUAL_CONTRADICTION = "text_visual_contradiction"
    VISUAL_ABSTAIN = "visual_abstain"
    VISUAL_ONLY = "visual_only"


class UserAction(str, Enum):
    """Human-in-the-loop wajib (ADR-013) - tidak pernah ada nilai 'executed'."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SAVED = "saved"


class AnalysisMode(str, Enum):
    FULL = "full"
    FALLBACK = "fallback"


class ErrorCode(str, Enum):
    INVALID_FILE = "INVALID_FILE"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    EMPTY_DATA = "EMPTY_DATA"
    MODEL_LOAD_FAILED = "MODEL_LOAD_FAILED"
    TIMEOUT = "TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ReviewSource(str, Enum):
    MANUAL_UPLOAD = "manual_upload"
    SAMPLE_DATASET = "sample_dataset"


def verify_taxonomy_matches_config() -> None:
    """Gagal cepat jika enum kode menyimpang dari configs/*.yaml.

    Dipanggil saat startup backend. Tanpa pemeriksaan ini, menambah aspek di config tanpa
    memperbarui kode (atau sebaliknya) akan menghasilkan sistem yang diam-diam mengabaikan
    aspek tersebut - kegagalan senyap yang jauh lebih mahal daripada crash di awal.
    """
    import yaml

    if TAXONOMY_PATH.exists():
        config = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
        config_aspects = {a["id"] for a in config["aspects"]}
        code_aspects = {a.value for a in Aspect}
        if config_aspects != code_aspects:
            raise ValueError(
                "Taksonomi aspek tidak sinkron antara kode dan config.\n"
                f"  hanya di config : {sorted(config_aspects - code_aspects)}\n"
                f"  hanya di kode   : {sorted(code_aspects - config_aspects)}\n"
                f"  perbaiki {TAXONOMY_PATH.relative_to(REPO_ROOT)} atau schemas/enums.py"
            )
        config_categories = set(config["categories"])
        code_categories = {c.value for c in Category}
        if config_categories != code_categories:
            raise ValueError(
                "Enum kategori tidak sinkron.\n"
                f"  hanya di config : {sorted(config_categories - code_categories)}\n"
                f"  hanya di kode   : {sorted(code_categories - config_categories)}"
            )

    if VISUAL_CLASSES_PATH.exists():
        visual = yaml.safe_load(VISUAL_CLASSES_PATH.read_text(encoding="utf-8"))
        config_labels = {c["id"] for c in visual["classes"]}
        code_labels = {v.value for v in VisualLabel}
        if config_labels != code_labels:
            raise ValueError(
                "Kelas visual tidak sinkron.\n"
                f"  hanya di config : {sorted(config_labels - code_labels)}\n"
                f"  hanya di kode   : {sorted(code_labels - config_labels)}"
            )
