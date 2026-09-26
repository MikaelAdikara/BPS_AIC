# API engine Deciqo

Kontrak aktual endpoint engine (katalog, analisis, temuan, fakta, draf, keputusan, read model).
Endpoint akun, sumber data, job, status, dan alert dijelaskan di README dan kode `apps/api/app/deciqo/`.

Semua endpoint di bawah butuh sesi (cookie). Tanpa sesi → `401 not_signed_in`. Data akun lain → `404 not_found`.
Error selalu `{"detail": {"code": "...", "message": "..."}}`. Waktu dalam ISO 8601 UTC.

Versi engine: `GET /api/v1/version` → `pipeline` (`PIPELINE_VERSION`) dan `verifier` (`VERIFIER_VERSION`).
Keduanya juga disimpan di setiap baris `analyses` dan di setiap draf (`gate_version`).

## Read model

| Method & path | Respons |
|---|---|
| `GET /api/v1/deciqo/inbox` | `{"items": [InboxItem]}` terurut |
| `GET /api/v1/deciqo/summary` | `{"products", "reviews", "findings_open", "buckets": {recurrence, needs_fact, to_do, monitoring, dismissed, not_detected}, "top": [InboxItem ×≤3], "engine": "ai"|"rules"}` |
| `GET /api/v1/deciqo/channels` | `{"channels": [{"key", "label", "mode", "connected", "synthetic", "status", "last_success_at", "last_error", "products", "reviews", "active_findings"}]}` |
| `GET /api/v1/deciqo/decisions` | `{"decisions": [{finding_id, product_id, product_title, channel, attribute_local, bucket, next_step, score, drivers[], example}], "total", "patterns": [...], "cross_channel": [...], "score_kind": "heuristic"}` |
| `GET /api/v1/deciqo/ledger` | `{"calls": [...], "by_purpose": [{"provider", "purpose", "calls", "cost_usd", "unconfirmed_usd"}], "budget_usd"}` |

Urutan inbox: bucket (`recurrence → needs_fact → to_do → monitoring → dismissed → not_detected`), lalu
severity (`high → low`), lalu support terbanyak.

**Bucket** (diturunkan, tidak disimpan):

| Bucket | Aturan |
|---|---|
| `recurrence` | state `reopened` (keluhan pendukung baru ditulis setelah `acted_at`) |
| `monitoring` | state `acted` |
| `dismissed` | state `dismissed` |
| `not_detected` | analisis sukses terakhir tidak menemukan temuan ini lagi |
| `needs_fact` | listing tersedia, fakta belum ada, dan draf ditahan `needs_merchant_fact` (tipe butuh fakta atau `expectation_mismatch`, dan listing belum menyatakannya secara verbatim) |
| `to_do` | aktif lainnya |

**`next`**: `recurrence`, `fact`, `apply` (draf siap), `draft`, `route` (operasional/kualitas),
`paste_listing` (listing belum ada), `monitoring`, atau `null` (dismissed / not_detected).

**InboxItem**: `id, product_id, product_title, channel, synthetic, image_url, attribute, attribute_local,
finding_type, fix_type, severity, state, bucket, next, engine, listing_fixable, needs_fact, needs_listing,
fact, draft_status, support, denominator, candidates_read, support_is_minimum, example, acted_at,
follow_up, updated_at`.

`draft_status` bernilai `null` untuk temuan yang tidak diperbaiki lewat listing (operasional, kualitas).

## Katalog dan analisis

| Method & path | Body | Respons |
|---|---|---|
| `GET /api/v1/deciqo/products` | – | `{"products": [{id, title, channel, data_origin, synthetic, captured_at, reviews, rating, findings, fixable, analysed_at, engine, analysis_status, stale}]}` |
| `GET /api/v1/deciqo/products/{id}` | – | ProductView |
| `PUT /api/v1/deciqo/products/{id}/listing` | `{"listing": "…"}` | ProductView + `job_id` (analisis ulang bila listing berubah, `null` bila sama) |
| `POST /api/v1/deciqo/products/{id}/analyse` | `{"force"?: bool}` | `202 {"job_id"}` |
| `POST /api/v1/deciqo/analyse-all` | – | `202 {"job_id"}` |
| `POST /api/v1/deciqo/products/{id}/draft` | – | Draft |
| `POST /api/v1/deciqo/products/{id}/vision` | – | ProductView + `vision_run` + `job_id` (lihat "Vision") |

