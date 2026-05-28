from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from fpl_insights.api.schemas import (
    Event,
    Fixture,
    PlayerHistoryEntry,
    PlayerListItem,
    Team,
)
from fpl_insights.db import queries
from fpl_insights.utils.formatting import position_code

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/events", response_model=List[Event])
def list_events():
    return queries.get_all_events()


@router.get("/teams", response_model=List[Team])
def list_teams():
    return queries.get_all_teams()


@router.get("/players", response_model=List[PlayerListItem])
def list_players(
    position: Optional[str] = Query(None, description="GK|DEF|MID|FWD"),
    team_id: Optional[int] = Query(None, ge=1),
    max_cost: Optional[float] = Query(None, gt=0),
    include_unavailable: bool = Query(True),
    order_by: str = Query("total_points"),
    limit: Optional[int] = Query(None, ge=1, le=1000),
):
    pos_code = None
    if position is not None:
        pos_code = position_code(position)
        if pos_code is None:
            raise HTTPException(status_code=400, detail=f"Invalid position '{position}'. Use GK|DEF|MID|FWD.")

    return queries.list_players(
        position=pos_code,
        team_id=team_id,
        max_cost=max_cost,
        include_unavailable=include_unavailable,
        order_by=order_by,
        limit=limit,
    )


@router.get("/players/{player_id}")
def get_player(player_id: int):
    player = queries.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    return player


@router.get("/players/{player_id}/history", response_model=List[PlayerHistoryEntry])
def get_player_history(player_id: int, last_n: Optional[int] = Query(None, ge=1)):
    player = queries.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    return queries.get_player_history(player_id, last_n=last_n)


@router.get("/fixtures", response_model=List[Fixture])
def list_fixtures(gw: Optional[int] = Query(None, ge=1, le=38)):
    return queries.get_fixtures(gw=gw)
