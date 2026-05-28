from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks

from fpl_insights.api.schemas import AdminStatus, HealthResponse, UpdateTriggerResponse
from fpl_insights.config import DB_PATH
from fpl_insights.db import queries
from fpl_insights.db.sqlite import get_connection
from fpl_insights.pipeline.update import read_last_status, update_fpl_data
from fpl_insights.utils.logger import get_logger

logger = get_logger("api.admin")
router = APIRouter(prefix="/api", tags=["admin"])


@router.get("/health", response_model=HealthResponse)
def health():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "ok"
    except Exception as exc:
        logger.warning(f"DB health check failed: {exc}")
        db_status = "error"
    return HealthResponse(status="ok", db=db_status)


@router.get("/admin/status", response_model=AdminStatus)
def status():
    return AdminStatus(
        db_path=str(DB_PATH),
        table_counts=queries.get_table_counts(),
        current_event=queries.get_current_event(),
        last_update=read_last_status(),
    )


@router.post("/admin/update", response_model=UpdateTriggerResponse, status_code=202)
def trigger_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_fpl_data)
    return UpdateTriggerResponse(
        status="update_started",
        started_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/admin/update/sync")
def trigger_update_sync():
    return update_fpl_data()
