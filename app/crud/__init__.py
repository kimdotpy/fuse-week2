"""
app/crud/__init__.py — re-export CRUD functions so callers can write:
    from app import crud
    crud.get_customers(...)
"""
from app.crud.crud import (  # noqa: F401
    count_customers,
    count_employees,
    count_offices,
    count_orderdetails,
    count_orders,
    count_payments,
    count_productlines,
    count_products,
    create_customer,
    delete_customer,
    get_customer,
    get_customers,
    update_customer,
)
