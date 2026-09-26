"""Perakitan modul Deciqo ke aplikasi FastAPI: router, startup, dan penanda versi.

`main.py` cukup memanggil `include(app)` dan `startup()`; urutan startup ada di satu tempat ini
supaya penambahan langkah (recovery job, seed demo, pemeriksaan ulang verifier) tidak menyentuh
berkas lain.
"""

from __future__ import annotations

import importlib
import logging

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import APP_NAME, APP_VERSION, alerts, auth, insights, routes_sources, settings, store, telegram
from .engine import routes as engine_routes

log = logging.getLogger("deciqo")

system_router = APIRouter(tags=["system"])


def _engine_versions() -> tuple[str, str]:
    engine = importlib.import_module("app.deciqo.engine")
    return (
        getattr(engine, "PIPELINE_VERSION", "unknown"),
        getattr(engine, "VERIFIER_VERSION", "unknown"),
    )


@system_router.get("/api/v1/version")
def version() -> dict:
    """Letak penanda versi build: dipakai README, footer Settings, dan manifest eval."""
    pipeline, verifier = _engine_versions()
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "commit": settings.app_commit(),
        "pipeline": pipeline,
        "verifier": verifier,
    }


_DECIQO_PREFIXES = ("/api/v1/deciqo", "/api/v1/auth")


def _install_error_handlers(app: FastAPI) -> None:
    """Validasi dan kegagalan tak terduga di endpoint Deciqo memakai bentuk error yang sama.

    Endpoint lama Ulasin tetap memakai bentuk bawaannya supaya tes dan klien lamanya tidak berubah."""
    from fastapi.exception_handlers import request_validation_exception_handler  # noqa: PLC0415

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        if not request.url.path.startswith(_DECIQO_PREFIXES):
            return await request_validation_exception_handler(request, exc)
        first = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(p) for p in first.get("loc", [])[1:]) or "body"
        return JSONResponse(
            status_code=422,
            content={"detail": {"code": "invalid_input", "message": f"Invalid value for {field}."}},
        )

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception):
        log.error(f"{request.method} {request.url.path} gagal: {type(exc).__name__}")
        return JSONResponse(
            status_code=500,
            content={"detail": {"code": "internal_error",
                                "message": "Something went wrong on the server. Please try again."}},
        )


def include(app: FastAPI) -> None:
    _install_error_handlers(app)
    app.include_router(system_router)
    app.include_router(auth.router)
    app.include_router(routes_sources.router)
    app.include_router(alerts.router)
    app.include_router(telegram.router)
    app.include_router(engine_routes.router)
    app.include_router(insights.router)


def _optional_hook(module: str, name: str) -> None:
    """Jalankan hook startup milik modul lain bila sudah ada, tanpa membuat startup gagal."""
    try:
        target = importlib.import_module(module)
    except ModuleNotFoundError:
        return
    hook = getattr(target, name, None)
    if hook is None:
        return
    try:
        hook()
    except Exception as exc:  # noqa: BLE001 - satu hook gagal tidak boleh mematikan API
        log.error(f"startup hook {module}.{name} gagal: {type(exc).__name__}")


def startup() -> None:
    """Migrasi → recovery job → seed akun demo → pemeriksaan ulang temuan oleh engine."""
    store.migrate()
    _optional_hook("app.deciqo.jobs", "recover")
    _optional_hook("app.deciqo.samples", "seed_demo")
    _optional_hook("app.deciqo.engine.pipeline", "on_startup")


def start_background() -> None:
    """Thread latar: pengirim alert dan polling Woo. Terpisah dari `startup()` supaya tes bisa
    menjalankan startup tanpa thread yang hidup terus."""
    _optional_hook("app.deciqo.alerts", "start_dispatcher")
    _optional_hook("app.deciqo.routes_sources", "start_poller")
    _optional_hook("app.deciqo.telegram", "start_polling")