**ProductView**: `product {id, title, channel, url, listing_text, listing_edit_text, listing_provided, data_origin, captured_at,
synthetic, image_url, images[], image_ocr}`, `source {status, last_success_at}`, `stats {reviews, rating, rating_hist, with_photos}`,
`analysis {engine, status, created_at, pipeline_version, verifier_version, note, error, trace[]}`,
`findings [Finding]` (tanpa yang `not_detected`), `not_detected [{id, attribute_local, updated_at}]`,
`draft` (draf tersimpan terakhir atau `null`), `generic_draft` (`null`), `decisions []`,
`reviews [{id, rating, text, variant, review_time, images[]}]`.

- `product.images`: URL gambar utama + galeri, tanpa duplikat (maks 8).
- `product.image_ocr`: `{status: "done"|"skipped"|"pending", images_read, images_total, reason?}`.
  `reason` ∈ `no_images`, `no_api_key`, `key_rejected`, `budget`, `disabled`, `error`.
- `product.listing_text` memuat blok `Teks pada gambar produk:` bila OCR menemukan teks; `listing_edit_text`
  tetap deskripsi yang bisa diedit merchant (tanpa teks gambar).

`analysis.status`: `ready`, `failed` (provider gagal; temuan lama tidak diubah), `pending`.
`analysis.note`: alasan mode aturan bila ada (`no_api_key`, `key_rejected:<alasan>`, `budget_exhausted:…`).

**Finding** (di ProductView) = InboxItem tanpa field produk, ditambah:
`buyer_expectation, merchant_question, needs_measurement, listing_check, metrics, evidence[], contradicting[],
rejected[], uncertain, not_detected_at, vision_summary`.

- `metrics`: `support, denominator, candidates_read, support_is_minimum, share, contradicting,
  hidden_high_star, with_photos, rating_now, rating_without, variants[]`. Semua dihitung kode dari ulasan
  tersimpan yang lolos verifier kutipan dan juri relevansi.
- `evidence[]` / `contradicting[]`: `{review_id, quote, rating, review_time, variant, has_photo}`; `quote`
  selalu potongan verbatim dari ulasan itu. Item `evidence[]` juga membawa `images: string[]` (URL foto
  ulasan itu) dan `vision: {verdict: "supports"|"contradicts"|"inconclusive", reason, model, checked_at} | null`
  (`null` = belum diperiksa). Bila satu ulasan punya beberapa foto yang diperiksa, yang ditampilkan adalah
  vonis terkuat (`supports` > `contradicts` > `inconclusive`).
- `vision_summary`: `{checked, supports, contradicts, inconclusive, skipped_reason?} | null`. `null` bila tidak
  ada item bukti ber-rating ≤3 dengan foto. Hitungan per item bukti. `skipped_reason` (ada bila sebagian
  item layak belum diperiksa) ∈ `no_api_key`, `key_rejected`, `budget`, `disabled`, `error`, `limit`
  (di luar batas foto/temuan per run), `not_run`.
- `rejected[]`: `{review_id, reason}`. Alasan: `quote_not_verbatim`, `quote_too_short`, `unknown_review_id`,
  `complaint_not_about_this_attribute`, `not_about_this_attribute`, `wrong_item_routes_to_operations`,
  `also_reports_wrong_variant`, `labelled_both_ways`, `complaint_without_attribute`.
