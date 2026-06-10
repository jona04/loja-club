"""Billing services: plan-definition CRUD (no subscription/charge yet)."""

import uuid

from sqlalchemy import ColumnElement, func
from sqlmodel import Session, col, select

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.billing.models import BillingPlan
from app.modules.billing.schemas import BillingPlanCreate, BillingPlanUpdate


def list_plans(
    *, session: Session, skip: int, limit: int
) -> tuple[list[BillingPlan], int]:
    """List plan definitions, excluding soft-deleted ones.

    Args:
        session: Active database session.
        skip: Pagination offset.
        limit: Pagination page size.

    Returns:
        A ``(plans, total_count)`` tuple for the current page.
    """
    conditions: list[ColumnElement[bool]] = [col(BillingPlan.deleted_at).is_(None)]
    count = session.exec(
        select(func.count()).select_from(BillingPlan).where(*conditions)
    ).one()
    plans = session.exec(
        select(BillingPlan)
        .where(*conditions)
        .order_by(col(BillingPlan.monthly_price_amount_minor))
        .offset(skip)
        .limit(limit)
    ).all()
    return list(plans), count


def get_plan(*, session: Session, plan_id: uuid.UUID) -> BillingPlan:
    """Return a plan definition by id, excluding soft-deleted ones.

    Args:
        session: Active database session.
        plan_id: The plan id.

    Returns:
        The plan.

    Raises:
        AppError: 404 if the plan does not exist or is soft-deleted.
    """
    plan = session.get(BillingPlan, plan_id)
    if plan is None or plan.deleted_at is not None:
        raise AppError("plan_not_found", "Plan not found", status_code=404)
    return plan


def create_plan(*, session: Session, payload: BillingPlanCreate) -> BillingPlan:
    """Create a plan definition.

    Args:
        session: Active database session.
        payload: The plan fields.

    Returns:
        The created plan.

    Raises:
        AppError: 409 if a non-deleted plan already uses the key.
    """
    existing = session.exec(
        select(BillingPlan).where(
            BillingPlan.key == payload.key, col(BillingPlan.deleted_at).is_(None)
        )
    ).first()
    if existing is not None:
        raise AppError(
            "plan_key_taken", "A plan with this key already exists", status_code=409
        )
    plan = BillingPlan.model_validate(payload)
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


def update_plan(
    *, session: Session, plan_id: uuid.UUID, payload: BillingPlanUpdate
) -> BillingPlan:
    """Update a plan definition (unset fields are ignored).

    Args:
        session: Active database session.
        plan_id: The plan id.
        payload: Fields to change.

    Returns:
        The updated plan.

    Raises:
        AppError: 404 if the plan does not exist or is soft-deleted.
    """
    plan = get_plan(session=session, plan_id=plan_id)
    plan.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


def delete_plan(*, session: Session, plan_id: uuid.UUID) -> None:
    """Soft-delete a plan definition.

    Args:
        session: Active database session.
        plan_id: The plan id.

    Raises:
        AppError: 404 if the plan does not exist or is already soft-deleted.
    """
    plan = get_plan(session=session, plan_id=plan_id)
    plan.deleted_at = get_datetime_utc()
    session.add(plan)
    session.commit()
