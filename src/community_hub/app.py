"""FastAPI application for the ORGAN-VI community hub."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from community_hub.config import Settings
from community_hub.routes import salons, curricula, community, api

TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine, SessionLocal
    db_url = Settings.require_db()
    engine = create_async_engine(db_url, pool_size=5, max_overflow=10)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    app.state.engine = engine
    app.state.db = SessionLocal
    yield
    if engine:
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="ORGAN-VI Community Hub",
        description="Community portal for salons, reading groups, and contributor stats",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — origins configurable via ALLOWED_ORIGINS env var (comma-separated)
    allowed_origins = Settings.ALLOWED_ORIGINS
    if allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=["GET"],
            allow_headers=["*"],
        )

    templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
    app.state.templates = templates

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(salons.router, prefix="/salons", tags=["salons"])
    app.include_router(curricula.router, prefix="/curricula", tags=["curricula"])
    app.include_router(community.router, prefix="/community", tags=["community"])
    app.include_router(api.router, prefix="/api", tags=["api"])

    @app.get("/")
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    return app


app = create_app()


def run():
    """Entry point for the community-hub CLI."""
    uvicorn.run(
        "community_hub.app:app",
        host=Settings.HOST,
        port=Settings.PORT,
        reload=Settings.DEBUG,
    )


if __name__ == "__main__":
    run()
