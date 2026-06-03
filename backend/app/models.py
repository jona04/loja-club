"""Shared, cross-cutting schemas (generic message and auth tokens)."""

from sqlmodel import Field, SQLModel


class Message(SQLModel):
    """Generic message response."""

    message: str


class Token(SQLModel):
    """JSON payload containing an access token."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """Contents of a decoded JWT."""

    sub: str | None = None


class NewPassword(SQLModel):
    """Password-reset payload (token + new password)."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)
