"""Application settings from environment variables."""

from __future__ import annotations

import os

from koinonia_db.config import require_database_url


class Settings:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "").lower() == "true"
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.environ.get("ALLOWED_ORIGINS", "").split(",")
        if o.strip()
    ]

    @classmethod
    def require_db(cls) -> str:
        return require_database_url()
