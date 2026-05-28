# fpl-insights

Personalni Fantasy Premier League data sloj. v1 cilj: skinuti podatke iz zvaničnog FPL API-ja, pohraniti ih u SQLite, i servirati ih kroz jednostavan FastAPI JSON interfejs.

Bez predikcija, bez AI, bez bota — sve to dolazi u kasnijim fazama. Ovo je samo *fetch → store → serve*.

## Quickstart

```bash
git clone https://github.com/jankovicsrb-droid/Fplinsights.git
cd Fplinsights

python -m venv .venv
.venv\Scripts\activate         # Windows PowerShell
# source .venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
cp .env.example .env           # opcionalno, popuni FPL_ENTRY_ID kasnije

# Skini sve podatke (prvi run traje ~1-2 min jer ide kroz ~700 igrača)
python -m scripts.update

# Pokreni API
uvicorn fpl_insights.api.main:app --reload
```

API je dostupan na `http://localhost:8000`, OpenAPI docs na `http://localhost:8000/docs`.

## Endpointi (v1)

| Method | Path | Šta vraća |
|---|---|---|
| GET  | `/api/health` | Health + DB konekcija |
| GET  | `/api/events` | Lista gameweek-ova |
| GET  | `/api/teams`  | PL ekipe + strength rating |
| GET  | `/api/players?position=MID&max_cost=10.0&limit=20` | Filtrirani igrači |
| GET  | `/api/players/{id}` | Pun player snapshot |
| GET  | `/api/players/{id}/history?last_n=5` | Per-GW istorija igrača |
| GET  | `/api/fixtures?gw=15` | Fixtures za GW (ili sve) |
| POST | `/api/admin/update` | Trigger pipeline u pozadini |
| POST | `/api/admin/update/sync` | Sinhroni update, vraća rezultat |
| GET  | `/api/admin/status` | Last update + broj redova po tabeli |

## Primer

```bash
curl 'http://localhost:8000/api/players?position=MID&max_cost=10.0&limit=10'
curl 'http://localhost:8000/api/admin/status'
```

## Struktura

```
fpl_insights/
  config.py              # putanje, URL-ovi
  db/                    # SQLite schema + read queries
  pipeline/              # fetch -> normalize -> load
  api/                   # FastAPI app + routers
  utils/                 # http, logger, formatting
scripts/update.py        # CLI entry
tests/                   # pytest, real in-memory SQLite
```

## Roadmap

| Faza | Šta donosi |
|---|---|
| v1 (now) | Pipeline + read API |
| v2 | Predikcije: player model + Monte Carlo (`/api/predictions/{gw}`) |
| v3 | Analiza mog tima + privatne lige + rivali |
| v4 | Telegram bot |
| v5 | AI sloj (opcioni) |

Detalji u `CLAUDE.md`.
