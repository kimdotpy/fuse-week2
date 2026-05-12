"""
config/settings.py — Application settings loaded from the .env file.

Pydantic-Settings reads every field from environment variables (or .env).
No secret ever needs to be hard-coded in source.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configuration the app needs.
    Field names match the keys in .env exactly (case-insensitive by default).
    """

    # ── Database ─────────────────────────────────────────────────────────────
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "localhost"

    # ── API tunables (optional — sensible defaults) ──────────────────────────
    DEFAULT_PAGE_LIMIT: int = 20
    MAX_PAGE_LIMIT: int = 100

    model_config = SettingsConfigDict(
        # Look for .env two levels above this file  (project root)
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",          # silently ignore unknown keys in .env
    )

    @property
    def database_url(self) -> str:
        """Assembled synchronous SQLAlchemy connection string."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# ── Module-level singleton ────────────────────────────────────────────────────
# Import `settings` anywhere instead of constructing a new Settings() each time.
settings = Settings()
