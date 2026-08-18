"""Susun berkas tugas anotasi manual untuk GOLD TEST SET (ADR-015).

Gold test set adalah SATU-SATUNYA sumber angka yang boleh masuk proposal untuk NLP-01.
Metrik pada label silver hanya mengukur kecocokan terhadap labeling function.

Desain sampling:
  - Diambil HANYA dari split `test` sehingga produknya terpisah dari data latih
    (product-level split, bagian 26.1 langkah 6) - gold otomatis jadi held-out sejati.
  - Bertingkat per aspek supaya aspek minoritas (rasa, kelengkapan, kemudahan_penggunaan)
    tetap punya cukup baris untuk dihitung F1-nya, bukan hanya aspek mayoritas.
  - Menyertakan kuota klausa yang labeling function-nya menyatakan TANPA aspek - tanpa ini,
    presisi LF tidak dapat diukur (hanya recall-nya).

Label silver SENGAJA TIDAK disertakan di berkas anotasi untuk menghindari anchoring bias:
pelabel yang melihat tebakan mesin cenderung menyetujuinya. Perbandingan silver vs gold
dilakukan belakangan lewat join pada `clause_id`.

Pemakaian:
    python ml/text/make_gold_task.py --n 500
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lexicon import ALL_ASPECTS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = REPO_ROOT / "data" / "processed"
OUT_DIR = REPO_ROOT / "data" / "annotation"

SEED = 42
PER_ASPECT_QUOTA = 30  # baris minimum per aspek supaya F1 per kelas bermakna
NO_ASPECT_QUOTA = 120  # untuk mengukur presisi LF, bukan hanya recall


def build_sample(test: pd.DataFrame, target_n: int) -> pd.DataFrame:
    rng_state = SEED
    picked: list[pd.DataFrame] = []
    used: set[str] = set()

    for aspect in ALL_ASPECTS:
        pool = test[(test[f"asp_{aspect}"] == 1) & (~test["clause_id"].isin(used))]
        take = pool.sample(min(PER_ASPECT_QUOTA, len(pool)), random_state=rng_state)
        used.update(take["clause_id"])
        picked.append(take)

    pool = test[(test["n_aspects"] == 0) & (~test["clause_id"].isin(used))]
    take = pool.sample(min(NO_ASPECT_QUOTA, len(pool)), random_state=rng_state)
    used.update(take["clause_id"])
    picked.append(take)

    sample = pd.concat(picked, ignore_index=True)

    # Sisa kuota diisi acak supaya distribusinya tidak seluruhnya hasil stratifikasi.
    remaining = target_n - len(sample)
    if remaining > 0:
        pool = test[~test["clause_id"].isin(used)]
        sample = pd.concat(
            [sample, pool.sample(min(remaining, len(pool)), random_state=rng_state)],
            ignore_index=True,
        )

    return sample.sample(frac=1.0, random_state=rng_state).reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=500, help="target jumlah klausa dianotasi")
    args = parser.parse_args()

    path = PROCESSED / "clauses_test_silver.csv"
    if not path.exists():
        print("Jalankan ml/text/build_dataset.py lebih dulu.", file=sys.stderr)
        return 1

    test = pd.read_csv(path)
    sample = build_sample(test, args.n)

    task = pd.DataFrame({
        "clause_id": sample["clause_id"],
        "clause_text": sample["clause_text"],
        "category_produk": sample["category"],
        # Kolom di bawah DIISI PELABEL. Aspek: tulis 1 jika klausa membicarakan aspek itu.
        **{f"asp_{a}": "" for a in ALL_ASPECTS},
        "sentimen": "",   # positif | negatif | netral
        "severity": "",   # rendah | sedang | tinggi (isi hanya jika sentimen negatif)
        "catatan_pelabel": "",
    })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "gold_annotation_task.csv"
    task.to_csv(out, index=False, encoding="utf-8-sig")  # BOM supaya Excel benar membaca UTF-8

    guide = OUT_DIR / "PANDUAN_ANOTASI.md"
    guide.write_text(_annotation_guide(len(task)), encoding="utf-8")

    print(f"berkas anotasi : {out.relative_to(REPO_ROOT)}  ({len(task)} klausa)")
    print(f"panduan        : {guide.relative_to(REPO_ROOT)}")
    print("\ndistribusi aspek pada sampel (menurut label silver, tidak ditampilkan ke pelabel):")
    for aspect in ALL_ASPECTS:
        print(f"   {aspect:26s} {int(sample[f'asp_{aspect}'].sum())}")
    print(f"   {'(tanpa aspek)':26s} {int((sample['n_aspects'] == 0).sum())}")
    return 0


def _annotation_guide(n: int) -> str:
    aspects = "\n".join(f"- `asp_{a}`" for a in ALL_ASPECTS)
    return f"""# Panduan Anotasi Gold Test Set

