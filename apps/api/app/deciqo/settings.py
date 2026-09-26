"""Konfigurasi Deciqo dari environment.

Dibaca lewat fungsi, bukan konstanta modul, supaya tes bisa mengganti env per kasus tanpa
me-reload modul. Tidak ada nilai rahasia di sini; tanpa `.env` sama sekali aplikasi tetap jalan
dalam mode aturan dengan akun demo.
"""

from __future__ import annotations

import os
import re


def env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return default if value is None or value.strip() == "" else value.strip()


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_float(name: str, default: float) -> float:
    try:
        return float(env(name, str(default)))
    except ValueError:
        return default


def env_int(name: str, default: int) -> int:
    try:
        return int(env(name, str(default)))
    except ValueError:
        return default


def demo_email() -> str:
    return env("DECIQO_DEMO_EMAIL", "demo@deciqo.app").lower()


def demo_password() -> str:
    return env("DECIQO_DEMO_PASSWORD", "deciqo-demo")


def allow_signup() -> bool:
    return env_bool("DECIQO_ALLOW_SIGNUP", True)


def cookie_secure() -> bool:
    return env_bool("DECIQO_COOKIE_SECURE", False)


def public_url() -> str:
    return env("DECIQO_PUBLIC_URL", "http://localhost:3000").split("#", 1)[0].rstrip("/")


def woo_base_url() -> str:
    return env("WOO_BASE_URL", "http://woo-demo:8080").rstrip("/")


def woo_demo_mode() -> bool:
    return env_bool("WOO_DEMO_MODE", True)


def woo_page_size() -> int:
    return max(1, min(100, env_int("WOO_PAGE_SIZE", 2)))


# Key dummy yang jelas-jelas publik: toko sintetis hanya meniru autentikasi Woo supaya jalur
# klien yang sama dipakai untuk toko nyata. Tidak membuka apa pun di luar container demo.
DEMO_WOO_KEY = "ck_deciqo_demo_public"
DEMO_WOO_SECRET = "cs_deciqo_demo_public"


def woo_consumer_key() -> str:
    return env("WOO_CONSUMER_KEY", DEMO_WOO_KEY)


def woo_consumer_secret() -> str:
    return env("WOO_CONSUMER_SECRET", DEMO_WOO_SECRET)


def poll_seconds() -> int:
    return env_int("DECIQO_POLL_SECONDS", 900)


def job_workers() -> int:
    return max(1, env_int("DECIQO_JOB_WORKERS", 3))


def telegram_token() -> str:
    return env("TELEGRAM_BOT_TOKEN")


def telegram_demo_mode() -> bool:
    return env_bool("TELEGRAM_DEMO_MODE", True)


def telegram_operator_chats() -> list[str]:
    """Chat ID penerima yang diatur operator server (dipisah koma).

    Hanya menerima alert akun DEMO (data sintetis), supaya demo bisa memperlihatkan pesan
    Telegram sungguhan tanpa pernah mengarahkan data toko akun lain ke chat yang diketik manual."""
    return [c.strip() for c in env("TELEGRAM_CHAT_ID").split(",") if re.fullmatch(r"-?\d{3,20}", c.strip())]


def openai_configured() -> bool:
    return bool(env("OPENAI_API_KEY"))


def llm_model() -> str:
    return env("DECIQO_LLM_MODEL", "gpt-5-mini")


def ai_budget_usd() -> float:
    return env_float("DECIQO_AI_BUDGET_USD", 5.0)


def apify_tokens() -> list[str]:
    return [t.strip() for t in env("APIFY_TOKEN").split(",") if t.strip()]


def apify_budget_usd() -> float:
    return env_float("DECIQO_APIFY_BUDGET_USD", 4.0)


def app_commit() -> str:
    return env("APP_COMMIT", "unknown")[:12]
