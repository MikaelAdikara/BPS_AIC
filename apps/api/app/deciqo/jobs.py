"""Job latar yang statusnya tersimpan di basis data.

- Pool thread terbatas (`DECIQO_JOB_WORKERS`, default 3); maksimal 2 job aktif per akun.
- Dedupe per kunci (akun + jenis + target): permintaan kembar mengembalikan job yang sama.
- Saat startup, job `queued`/`running` dari proses sebelumnya ditandai `interrupted`, sehingga UI
  tidak mem-poll job yang tidak akan pernah selesai.
- Error yang disimpan hanya nama jenis kegagalan + pesan pendek, tanpa stack trace.
"""

from __future__ import annotations

import logging
import secrets
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from . import settings, store
from .errors import DeciqoError, not_found

log = logging.getLogger("deciqo.jobs")

MAX_ACTIVE_PER_USER = 2
ACTIVE = ("queued", "running")

# Analisis diserialkan: model triage dan reservasi anggaran AI dipakai bersama.
ANALYSIS_LOCK = threading.Lock()

_executor: ThreadPoolExecutor | None = None
_executor_lock = threading.Lock()
_submit_lock = threading.Lock()


class JobFailed(Exception):
    """Kegagalan yang pesannya aman ditampilkan ke merchant (kode + kalimat)."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class JobContext:
    def __init__(self, job_id: str, user_id: int):
        self.id = job_id
        self.user_id = user_id
        self._detail: dict[str, Any] = {}

    def progress(self, index: int | None = None, total: int | None = None,
                 stage: str | None = None, **extra: Any) -> None:
        if index is not None:
            self._detail["index"] = index
        if total is not None:
            self._detail["total"] = total
        if stage is not None:
            self._detail["stage"] = stage
        self._detail.update(extra)
        with store.database() as conn:
            conn.execute(
                "UPDATE jobs SET detail_json = ?, updated_at = ? WHERE id = ?",
                (store.dumps(self._detail), store.now(), self.id),
            )


def _pool() -> ThreadPoolExecutor:
    global _executor
    with _executor_lock:
        if _executor is None:
            _executor = ThreadPoolExecutor(max_workers=settings.job_workers(), thread_name_prefix="job")
        return _executor


def public_job(job: dict) -> dict:
    return {
        "id": job["id"],
        "kind": job["kind"],
        "status": job["status"],
        "detail": store.loads(job.get("detail_json"), {}),
        "error": store.loads(job.get("error"), None) if job.get("error") else None,
        "result": store.loads(job.get("result_json"), None),
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
    }


def start(user_id: int, kind: str, fn: Callable[[JobContext], dict | None], *,
          target: str = "", detail: dict | None = None, run_inline: bool = False) -> str:
    """Daftarkan job dan jalankan di pool. Mengembalikan id job.

    `run_inline=True` menjalankan di thread pemanggil (dipakai seed saat startup dan tes)."""
    dedupe_key = f"{user_id}:{kind}:{target}"
    with _submit_lock, store.database() as conn:
        same = store.row(conn.execute(
            "SELECT id FROM jobs WHERE dedupe_key = ? AND status IN ('queued', 'running')", (dedupe_key,)))
        if same:
            return same["id"]
        active = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE user_id = ? AND status IN ('queued', 'running')",
            (user_id,)).fetchone()[0]
        if active >= MAX_ACTIVE_PER_USER and not run_inline:
            raise DeciqoError(429, "workspace_busy",
                              "Two tasks are already running for this workspace. Try again when one finishes.")
        job_id = "j_" + secrets.token_hex(6)
        now = store.now()
        conn.execute(
            "INSERT INTO jobs(id, user_id, kind, status, dedupe_key, detail_json, created_at, updated_at) "
            "VALUES(?, ?, ?, 'queued', ?, ?, ?, ?)",
            (job_id, user_id, kind, dedupe_key, store.dumps(detail or {}), now, now),
        )
    if run_inline:
        _run(job_id, user_id, kind, fn)
    else:
        _pool().submit(_run, job_id, user_id, kind, fn)
    return job_id


def _finish(job_id: str, status: str, *, result: dict | None = None, error: dict | None = None) -> None:
    with store.database() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, result_json = ?, error = ?, updated_at = ? WHERE id = ?",
            (status, store.dumps(result) if result is not None else None,
             store.dumps(error) if error else None, store.now(), job_id),
        )


def _run(job_id: str, user_id: int, kind: str, fn: Callable[[JobContext], dict | None]) -> None:
    ctx = JobContext(job_id, user_id)
    with store.database() as conn:
        conn.execute("UPDATE jobs SET status = 'running', updated_at = ? WHERE id = ?", (store.now(), job_id))
    try:
        result = fn(ctx) or {}
    except JobFailed as exc:
        _finish(job_id, "failed", error={"code": exc.code, "message": exc.message})
        _notify(user_id, job_id, kind, ok=False)
        return
    except Exception as exc:  # noqa: BLE001 - job tidak boleh mematikan worker
        log.error(f"job {kind} {job_id} gagal: {type(exc).__name__}: {str(exc)[:200]}")
        _finish(job_id, "failed", error={"code": "job_failed",
                                          "message": "The task stopped because of a server error."})
        _notify(user_id, job_id, kind, ok=False)
        return
    _finish(job_id, "done", result=result)
    _notify(user_id, job_id, kind, ok=True)


def _notify(user_id: int, job_id: str, kind: str, ok: bool) -> None:
    try:
        from . import alerts  # noqa: PLC0415

        hook = getattr(alerts, "on_job_finished", None)
        if hook:
            hook(user_id, job_id, kind, ok)
    except Exception as exc:  # noqa: BLE001
        log.error(f"alert job gagal dibuat: {type(exc).__name__}")


def get(user_id: int, job_id: str) -> dict:
    with store.database() as conn:
        job = store.row(conn.execute("SELECT * FROM jobs WHERE id = ? AND user_id = ?", (job_id, user_id)))
    if not job:
        raise not_found("task")
    return public_job(job)


def active_for(user_id: int) -> list[dict]:
    with store.database() as conn:
        found = store.rows(conn.execute(
            "SELECT * FROM jobs WHERE user_id = ? AND status IN ('queued', 'running') ORDER BY created_at",
            (user_id,)))
    return [public_job(j) for j in found]


def recover() -> int:
    """Tandai job yang terputus oleh restart. Dipanggil sekali saat startup."""
    with store.database() as conn:
        cur = conn.execute(
            "UPDATE jobs SET status = 'interrupted', error = ?, updated_at = ? "
            "WHERE status IN ('queued', 'running')",
            (store.dumps({"code": "interrupted", "message": "The server restarted while this task was running."}),
             store.now()),
        )
        return cur.rowcount