Berkas: `gold_annotation_task.csv` ({n} klausa)

Gold test set ini adalah **satu-satunya sumber angka NLP-01 yang boleh masuk proposal**
(ADR-015). Karena itu kualitas anotasi di sini menentukan kredibilitas seluruh klaim model.

## Aturan umum

1. **Labeli apa yang tertulis, bukan yang Anda duga dimaksud.** Kalau klausa tidak cukup
   jelas, isi `catatan_pelabel` dan tetap ambil keputusan terbaik.
2. Satu klausa boleh punya **lebih dari satu aspek**, boleh juga **tidak punya aspek sama
   sekali** (mis. "terima kasih gan"). Klausa tanpa aspek adalah label yang sah, bukan
   kesalahan - biarkan seluruh kolom aspek kosong.
3. Jangan melihat tebakan sistem sebelum melabeli. Berkas ini sengaja tidak memuatnya.

## Kolom aspek - isi `1` jika klausa membicarakan aspek tersebut, biarkan kosong jika tidak

{aspects}

Acuan definisi tiap aspek ada di `configs/taxonomy.yaml` (status FROZEN).
Catatan khusus: untuk kategori F&B, `asp_ukuran_varian` dipakai untuk keluhan
**porsi/takaran**; untuk kerajinan, untuk **dimensi produk**.

## Kolom `sentimen` - wajib diisi salah satu

| Nilai | Kapan dipakai |
| --- | --- |
| `positif` | Klausa menyampaikan kepuasan/pujian |
| `negatif` | Klausa menyampaikan keluhan/kekecewaan |
| `netral` | Pernyataan datar tanpa arah jelas, atau sekadar deskripsi/pertanyaan |

Perhatikan **negasi** ("bukan jelek kok" = positif) dan **sarkasme** ("mantap banget nih
ditipu" = negatif). Dua hal ini adalah titik paling sering salah.

## Kolom `severity` - isi HANYA jika sentimen negatif

| Nilai | Kapan dipakai |
| --- | --- |
| `tinggi` | Kerugian nyata bagi pembeli: barang rusak, salah kirim, tidak sampai, palsu |
| `sedang` | Mengganggu tapi masih dapat ditoleransi: pengiriman lambat, kemasan penyok |
| `rendah` | Keluhan ringan/preferensi: warna kurang cerah, harga agak mahal |

## Kualitas anotasi

- Jika lebih dari satu orang melabeli, **sisihkan 50 klausa yang dilabeli semua pelabel**
  untuk menghitung inter-annotator agreement (bagian 26.2 langkah 6). Catat hasilnya di
  `ml/evaluation/experiment_log.md`.
- Simpan hasil sebagai `data/annotation/gold_annotation_done.csv` dengan kolom yang sama.
- Berkas gold ini **boleh di-commit** (ukurannya kecil dan esensial untuk reproducibility
  evaluasi), berbeda dari data latih yang tidak di-commit.
"""


if __name__ == "__main__":
    raise SystemExit(main())
