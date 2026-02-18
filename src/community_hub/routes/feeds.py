"""Atom 1.0 feeds for salons, events, and curricula."""

from __future__ import annotations

from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring

from fastapi import APIRouter, Request
from fastapi.responses import Response
from sqlalchemy import select

from koinonia_db.models.salon import SalonSessionRow
from koinonia_db.models.reading import Curriculum
from koinonia_db.models.community import Event

router = APIRouter()

ATOM_NS = "http://www.w3.org/2005/Atom"


def _atom_feed(
    title: str,
    feed_url: str,
    site_url: str,
    entries: list[dict],
) -> bytes:
    """Build an Atom 1.0 XML feed from a list of entry dicts."""
    feed = Element("feed", xmlns=ATOM_NS)
    SubElement(feed, "title").text = title
    SubElement(feed, "id").text = feed_url
    SubElement(feed, "link", href=site_url, rel="alternate")
    SubElement(feed, "link", href=feed_url, rel="self")
    SubElement(feed, "updated").text = datetime.now(timezone.utc).isoformat()
    SubElement(feed, "generator").text = "ORGAN-VI Community Hub"

    for entry_data in entries:
        entry_el = SubElement(feed, "entry")
        SubElement(entry_el, "title").text = entry_data["title"]
        SubElement(entry_el, "id").text = entry_data["id"]
        SubElement(entry_el, "link", href=entry_data["link"], rel="alternate")
        SubElement(entry_el, "updated").text = entry_data["updated"]
        if entry_data.get("summary"):
            SubElement(entry_el, "summary").text = entry_data["summary"]

    return b'<?xml version="1.0" encoding="utf-8"?>\n' + tostring(feed, encoding="unicode").encode("utf-8")


@router.get("/feeds/salons.xml")
async def feed_salons(request: Request):
    """Atom feed of salon sessions."""
    base = str(request.base_url).rstrip("/")
    async with request.app.state.db() as session:
        stmt = select(SalonSessionRow).order_by(SalonSessionRow.date.desc()).limit(50)
        rows = (await session.execute(stmt)).scalars().all()

    entries = []
    for r in rows:
        date_str = r.date.isoformat() if r.date else datetime.now(timezone.utc).isoformat()
        entries.append({
            "title": r.title,
            "id": f"{base}/salons/{r.id}",
            "link": f"{base}/salons/{r.id}",
            "updated": date_str,
            "summary": f"Format: {r.format}. Facilitator: {r.facilitator or 'N/A'}.",
        })

    xml = _atom_feed(
        title="ORGAN-VI Salons",
        feed_url=f"{base}/feeds/salons.xml",
        site_url=f"{base}/salons",
        entries=entries,
    )
    return Response(content=xml, media_type="application/atom+xml")


@router.get("/feeds/events.xml")
async def feed_events(request: Request):
    """Atom feed of community events."""
    base = str(request.base_url).rstrip("/")
    async with request.app.state.db() as session:
        stmt = select(Event).order_by(Event.date.desc()).limit(50)
        rows = (await session.execute(stmt)).scalars().all()

    entries = []
    for r in rows:
        date_str = r.date.isoformat() if r.date else datetime.now(timezone.utc).isoformat()
        entries.append({
            "title": r.title,
            "id": f"{base}/community/events#{r.id}",
            "link": f"{base}/community/events",
            "updated": date_str,
            "summary": r.description or "",
        })

    xml = _atom_feed(
        title="ORGAN-VI Community Events",
        feed_url=f"{base}/feeds/events.xml",
        site_url=f"{base}/community/events",
        entries=entries,
    )
    return Response(content=xml, media_type="application/atom+xml")


@router.get("/feeds/curricula.xml")
async def feed_curricula(request: Request):
    """Atom feed of reading curricula."""
    base = str(request.base_url).rstrip("/")
    async with request.app.state.db() as session:
        stmt = select(Curriculum).order_by(Curriculum.id.desc()).limit(50)
        rows = (await session.execute(stmt)).scalars().all()

    entries = []
    for r in rows:
        entries.append({
            "title": r.title,
            "id": f"{base}/curricula/{r.id}",
            "link": f"{base}/curricula/{r.id}",
            "updated": datetime.now(timezone.utc).isoformat(),
            "summary": f"{r.theme} — {r.duration_weeks} weeks. {r.description}",
        })

    xml = _atom_feed(
        title="ORGAN-VI Reading Curricula",
        feed_url=f"{base}/feeds/curricula.xml",
        site_url=f"{base}/curricula",
        entries=entries,
    )
    return Response(content=xml, media_type="application/atom+xml")
