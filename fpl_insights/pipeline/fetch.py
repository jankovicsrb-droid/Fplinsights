import json
from typing import Any, Dict, List

import requests

from fpl_insights.config import (
    BOOTSTRAP_URL,
    FIXTURES_URL,
    PLAYER_SUMMARY_URL,
    PLAYERS_RAW_DIR,
    RAW_DIR,
)
from fpl_insights.utils.http import DEFAULT_TIMEOUT, create_session


def ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PLAYERS_RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_bootstrap_static(write: bool = True) -> Dict[str, Any]:
    ensure_dirs()
    session = create_session()
    resp = session.get(BOOTSTRAP_URL, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if write:
        (RAW_DIR / "bootstrap_static.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )
    return data


def fetch_fixtures() -> List[Dict[str, Any]]:
    ensure_dirs()
    session = create_session()
    resp = session.get(FIXTURES_URL, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    (RAW_DIR / "fixtures.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )
    return data


def fetch_player_summary(
    player_id: int,
    session: requests.Session | None = None,
    write: bool = True,
) -> Dict[str, Any]:
    ensure_dirs()
    url = PLAYER_SUMMARY_URL.format(player_id=player_id)
    sess = session or create_session()
    resp = sess.get(url, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if write:
        (PLAYERS_RAW_DIR / f"{player_id}.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )
    return data
