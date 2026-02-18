"""Community routes — events, contributors, stats."""

from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import select, func

from koinonia_db.models.community import Event, Contributor, Contribution
from koinonia_db.models.salon import SalonSessionRow, TaxonomyNodeRow
from koinonia_db.models.reading import Curriculum, Entry

router = APIRouter()


@router.get("/events")
async def events_list(request: Request):
    templates = request.app.state.templates
    async with request.app.state.db() as session:
        stmt = select(Event).order_by(Event.date.desc())
        events = (await session.execute(stmt)).scalars().all()
    return templates.TemplateResponse("community/events.html", {
        "request": request,
        "events": events,
    })


@router.get("/stats")
async def stats(request: Request):
    templates = request.app.state.templates
    async with request.app.state.db() as session:
        salon_count = (await session.execute(
            select(func.count(SalonSessionRow.id))
        )).scalar() or 0
        curriculum_count = (await session.execute(
            select(func.count(Curriculum.id))
        )).scalar() or 0
        entry_count = (await session.execute(
            select(func.count(Entry.id))
        )).scalar() or 0
        taxonomy_count = (await session.execute(
            select(func.count(TaxonomyNodeRow.id))
        )).scalar() or 0
        contributor_count = (await session.execute(
            select(func.count(Contributor.id))
        )).scalar() or 0
        event_count = (await session.execute(
            select(func.count(Event.id))
        )).scalar() or 0
    return templates.TemplateResponse("community/stats.html", {
        "request": request,
        "stats": {
            "salons": salon_count,
            "curricula": curriculum_count,
            "reading_entries": entry_count,
            "taxonomy_nodes": taxonomy_count,
            "contributors": contributor_count,
            "events": event_count,
        },
    })
