# fpl-insights — CLAUDE.md

## What this project is

Personal Fantasy Premier League data layer. The v1 goal is *the minimum that's useful*: fetch data from the FPL API, store it in SQLite, and serve it through FastAPI JSON endpoints. No analysis, predictions, bot, or AI in the first phase.

Not a public product. Single-user, local-run.

---

## Phases

### Phase 1 — Pipeline + read API (CURRENT)
- FPL API → SQLite (`pipeline/`)
- Read endpoints (`/api/players`, `/api/fixtures`, `/api/events`, `/api/teams`, ...)
- `/api/admin/update`, `/api/admin/status`, `/api/health`

### Phase 2 — Predictions
- `models/player_model.py` (ported from the old repo, already calibrated)
- `models/monte_carlo.py`
- `services/prediction_service.py`
- `/api/predictions/{gw}`, `/api/predictions/player/{id}/{gw}`

### Phase 3 — Team and leagues
- `services/team_service.py` — my-team analysis (entry_id), captain advice
- `services/league_service.py` — private leagues, rivals, h2h
- Endpoints: `/api/team/{entry_id}`, `/api/leagues`, `/api/rivals`

### Phase 4 — Telegram bot
- `/rank`, `/predictions`, `/team`, `/update`

### Phase 5 — AI layer (optional)
- OpenAI advice for captain/transfer/free-hit
- Must stay optional — core works without it

---

## Architecture

```
fpl-insights/
├── README.md
├── CLAUDE.md
├── requirements.txt
├── .env.example
├── .env                          # gitignored
├── .gitignore
├── fpl.db                        # gitignored (SQLite)
│
├── fpl_insights/
│   ├── __init__.py
│   ├── config.py                 # paths, URLs, constants
│   ├── db/
│   │   ├── sqlite.py             # schema, init, connection
│   │   └── queries.py            # ALL read SQL — centralized
│   ├── pipeline/
│   │   ├── fetch.py              # FPL API wrapper
│   │   ├── normalize.py          # raw JSON → tuples
│   │   ├── load.py               # INSERT/REPLACE
│   │   ├── schema_checker.py     # drift detection
│   │   └── update.py             # orchestrator
│   ├── api/
│   │   ├── main.py               # FastAPI app
│   │   ├── schemas.py            # Pydantic
│   │   └── routers/
│   │       ├── data.py           # /api/players, /teams, /fixtures, /events
│   │       └── admin.py          # /api/health, /admin/update, /admin/status
│   └── utils/
│       ├── http.py               # requests session + retry
│       ├── logger.py             # central logger
│       └── formatting.py         # POSITION_MAP, position_label
│
├── scripts/
│   └── update.py                 # python -m scripts.update
│
├── tests/
│   ├── conftest.py
│   ├── fixtures/                 # fixture JSON for pipeline tests
│   └── test_pipeline.py
│
└── data/                         # gitignored
    ├── raw/                      # raw FPL JSON cache
    └── last_update.json
```

---

## Rules and conventions

### General
- **Never add a feature that wasn't asked for.** Ask first.
- **Don't write comments** unless the logic is non-obvious (workaround, hidden constraint).
- **Logging instead of print** — use `utils/logger.py`.
- **All SQL** lives in `db/queries.py`. Nothing outside it may write SQL.
- **API routers** may only call `db/queries.py` and `pipeline/update.py`. No business logic in routers.

### Pipeline
- `pipeline/` is stable — don't refactor without a reason.
- The only entry point for an update is `pipeline.update.update_fpl_data()`.

### Tests
- Don't mock the DB. Use real SQLite (in-memory or temp file).
- Fetch may be mocked via fixture JSON in `tests/fixtures/`.

### What we DON'T do in v1
- No `services/` layer (returns in v2 with predictions).
- No `models/` (player model and MC arrive in v2).
- No AI, bot, or panel.
- No auth (local-run only).

### Deployment
- `.env` never in git.
- `data/` and `fpl.db` never in git.

---

## FPL API endpoints we use

No authentication required.
- `/bootstrap-static/` — teams, players, events
- `/fixtures/` — all fixtures
- `/element-summary/{id}/` — per-player history + upcoming fixtures

Sleep `0.1s` between player-summary calls (rate-limit safety).

---

## Stack

- Python 3.11+
- SQLite (`fpl.db`)
- FastAPI + Uvicorn
- Pydantic v2
- requests
- pytest + httpx (for API integration tests)
