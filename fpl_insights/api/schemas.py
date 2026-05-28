"""Pydantic response schemas for v1 endpoints."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    db: str


class Event(BaseModel):
    id: int
    name: str
    deadline_time: Optional[str] = None
    average_entry_score: Optional[int] = None
    finished: int
    is_current: int
    is_next: int
    most_captained: Optional[int] = None
    most_transferred_in: Optional[int] = None


class Team(BaseModel):
    id: int
    code: Optional[int] = None
    name: str
    short_name: str
    strength: Optional[int] = None
    strength_overall_home: Optional[int] = None
    strength_overall_away: Optional[int] = None
    strength_attack_home: Optional[int] = None
    strength_attack_away: Optional[int] = None
    strength_defence_home: Optional[int] = None
    strength_defence_away: Optional[int] = None
    form: Optional[float] = None
    played: Optional[int] = None
    win: Optional[int] = None
    draw: Optional[int] = None
    loss: Optional[int] = None
    points: Optional[int] = None
    position: Optional[int] = None


class PlayerListItem(BaseModel):
    id: int
    first_name: str
    second_name: str
    team_id: Optional[int] = None
    team: Optional[str] = None
    element_type: int
    now_cost: float
    total_points: int
    form: Optional[float] = None
    points_per_game: Optional[float] = None
    selected_by_percent: Optional[float] = None
    minutes: int
    status: Optional[str] = None
    ep_next: Optional[float] = None
    ep_this: Optional[float] = None
    news: Optional[str] = None
    chance_of_playing_next_round: Optional[int] = None


class PlayerHistoryEntry(BaseModel):
    gameweek: int
    total_points: int
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    bonus_points: Optional[int] = None
    starts: Optional[int] = None
    bps: Optional[int] = None
    ict_index: Optional[float] = None
    influence: Optional[float] = None
    creativity: Optional[float] = None
    threat: Optional[float] = None
    expected_goals: Optional[float] = None
    expected_assists: Optional[float] = None
    expected_goal_involvements: Optional[float] = None
    expected_goals_conceded: Optional[float] = None
    selected: Optional[int] = None
    transfers_balance: Optional[int] = None
    value: Optional[int] = None
    opponent_team: Optional[int] = None
    home: Optional[bool] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    kickoff_time: Optional[str] = None


class Fixture(BaseModel):
    id: int
    event: Optional[int] = None
    team_h: int
    team_a: int
    team_h_name: str
    team_a_name: str
    team_h_score: Optional[int] = None
    team_a_score: Optional[int] = None
    difficulty_home: Optional[int] = None
    difficulty_away: Optional[int] = None
    finished: int
    started: Optional[int] = None
    kickoff_time: Optional[str] = None


class UpdateTriggerResponse(BaseModel):
    status: str
    started_at: str


class AdminStatus(BaseModel):
    db_path: str
    table_counts: Dict[str, int]
    current_event: Optional[Dict[str, Any]] = None
    last_update: Dict[str, Any]
