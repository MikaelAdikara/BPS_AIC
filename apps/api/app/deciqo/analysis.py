"""Jembatan platform → engine: menjalankan analisis untuk produk yang berubah setelah ingest.

Engine menyediakan `engine.pipeline.analyse(product_id, force=False)`. Platform tidak tahu isi
analisisnya; ia hanya memastikan analisis berjalan serial (satu lock untuk model triage dan
anggaran AI), melaporkan progres job, dan tidak menjatuhkan seluruh batch bila satu produk gagal.
"""

from __future__ import annotations

import importlib
import logging

from .jobs import ANALYSIS_LOCK, JobContext

log = logging.getLogger("deciqo.analysis")


def _pipeline():
    try:
        return importlib.import_module("app.deciqo.engine.pipeline")
    except ModuleNotFoundError:
        return None


def available() -> bool:
    pipeline = _pipeline()
    return bool(pipeline and hasattr(pipeline, "analyse"))


def analyse_products(ctx: JobContext | None, product_ids: list[str], *, force: bool = False,
                     offset: int = 0, total: int | None = None) -> dict:
    """Analisis beberapa produk berurutan. Mengembalikan ringkasan untuk hasil job."""
    pipeline = _pipeline()
    if not product_ids:
        return {"analysed": 0, "failed": 0}
    if pipeline is None or not hasattr(pipeline, "analyse"):
        return {"analysed": 0, "failed": 0, "pending_engine": len(product_ids)}
    analysed = failed = 0
    total = total if total is not None else len(product_ids)
    for i, pid in enumerate(product_ids):
        if ctx:
            ctx.progress(index=offset + i + 1, total=total, stage="analysing")
        try:
            with ANALYSIS_LOCK:
                pipeline.analyse(pid, force=force)
            analysed += 1
        except Exception as exc:  # noqa: BLE001 - satu produk gagal tidak menghentikan batch
            failed += 1
            log.error(f"analisis {pid} gagal: {type(exc).__name__}: {str(exc)[:200]}")
    return {"analysed": analysed, "failed": failed}
