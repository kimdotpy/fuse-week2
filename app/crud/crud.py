"""
crud/crud.py — Layer 3: The Kitchen (database operations).

Rules for this module
---------------------
* Only talks to the database — never to HTTP, external APIs, or other services.
* One function per CRUD operation.
* Always logs what it is doing so operations are auditable.
* Returns None (not raises) when a record is simply not found; the router
  decides what HTTP status to return.
"""

from sqlalchemy.orm import Session, joinedload

from app.logger import get_logger
from app.models.models import Customer
from app.schemas.schemas import CustomerCreate, CustomerUpdate

logger = get_logger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# READ — all customers (paginated)
# ══════════════════════════════════════════════════════════════════════════════
def get_customers(db: Session, skip: int = 0, limit: int = 20) -> list[Customer]:
    """
    Return a page of customers ordered by customerNumber.

    Args:
        db:    Active SQLAlchemy session.
        skip:  Number of rows to skip (offset).
        limit: Maximum rows to return.

    Returns:
        List of Customer ORM objects (may be empty).
    """
    logger.info("READ customers | skip=%d, limit=%d", skip, limit)
    customers = (
        db.query(Customer)
        .order_by(Customer.customerNumber)
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.info("READ customers | returned %d record(s)", len(customers))
    return customers


# ══════════════════════════════════════════════════════════════════════════════
# READ — single customer (with orders + payments eager-loaded)
# ══════════════════════════════════════════════════════════════════════════════
def get_customer(db: Session, customer_number: int) -> Customer | None:
    """
    Fetch a single customer by primary key, including their orders and payments.

    Args:
        db:              Active SQLAlchemy session.
        customer_number: The customerNumber PK to look up.

    Returns:
        Customer ORM object with .orders and .payments populated,
        or None if not found.
    """
    logger.info("READ customer | customerNumber=%d", customer_number)
    customer = (
        db.query(Customer)
        .options(
            joinedload(Customer.orders),
            joinedload(Customer.payments),
        )
        .filter(Customer.customerNumber == customer_number)
        .first()
    )
    if customer is None:
        logger.warning("READ customer | NOT FOUND: customerNumber=%d", customer_number)
    else:
        logger.info(
            "READ customer | FOUND: %s (customerNumber=%d)",
            customer.customerName,
            customer_number,
        )
    return customer


# ══════════════════════════════════════════════════════════════════════════════
# CREATE
# ══════════════════════════════════════════════════════════════════════════════
def create_customer(db: Session, data: CustomerCreate) -> Customer:
    """
    Insert a new customer row.

    Args:
        db:   Active SQLAlchemy session.
        data: Validated CustomerCreate Pydantic model.

    Returns:
        The newly created Customer ORM object (with DB-generated values).

    Raises:
        sqlalchemy.exc.IntegrityError: If the customerNumber already exists
        or a FK constraint is violated (logged before re-raising).
    """
    logger.info("CREATE customer | customerNumber=%d, name='%s'",
                data.customerNumber, data.customerName)
    try:
        customer = Customer(**data.model_dump())
        db.add(customer)
        db.commit()
        db.refresh(customer)
        logger.info("CREATE customer | SUCCESS customerNumber=%d", customer.customerNumber)
        return customer
    except Exception as exc:
        db.rollback()
        logger.error("CREATE customer | FAILED: %s", exc)
        raise


# ══════════════════════════════════════════════════════════════════════════════
# UPDATE
# ══════════════════════════════════════════════════════════════════════════════
def update_customer(
    db: Session, customer_number: int, data: CustomerUpdate
) -> Customer | None:
    """
    Apply a partial update to an existing customer.

    Only the fields explicitly set by the caller are changed; fields left as
    None in CustomerUpdate are skipped (exclude_unset=True).

    Args:
        db:              Active SQLAlchemy session.
        customer_number: PK of the customer to update.
        data:            Validated CustomerUpdate model (all fields optional).

    Returns:
        Updated Customer ORM object, or None if the record does not exist.
    """
    logger.info("UPDATE customer | customerNumber=%d", customer_number)
    customer = db.query(Customer).filter(
        Customer.customerNumber == customer_number
    ).first()

    if customer is None:
        logger.warning("UPDATE customer | NOT FOUND: customerNumber=%d", customer_number)
        return None

    changes = data.model_dump(exclude_unset=True)
    if not changes:
        logger.warning("UPDATE customer | No fields to update for customerNumber=%d",
                       customer_number)
        return customer

    for field, value in changes.items():
        setattr(customer, field, value)

    try:
        db.commit()
        db.refresh(customer)
        logger.info("UPDATE customer | SUCCESS customerNumber=%d | changed: %s",
                    customer_number, list(changes.keys()))
        return customer
    except Exception as exc:
        db.rollback()
        logger.error("UPDATE customer | FAILED customerNumber=%d: %s", customer_number, exc)
        raise


# ══════════════════════════════════════════════════════════════════════════════
# DELETE
# ══════════════════════════════════════════════════════════════════════════════
def delete_customer(db: Session, customer_number: int) -> bool:
    """
    Delete a customer by primary key.

    Args:
        db:              Active SQLAlchemy session.
        customer_number: PK of the customer to delete.

    Returns:
        True  — record was found and deleted.
        False — record did not exist (nothing was deleted).

    Raises:
        sqlalchemy.exc.IntegrityError: If FK constraints prevent deletion
        (e.g. the customer still has orders).
    """
    logger.info("DELETE customer | customerNumber=%d", customer_number)
    customer = db.query(Customer).filter(
        Customer.customerNumber == customer_number
    ).first()

    if customer is None:
        logger.warning("DELETE customer | NOT FOUND: customerNumber=%d", customer_number)
        return False

    try:
        db.delete(customer)
        db.commit()
        logger.info("DELETE customer | SUCCESS customerNumber=%d", customer_number)
        return True
    except Exception as exc:
        db.rollback()
        logger.error("DELETE customer | FAILED customerNumber=%d: %s", customer_number, exc)
        raise
