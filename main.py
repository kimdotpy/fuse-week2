"""
main.py — Application entry point.

Boots the FastAPI app, verifies the DB connection on startup,
and mounts all routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import verify_connection
from app.logger import get_logger
from app.router.router import router as customer_router
from app.router.dashboard_router import router as dashboard_router

logger = get_logger(__name__)


# ── Lifespan: runs once on startup, then on shutdown ──────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    verify_connection()          # fails fast if DB is not reachable
    logger.info("Application ready.")
    yield
    logger.info("Application shutting down.")


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Classic Models — Customer API",
    description=(
        "A layered REST API for managing customers, orders, and payments "
        "in the Classic Models database.\n\n"
        "**Features:**\n"
        "- CRUD operations on customers, orders, and payments\n"
        "- Individual count endpoints for all 8 database tables\n"
        "- High-performance dashboard with concurrent queries (asyncio.gather)\n\n"
        "**Architecture layers:**\n"
        "- `config/settings.py` — environment-based configuration\n"
        "- `db/database.py` — connection & session management\n"
        "- `models/models.py` — SQLAlchemy ORM models\n"
        "- `schemas/schemas.py` — Pydantic validation blueprints\n"
        "- `crud/crud.py` — database operations (Create/Read/Update/Delete)\n"
        "- `router/router.py` — Customer CRUD endpoints\n"
        "- `router/dashboard_router.py` — Dashboard & count endpoints\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"tryItOutEnabled": True},#cant use "supportedSubmitMethods": []since tryitout button seems to be prerequisit for execute, turning it on every time is hassle so ill just turn it on permanently 
)

# ── Register routers ──────────────────────────────────────────────────────────
# Dashboard router MUST be registered first so /customers/count is matched
# before the dynamic /customers/{customer_number} route from customer_router
app.include_router(dashboard_router)
app.include_router(customer_router)


# ── Root health-check ─────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    logger.info("GET / | health-check called")
    return {"status": "ok", "message": "Classic Models API is running 🚀"}


# ── Dev runner ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
