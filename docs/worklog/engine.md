# Worklog engine

## Checkpoint 1

Selesai dan terbukti (tes `tests/unit/test_deciqo_engine*.py`, `test_deciqo_gate.py`):

- Verifier kutipan: substring setelah normalisasi aman, tanpa fuzzy; pemisah desimal dipertahankan.
- Pemeriksa angka bersatuan di draf: angka dan satuan harus sama persis dengan sumber
  (`gap-v1`/`verify-v1` belum mengonversi satuan).
- Leksikon engine bersama (keluhan, pujian, negasi, kelompok atribut) dan juri relevansi berbasis kode.
  Rating tidak dipakai. Salah kirim dirutekan ke temuan operasional.
- Triage memakai klasifier IndoBERT yang sudah dimuat API bila ada, leksikon bila tidak;
  cache per `version_hash` ulasan + versi model.
- Analyser aturan (cadangan tanpa AI) dengan bentuk output yang sama dengan discovery.
- Discovery + membership lewat Responses API (structured output strict), reservasi anggaran,
  ledger per panggilan, respons `incomplete` = gagal, key ditolak → mode aturan berlabel.
- Pipeline: metrik dan severity dari kode, id temuan dari atribut yang dinormalisasi, rekonsiliasi,
  reopen hanya dari ulasan setelah `acted_at`, alert isu baru tanpa teks ulasan.
- Read model (inbox, summary, channels, products, product view) dan endpoint fakta, draf, keputusan.
- `harness.run_bundle` untuk runner eval.

Keputusan:

- Label model tidak pernah dihitung apa adanya: dukungan dihitung hanya bila kutipan verbatim
  dan juri relevansi setuju. Ini bisa membuang dukungan asli yang kosakatanya belum dikenal
  leksikon; dicatat sebagai risiko untuk diukur di eval.
- Anggaran habis ditangani seperti key ditolak (mode aturan berlabel), bukan analisis gagal,
  supaya merchant tetap melihat temuan yang cakupannya disebut jelas.

Belum (menunggu hasil baseline): konversi satuan, lokasi/sumbu/varian, klaim non-angka berpolaritas,
validasi fakta, pemeriksaan ulang temuan saat versi verifier berubah.