- `listing_check`: `{status, quote, related[], coverage {chars_checked, chars_total, model_chars, images_read, images_total}, reason?}`.
  Kode memeriksa listing utuh; `model_chars` adalah bagian yang dibaca model. Teks terkait yang hanya ada di luar
  bagian itu memberi status `incomplete_source` (`reason: related_text_beyond_model_window`).
  `status` ∈ `not_provided`, `pending`, `evidence_found`, `not_found_in_checked_content`,
  `verification_failed`, `incomplete_source`, `conflicting`, `not_applicable` (temuan operasional/kualitas).
- `follow_up` (hanya `acted`/`reopened`): `{state: insufficient_data|no_recurrence_observed|recurrence,
  acted_at, after, complaints, undated}`. Hanya ulasan yang ditulis setelah `acted_at` yang dihitung.

## Vision

`POST /api/v1/deciqo/products/{id}/vision` (sinkron) menjalankan OCR gambar produk lalu cek foto pembeli
untuk produk itu, dan mengembalikan ProductView terbaru ditambah:

- `vision_run`: `{ocr: {status, reason, images_read, images_total, changed}, photos: {status, reason?, planned,
  checked, cached, checked_at}}`.
- `job_id`: job analisis ulang bila teks gambar berubah (teks listing yang diperiksa ikut berubah), selain itu `null`.

Hal yang sama dijalankan otomatis di analisis mode AI: OCR sebelum pemeriksaan listing (teks gambar ikut
diperiksa di run yang sama), cek foto setelah temuan disimpan. Vision hanya menambah bukti; tidak membuat,
menghapus, atau mengubah bucket/state/severity temuan. Tanpa key atau anggaran habis: `skipped` dengan alasan,
bukan error, dan analisis tetap sukses. Batas: 3 foto per temuan, 8 temuan per produk per run, 8 gambar produk.
Semua hasil di-cache (`vision_checks`, `image_ocr`); ledger purpose `vision`, reservasi 1500 token per gambar.
`DECIQO_VISION=off` mematikan jalur ini.

## Fakta dan keputusan

| Method & path | Body | Respons |
|---|---|---|
| `POST /api/v1/deciqo/findings/{id}/fact` | `{"value": "32 x 24", "unit"?: "cm", "variant"?: ""}` | `{value, unit, raw_value, location, variant, source, confirmed_at}`; `422 not_a_fact` bila kosong |
| `POST /api/v1/deciqo/findings/{id}/decision` | `{"decision": "acted", "note"}` / `{"decision": "dismissed", "reason"}` / `{"decision": "reopened"}` | Finding; `422 note_required`, `422 reason_required` |

- `reason` untuk dismissed: `false_positive`, `not_relevant`, `wont_fix`.
- Menyimpan fakta memindahkan temuan `open` ke `investigating`. Fakta lama disimpan tidak aktif.
- `reopened` manual mengembalikan temuan ke `open`/`investigating`; bucket `recurrence` hanya untuk
  reopen otomatis dari ulasan baru.

## Draf

```json
{"status": "needs_merchant_fact", "gate_version": "verify-v1",
 "sections": [{"finding_id": "f_…", "status": "needs_merchant_fact", "text": "", "rendered_from": null,
               "held_suggestion": null, "reasons": ["missing_fact"], "unsupported": [], "sources": []}],
 "title_suggestion": {"text": "", "status": "unchanged"}}
```

Section dibuat untuk temuan aktif yang bisa diperbaiki lewat listing. Urutan keputusan:
listing belum ada → `needs_listing`; fakta dibutuhkan tapi belum ada → `needs_merchant_fact`; placeholder
`[[…]]` tersisa → `needs_merchant_fact`; angka bersatuan tanpa sumber → `blocked` (`unsupported_quantity`);
selain itu `ready` ("Ready for your review"). Teks dirender dari jawaban merchant apa adanya
(`rendered_from: "merchant_fact"`). Untuk `expectation_mismatch` tanpa fakta merchant, bila listing sudah
menyatakan atributnya (`listing_check.status = evidence_found`) dan kutipan cocok dengan teks listing,
section menjadi `needs_review`, dengan `reasons: ["already_in_listing"]` dan kutipan pada `sources`.
Teks draf tetap kosong dan `rendered_from` tetap `null`; merchant meninjau penekanan listing.
Section tanpa teks yang dapat dirender juga menjadi `needs_review`, dengan alasan `nothing_rendered`.
Status keseluruhan = section terlemah; tanpa section → `nothing_to_draft`.

