"""Fase 3 — gerbang go/no-go VIS-01 (blueprint bagian 19.3, 22, 26.2).

Menjalankan CLIP zero-shot pada foto ulasan berlabel manusia, mengalibrasi ambang abstention,
lalu memutuskan **GO / CONDITIONAL GO / NO-GO**. Hasilnya menentukan seberapa kuat klaim visual
boleh ditulis di proposal dan video — bukan sebaliknya.

Tiga hal yang menjaga angkanya tetap sah:

1. **Ambang dikalibrasi pada split terpisah.** Memilih ambang pada foto yang sama dengan yang
   dilaporkan akan menghasilkan angka yang tampak baik tanpa perbaikan nyata.
2. **Split dilakukan per ULASAN, bukan per foto.** Satu ulasan kerap melampirkan empat foto
   yang nyaris identik; membelahnya per foto akan menaruh kembaran di kedua sisi dan
   melambungkan skor.
3. **Kelas dengan contoh terlalu sedikit tidak dilaporkan sebagai capaian.** `kemasan_rusak`
   hanya punya empat label dan dua di antaranya diperiksa dan tampak keliru (LIMITATIONS).

Jalankan:
    python ml/visual/evaluate_gate.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "ml" / "visual"))

from zero_shot import ZeroShotVisual  # noqa: E402

TASK_CSV = REPO / "data" / "annotation" / "visual_labeling_task.csv"
PHOTOS = REPO / "data" / "raw" / "review_photos"
OUT = REPO / "ml" / "evaluation" / "visual_gate.json"

# Kelas yang jumlah labelnya di bawah ini boleh dihitung, tetapi TIDAK dilaporkan
# sebagai capaian. Sepuluh dipilih karena di bawah itu satu kekeliruan saja menggeser
# akurasi kelas lebih dari sepuluh poin.
MIN_N_LAPOR = 10

GRID_CONF = np.round(np.arange(0.30, 0.96, 0.05), 3)
GRID_MARGIN = np.round(np.arange(0.00, 0.51, 0.05), 3)


def load_gold() -> list[dict]:
    rows = []
    for r in csv.DictReader(TASK_CSV.open(encoding="utf-8")):
        if r["sulit_dinilai"].strip():
            # Foto yang manusia sendiri tidak dapat nilai bukan bahan uji akurasi. Ia diuji
            # terpisah: apakah model IKUT abstain di situ (lihat `abstain_pada_sulit`).
            rows.append({**r, "gold": None})
        elif r["label_manusia"].strip():
            rows.append({**r, "gold": r["label_manusia"].strip()})
    return rows


def split_per_ulasan(rows: list[dict], seed: int = 7) -> tuple[list[dict], list[dict]]:
    """Belah per ulasan agar foto kembar tidak jatuh di kedua sisi."""
    kunci = {}
    for r in rows:
        kunci.setdefault(r["review_text"] or r["image_file"], []).append(r)
    grup = list(kunci.values())
    rng = np.random.default_rng(seed)
    rng.shuffle(grup)
    tengah = len(grup) // 2
    kal = [r for g in grup[:tengah] for r in g]
    uji = [r for g in grup[tengah:] for r in g]
    return kal, uji


def ukur(rows: list[dict], skor: dict, conf: float, margin: float) -> dict:
    """Selective accuracy + coverage pada satu pasang ambang."""
    dinilai = [r for r in rows if r["gold"]]
    dijawab, benar = 0, 0
    per_kelas: dict[str, list[int]] = {}
    for r in dinilai:
        s = skor[r["image_file"]]
        label = s.decide(conf, margin)
        if label is None:
            continue
        dijawab += 1
        ok = int(label == r["gold"])
        benar += ok
        per_kelas.setdefault(r["gold"], []).append(ok)

    sulit = [r for r in rows if not r["gold"]]
    abstain_sulit = sum(1 for r in sulit if skor[r["image_file"]].decide(conf, margin) is None)

    return {
        "min_confidence": conf,
        "min_margin": margin,
        "n_dinilai": len(dinilai),
        "n_dijawab": dijawab,
        "coverage": round(dijawab / len(dinilai), 4) if dinilai else 0.0,
        "selective_accuracy": round(benar / dijawab, 4) if dijawab else 0.0,
        "per_kelas": {
            k: {"n": len(v), "akurasi": round(sum(v) / len(v), 4)} for k, v in per_kelas.items()
        },
        "abstain_pada_sulit": f"{abstain_sulit}/{len(sulit)}" if sulit else "-",
    }


def diagnosa_tanpa_abstain(rows: list[dict], skor: dict) -> dict:
    """Matriks kebingungan argmax murni, plus pembanding sepele.

    Selective accuracy pada coverage rendah mudah terlihat baik tanpa berarti apa-apa: bila
    model hanya berani menjawab pada foto kelas mayoritas, angkanya tinggi sementara
    kegunaannya nol. Perbandingan terhadap "selalu tebak `normal`" adalah pemeriksaan yang
    tidak dapat dikelabui oleh pengaturan ambang.
    """
    kelas = ["produk_rusak", "salah_kirim", "kemasan_rusak", "normal"]
    masalah = set(kelas[:3])
    cm = {(g, p): 0 for g in kelas for p in kelas}
    for r in rows:
        if r["gold"]:
            cm[(r["gold"], skor[r["image_file"]].top_label)] += 1

    dinilai = [r for r in rows if r["gold"]]
    benar = sum(cm[(k, k)] for k in kelas)
    gold_m = [r for r in dinilai if r["gold"] in masalah]
    gold_n = [r for r in dinilai if r["gold"] == "normal"]
    ketemu = sum(1 for r in gold_m if skor[r["image_file"]].top_label in masalah)
    alarm = sum(1 for r in gold_n if skor[r["image_file"]].top_label in masalah)

    return {
        "matriks": {g: {p: cm[(g, p)] for p in kelas} for g in kelas},
        "akurasi_argmax": round(benar / len(dinilai), 4),
        "akurasi_selalu_tebak_normal": round(len(gold_n) / len(dinilai), 4),
        "recall_masalah_gabungan": round(ketemu / len(gold_m), 4) if gold_m else 0.0,
        "alarm_palsu_pada_normal": round(alarm / len(gold_n), 4) if gold_n else 0.0,
    }


def putuskan(hasil: dict) -> tuple[str, str]:
    """Terjemahkan angka menjadi keputusan gerbang beserta alasannya."""
    acc, cov = hasil["selective_accuracy"], hasil["coverage"]
    layak = {k: v for k, v in hasil["per_kelas"].items() if v["n"] >= MIN_N_LAPOR}
    if acc >= 0.80 and cov >= 0.50 and len(layak) >= 2:
        return "GO", (
            f"Selective accuracy {acc:.0%} pada coverage {cov:.0%}, dengan {len(layak)} kelas "
            "yang jumlah labelnya memadai. Hasil visual boleh disebut sebagai kapabilitas."
        )
    if acc >= 0.65 and cov >= 0.30:
        return "CONDITIONAL GO", (
            f"Selective accuracy {acc:.0%} pada coverage {cov:.0%}. Cukup untuk ditampilkan "
            "sebagai fitur pendukung yang menyertakan keterbatasannya, TIDAK boleh disebut "
            "sebagai kapabilitas yang terbukti, dan tidak boleh menjadi sorotan video."
        )
    return "NO-GO", (
        f"Selective accuracy {acc:.0%} pada coverage {cov:.0%} tidak cukup untuk klaim apa pun. "
        "Jalur visual tetap ada di kode sebagai komponen yang gracefully degrade, tetapi "
        "hasilnya tidak ditampilkan dan tidak disebut di proposal maupun video."
    )


def main() -> int:
    rows = load_gold()
    if not rows:
        print("Belum ada label. Jalankan pelabelan lebih dulu.", file=sys.stderr)
        return 1
    print(f"{len(rows)} foto berlabel ({sum(1 for r in rows if not r['gold'])} sulit dinilai).")

    hasil_varian = {}
    for lang in ("all", "en"):
        print(f"\n=== Prompt: {lang} ===", flush=True)
        model = ZeroShotVisual(prompt_lang=lang)
        paths = [PHOTOS / r["image_file"] for r in rows]
        skor = {s.image_file: s for s in model.score(paths)}
        print(f"  {len(skor)} foto diskor.", flush=True)

        kal, uji = split_per_ulasan(rows)
        print(f"  kalibrasi {len(kal)} foto · uji {len(uji)} foto", flush=True)

        # Pilih ambang pada split kalibrasi: akurasi tertinggi di antara yang coverage-nya
        # masih layak. Coverage 100% berarti tidak pernah abstain, dan itu justru melanggar
        # syarat abstention wajib pada bagian 19.2.
        kandidat = [ukur(kal, skor, c, m) for c in GRID_CONF for m in GRID_MARGIN]
        layak = [k for k in kandidat if 0.30 <= k["coverage"] <= 0.95]
        terpilih = max(layak or kandidat, key=lambda k: (k["selective_accuracy"], k["coverage"]))

        diag = diagnosa_tanpa_abstain(rows, skor)
        pada_uji = ukur(uji, skor, terpilih["min_confidence"], terpilih["min_margin"])
        keputusan, alasan = putuskan(pada_uji)
        if diag["akurasi_argmax"] <= diag["akurasi_selalu_tebak_normal"]:
            keputusan = "NO-GO"
            alasan = (
                f"Akurasi argmax {diag['akurasi_argmax']:.0%} TIDAK melampaui pembanding sepele "
                f"'selalu tebak normal' ({diag['akurasi_selalu_tebak_normal']:.0%}), dan "
                f"{diag['alarm_palsu_pada_normal']:.0%} foto normal salah ditandai bermasalah. "
                "Selective accuracy yang tampak tinggi hanya dihasilkan oleh abstain pada "
                "hampir seluruh foto bermasalah — model menjawab terutama pada kelas mayoritas."
            )
        print(f"  ambang: conf {terpilih['min_confidence']} margin {terpilih['min_margin']}")
        print(f"  UJI: acc {pada_uji['selective_accuracy']} cov {pada_uji['coverage']}")
        print(f"  argmax {diag['akurasi_argmax']:.0%} vs selalu-normal "
              f"{diag['akurasi_selalu_tebak_normal']:.0%} · alarm palsu "
              f"{diag['alarm_palsu_pada_normal']:.0%}")
        print(f"  -> {keputusan}", flush=True)

        hasil_varian[lang] = {
            "ambang_dari_kalibrasi": {
                "min_confidence": terpilih["min_confidence"],
                "min_margin": terpilih["min_margin"],
                "pada_split_kalibrasi": {
                    "selective_accuracy": terpilih["selective_accuracy"],
                    "coverage": terpilih["coverage"],
                },
            },
            "pada_split_uji": pada_uji,
            "diagnosa_tanpa_abstain": diag,
            "keputusan": keputusan,
            "alasan": alasan,
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "catatan": (
            "Ambang dipilih pada split KALIBRASI dan dilaporkan pada split UJI yang tidak "
            "pernah dilihat saat memilih. Split dilakukan per ULASAN, bukan per foto, karena "
            "satu ulasan kerap melampirkan foto yang nyaris identik."
        ),
        "model": ZeroShotVisual().model_name,
        "n_foto": len(rows),
        "kelas_tidak_dilaporkan": (
            f"Kelas dengan n < {MIN_N_LAPOR} tidak boleh disebut sebagai capaian. Pada batch "
            "ini kemasan_rusak (n=4, dua di antaranya diperiksa dan tampak keliru) dan "
            "salah_kirim (n=7) masuk kategori itu."
        ),
        "varian_prompt": hasil_varian,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDitulis ke {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
