# apps/web - Frontend React + Vite

Competition MVP Tier 1. Referensi: blueprint bagian 14 (wireframe per screen), 29 (arsitektur
frontend), 13.1 (sitemap linear), ADR-009.

## Empat screen - tidak lebih (bagian 13.1, 14)

| Screen | Komponen utama | Referensi |
| --- | --- | --- |
| 1. Landing & Input | `LandingHero`, `UploadPanel`, `DataPreviewTable`, `PrivacyNotice`, `AnalyzeButton` | bagian 14.1 |
| 2. Processing | `ProgressBar`, `StageChecklist`, `FriendlyHint` | bagian 14.2 |
| 3. Analysis Result | `ExecutiveSummary`, `ActionCardList`, `VisualFindingsPanel`, `BenchmarkCard`, `QnaBox` | bagian 14.3 |
| 4. Evidence Detail | `EvidenceHeader`, `OriginalQuoteBlock`, `VisualEvidenceBlock`, `RelatedReviewsList` | bagian 14.4 |

Tidak ada nav bar global, halaman pengaturan, riwayat, atau akun pada Tier 1.

## Aturan UI yang mengikat

- Setiap Action Card wajib tombol **Terima / Tolak / Simpan Nanti** - tidak pernah eksekusi
  otomatis (ADR-013).
- Warna urgensi selalu didampingi **label teks** (aksesibilitas buta warna, bagian 14.3).
- Confidence rendah/abstain memakai **abu-abu, bukan merah** - abstain bukan error (bagian 14.3).
- Bahasa antarmuka sederhana, tanpa istilah teknis; microcopy sudah ditentukan di bagian 14.
- Build menghasilkan static files yang di-serve container ringan - tidak butuh Node runtime saat
  production (bagian 29.1).

_Belum ada implementasi. Dikerjakan pada Fase 6._
