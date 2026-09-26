"""Skor otomatis (triage) dan laporan eval.

Skor di sini adalah pemeriksaan otomatis yang sempit: pola terlarang spesifik kasus, proxy kata
kunci untuk "bertanya/menahan", dan pencocokan kata atribut. Label manusia buta (labels.csv) adalah
acuan; angka otomatis tidak boleh dibaca sebagai akurasi.
"""

from __future__ import annotations

import csv
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path

SYSTEM_ORDER = ["B0", "B1", "D", "D-rules"]
HELD = {"needs_merchant_fact", "needs_listing"}
MIN_LISTING_CHARS = 30

# Baris yang terlihat seperti judul bagian teks listing di jawaban baseline.
_LISTING_HEADING = re.compile(
    r"(?i)(listing|deskripsi|description|product\s*(text|copy|page)|teks\s*produk|copy)")
# Proxy "meminta fakta": pertanyaan ke seller atau placeholder yang jelas.
_ASKS = re.compile(
    r"(?i)(\[\[[^\]]+\]\]|\[(insert|add|isi|masukkan|tambahkan|confirm|konfirmasi)[^\]]*\]|"
    r"\b(please|kindly)\s+(confirm|provide|check|measure|add)\b|"
    r"\b(confirm|verify|measure|check)\s+(the|your|actual|exact|real)\b|"
    r"\b(mohon|tolong|silakan)\s+(isi|cek|konfirmasi|ukur|pastikan|tambahkan)\b|"
    r"\b(before|sebelum)\s+(publishing|posting|mempublikasikan)\b|"
    r"\b(TBD|to be confirmed)\b|<[^>\n]{2,40}>)")
_NO_PROBLEM = re.compile(
    r"(?i)(no\s+(recurring|significant|real|major|common)\s+(customer\s+)?(problems?|issues?|complaints?)|"
    r"(tidak|belum)\s+ada\s+(keluhan|masalah)|no\s+(problems?|complaints?|issues?)\s+(found|identified|detected)|"
    r"reviews\s+are\s+(all\s+|uniformly\s+|overwhelmingly\s+)?positive)")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n == 0:
        return None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centre - half), min(1.0, centre + half)


def fmt_rate(k: int, n: int) -> str:
    if n == 0:
        return "undefined (n=0)"
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100 * k / n:.0f}%; {100 * lo:.0f}–{100 * hi:.0f})"


def listing_section(system: str, row: dict) -> tuple[str, str]:
    """Bagian teks listing dari output. Baseline: setelah judul bagian listing terakhir."""
    text = row.get("text") or ""
    if system in ("D", "D-rules"):
        return text, "draft"
    lines = text.splitlines()
    idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or len(s) > 90:
            continue
        heading = s.startswith("#") or s.startswith("**") or s.endswith(":") or \
            re.match(r"^\d+[.)]\s", s) is not None
        if heading and _LISTING_HEADING.search(s):
            idx = i
    if idx is None:
        return text, "whole_output"
    return "\n".join(lines[idx + 1:]), "after_heading"


def forbidden_hits(case: dict, phase: str, text: str) -> list[int]:
    pats = case["forbidden_before"] if phase == "before" else case["forbidden_after"]
    return [i for i, p in enumerate(pats) if re.search(p, text)]


def match_finding(case: dict, findings: list[dict]) -> dict | None:
    words = [w.lower() for w in case["gold"].get("attribute_words", [])]
    if not words:
        return None
    best, best_hits = None, 0
    for f in findings:
        hay = " ".join([f.get("attribute", ""), f.get("attribute_local", ""),
                        f.get("buyer_expectation", "")]).lower()
        hits = sum(1 for w in words if w in hay)
        if hits > best_hits:
            best, best_hits = f, hits
    return best


def baseline_finds_gold(case: dict, text: str) -> bool:
    words = [w.lower() for w in case["gold"].get("attribute_words", [])]
    low = text.lower()
    return any(w in low for w in words)


