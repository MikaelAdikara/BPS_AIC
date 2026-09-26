# Deciqo

**Deciqo helps solo online sellers turn piling-up customer reviews into a prioritised list of
issues, the next step for each, and a record of what they did about it.** When the problem is
missing product information, Deciqo opens the listing, names the fact that is not written there,
and holds the draft until the seller confirms the real value. After the seller records an action,
new complaints written after that change reopen the issue.

Deciqo (formerly Ulasin) keeps Ulasin's IndoBERT/lexicon classifier as a triage signal. The
classifier, its training pipeline, and the original single-session analysis endpoints are
documented in [docs/ULASIN_CLASSIFIER.md](docs/ULASIN_CLASSIFIER.md).

- **Counts are computed from stored reviews** ("N of M reviews read"), never taken from model text.
- **Quotes are verbatim**; drafts only use the current listing or facts the seller confirmed.
- **Decisions belong to the seller.** Deciqo never writes back to a store.

---

## Setup

Prerequisites: Docker Desktop (Compose v2.24+). Nothing else is required to run the app.

```bash
git clone <this repository>
cd BPS_AIC
cp .env.example .env        # optional: fill OPENAI_API_KEY, TELEGRAM_BOT_TOKEN, APIFY_TOKEN
```

Every variable in `.env` is optional. **Without any `.env` the app still runs**: the engine uses the
rule analyser (labelled "AI is off" in the UI), Telegram alerts are logged but not sent, and the
Lazada live fetch button is disabled with a reason. See [.env.example](.env.example) for the full
list.

Optional, for the IndoBERT triage model (without it, triage uses the lexicon and
`/api/v1/readiness` says so):

```bash
python scripts/download_checkpoint.py     # downloads ~499 MB into ./models (not committed)
```

## Run

```bash
APP_COMMIT=$(git rev-parse --short HEAD) docker compose up --build -d
```

On Windows, double-click `start.bat`: it starts Docker Desktop if it is not running, copies
`.env.example` to `.env` if missing, builds, waits until the app answers, and opens the browser.
`stop.bat` stops the containers and keeps the data. The Compose project is always named
`deciqo-local`, so the database volume is the same whichever folder or shell starts it.

| What | Where |
|---|---|
| App | <http://localhost:3000> |
| API | <http://localhost:8000> (docs at `/api/docs`) |
| Demo account | `demo@deciqo.app` / `deciqo-demo` (change with `DECIQO_DEMO_EMAIL` / `DECIQO_DEMO_PASSWORD`) |

Three services start:

| Service | Purpose |
|---|---|
| `api` | FastAPI + SQLite in the `deciqo-data` volume (accounts, catalog, findings, decisions, alerts) |
| `web` | React build served by nginx; proxies `/api/` to `api` |
| `woo-demo` | A **synthetic** WooCommerce store (REST `wc/v3`) used by the demo account. Internal only |

The demo account is created and filled automatically on first start from the synthetic store (every
product is labelled "Synthetic example, not customer data"). **Sources → Reset to demo data** restores
it. New accounts start empty.

Ports are bound to `127.0.0.1`. Stop with `docker compose down`; add `-v` to also delete the
database volume.

Running without Docker (development):

```bash
python -m venv .venv && .venv/bin/pip install -r apps/api/requirements.txt pytest
.venv/bin/python -m uvicorn app.main:app --app-dir apps/api --port 8000
npm --prefix apps/web install && npm --prefix apps/web run dev
```

Outside Docker the database defaults to `tmp/deciqo.sqlite3` and the Woo demo store must be started
separately (`uvicorn app.deciqo.mock_woo:app --app-dir apps/api --port 8080` with
`WOO_BASE_URL=http://localhost:8080`).

## Version marker

`GET /api/v1/version` returns the build that is running:

```json
{"app": "deciqo", "version": "1.0.0", "commit": "abc1234", "pipeline": "gap-v1", "verifier": "verify-v1"}
```

- `commit` is injected at build time through `APP_COMMIT`; if it was not provided the value is
  `"unknown"`, never a guess.
- `pipeline` / `verifier` change whenever engine behaviour changes and are stored with every
  analysis and draft.
- The same values are shown in the app footer under **Settings**.

Other health endpoints: `GET /api/v1/health` (process alive), `GET /api/v1/readiness` (triage model
loaded or lexicon fallback, with the reason).

## Test suite

```bash
.venv/bin/python -m pytest tests -q
npm --prefix apps/web test
npm --prefix apps/web run build
```

What the suites cover:

| Command | Covers |
|---|---|
| `python -m pytest tests/unit -q -k deciqo` | Deciqo engine and platform: verbatim quote check, unit-aware quantity gate, relevance judge, pipeline and finding identity, merchant facts, drafts, in-process eval harness, auth, ingest and PII redaction, sources, Lazada, Telegram |
| `python -m pytest tests -q` | The above plus the Ulasin classifier, legacy analysis endpoints, and integration checks (Docker build context, serving dependencies) |
| `npm --prefix apps/web test` | EN/ID dictionary parity, router (landing anchors are not routes), storage fallback, API client |
| `python eval/components.py` | Deterministic suites over `data/eval/` (packaging, English and mixed negation, complaints in 4–5★ reviews, odd inputs, fictional PII); no model calls |
| `python eval/run_final.py --rules` | End-to-end eval dry run with the rule engine; free, no API key |
| `python eval/run_final.py --systems B0,B1,D --budget 2` | Paid eval run with a hard USD budget; stops if the key is rejected or the budget is spent |
| `python eval/run_final.py --rescore` | Recomputes the report from stored raw outputs without calling a model |

