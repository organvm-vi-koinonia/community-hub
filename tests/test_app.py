"""Tests for the community-hub FastAPI application."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from community_hub.config import Settings


def test_settings_defaults():
    assert Settings.HOST == "0.0.0.0"
    assert Settings.PORT == 8000


def test_settings_require_db_converts_url():
    with patch.object(Settings, "DATABASE_URL", "postgresql://user:pass@host/db"):
        url = Settings.require_db()
        assert url.startswith("postgresql+psycopg://")


def test_settings_require_db_raises_without_url():
    with patch.object(Settings, "DATABASE_URL", ""):
        with pytest.raises(RuntimeError, match="DATABASE_URL"):
            Settings.require_db()
