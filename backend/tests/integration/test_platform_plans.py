"""Integration tests for platform-admin plan operations."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.api import AppError
from app.core.config import settings
from app.modules.billing import services
from app.modules.billing.models import BillingPlan
from app.modules.billing.schemas import BillingPlanCreate, BillingPlanUpdate


def _create(db: Session, **kwargs: object) -> BillingPlan:
    payload = {
        "name": "Plan",
        "monthly_price_amount_minor": 100,
        "monthly_price_currency": "BRL",
        "commission_bps": 200,
        **kwargs,
    }
    return services.create_plan(session=db, payload=BillingPlanCreate(**payload))


def test_seed_creates_free_and_pro(db: Session) -> None:
    plans = {p.key: p for p in db.exec(select(BillingPlan)).all()}
    assert "free" in plans
    assert "pro" in plans
    assert plans["free"].monthly_price_amount_minor == 0
    assert plans["free"].commission_bps == 500
    assert plans["pro"].monthly_price_amount_minor == 9990
    assert plans["pro"].commission_bps == 150


def test_list_plans_excludes_soft_deleted(db: Session) -> None:
    plan = _create(db, key="temp")
    services.delete_plan(session=db, plan_id=plan.id)
    plans, _count = services.list_plans(session=db, skip=0, limit=100)
    assert "temp" not in {p.key for p in plans}


def test_create_plan_duplicate_key_conflict(db: Session) -> None:
    with pytest.raises(AppError) as exc:
        _create(db, key="free")  # already seeded
    assert exc.value.status_code == 409


def test_update_plan(db: Session) -> None:
    plan = _create(db, key="upd", name="Upd")
    updated = services.update_plan(
        session=db, plan_id=plan.id, payload=BillingPlanUpdate(commission_bps=250)
    )
    assert updated.commission_bps == 250
    assert updated.name == "Upd"


def test_delete_plan_then_get_not_found(db: Session) -> None:
    plan = _create(db, key="del")
    services.delete_plan(session=db, plan_id=plan.id)
    with pytest.raises(AppError) as exc:
        services.get_plan(session=db, plan_id=plan.id)
    assert exc.value.status_code == 404


def test_get_plan_missing_not_found(db: Session) -> None:
    with pytest.raises(AppError) as exc:
        services.get_plan(session=db, plan_id=uuid.uuid4())
    assert exc.value.status_code == 404


def test_list_plans_requires_platform_permission(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/platform/plans", headers=normal_user_token_headers
    )
    assert r.status_code == 403


def test_plans_crud_over_http(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/platform/plans", headers=superuser_token_headers
    )
    assert r.status_code == 200
    assert r.json()["count"] >= 2

    r = client.post(
        f"{settings.API_V1_STR}/platform/plans",
        headers=superuser_token_headers,
        json={
            "key": "enterprise",
            "name": "Enterprise",
            "monthly_price_amount_minor": 49990,
            "monthly_price_currency": "BRL",
            "commission_bps": 100,
        },
    )
    assert r.status_code == 201
    plan_id = r.json()["id"]

    r = client.patch(
        f"{settings.API_V1_STR}/platform/plans/{plan_id}",
        headers=superuser_token_headers,
        json={"commission_bps": 90},
    )
    assert r.status_code == 200
    assert r.json()["commission_bps"] == 90

    r = client.delete(
        f"{settings.API_V1_STR}/platform/plans/{plan_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