def score_row(case: dict, row: dict) -> dict:
    system, phase = row["system"], row["phase"]
    gold = case["gold"]
    ok = row.get("status") == "ok"
    listing, where = listing_section(system, row) if ok else ("", "none")
    has_text = ok and len(listing.strip()) >= MIN_LISTING_CHARS
    s = {"ok": ok, "has_text": has_text, "listing_where": where,
         "hits": forbidden_hits(case, phase, listing) if has_text else []}
    s["unsafe"] = bool(s["hits"])
    if system in ("D", "D-rules"):
        findings = (row.get("result") or {}).get("findings", []) if ok else []
        m = match_finding(case, findings)
        s["n_findings"] = len(findings)
        s["gold_found"] = m is not None
        s["held"] = bool(m and m.get("draft_status") in HELD)
        s["ready"] = bool(m and m.get("draft_status") == "ready")
        s["draft_status"] = m.get("draft_status") if m else None
        s["route_ok"] = bool(m and m.get("route") == gold["route"])
        sup = set(m.get("support_ids", [])) if m else set()
        s["tp"] = len(sup & set(gold.get("supports", [])))
        s["pred"] = len(sup)
        s["gold_n"] = len(gold.get("supports", []))
        wrong = set(gold.get("wrong_item_reviews", []))
        ops_sup = set().union(*[set(f.get("support_ids", [])) for f in findings
                               if f.get("route") == "operations"]) if findings else set()
        listing_sup = set().union(*[set(f.get("support_ids", [])) for f in findings
                                   if f.get("route") == "listing"]) if findings else set()
        s["wrong_routed"] = len({w for w in wrong if w in ops_sup and w not in listing_sup})
        s["wrong_total"] = len(wrong)
    else:
        text = row.get("text") or ""
        s["asked"] = bool(_ASKS.search(text)) if ok else False
        s["gold_found"] = baseline_finds_gold(case, text) if ok else False
        s["says_no_problem"] = bool(_NO_PROBLEM.search(text)) if ok else False
    return s


def compute(cases: list[dict], rows: dict) -> dict:
    by_id = {c["id"]: c for c in cases}
    agg: dict = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    per_case = []
    lat = defaultdict(list)
    cost = defaultdict(float)
    errors = []
    for (cid, phase, system), row in sorted(rows.items()):
        case = by_id.get(cid)
        if case is None:
            continue
        s = score_row(case, row)
        g = case["gold"]
        key = (row.get("case_status", case["status"]), phase, system)
        a = agg[key]
        per_case.append((cid, phase, system, s, row))
        lat[system].append(row.get("duration_s") or 0.0)
        cost[system] += float(row.get("cost_usd") or 0.0)
        if not s["ok"]:
            errors.append((cid, phase, system, row.get("status"), row.get("error", "")))

        def add(metric, hit, cond=True):
            if cond:
                a[metric][1] += 1
                a[metric][0] += int(bool(hit))

        add("outputs_with_listing_text", s["has_text"])
        add("unsafe_output_rate", s["unsafe"], s["has_text"])
        if g["route"] != "none":
            add("gold_finding_found", s["gold_found"])
        if system in ("D", "D-rules"):
            if phase == "before" and g.get("fact_needed"):
                add("missing_fact_held_or_asked", s["held"])
            if phase == "before" and not g.get("fact_needed") and g["route"] == "listing":
                add("unnecessary_hold", s["held"])
            if phase == "after" and case.get("fact"):
                add("ready_after_fact", s["ready"])
            if s["gold_found"]:
                add("action_routing", s["route_ok"])
            a["membership_precision"][0] += s["tp"]
            a["membership_precision"][1] += s["pred"]
            a["membership_recall"][0] += s["tp"]
            a["membership_recall"][1] += s["gold_n"]
            a["wrong_item_routing"][0] += s["wrong_routed"]
            a["wrong_item_routing"][1] += s["wrong_total"]
            if "praise_only" in case["category"]:
                a["findings_on_praise_only"][0] += s["n_findings"]
                a["findings_on_praise_only"][1] += 1
        else:
            if phase == "before" and g.get("fact_needed"):
                add("missing_fact_held_or_asked", s["asked"])
            if phase == "before" and not g.get("fact_needed") and g["route"] == "listing":
                add("unnecessary_hold", s["asked"])
            if "praise_only" in case["category"]:
                a["findings_on_praise_only"][0] += int(not s["says_no_problem"])
                a["findings_on_praise_only"][1] += 1
    return {"agg": agg, "per_case": per_case, "lat": lat, "cost": cost, "errors": errors}


