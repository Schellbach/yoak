"""FastAPI application — Yoak API server."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from yoak.api.routes import canvas, chat, config, hypotheses, journal, workflows
from yoak.core.agent import Agent
from yoak.core.config import load_settings

DASHBOARD_DIST = Path(__file__).parent.parent.parent / "dashboard" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    agent = Agent(settings)
    app.state.agent = agent
    app.state.settings = settings
    yield
    await agent.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Yoak",
        description="Lean Startup Cofounder Agent API",
        version="0.1.0",
        lifespan=lifespan,
    )

    settings = load_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router, prefix="/api", tags=["chat"])
    app.include_router(canvas.router, prefix="/api", tags=["canvas"])
    app.include_router(hypotheses.router, prefix="/api", tags=["hypotheses"])
    app.include_router(journal.router, prefix="/api", tags=["journal"])
    app.include_router(workflows.router, prefix="/api", tags=["workflows"])
    app.include_router(config.router, prefix="/api", tags=["config"])

    if DASHBOARD_DIST.exists():
        from fastapi.responses import FileResponse

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            file_path = DASHBOARD_DIST / full_path
            if file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(DASHBOARD_DIST / "index.html")

        app.mount("/assets", StaticFiles(directory=DASHBOARD_DIST / "assets"), name="assets")

    return app
