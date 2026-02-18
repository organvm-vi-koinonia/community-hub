"""Tests for API Pydantic response models."""

from __future__ import annotations


def test_pydantic_models_importable():
    from community_hub.routes.api import (
        SalonSummary, SalonDetail, ParticipantOut, SegmentOut,
        CurriculumSummary, CurriculumDetail, SessionOut,
        TaxonomyRoot, TaxonomyChild,
        StatsOut, HealthDeep, ManifestOut,
    )
    assert all([
        SalonSummary, SalonDetail, ParticipantOut, SegmentOut,
        CurriculumSummary, CurriculumDetail, SessionOut,
        TaxonomyRoot, TaxonomyChild,
        StatsOut, HealthDeep, ManifestOut,
    ])


def test_stats_model():
    from community_hub.routes.api import StatsOut
    s = StatsOut(salons=5, curricula=3, taxonomy_nodes=42, contributors=1)
    assert s.salons == 5
    assert s.contributors == 1


def test_manifest_model():
    from community_hub.routes.api import ManifestOut
    m = ManifestOut(
        version="0.2.0",
        endpoints={"health": "http://localhost/health"},
        capabilities=["salon_archive"],
    )
    assert m.organ_id == "VI"
    assert m.organ_name == "Koinonia"
    assert "salon_archive" in m.capabilities


def test_health_deep_model():
    from community_hub.routes.api import HealthDeep, StatsOut
    h = HealthDeep(
        status="ok", database="connected",
        counts=StatsOut(salons=5, curricula=3, taxonomy_nodes=42, contributors=1),
        version="0.2.0",
    )
    assert h.organ == "VI"
    assert h.counts.salons == 5


def test_salon_summary_model():
    from community_hub.routes.api import SalonSummary
    s = SalonSummary(
        id=1, title="Test Salon", date="2026-02-17",
        format="deep_dive", facilitator="Alice",
        organ_tags=["I", "VI"],
    )
    assert s.organ_tags == ["I", "VI"]


def test_curriculum_detail_model():
    from community_hub.routes.api import CurriculumDetail, SessionOut
    c = CurriculumDetail(
        id=1, title="Foundations", theme="recursion",
        organ_focus="I", duration_weeks=6,
        description="Deep dive",
        sessions=[SessionOut(id=1, week=1, title="Week 1", duration_minutes=90)],
    )
    assert len(c.sessions) == 1
    assert c.sessions[0].week == 1


def test_taxonomy_root_model():
    from community_hub.routes.api import TaxonomyRoot, TaxonomyChild
    t = TaxonomyRoot(
        slug="i-theoria", label="Theoria", organ_id=1,
        description="Theory organ",
        children=[TaxonomyChild(slug="recursion", label="Recursion", description="Self-reference")],
    )
    assert len(t.children) == 1
    assert t.children[0].slug == "recursion"
