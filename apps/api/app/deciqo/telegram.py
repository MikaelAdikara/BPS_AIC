"""Bot Telegram: tautan akun, perintah, dan pengiriman alert.

- Long polling (`getUpdates`), bukan webhook: tidak butuh URL publik, jalan dari laptop mana pun.
- Chat ID tidak pernah diketik manual (alert bisa diarahkan ke chat orang lain). Akun ditautkan
  lewat `/start <kode>` dengan kode sekali pakai 15 menit, atau dengan membagikan kontak SENDIRI
  yang nomornya cocok dengan nomor di akun; kontak terusan ditolak.
- Jawaban perintah hanya memuat nama produk dan hitungan, tidak pernah teks ulasan.
"""

from __future__ import annotations

import logging
import re
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, Response

from . import settings, store
from .auth import current_user

log = logging.getLogger("deciqo.telegram")

router = APIRouter(prefix="/api/v1/deciqo", tags=["deciqo-telegram"])

API = "https://api.telegram.org"
LINK_MINUTES = 15
POLL_TIMEOUT = 25
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # tanpa 0/O/1/I agar mudah diketik
_CODE_RE = re.compile(r"^[A-Z2-9]{6}$")
_bot_username: dict[str, str] = {}

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


# --- panggilan Bot API ---------------------------------------------------------------------


def _call(method: str, payload: dict | None = None, timeout: float = 10.0) -> dict:
    token = settings.telegram_token()
    if not token:
        raise RuntimeError("bot_not_configured")
    response = httpx.post(f"{API}/bot{token}/{method}", json=payload or {}, timeout=timeout)
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"telegram {method} {response.status_code}: {data.get('description', '')[:80]}")
    return data.get("result")


def bot_username() -> str | None:
    token = settings.telegram_token()
    if not token:
        return None
    if token not in _bot_username:
        try:
            _bot_username[token] = _call("getMe")["username"]
        except Exception as exc:  # noqa: BLE001
            log.warning(f"getMe gagal: {type(exc).__name__}")
            return None
    return _bot_username[token]


def send(chat_id: str | int, text: str, *, keyboard: dict | None = None) -> dict:
    body: dict = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if keyboard:
        body["reply_markup"] = keyboard
    return _call("sendMessage", body)


# --- endpoint --------------------------------------------------------------------------------


@router.post("/telegram/link")
def create_link(user: dict = Depends(current_user)) -> dict:
    code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(6))
    expires = (datetime.now(timezone.utc) + timedelta(minutes=LINK_MINUTES)).replace(microsecond=0)
    with store.database() as conn:
        conn.execute("DELETE FROM telegram_links WHERE user_id = ? OR expires_at < ?", (user["id"], store.now()))
        conn.execute("INSERT INTO telegram_links(code, user_id, expires_at) VALUES(?, ?, ?)",
                     (code, user["id"], expires.isoformat()))
    username = bot_username()
    return {
        "code": code,
        "deep_link": f"https://t.me/{username}?start={code}" if username else None,
        "bot_username": username,
        "bot_configured": bool(settings.telegram_token()),
        "expires_at": expires.isoformat(),
    }


@router.delete("/telegram/link", status_code=204)
def unlink(user: dict = Depends(current_user)) -> Response:
    with store.database() as conn:
        conn.execute("UPDATE users SET telegram_chat_id = NULL WHERE id = ?", (user["id"],))
        conn.execute("DELETE FROM telegram_links WHERE user_id = ?", (user["id"],))
    return Response(status_code=204)


@router.post("/telegram/test")
def test_message(user: dict = Depends(current_user)) -> dict:
    if not settings.telegram_token() or not user.get("telegram_chat_id"):
        return {"status": "unconfigured",
                "reason": "bot_not_configured" if not settings.telegram_token() else "telegram_not_linked"}
    lang = user.get("lang") or "en"
    text = ("Deciqo test message. Alerts for this workspace will arrive here." if lang == "en"
            else "Pesan uji Deciqo. Alert untuk workspace ini akan masuk ke sini.")
    try:
        send(user["telegram_chat_id"], text)
    except Exception as exc:  # noqa: BLE001
        log.warning(f"pesan uji gagal: {type(exc).__name__}")
        return {"status": "failed"}
    return {"status": "sent"}


# --- tautan akun -----------------------------------------------------------------------------


def redeem_code(conn, code: str, chat_id: str) -> dict | None:
    """Tukar kode sekali pakai dengan tautan chat. None bila kode salah atau kedaluwarsa."""
    code = code.strip().upper()
    if not _CODE_RE.match(code):
        return None
    link = store.row(conn.execute("SELECT * FROM telegram_links WHERE code = ?", (code,)))
    conn.execute("DELETE FROM telegram_links WHERE code = ?", (code,))
    if not link or (store.parse_time(link["expires_at"]) or datetime.min.replace(tzinfo=timezone.utc)) < datetime.now(timezone.utc):
        return None
    # Satu chat hanya untuk satu akun: tautan lama ke chat ini dilepas.
    conn.execute("UPDATE users SET telegram_chat_id = NULL WHERE telegram_chat_id = ?", (chat_id,))
    conn.execute("UPDATE users SET telegram_chat_id = ? WHERE id = ?", (chat_id, link["user_id"]))
    return store.row(conn.execute("SELECT * FROM users WHERE id = ?", (link["user_id"],)))