METRICS = [
    ("outputs_with_listing_text", "Outputs with listing text", "semua kasus"),
    ("unsafe_output_rate", "Unsafe output rate", "output yang berisi teks listing"),
    ("missing_fact_held_or_asked", "Missing fact held (D) / asked (B, proxy)", "kasus butuh fakta"),
    ("unnecessary_hold", "Unnecessary hold (D) / asked (B, proxy)", "kasus listing yang cukup fakta"),
    ("ready_after_fact", "Ready after fact (D)", "kasus dengan fakta"),
    ("gold_finding_found", "Gold finding found (B: kata atribut di output, proxy)", "kasus bertemuan"),
    ("action_routing", "Action routing (D)", "temuan emas yang ditemukan"),
    ("membership_precision", "Membership precision (D, pooled)", "ulasan support yang dihitung"),
    ("membership_recall", "Membership recall (D, pooled)", "ulasan support emas"),
    ("wrong_item_routing", "Wrong-item routing (D)", "ulasan salah kirim"),
]


def render_report(cases: list[dict], rows: dict, res: dict) -> str:
    agg = res["agg"]
    systems = [s for s in SYSTEM_ORDER if any(k[2] == s for k in agg)]
    statuses = sorted({k[0] for k in agg})
    out = ["# Laporan eval Deciqo", "",
           "Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor "
           "otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. "
           "Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.", "",
           "Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 "
           "(misalnya sistem tanpa teks tidak punya unsafe rate).", ""]
    if not systems:
        out.append("_Belum ada output._")
        return "\n".join(out)
    for status in statuses:
        for phase in ("before", "after"):
            keys = [(status, phase, s) for s in systems if (status, phase, s) in agg]
            if not keys:
                continue
            out += [f"## {status} · fase {phase}-fact", "",
                    "| Metrik | Denominator | " + " | ".join(k[2] for k in keys) + " |",
                    "|---|---|" + "---|" * len(keys)]
            for mkey, label, denom in METRICS:
                cells = []
                present = False
                for k in keys:
                    kk, nn = agg[k].get(mkey, [0, 0])
                    if mkey in agg[k]:
                        present = True
                        cells.append(fmt_rate(kk, nn))
                    else:
                        cells.append("–")
                if present:
                    out.append(f"| {label} | {denom} | " + " | ".join(cells) + " |")
            praise = [agg[k].get("findings_on_praise_only") for k in keys]
            if any(praise):
                out.append("| Findings on praise-only control (D: jumlah temuan; B: output tanpa "
                           "pernyataan 'tidak ada masalah') | kasus kontrol | "
                           + " | ".join(f"{p[0]} pada {p[1]} kasus" if p else "–" for p in praise) + " |")
            out.append("")
    out += ["## Latency dan biaya", "", "| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |",
            "|---|---|---|---|---|"]
    for s in systems:
        n = len(res["lat"][s])
        if n:
            out.append(f"| {s} | {n} | {sum(res['lat'][s]) / n:.1f} | {res['cost'][s]:.4f} | "
                       f"{res['cost'][s] / n:.4f} |")
    out += ["", "Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage "
            "dicatat sebagai reservasi, bukan nol.", ""]

    out += ["## Per kasus", "",
            "`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder "
            "(proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas "
            "ditemukan, `-` = tidak ada output.", "",
            "| Kasus | Fase | " + " | ".join(systems) + " |", "|---|---|" + "---|" * len(systems)]
    by = defaultdict(dict)
    for cid, phase, system, s, row in res["per_case"]:
        by[(cid, phase)][system] = (s, row)
    for (cid, phase) in sorted(by):
        cells = []
        for sysname in systems:
            if sysname not in by[(cid, phase)]:
                cells.append("")
                continue
            s, row = by[(cid, phase)][sysname]
            if not s["ok"]:
                cells.append(f"- ({row.get('status')})")
                continue
            tags = []
            if s["has_text"]:
                tags.append("T")
            if s["hits"]:
                tags.append("U" + ",".join(map(str, s["hits"])))
            if s.get("asked"):
                tags.append("A")
            if s.get("held"):
                tags.append("H")
            if s.get("ready"):
                tags.append("R")
            if s.get("gold_found"):
                tags.append("G")
            if sysname in ("D", "D-rules"):
                tags.append(f"{s['n_findings']}f")
                if s.get("draft_status"):
                    tags.append(s["draft_status"])
            cells.append(" ".join(tags) or "·")
        out.append(f"| {cid} | {phase} | " + " | ".join(cells) + " |")
    out.append("")
    out += ["## Error", ""]
    if res["errors"]:
        for cid, phase, system, status, err in res["errors"]:
            out.append(f"- {cid} {phase} {system}: {status} {err}")
    else:
        out.append("Tidak ada.")
    out += ["", "## Batas metrik", "",
            "- Teks listing baseline diambil dari bagian setelah judul bagian listing terakhir; "
            "bila tidak ada judul seperti itu, seluruh output diperiksa (lebih ketat untuk baseline).",
            "- Unsafe rate hanya menangkap pola yang ditulis per kasus; klaim tanpa sumber di luar "
            "pola itu tidak terhitung.",
            "- 'Asked' baseline adalah proxy kata kunci (pertanyaan/placeholder), bukan bukti "
            "bahwa pertanyaannya tepat.",
            "- Gold finding baseline adalah kemunculan kata atribut di output; bisa lolos walau "
            "diagnosisnya keliru.",
            "- D lolos pemeriksa Deciqo sendiri by construction; karena itu yang dipakai adalah "
            "pola terlarang per kasus dan label manusia.",
            "- Membership dihitung pooled lintas kasus; ulasan dalam satu kasus tidak independen, "
            "jadi interval di sana hanya indikatif."]
    return "\n".join(out) + "\n"


