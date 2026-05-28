"""Archive the current fpl.db as a finished-season snapshot.

Stamps the season label into the `meta` table, then copies fpl.db to
`data/archive/fpl_<season>.db`. The live fpl.db is left untouched so the
next season can keep using it.

Usage:
    python -m scripts.archive_season              # season 2025-2026
    python -m scripts.archive_season 2026-2027
"""
import shutil
import sys
from datetime import datetime, timezone

from fpl_insights.config import ARCHIVE_DIR, DB_PATH
from fpl_insights.db.queries import get_table_counts, set_meta
from fpl_insights.utils.logger import get_logger

logger = get_logger("scripts.archive_season")

DEFAULT_SEASON = "2025-2026"


def archive_season(season: str = DEFAULT_SEASON):
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB not found: {DB_PATH}")

    counts = get_table_counts()
    logger.info(f"Archiving season {season} (row counts: {counts})")

    set_meta("season", season)
    set_meta("season_archived_at", datetime.now(timezone.utc).isoformat())

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    dest = ARCHIVE_DIR / f"fpl_{season}.db"
    if dest.exists():
        raise FileExistsError(f"Archive already exists: {dest}")

    shutil.copy2(DB_PATH, dest)
    logger.info(f"Done. Snapshot written to {dest}")
    return dest


if __name__ == "__main__":
    season = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SEASON
    archive_season(season)
