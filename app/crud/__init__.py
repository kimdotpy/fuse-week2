"""
app/crud/__init__.py — re-export CRUD functions so callers can write:
    from app import crud
    crud.get_customers(...)
"""
from app.crud.crud import (  # noqa: F401
    create_customer,
    delete_customer,
    get_customer,
    get_customers,
    update_customer,
)