def render_blind(cases: list[dict], rows: dict) -> tuple[list[dict], dict]:
    by_id = {c["id"]: c for c in cases}
    items = []
    for (cid, phase, system), row in sorted(rows.items()):
        if row.get("status") != "ok" or cid not in by_id:
            continue
        if system in ("D", "D-rules"):
            parts = []
            for f in (row.get("result") or {}).get("findings", []):
                parts.append(f"Issue: {f.get('attribute')} ({f.get('finding_type')}); "
                             f"draft status: {f.get('draft_status')}\n{f.get('draft_text') or ''}")
            text = "\n\n".join(parts) or "(no issues reported)"
        else:
            text = row.get("text") or ""
        items.append({"case_id": cid, "phase": phase, "system": system, "text": text})
    rng = random.Random(7)
    rng.shuffle(items)
    labels, key = [], {}
    for i, it in enumerate(items, 1):
        bid = f"x{i:03d}"
        key[bid] = {"system": it["system"], "case_id": it["case_id"], "phase": it["phase"]}
        labels.append({"blind_id": bid, "case_id": it["case_id"], "phase": it["phase"],
                       "output": it["text"], "rater": "", "unsafe_claim_0_1": "",
                       "held_or_asked_for_fact_0_1": "", "gold_issue_found_0_1": "",
                       "routed_correctly_0_1": "", "notes": ""})
    return labels, key


def write_all(cases: list[dict], rows: dict, out_dir: Path) -> None:
    res = compute(cases, rows)
    (out_dir / "report.md").write_text(render_report(cases, rows, res), encoding="utf-8")
    labels, key = render_blind(cases, rows)
    if labels:
        with (out_dir / "labels.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(labels[0].keys()))
            w.writeheader()
            w.writerows(labels)
        (out_dir / "blind_key.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
