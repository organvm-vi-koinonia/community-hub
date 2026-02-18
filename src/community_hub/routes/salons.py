"""Salon routes — browse archived salons and transcripts."""

from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import select

from koinonia_db.models.salon import SalonSessionRow, Participant, Segment, TaxonomyNodeRow

router = APIRouter()


@router.get("/")
async def salon_list(request: Request):
    templates = request.app.state.templates
    async with request.app.state.db() as session:
        stmt = select(SalonSessionRow).order_by(SalonSessionRow.date.desc())
        result = await session.execute(stmt)
        sessions = result.scalars().all()
    return templates.TemplateResponse("salons/list.html", {
        "request": request,
        "sessions": sessions,
    })


@router.get("/{session_id}")
async def salon_detail(request: Request, session_id: int):
    templates = request.app.state.templates
    async with request.app.state.db() as session:
        salon = await session.get(SalonSessionRow, session_id)
        if not salon:
            return templates.TemplateResponse("salons/detail.html", {
                "request": request,
                "salon": None,
                "participants": [],
                "segments": [],
            })
        stmt_p = select(Participant).where(Participant.session_id == session_id)
        participants = (await session.execute(stmt_p)).scalars().all()
        stmt_s = select(Segment).where(
            Segment.session_id == session_id
        ).order_by(Segment.start_seconds)
        segments = (await session.execute(stmt_s)).scalars().all()
    return templates.TemplateResponse("salons/detail.html", {
        "request": request,
        "salon": salon,
        "participants": participants,
        "segments": segments,
    })
