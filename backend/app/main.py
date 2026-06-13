"""FastAPI application entrypoint: builds the ASGI app and wires routers."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlmodel import Session, select
from starlette.middleware.cors import CORSMiddleware

from app import models_registry  # noqa: F401  registers all models on the metadata
from app.api.router import api_router
from app.core import storage
from app.core.api import register_exception_handlers
from app.core.cache import close as close_redis
from app.core.cache import get_redis
from app.core.config import settings
from app.core.db import dispose_engine, engine
from app.core.queue import close_pool


def custom_generate_unique_id(route: APIRoute) -> str:
    """Build a stable OpenAPI operation id from a route's tag and name.

    Args:
        route: The API route whose unique id is being generated.

    Returns:
        An id in the form ``"{first_tag}-{route_name}"``, used by the
        frontend client generator to name SDK methods.
    """
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "development":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: the single place that releases shared clients.

    External clients are created once and reused (INV-F6); on shutdown every one
    is released here (arq pool, S3 client, Redis, DB engine).

    Args:
        _app: The FastAPI application (unused).

    Yields:
        Control to the running app; shared clients are released on shutdown.
    """
    yield
    await close_pool()
    storage.close_client()
    close_redis()
    dispose_engine()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Render every error with the structured envelope (P1-API-01).
register_exception_handlers(app)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness check confirming the app process is up.

    Returns:
        A small JSON payload ``{"status": "ok"}``.
    """
    return {"status": "ok"}


@app.get("/health/db", tags=["health"])
def health_db() -> dict[str, str]:
    """Readiness check for the database.

    Runs ``SELECT 1``; raises (HTTP 500) if the database is unreachable.

    Returns:
        A small JSON payload ``{"status": "ok"}`` when the database responds.
    """
    with Session(engine) as session:
        session.exec(select(1)).one()
    return {"status": "ok"}


@app.get("/health/redis", tags=["health"])
def health_redis() -> dict[str, str]:
    """Readiness check for Redis.

    PINGs the Redis server; raises (HTTP 500) if it is unreachable.

    Returns:
        A small JSON payload ``{"status": "ok"}`` when Redis responds.
    """
    get_redis().ping()
    return {"status": "ok"}