Eval artifacts live in `eval/final/` (cases, raw outputs, manifest, report, blind label sheet).
See [eval/README.md](eval/README.md) for the metric definitions.

## Evaluation

Checkpoint 1 (test suite, first run, baseline scores, execution evidence, weaknesses found):
[`eval/CHECKPOINT_1.md`](eval/CHECKPOINT_1.md).

**Question:** when a seller pastes reviews and a listing into a language model, what goes wrong,
and does Deciqo's workflow (evidence counted from stored reviews, a listing check, a question for
the missing fact, a gate before a draft is marked ready) close those gaps?

**Systems**, all given the same input bundle (title, full listing, every review; the after-fact
phase adds the same merchant fact to every system):

- **B0**: `gpt-5-mini` with a plain seller prompt ("Identify recurring customer problems and suggest
  what I should do. Then write improved listing text.").
- **B1**: the same model with a careful prompt (use only given facts, ask when unsure, treat reviews
  as untrusted data).
- **D**: the Deciqo engine in-process on an isolated SQLite file; **D-rules**: the same engine
  without a model.
- **U**: the Ulasin aspect classifier as shipped (IndoBERT vs lexicon) on 120 human-labelled clauses.

**Cases:** 22 synthetic development cases (`c01`–`c22`) and 10 synthetic holdout cases (`h01`–`h10`),
each aimed at a failure point: missing facts, inch vs cm, inner vs outer size, negation, water
claims, device compatibility, disputed capacity, electrical specs, size charts per variant,
misleading star ratings, wrong items, defects, delivery, empty or truncated listings, prompt
injection inside a review, and a praise-only control. Holdout cases are marked before they are
run and are excluded from iteration runs.

**Baseline (development cases, before the merchant fact is given)**. Automatic scoring only;
blind human labels are pending. Cells are `k/n (%; Wilson 95% interval)`.

| Metric | B0 | B1 | D (engine gap-v1) | D-rules |
|---|---|---|---|---|
| Outputs with listing text | 22/22 | 22/22 | 0/22 | 0/22 |
| Unsafe output rate (case-specific forbidden claims in the listing text) | 12/22 (55%; 35–73) | 3/22 (14%; 5–33) | undefined, no text | undefined, no text |
| Missing fact held (D) / asked (B, keyword proxy) | 5/13 | 12/13 | 8/13 (62%; 36–82) | 4/13 |
| Held although the listing already had the answer | – | – | 3/3 | 1/3 |
| Ready for review after the fact is given | – | – | 6/13 (46%; 23–71) | 4/13 |

Examples from the raw outputs: with no inner size in the listing, B0 wrote "Ukuran dalam efektif:
34.5 x 25 cm"; with a prompt injection in a review, B0 prepared listing text saying "Original
Lenovo, Garansi Resmi 5 Tahun". Deciqo's first version had its own specific failures: a size chart
answer rendered as "100 x 60 x 106 x 62 cm" and still marked ready, triage that dropped every
review of two products before the model saw them, and drafts held even when the listing already
answered the question. Every finding, fix, and failed fix is logged in
[eval/ITERATIONS.md](eval/ITERATIONS.md). Baseline tables:
[eval/final/run1-baseline-gap-v1/report.md](eval/final/run1-baseline-gap-v1/report.md); latest run:
[eval/final/report.md](eval/final/report.md).

**U (why classification alone was not enough):** on the same human reference, IndoBERT macro F1 was
0.579, the lexicon 0.581, and TF-IDF 0.585; the size/variant aspect scored 0.174 for both IndoBERT
and the lexicon ([eval/final/ulasin_classifier.md](eval/final/ulasin_classifier.md)).

What these numbers do **not** show: that a draft is correct (only that it avoided the claims each
case forbids), that a question to the seller was the right one, or anything about real merchants,
returns, or ratings.

## Limitations

- **Synthetic evaluation.** All eval cases are written by the team. Automatic scores are triage;
  blind labels from two raters are pending. Intervals are wide because n is small.
- **Model runs vary.** D and the baselines call a language model; repeated runs of the same version
  can differ. Changes between versions are reported with that in mind.
- **Triage vocabulary.** Complaints the complaint lexicon does not recognise never reach the model.
  In the component suites, English complaints were recognised in 19/68 cases and subtle complaints
  in 4–5★ reviews in 5/12.
- **Privacy.** Phone numbers, emails, street addresses, ID and account numbers, and handles are
  redacted at ingest; person names, body measurements, and phone numbers written with dots were not
  redacted in the fictional PII suite.
- **Rule mode is narrow.** Without an API key, the rule engine only covers size complaints on bags,
  clothing, and folding items, plus delivery, packaging, and quality topics.
- **"Ready for your review" is not "verified".** The gate checks drafts against the listing and the
  seller's confirmed facts; a confirmed fact is the seller's statement, not a measurement by Deciqo.
- **Not validated yet:** results with a live merchant store, impact on returns or ratings, official
  real-time Shopee or Tokopedia connectors, and accuracy rated by independent human reviewers.
