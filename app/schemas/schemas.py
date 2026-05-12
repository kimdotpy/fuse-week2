"""
schemas/schemas.py — Layer 2: The Blueprints (Pydantic validation models).

Separate schemas for each operation:
  * *Base   — shared fields
  * *Create — what the client sends to create a record (no auto-generated PK)
  * *Update — partial update (all fields Optional)
  * *Out    — what the API returns (includes PK + related data)

Pydantic v2 is used throughout (model_config instead of class Config).
"""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator
from pydantic import ConfigDict

from app.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: log validation errors via a root validator
# ─────────────────────────────────────────────────────────────────────────────
def _log_validation_warning(model_name: str, values: dict) -> None:
    logger.warning("Validation called for %s with data: %s", model_name, values)


# ══════════════════════════════════════════════════════════════════════════════
# Payment schemas
# ══════════════════════════════════════════════════════════════════════════════
class PaymentBase(BaseModel):
    checkNumber: str
    paymentDate: date
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            logger.warning("Validation error: payment amount must be positive, got %s", v)
            raise ValueError("amount must be a positive number")
        return v


class PaymentCreate(PaymentBase):
    customerNumber: int


class PaymentOut(PaymentBase):
    customerNumber: int

    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════════════════════════════════════
# Order schemas
# ══════════════════════════════════════════════════════════════════════════════
class OrderBase(BaseModel):
    orderDate: date
    requiredDate: date
    shippedDate: Optional[date] = None
    status: str
    comments: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        allowed = {"Shipped", "Resolved", "Cancelled", "On Hold", "Disputed", "In Process"}
        if v not in allowed:
            logger.warning("Validation error: invalid order status '%s'", v)
            raise ValueError(f"status must be one of {allowed}")
        return v


class OrderCreate(OrderBase):
    customerNumber: int


class OrderOut(OrderBase):
    orderNumber: int
    customerNumber: int

    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════════════════════════════════════
# Customer schemas
# ══════════════════════════════════════════════════════════════════════════════
class CustomerBase(BaseModel):
    customerName: str
    contactLastName: str
    contactFirstName: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: str
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[Decimal] = None

    @field_validator("customerName", "contactLastName", "contactFirstName", "country")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            logger.warning("Validation error: required string field is blank")
            raise ValueError("field must not be blank or whitespace")
        return v

    @field_validator("creditLimit")
    @classmethod
    def credit_limit_non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            logger.warning("Validation error: creditLimit is negative (%s)", v)
            raise ValueError("creditLimit must be 0 or greater")
        return v


class CustomerCreate(CustomerBase):
    """Used when creating a new customer. customerNumber is omitted — the DB assigns it."""
    customerNumber: int  # required because the seed DB uses natural PKs (not serial)


class CustomerUpdate(BaseModel):
    """
    Partial update schema — every field is Optional so the client can
    send only the fields they want to change.
    """
    customerName: Optional[str] = None
    contactLastName: Optional[str] = None
    contactFirstName: Optional[str] = None
    phone: Optional[str] = None
    addressLine1: Optional[str] = None
    addressLine2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[Decimal] = None

    @field_validator("creditLimit")
    @classmethod
    def credit_limit_non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            logger.warning("Validation error on update: creditLimit is negative (%s)", v)
            raise ValueError("creditLimit must be 0 or greater")
        return v


class CustomerOut(CustomerBase):
    """
    What the API returns to the caller.
    Includes the PK and nested orders/payments (empty lists if none exist).
    """
    customerNumber: int
    orders: list[OrderOut] = []
    payments: list[PaymentOut] = []

    model_config = ConfigDict(from_attributes=True)


class CustomerOutSimple(CustomerBase):
    """
    Lightweight view used in the paginated list endpoint —
    no nested relations (avoids N+1 queries on large result sets).
    """
    customerNumber: int

    model_config = ConfigDict(from_attributes=True)