## Fungsi in-process untuk evaluasi

`app.deciqo.engine.harness.run_bundle(bundle, db_path=..., engine="ai"|"rules")` menjalankan ingest,
analisis, fakta (opsional), dan draf pada berkas SQLite yang diberikan, dengan akun evaluasi sendiri.
`bundle`: `title`, `listing`, `reviews[{id, rating, text, date?, variant?}]`, `fact?`, `fact_target_words?`.
Hasil: `findings[{id, attribute, attribute_local, finding_type, support_ids, contradict_ids, listing_status,
fact_applied, draft {status, text, reasons}, metrics, …}]`, `engine`, `engine_note`, `pipeline_version`,
`verifier_version`, `usage {input_tokens, cached_tokens, output_tokens, calls, cost_usd}`, `trace`, `errors`.
Tanpa key atau bila key ditolak, `engine` bernilai `rules` dan `engine_note` menyebut alasannya.

## Rencana keputusan

Heuristik yang bisa dijelaskan, bukan optimum atau prediksi profit. Hanya isu di bucket
`recurrence`, `needs_fact`, `to_do`. `score = impact / sqrt(effort_minutes)`.

- `impact` = batas bawah Wilson 95% share keluhan × 100 + min(support, 30) × 1,5 + 3 × keluhan di ★4–5
  + 12 bila tren naik / −6 bila turun (90 hari terakhir vs sebelumnya, ulasan bertanggal saja) + 15 bila
  muncul lagi + 2 × log10(1 + units sold); satu laporan → × 0,3.
- `next_step` dan menit (konstanta, `measured: false`): `paste_listing` 2, `review_draft` 3,
  `edit_listing` 8, `confirm_fact` 10, `change_process` 30, `talk_to_supplier` 45.
- `drivers[].key` ∈ `reach` (`support`, `share`, `confident_share`), `hidden` (`n`), `rising`/`falling`
  (`recent`, `before`), `recurrence`, `units` (`units_sold`, `at_least` = ulasan yang menyebut isu, `projected_min` = ⌊Wilson × units sold⌋ hanya bila `sampling` produk `complete`/`random` dan `at_least` ≥ 2, selain itu `null`; `sampling`; `assumption`),
  `single_report`, `effort` (`step`, `minutes`, `measured`).
- `patterns`: atribut yang sama di beberapa produk; `cross_channel`: judul mirip (≥0,5) di channel
  berbeda. Keduanya `kind: "candidate"`, bukan identitas SKU.

## Pembanding chatbot umum

`POST /api/v1/deciqo/products/{id}/generic` → model dan bundle yang sama dengan engine (judul, listing
yang dibaca model, ulasan tersimpan), prompt seller biasa. Tanpa AI → `503 generic_unavailable`.

```json
{"system": "generic_chatbot", "same_bundle": true, "model": "gpt-5-mini", "prompt_sha": "…",
 "problems": [{"problem": "…", "suggestion": "…"}],
 "sentences": [{"text": "…", "status": "passed|blocked", "reasons": ["unsupported_quantity", "unsupported_claim"],
                "unsupported": ["34 x 24 cm", "kulit asli"]}],
 "passed_text": "…", "counts": {"sentences": 4, "blocked": 2}, "gate_version": "verify-v2.2", "usage": {…}}
```

Setiap kalimat dinilai gerbang yang sama (sumber: listing dan fakta merchant; ulasan bukan sumber).
Kalimat terblokir ditampilkan, tidak dibuang. Hasil terakhir juga ada di `ProductView.generic_draft`.
