"""Pemeriksaan ulang startup berjalan di latar dan berbagi lock dengan job."""
import threading

from app.deciqo import jobs, store
from app.deciqo.engine import pipeline


def test_startup_recheck_runs_in_background_under_analysis_lock(tmp_path, monkeypatch):
    monkeypatch.setenv("DECIQO_DB_PATH", str(tmp_path / "startup.sqlite3"))
    store.migrate()
    pending = []
    observed = []

    class DeferredThread:
        def __init__(self, *, target, name, daemon):
            assert name == "engine-recheck"
            assert daemon
            self.target = target

        def start(self):
            pending.append(self.target)

    lock = threading.Lock()
    monkeypatch.setattr(jobs, "ANALYSIS_LOCK", lock)
    monkeypatch.setattr(threading, "Thread", DeferredThread)
    monkeypatch.setattr(pipeline, "recheck_stale", lambda: observed.append(lock.locked()))
    pipeline.on_startup()
    assert observed == []
    assert len(pending) == 1
    pending[0]()
    assert observed == [True]
    assert not lock.locked()
