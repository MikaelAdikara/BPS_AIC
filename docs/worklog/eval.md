# Worklog eval

## Checkpoint 1 (baseline)

Selesai dan terbukti:
- 22 kasus development sintetis (`eval/final/cases.jsonl`, sumber `cases_dev.py`), divalidasi
  `eval/validate_cases.py`; semua tag titik rawan tercakup.
- Runner `eval/run_final.py`: B0, B1, D, D-rules; `--budget`, `--rules`, `--rescore`, `--cases`.
  Key ditolak atau anggaran habis menghentikan run. Output mentah, manifest, report dengan
  interval Wilson, lembar label buta.
- Run B0/B1 (70 baris, $0,20), D-rules (35 baris, gratis), D dengan AI (35 baris, $0,10), semua
  tanpa error.
- Angka klasifier Ulasin (U) diringkas dari hasil tersimpan (`eval/final/ulasin_classifier.md`).

Keputusan dan alasannya:
- Pola terlarang diperiksa pada teks listing saja, setelah placeholder, pertanyaan, dan kalimat
  bersyarat dibuang. Alasan: pemeriksaan manual menemukan hit palsu pada teks seperti itu; run
  pertama disimpan di `eval/final/run1-fe2bd1e/` sebagai pembanding.
- Baris D yang diam-diam jatuh ke mode aturan diberi status `fallback_rules`, karena run pertama D
  ternyata berjalan tanpa modul LLM dan akan terbaca sebagai hasil AI.
- Dua hit borderline (c05 B1, c18 B1) dibiarkan dan diserahkan ke label manusia, supaya alat ukur
  tidak disetel mengikuti output.

Ditunda:
- Label manusia buta (dua penilai) belum diisi.
- Kasus holdout ditulis setelah siklus perbaikan pertama.
