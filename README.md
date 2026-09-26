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

On Windows, double-click `start.bat` (it copies `.env.example` to `.env` if missing, builds, and
opens the browser).

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

<!-- Evaluation, test suite details, and limitations sections follow. -->

## Evaluation

## Limitations
