"""Akun dan sesi.

- Password: PBKDF2-SHA256 bergaram, dibandingkan dengan `hmac.compare_digest`.
- Sesi: token acak di cookie HttpOnly SameSite=Lax; yang tersimpan hanya hash SHA-256-nya,
  sehingga salinan basis data tidak bisa dipakai untuk masuk.
- Throttle login gagal per email di memori (satu proses API).
"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from . import settings, store
from .errors import DeciqoError, unauthorized

COOKIE_NAME = "deciqo_session"
SESSION_DAYS = 7
PBKDF2_ITERATIONS = 200_000
MIN_PASSWORD = 8
KNOWN_CHANNELS = {"woocommerce", "lazada", "tokopedia", "shopee", "tiktok", "blibli", "manual"}

# Lima kegagalan dalam 15 menit mengunci email itu sementara. Disimpan di memori: restart
# melepas kunci, dan itu dapat diterima untuk satu proses tanpa layanan eksternal.
THROTTLE_MAX = 5
THROTTLE_WINDOW = 15 * 60
_failures: dict[str, list[float]] = {}
_failures_lock = threading.Lock()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# --- password & token -------------------------------------------------------------------


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations, salt_hex, hash_hex = stored.split("$")
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
    )
    return hmac.compare_digest(derived.hex(), hash_hex)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# --- bentuk user untuk klien ------------------------------------------------------------


def public_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "is_demo": bool(user["is_demo"]),
        "phone": user.get("phone") or "",
        "channels": store.loads(user.get("channels_json"), []),
        "lang": user.get("lang") or "en",
        "telegram_linked": bool(user.get("telegram_chat_id")),
    }


def get_user(conn, user_id: int) -> dict | None:
    return store.row(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)))


def create_user(conn, email: str, password: str, name: str, is_demo: bool = False,
                channels: list[str] | None = None) -> dict:
    cur = conn.execute(
        "INSERT INTO users(email, name, password_hash, is_demo, channels_json, created_at) "
        "VALUES(?, ?, ?, ?, ?, ?)",
        (email.lower(), name, hash_password(password), int(is_demo),
         store.dumps(channels or []), store.now()),
    )
    return get_user(conn, cur.lastrowid)


def start_session(conn, response: Response, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    conn.execute(
        "INSERT INTO sessions(token_hash, user_id, created_at, expires_at) VALUES(?, ?, ?, ?)",
        (_token_hash(token), user_id, store.now(), expires.replace(microsecond=0).isoformat()),
    )
    response.set_cookie(
        COOKIE_NAME, token, max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax",
        secure=settings.cookie_secure(), path="/",
    )


# --- dependency -------------------------------------------------------------------------


def current_user(request: Request) -> dict:
    """User dari cookie sesi, atau 401. Dipakai semua endpoint workspace."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise unauthorized()
    with store.database() as conn:
        found = store.row(conn.execute(
            "SELECT u.*, s.expires_at AS session_expires FROM sessions s "
            "JOIN users u ON u.id = s.user_id WHERE s.token_hash = ?",
            (_token_hash(token),),
        ))
        if not found:
            raise unauthorized()
        expires = store.parse_time(found.pop("session_expires"))
        if expires is None or expires < datetime.now(timezone.utc):
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(token),))
            raise unauthorized()
    return found


# --- throttle ---------------------------------------------------------------------------


def _throttled(email: str) -> bool:
    cutoff = time.monotonic() - THROTTLE_WINDOW
    with _failures_lock:
        recent = [t for t in _failures.get(email, []) if t > cutoff]
        _failures[email] = recent
        return len(recent) >= THROTTLE_MAX


def _record_failure(email: str) -> None:
    with _failures_lock:
        _failures.setdefault(email, []).append(time.monotonic())


def _clear_failures(email: str) -> None:
    with _failures_lock:
        _failures.pop(email, None)


# --- endpoint ---------------------------------------------------------------------------


class RegisterBody(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=256)
    name: str = Field(default="", max_length=120)


class LoginBody(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=256)


class PatchMeBody(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=32)
    channels: list[str] | None = None
    lang: str | None = Field(default=None, max_length=5)


@router.post("/register", status_code=201)
def register(body: RegisterBody, response: Response) -> dict:
    if not settings.allow_signup():
        raise DeciqoError(403, "signup_closed", "Sign-up is closed on this server.")
    email = body.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise DeciqoError(422, "invalid_email", "Enter a valid email address.")
    if len(body.password) < MIN_PASSWORD:
        raise DeciqoError(422, "weak_password", "Use at least 8 characters.")
    with store.database() as conn:
        if conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            raise DeciqoError(409, "email_taken", "An account with this email already exists.")
        user = create_user(conn, email, body.password, body.name.strip() or email.split("@")[0])
        start_session(conn, response, user["id"])
    return public_user(user)


@router.post("/login")
def login(body: LoginBody, response: Response) -> dict:
    email = body.email.strip().lower()
    if _throttled(email):
        raise DeciqoError(429, "too_many_attempts", "Too many attempts. Try again in 15 minutes.")
    with store.database() as conn:
        user = store.row(conn.execute("SELECT * FROM users WHERE email = ?", (email,)))
        if not user or not verify_password(body.password, user["password_hash"]):
            _record_failure(email)
            raise DeciqoError(401, "bad_credentials", "Email or password is incorrect.")
        _clear_failures(email)
        # Sesi kedaluwarsa dibersihkan sambil lalu; tidak perlu job terpisah.
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (store.now(),))
        start_session(conn, response, user["id"])
    return public_user(user)


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response) -> Response:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        with store.database() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(token),))
    response.status_code = 204
    response.delete_cookie(COOKIE_NAME, path="/")
    return response


@router.get("/me")
def me(user: dict = Depends(current_user)) -> dict:
    return public_user(user)


@router.patch("/me")
def patch_me(body: PatchMeBody, user: dict = Depends(current_user)) -> dict:
    updates: dict[str, object] = {}
    if body.name is not None:
        updates["name"] = body.name.strip()
    if body.phone is not None:
        phone = re.sub(r"[^\d+]", "", body.phone)
        if phone and not re.fullmatch(r"\+?\d{8,15}", phone):
            raise DeciqoError(422, "invalid_phone", "Enter a phone number with 8 to 15 digits.")
        updates["phone"] = phone
    if body.channels is not None:
        unknown = [c for c in body.channels if c not in KNOWN_CHANNELS]
        if unknown:
            raise DeciqoError(422, "unknown_channel", f"Unknown channel: {unknown[0]}.")
        updates["channels_json"] = store.dumps(list(dict.fromkeys(body.channels)))
    if body.lang is not None:
        if body.lang not in {"en", "id"}:
            raise DeciqoError(422, "unknown_language", "Language must be en or id.")
        updates["lang"] = body.lang
    with store.database() as conn:
        if updates:
            assignments = ", ".join(f"{k} = ?" for k in updates)
            conn.execute(f"UPDATE users SET {assignments} WHERE id = ?", (*updates.values(), user["id"]))
        fresh = get_user(conn, user["id"])
    return public_user(fresh)
