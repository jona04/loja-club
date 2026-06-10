"""Top-level API router aggregating all module and shared routers."""

from fastapi import APIRouter

from app.api.routes import private, utils
from app.core.config import settings
from app.modules.accounts.auth import router as auth_router
from app.modules.accounts.routes import router as users_router
from app.modules.catalog.routes import router as catalog_router
from app.modules.content.routes import router as content_router
from app.modules.media.routes import router as media_router
from app.modules.storefront.routes import router as storefront_router
from app.modules.stores.routes import router as stores_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(stores_router)
api_router.include_router(catalog_router)
api_router.include_router(content_router)
api_router.include_router(media_router)
api_router.include_router(storefront_router)
api_router.include_router(utils.router)


if settings.ENVIRONMENT == "development":
    api_router.include_router(private.router)
