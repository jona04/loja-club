"""Routes for the platform 3D catalog (merchant-facing browse).

The catalog is global (platform-owned), so it is not store-scoped. Any
authenticated user can browse the active models to pick one for a product.
"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.modules.customization import services
from app.modules.customization.schemas import Platform3DModelPublic

router = APIRouter(prefix="/3d-catalog", tags=["3d-catalog"])


@router.get("/models", response_model=list[Platform3DModelPublic])
def list_models(
    session: SessionDep, _current_user: CurrentUser
) -> list[Platform3DModelPublic]:
    """List the active catalog models with their active version.

    Args:
        session: Active database session.
        _current_user: The authenticated user (browse requires login).

    Returns:
        The active catalog models.
    """
    return services.list_catalog(session=session)
