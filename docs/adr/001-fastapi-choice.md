# ADR 001: FastAPI as Web Framework

## Status
Accepted

## Context
ORGAN-VI community-hub needs a web framework for serving HTML pages and JSON APIs. The application connects to PostgreSQL via SQLAlchemy async and renders Jinja2 templates.

## Decision
Use FastAPI with Jinja2 templates.

## Rationale
- **Async-native:** Aligns with SQLAlchemy 2.0 async engine already used across ORGAN-VI
- **Lightweight:** No heavy ORM opinions, admin panels, or batteries we don't need
- **API-first:** Built-in OpenAPI docs, easy to add JSON endpoints alongside HTML
- **Performance:** ASGI-based, efficient for I/O-bound database queries
- **Ecosystem:** Widely adopted, good testing support with httpx

## Alternatives Considered
- **Django:** Too heavy for this use case; brings its own ORM, admin, auth — we already have SQLAlchemy
- **Flask:** Sync-only without extensions; would need async adapter
- **Starlette:** Too low-level; FastAPI adds validation and docs at minimal cost

## Consequences
- Templates use Jinja2 directly (no Django template language)
- Static files served via FastAPI's StaticFiles mount
- Testing uses httpx.AsyncClient or pytest with TestClient
