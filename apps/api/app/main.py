"""Backend Ulasin - FastAPI, satu service (blueprint bagian 27, 28, ADR-008).

Enam endpoint Tier 1. Seluruhnya **sinkron**: satu input masuk, satu output AI keluar, tanpa
background job (batas MVP rulebook bagian 2.4).

Model dimuat SEKALI saat startup, bukan per-request (bagian 27.2). `/readiness` baru
mengembalikan 200 setelah pemuatan selesai, sehingga frontend tidak menembak API yang belum siap.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(APP_ROOT.parent))

from app.schemas import (  # noqa: E402
    AnalysisResult,
    ConfidenceLevel,
    ErrorCode,
    ErrorResponse,
    OcrDraftReview,
    OcrResponse,
    QnAResponse,
    RawReview,
    verify_taxonomy_matches_config,
)
from app.services.analyze import AnalyzeService  # noqa: E402

REPO_ROOT = APP_ROOT.parents[2]
SAMPLE_DIR = REPO_ROOT / "data" / "samples"

# Dua dataset contoh, dan bawaannya yang ASLI. Dataset kurasi enak dipakai menguji tampilan
# karena tiap aspek pasti muncul, tetapi justru karena itu ia tidak membuktikan apa pun soal
# kegunaan nyata: yang dilihat orang adalah hasil pada ulasan yang sudah dipilih. Yang asli
# apa adanya - ada ulasan satu kata, ada yang tidak menyinggung aspek mana pun.
SAMPLES = {
    "asli": ("demo_shopee_asli.csv", "66 ulasan Shopee asli (dianonimkan)"),
    "kurasi": ("demo_reviews.csv", "120 ulasan kurasi - tiap aspek terwakili"),
}
DEFAULT_SAMPLE = "asli"

# Nama kolom berbeda antara berkas hasil scraping dan berkas kurasi. Penyeragaman terjadi di
# sini supaya frontend memakai satu bentuk saja, dan menambah dataset ketiga kelak tidak
# menuntut perubahan di sisi klien.
SAMPLE_ALIASES = {
    "text": ("text", "ulasan", "review", "comment"),
    "rating": ("rating", "bintang", "star"),
    "timestamp": ("timestamp", "tanggal", "date"),
    "category": ("category", "kategori"),
    "product_name": ("product_name", "produk", "product"),
    "variant": ("variant", "varian"),
}

# Batas ini terikat perangkat keras, bukan produk, sehingga dapat diatur lewat lingkungan
# alih-alih dipaku di kode. Pada 2 vCPU terukur ~0,62 detik per ulasan ditambah ~47 detik biaya
# tetap - pengukuran itu MENDAHULUI pengelompokan batch menurut panjang teks di
# EmbeddingAdapter, jadi angka sebenarnya kini lebih baik; batas di bawah tetap memakai angka
# lama sampai ada pengukuran ulang di VM. Batas waktu klien dan nginx sama-sama 300 detik -
# artinya plafon nyatanya
# sekitar 400 ulasan. Membiarkan 1.000 lolos di mesin sekecil itu berarti pengguna menunggu
# beberapa menit hanya untuk berakhir pada pesan kehabisan waktu yang tidak menjelaskan apa
# pun, padahal penolakan yang jujur bisa diberikan seketika. Mesin yang lebih besar tinggal
# menaikkan angkanya tanpa menyentuh kode.
MAX_REVIEWS_PER_REQUEST = int(os.getenv("MAX_REVIEWS_PER_REQUEST", "1000"))

# Batas jumlah gambar per permintaan OCR. Tesseract berjalan sinkron di dalam proses yang sama
# dengan endpoint lain; sepuluh tangkapan layar HP sudah menghabiskan beberapa detik CPU, dan
# batch yang jauh lebih besar akan menahan permintaan analisis milik pengguna lain.
MAX_IMAGES_PER_REQUEST = int(os.getenv("MAX_IMAGES_PER_REQUEST", "10"))

# Log terstruktur tanpa PII - hanya review_id dan metadata agregat (bagian 37.1).
logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","msg":"%(message)s"}')
log = logging.getLogger("ulasin")

state: dict = {"ready": False, "service": None, "errors": []}


def _build_service() -> AnalyzeService:
    from app.adapters.text_model import TextModelAdapter  # noqa: PLC0415

    text_adapter = TextModelAdapter()
    if text_adapter.fallback_reason:
        # Bukan sekadar catatan: tanpa checkpoint, yang berjalan bukan sistem yang dijelaskan
        # proposal, dan itu wajib terbaca di /readiness alih-alih hanya di log.
        state["errors"].append(f"model teks memakai leksikon - {text_adapter.fallback_reason}")
        log.warning(f"model teks jatuh ke leksikon: {text_adapter.fallback_reason}")

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
    title="Ulasin API",
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
    """Bentuk error konsisten (bagian 25.13) - pesan Bahasa Indonesia sederhana, bukan trace."""
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
    """Proses backend hidup. Tidak menjamin model sudah siap - itu tugas /readiness."""
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
    """Versi model aktif - dipakai juri untuk memverifikasi reproducibility (bagian 28.1)."""
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
def demo_sample(dataset: str = DEFAULT_SAMPLE) -> dict:
    """Dataset contoh bawaan agar siapa pun dapat mencoba tanpa menyiapkan data (ING-04)."""
    if dataset not in SAMPLES:
        raise HTTPException(
            status_code=400,
            detail="dataset contoh tidak dikenal; pilihan: %s" % ", ".join(SAMPLES),
        )
    nama_berkas, label = SAMPLES[dataset]
    path = SAMPLE_DIR / nama_berkas
    if not path.exists():
        raise HTTPException(status_code=404, detail="dataset contoh belum tersedia")
    import csv  # noqa: PLC0415

    with path.open(encoding="utf-8") as fh:
        mentah = list(csv.DictReader(fh))

    reviews = []
    for i, row in enumerate(mentah):
        baris = {"review_id": row.get("review_id") or f"{dataset}_{i:04d}"}
        for kanonik, kandidat in SAMPLE_ALIASES.items():
            baris[kanonik] = next((row[k] for k in kandidat if row.get(k)), "")
        reviews.append(baris)

    return {"total": len(reviews), "dataset": dataset, "label": label, "reviews": reviews}


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


@app.post("/api/v1/ocr", response_model=OcrResponse)
async def ocr(images: list[UploadFile] = File(...)):
    """ING-10 - baca teks ulasan dari tangkapan layar.

    Endpoint ini TIDAK menganalisis apa pun. Ia mengembalikan draf teks untuk diperiksa
    pengguna; analisis baru berjalan setelah pengguna menekan tombolnya sendiri di
    `/analyze`. Pemisahan itu disengaja - pembacaan gambar tidak pernah sempurna, dan
    menganalisis hasil bacaan yang belum dikonfirmasi berarti menumpuk kesalahan.

    Gambarnya sendiri tidak pernah disimpan: byte-nya dibaca dari memori, dipakai, lalu
    dilepas bersama request (ADR-010, kebijakan session-only).
    """
    from app.tools.ocr import OcrRejected, OcrUnavailable, read_screenshot  # noqa: PLC0415

    if len(images) > MAX_IMAGES_PER_REQUEST:
        return _error(
            ErrorCode.INVALID_FILE,
            f"Maksimal {MAX_IMAGES_PER_REQUEST} gambar sekali unggah.",
            recoverable=True,
            action="Unggah sebagian dulu, lalu tambahkan sisanya.",
        )

    terbaca: list[str] = []
    drafts: list[OcrDraftReview] = []
    notes: list[str] = []

    for berkas in images:
        nama = berkas.filename or "gambar"
        try:
            hasil = read_screenshot(await berkas.read(), nama)
        except OcrUnavailable as exc:
            log.error(f"OCR tidak tersedia: {exc}")
            return _error(
                ErrorCode.MODEL_LOAD_FAILED,
                "Pembacaan teks dari gambar sedang tidak tersedia di server ini.",
                recoverable=False,
                action="Sementara ini, tempel teks ulasannya langsung atau unggah berkas CSV.",
            )
        except OcrRejected as exc:
            notes.append(f"{nama}: {exc}")
            continue

        terbaca.append(nama)
        if not hasil.drafts:
            notes.append(f"{nama}: tidak ada teks ulasan yang terbaca.")
        for d in hasil.drafts:
            drafts.append(
                OcrDraftReview(
                    text=d.text,
                    rating=d.rating,
                    confidence_level=ConfidenceLevel(d.confidence_level),
                    source_image=nama,
                )
            )

    # Tanpa PII dan tanpa isi teks - hanya jumlah, sesuai bagian 37.1.
    log.info(f"ocr selesai: {len(terbaca)} gambar, {len(drafts)} draf ulasan")
    return OcrResponse(images=terbaca, reviews=drafts, notes=notes)


@app.post("/api/v1/questions", response_model=QnAResponse)
def questions(payload: QuestionRequest):
    """Q&A ter-ground: jawaban disusun dari angka analisis dan selalu membawa kutipannya.

    Tanpa orchestrator, jawaban memakai kalimat template - sama seperti ringkasan eksekutif pada
    FALLBACK MODE (ADR-014). Yang tidak pernah berubah adalah syaratnya: tanpa bukti yang dapat
    dikutip, sistem menolak menjawab alih-alih mengarang (bagian 30.2).
    """
    if not state["ready"] or state["service"] is None:
        return QnAResponse(
            answer="", citations=[], no_answer=True,
            no_answer_reason="Sistem masih menyiapkan model. Coba lagi sebentar lagi.",
        )
    return state["service"].answer(payload.analysis_id, payload.question)
