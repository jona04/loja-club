"""Top-level API router aggregating all module and shared routers."""

from fastapi import APIRouter

from app.api.routes import private, utils
from app.core.config import settings
from app.modules.accounts.auth import router as auth_router
from app.modules.accounts.routes import router as users_router
from app.modules.stores.routes import router as stores_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(stores_router)
api_router.include_router(utils.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
