"""
router/dashboard_router.py — Dashboard layer: Table count endpoints and aggregated metrics.

This router provides:
1. Eight individual count endpoints (one per table)
2. One aggregated /overall_counts endpoint that fetches all counts concurrently

Concurrency: The /overall_counts endpoint uses asyncio.gather() to query all
tables simultaneously, avoiding sequential delays.

Endpoint map
------------
GET  /customers/count       → total customers
GET  /orders/count          → total orders
GET  /products/count        → total products
GET  /employees/count       → total employees
GET  /offices/count         → total offices
GET  /payments/count        → total payments
GET  /orderdetails/count    → total order details
GET  /productlines/count    → total product lines
GET  /overall_counts        → aggregated dashboard (all counts at once)
"""

import asyncio
import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.db.database import get_db
from app.logger import get_logger
from app.schemas.schemas import CountResponse, OverallCounts

logger = get_logger(__name__)

router = APIRouter(
    prefix="",
    tags=["Dashboard"],
)


# ══════════════════════════════════════════════════════════════════════════════
# Individual count endpoints — 8 tables
# ══════════════════════════════════════════════════════════════════════════════


@router.get(
    "/customers/count",
    response_model=CountResponse,
    summary="Count customers",
    description="Returns the total number of rows in the customers table.",
)
def count_customers(db: Session = Depends(get_db)):
    """Get count of customers from the database."""
    logger.info("GET /customers/count | incoming request")
    count = crud.count_customers(db)
    logger.info("GET /customers/count | 200 OK — count=%d", count)
    return CountResponse(count=count)


@router.get(
    "/orders/count",
    response_model=CountResponse,
    summary="Count orders",
    description="Returns the total number of rows in the orders table.",
)
def count_orders(db: Session = Depends(get_db)):
    """Get count of orders from the database."""
    logger.info("GET /orders/count | incoming request")
    count = crud.count_orders(db)
    logger.info("GET /orders/count | 200 OK — count=%d", count)
    return CountResponse(count=count)


@router.get(
    "/products/count",
    response_model=CountResponse,
    summary="Count products",
    description="Returns the total number of rows in the products table.",
)
def count_products(db: Session = Depends(get_db)):
    """Get count of products from the database."""
    logger.info("GET /products/count | incoming request")
    count = crud.count_products(db)
    logger.info("GET /products/count | 200 OK — count=%d", count)
    return CountResponse(count=count)


@router.get(
    "/employees/count",
    response_model=CountResponse,
    summary="Count employees",
    description="Returns the total number of rows in the employees table.",
)
def count_employees(db: Session = Depends(get_db)):
    """Get count of employees from the database."""
    logger.info("GET /employees/count | incoming request")
    count = crud.count_employees(db)
    logger.info("GET /employees/count | 200 OK — count=%d", count)
    return CountResponse(count=count)


@router.get(
    "/offices/count",
    response_model=CountResponse,
    summary="Count offices",
    description="Returns the total number of rows in the offices table.",
)
def count_offices(db: Session = Depends(get_db)):
    """Get count of offices from the database."""
    logger.info("GET /offices/count | incoming request")
    count = crud.count_offices(db)
    logger.info("GET /offices/count | 200 OK — count=%d", count)
    return CountResponse(count=count)


@router.get(
    "/payments/count",
    response_model=CountResponse,
    summary="Count payments",
    description="Returns the total number of rows in the payments table.",
)
def count_payments(db: Session = Depends(get_db)):
    """Get count of payments from the database."""
    logger.info("GET /payments/count | incoming request")
    count = crud.count_payments(db)
    logger.info("GET /payments/count | 200 OK — count=%d", count)
    return CountResponse(count=count)


@router.get(
    "/orderdetails/count",
    response_model=CountResponse,
    summary="Count order details",
    description="Returns the total number of rows in the orderdetails table.",
)
def count_orderdetails(db: Session = Depends(get_db)):
    """Get count of order details from the database."""
    logger.info("GET /orderdetails/count | incoming request")
    count = crud.count_orderdetails(db)
    logger.info("GET /orderdetails/count | 200 OK — count=%d", count)
    return CountResponse(count=count)


