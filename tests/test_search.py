"""Tests for search route module."""

from __future__ import annotations


def test_search_module_importable():
    from community_hub.routes.search import router, search_page, search_api, _search_all
    assert router is not None
    assert callable(search_page)
    assert callable(search_api)
    assert callable(_search_all)


def test_search_route_has_get_endpoints():
    from community_hub.routes.search import router
    paths = [r.path for r in router.routes]
    assert "/search" in paths
    assert "/api/search" in paths
