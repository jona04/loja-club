"""Top-level API router aggregating all module and shared routers."""

from fastapi import APIRouter

from app.api.routes import private, utils
from app.core.config import settings
from app.modules.accounts.auth import router as auth_router
from app.modules.accounts.routes import router as users_router
from app.modules.cart.routes import router as cart_router
from app.modules.catalog.routes import router as catalog_router
from app.modules.checkout.routes import public_router as checkout_public_router
from app.modules.checkout.routes import router as checkout_router
from app.modules.content.routes import router as content_router
from app.modules.customers.routes import router as customers_router
from app.modules.customization.routes import (
    panel_router as customization_panel_router,
)
from app.modules.customization.routes import router as customization_router
from app.modules.discounts.routes import router as discounts_router
from app.modules.media.routes import router as media_router
from app.modules.orders.routes import router as orders_router
from app.modules.platform_admin.routes import router as platform_admin_router
from app.modules.shipping.routes import router as shipping_router
from app.modules.storefront.routes import router as storefront_router
from app.modules.stores.routes import router as stores_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(stores_router)
api_router.include_router(cart_router)
api_router.include_router(catalog_router)
api_router.include_router(checkout_router)
api_router.include_router(checkout_public_router)
api_router.include_router(content_router)
api_router.include_router(customers_router)
api_router.include_router(customization_router)
api_router.include_router(customization_panel_router)
api_router.include_router(discounts_router)
api_router.include_router(media_router)
api_router.include_router(orders_router)
api_router.include_router(platform_admin_router)
api_router.include_router(shipping_router)
api_router.include_router(storefront_router)
api_router.include_router(utils.router)


if settings.ENVIRONMENT == "development":
    api_router.include_router(private.router)
