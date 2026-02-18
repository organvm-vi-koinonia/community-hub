"""JSON API endpoints for all community hub data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, func, text

from koinonia_db.models.salon import SalonSessionRow, Participant, Segment, TaxonomyNodeRow
from koinonia_db.models.reading import Curriculum, ReadingSessionRow, DiscussionQuestion, Guide
from koinonia_db.models.community import Event, Contributor, Contribution

router = APIRouter()


# ── Pydantic Response Models ─────────────────────────────────────────


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    limit: int
    offset: int


class SalonSummary(BaseModel):
    id: int
    title: str
    date: str | None
    format: str
    facilitator: str | None
    organ_tags: list[str] = Field(default_factory=list, examples=[["I", "VI"]])


class ParticipantOut(BaseModel):
    name: str
    role: str


class SegmentOut(BaseModel):
    speaker: str
    text: str
    start_seconds: float
    end_seconds: float
    confidence: float


class SalonDetail(SalonSummary):
    notes: str
    participants: list[ParticipantOut]
    segments: list[SegmentOut]


class CurriculumSummary(BaseModel):
    id: int
    title: str
    theme: str
    organ_focus: str | None
    duration_weeks: int
    description: str


class SessionOut(BaseModel):
    id: int
    week: int
    title: str
    duration_minutes: int


class CurriculumDetail(CurriculumSummary):
    sessions: list[SessionOut]


class TaxonomyChild(BaseModel):
    slug: str
    label: str
    description: str


class TaxonomyRoot(BaseModel):
    slug: str
    label: str
    organ_id: int | None
    description: str
    children: list[TaxonomyChild]


class ContributionOut(BaseModel):
    repo: str
    type: str
    url: str | None
    date: str
    description: str


class ContributorOut(BaseModel):
    github_handle: str
    name: str
    organs_active: list[str] = Field(default_factory=list)
    first_contribution_date: str
    contribution_count: int = 0


class ContributorDetail(ContributorOut):
    contributions: list[ContributionOut]


class StatsOut(BaseModel):
    salons: int = Field(examples=[5])
    curricula: int = Field(examples=[3])
    taxonomy_nodes: int = Field(examples=[42])
    contributors: int = Field(examples=[1])


class HealthDeep(BaseModel):
    status: str
    database: str
    counts: StatsOut
    organ: str = "VI"
    organ_name: str = "Koinonia"
    version: str


class ManifestOut(BaseModel):
    organ_id: str = "VI"
    organ_name: str = "Koinonia"
    organ_slug: str = "vi-koinonia"
    github_org: str = "organvm-vi-koinonia"
    version: str
    endpoints: dict[str, str]
    capabilities: list[str]


# ── Routes ───────────────────────────────────────────────────────────


@router.get("/salons")
async def api_salons(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    async with request.app.state.db() as session:
        total = (await session.execute(
            select(func.count(SalonSessionRow.id))
        )).scalar() or 0
        stmt = (
            select(SalonSessionRow)
            .order_by(SalonSessionRow.date.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await session.execute(stmt)).scalars().all()
    items = [
        SalonSummary(
            id=r.id, title=r.title,
            date=r.date.isoformat() if r.date else None,
            format=r.format, facilitator=r.facilitator,
            organ_tags=r.organ_tags or [],
        )
        for r in rows
    ]
    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/salons/{session_id}", response_model=SalonDetail)
async def api_salon_detail(request: Request, session_id: int):
    async with request.app.state.db() as session:
        salon = await session.get(SalonSessionRow, session_id)
        if not salon:
            raise HTTPException(status_code=404, detail="Salon not found")
        stmt_p = select(Participant).where(Participant.session_id == session_id)
        participants = (await session.execute(stmt_p)).scalars().all()
        stmt_s = select(Segment).where(
            Segment.session_id == session_id
        ).order_by(Segment.start_seconds)
        segments = (await session.execute(stmt_s)).scalars().all()
    return SalonDetail(
        id=salon.id, title=salon.title,
        date=salon.date.isoformat() if salon.date else None,
        format=salon.format, facilitator=salon.facilitator,
        notes=salon.notes, organ_tags=salon.organ_tags or [],
        participants=[ParticipantOut(name=p.name, role=p.role) for p in participants],
        segments=[
            SegmentOut(
                speaker=s.speaker, text=s.text,
                start_seconds=s.start_seconds, end_seconds=s.end_seconds,
                confidence=s.confidence,
            )
            for s in segments
        ],
    )


@router.get("/curricula")
async def api_curricula(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    async with request.app.state.db() as session:
        total = (await session.execute(
            select(func.count(Curriculum.id))
        )).scalar() or 0
        stmt = select(Curriculum).order_by(Curriculum.id).limit(limit).offset(offset)
        rows = (await session.execute(stmt)).scalars().all()
    items = [
        CurriculumSummary(
            id=r.id, title=r.title, theme=r.theme,
            organ_focus=r.organ_focus, duration_weeks=r.duration_weeks,
            description=r.description,
        )
        for r in rows
    ]
    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/curricula/{curriculum_id}", response_model=CurriculumDetail)
async def api_curriculum_detail(request: Request, curriculum_id: int):
    async with request.app.state.db() as session:
        curriculum = await session.get(Curriculum, curriculum_id)
        if not curriculum:
            raise HTTPException(status_code=404, detail="Curriculum not found")
        stmt = select(ReadingSessionRow).where(
            ReadingSessionRow.curriculum_id == curriculum_id
        ).order_by(ReadingSessionRow.week)
        sessions = (await session.execute(stmt)).scalars().all()
    return CurriculumDetail(
        id=curriculum.id, title=curriculum.title, theme=curriculum.theme,
        organ_focus=curriculum.organ_focus, duration_weeks=curriculum.duration_weeks,
        description=curriculum.description,
        sessions=[
            SessionOut(id=s.id, week=s.week, title=s.title, duration_minutes=s.duration_minutes)
            for s in sessions
        ],
    )


@router.get("/taxonomy", response_model=list[TaxonomyRoot])
async def api_taxonomy(request: Request):
    async with request.app.state.db() as session:
        stmt = select(TaxonomyNodeRow).where(
            TaxonomyNodeRow.parent_id.is_(None)
        ).order_by(TaxonomyNodeRow.organ_id)
        roots = (await session.execute(stmt)).scalars().all()
        result = []
        for root in roots:
            stmt_children = select(TaxonomyNodeRow).where(
                TaxonomyNodeRow.parent_id == root.id
            )
            children = (await session.execute(stmt_children)).scalars().all()
            result.append(TaxonomyRoot(
                slug=root.slug, label=root.label,
                organ_id=root.organ_id, description=root.description,
                children=[
                    TaxonomyChild(slug=c.slug, label=c.label, description=c.description)
                    for c in children
                ],
            ))
    return result


@router.get("/contributors")
async def api_contributors(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    async with request.app.state.db() as session:
        total = (await session.execute(
            select(func.count(Contributor.id))
        )).scalar() or 0
        stmt = (
            select(Contributor)
            .order_by(Contributor.first_contribution_date.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await session.execute(stmt)).scalars().all()
    items = []
    for c in rows:
        items.append(ContributorOut(
            github_handle=c.github_handle,
            name=c.name,
            organs_active=c.organs_active or [],
            first_contribution_date=c.first_contribution_date.isoformat(),
            contribution_count=0,
        ))
    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/contributors/{handle}", response_model=ContributorDetail)
async def api_contributor_detail(request: Request, handle: str):
    async with request.app.state.db() as session:
        stmt = select(Contributor).where(Contributor.github_handle == handle)
        contributor = (await session.execute(stmt)).scalar_one_or_none()
        if not contributor:
            raise HTTPException(status_code=404, detail="Contributor not found")
        stmt_c = (
            select(Contribution)
            .where(Contribution.contributor_id == contributor.id)
            .order_by(Contribution.date.desc())
        )
        contributions = (await session.execute(stmt_c)).scalars().all()
    return ContributorDetail(
        github_handle=contributor.github_handle,
        name=contributor.name,
        organs_active=contributor.organs_active or [],
        first_contribution_date=contributor.first_contribution_date.isoformat(),
        contribution_count=len(contributions),
        contributions=[
            ContributionOut(
                repo=c.repo, type=c.type,
                url=c.url, date=c.date.isoformat(),
                description=c.description,
            )
            for c in contributions
        ],
    )


@router.get("/stats", response_model=StatsOut)
async def api_stats(request: Request):
    async with request.app.state.db() as session:
        salon_count = (await session.execute(
            select(func.count(SalonSessionRow.id))
        )).scalar() or 0
        curriculum_count = (await session.execute(
            select(func.count(Curriculum.id))
        )).scalar() or 0
        taxonomy_count = (await session.execute(
            select(func.count(TaxonomyNodeRow.id))
        )).scalar() or 0
        contributor_count = (await session.execute(
            select(func.count(Contributor.id))
        )).scalar() or 0
    return StatsOut(
        salons=salon_count,
        curricula=curriculum_count,
        taxonomy_nodes=taxonomy_count,
        contributors=contributor_count,
    )


@router.get("/health/deep", response_model=HealthDeep)
async def api_health_deep(request: Request):
    """Deep health check — DB connectivity, data counts, organ metadata."""
    try:
        async with request.app.state.db() as session:
            await session.execute(text("SELECT 1"))
            salon_count = (await session.execute(
                select(func.count(SalonSessionRow.id))
            )).scalar() or 0
            curriculum_count = (await session.execute(
                select(func.count(Curriculum.id))
            )).scalar() or 0
            taxonomy_count = (await session.execute(
                select(func.count(TaxonomyNodeRow.id))
            )).scalar() or 0
            contributor_count = (await session.execute(
                select(func.count(Contributor.id))
            )).scalar() or 0
        db_status = "connected"
    except Exception:
        db_status = "error"
        salon_count = curriculum_count = taxonomy_count = contributor_count = 0

    return HealthDeep(
        status="ok" if db_status == "connected" else "degraded",
        database=db_status,
        counts=StatsOut(
            salons=salon_count,
            curricula=curriculum_count,
            taxonomy_nodes=taxonomy_count,
            contributors=contributor_count,
        ),
        version="0.4.0",
    )


@router.get("/manifest", response_model=ManifestOut)
async def api_manifest(request: Request):
    """Organ manifest for ORGAN-IV orchestration registry."""
    base_url = str(request.base_url).rstrip("/")
    return ManifestOut(
        version="0.4.0",
        endpoints={
            "health": f"{base_url}/health",
            "health_deep": f"{base_url}/api/health/deep",
            "stats": f"{base_url}/api/stats",
            "salons": f"{base_url}/api/salons",
            "curricula": f"{base_url}/api/curricula",
            "taxonomy": f"{base_url}/api/taxonomy",
            "contributors": f"{base_url}/api/contributors",
            "search": f"{base_url}/api/search",
            "syllabus": f"{base_url}/api/syllabus/generate",
            "feeds_salons": f"{base_url}/feeds/salons.xml",
            "feeds_events": f"{base_url}/feeds/events.xml",
            "feeds_curricula": f"{base_url}/feeds/curricula.xml",
            "openapi": f"{base_url}/openapi.json",
        },
        capabilities=[
            "salon_archive",
            "reading_curricula",
            "taxonomy_browse",
            "fulltext_search",
            "adaptive_syllabus",
            "community_stats",
            "contributor_profiles",
            "atom_feeds",
            "rate_limiting",
            "websocket_live_salons",
        ],
    )
