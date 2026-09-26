# Baseline U: klasifier aspek Ulasin

Sumber: `ml/evaluation/aspect_human_results.json` (git blob `287106879710`), dihasilkan `ml/text/evaluate_aspect_human.py`. Tidak dijalankan ulang di sini.

Susunan label: `llm_plus_human`. Rujukan = label manusia saja; label LLM hanya pembanding. Ini lebih lemah daripada dua penilai manusia independen.

- Klausa rujukan: n = 120
- Kesepakatan antar-pelabel: pooled kappa 0.68, kecocokan baris persis 0.53 (n = 120)
- Aspek dengan kappa di bawah 0,4 tidak dapat ditafsirkan: kelengkapan, kemudahan_penggunaan

| Pendekatan | Macro F1 | Micro F1 | F1 ukuran_varian |
|---|---|---|---|
| Leksikon (rule-based) | 0.581 | 0.620 | 0.174 |
| TF-IDF + logistic regression | – | – | – |
| IndoBERT head awal (v1) | 0.579 | 0.614 | 0.174 |
| IndoBERT runtime (head/ambang yang aktif) | 0.585 | 0.636 | 0.231 |
| Label gold-LLM lama (hanya klausa dari gold) | 0.704 | 0.734 | 0.375 |
| Anotator LLM A | 0.660 | 0.716 | 0.552 |

Bacaan: bedakan head awal dari runtime yang memakai head dan ambang aktif. Baris bertanda kosong tidak dijalankan; skor TF-IDF historis tidak membuktikan hasil saat ini. Aspek ukuran/varian, yang paling relevan untuk keluhan informasi produk, adalah salah satu yang paling lemah. Klasifikasi aspek saja tidak memberi tahu seller fakta apa yang hilang, tindakan apa yang perlu, atau apakah masalahnya muncul lagi; karena itu klasifier dipertahankan hanya sebagai sinyal triage.

Catatan interval: F1 per kelas di sini dihitung dari support kecil (mis. 9 klausa untuk ukuran_varian), jadi selisih kecil antarpendekatan tidak bermakna.

Runtime terukur: `indobert-nlp01@thr0.3+asp-v2`, CPU, 3.964 detik untuk 120 klausa (30.28 klausa/detik). Waktu load terpisah: 3.019 detik. Ini pengukuran lokal satu run, bukan SLA.
Hash artefak lengkap tersimpan pada hasil JSON. Dataset ini sudah dipakai evaluasi sebelumnya; run ulang adalah regresi, bukan holdout baru.
