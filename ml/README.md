# ml/ - Pipeline model dan evaluasi

Kode training/validasi/evaluasi yang berjalan **di luar runtime inference**. Hasilnya berupa
model artifact dan data artifact yang dikonsumsi `apps/api`.

| Folder | Isi | Fase | Referensi |
| --- | --- | --- | --- |
| `text/` | Harmonisasi dataset, baseline TF-IDF + Logistic Regression, fine-tuning IndoBERT | 1–2 | bagian 26.1 |
| `vision/` | Eksperimen zero-shot CLIP, seleksi threshold, kalibrasi abstention | 3 | bagian 26.2, 19.2 |
| `embeddings/` | Setup BGE-M3 + indexing ke Chroma | 4 | bagian 21 |
| `orchestrator/` | Konfigurasi quantization SEA-LION/Sailor2 | 5 | bagian 17.5 |
| `evaluation/` | Script evaluasi + `experiment_log.md` | 8 | bagian 33, 34 |

## Urutan yang mengikat

1. **Baseline dulu, fine-tuning kemudian.** TF-IDF + Logistic Regression wajib dijalankan dan
   dicatat **sebelum** klaim bahwa model fine-tuned lebih baik (bagian 26.1 langkah 12, bagian 34).
2. **Product-level split**, bukan random per baris - plus verifikasi eksplisit tidak ada leakage
   (bagian 26.1 langkah 6–7).
3. **Seed di-fix dan dicatat** pada setiap script training (bagian 26.1 langkah 18).
4. **Model selection berdasar validation F1 terbaik**, bukan training loss terendah (langkah 16).
5. Model visual: keputusan **go/no-go eksplisit** di akhir Fase 3 sebelum hasil visual boleh
   diklaim di proposal/video (bagian 19.3, 26.2 langkah 12).

## Jalur visual - dua percobaan, satu gerbang

| Skrip | Pendekatan | Status |
| --- | --- | --- |
| [`visual/zero_shot.py`](visual/zero_shot.py) + [`visual/evaluate_gate.py`](visual/evaluate_gate.py) | CLIP zero-shot, prompt ensemble, ambang abstention | **NO-GO** - lihat [`evaluation/visual_gate.json`](evaluation/visual_gate.json) |
| [`visual/linear_probe.py`](visual/linear_probe.py) | Linear probe di atas embedding CLIP **beku** | Ditulis, belum dijalankan - butuh `data/raw/review_photos/` |

Zero-shot gagal bukan karena CLIP tidak melihat apa-apa, melainkan karena ruang teksnya tidak
sejajar dengan pertanyaan produk ini: akurasi argmax 45% tidak melampaui pembanding sepele
"selalu tebak normal" (61%), dan 61% foto yang sebenarnya normal salah ditandai bermasalah.
Linear probe membekukan encoder-nya tetapi mempelajari pemetaan ke kelas dari foto ulasan
Indonesia yang sebenarnya.

`linear_probe.py` memakai pagar yang sama dengan gerbang zero-shot - split per **ulasan** bukan
per foto, ambang dikalibrasi di dalam fold latih, pembanding sepele selalu ikut dilaporkan - plus
dua tambahan yang dituntut oleh ukuran datanya:

- **Cross-validation berulang, bukan satu split.** Dengan 93 foto berlabel, satu split menyisakan
  belasan foto uji; angkanya lebih ditentukan keberuntungan pembagian daripada oleh model. Yang
  dilaporkan adalah rata-rata beserta sebarannya.
- **Dua perumusan.** Empat kelas (bentuk yang dikunci Fase 0) dan biner "perlu diperiksa vs
  tidak". Perumusan biner ada karena `kemasan_rusak` hanya punya 4 label dan `salah_kirim` 7 -
  terlalu sedikit untuk klaim apa pun - sementara menyatukan ketiga kelas masalah menghasilkan 36
  contoh melawan 57, dan kebetulan itulah keputusan yang benar-benar dibutuhkan produk.

**Fotonya tidak ikut di-commit** (`data/raw/` ada di `.gitignore`) dan tidak dapat diunduh ulang
dari berkas label: nama berkasnya berupa hash isi, bukan URL. Susun ulang folder fotonya lewat
`scripts/prepare_apify_photos.py` sebelum menjalankan probe.
