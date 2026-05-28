from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DB_PATH = ROOT_DIR / "fpl.db"

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PLAYERS_RAW_DIR = RAW_DIR / "players"
LAST_UPDATE_FILE = DATA_DIR / "last_update.json"

FPL_API_BASE = "https://fantasy.premierleague.com/api"
BOOTSTRAP_URL = f"{FPL_API_BASE}/bootstrap-static/"
FIXTURES_URL = f"{FPL_API_BASE}/fixtures/"
PLAYER_SUMMARY_URL = f"{FPL_API_BASE}/element-summary/{{player_id}}/"

PLAYER_SUMMARY_SLEEP = 0.1
