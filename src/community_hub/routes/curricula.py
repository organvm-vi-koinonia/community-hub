"""Curricula routes — browse reading group curricula and sessions."""

from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import select

from koinonia_db.models.reading import Curriculum, ReadingSessionRow, DiscussionQuestion, Guide

router = APIRouter()


@router.get("/")
async def curricula_list(request: Request):
    templates = request.app.state.templates
    async with request.app.state.db() as session:
        stmt = select(Curriculum).order_by(Curriculum.id)
        result = await session.execute(stmt)
        curricula = result.scalars().all()
    return templates.TemplateResponse("curricula/list.html", {
        "request": request,
        "curricula": curricula,
    })


@router.get("/{curriculum_id}")
async def curriculum_detail(request: Request, curriculum_id: int):
    templates = request.app.state.templates
    async with request.app.state.db() as session:
        curriculum = await session.get(Curriculum, curriculum_id)
        if not curriculum:
            return templates.TemplateResponse("curricula/detail.html", {
                "request": request,
                "curriculum": None,
                "sessions": [],
            })
        stmt = select(ReadingSessionRow).where(
            ReadingSessionRow.curriculum_id == curriculum_id
        ).order_by(ReadingSessionRow.week)
        sessions = (await session.execute(stmt)).scalars().all()
    return templates.TemplateResponse("curricula/detail.html", {
        "request": request,
        "curriculum": curriculum,
        "sessions": sessions,
    })


@router.get("/{curriculum_id}/sessions/{session_id}")
async def session_detail(request: Request, curriculum_id: int, session_id: int):
    templates = request.app.state.templates
    async with request.app.state.db() as session:
        reading_session = await session.get(ReadingSessionRow, session_id)
        if not reading_session:
            return templates.TemplateResponse("curricula/session.html", {
                "request": request,
                "reading_session": None,
                "questions": [],
                "guide": None,
            })
        stmt_q = select(DiscussionQuestion).where(
            DiscussionQuestion.session_id == session_id
        )
        questions = (await session.execute(stmt_q)).scalars().all()
        stmt_g = select(Guide).where(Guide.session_id == session_id)
        guide = (await session.execute(stmt_g)).scalar()
    return templates.TemplateResponse("curricula/session.html", {
        "request": request,
        "reading_session": reading_session,
        "questions": questions,
        "guide": guide,
    })
