from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fpl_insights.api.routers import admin, data
from fpl_insights.db.sqlite import init_db
from fpl_insights.utils.logger import get_logger

logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting fpl-insights API — initializing DB...")
    init_db()
    logger.info("DB ready.")
    yield
    logger.info("API shutting down.")


app = FastAPI(
    title="fpl-insights API",
    description="FPL data — fetched, stored, served. v1: read-only data + admin update.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(data.router)


@app.get("/", tags=["root"])
def root():
    return {
        "service": "fpl-insights",
        "version": "0.1.0",
        "docs": "/docs",
    }