@router.get(
    "/productlines/count",
    response_model=CountResponse,
    summary="Count product lines",
    description="Returns the total number of rows in the productlines table.",
)
def count_productlines(db: Session = Depends(get_db)):
    """Get count of product lines from the database."""
    logger.info("GET /productlines/count | incoming request")
    count = crud.count_productlines(db)
    logger.info("GET /productlines/count | 200 OK — count=%d", count)
    return CountResponse(count=count)


# ══════════════════════════════════════════════════════════════════════════════
# GET /overall_counts — Aggregated dashboard using asyncio.gather()
# ══════════════════════════════════════════════════════════════════════════════


@router.get(
    "/overall_counts",
    response_model=OverallCounts,
    summary="Dashboard: all table counts",
    description=(
        "Returns a dashboard with the total row counts from all 8 tables. "
        "Uses concurrent queries (asyncio.gather) to fetch all counts simultaneously "
        "for optimal performance.\n\n"
        "**Response includes:**\n"
        "- customers: total customers\n"
        "- orders: total orders\n"
        "- products: total products\n"
        "- employees: total employees\n"
        "- offices: total offices\n"
        "- payments: total payments\n"
        "- orderdetails: total order details\n"
        "- productlines: total product lines"
    ),
)
async def get_overall_counts(db: Session = Depends(get_db)):
    """
    Fetch all 8 table counts concurrently using asyncio.gather().

    This endpoint demonstrates high-performance concurrent database queries.
    Instead of querying tables sequentially, all 8 queries start at the same time,
    resulting in much faster response times.

    Returns:
        OverallCounts: JSON object with all 8 table counts and response time.
    """
    start_time = time.time()
    logger.info("GET /overall_counts | incoming request — starting concurrent queries")

    # Run all 8 count queries concurrently using asyncio.gather()
    # Each count function runs in parallel, not sequentially
    logger.info("GET /overall_counts | asyncio.gather() starting — fetching all tables concurrently")

    try:
        # Create coroutines for all count operations
        # We run them in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        
        customers_count, orders_count, products_count, employees_count, \
        offices_count, payments_count, orderdetails_count, productlines_count = \
            await asyncio.gather(
                loop.run_in_executor(None, lambda: crud.count_customers(db)),
                loop.run_in_executor(None, lambda: crud.count_orders(db)),
                loop.run_in_executor(None, lambda: crud.count_products(db)),
                loop.run_in_executor(None, lambda: crud.count_employees(db)),
                loop.run_in_executor(None, lambda: crud.count_offices(db)),
                loop.run_in_executor(None, lambda: crud.count_payments(db)),
                loop.run_in_executor(None, lambda: crud.count_orderdetails(db)),
                loop.run_in_executor(None, lambda: crud.count_productlines(db)),
            )

        elapsed = time.time() - start_time
        logger.info(
            "GET /overall_counts | asyncio.gather() completed in %.3fs — "
            "customers=%d, orders=%d, products=%d, employees=%d, "
            "offices=%d, payments=%d, orderdetails=%d, productlines=%d",
            elapsed,
            customers_count, orders_count, products_count, employees_count,
            offices_count, payments_count, orderdetails_count, productlines_count,
        )
        logger.info("GET /overall_counts | 200 OK — response_time=%.3fs", elapsed)

        return OverallCounts(
            customers=customers_count,
            orders=orders_count,
            products=products_count,
            employees=employees_count,
            offices=offices_count,
            payments=payments_count,
            orderdetails=orderdetails_count,
            productlines=productlines_count,
        )

    except Exception as exc:
        elapsed = time.time() - start_time
        logger.error(
            "GET /overall_counts | asyncio.gather() FAILED after %.3fs: %s",
            elapsed, exc
        )
        # Return zeros for all counts if any query fails
        return OverallCounts(
            customers=0,
            orders=0,
            products=0,
            employees=0,
            offices=0,
            payments=0,
            orderdetails=0,
            productlines=0,
        )
