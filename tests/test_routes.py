"""Tests for community-hub route modules — import and structure checks."""

from __future__ import annotations


def test_salon_routes_importable():
    from community_hub.routes import salons
    assert hasattr(salons, "router")
    assert hasattr(salons, "salon_list")
    assert hasattr(salons, "salon_detail")


def test_curricula_routes_importable():
    from community_hub.routes import curricula
    assert hasattr(curricula, "router")
    assert hasattr(curricula, "curricula_list")
    assert hasattr(curricula, "curriculum_detail")


def test_community_routes_importable():
    from community_hub.routes import community
    assert hasattr(community, "router")
    assert hasattr(community, "events_list")
    assert hasattr(community, "contributors_list")
    assert hasattr(community, "contributor_detail")
    assert hasattr(community, "stats")


def test_api_routes_importable():
    from community_hub.routes import api
    assert hasattr(api, "router")
    assert hasattr(api, "api_salons")
    assert hasattr(api, "api_curricula")
    assert hasattr(api, "api_taxonomy")
    assert hasattr(api, "api_stats")


def test_search_routes_importable():
    from community_hub.routes import search
    assert hasattr(search, "router")
    assert hasattr(search, "search_page")
    assert hasattr(search, "search_api")


def test_syllabus_routes_importable():
    from community_hub.routes import syllabus
    assert hasattr(syllabus, "router")
    assert hasattr(syllabus, "syllabus_form")
    assert hasattr(syllabus, "syllabus_generate")
    assert hasattr(syllabus, "syllabus_view")
    assert hasattr(syllabus, "api_syllabus_generate")


def test_feeds_routes_importable():
    from community_hub.routes import feeds
    assert hasattr(feeds, "router")
    assert hasattr(feeds, "feed_salons")
    assert hasattr(feeds, "feed_events")
    assert hasattr(feeds, "feed_curricula")


def test_live_routes_importable():
    from community_hub.routes import live
    assert hasattr(live, "router")
    assert hasattr(live, "salon_live")
    assert hasattr(live, "salon_ws")
    assert hasattr(live, "RoomManager")
    assert hasattr(live, "manager")


def test_syllabus_uses_shared_service():
    """syllabus.py should import from koinonia_db.syllabus_service, not define its own."""
    from community_hub.routes import syllabus
    import inspect
    source = inspect.getsource(syllabus)
    assert "from koinonia_db.syllabus_service import generate_learning_path" in source
    assert "_generate_path" not in source


def test_app_creates():
    from community_hub.app import create_app
    app = create_app()
    assert app.title == "ORGAN-VI Community Hub"
    assert app.version == "0.4.0"
    routes = [r.path for r in app.routes]
    assert "/" in routes


def test_app_has_all_routers():
    from community_hub.app import create_app
    app = create_app()
    routes = [r.path for r in app.routes]
    assert "/health" in routes
    assert "/salons" in routes or "/salons/" in routes
    assert "/search" in routes or "/search/" in routes


def test_logging_config_importable():
    from community_hub.logging_config import configure_logging, JSONFormatter
    assert callable(configure_logging)
    assert JSONFormatter is not None
