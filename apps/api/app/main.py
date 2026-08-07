"""Backend InsightUlasan — FastAPI, satu service (blueprint bagian 27, 28, ADR-008).

Enam endpoint Tier 1. Seluruhnya **sinkron**: satu input masuk, satu output AI keluar, tanpa
background job (batas MVP rulebook bagian 2.4).

Model dimuat SEKALI saat startup, bukan per-request (bagian 27.2). `/readiness` baru
mengembalikan 200 setelah pemuatan selesai, sehingga frontend tidak menembak API yang belum siap.
"""

from __future__ import annotations

import logging
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(APP_ROOT.parent))

from app.schemas import (  # noqa: E402
    AnalysisResult,
    ErrorCode,
    ErrorResponse,
    QnAResponse,
    RawReview,
    verify_taxonomy_matches_config,
)
from app.services.analyze import AnalyzeService  # noqa: E402

REPO_ROOT = APP_ROOT.parents[2]
SAMPLE_PATH = REPO_ROOT / "data" / "samples" / "demo_reviews.csv"

MAX_REVIEWS_PER_REQUEST = 1000

# Log terstruktur tanpa PII — hanya review_id dan metadata agregat (bagian 37.1).
logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","msg":"%(message)s"}')
log = logging.getLogger("insightulasan")

state: dict = {"ready": False, "service": None, "errors": []}


def _build_service() -> AnalyzeService:
    from app.adapters.text_model import TextModelAdapter  # noqa: PLC0415

    text_adapter = TextModelAdapter()

    # Embedding opsional: tanpanya Action Card tetap terbit, hanya tanpa kutipan bukti.
    embedding_adapter = None
    try:
        from app.adapters.embedding import EmbeddingAdapter  # noqa: PLC0415

        embedding_adapter = EmbeddingAdapter()
    except Exception as exc:  # pragma: no cover
        state["errors"].append(f"embedding: {exc}")
        log.warning("embedding adapter tidak tersedia, evidence retrieval dinonaktifkan")

    # Orchestrator belum diintegrasikan (Fase 5 lanjutan) - sistem berjalan di FALLBACK MODE,
    # yang memang dirancang menghasilkan data identik dengan narasi template (ADR-014).
    return AnalyzeService(
        text_adapter=text_adapter, embedding_adapter=embedding_adapter, orchestrator=None
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    started = time.time()
    try:
        verify_taxonomy_matches_config()
        state["service"] = _build_service()
        state["ready"] = True
        log.info(f"siap dalam {time.time() - started:.1f} detik")
    except Exception as exc:
        state["errors"].append(str(exc))
        log.error(f"startup gagal: {exc}")
    yield


app = FastAPI(
    title="InsightUlasan API",
    version="0.1.0",
    description="Mengubah ulasan pelanggan UMKM menjadi rekomendasi aksi dengan bukti kutipan.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _error(code: ErrorCode, message: str, recoverable: bool, action: str | None = None):
    """Bentuk error konsisten (bagian 25.13) — pesan Bahasa Indonesia sederhana, bukan trace."""
    return JSONResponse(
        status_code=400 if recoverable else 500,
        content=ErrorResponse(
            error_code=code, message=message, recoverable=recoverable, suggested_action=action
        ).model_dump(mode="json"),
    )


class AnalyzeRequest(BaseModel):
    reviews: list[RawReview] = Field(min_length=1)


class QuestionRequest(BaseModel):
    analysis_id: str
    question: str = Field(min_length=1, max_length=500)


@app.get("/api/v1/health")
def health() -> dict:
    """Proses backend hidup. Tidak menjamin model sudah siap — itu tugas /readiness."""
    return {"status": "ok"}


@app.get("/api/v1/readiness")
def readiness():
    if not state["ready"]:
        return JSONResponse(
            status_code=503,
            content={"status": "memuat model", "errors": state["errors"]},
        )
    return {"status": "siap", "warnings": state["errors"]}


@app.get("/api/v1/models")
def models() -> dict:
    """Versi model aktif — dipakai juri untuk memverifikasi reproducibility (bagian 28.1)."""
    service = state["service"]
    if service is None:
        return {"status": "belum siap"}
    return {
        "text": service.text_adapter.model_version,
        "text_mode": service.text_adapter.mode,
        "embedding": getattr(service.embedding_adapter, "model_name", "tidak aktif"),
        "orchestrator": "tidak aktif (FALLBACK MODE)",
    }


@app.get("/api/v1/demo/sample")
def demo_sample() -> dict:
    """Dataset contoh bawaan agar siapa pun dapat mencoba tanpa menyiapkan data (ING-04)."""
    if not SAMPLE_PATH.exists():
        raise HTTPException(status_code=404, detail="dataset contoh belum tersedia")
    import csv  # noqa: PLC0415

    with SAMPLE_PATH.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {"total": len(rows), "reviews": rows}


@app.post("/api/v1/analyze", response_model=AnalysisResult)
def analyze(payload: AnalyzeRequest, request: Request):
    if not state["ready"] or state["service"] is None:
        return _error(
            ErrorCode.MODEL_LOAD_FAILED,
            "Sistem masih menyiapkan model. Coba lagi sebentar lagi.",
            recoverable=True,
            action="Tunggu beberapa saat lalu ulangi.",
        )
    if len(payload.reviews) > MAX_REVIEWS_PER_REQUEST:
        return _error(
            ErrorCode.INVALID_FILE,
            f"Jumlah ulasan melebihi batas {MAX_REVIEWS_PER_REQUEST} per analisis.",
            recoverable=True,
            action="Bagi data Anda menjadi beberapa batch.",
        )

    started = time.time()
    try:
        result = state["service"].analyze(payload.reviews)
    except Exception as exc:
        log.exception("analisis gagal")
        return _error(
            ErrorCode.INTERNAL_ERROR,
            "Terjadi masalah saat menganalisis data Anda.",
            recoverable=False,
            action="Coba unggah ulang, atau gunakan data contoh untuk memastikan sistem berjalan.",
        )

    # Log tanpa PII: hanya jumlah dan durasi, tidak pernah teks ulasan (bagian 37.1).
    log.info(
        f"analyze selesai: {result.summary.total_reviews} ulasan, "
        f"{len(result.top_actions)} action card, mode {result.mode.value}, "
        f"{time.time() - started:.2f}s"
    )
    return result


@app.post("/api/v1/questions", response_model=QnAResponse)
def questions(payload: QuestionRequest):
    """Q&A ter-ground. Pada FALLBACK MODE fitur ini dinonaktifkan dengan pesan jelas.

    Menonaktifkan lebih jujur daripada menjawab tanpa orchestrator: jawaban yang tidak
    ter-ground pada bukti persis yang dihindari produk ini (bagian 30.2).
    """
    return QnAResponse(
        answer="",
        citations=[],
        no_answer=True,
        no_answer_reason=(
            "Tanya jawab sedang tidak tersedia karena sistem berjalan dalam mode sederhana. "
            "Seluruh angka, skor, dan bukti pada hasil analisis tetap lengkap."
        ),
    )
