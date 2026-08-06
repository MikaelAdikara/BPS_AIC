"""Bandingkan pra-anotasi LLM vs label silver, lalu susun berkas adjudikasi manusia.

Alur kerja anotasi gold (ADR-017):

    1. Labeling function leksikon  -> label SILVER  (otomatis, sudah ada)
    2. Pembacaan semantik LLM      -> pra-anotasi   (independen dari langkah 1)
    3. Manusia mengadjudikasi      -> label GOLD    (langkah ini yang menentukan)

Manusia HANYA meninjau baris yang kedua sumbernya berbeda, ditambah sampel acak baris yang
keduanya sepakat. Sampel acak itu penting: tanpanya, kesalahan yang KEBETULAN disepakati kedua
sumber tidak akan pernah ketahuan, dan justru kesalahan semacam itu yang paling berbahaya karena
tak meninggalkan jejak.

Pemakaian:
    python scripts/build_adjudication_task.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "ml" / "text"))
sys.path.insert(0, str(REPO_ROOT / "data" / "annotation"))

from _preannotation_raw import ANNOTATIONS  # noqa: E402
from lexicon import ALL_ASPECTS  # noqa: E402

ANNOT_DIR = REPO_ROOT / "data" / "annotation"
PROCESSED = REPO_ROOT / "data" / "processed"

ASPECT_CODE = {
    "kp": "kualitas_produk", "kd": "kesesuaian_deskripsi", "hv": "harga_value",
    "km": "kemasan", "pg": "pengiriman", "pp": "pelayanan_penjual",
    "uv": "ukuran_varian", "rm": "rasa_kualitas_makanan", "kl": "kelengkapan",
    "ka": "keaslian", "ku": "kemudahan_penggunaan",
}
SENTIMENT_CODE = {"p": "positif", "n": "negatif", "e": "netral"}
SEVERITY_CODE = {"r": "rendah", "s": "sedang", "t": "tinggi", "": ""}

# Berapa banyak baris yang DISEPAKATI ikut diperiksa manusia sebagai kontrol.
AGREEMENT_SAMPLE = 40
SEED = 42


def parse(code: str) -> tuple[set[str], str, str]:
    aspects, sentiment, severity = code.split(";")
    parsed = {ASPECT_CODE[a] for a in aspects.split(",") if a}
    unknown = {a for a in aspects.split(",") if a and a not in ASPECT_CODE}
    if unknown:
        raise ValueError(f"kode aspek tidak dikenal: {unknown}")
    return parsed, SENTIMENT_CODE[sentiment], SEVERITY_CODE[severity]


def main() -> int:
    task = pd.read_csv(ANNOT_DIR / "gold_annotation_task.csv")
    silver = pd.read_csv(PROCESSED / "clauses_test_silver.csv").set_index("clause_id")

    if len(ANNOTATIONS) != len(task):
        print(f"pra-anotasi {len(ANNOTATIONS)} baris, berkas tugas {len(task)} baris.", file=sys.stderr)
        return 1

    rows = []
    for i, row in task.iterrows():
        llm_aspects, llm_sentiment, llm_severity = parse(ANNOTATIONS[i])
        s = silver.loc[row.clause_id]
        silver_aspects = {a for a in ALL_ASPECTS if s[f"asp_{a}"] == 1}

        aspect_match = llm_aspects == silver_aspects
        sentiment_match = llm_sentiment == s["sentiment"]

        reasons = []
        if not aspect_match:
            reasons.append("aspek")
        if not sentiment_match:
            reasons.append("sentimen")

        rows.append({
            "clause_id": row.clause_id,
            "clause_text": row.clause_text,
            "silver_aspek": ", ".join(sorted(silver_aspects)) or "(tidak ada)",
            "llm_aspek": ", ".join(sorted(llm_aspects)) or "(tidak ada)",
            "silver_sentimen": s["sentiment"],
            "llm_sentimen": llm_sentiment,
            "llm_severity": llm_severity,
            "beda_pada": " + ".join(reasons) or "-",
            "sepakat": not reasons,
        })

    df = pd.DataFrame(rows)

    disagree = df[~df["sepakat"]]
    agree_sample = df[df["sepakat"]].sample(
        min(AGREEMENT_SAMPLE, int(df["sepakat"].sum())), random_state=SEED
    )
    adjudication = pd.concat([disagree, agree_sample]).sample(frac=1.0, random_state=SEED)

    adjudication = adjudication.assign(
        final_aspek="", final_sentimen="", final_severity="", catatan=""
    ).drop(columns=["sepakat"])
    out = ANNOT_DIR / "gold_adjudication_task.csv"
    adjudication.to_csv(out, index=False, encoding="utf-8-sig")

    # ---- Statistik kesepakatan ----
    n = len(df)
    aspect_agree = int((df["silver_aspek"] == df["llm_aspek"]).sum())
    sentiment_agree = int((df["silver_sentimen"] == df["llm_sentimen"]).sum())
    both = int(df["sepakat"].sum())

    stats = {
        "total_klausa": n,
        "kesepakatan_aspek_persis": round(aspect_agree / n, 4),
        "kesepakatan_sentimen": round(sentiment_agree / n, 4),
        "kesepakatan_keduanya": round(both / n, 4),
        "perlu_adjudikasi": int(len(disagree)),
        "sampel_kontrol_sepakat": int(len(agree_sample)),
        "total_baris_ditinjau_manusia": int(len(adjudication)),
        "beda_pada": {k: int(v) for k, v in df["beda_pada"].value_counts().items()},
        "catatan": (
            "Kesepakatan BUKAN ukuran kebenaran - keduanya bisa sama-sama salah. Angka ini "
            "hanya menunjukkan berapa banyak baris yang perlu diputuskan manusia."
        ),
    }
    (ANNOT_DIR / "agreement_report.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"kesepakatan aspek (persis)  : {stats['kesepakatan_aspek_persis']:.1%}")
    print(f"kesepakatan sentimen        : {stats['kesepakatan_sentimen']:.1%}")
    print(f"sepakat pada keduanya       : {stats['kesepakatan_keduanya']:.1%}")
    print(f"\nberbeda pada: {stats['beda_pada']}")
    print(f"\nperlu ditinjau manusia      : {len(adjudication)} baris "
          f"({len(disagree)} berbeda + {len(agree_sample)} kontrol)")
    print(f"berkas                      : {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
