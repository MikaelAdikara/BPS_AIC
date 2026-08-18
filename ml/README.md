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

_Belum ada implementasi._
