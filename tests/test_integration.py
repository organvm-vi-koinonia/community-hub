"""Integration tests — HTTP routes via FastAPI TestClient with mocked DB."""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def mock_session():
    """Create a mock async DB session that returns empty results."""
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar.return_value = 0
    mock_result.scalar_one_or_none.return_value = None
    mock_result.mappings.return_value.all.return_value = []
    session.execute.return_value = mock_result
    session.get.return_value = None
    return session


@pytest.fixture
def client(mock_session):
    """Create TestClient using the real app with a swapped-in test lifespan."""
    from community_hub.app import create_app

    @asynccontextmanager
    async def mock_db():
        yield mock_session

    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        from community_hub.app import TEMPLATE_DIR
        from fastapi.templating import Jinja2Templates

        app.state.db = mock_db
        app.state.engine = None
        app.state.templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
        yield

    app = create_app()
    app.router.lifespan_context = test_lifespan

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ── Health + Index ──────────────────────────────────────────────


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_index(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "ORGAN-VI" in r.text


# ── Salons (HTML) ───────────────────────────────────────────────


def test_salons_list(client):
    r = client.get("/salons/")
    assert r.status_code == 200
    assert "Salon Archive" in r.text


def test_salons_detail_404(client):
    r = client.get("/salons/999")
    assert r.status_code == 404


# ── Curricula (HTML) ────────────────────────────────────────────


def test_curricula_list(client):
    r = client.get("/curricula/")
    assert r.status_code == 200
    assert "Reading Curricula" in r.text


# ── Community (HTML) ────────────────────────────────────────────


def test_community_events(client):
    r = client.get("/community/events")
    assert r.status_code == 200
    assert "Events" in r.text


def test_community_stats(client):
    r = client.get("/community/stats")
    assert r.status_code == 200
    assert "Community Stats" in r.text


def test_community_contributors(client):
    r = client.get("/community/contributors")
    assert r.status_code == 200
    assert "Contributors" in r.text


def test_community_contributor_detail_404(client):
    r = client.get("/community/contributors/nonexistent")
    assert r.status_code == 404


# ── Search (HTML) ───────────────────────────────────────────────


def test_search_empty(client):
    r = client.get("/search?q=")
    assert r.status_code == 200


def test_search_short_query(client):
    r = client.get("/search?q=a")
    assert r.status_code == 200


# ── Syllabus (HTML) ─────────────────────────────────────────────


def test_syllabus_form(client):
    r = client.get("/syllabus")
    assert r.status_code == 200


# ── API: Salons ─────────────────────────────────────────────────


def test_api_salons(client):
    r = client.get("/api/salons")
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 50
    assert data["offset"] == 0


def test_api_salons_pagination_params(client):
    r = client.get("/api/salons?limit=5&offset=10")
    assert r.status_code == 200
    data = r.json()
    assert data["limit"] == 5
    assert data["offset"] == 10


def test_api_salon_detail_404(client):
    r = client.get("/api/salons/999")
    assert r.status_code == 404


# ── API: Curricula ──────────────────────────────────────────────


def test_api_curricula(client):
    r = client.get("/api/curricula")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] == 0


# ── API: Taxonomy ───────────────────────────────────────────────


def test_api_taxonomy(client):
    r = client.get("/api/taxonomy")
    assert r.status_code == 200
    assert r.json() == []


# ── API: Contributors ───────────────────────────────────────────


def test_api_contributors(client):
    r = client.get("/api/contributors")
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_api_contributor_detail_404(client):
    r = client.get("/api/contributors/nonexistent")
    assert r.status_code == 404


# ── API: Stats ──────────────────────────────────────────────────


def test_api_stats(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["salons"] == 0
    assert data["curricula"] == 0


# ── API: Health Deep ────────────────────────────────────────────


def test_api_health_deep(client):
    r = client.get("/api/health/deep")
    assert r.status_code == 200
    data = r.json()
    assert data["organ"] == "VI"
    assert data["version"] == "0.4.0"


# ── API: Manifest ──────────────────────────────────────────────


def test_api_manifest(client):
    r = client.get("/api/manifest")
    assert r.status_code == 200
    data = r.json()
    assert data["organ_id"] == "VI"
    assert "contributor_profiles" in data["capabilities"]
    assert "atom_feeds" in data["capabilities"]
    assert "rate_limiting" in data["capabilities"]
    assert "websocket_live_salons" in data["capabilities"]
    assert "contributors" in data["endpoints"]
    assert "feeds_salons" in data["endpoints"]


# ── API: Search ─────────────────────────────────────────────────


def test_api_search(client):
    r = client.get("/api/search?q=test")
    assert r.status_code == 200


# ── Atom Feeds ─────────────────────────────────────────────────


def test_feed_salons(client):
    r = client.get("/feeds/salons.xml")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/atom+xml"
    assert b"<feed" in r.content
    assert b"ORGAN-VI Salons" in r.content


def test_feed_events(client):
    r = client.get("/feeds/events.xml")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/atom+xml"
    assert b"ORGAN-VI Community Events" in r.content


def test_feed_curricula(client):
    r = client.get("/feeds/curricula.xml")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/atom+xml"
    assert b"ORGAN-VI Reading Curricula" in r.content


# ── Syllabus Service Import ────────────────────────────────────


def test_syllabus_service_importable():
    """The shared syllabus service should be importable from koinonia_db."""
    from koinonia_db.syllabus_service import generate_learning_path
    assert callable(generate_learning_path)


# ── Live Salon Room (HTTP) ─────────────────────────────────────


def test_live_salon_page(client):
    r = client.get("/salons/1/live")
    assert r.status_code == 200
    assert "Live Salon" in r.text
    assert "/ws/salons/" in r.text
    assert "sessionId = 1" in r.text


# ── WebSocket Live Salons ──────────────────────────────────────


def test_websocket_connect_and_message(client):
    """WebSocket should accept connection and broadcast messages."""
    with client.websocket_connect("/ws/salons/1") as ws:
        # First message: system join notification
        data = ws.receive_json()
        assert data["type"] == "system"
        assert "joined" in data["text"]
        assert data["count"] == 1

        # Send a message
        ws.send_text("Hello salon")
        data = ws.receive_json()
        assert data["type"] == "message"
        assert data["text"] == "Hello salon"
        assert "timestamp" in data


def test_websocket_ping_pong(client):
    """WebSocket should respond to ping with pong."""
    with client.websocket_connect("/ws/salons/2") as ws:
        ws.receive_json()  # consume system join message
        ws.send_text("ping")
        data = ws.receive_json()
        assert data["type"] == "pong"


def test_websocket_multiple_connections(client):
    """Two connections to same room should both receive broadcasts."""
    with client.websocket_connect("/ws/salons/3") as ws1:
        ws1.receive_json()  # ws1 join

        with client.websocket_connect("/ws/salons/3") as ws2:
            # ws1 sees ws2 join
            join1 = ws1.receive_json()
            assert join1["type"] == "system"
            assert join1["count"] == 2

            # ws2 sees own join
            join2 = ws2.receive_json()
            assert join2["type"] == "system"
            assert join2["count"] == 2

            # ws1 sends, both should receive
            ws1.send_text("From ws1")
            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()
            assert msg1["type"] == "message"
            assert msg1["text"] == "From ws1"
            assert msg2["type"] == "message"
            assert msg2["text"] == "From ws1"


# ── RoomManager unit tests ─────────────────────────────────────


def test_room_manager_initial_count():
    """RoomManager should report 0 participants for unknown rooms."""
    from community_hub.routes.live import RoomManager
    mgr = RoomManager()
    assert mgr.participant_count("unknown") == 0
