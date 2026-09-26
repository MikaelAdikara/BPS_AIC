"""Validasi format kasus eval sebelum dipakai runner.

Memeriksa: field wajib, id unik dan berawalan sesuai status, id ulasan di label emas benar-benar
ada, supports/not_supports tidak tumpang tindih, pola terlarang bisa di-compile, dan fakta merchant
sendiri tidak terkena pola `forbidden_after` (kalau terkena, polanya salah, bukan sistemnya).

Jalankan: python eval/validate_cases.py [berkas.jsonl ...]
Keluar dengan kode 1 bila ada kesalahan.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_FILES = [HERE / "final" / "cases.jsonl", HERE / "final" / "cases_holdout.jsonl",
                 HERE / "final" / "cases_holdout2.jsonl", HERE / "final" / "cases_holdout3.jsonl",
                 HERE / "final" / "cases_holdout4.jsonl"]

CATEGORIES = {
    "missing_fact", "cm_inch", "inner_outer", "negation", "water_claims", "compatibility",
    "capacity_conflict", "electrical", "size_chart_variant", "praise_low_star",
    "hidden_high_star", "wrong_item", "quality", "delivery", "no_listing", "truncated_listing",
    "injection", "praise_only", "mixed", "informal",
}
ROUTES = {"listing", "operations", "quality", "none"}
REQUIRED = ["id", "status", "category", "title", "listing", "reviews", "gold", "fact",
            "forbidden_before", "forbidden_after"]
GOLD_REQUIRED = ["attribute_words", "route", "supports", "not_supports", "ops_reviews",
                 "fact_needed"]
TRUNCATION_CHARS = 9000


def validate_case(case: dict) -> list[str]:
    errs: list[str] = []
    cid = case.get("id", "?")
    for key in REQUIRED:
        if key not in case:
            errs.append(f"{cid}: field '{key}' tidak ada")
    if errs:
        return errs

    status = case["status"]
    if status not in {"development", "holdout"}:
        errs.append(f"{cid}: status '{status}' tidak dikenal")
    prefix = "c" if status == "development" else "h"
    if not re.fullmatch(prefix + r"\d{2}", cid):
        errs.append(f"{cid}: id harus berpola {prefix}NN untuk status {status}")

    unknown = set(case["category"]) - CATEGORIES
    if unknown:
        errs.append(f"{cid}: kategori tidak dikenal {sorted(unknown)}")

    review_ids = [r.get("id") for r in case["reviews"]]
    if len(review_ids) != len(set(review_ids)):
        errs.append(f"{cid}: id ulasan ganda")
    for r in case["reviews"]:
        if not isinstance(r.get("rating"), int) or not 1 <= r["rating"] <= 5:
            errs.append(f"{cid}/{r.get('id')}: rating harus bilangan 1-5")
        if not str(r.get("text", "")).strip():
            errs.append(f"{cid}/{r.get('id')}: teks ulasan kosong")

    gold = case["gold"]
    for key in GOLD_REQUIRED:
        if key not in gold:
            errs.append(f"{cid}: gold.{key} tidak ada")
    if gold.get("route") not in ROUTES:
        errs.append(f"{cid}: gold.route '{gold.get('route')}' tidak dikenal")
    for key in ("supports", "not_supports", "ops_reviews", "contradicts", "quality_reviews",
                "wrong_item_reviews"):
        missing = set(gold.get(key, [])) - set(review_ids)
        if missing:
            errs.append(f"{cid}: gold.{key} menyebut ulasan yang tidak ada {sorted(missing)}")
    overlap = set(gold.get("supports", [])) & set(gold.get("not_supports", []))
    if overlap:
        errs.append(f"{cid}: ulasan ada di supports dan not_supports {sorted(overlap)}")
    if gold.get("route") != "none" and not gold.get("attribute_words"):
        errs.append(f"{cid}: temuan emas tanpa attribute_words")
    if gold.get("route") == "none" and gold.get("supports"):
        errs.append(f"{cid}: kasus tanpa temuan tidak boleh punya supports")

    if gold.get("fact_needed") and not case["fact"].strip():
        errs.append(f"{cid}: fact_needed=true tetapi fakta after-phase kosong")

    for phase in ("forbidden_before", "forbidden_after"):
        for pat in case[phase]:
            try:
                rx = re.compile(pat)
            except re.error as exc:
                errs.append(f"{cid}: pola {phase} tidak valid {pat!r}: {exc}")
                continue
            if phase == "forbidden_after" and case["fact"] and rx.search(case["fact"]):
                errs.append(f"{cid}: fakta merchant sendiri terkena pola forbidden_after {pat!r}")

    if "no_listing" in case["category"] and case["listing"].strip():
        errs.append(f"{cid}: kategori no_listing tetapi listing terisi")
    if "truncated_listing" in case["category"] and len(case["listing"]) <= TRUNCATION_CHARS:
        errs.append(f"{cid}: listing truncated harus lebih dari {TRUNCATION_CHARS} karakter")
    return errs


def load(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"{path}:{n}: JSON tidak valid: {exc}") from exc
    return rows


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv] or DEFAULT_FILES
    all_errs: list[str] = []
    seen: set[str] = set()
    coverage: dict[str, int] = {c: 0 for c in CATEGORIES}
    total = 0
    for path in files:
        for case in load(path):
            total += 1
            if case.get("id") in seen:
                all_errs.append(f"{case.get('id')}: id kasus ganda antar berkas")
            seen.add(case.get("id"))
            all_errs.extend(validate_case(case))
            for cat in case.get("category", []):
                if cat in coverage:
                    coverage[cat] += 1
    print(f"{total} kasus diperiksa")
    print("cakupan kategori: " + ", ".join(f"{k}={v}" for k, v in sorted(coverage.items())))
    empty = [k for k, v in coverage.items() if v == 0]
    if empty:
        print(f"PERINGATAN kategori tanpa kasus: {empty}")
    for err in all_errs:
        print("ERROR", err)
    return 1 if all_errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
