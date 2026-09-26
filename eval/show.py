"""Tampilkan output mentah satu (kasus, fase, sistem) beserta pola terlarang yang cocok.

Dipakai untuk menulis temuan di ITERATIONS.md dengan kutipan output yang persis.

    python eval/show.py c01 before B0
    python eval/show.py c01            # semua fase dan sistem untuk kasus itu, ringkas
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import scoring  # noqa: E402


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if not argv:
        print(__doc__)
        return 1
    cid = argv[0]
    phase = argv[1] if len(argv) > 1 else None
    system = argv[2] if len(argv) > 2 else None
    cases = {}
    for name in ("cases.jsonl", "cases_holdout.jsonl"):
        p = HERE / "final" / name
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    c = json.loads(line)
                    cases[c["id"]] = c
    case = cases[cid]
    for line in (HERE / "final" / "outputs.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["case_id"] != cid or (phase and row["phase"] != phase) or \
                (system and row["system"] != system):
            continue
        s = scoring.score_row(case, row)
        text, where = scoring.listing_section(row["system"], row)
        pats = case["forbidden_before"] if row["phase"] == "before" else case["forbidden_after"]
        print(f"===== {cid} {row['phase']} {row['system']} status={row.get('status')} "
              f"listing={where} score={ {k: v for k, v in s.items() if k != 'hits'} }")
        for i in s["hits"]:
            for m in re.finditer(pats[i], scoring.claim_text(text)):
                ct = scoring.claim_text(text)
                a, b = max(0, m.start() - 60), min(len(ct), m.end() + 40)
                print(f"  pola[{i}] -> ...{ct[a:b]!r}...")
        if system:
            print(row.get("text", ""))
            if row.get("result"):
                print(json.dumps(row["result"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
