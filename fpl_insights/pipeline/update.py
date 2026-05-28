import json
import time
from datetime import datetime, timezone
from typing import Any, Dict

from fpl_insights.config import LAST_UPDATE_FILE, PLAYER_SUMMARY_SLEEP, RAW_DIR
from fpl_insights.db.sqlite import get_connection, init_db
from fpl_insights.pipeline.fetch import (
    fetch_bootstrap_static,
    fetch_fixtures,
    fetch_player_summary,
)
from fpl_insights.pipeline.load import (
    append_player_gw_snapshot,
    replace_events,
    replace_fixtures,
    replace_player_fixtures,
    replace_player_history,
    replace_player_history_past,
    replace_players,
    replace_teams,
)
from fpl_insights.pipeline.normalize import (
    normalize_events,
    normalize_fixtures,
    normalize_player_fixtures,
    normalize_player_gw_snapshot,
    normalize_player_history,
    normalize_player_history_past,
    normalize_players,
    normalize_teams,
)
from fpl_insights.pipeline.schema_checker import check_schema_change
from fpl_insights.utils.http import create_session
from fpl_insights.utils.logger import get_logger

logger = get_logger("pipeline.update")


def _write_status(payload: Dict[str, Any]):
    LAST_UPDATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_UPDATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def update_fpl_data() -> Dict[str, Any]:
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        logger.info("Initializing DB schema...")
        init_db()

        logger.info("Fetching bootstrap-static...")
        bootstrap = fetch_bootstrap_static(write=False)
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        check_schema_change(RAW_DIR, "bootstrap_static", bootstrap)
        (RAW_DIR / "bootstrap_static.json").write_text(
            json.dumps(bootstrap, indent=2), encoding="utf-8"
        )

        logger.info("Fetching fixtures...")
        fixtures_raw = fetch_fixtures()

        logger.info("Normalizing teams/players/events/fixtures...")
        teams_rows = normalize_teams(bootstrap)
        players_rows = normalize_players(bootstrap)
        events_rows = normalize_events(bootstrap)
        fixtures_rows = normalize_fixtures(fixtures_raw)
        snapshot_time = datetime.now(timezone.utc).isoformat()
        snapshot_rows = normalize_player_gw_snapshot(bootstrap, snapshot_time=snapshot_time)

        conn = get_connection()
        try:
            conn.execute("BEGIN")
            logger.info("Writing teams...")
            replace_teams(teams_rows, conn=conn)
            logger.info("Writing players...")
            replace_players(players_rows, conn=conn)
            logger.info("Writing events...")
            replace_events(events_rows, conn=conn)
            logger.info("Writing fixtures...")
            replace_fixtures(fixtures_rows, conn=conn)
            logger.info("Writing player GW snapshot...")
            append_player_gw_snapshot(snapshot_rows, conn=conn)

            logger.info("Fetching player summaries (this might take a while)...")
            all_history_rows = []
            all_player_fixtures_rows = []
            all_history_past_rows = []
            session = create_session()
            elements = bootstrap["elements"]
            total = len(elements)
            for idx, p in enumerate(elements, start=1):
                pid = p["id"]
                summary = fetch_player_summary(pid, session=session)
                all_history_rows.extend(normalize_player_history(pid, summary))
                all_player_fixtures_rows.extend(normalize_player_fixtures(pid, summary))
                all_history_past_rows.extend(normalize_player_history_past(pid, summary))
                if idx % 100 == 0 or idx == total:
                    logger.info(f"  fetched {idx}/{total} player summaries")
                time.sleep(PLAYER_SUMMARY_SLEEP)

            logger.info("Writing player history...")
            replace_player_history(all_history_rows, conn=conn)
            logger.info("Writing player fixtures...")
            replace_player_fixtures(all_player_fixtures_rows, conn=conn)
            logger.info("Writing player history past...")
            replace_player_history_past(all_history_past_rows, conn=conn)

            conn.commit()
        finally:
            conn.close()

        finished_at = datetime.now(timezone.utc).isoformat()
        result = {
            "status": "ok",
            "started_at": started_at,
            "finished_at": finished_at,
            "players": len(players_rows),
            "fixtures": len(fixtures_rows),
            "history_rows": len(all_history_rows),
        }
        _write_status(result)
        logger.info("Done. fpl.db is updated.")
        return result

    except Exception as exc:
        finished_at = datetime.now(timezone.utc).isoformat()
        result = {
            "status": "error",
            "started_at": started_at,
            "finished_at": finished_at,
            "error": str(exc),
        }
        _write_status(result)
        logger.exception("Update failed")
        raise


def read_last_status() -> Dict[str, Any]:
    if LAST_UPDATE_FILE.exists():
        try:
            return json.loads(LAST_UPDATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}
