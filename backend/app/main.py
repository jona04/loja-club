import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app import models_registry  # noqa: F401  registers all models on the metadata
from app.api.main import api_router
from app.core.cache import get_redis
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

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


@app.get("/health/redis", tags=["health"])
def health_redis() -> dict[str, str]:
    """Readiness check for Redis.

    PINGs the Redis server; raises (HTTP 500) if it is unreachable.

    Returns:
        A small JSON payload ``{"status": "ok"}`` when Redis responds.
    """
    get_redis().ping()
    return {"status": "ok"}
