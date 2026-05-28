"""
Centralized read queries for the v1 API. All SQL in the project lives here.
"""
from typing import Any, Dict, List, Optional

from fpl_insights.db.sqlite import get_connection


def get_all_teams() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, code, name, short_name, strength,
               strength_overall_home, strength_overall_away,
               strength_attack_home, strength_attack_away,
               strength_defence_home, strength_defence_away,
               form, played, win, draw, loss, points, position
        FROM teams
        ORDER BY position IS NULL, position, name
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_events() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, deadline_time, average_entry_score,
               finished, is_current, is_next, most_captained, most_transferred_in
        FROM events
        ORDER BY id
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_current_event() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, deadline_time, finished, is_current, is_next
        FROM events
        WHERE is_current = 1
        LIMIT 1
        """
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def list_players(
    position: Optional[int] = None,
    team_id: Optional[int] = None,
    max_cost: Optional[float] = None,
    include_unavailable: bool = True,
    order_by: str = "total_points",
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Filtered player snapshot. `position` is element_type (1=GK, 2=DEF, 3=MID, 4=FWD).
    """
    allowed_order = {
        "total_points": "p.total_points DESC",
        "now_cost": "p.now_cost DESC",
        "form": "p.form DESC",
        "selected_by_percent": "p.selected_by_percent DESC",
        "ep_next": "p.ep_next DESC",
    }
    order_clause = allowed_order.get(order_by, allowed_order["total_points"])

    query = [
        "SELECT p.id, p.first_name, p.second_name, p.team_id, t.short_name AS team,",
        "       p.element_type, p.now_cost, p.total_points, p.form, p.points_per_game,",
        "       p.selected_by_percent, p.minutes, p.status, p.ep_next, p.ep_this,",
        "       p.news, p.chance_of_playing_next_round",
        "FROM players p",
        "LEFT JOIN teams t ON t.id = p.team_id",
        "WHERE 1=1",
    ]
    params: list = []

    if position is not None:
        query.append("AND p.element_type = ?")
        params.append(position)
    if team_id is not None:
        query.append("AND p.team_id = ?")
        params.append(team_id)
    if max_cost is not None:
        query.append("AND p.now_cost <= ?")
        params.append(max_cost)
    if not include_unavailable:
        query.append("AND p.status NOT IN ('i', 's', 'u', 'o')")

    query.append(f"ORDER BY {order_clause}")
    if limit is not None:
        query.append("LIMIT ?")
        params.append(limit)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(" ".join(query), params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_player(player_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.*, t.short_name AS team_short, t.name AS team_name
        FROM players p
        LEFT JOIN teams t ON t.id = p.team_id
        WHERE p.id = ?
        """,
        (player_id,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_player_history(player_id: int, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT gameweek, total_points, minutes, goals_scored, assists, clean_sheets,
               bonus_points, starts, bps, ict_index, influence, creativity, threat,
               expected_goals, expected_assists, expected_goal_involvements,
               expected_goals_conceded, selected, transfers_balance, value,
               opponent_team, home, home_score, away_score, kickoff_time
        FROM player_history
        WHERE player_id = ?
        ORDER BY gameweek DESC
    """
    params: list = [player_id]
    if last_n is not None:
        query += " LIMIT ?"
        params.append(last_n)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_fixtures(gw: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    query = [
        "SELECT f.id, f.event, f.team_h, f.team_a,",
        "       th.short_name AS team_h_name, ta.short_name AS team_a_name,",
        "       f.team_h_score, f.team_a_score,",
        "       f.difficulty_home, f.difficulty_away,",
        "       f.finished, f.started, f.kickoff_time",
        "FROM fixtures f",
        "JOIN teams th ON th.id = f.team_h",
        "JOIN teams ta ON ta.id = f.team_a",
    ]
    params: list = []
    if gw is not None:
        query.append("WHERE f.event = ?")
        params.append(gw)
    query.append("ORDER BY f.kickoff_time, f.id")

    cur.execute(" ".join(query), params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_meta(key: str, value: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()
    conn.close()


def get_meta(key: str) -> Optional[str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM meta WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row["value"] if row else None


def get_table_counts() -> Dict[str, int]:
    tables = ["teams", "players", "events", "fixtures", "player_history"]
    conn = get_connection()
    cur = conn.cursor()
    counts: Dict[str, int] = {}
    for t in tables:
        cur.execute(f"SELECT COUNT(*) AS c FROM {t}")
        counts[t] = int(cur.fetchone()["c"])
    conn.close()
    return counts
