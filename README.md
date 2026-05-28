# fpl-insights

Personal Fantasy Premier League data layer. v1 goal: fetch data from the official FPL API, persist it to SQLite, and serve it through a simple FastAPI JSON interface.

No predictions, no AI, no bot — those come in later phases. This is just *fetch → store → serve*.

## Quickstart

```bash
git clone https://github.com/jankovicsrb-droid/Fplinsights.git
cd Fplinsights

python -m venv .venv
.venv\Scripts\activate         # Windows PowerShell
# source .venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
cp .env.example .env           # optional, fill in FPL_ENTRY_ID later

# Fetch all data (first run takes ~1-2 min — iterates over ~700 players)
python -m scripts.update

# Run the API
uvicorn fpl_insights.api.main:app --reload
```

API is available at `http://localhost:8000`, OpenAPI docs at `http://localhost:8000/docs`.

## Endpoints (v1)

| Method | Path | Returns |
|---|---|---|
| GET  | `/api/health` | Health + DB connectivity |
| GET  | `/api/events` | Gameweek list |
| GET  | `/api/teams`  | PL teams + strength rating |
| GET  | `/api/players?position=MID&max_cost=10.0&limit=20` | Filtered player snapshot |
| GET  | `/api/players/{id}` | Full player record |
| GET  | `/api/players/{id}/history?last_n=5` | Per-GW history for a player |
| GET  | `/api/fixtures?gw=15` | Fixtures for a GW (or all) |
| POST | `/api/admin/update` | Trigger pipeline in the background |
| POST | `/api/admin/update/sync` | Sync update, returns result |
| GET  | `/api/admin/status` | Last update + row counts per table |

## Example

```bash
curl 'http://localhost:8000/api/players?position=MID&max_cost=10.0&limit=10'
curl 'http://localhost:8000/api/admin/status'
```

## Layout

```
fpl_insights/
  config.py              # paths, URLs
  db/                    # SQLite schema + read queries
  pipeline/              # fetch -> normalize -> load
  api/                   # FastAPI app + routers
  utils/                 # http, logger, formatting
scripts/update.py        # CLI entry
tests/                   # pytest, real in-memory SQLite
```

## Roadmap

| Phase | What it adds |
|---|---|
| v1 (now) | Pipeline + read API |
| v2 | Predictions: player model + Monte Carlo (`/api/predictions/{gw}`) |
| v3 | My-team analysis + private leagues + rivals |
| v4 | Telegram bot |
| v5 | AI layer (optional) |

Details in `CLAUDE.md`.
