# fpl-insights — CLAUDE.md

## Šta je ovaj projekat

Personalni Fantasy Premier League data sloj. v1 cilj je *minimum koji vredi*: skinuti podatke iz FPL API-ja, smestiti ih u SQLite, servirati kroz FastAPI JSON endpointe. Bez analize, predikcija, bota i AI-ja u prvoj fazi.

Nije public product. Lokalni run za jednog korisnika.

---

## Faze razvoja

### Faza 1 — Pipeline + read API (TRENUTNA)
- FPL API → SQLite (`pipeline/`)
- Read endpointi (`/api/players`, `/api/fixtures`, `/api/events`, `/api/teams`, ...)
- `/api/admin/update`, `/api/admin/status`, `/api/health`

### Faza 2 — Predikcije
- `models/player_model.py` (port iz starog repo-a, kalibrisan)
- `models/monte_carlo.py`
- `services/prediction_service.py`
- `/api/predictions/{gw}`, `/api/predictions/player/{id}/{gw}`

### Faza 3 — Tim i lige
- `services/team_service.py` — analiza mog tima (entry_id), captain advice
- `services/league_service.py` — privatne lige, rivali, h2h
- Endpointi: `/api/team/{entry_id}`, `/api/leagues`, `/api/rivals`

### Faza 4 — Telegram bot
- `/rank`, `/predictions`, `/team`, `/update`

### Faza 5 — AI sloj (opcioni)
- OpenAI advice za captain/transfer/free-hit
- Mora ostati opcioni — core radi bez njega

---

## Arhitektura

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
│   ├── config.py                 # putanje, URL-ovi, konstante
│   ├── db/
│   │   ├── sqlite.py             # schema, init, konekcija
│   │   └── queries.py            # SVE read SQL — centralizovano
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
│       ├── logger.py             # centralni logger
│       └── formatting.py         # POSITION_MAP, position_label
│
├── scripts/
│   └── update.py                 # python -m scripts.update
│
├── tests/
│   ├── conftest.py
│   ├── fixtures/                 # fixture JSON za pipeline testove
│   └── test_pipeline.py
│
└── data/                         # gitignored
    ├── raw/                      # raw FPL JSON cache
    └── last_update.json
```

---

## Pravila i konvencije

### Opšta
- **Nikad ne dodavati feature koji nije tražen.** Pitati pre.
- **Ne pisati komentare** osim ako logika nije očigledna (workaround, hidden constraint).
- **Logging umesto print** — `utils/logger.py`.
- **Sve SQL upite** držati u `db/queries.py`. Ništa van toga ne sme pisati SQL.
- **API routeri** smeju zvati samo `db/queries.py` i `pipeline/update.py`. Bez biznis logike u routerima.

### Pipeline
- `pipeline/` je stabilan — ne refaktorisati bez razloga.
- Jedini ulaz za update je `pipeline.update.update_fpl_data()`.

### Testovi
- Ne mockati DB. Koristiti real SQLite (in-memory ili temp fajl).
- Fetch može da se mockuje preko fixture JSON-a iz `tests/fixtures/`.

### Šta NE radimo u v1
- Bez `services/` sloja (vraća se u v2 sa predikcijama).
- Bez `models/` (player model i MC dolaze u v2).
- Bez AI, bota, panela.
- Bez auth-a (lokalni run).

### Deployment
- `.env` nikad u git.
- `data/` i `fpl.db` nikad u git.

---

## FPL API endpointi koje koristimo

Bez autentifikacije.
- `/bootstrap-static/` — teams, players, events
- `/fixtures/` — sve fixtures
- `/element-summary/{id}/` — per-player history + upcoming fixtures

Sleep `0.1s` između player summary poziva (rate limit safety).

---

## Stack

- Python 3.11+
- SQLite (`fpl.db`)
- FastAPI + Uvicorn
- Pydantic v2
- requests
- pytest + httpx (za API integration testove)
