"""
FastAPI application entry point.

Endpoints
---------
GET  /health                    -- liveness probe (K8s readiness)
GET  /api/v1/alerts             -- paginated fall event log from MongoDB
POST /api/v1/alerts/{alert_id}/acknowledge
GET  /api/v1/devices            -- registered CSI sensor devices
GET  /api/v1/stats/daily        -- daily fall counts from materialized view
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "fall_sensing"
    postgres_dsn: str = "postgresql+psycopg://user:pass@localhost:5432/fall_sensing"
    log_level: str = "INFO"


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup/shutdown: open DB connections, close on exit."""
    # TODO: initialise motor client, psycopg pool
    yield
    # TODO: close connections


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="Fall Sensing API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # TODO: include routers
    # app.include_router(alerts_router, prefix="/api/v1/alerts")
    # app.include_router(devices_router, prefix="/api/v1/devices")
    # app.include_router(stats_router, prefix="/api/v1/stats")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
