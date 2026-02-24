"""Tests for community_hub data_export — API routes and community stats."""
import json
from pathlib import Path

from community_hub.data_export import (
    extract_api_routes,
    build_community_stats,
    export_all,
)


SEED_DIR = Path(__file__).parent.parent.parent / "koinonia-db" / "seed"


def test_extract_api_routes():
    """Route extraction returns a non-empty list of routes."""
    routes = extract_api_routes()
    assert len(routes) > 10
    paths = [r["path"] for r in routes]
    assert "/health" in paths
    assert "/api/stats" in paths
    assert "/api/salons" in paths


def test_route_structure():
    """Each route has the expected keys."""
    routes = extract_api_routes()
    for r in routes:
        assert "path" in r
        assert "methods" in r
        assert "name" in r
        assert isinstance(r["methods"], list)
        assert len(r["methods"]) > 0


def test_build_community_stats():
    """Stats computed from real seed data have expected keys and values."""
    stats = build_community_stats(SEED_DIR)
    assert stats["salon_count"] >= 2
    assert stats["curriculum_count"] >= 3
    assert stats["reading_entry_count"] > 10
    assert stats["taxonomy_root_count"] == 8
    assert stats["taxonomy_total_nodes"] > 30
    assert stats["event_count"] >= 3
    assert stats["contributor_count"] >= 1


def test_build_community_stats_missing_dir(tmp_path):
    """Stats default to zero when seed dir is empty."""
    stats = build_community_stats(tmp_path)
    assert stats["salon_count"] == 0
    assert stats["curriculum_count"] == 0
    assert stats["reading_entry_count"] == 0
    assert stats["taxonomy_root_count"] == 0


def test_export_all_writes_files(tmp_path):
    """export_all writes both artifacts to the output directory."""
    paths = export_all(seed_dir=SEED_DIR, output_dir=tmp_path)
    assert len(paths) == 2

    routes_path = tmp_path / "api-routes.json"
    assert routes_path.exists()
    data = json.loads(routes_path.read_text())
    assert data["route_count"] > 10

    stats_path = tmp_path / "community-stats.json"
    assert stats_path.exists()
    data = json.loads(stats_path.read_text())
    assert data["organ"] == "VI"
    assert data["salon_count"] >= 2
