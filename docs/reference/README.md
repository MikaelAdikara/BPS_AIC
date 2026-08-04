# docs/reference/ — Dokumen rujukan (bukan kode)

Folder ini berisi dokumen riset dan desain yang menjadi **sumber kebenaran** implementasi.
Jangan diedit sebagai bagian dari pekerjaan koding — perubahan keputusan harus diedit di dokumen
ini **lebih dulu**, baru diikuti kodenya, agar dokumen tetap satu sumber kebenaran yang konsisten.

| File | Isi | Di-commit? |
| --- | --- | --- |
| `INSIGHTULASAN_BLUEPRINT.md` | Blueprint sistem dan produk lengkap, 50 bagian — sumber kebenaran utama untuk semua keputusan implementasi | ya |
| `AIC_RESEARCH_DOSSIER.md` | Dasar riset v6: masalah, evidence, dataset, kompetitor, keputusan arsitektur v1–v6 — rujukan untuk alasan "kenapa" | ya |
| `PROMPT_CLAUDE_CODE.md` | Instruksi eksekusi fase 0–10 dan batasan non-negotiable | ya |
| `InsightUlasan_Full_System_Product_Blueprint.docx` | Versi Word dari blueprint (isi identik) | tidak (gitignore) |
| `AIC_Smart_Commerce_Research_Dossier.pdf` | Versi PDF dari dossier (isi identik) | tidak (gitignore) |
| `[AIC] AI Innovation Challenge_compressed (1).pdf` | Rulebook resmi panitia | tidak (gitignore) |

File biner (`.pdf`, `.docx`) sengaja di-gitignore: isinya duplikat dari versi markdown, dan
rulebook adalah dokumen milik panitia — repository kompetisi bersifat publik.

## Cara merujuk

Gunakan nomor bagian, mis. "blueprint bagian 22.2" atau "dossier bagian 21B.6", supaya rujukan
tidak ambigu.

**Catatan penomoran:** sebagian rujukan silang di dalam blueprint mengacu pada penomoran draf
sebelumnya dan bergeser dari daftar isi final — mis. teks yang menyebut "bagian 24 tool contracts"
sebenarnya ada di bagian **27.3**, "bagian 34 evaluasi" ada di bagian **33**, dan "go/no-go gate
bagian 22" ada di bagian **19.3 + 26.2**. Ikuti judul bagiannya, bukan nomor mentahnya, bila
keduanya berbeda.
