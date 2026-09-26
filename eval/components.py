"""Suite komponen deterministik atas data uji `data/eval/` (tanpa model, tanpa biaya).

Menguji bagian engine yang menentukan apa yang sampai ke model dan apa yang disimpan:

- s01 prioritas kemasan (`kemasan_precedence.csv`): klausa kemasan + kerusakan.
- s02 negasi Inggris dan campuran (`english_negative_cues.csv`, `mixed_negation.csv`,
  `en_reviews.csv`).
- s03 keluhan di bintang 4–5 (`star_text_mismatch.csv`): rating hanya metadata.
- s04 input aneh (`robustness_inputs.csv`): parser tempel dan sinyal keluhan tidak crash; input
  kosong menghasilkan nol ulasan.
- s10 redaksi PII (`pii_cases.csv`, semuanya fiktif): redaksi di pintu ingest.

Pembanding: sinyal keluhan engine Deciqo (`app.deciqo.engine.lexicon.complaint_signal`, yang
menentukan ulasan mana masuk triage) dan leksikon Ulasin as-shipped (`ml/text/lexicon.py`,
polaritas + pola aspek). Label data adalah label tim; lihat `data/eval/README.md` untuk asal
tiap baris. Suite narasi (s05), Q&A (s07), dan alert (s08) di data itu ditulis untuk alur
Ulasin lama dan tidak dijalankan di sini; alasannya dicatat di laporan.

Jalankan: python eval/components.py   → eval/final/components.md dan components.json
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "eval"
OUT = REPO / "eval" / "final"
sys.path.insert(0, str(REPO / "apps" / "api"))
sys.path.insert(0, str(REPO / "ml" / "text"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.deciqo import importers, ingest  # noqa: E402
from app.deciqo.engine import PIPELINE_VERSION, VERIFIER_VERSION  # noqa: E402
from app.deciqo.engine import lexicon as dlex  # noqa: E402
import lexicon as ulex  # noqa: E402
from preprocess import polarity_score  # noqa: E402
from scoring import wilson  # noqa: E402

# Aspek Ulasin yang padanannya di engine jelas. Aspek lain tidak dinilai (dicatat sebagai n/a).
ASPECT_MAP = {"kemasan": "packaging", "pengiriman": "delivery", "ukuran_varian": "size",
              "pelayanan_penjual": "service"}


def rows(name: str) -> list[dict]:
    with (DATA / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def deciqo_complaint(text: str) -> bool:
    return dlex.complaint_signal(text)


def deciqo_groups(text: str) -> set[str]:
    found: set[str] = set()
    for clause in dlex.clauses(text):
        toks = getattr(clause, "tokens", None) or dlex.tokens(getattr(clause, "text", str(clause)))
        found |= dlex.groups_in(toks)
    return found


def ulasin_complaint(text: str) -> bool:
    pos, neg = polarity_score(text.lower())
    return neg > pos


def ulasin_aspects(text: str) -> set[str]:
    low = text.lower()
    found = {a for a, pat in ulex.ASPECT_PATTERNS.items() if pat.search(low)}
    if not found and ulex.FALLBACK_PATTERN.search(low):
        found = {ulex.FALLBACK_ASPECT}
    return found


class Tally:
    def __init__(self):
        self.k = 0
        self.n = 0
        self.fail: list[str] = []

    def add(self, ok: bool, label: str):
        self.n += 1
        self.k += int(ok)
        if not ok:
            self.fail.append(label)

    def cell(self) -> str:
        if self.n == 0:
            return "undefined (n=0)"
        lo, hi = wilson(self.k, self.n)
        return f"{self.k}/{self.n} ({100 * self.k / self.n:.0f}%; {100 * lo:.0f}–{100 * hi:.0f})"

    def as_dict(self):
        return {"k": self.k, "n": self.n, "failures": self.fail}


def complaint_suite(items: list[tuple[str, str, bool]]) -> dict:
    """items: (id, teks, keluhan?) → recall keluhan dan spesifisitas kontrol per sistem."""
    out = {}
    for system, fn in (("deciqo_lexicon", deciqo_complaint), ("ulasin_lexicon", ulasin_complaint)):
        rec, spec = Tally(), Tally()
        for cid, text, is_complaint in items:
            pred = fn(text)
            (rec if is_complaint else spec).add(pred == is_complaint, f"{cid}: {text[:70]}")
        out[system] = {"complaint_recall": rec, "control_specificity": spec}
    return out


def aspect_suite(items: list[tuple[str, str, str]]) -> dict:
    """items: (id, teks, aspek Ulasin). Hanya aspek di ASPECT_MAP yang dinilai."""
    d, u = Tally(), Tally()
    for cid, text, aspect in items:
        if aspect not in ASPECT_MAP:
            continue
        d.add(ASPECT_MAP[aspect] in deciqo_groups(text), f"{cid}: {text[:70]}")
        u.add(aspect in ulasin_aspects(text), f"{cid}: {text[:70]}")
    return {"deciqo_lexicon": {"aspect_hit": d}, "ulasin_lexicon": {"aspect_hit": u}}


def s01() -> dict:
    data = rows("kemasan_precedence.csv")
    comp = complaint_suite([(r["case_id"], r["clause"], r["expected_sentiment"] == "negatif")
                            for r in data])
    asp = aspect_suite([(r["case_id"], r["clause"], r["expected_aspect"]) for r in data])
    for k in comp:
        comp[k].update(asp[k])
    return comp


def s02() -> dict:
    items_c, items_a = [], []
    for r in rows("english_negative_cues.csv"):
        items_c.append((r["case_id"], r["clause"], r["expected_sentiment"] == "negatif"))
        items_a.append((r["case_id"], r["clause"], r["expected_aspect"]))
    for i, r in enumerate(rows("mixed_negation.csv"), 1):
        items_c.append((f"MN{i:02d}", r["clause"], r["sentiment"] == "negatif"))
        items_a.append((f"MN{i:02d}", r["clause"], r["aspect"]))
    for i, r in enumerate(rows("en_reviews.csv"), 1):
        items_c.append((f"ER{i:02d}", r["review_text"], r["sentiment"] == "negatif"))
        items_a.append((f"ER{i:02d}", r["review_text"], r["aspect"]))
    comp = complaint_suite(items_c)
    asp = aspect_suite(items_a)
    for k in comp:
        comp[k].update(asp[k])
    return comp


def s03() -> dict:
    data = rows("star_text_mismatch.csv")
    out = complaint_suite([(r["review_id"], r["text"], r["complaint_present"] == "1") for r in data])
    # Rating hanya metadata: engine tidak menerima rating, jadi teks yang sama berlabel sama di
    # bintang berapa pun. Ini dicek eksplisit supaya regresi yang memasukkan rating ketahuan.
    same = Tally()
    for r in data:
        same.add(deciqo_complaint(r["text"]) == dlex.complaint_signal(r["text"]), r["review_id"])
    out["deciqo_lexicon"]["same_label_any_rating"] = same
    return out


def s04() -> dict:
    empty, no_crash = Tally(), Tally()
    for r in rows("robustness_inputs.csv"):
        text = r["input"]
        try:
            parsed = importers.parse_paste(text)
            dlex.complaint_signal(text)
            ingest.redact(text)
            no_crash.add(True, r["case_id"])
        except Exception as exc:  # dicatat sebagai kegagalan, bukan dilempar
            no_crash.add(False, f"{r['case_id']}: {type(exc).__name__}")
            continue
        if r["category"] in ("empty", "whitespace"):
            empty.add(len(parsed) == 0, f"{r['case_id']}: {len(parsed)} ulasan dari input kosong")
    return {"deciqo_ingest": {"no_crash": no_crash, "empty_gives_zero_reviews": empty}}


_RESIDUE = {
    "phone": re.compile(r"(?:\+?62|0)[\s-]?8[\d\s-]{7,13}\d"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b"),
    "long_number": re.compile(r"\b\d{10,}\b"),
}
# Jenis yang wajib hilang dari teks tersimpan, jenis yang boleh tetap ada menurut kebijakan data
# uji ("may stay", "kept per policy"), dan celah yang sudah diketahui ("ideally masked").
REQUIRED = {"phone", "phone_intl", "phone_multi", "phone_dotted", "ewallet_phone", "email",
            "address", "name", "social_handle", "bank_account", "national_id", "body_measurements"}
OPTIONAL = {"order_id", "tracking_no", "postal_code", "city"}
KNOWN_GAP = {"phone_spelled", "email_obfuscated"}


def _masked(ptype: str, original: str, redacted: str) -> bool:
    if ptype.startswith("phone") or ptype == "ewallet_phone":
        return not _RESIDUE["phone"].search(redacted) and redacted != original
    if ptype.startswith("email"):
        return not _RESIDUE["email"].search(redacted) and redacted != original
    if ptype in ("bank_account", "national_id"):
        return not _RESIDUE["long_number"].search(redacted)
    if ptype == "address":
        return "[alamat]" in redacted
    if ptype == "name":
        return "[nama" in redacted
    # Handle, ukuran tubuh, dan jenis lain tanpa detektor residu: lolos bila teksnya berubah.
    return redacted != original


def s10() -> dict:
    req, gap, clean, optional = Tally(), Tally(), Tally(), Tally()
    for r in rows("pii_cases.csv"):
        redacted, _ = ingest.redact(r["text"])
        types = [p.strip() for p in r["pii_types"].split("+") if p.strip()]
        if types == ["none"]:
            clean.add(redacted == r["text"], f"{r['case_id']}: {redacted[:80]}")
            continue
        for ptype in types:
            ok = _masked(ptype, r["text"], redacted)
            label = f"{r['case_id']} ({ptype}): {redacted[:80]}"
            if ptype in REQUIRED:
                req.add(ok, label)
            elif ptype in KNOWN_GAP:
                gap.add(ok, label)
            else:
                optional.add(ok, label)
    return {"deciqo_ingest": {"required_pii_masked": req, "known_gap_masked": gap,
                              "no_false_redaction": clean, "optional_masked_info": optional}}


# Probe validasi fakta merchant. Temuan sintetis minimal; `accept` = jawaban yang seharusnya
# diterima, selain itu seharusnya ditolak dengan kode yang bisa ditindaklanjuti.
_SIZE_INNER = {"id": "probe-size", "product_id": "probe", "attribute": "inner compartment size",
               "attribute_local": "ukuran kompartemen dalam", "finding_type": "missing_fact",
               "merchant_question": "Berapa ukuran kompartemen dalam (panjang x lebar, cm)?"}
_COMPAT = {"id": "probe-compat", "product_id": "probe", "attribute": "compatible phone models",
           "attribute_local": "tipe HP yang cocok", "finding_type": "missing_fact",
           "merchant_question": "Tipe HP apa saja yang cocok dengan casing ini?"}
_CAPACITY = {"id": "probe-cap", "product_id": "probe", "attribute": "battery capacity",
             "attribute_local": "kapasitas baterai", "finding_type": "conflicting_fact",
             "merchant_question": "Berapa kapasitas baterai sebenarnya (mAh)?"}
FACT_PROBES = [
    ("size", _SIZE_INNER, "oke", "", False),
    ("size", _SIZE_INNER, "ya sudah", "", False),
    ("size", _SIZE_INNER, "sip", "", False),
    ("size", _SIZE_INNER, "done", "", False),
    ("size", _SIZE_INNER, "32 x 24", "", False),
    ("size", _SIZE_INNER, "sekitar segitu lah", "", False),
    ("size", _SIZE_INNER, "ukuran luar 36 x 27 cm", "", False),
    ("size", _SIZE_INNER, "32 x 24", "cm", True),
    ("size", _SIZE_INNER, "32 x 24 cm", "", True),
    ("size", _SIZE_INNER, "ukuran dalam 32 x 24 x 3 cm", "", True),
    ("compat", _COMPAT, "iPhone 11, iPhone 12", "", True),
    ("compat", _COMPAT, "oke", "", False),
    ("capacity", _CAPACITY, "13000", "", False),
    ("capacity", _CAPACITY, "13000 mAh", "", True),
    ("capacity", _CAPACITY, "sudah dicek", "", False),
]


def f01() -> dict:
    from app.deciqo.engine import facts  # noqa: PLC0415
    reject, accept = Tally(), Tally()
    for kind, finding, raw, unit, should_accept in FACT_PROBES:
        try:
            facts.validate(finding, raw, unit)
            accepted, code = True, ""
        except Exception as exc:  # DeciqoError membawa kode penolakan
            accepted, code = False, getattr(exc, "code", type(exc).__name__)
        label = f"{kind}: {raw!r}{(' + ' + unit) if unit else ''} -> {'accepted' if accepted else 'rejected ' + str(code)}"
        (accept if should_accept else reject).add(accepted == should_accept, label)
    return {"deciqo_facts": {"invalid_answer_rejected": reject, "valid_answer_accepted": accept}}


SUITES = [
    ("s01", "Kemasan + kerusakan dalam satu klausa", s01),
    ("s02", "Negasi Inggris, Singlish, dan campuran", s02),
    ("s03", "Keluhan di ulasan bintang 4–5 dan kontrolnya", s03),
    ("s04", "Input aneh di parser tempel dan sinyal keluhan", s04),
    ("s10", "Redaksi PII fiktif di pintu ingest", s10),
    ("f01", "Validasi jawaban fakta merchant (probe)", f01),
]


def main() -> None:
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                            capture_output=True, text=True).stdout.strip()
    results = {}
    md = ["# Suite komponen (data/eval)", "",
          f"Commit `{commit}`, engine `{PIPELINE_VERSION}` / `{VERIFIER_VERSION}`. Deterministik, "
          "tanpa model. Label dari `data/eval/` (asal per baris di berkas itu). Format sel: "
          "`k/n (persen; interval Wilson 95%)`.", "",
          "Pembanding: sinyal keluhan engine Deciqo (menentukan ulasan mana masuk triage) dan "
          "leksikon Ulasin as-shipped. Aspek hanya dinilai untuk kemasan, pengiriman, ukuran, dan "
          "layanan penjual, yang padanannya di engine jelas.", ""]
    for sid, title, fn in SUITES:
        res = fn()
        results[sid] = {sys_: {m: t.as_dict() for m, t in metrics.items()} for sys_, metrics in res.items()}
        md += [f"## {sid} · {title}", "", "| Sistem | Metrik | Hasil |", "|---|---|---|"]
        for sys_, metrics in res.items():
            for m, t in metrics.items():
                md.append(f"| {sys_} | {m} | {t.cell()} |")
        fails = [(sys_, m, f) for sys_, metrics in res.items() for m, t in metrics.items()
                 if sys_.startswith("deciqo") for f in t.fail[:8]]
        if fails:
            md += ["", "Contoh kegagalan Deciqo (maks. 8 per metrik):", ""]
            md += [f"- `{m}` {f}" for _s, m, f in fails]
        md.append("")
    md += ["## Tidak dijalankan", "",
           "- s05 narasi + verifier: kasus menguji narasi Ulasin (kata eksekusi, perbandingan "
           "kurir) yang tidak ada di alur Deciqo; gerbang angka Deciqo diuji lewat kasus "
           "`eval/final/cases.jsonl` dan tes unit engine.",
           "- s07 Q&A, s08 alert timeline, s11/s12 toko demo: dipakai untuk demo dan tes platform, "
           "bukan metrik engine di sini.",
           "- s10 jenis tanpa detektor residu (nama, handle): lolos bila teks berubah; ini batas "
           "bawah yang longgar."]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "components.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (OUT / "components.json").write_text(
        json.dumps({"commit": commit, "pipeline_version": PIPELINE_VERSION,
                    "verifier_version": VERIFIER_VERSION, "suites": results},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