def _digits(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    return "62" + digits[1:] if digits.startswith("0") else digits


def link_by_contact(conn, message: dict) -> dict | None:
    contact = message.get("contact") or {}
    sender = (message.get("from") or {}).get("id")
    # Kontak terusan/milik orang lain: user_id kontak tidak sama dengan pengirim.
    if not contact or contact.get("user_id") != sender:
        return None
    phone = _digits(contact.get("phone_number", ""))
    if len(phone) < 8:
        return None
    for user in store.rows(conn.execute("SELECT * FROM users WHERE phone != ''")):
        if _digits(user["phone"]) == phone:
            chat_id = str(message["chat"]["id"])
            conn.execute("UPDATE users SET telegram_chat_id = NULL WHERE telegram_chat_id = ?", (chat_id,))
            conn.execute("UPDATE users SET telegram_chat_id = ? WHERE id = ?", (chat_id, user["id"]))
            return user
    return None


# --- perintah --------------------------------------------------------------------------------

_T = {
    "en": {
        "linked": "Linked to Deciqo workspace of {name}. Alerts will arrive here. Type /help for commands.",
        "bad_code": "That code is not valid or has expired. Create a new one in Deciqo → Settings → Telegram.",
        "not_linked": "This chat is not linked yet. In Deciqo open Settings → Connect Telegram, then send the code here.",
        "help": "/status summary · /issues top issues · /analyse analyse changed products · /unlink stop alerts · /help",
        "status": "{products} products · {reviews} reviews · {open} active issues ({needs_fact} need your fact, {came_back} came back).",
        "no_issues": "No active issues right now.",
        "issue": "{i}. {product}: {attribute} — at least {support} of {denominator} reviews read",
        "analysing": "Analysis started for {n} changed product(s). You will get an alert if something new comes up.",
        "nothing": "Nothing changed since the last analysis.",
        "unlinked": "Unlinked. This chat will no longer receive alerts.",
        "contact_bad": "Share your own contact with the same phone number saved in Deciqo, or use the link code.",
        "open": "Open Deciqo",
    },
    "id": {
        "linked": "Terhubung ke workspace Deciqo milik {name}. Alert akan masuk ke sini. Ketik /bantuan untuk perintah.",
        "bad_code": "Kode tidak valid atau sudah kedaluwarsa. Buat kode baru di Deciqo → Pengaturan → Telegram.",
        "not_linked": "Chat ini belum terhubung. Di Deciqo buka Pengaturan → Hubungkan Telegram, lalu kirim kodenya ke sini.",
        "help": "/status ringkasan · /isu isu teratas · /analisis analisis produk yang berubah · /putus hentikan alert · /bantuan",
        "status": "{products} produk · {reviews} ulasan · {open} isu aktif ({needs_fact} perlu fakta Anda, {came_back} muncul lagi).",
        "no_issues": "Tidak ada isu aktif saat ini.",
        "issue": "{i}. {product}: {attribute} — setidaknya {support} dari {denominator} ulasan yang dibaca",
        "analysing": "Analisis dimulai untuk {n} produk yang berubah. Anda akan mendapat alert bila ada hal baru.",
        "nothing": "Tidak ada yang berubah sejak analisis terakhir.",
        "unlinked": "Tautan diputus. Chat ini tidak akan menerima alert lagi.",
        "contact_bad": "Bagikan kontak Anda sendiri dengan nomor yang sama seperti di Deciqo, atau pakai kode tautan.",
        "open": "Buka Deciqo",
    },
}

COMMANDS = {
    "/status": "status", "/isu": "issues", "/issues": "issues", "/analisis": "analyse", "/analyse": "analyse",
    "/putus": "unlink", "/unlink": "unlink", "/bantuan": "help", "/help": "help",
}


def _lang(user: dict | None, message: dict) -> str:
    if user and user.get("lang") in _T:
        return user["lang"]
    return "id" if ((message.get("from") or {}).get("language_code") or "").startswith("id") else "en"


def _status_text(conn, user: dict, t: dict) -> str:
    uid = user["id"]
    products = conn.execute("SELECT COUNT(*) FROM products WHERE user_id = ?", (uid,)).fetchone()[0]
    reviews = conn.execute("SELECT COUNT(*) FROM reviews r JOIN products p ON p.id = r.product_id "
                           "WHERE p.user_id = ? AND r.deleted_at IS NULL", (uid,)).fetchone()[0]
    rows = store.rows(conn.execute(
        "SELECT f.state, f.id FROM findings f JOIN products p ON p.id = f.product_id "
        "WHERE p.user_id = ? AND f.state IN ('open', 'investigating', 'reopened') AND f.not_detected_at IS NULL",
        (uid,)))
    needs_fact = sum(1 for r in rows if r["state"] == "open" and not conn.execute(
        "SELECT 1 FROM facts WHERE finding_id = ? AND active = 1", (r["id"],)).fetchone())
    came_back = sum(1 for r in rows if r["state"] == "reopened")
    return t["status"].format(products=products, reviews=reviews, open=len(rows),
                              needs_fact=needs_fact, came_back=came_back)


def _issues_text(conn, user: dict, t: dict) -> str:
    rows = store.rows(conn.execute(
        "SELECT f.attribute_local, f.attribute, f.severity, f.support, f.denominator, f.state, p.title "
        "FROM findings f JOIN products p ON p.id = f.product_id WHERE p.user_id = ? "
        "AND f.state IN ('open', 'investigating', 'reopened') AND f.not_detected_at IS NULL", (user["id"],)))
    if not rows:
        return t["no_issues"]
    rows.sort(key=lambda r: (r["state"] != "reopened", SEVERITY_ORDER.get(r["severity"], 3), -r["support"]))
    lines = [t["issue"].format(i=i, product=r["title"], attribute=r["attribute_local"] or r["attribute"],
                               support=r["support"], denominator=r["denominator"])
             for i, r in enumerate(rows[:5], start=1)]
    return "\n".join(lines)


def _start_analysis(user: dict, t: dict) -> str:
    from . import analysis, jobs  # noqa: PLC0415
    from .errors import DeciqoError  # noqa: PLC0415

    with store.database() as conn:
        changed = [r["id"] for r in conn.execute(
            "SELECT p.id FROM products p LEFT JOIN analyses a ON a.product_id = p.id "
            "WHERE p.user_id = ? AND (a.product_id IS NULL OR a.created_at < p.updated_at "
            "OR EXISTS (SELECT 1 FROM reviews r WHERE r.product_id = p.id AND r.fetched_at > a.created_at "
            "AND r.triage_json IS NULL))", (user["id"],))]
    if not changed:
        return t["nothing"]
    try:
        jobs.start(user["id"], "analyse_all", lambda ctx: analysis.analyse_products(ctx, changed), target="all")
    except DeciqoError as exc:
        return exc.detail["message"]
    return t["analysing"].format(n=len(changed))


def handle_update(update: dict) -> str | None:
    """Proses satu update. Mengembalikan teks balasan (dikirim pemanggil), atau None."""
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    if not chat or chat.get("type") != "private":
        return None
    chat_id = str(chat["id"])
    text = (message.get("text") or "").strip()
    with store.database() as conn:
        user = store.row(conn.execute("SELECT * FROM users WHERE telegram_chat_id = ?", (chat_id,)))
        t = _T[_lang(user, message)]
        if message.get("contact"):
            linked = link_by_contact(conn, message)
            return t["linked"].format(name=linked["name"]) if linked else t["contact_bad"]
        first, _, rest = text.partition(" ")
        command = first.split("@")[0].lower()
        if command == "/start" and rest.strip():
            linked = redeem_code(conn, rest, chat_id)
            return _T[_lang(linked, message)]["linked"].format(name=linked["name"]) if linked else t["bad_code"]
        if not command.startswith("/") and _CODE_RE.match(text.upper()):
            linked = redeem_code(conn, text, chat_id)
            return _T[_lang(linked, message)]["linked"].format(name=linked["name"]) if linked else t["bad_code"]
        if user is None:
            return t["not_linked"]
        action = COMMANDS.get(command, "help")
        if action == "status":
            return _status_text(conn, user, t)
        if action == "issues":
            return _issues_text(conn, user, t)
        if action == "unlink":
            conn.execute("UPDATE users SET telegram_chat_id = NULL WHERE id = ?", (user["id"],))
            return t["unlinked"]
        if action == "help":
            return t["help"]
    return _start_analysis(user, t)


# --- polling ---------------------------------------------------------------------------------

_poller_started = threading.Event()


def poll_once(timeout: int = POLL_TIMEOUT) -> int:
    with store.database() as conn:
        offset = int(store.get_kv(conn, "telegram_offset", "0") or 0)
    updates = _call("getUpdates", {"offset": offset, "timeout": timeout, "allowed_updates": ["message"]},
                    timeout=timeout + 10)
    for update in updates:
        try:
            reply = handle_update(update)
            if reply:
                send(update["message"]["chat"]["id"], reply)
        except Exception as exc:  # noqa: BLE001 - satu update rusak tidak menghentikan polling
            log.warning(f"update telegram gagal diproses: {type(exc).__name__}")
        with store.database() as conn:
            store.set_kv(conn, "telegram_offset", str(update["update_id"] + 1))
    return len(updates)


def start_polling() -> None:
    if _poller_started.is_set() or not settings.telegram_token():
        return
    _poller_started.set()

    def loop():
        failures = 0
        while True:
            try:
                poll_once()
                failures = 0
            except Exception as exc:  # noqa: BLE001
                failures += 1
                # 409 = proses lain memakai token yang sama untuk polling (mis. laptop anggota lain).
                log.warning(f"polling telegram gagal ({failures}x): {str(exc)[:120]}")
                time.sleep(min(60, 5 * failures))

    threading.Thread(target=loop, name="telegram-poller", daemon=True).start()
