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
    assert hasattr(community, "stats")


def test_api_routes_importable():
    from community_hub.routes import api
    assert hasattr(api, "router")
    assert hasattr(api, "api_salons")
    assert hasattr(api, "api_curricula")
    assert hasattr(api, "api_taxonomy")
    assert hasattr(api, "api_stats")


def test_app_creates():
    from community_hub.app import create_app
    app = create_app()
    assert app.title == "ORGAN-VI Community Hub"
    routes = [r.path for r in app.routes]
    assert "/" in routes
