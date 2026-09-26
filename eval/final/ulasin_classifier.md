# Baseline U: klasifier aspek Ulasin (as-shipped)

Sumber: `ml/evaluation/aspect_human_results.json` (git blob `8db4d5234e13`), dihasilkan `ml/text/evaluate_aspect_human.py`. Tidak dijalankan ulang di sini.

Susunan label: `llm_plus_human`. Rujukan = label manusia saja; label LLM hanya pembanding. Ini lebih lemah daripada dua penilai manusia independen.

- Klausa rujukan: n = 120
- Kesepakatan antar-pelabel: pooled kappa 0.68, kecocokan baris persis 0.53 (n = 120)
- Aspek dengan kappa di bawah 0,4 tidak dapat ditafsirkan: kelengkapan, kemudahan_penggunaan

| Pendekatan | Macro F1 | Micro F1 | F1 ukuran_varian |
|---|---|---|---|
| Leksikon (rule-based) | 0.581 | 0.620 | 0.174 |
| TF-IDF + logistic regression | 0.585 | 0.598 | 0.320 |
| IndoBERT fine-tuned (as-shipped) | 0.579 | 0.614 | 0.174 |
| Label gold-LLM lama (hanya klausa dari gold) | 0.704 | 0.734 | 0.375 |
| Anotator LLM A | 0.660 | 0.716 | 0.552 |

Bacaan: pada rujukan manusia yang sama, IndoBERT fine-tuned setara dengan leksikon dan TF-IDF (selisih macro F1 kurang dari 0,01). Aspek ukuran/varian, yang paling relevan untuk keluhan informasi produk, adalah salah satu yang paling lemah. Klasifikasi aspek saja tidak memberi tahu seller fakta apa yang hilang, tindakan apa yang perlu, atau apakah masalahnya muncul lagi; karena itu klasifier dipertahankan hanya sebagai sinyal triage.

Catatan interval: F1 per kelas di sini dihitung dari support kecil (mis. 9 klausa untuk ukuran_varian), jadi selisih kecil antarpendekatan tidak bermakna.
