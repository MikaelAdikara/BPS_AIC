"""Outbox alert: kapan alert dibuat, isi pesannya, dan status kirimnya.

Aturan:
- Isu baru: dipicu engine (≥3 ulasan pendukung unik dalam 30 hari, atau celah listing berdampak tinggi).
- Muncul lagi: temuan acted/dismissed mendapat keluhan baru yang ditulis setelah tindakan.
  Cooldown 24 jam per temuan.
- Masalah sumber: kredensial dicabut, atau dua kegagalan sinkron beruntun.
- Job selesai/gagal untuk impor, fetch, dan analisis massal.

Dedupe lewat `fingerprint` unik (akun + temuan + jenis + versi bukti). Pengiriman maksimal 8 per
jam per akun; kelebihannya ditunda ke jam berikutnya dan dikirim sebagai satu ringkasan. Retry
maksimal 5 kali. Pesan hanya memuat metadata (produk, atribut, hitungan, tautan), **tidak pernah
teks ulasan**. Data sintetis diawali `[DEMO · data sintetis]` dan dikirim ke sink simulasi.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends

from . import settings, store
from .auth import current_user

log = logging.getLogger("deciqo.alerts")

router = APIRouter(prefix="/api/v1/deciqo", tags=["deciqo-alerts"])

KINDS = ("new_issue", "reopened", "source_problem", "job_done", "job_failed", "digest")
BULK_JOB_KINDS = {"import_analyse", "lazada_fetch", "lazada_snapshot", "analyse_all", "sample"}
MAX_PER_HOUR = 8
MAX_ATTEMPTS = 5
REOPEN_COOLDOWN = timedelta(hours=24)
DISPATCH_INTERVAL = 5

RULES = {
    "new_issue": {"min_support": 3, "window_days": 30, "or_high_impact_listing_gap": True},
    "reopened": {"after_decision": ["acted", "dismissed"], "cooldown_hours": 24},
    "source_problem": {"on_auth_revoked": True, "consecutive_failures": 2},
    "job": {"kinds": sorted(BULK_JOB_KINDS)},
    "delivery": {"max_per_hour": MAX_PER_HOUR, "max_attempts": MAX_ATTEMPTS, "review_text": False},
}

DEMO_PREFIX = "[DEMO · data sintetis] "


def enqueue_event(user_id: int, kind: str, *, finding_id: str | None = None, payload: dict | None = None,
                  synthetic: bool = False, version: str = "", conn=None) -> int | None:
    """Masukkan alert ke outbox. Mengembalikan id, atau None bila duplikat/dalam cooldown.

    `payload` hanya metadata: `product`, `attribute_local`, `count`, `total`, dan opsional
    `channel`, `job_kind`, `code`. Kunci lain yang berisi teks bebas dibuang."""
    if kind not in KINDS:
        raise ValueError(f"unknown alert kind {kind}")
    if conn is None:
        with store.database() as own:
            return enqueue_event(user_id, kind, finding_id=finding_id, payload=payload,
                                 synthetic=synthetic, version=version, conn=own)
    allowed = {"product", "attribute_local", "count", "total", "channel", "job_kind", "code", "product_id",
               "events"}
    clean = {k: v for k, v in (payload or {}).items() if k in allowed}
    if kind == "reopened" and finding_id:
        last = conn.execute(
            "SELECT created_at FROM alert_events WHERE finding_id = ? AND kind = 'reopened' "
            "ORDER BY created_at DESC LIMIT 1", (finding_id,)).fetchone()
        last_at = store.parse_time(last["created_at"]) if last else None
        if last_at and datetime.now(timezone.utc) - last_at < REOPEN_COOLDOWN:
            return None
    fingerprint = store.digest(user_id, finding_id or "", kind, version)
    cur = conn.execute(
        "INSERT OR IGNORE INTO alert_events(user_id, finding_id, kind, fingerprint, payload_json, synthetic, "
        "status, created_at) VALUES(?, ?, ?, ?, ?, ?, 'pending', ?)",
        (user_id, finding_id, kind, fingerprint, store.dumps(clean), int(synthetic), store.now()),
    )
    return cur.lastrowid if cur.rowcount else None


def on_source_problem(user_id: int, channel: str, code: str, consecutive_failures: int, *,
                      synthetic: bool = False) -> None:
    if code != "store_auth_failed" and consecutive_failures < RULES["source_problem"]["consecutive_failures"]:
        return
    # Satu alert per rangkaian kegagalan: versinya hari ini, jadi masalah yang berlanjut besok
    # boleh mengingatkan lagi.
    enqueue_event(user_id, "source_problem", payload={"channel": channel, "code": code},
                  synthetic=synthetic, version=f"{channel}:{code}:{datetime.now(timezone.utc).date()}")


def on_job_finished(user_id: int, job_id: str, kind: str, ok: bool) -> None:
    if kind not in BULK_JOB_KINDS:
        return
    with store.database() as conn:
        synthetic = bool(conn.execute(
            "SELECT 1 FROM users WHERE id = ? AND is_demo = 1", (user_id,)).fetchone())
        enqueue_event(user_id, "job_done" if ok else "job_failed", payload={"job_kind": kind},
                      synthetic=synthetic, version=job_id, conn=conn)


# --- render ---------------------------------------------------------------------------------

_TEXT = {
    "en": {
        "new_issue": "New issue on {product}: {attribute}. At least {count} of {total} reviews read mention it.",
        "reopened": "Came back on {product}: {attribute}. {count} new complaint(s) written after your change.",
        "source_problem": "{channel} could not be synced ({code}). Your saved data is still available.",
        "job_done": "Task finished: {job_kind}.",
        "job_failed": "Task failed: {job_kind}. Open Deciqo to see why.",
        "digest": "{events} more alert(s) this hour. Open Deciqo to see them all.",
        "open": "Open issue",
    },
    "id": {
        "new_issue": "Isu baru di {product}: {attribute}. Setidaknya {count} dari {total} ulasan yang dibaca menyebutnya.",
        "reopened": "Muncul lagi di {product}: {attribute}. {count} keluhan baru ditulis setelah perubahan Anda.",
        "source_problem": "{channel} gagal disinkronkan ({code}). Data tersimpan Anda tetap tersedia.",
        "job_done": "Tugas selesai: {job_kind}.",
        "job_failed": "Tugas gagal: {job_kind}. Buka Deciqo untuk melihat sebabnya.",
        "digest": "{events} alert lain dalam satu jam ini. Buka Deciqo untuk melihat semuanya.",
        "open": "Buka isu",
    },
}


def render(event: dict, lang: str = "en") -> str:
    texts = _TEXT.get(lang, _TEXT["en"])
    payload = store.loads(event.get("payload_json"), {}) if "payload_json" in event else event.get("payload", {})
    values = {
        "product": payload.get("product", "?"), "attribute": payload.get("attribute_local", "?"),
        "count": payload.get("count", "?"), "total": payload.get("total", "?"),
        "channel": payload.get("channel", "?"), "code": payload.get("code", "?"),
        "job_kind": payload.get("job_kind", "?"), "events": payload.get("events", "?"),
    }
    message = texts[event["kind"]].format(**values)
    if event.get("finding_id"):
        message += f"\n{texts['open']}: {settings.public_url()}/#/app/issues?f={event['finding_id']}"
    return (DEMO_PREFIX + message) if event.get("synthetic") else message


def public_event(event: dict, lang: str) -> dict:
    return {
        "id": event["id"], "kind": event["kind"], "status": event["status"], "finding_id": event["finding_id"],
        "synthetic": bool(event["synthetic"]), "payload": store.loads(event["payload_json"], {}),
        "message": render(event, lang), "attempts": event["attempts"],
        "created_at": event["created_at"], "sent_at": event["sent_at"],
    }


@router.get("/alerts")
def list_alerts(user: dict = Depends(current_user)) -> dict:
    with store.database() as conn:
        events = store.rows(conn.execute(
            "SELECT * FROM alert_events WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT 100",
            (user["id"],)))
    return {
        "events": [public_event(e, user.get("lang") or "en") for e in events],
        "rules": RULES,
        "telegram": {"linked": bool(user.get("telegram_chat_id")), "bot_configured": bool(settings.telegram_token()),
                     "demo_sink": settings.telegram_demo_mode()},
    }


# --- pengiriman --------------------------------------------------------------------------------


def _send_telegram(base: str, token: str, chat_id: str, text: str, finding_id: str | None) -> dict:
    body: dict = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if finding_id and settings.public_url().startswith("https://"):
        # Telegram menolak tombol URL non-HTTPS; di lokal tautannya tetap ada di teks pesan.
        body["reply_markup"] = {"inline_keyboard": [[{
            "text": "Buka isu", "url": f"{settings.public_url()}/#/app/issues?f={finding_id}"}]]}
    response = httpx.post(f"{base}/bot{token}/sendMessage", json=body, timeout=10.0)
    data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
    if response.status_code >= 400 or not data.get("ok", False):
        raise RuntimeError(f"telegram http {response.status_code}")
    return {"message_id": (data.get("result") or {}).get("message_id")}


def dispatch_once(now: datetime | None = None) -> int:
    """Kirim alert yang tertunda. Mengembalikan jumlah yang diproses."""
    now = now or datetime.now(timezone.utc)
    hour_ago = (now - timedelta(hours=1)).replace(microsecond=0).isoformat()
    processed = 0
    with store.database() as conn:
        pending = store.rows(conn.execute(
            "SELECT e.*, u.telegram_chat_id, u.lang FROM alert_events e JOIN users u ON u.id = e.user_id "
            "WHERE e.status = 'pending' AND (e.next_attempt_at IS NULL OR e.next_attempt_at <= ?) "
            "ORDER BY e.id LIMIT 50", (now.replace(microsecond=0).isoformat(),)))
    for event in pending:
        with store.database() as conn:
            sent_last_hour = conn.execute(
                "SELECT COUNT(*) FROM alert_events WHERE user_id = ? AND status IN ('sent', 'simulated') "
                "AND sent_at >= ?", (event["user_id"], hour_ago)).fetchone()[0]
        if sent_last_hour >= MAX_PER_HOUR:
            _defer_to_digest(event, now)
            continue
        processed += 1
        _deliver(event, now)
    return processed


def _defer_to_digest(event: dict, now: datetime) -> None:
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    with store.database() as conn:
        conn.execute("UPDATE alert_events SET status = 'digested', delivery_json = ? WHERE id = ?",
                     (store.dumps({"deferred": "rate_limit"}), event["id"]))
        waiting = conn.execute(
            "SELECT COUNT(*) FROM alert_events WHERE user_id = ? AND delivery_json LIKE '%rate_limit%' "
            "AND created_at >= ?", (event["user_id"], (now - timedelta(hours=1)).isoformat())).fetchone()[0]
        enqueue_event(event["user_id"], "digest", payload={"events": waiting}, synthetic=bool(event["synthetic"]),
                      version=next_hour.isoformat(), conn=conn)
        conn.execute("UPDATE alert_events SET next_attempt_at = ?, payload_json = ? WHERE kind = 'digest' "
                     "AND user_id = ? AND status = 'pending'",
                     (next_hour.isoformat(), store.dumps({"events": waiting}), event["user_id"]))


def _deliver(event: dict, now: datetime) -> None:
    token = settings.telegram_token()
    text = render(event, event.get("lang") or "en")
    status, delivery = "unconfigured", {}
    try:
        if event["synthetic"] and settings.telegram_demo_mode():
            # Data sintetis tidak pernah ke chat nyata: ke sink simulasi di toko demo.
            delivery = _send_telegram(settings.woo_base_url(), token or "demo", event.get("telegram_chat_id") or "demo",
                                      text, event["finding_id"])
            status = "simulated"
        elif token and event.get("telegram_chat_id"):
            delivery = _send_telegram("https://api.telegram.org", token, event["telegram_chat_id"], text,
                                      event["finding_id"])
            status = "sent"
        else:
            delivery = {"reason": "bot_not_configured" if not token else "telegram_not_linked"}
    except Exception as exc:  # noqa: BLE001
        attempts = event["attempts"] + 1
        final = attempts >= MAX_ATTEMPTS
        backoff = now + timedelta(seconds=30 * (2 ** attempts))
        with store.database() as conn:
            conn.execute(
                "UPDATE alert_events SET status = ?, attempts = ?, next_attempt_at = ?, delivery_json = ? WHERE id = ?",
                ("permanent_failure" if final else "pending", attempts, backoff.replace(microsecond=0).isoformat(),
                 store.dumps({"error": type(exc).__name__}), event["id"]))
        log.warning(f"alert {event['id']} gagal dikirim (percobaan {attempts}): {type(exc).__name__}")
        return
    with store.database() as conn:
        conn.execute(
            "UPDATE alert_events SET status = ?, attempts = attempts + 1, sent_at = ?, delivery_json = ? WHERE id = ?",
            (status, store.now() if status in ("sent", "simulated") else None, store.dumps(delivery), event["id"]))


_dispatcher_started = threading.Event()


def start_dispatcher() -> None:
    if _dispatcher_started.is_set():
        return
    _dispatcher_started.set()

    def loop():
        while True:
            try:
                dispatch_once()
            except Exception as exc:  # noqa: BLE001
                log.error(f"dispatcher alert gagal: {type(exc).__name__}")
            time.sleep(DISPATCH_INTERVAL)

    threading.Thread(target=loop, name="alert-dispatcher", daemon=True).start()
