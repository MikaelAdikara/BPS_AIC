"""Baseline U: klasifier aspek Ulasin as-shipped pada klausa berlabel manusia.

Membaca hasil tersimpan `ml/evaluation/aspect_human_results.json` (dihasilkan
`ml/text/evaluate_aspect_human.py`) dan menulis ringkasan apa adanya ke
`eval/final/ulasin_classifier.md`. Skrip ini tidak menjalankan ulang model: checkpoint IndoBERT
tidak di-commit, dan menjalankan evaluasi tanpa checkpoint akan menimpa hasil dengan "skipped".
Hash blob git berkas sumber dicatat supaya angkanya bisa ditelusuri.

Jalankan: python eval/ulasin_classifier.py
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "ml" / "evaluation" / "aspect_human_results.json"
OUT = REPO / "eval" / "final" / "ulasin_classifier.md"

LABELS = {
    "lexicon_rule_based": "Leksikon (rule-based)",
    "tfidf_logreg": "TF-IDF + logistic regression",
    "indobert_finetuned": "IndoBERT head awal (v1)",
    "indobert_runtime": "IndoBERT runtime (head/ambang yang aktif)",
    "gold_llm_labels_adr017": "Label gold-LLM lama (hanya klausa dari gold)",
    "llm_annotator_a": "Anotator LLM A",
}


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    blob = subprocess.run(["git", "hash-object", str(SRC)], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()
    ev = data["evaluation"]
    agr = data["agreement"]
    lines = [
        "# Baseline U: klasifier aspek Ulasin", "",
        f"Sumber: `ml/evaluation/aspect_human_results.json` (git blob `{blob[:12]}`), dihasilkan "
        "`ml/text/evaluate_aspect_human.py`. Tidak dijalankan ulang di sini.", "",
        f"Susunan label: `{data['setup']}`. Rujukan = label manusia saja; label LLM hanya "
        "pembanding. Ini lebih lemah daripada dua penilai manusia independen.", "",
        f"- Klausa rujukan: n = {ev['n_reference']}",
        f"- Kesepakatan antar-pelabel: pooled kappa {agr['pooled_kappa']:.2f}, kecocokan baris "
        f"persis {agr['exact_row_agreement']:.2f} (n = {agr['n_both']})",
        "- Aspek dengan kappa di bawah 0,4 tidak dapat ditafsirkan: "
        + ", ".join(k for k, v in agr["per_aspect"].items() if not v["interpretable"]), "",
        "| Pendekatan | Macro F1 | Micro F1 | F1 ukuran_varian |",
        "|---|---|---|---|",
    ]
    for key, label in LABELS.items():
        m = ev["models"].get(key)
        if not m or "aspect_macro_f1" not in m:
            lines.append(f"| {label} | – | – | – |")
            continue
        size = m.get("per_class", {}).get("ukuran_varian", {}).get("f1")
        lines.append(f"| {label} | {m['aspect_macro_f1']:.3f} | {m['aspect_micro_f1']:.3f} | "
                     f"{'–' if size is None else f'{size:.3f}'} |")
    lines += [
        "", "Bacaan: bedakan head awal dari runtime yang memakai head dan ambang aktif. "
        "Baris bertanda kosong tidak dijalankan; skor TF-IDF historis tidak membuktikan hasil saat ini. "
        "Aspek ukuran/varian, yang paling relevan untuk "
        "keluhan informasi produk, adalah salah satu yang paling lemah. Klasifikasi aspek saja tidak "
        "memberi tahu seller fakta apa yang hilang, tindakan apa yang perlu, atau apakah masalahnya "
        "muncul lagi; karena itu klasifier dipertahankan hanya sebagai sinyal triage.", "",
        "Catatan interval: F1 per kelas di sini dihitung dari support kecil (mis. 9 klausa untuk "
        "ukuran_varian), jadi selisih kecil antarpendekatan tidak bermakna.",
    ]
    runtime = ev["models"].get("indobert_runtime", {})
    if runtime.get("model_version"):
        lines += ["", f"Runtime terukur: `{runtime['model_version']}`, CPU, "
                  f"{runtime['inference_seconds']:.3f} detik untuk {runtime['n']} klausa "
                  f"({runtime['clauses_per_second']} klausa/detik). Waktu load terpisah: "
                  f"{runtime['load_seconds']:.3f} detik. Ini pengukuran lokal satu run, bukan SLA.",
                  "Hash artefak lengkap tersimpan pada hasil JSON. Dataset ini sudah dipakai "
                  "evaluasi sebelumnya; run ulang adalah regresi, bukan holdout baru."]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ditulis {OUT}")


if __name__ == "__main__":
    main()
