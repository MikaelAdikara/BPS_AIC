"""Runner eval: B0 dan B1 (prompt ke model yang sama) lawan Deciqo (D, D-rules).

Contoh:
    python eval/run_final.py --rules                       # D mode aturan saja, gratis
    python eval/run_final.py --systems B0,B1 --budget 2    # baseline berbayar, batas keras USD
    python eval/run_final.py --rescore                     # hitung ulang report dari outputs.jsonl
    python eval/run_final.py --cases "c0*" --systems D --budget 1

Setiap (kasus, fase, sistem) menulis satu baris ke outputs.jsonl: teks mentah, status, durasi,
token, biaya, error. Run yang menjalankan sebagian kasus mengganti baris yang sama saja; baris lain
dipertahankan. Key API tidak pernah ditulis ke berkas mana pun.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import deciqo_adapter  # noqa: E402
import scoring  # noqa: E402
from prompts import PROMPTS, bundle_text, prompt_sha  # noqa: E402

CASES_DIR = HERE / "final"
OUT = CASES_DIR  # bisa diganti --out; kasus selalu dibaca dari CASES_DIR
CASE_FILES = ["cases.jsonl", "cases_holdout.jsonl"]
ALL_SYSTEMS = ["B0", "B1", "D", "D-rules"]
PAID = {"B0", "B1", "D"}

# Harga per juta token (gpt-5-mini, tarif publik); bisa ditimpa env seperti engine.
PRICE_IN = float(os.environ.get("DECIQO_PRICE_INPUT_PER_M", "0.25"))
PRICE_CACHED = float(os.environ.get("DECIQO_PRICE_CACHED_PER_M", "0.025"))
PRICE_OUT = float(os.environ.get("DECIQO_PRICE_OUTPUT_PER_M", "2.00"))
MAX_OUTPUT_TOKENS = 8000
REASONING_EFFORT = "low"


class KeyRejected(RuntimeError):
    """Key ditolak/kuota habis: run berhenti, bukan lanjut dengan hasil kosong."""


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    def __init__(self, limit: float):
        self.limit = limit
        self.spent = 0.0
        self.reserved = 0.0
        self.lock = threading.Lock()

    def reserve(self, amount: float) -> None:
        with self.lock:
            if self.spent + self.reserved + amount > self.limit:
                raise BudgetExceeded(
                    f"reservasi {amount:.4f} melampaui sisa anggaran "
                    f"{self.limit - self.spent - self.reserved:.4f} USD")
            self.reserved += amount

    def settle(self, reserved: float, actual: float) -> None:
        with self.lock:
            self.reserved -= reserved
            self.spent += actual


def load_env_file() -> None:
    """Muat .env di root repo (tidak di-commit) tanpa menimpa env yang sudah ada."""
    path = REPO / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and v and k not in os.environ:
                os.environ[k] = v


def git_commit() -> dict:
    def run(*args):
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()
    return {"commit": run("rev-parse", "HEAD"), "short": run("rev-parse", "--short", "HEAD"),
            "dirty_files": [l[3:] for l in run("status", "--porcelain").splitlines() if l]}


def load_cases(pattern: str | None, include_holdout: bool = True) -> list[dict]:
    rows = []
    for name in CASE_FILES:
        path = CASES_DIR / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    if not include_holdout:
        rows = [c for c in rows if c["status"] != "holdout"]
    if pattern:
        pats = [p.strip() for p in pattern.split(",") if p.strip()]
        rows = [c for c in rows if any(fnmatch.fnmatch(c["id"], p) for p in pats)]
    return rows


def phases_for(case: dict) -> list[str]:
    return ["before", "after"] if case.get("fact") else ["before"]


# ---------------------------------------------------------------------------- baseline B0/B1

def _cost(inp: int, cached: int, out: int) -> float:
    return ((inp - cached) * PRICE_IN + cached * PRICE_CACHED + out * PRICE_OUT) / 1e6


def call_baseline(client, model: str, system: str, case: dict, phase: str, budget: Budget) -> dict:
    import openai

    prompt = PROMPTS[system]
    user = bundle_text(case, phase)
    # Reservasi terburuk: ±2 karakter per token untuk input, output penuh.
    reserve = _cost((len(prompt) + len(user)) // 2 + 50, 0, MAX_OUTPUT_TOKENS)
    budget.reserve(reserve)
    t0 = time.perf_counter()
    row = {"status": "error", "text": "", "usage": {}, "cost_usd": reserve, "cost_kind": "reserved_unknown"}
    try:
        resp = client.responses.create(
            model=model,
            instructions=prompt,
            input=user,
            reasoning={"effort": REASONING_EFFORT},
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )
        u = resp.usage
        inp = getattr(u, "input_tokens", 0) or 0
        cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        out = getattr(u, "output_tokens", 0) or 0
        reasoning = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0
        row["usage"] = {"input_tokens": inp, "cached_tokens": cached, "output_tokens": out,
                        "reasoning_tokens": reasoning}
        row["cost_usd"] = _cost(inp, cached, out)
        row["cost_kind"] = "actual"
        row["text"] = resp.output_text or ""
        if resp.status == "incomplete":
            reason = getattr(getattr(resp, "incomplete_details", None), "reason", "unknown")
            row["status"] = "incomplete"
            row["error"] = f"incomplete: {reason}"
        else:
            row["status"] = "ok" if row["text"].strip() else "empty"
    except (openai.AuthenticationError, openai.PermissionDeniedError) as exc:
        raise KeyRejected(f"{type(exc).__name__}") from exc
    except openai.RateLimitError as exc:
        if "insufficient_quota" in str(exc):
            raise KeyRejected("insufficient_quota") from exc
        row["error"] = f"RateLimitError: {str(exc)[:200]}"
    except openai.APIError as exc:
        row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
    finally:
        row["duration_s"] = round(time.perf_counter() - t0, 2)
        budget.settle(reserve, row["cost_usd"])
    row.update({"model": model, "prompt_sha": prompt_sha(prompt),
                "reasoning_effort": REASONING_EFFORT, "max_output_tokens": MAX_OUTPUT_TOKENS})
    return row


# ---------------------------------------------------------------------------- Deciqo

def call_deciqo(system: str, case: dict, phase: str, db_dir: Path, budget: Budget) -> dict:
    engine = "rules" if system == "D-rules" else "ai"
    db_path = db_dir / f"{system}-{case['id']}-{phase}.sqlite3"
    if db_path.exists():
        db_path.unlink()
    reserve = 0.05 if engine == "ai" else 0.0
    if reserve:
        budget.reserve(reserve)
    t0 = time.perf_counter()
    row: dict = {"status": "error", "text": "", "cost_usd": reserve if reserve else 0.0}
    try:
        result = deciqo_adapter.run(case, phase, db_path=db_path, engine=engine)
        row["result"] = result
        row["cost_usd"] = result["cost_usd"]
        row["cost_kind"] = "actual" if engine == "ai" else "none"
        row["text"] = "\n\n".join(f["draft_text"] for f in result["findings"] if f["draft_text"])
        row["status"] = "ok"
        row["engine"] = result.get("engine") or engine
        if engine == "ai" and row["engine"] != "ai":
            # D yang diam-diam jatuh ke mode aturan tidak boleh terbaca sebagai hasil AI.
            row["status"] = "fallback_rules"
            row["error"] = f"engine fell back to {row['engine']}: {result.get('engine_note') or 'no reason given'}"
        row["pipeline_version"] = result.get("pipeline_version")
        row["verifier_version"] = result.get("verifier_version")
        row["usage"] = result.get("usage") or {}
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
        row["trace_tail"] = traceback.format_exc().splitlines()[-3:]
    finally:
        row["duration_s"] = round(time.perf_counter() - t0, 2)
        if reserve:
            budget.settle(reserve, row["cost_usd"])
    return row


# ---------------------------------------------------------------------------- main

def read_outputs() -> dict:
    path = OUT / "outputs.jsonl"
    rows = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                rows[(r["case_id"], r["phase"], r["system"])] = r
    return rows


def write_outputs(rows: dict) -> None:
    path = OUT / "outputs.jsonl"
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for key in sorted(rows):
            fh.write(json.dumps(rows[key], ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--systems", default="B0,B1,D,D-rules")
    ap.add_argument("--cases", default=None, help="glob id kasus, dipisah koma (mis. 'c0*,h*')")
    ap.add_argument("--budget", type=float, default=None, help="batas keras USD untuk sistem berbayar")
    ap.add_argument("--rules", action="store_true", help="dry run gratis: hanya D-rules")
    ap.add_argument("--rescore", action="store_true", help="hanya hitung ulang report dari outputs.jsonl")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--model", default=None)
    ap.add_argument("--holdout", action="store_true",
                    help="ikutkan kasus holdout; hanya untuk run final di build beku")
    ap.add_argument("--out", default=None, help="folder output lain (mis. pratinjau), default eval/final")
    args = ap.parse_args()
    global OUT
    if args.out:
        OUT = Path(args.out).resolve()
        OUT.mkdir(parents=True, exist_ok=True)

    if args.rescore:
        cases = load_cases(None)
        manifest_path = OUT / "manifest.json"
        if manifest_path.exists():
            # Status development/holdout dicatat sebelum kasus holdout pernah dijalankan.
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["case_status"] = {c["id"]: c["status"] for c in cases}
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        scoring.write_all(cases, read_outputs(), OUT)
        print("report.md, labels.csv, blind_key.json ditulis ulang dari outputs.jsonl")
        return 0

    load_env_file()
    systems = ["D-rules"] if args.rules else [s.strip() for s in args.systems.split(",") if s.strip()]
    unknown = set(systems) - set(ALL_SYSTEMS)
    if unknown:
        ap.error(f"sistem tidak dikenal: {sorted(unknown)}")
    paid = [s for s in systems if s in PAID]
    if paid and args.budget is None:
        ap.error(f"sistem berbayar {paid} butuh --budget <USD>")
    if paid and not os.environ.get("OPENAI_API_KEY"):
        ap.error("OPENAI_API_KEY tidak ada di environment atau .env")

    model = args.model or os.environ.get("DECIQO_LLM_MODEL") or "gpt-5-mini"
    cases = load_cases(args.cases, include_holdout=args.holdout)
    if not cases:
        ap.error("tidak ada kasus yang cocok")

    d_ok, d_reason = deciqo_adapter.available()
    skipped = []
    if not d_ok:
        for s in ("D", "D-rules"):
            if s in systems:
                systems.remove(s)
                skipped.append(s)
        if skipped:
            print(f"LEWATI {skipped}: {d_reason}")

    budget = Budget(args.budget or 0.0)
    client = None
    if any(s in ("B0", "B1") for s in systems):
        import openai
        client = openai.OpenAI(timeout=180, max_retries=2)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    db_dir = HERE / ".work" / run_id
    db_dir.mkdir(parents=True, exist_ok=True)

    jobs = [(c, ph, s) for c in cases for ph in phases_for(c) for s in systems]
    rows = read_outputs()
    stop = threading.Event()
    stop_reason = []
    started = time.perf_counter()

    def work(case, phase, system):
        if stop.is_set():
            return None
        base = {"case_id": case["id"], "phase": phase, "system": system,
                "case_status": case["status"], "run_id": run_id}
        try:
            if system in ("B0", "B1"):
                r = call_baseline(client, model, system, case, phase, budget)
            else:
                r = call_deciqo(system, case, phase, db_dir, budget)
        except (KeyRejected, BudgetExceeded) as exc:
            stop.set()
            stop_reason.append(f"{type(exc).__name__}: {exc}")
            return None
        base.update(r)
        return base

    done = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = [ex.submit(work, *j) for j in jobs]
        for fut in as_completed(futs):
            r = fut.result()
            if r is None:
                continue
            rows[(r["case_id"], r["phase"], r["system"])] = r
            done += 1
            print(f"[{done}/{len(jobs)}] {r['case_id']} {r['phase']:6} {r['system']:7} "
                  f"{r['status']:10} {r.get('duration_s', 0):6.1f}s ${r.get('cost_usd', 0):.4f}"
                  + (f"  {r.get('error')}" if r.get("error") else ""), flush=True)
            if done % 10 == 0:
                write_outputs(rows)

    write_outputs(rows)
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    runs = manifest.get("runs", [])
    runs.append({
        "run_id": run_id,
        "git": git_commit(),
        "systems": systems,
        "systems_skipped": {s: d_reason for s in skipped},
        "deciqo_harness": d_reason,
        "cases": [c["id"] for c in cases],
        "jobs_planned": len(jobs),
        "jobs_done": done,
        "stopped": stop_reason,
        "budget_usd": args.budget,
        "spent_usd": round(budget.spent, 4),
        "wall_seconds": round(time.perf_counter() - started, 1),
    })
    all_cases = load_cases(None)
    manifest.update({
        "model": model,
        "reasoning_effort": REASONING_EFFORT,
        "max_output_tokens_baseline": MAX_OUTPUT_TOKENS,
        "prices_per_million": {"input": PRICE_IN, "cached_input": PRICE_CACHED, "output": PRICE_OUT},
        "prompts": {k: {"sha256_16": prompt_sha(v), "text": v} for k, v in PROMPTS.items()},
        "engine": deciqo_adapter.versions(),
        "bundle": {
            "baselines": "judul, listing utuh, semua ulasan kasus (id, rating, tanggal, varian); "
                         "fase after menambah fakta merchant yang sama",
            "deciqo": "bundle yang sama sebagai data terstruktur; potongan listing yang dibaca "
                      "engine adalah keputusan engine dan tercatat di hasil D",
        },
        "case_status": {c["id"]: c["status"] for c in all_cases},
        "runs": runs,
    })
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    scoring.write_all(all_cases, rows, OUT)
    print(f"selesai: {done}/{len(jobs)} job, biaya ${budget.spent:.4f}"
          + (f", BERHENTI: {stop_reason[0]}" if stop_reason else ""))
    return 2 if stop_reason else 0


if __name__ == "__main__":
    sys.exit(main())
