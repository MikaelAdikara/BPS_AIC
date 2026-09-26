"""Atribusi kehilangan recall bukti D: di tahap mana ulasan pendukung emas hilang.

Untuk setiap (kasus, fase before) D dan setiap ulasan di `gold.supports`:

- `counted`          : dihitung pada temuan emas (true positive)
- `counted_elsewhere`: dihitung, tetapi pada temuan lain (model membelah atribut)
- `set_aside:<alasan>`: model melabelinya pada temuan emas, verifier/juri menyisihkannya
- `no_gold_finding`  : temuan emas tidak ditemukan sama sekali
- `never_labelled`   : temuan emas ada, model tidak pernah melabeli ulasan itu untuknya

Jalankan: python eval/recall_loss.py <folder-run> [--phase before|after|all]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_final import load_cases  # noqa: E402
from scoring import match_finding  # noqa: E402


def attribute(case: dict, row: dict) -> list[tuple[str, str]]:
    findings = (row.get("result") or {}).get("findings", []) if row.get("status") == "ok" else []
    gold = match_finding(case, findings)
    out = []
    for rid in case["gold"].get("supports", []):
        if gold is None:
            out.append((rid, "no_gold_finding"))
        elif rid in gold.get("support_ids", []):
            out.append((rid, "counted"))
        elif any(rid in f.get("support_ids", []) for f in findings):
            out.append((rid, "counted_elsewhere"))
        else:
            aside = next((x for x in gold.get("set_aside", []) if x.get("review_id") == rid), None)
            out.append((rid, f"set_aside:{aside['reason']}" if aside else "never_labelled"))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--phase", default="before")
    ap.add_argument("--system", default="D")
    args = ap.parse_args()
    cases = {c["id"]: c for c in load_cases(None, include_holdout=True)}
    rows = [json.loads(line) for line in (Path(args.run_dir) / "outputs.jsonl").open(encoding="utf-8")]
    total: Counter = Counter()
    for row in rows:
        if row["system"] != args.system or (args.phase != "all" and row["phase"] != args.phase):
            continue
        case = cases.get(row["case_id"])
        if not case:
            continue
        for rid, where in attribute(case, row):
            total[where] += 1
            if where != "counted":
                text = next(r["text"] for r in case["reviews"] if r["id"] == rid)
                print(f"{row['case_id']}/{row['phase']}/{rid:4} {where:45} {text[:70]}")
    print()
    n = sum(total.values())
    for where, k in total.most_common():
        print(f"{where:45} {k:3}/{n}")


if __name__ == "__main__":
    main()
