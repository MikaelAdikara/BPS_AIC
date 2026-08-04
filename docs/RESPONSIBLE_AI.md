# Responsible AI

> **Placeholder (Fase 0).** Diisi lengkap pada Fase 10, merangkum blueprint bagian 36
> (security, privacy, responsible AI) dan kebijakan governance terkait.

## 1. Checklist responsible AI (bagian 36.2)

| Komitmen | Status implementasi |
| --- | --- |
| Setiap rekomendasi punya evidence yang dapat ditelusuri | belum diimplementasikan |
| Tidak ada eksekusi otomatis tindakan bisnis (human-in-the-loop wajib) | belum diimplementasikan |
| Model visual wajib abstain saat tidak yakin | belum diimplementasikan |
| Klaim performa tidak dipublikasikan sebelum evaluasi selesai | berlaku sejak sekarang |
| PII di-mask sebelum data mencapai model manapun | belum diimplementasikan |
| Sumber data scraping didokumentasikan transparan | belum diimplementasikan |

## 2. Privasi dan data pengguna
_Session-only processing, tidak ada penyimpanan permanen data pengguna, tombol hapus eksplisit,
privacy notice sebelum upload. Diisi setelah implementasi ING-09/GOV-01._

## 3. Threat model (bagian 36.1)
_Prompt injection dari teks ulasan, PII leakage, upload berbahaya, path traversal, oversized input._

**Prinsip inti:** teks ulasan adalah **DATA, bukan INSTRUKSI**. Orchestrator dilarang mengikuti
instruksi yang muncul di dalam teks ulasan yang sedang dianalisis. Guardrail ini wajib diuji
sebagai bagian test suite (blueprint bagian 32, 36.1).

## 4. Kepatuhan regulasi
_UU PDP untuk data pribadi pelanggan yang diproses UMKM. Diisi pada Fase 10._

## 5. Batas klaim (bagian 43)
_Ringkasan tiga daftar: yang boleh diklaim, yang hanya boleh setelah pengujian, dan yang tidak
boleh diklaim sama sekali._
