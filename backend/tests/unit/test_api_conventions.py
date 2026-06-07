"""Unit tests for the shared API conventions (pagination + error envelope)."""

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.api import AppError, Page, register_exception_handlers


class _Item(BaseModel):
    name: str


def test_page_envelope_serializes() -> None:
    page = Page[_Item](data=[_Item(name="a"), _Item(name="b")], count=42)
    assert page.model_dump() == {
        "data": [{"name": "a"}, {"name": "b"}],
        "count": 42,
    }


def _app_with_routes() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom-http")
    def _boom_http() -> None:
        raise HTTPException(status_code=404, detail="Not here")

    @app.get("/boom-app")
    def _boom_app() -> None:
        raise AppError("store_not_found", "Loja nao encontrada", status_code=404)

    @app.get("/needs-q")
    def _needs_q(n: int) -> dict[str, int]:
        return {"n": n}

    @app.get("/boom-unhandled")
    def _boom_unhandled() -> None:
        raise ValueError("secret internal detail")

    return app


def test_http_exception_maps_to_envelope() -> None:
    client = TestClient(_app_with_routes())
    r = client.get("/boom-http")
    assert r.status_code == 404
    assert r.json() == {
        "error": {"code": "not_found", "message": "Not here", "details": None}
    }


def test_app_error_uses_explicit_code() -> None:
    client = TestClient(_app_with_routes())
    r = client.get("/boom-app")
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "store_not_found"
    assert body["error"]["message"] == "Loja nao encontrada"


def test_validation_error_envelope() -> None:
    client = TestClient(_app_with_routes())
    r = client.get("/needs-q")  # missing required query param 'n'
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"
    assert isinstance(body["error"]["details"], list)
    assert len(body["error"]["details"]) > 0


def test_unhandled_exception_returns_envelope_without_leak() -> None:
    client = TestClient(_app_with_routes(), raise_server_exceptions=False)
    r = client.get("/boom-unhandled")
    assert r.status_code == 500
    body = r.json()
    assert body["error"]["code"] == "internal_error"
    assert body["error"]["message"] == "Internal server error"
    assert "secret internal detail" not in r.text
