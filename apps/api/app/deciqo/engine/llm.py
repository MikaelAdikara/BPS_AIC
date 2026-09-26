"""Klien LLM engine: OpenAI Responses API dengan structured output (JSON schema, strict).

Setiap panggilan:

1. Reservasi biaya TERBURUK sebelum memanggil (input ≈ karakter/2 termasuk skema, output =
   `max_output_tokens`). Ditolak bila melampaui sisa anggaran server atau kuota akun.
2. Satu baris ledger per panggilan dengan harga yang berlaku saat itu. Setelah respons, reservasi
   diganti biaya nyata dari `usage` (cached input dihargai terpisah). Panggilan gagal tanpa `usage`
   tetap tercatat `unknown:*` dengan biaya reservasinya, bukan nol.
3. Respons `incomplete` (mis. kehabisan `max_output_tokens`) adalah KEGAGALAN, bukan hasil kosong.
4. Key ditolak (401, kuota habis, akun nonaktif): AI dimatikan untuk sisa proses, alasannya
   disimpan, dan pemanggil beralih ke analyser aturan.
5. Gambar (purpose `vision`) dikirim sebagai URL dengan `detail: low`. Reservasinya tetap
   dihitung konservatif `IMAGE_RESERVE_TOKENS` token input per gambar, jauh di atas biaya nyata
   detail rendah, supaya anggaran tidak pernah terlampaui karena gambar.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime, timezone

from .. import settings, store

log = logging.getLogger("deciqo.engine.llm")


class LLMError(Exception):
    """Panggilan gagal (timeout, error provider, respons tidak lengkap/tidak valid)."""


class KeyRejected(LLMError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class BudgetExceeded(LLMError):
    pass


class ImageUnreadable(LLMError):
    """Provider menolak permintaan bergambar (400): biasanya URL gambar tidak bisa diunduh/dibaca."""


# Aturan hackkit: anggap ~1500 token input per gambar saat reservasi, apa pun detailnya.
IMAGE_RESERVE_TOKENS = 1500

_rejected: dict[str, str] = {}
_lock = threading.Lock()
_client = None


def model_name() -> str:
    return settings.llm_model()


def prices() -> dict:
    return {
        "in": settings.env_float("DECIQO_PRICE_INPUT_PER_M", 0.25),
        "cached": settings.env_float("DECIQO_PRICE_CACHED_INPUT_PER_M", 0.025),
        "out": settings.env_float("DECIQO_PRICE_OUTPUT_PER_M", 2.00),
    }


def key_rejected() -> str | None:
    return _rejected.get("reason")


def reset_rejection() -> None:
    _rejected.clear()


def available(user_id: int | None = None) -> tuple[bool, str]:
    if not settings.openai_configured():
        return False, "no_api_key"
    if _rejected:
        return False, f"key_rejected:{_rejected['reason']}"
    return True, ""


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI  # noqa: PLC0415

        _client = OpenAI(api_key=settings.env("OPENAI_API_KEY"), timeout=settings.env_float("DECIQO_LLM_TIMEOUT_S", 120.0),
                         max_retries=1)
    return _client


def set_client(client) -> None:
    """Untuk tes: pasang klien palsu (atau None untuk kembali ke klien sungguhan)."""
    global _client
    _client = client


def _cost(input_tokens: int, cached: int, output_tokens: int, p: dict) -> float:
    fresh = max(0, input_tokens - cached)
    return (fresh * p["in"] + cached * p["cached"] + output_tokens * p["out"]) / 1_000_000


def _committed(conn) -> float:
    """Biaya terkonfirmasi + reservasi yang belum diselesaikan atau gagal tanpa usage."""
    return conn.execute(
        "SELECT COALESCE(SUM(CASE WHEN status = 'ok' THEN cost_usd ELSE reserved_usd END), 0) "
        "FROM ledger WHERE provider = 'openai'").fetchone()[0]


def _account_spent(conn, user_id: int) -> float:
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    return conn.execute(
        "SELECT COALESCE(SUM(CASE WHEN status = 'ok' THEN cost_usd ELSE reserved_usd END), 0) FROM ledger "
        "WHERE provider = 'openai' AND user_id = ? AND substr(created_at, 1, 7) = ?", (user_id, month)).fetchone()[0]


def _reserve(purpose: str, user_id: int | None, ref: str, amount: float, p: dict, db_path) -> int:
    with store.database(db_path) as conn:
        remaining = settings.ai_budget_usd() - _committed(conn)
        if amount > remaining:
            raise BudgetExceeded(f"reservation {amount:.4f} exceeds remaining budget {remaining:.4f}")
        quota = settings.env_float("DECIQO_ACCOUNT_MONTHLY_AI_USD", 0.0)
        if quota > 0 and user_id is not None and _account_spent(conn, user_id) + amount > quota:
            raise BudgetExceeded("account monthly AI quota reached")
        cur = conn.execute(
            "INSERT INTO ledger(user_id, provider, purpose, model, status, price_in, price_cached, price_out, "
            "reserved_usd, ref, created_at) VALUES(?, 'openai', ?, ?, 'reserved', ?, ?, ?, ?, ?, ?)",
            (user_id, purpose, model_name(), p["in"], p["cached"], p["out"], amount, ref, store.now()))
        return cur.lastrowid


def _settle(row_id: int, status: str, usage: dict | None, latency_ms: int, p: dict, db_path) -> float:
    with store.database(db_path) as conn:
        if usage:
            cost = _cost(usage["input_tokens"], usage["cached_tokens"], usage["output_tokens"], p)
            conn.execute(
                "UPDATE ledger SET status = ?, input_tokens = ?, cached_tokens = ?, output_tokens = ?, cost_usd = ?, "
                "latency_ms = ? WHERE id = ?",
                (status, usage["input_tokens"], usage["cached_tokens"], usage["output_tokens"], cost, latency_ms, row_id))
            return cost
        conn.execute("UPDATE ledger SET status = ?, latency_ms = ? WHERE id = ?", (status, latency_ms, row_id))
        return 0.0


def _usage_of(response) -> dict | None:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    details = getattr(usage, "input_tokens_details", None)
    return {"input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
            "cached_tokens": int(getattr(details, "cached_tokens", 0) or 0) if details else 0,
            "output_tokens": int(getattr(usage, "output_tokens", 0) or 0)}


def _is_key_rejection(exc: Exception) -> str | None:
    name = type(exc).__name__
    code = str(getattr(exc, "code", "") or "")  # openai.APIError membawa kode error provider
    if name in {"AuthenticationError", "PermissionDeniedError"} or getattr(exc, "status_code", None) == 401:
        return "invalid_or_revoked_key"
    if code in {"insufficient_quota", "account_deactivated", "billing_hard_limit_reached"}:
        return code
    return None


def _mark_rejected(reason: str, db_path) -> None:
    with _lock:
        _rejected["reason"] = reason
    try:
        with store.database(db_path) as conn:
            store.set_kv(conn, "llm_key_rejected", reason)
    except Exception:  # noqa: BLE001 - status tetap tercatat di memori proses
        pass
    log.warning(f"key AI ditolak ({reason}); engine beralih ke mode aturan")


def call_json(*, purpose: str, system: str, user: str, schema: dict, schema_name: str,
              max_output_tokens: int, user_id: int | None = None, ref: str = "",
              reasoning: str | None = None, db_path=None, images: list[str] | None = None,
              image_detail: str = "low") -> tuple[dict, dict]:
    """Satu panggilan structured output. Mengembalikan (objek JSON, usage + biaya).

    `images`: URL gambar yang ikut dikirim di pesan user sebagai bagian `input_image`."""
    ok, reason = available(user_id)
    if not ok:
        raise KeyRejected(reason) if reason.startswith("key_rejected") else LLMError(reason)
    p = prices()
    schema_text = json.dumps(schema)
    images = [u for u in (images or []) if u]
    est_input = (len(system) + len(user) + len(schema_text)) / 2 + IMAGE_RESERVE_TOKENS * len(images)
    reserve = _cost(int(est_input), 0, max_output_tokens, p)
    row_id = _reserve(purpose, user_id, ref, reserve, p, db_path)
    started = time.perf_counter()
    effort = reasoning or settings.env("DECIQO_LLM_REASONING", "low")
    user_content: str | list = user
    if images:
        user_content = [{"type": "input_text", "text": user},
                        *({"type": "input_image", "image_url": url, "detail": image_detail} for url in images)]
    try:
        response = _get_client().responses.create(
            model=model_name(),
            input=[{"role": "system", "content": system}, {"role": "user", "content": user_content}],
            text={"format": {"type": "json_schema", "name": schema_name, "schema": schema, "strict": True}},
            reasoning={"effort": effort},
            max_output_tokens=max_output_tokens,
            # Teks ulasan (sudah diredaksi) tidak disimpan di sisi OpenAI; kita tidak memakai previous_response_id.
            store=False,
        )
    except Exception as exc:  # noqa: BLE001 - setiap kegagalan dicatat lalu diteruskan dengan jenisnya
        latency = int((time.perf_counter() - started) * 1000)
        rejection = _is_key_rejection(exc)
        _settle(row_id, f"unknown:{type(exc).__name__}", None, latency, p, db_path)
        if rejection:
            _mark_rejected(rejection, db_path)
            raise KeyRejected(rejection) from exc
        if images and type(exc).__name__ == "BadRequestError":
            raise ImageUnreadable("BadRequestError") from exc
        raise LLMError(f"{type(exc).__name__}") from exc
    latency = int((time.perf_counter() - started) * 1000)
    usage = _usage_of(response)
    status = getattr(response, "status", "completed")
    if status != "completed":
        detail = getattr(getattr(response, "incomplete_details", None), "reason", None) or status
        _settle(row_id, f"incomplete:{detail}", usage, latency, p, db_path)
        raise LLMError(f"incomplete response ({detail})")
    try:
        data = json.loads(getattr(response, "output_text", "") or "")
    except ValueError as exc:
        _settle(row_id, "invalid_json", usage, latency, p, db_path)
        raise LLMError("invalid json in response") from exc
    cost = _settle(row_id, "ok", usage, latency, p, db_path)
    return data, {**(usage or {}), "cost_usd": cost, "latency_ms": latency, "calls": 1}


def add_usage(total: dict, part: dict) -> dict:
    for key in ("input_tokens", "cached_tokens", "output_tokens", "calls", "latency_ms"):
        total[key] = total.get(key, 0) + part.get(key, 0)
    total["cost_usd"] = round(total.get("cost_usd", 0.0) + part.get("cost_usd", 0.0), 6)
    return total
