"""
Pytest fixtures for fpl-insights tests.

- Uses a real SQLite file in tmp_path (no mocks).
- Patches DB_PATH, RAW_DIR, and LAST_UPDATE_FILE to point inside tmp_path.
- Patches pipeline.fetch.* to read fixture JSON instead of hitting FPL API.
"""
import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _load_fixture(name: str):
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture
def isolated_paths(tmp_path, monkeypatch):
    """Redirect DB_PATH, RAW_DIR, LAST_UPDATE_FILE into tmp_path."""
    db_path = tmp_path / "test.db"
    data_dir = tmp_path / "data"
    raw_dir = data_dir / "raw"
    players_raw_dir = raw_dir / "players"
    last_update = data_dir / "last_update.json"

    raw_dir.mkdir(parents=True, exist_ok=True)
    players_raw_dir.mkdir(parents=True, exist_ok=True)

    import fpl_insights.config as config
    import fpl_insights.db.sqlite as sqlite_mod
    import fpl_insights.pipeline.fetch as fetch_mod
    import fpl_insights.pipeline.update as update_mod
    import fpl_insights.api.routers.admin as admin_router

    monkeypatch.setattr(config, "DB_PATH", db_path)
    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(config, "RAW_DIR", raw_dir)
    monkeypatch.setattr(config, "PLAYERS_RAW_DIR", players_raw_dir)
    monkeypatch.setattr(config, "LAST_UPDATE_FILE", last_update)

    monkeypatch.setattr(sqlite_mod, "DB_PATH", db_path)
    monkeypatch.setattr(fetch_mod, "RAW_DIR", raw_dir)
    monkeypatch.setattr(fetch_mod, "PLAYERS_RAW_DIR", players_raw_dir)
    monkeypatch.setattr(update_mod, "RAW_DIR", raw_dir)
    monkeypatch.setattr(update_mod, "LAST_UPDATE_FILE", last_update)
    monkeypatch.setattr(admin_router, "DB_PATH", db_path)

    return {
        "db_path": db_path,
        "data_dir": data_dir,
        "raw_dir": raw_dir,
        "last_update": last_update,
    }


@pytest.fixture
def mocked_fetch(monkeypatch):
    """Replace pipeline.fetch.* with fixture-loading stubs."""
    bootstrap = _load_fixture("bootstrap_static.json")
    fixtures_data = _load_fixture("fixtures.json")
    summaries = {
        1: _load_fixture("player_summary_1.json"),
        2: _load_fixture("player_summary_2.json"),
        3: _load_fixture("player_summary_3.json"),
    }

    def fake_bootstrap(write=True):
        return bootstrap

    def fake_fixtures():
        return fixtures_data

    def fake_summary(player_id, session=None, write=True):
        return summaries[player_id]

    import fpl_insights.pipeline.fetch as fetch_mod
    import fpl_insights.pipeline.update as update_mod

    monkeypatch.setattr(fetch_mod, "fetch_bootstrap_static", fake_bootstrap)
    monkeypatch.setattr(fetch_mod, "fetch_fixtures", fake_fixtures)
    monkeypatch.setattr(fetch_mod, "fetch_player_summary", fake_summary)
    monkeypatch.setattr(update_mod, "fetch_bootstrap_static", fake_bootstrap)
    monkeypatch.setattr(update_mod, "fetch_fixtures", fake_fixtures)
    monkeypatch.setattr(update_mod, "fetch_player_summary", fake_summary)

    # Skip the per-player sleep in tests.
    import fpl_insights.config as config
    monkeypatch.setattr(config, "PLAYER_SUMMARY_SLEEP", 0)
    monkeypatch.setattr(update_mod, "PLAYER_SUMMARY_SLEEP", 0)

    return {"bootstrap": bootstrap, "fixtures": fixtures_data, "summaries": summaries}
