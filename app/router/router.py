"""
router/router.py — Layer 4: The Front Desk (HTTP endpoints).

Endpoint map
------------
GET  /customers              → list all customers (paginated)
POST /customers              → create a new customer
GET  /customers/{number}     → get one customer with orders + payments
PUT  /customers/{number}     → partial-update a customer
DELETE /customers/{number}   → delete a customer

All endpoints log the incoming request and the response outcome.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.db.database import get_db
from app.logger import get_logger
from app.schemas.schemas import (
    CustomerCreate,
    CustomerOut,
    CustomerOutSimple,
    CustomerUpdate,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


# ══════════════════════════════════════════════════════════════════════════════
# GET /customers  — paginated list
# ══════════════════════════════════════════════════════════════════════════════
@router.get(
    "",
    response_model=list[CustomerOutSimple],
    summary="List customers (paginated)",
    description=(
        "Returns a paginated list of customers. "
        "Use `skip` to offset and `limit` to control page size."
    ),
)
def list_customers(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db),
):
    logger.info("GET /customers | skip=%d, limit=%d", skip, limit)
    customers = crud.get_customers(db, skip=skip, limit=limit)
    logger.info("GET /customers | returning %d customer(s)", len(customers))
    return customers


# ══════════════════════════════════════════════════════════════════════════════
# GET /customers/{customer_number}  — single customer with related data
# ══════════════════════════════════════════════════════════════════════════════
@router.get(
    "/{customer_number}",
    response_model=CustomerOut,
    summary="Get a single customer",
    description=(
        "Fetches one customer by their customerNumber. "
        "Includes their full order history and payments. "
        "Returns 404 if not found."
    ),
)
def get_customer(
    customer_number: int,
    db: Session = Depends(get_db),
):
    logger.info("GET /customers/%d | incoming request", customer_number)
    customer = crud.get_customer(db, customer_number=customer_number)

    if customer is None:
        logger.warning(
            "GET /customers/%d | 404 Not Found", customer_number
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with customerNumber={customer_number} not found.",
        )

    logger.info("GET /customers/%d | 200 OK — %s", customer_number, customer.customerName)
    return customer


# ══════════════════════════════════════════════════════════════════════════════
# POST /customers  — create
# ══════════════════════════════════════════════════════════════════════════════
@router.post(
    "",
    response_model=CustomerOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
):
    logger.info(
        "POST /customers | customerNumber=%d, name='%s'",
        payload.customerNumber,
        payload.customerName,
    )
    # Guard: reject duplicate customerNumber
    existing = crud.get_customer(db, customer_number=payload.customerNumber)
    if existing:
        logger.warning(
            "POST /customers | 409 Conflict — customerNumber=%d already exists",
            payload.customerNumber,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"customerNumber={payload.customerNumber} already exists.",
        )

    customer = crud.create_customer(db, data=payload)
    logger.info("POST /customers | 201 Created customerNumber=%d", customer.customerNumber)
    # Reload with relations so the response schema is fully populated
    return crud.get_customer(db, customer_number=customer.customerNumber)


# ══════════════════════════════════════════════════════════════════════════════
# PUT /customers/{customer_number}  — partial update
# ══════════════════════════════════════════════════════════════════════════════
@router.put(
    "/{customer_number}",
    response_model=CustomerOut,
    summary="Update a customer (partial)",
    description="Only the fields included in the request body are updated.",
)
def update_customer(
    customer_number: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    logger.info("PUT /customers/%d | incoming update", customer_number)
    customer = crud.update_customer(db, customer_number=customer_number, data=payload)

    if customer is None:
        logger.warning("PUT /customers/%d | 404 Not Found", customer_number)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with customerNumber={customer_number} not found.",
        )

    logger.info("PUT /customers/%d | 200 OK", customer_number)
    return crud.get_customer(db, customer_number=customer_number)


# ══════════════════════════════════════════════════════════════════════════════
# DELETE /customers/{customer_number}
# ══════════════════════════════════════════════════════════════════════════════
@router.delete(
    "/{customer_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a customer",
)
def delete_customer(
    customer_number: int,
    db: Session = Depends(get_db),
):
    logger.info("DELETE /customers/%d | incoming request", customer_number)
    deleted = crud.delete_customer(db, customer_number=customer_number)

    if not deleted:
        logger.warning("DELETE /customers/%d | 404 Not Found", customer_number)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with customerNumber={customer_number} not found.",
        )

    logger.info("DELETE /customers/%d | 204 No Content", customer_number)
