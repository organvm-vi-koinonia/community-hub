"""JSON API endpoints for all community hub data."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Request
from sqlalchemy import select, func

from koinonia_db.models.salon import SalonSessionRow, Participant, Segment, TaxonomyNodeRow
from koinonia_db.models.reading import Curriculum, ReadingSessionRow, DiscussionQuestion, Guide
from koinonia_db.models.community import Event, Contributor, Contribution

router = APIRouter()


@router.get("/salons")
async def api_salons(request: Request):
    async with request.app.state.db() as session:
        stmt = select(SalonSessionRow).order_by(SalonSessionRow.date.desc())
        rows = (await session.execute(stmt)).scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "date": r.date.isoformat() if r.date else None,
            "format": r.format,
            "facilitator": r.facilitator,
            "organ_tags": r.organ_tags or [],
        }
        for r in rows
    ]


@router.get("/salons/{session_id}")
async def api_salon_detail(request: Request, session_id: int):
    async with request.app.state.db() as session:
        salon = await session.get(SalonSessionRow, session_id)
        if not salon:
            return {"error": "not found"}
        stmt_p = select(Participant).where(Participant.session_id == session_id)
        participants = (await session.execute(stmt_p)).scalars().all()
        stmt_s = select(Segment).where(
            Segment.session_id == session_id
        ).order_by(Segment.start_seconds)
        segments = (await session.execute(stmt_s)).scalars().all()
    return {
        "id": salon.id,
        "title": salon.title,
        "date": salon.date.isoformat() if salon.date else None,
        "format": salon.format,
        "facilitator": salon.facilitator,
        "notes": salon.notes,
        "organ_tags": salon.organ_tags or [],
        "participants": [
            {"name": p.name, "role": p.role} for p in participants
        ],
        "segments": [
            {
                "speaker": s.speaker,
                "text": s.text,
                "start_seconds": s.start_seconds,
                "end_seconds": s.end_seconds,
                "confidence": s.confidence,
            }
            for s in segments
        ],
    }


@router.get("/curricula")
async def api_curricula(request: Request):
    async with request.app.state.db() as session:
        stmt = select(Curriculum).order_by(Curriculum.id)
        rows = (await session.execute(stmt)).scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "theme": r.theme,
            "organ_focus": r.organ_focus,
            "duration_weeks": r.duration_weeks,
            "description": r.description,
        }
        for r in rows
    ]


@router.get("/curricula/{curriculum_id}")
async def api_curriculum_detail(request: Request, curriculum_id: int):
    async with request.app.state.db() as session:
        curriculum = await session.get(Curriculum, curriculum_id)
        if not curriculum:
            return {"error": "not found"}
        stmt = select(ReadingSessionRow).where(
            ReadingSessionRow.curriculum_id == curriculum_id
        ).order_by(ReadingSessionRow.week)
        sessions = (await session.execute(stmt)).scalars().all()
    return {
        "id": curriculum.id,
        "title": curriculum.title,
        "theme": curriculum.theme,
        "organ_focus": curriculum.organ_focus,
        "duration_weeks": curriculum.duration_weeks,
        "description": curriculum.description,
        "sessions": [
            {"id": s.id, "week": s.week, "title": s.title, "duration_minutes": s.duration_minutes}
            for s in sessions
        ],
    }


@router.get("/taxonomy")
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
            result.append({
                "slug": root.slug,
                "label": root.label,
                "organ_id": root.organ_id,
                "description": root.description,
                "children": [
                    {"slug": c.slug, "label": c.label, "description": c.description}
                    for c in children
                ],
            })
    return result


@router.get("/stats")
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
    return {
        "salons": salon_count,
        "curricula": curriculum_count,
        "taxonomy_nodes": taxonomy_count,
        "contributors": contributor_count,
    }
