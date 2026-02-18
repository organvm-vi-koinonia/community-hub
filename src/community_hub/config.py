"""Application settings from environment variables."""

from __future__ import annotations

import os


class Settings:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "").lower() == "true"

    @classmethod
    def require_db(cls) -> str:
        if not cls.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set")
        url = cls.DATABASE_URL
        if url.startswith("postgresql://") and "+psycopg" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url
