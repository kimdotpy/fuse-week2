"""
db/database.py — Layer 1: The Connection (the "plumbing").

Responsibilities
----------------
* Build a single SQLAlchemy Engine from settings.
* Expose a SessionLocal factory.
* Provide a FastAPI dependency `get_db` that yields a session and always
  closes it — even if an exception occurs.

Nothing in this file touches HTTP, business logic, or any external service.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config.settings import settings
from app.logger import get_logger

logger = get_logger(__name__)

# ── Engine ────────────────────────────────────────────────────────────────────
# pool_pre_ping=True: SQLAlchemy checks the connection is alive before using it
# (recovers from "server closed the connection unexpectedly" after idle time).
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,   # Set True to log every SQL statement (very noisy in prod)
)

# ── Session factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ── Declarative base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """All ORM models inherit from this base."""
    pass


# ── FastAPI dependency ─────────────────────────────────────────────────────────
def get_db():
    """
    Yield a database session and guarantee it is closed afterwards.

    Usage in a router:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        logger.info("Database session opened")
        yield db
    except Exception as exc:
        logger.error("Unexpected error during database session: %s", exc)
        db.rollback()
        raise
    finally:
        db.close()
        logger.info("Database session closed")


# ── Connection smoke-test (called once on startup) ────────────────────────────
def verify_connection() -> None:
    """
    Execute a trivial query to confirm the database is reachable.
    Raises an exception (and logs ERROR) if the connection fails.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully")
    except Exception as exc:
        logger.error("Database connection FAILED: %s", exc)
        raise
