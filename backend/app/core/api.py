"""Shared API conventions: pagination envelope/params and error responses.

Locks the platform-wide HTTP contract (DEC-5, Foundations §5): list endpoints
use **offset pagination** and return ``{"data": [...], "count": <total>}``;
all errors use the structured envelope ``{"error": {"code", "message"}}``.
"""

from typing import Annotated, Any, Generic, TypeVar

from fastapi import FastAPI, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic offset-paginated list envelope.

    Attributes:
        data: The items in the current page.
        count: Total number of matching items (across all pages).
    """

    data: list[T]
    count: int


class PageParams(BaseModel):
    """Validated offset pagination parameters."""

    skip: int = 0
    limit: int = 100


def pagination_params(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> PageParams:
    """Provide validated offset pagination params from the query string.

    Args:
        skip: Number of items to skip (``>= 0``).
        limit: Maximum number of items to return (``1..100``).

    Returns:
        The validated pagination parameters.
    """
    return PageParams(skip=skip, limit=limit)


class ErrorDetail(BaseModel):
    """Machine-readable error payload.

    Attributes:
        code: Stable error code for clients to branch on (e.g. ``not_found``).
        message: Human-readable message (no internal details leaked).
        details: Optional structured details (e.g. field validation errors).
    """

    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    """Structured error envelope returned for every API error."""

    error: ErrorDetail


class AppError(Exception):
    """Domain error rendered as a structured API error response.

    Raise this for business/validation failures that need a stable ``code``.
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        """Build a domain error.

        Args:
            code: Stable error code (e.g. ``store_not_found``).
            message: Human-readable message.
            status_code: HTTP status to respond with.
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


_STATUS_CODE_SLUGS: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "validation_error",
    status.HTTP_429_TOO_MANY_REQUESTS: "rate_limited",
}


def _error_json(
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    """Build a JSONResponse carrying the structured error envelope.

    Args:
        status_code: HTTP status code.
        code: Stable error code.
        message: Human-readable message.
        details: Optional structured details.

    Returns:
        A JSONResponse with ``{"error": {"code", "message", "details"}}``.
    """
    payload = ErrorResponse(
        error=ErrorDetail(code=code, message=message, details=details)
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers that render all errors with the structured envelope.

    Args:
        app: The FastAPI application to attach the handlers to.
    """

    @app.exception_handler(AppError)
    async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:  # noqa: ARG001
        return _error_json(exc.status_code, exc.code, exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception_handler(
        request: Request,  # noqa: ARG001
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code = _STATUS_CODE_SLUGS.get(exc.status_code, "error")
        return _error_json(exc.status_code, code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(
        request: Request,  # noqa: ARG001
        exc: RequestValidationError,
    ) -> JSONResponse:
        return _error_json(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "validation_error",
            "Validation failed",
            jsonable_encoder(exc.errors()),
        )
