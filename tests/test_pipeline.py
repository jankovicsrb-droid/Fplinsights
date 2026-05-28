"""Integration test: run the full pipeline against a real (temp) SQLite DB."""
from fastapi.testclient import TestClient

from fpl_insights.api.main import app
from fpl_insights.db import queries
from fpl_insights.db.sqlite import get_connection, init_db
from fpl_insights.pipeline.update import update_fpl_data


def test_full_pipeline_writes_expected_rows(isolated_paths, mocked_fetch):
    result = update_fpl_data()

    assert result["status"] == "ok"
    assert result["players"] == 3
    assert result["fixtures"] == 3

    counts = queries.get_table_counts()
    assert counts["teams"] == 2
    assert counts["players"] == 3
    assert counts["events"] == 3
    assert counts["fixtures"] == 3
    assert counts["player_history"] == 4  # Saka 2 + Watkins 1 + Raya 1


def test_pipeline_history_count_matches_fixtures(isolated_paths, mocked_fetch):
    update_fpl_data()

    saka_history = queries.get_player_history(1)
    assert len(saka_history) == 2
    assert saka_history[0]["gameweek"] == 15
    assert saka_history[1]["gameweek"] == 14

    watkins_history = queries.get_player_history(2)
    assert len(watkins_history) == 1


def test_query_filters(isolated_paths, mocked_fetch):
    update_fpl_data()

    mids = queries.list_players(position=3)
    assert len(mids) == 1
    assert mids[0]["second_name"] == "Saka"

    cheap = queries.list_players(max_cost=6.0)
    assert {p["second_name"] for p in cheap} == {"Raya"}

    arsenal_players = queries.list_players(team_id=1)
    assert len(arsenal_players) == 2


def test_current_event(isolated_paths, mocked_fetch):
    update_fpl_data()
    current = queries.get_current_event()
    assert current is not None
    assert current["id"] == 16


def test_fixtures_for_gw(isolated_paths, mocked_fetch):
    update_fpl_data()
    gw15 = queries.get_fixtures(gw=15)
    assert len(gw15) == 1
    assert gw15[0]["team_h_name"] == "ARS"
    assert gw15[0]["team_a_name"] == "AVL"
    assert gw15[0]["team_h_score"] == 2


def test_init_db_only(isolated_paths):
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = {row["name"] for row in cur.fetchall()}
    conn.close()
    for expected in {"teams", "players", "events", "fixtures", "player_history",
                     "player_fixtures", "player_history_past", "player_gw_snapshot", "meta"}:
        assert expected in table_names


def test_api_endpoints_smoke(isolated_paths, mocked_fetch):
    update_fpl_data()
    with TestClient(app) as client:
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["db"] == "ok"

        r = client.get("/api/teams")
        assert r.status_code == 200
        teams = r.json()
        assert len(teams) == 2

        r = client.get("/api/players?position=MID")
        assert r.status_code == 200
        mids = r.json()
        assert len(mids) == 1
        assert mids[0]["second_name"] == "Saka"

        r = client.get("/api/players?position=BAD")
        assert r.status_code == 400

        r = client.get("/api/players/1")
        assert r.status_code == 200
        assert r.json()["second_name"] == "Saka"

        r = client.get("/api/players/999")
        assert r.status_code == 404

        r = client.get("/api/players/1/history")
        assert r.status_code == 200
        assert len(r.json()) == 2

        r = client.get("/api/fixtures?gw=15")
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = client.get("/api/admin/status")
        assert r.status_code == 200
        body = r.json()
        assert body["table_counts"]["players"] == 3
        assert body["current_event"]["id"] == 16
