# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-02-17

### Added
- **AQUA COMMUNIS sprint** — live platform with real-time features
- WebSocket live salon rooms (`/salons/{id}/live`, `/ws/salons/{id}`) with RoomManager, broadcast, and 30s keepalive
- Atom 1.0 feeds: `/feeds/salons.xml`, `/feeds/events.xml`, `/feeds/curricula.xml` with autodiscovery links
- Contributor profiles: `/community/contributors`, `/community/contributors/{handle}` (HTML + JSON API)
- Pagination on all list endpoints (`limit`/`offset` query params, prev/next navigation)
- Rate limiting via slowapi (`10/min` POST syllabus, `20/min` GET API syllabus)
- 32 new integration tests (TestClient with mocked DB, WebSocket tests)
- `/api/manifest` now reports 10 capabilities including `atom_feeds`, `rate_limiting`, `websocket_live_salons`

### Changed
- CORS now allows POST in addition to GET
- Syllabus generation logic extracted to `koinonia_db.syllabus_service` (shared service)
- `syllabus.py` reduced from 237 to 107 lines (deduplication)

### Fixed
- Version consistency across pyproject.toml, app.py, and test assertions

## [0.3.0] - 2026-02-17

### Added
- **IGNIS KOINOS sprint** — production deployment infrastructure
- Dark alchemical theme (Playfair Display + Inter + JetBrains Mono, gold/indigo accents)
- SVG hexagonal favicon with organ numeral
- Full-text search (`/search`, `/api/search`) using PostgreSQL tsvector with highlighted results
- Adaptive syllabus generator (`/syllabus`, `/api/syllabus/generate`) with DB persistence
- Structured JSON logging (`logging_config.py`) for production observability
- HTML error pages with browser/API content negotiation
- Alembic migrations in Docker entrypoint (runs before app start)
- Cross-organ API: `/api/health/deep`, `/api/manifest`
- Pydantic response models on all API endpoints
- Organ-colored tags, card hover glow, transcript timeline styling

### Changed
- Render.yaml switched from `runtime: python` to `runtime: docker` for full build control
- Dockerfile now installs git, clones koinonia-db for Alembic, uses entrypoint script
- Version bumped to 0.2.0

## [0.2.0] - 2026-02-17

### Added
- `/health` endpoint returning `{"status": "ok"}`
- CORS middleware (configurable via `ALLOWED_ORIGINS` env var)
- CI workflow (`.github/workflows/ci.yml`)
- README.md with full route documentation and architecture guide

### Fixed
- API routes now return HTTP 404 instead of 200 with `{"error": "not found"}`
- Template routes now raise HTTPException(404) for missing records
- Session detail route now validates `curriculum_id` matches the session
- Broken type annotation on index route (`"fastapi.Request"` → `Request`)
- Dockerfile and render.yaml use `git+https://` for koinonia-db (was broken local path)

### Changed
- `koinonia-db` dependency uses git URL for deployment compatibility

## [0.1.0] - 2026-02-17

### Added
- FastAPI application with Jinja2 templates
- Salon archive browser with transcript viewer
- Reading curricula browser with session details
- Community stats dashboard
- JSON API for all data (salons, curricula, taxonomy, stats)
- Mobile-responsive CSS (no framework dependencies)
- Dockerfile and render.yaml for deployment
- Test suite for config, routes, and app structure

[Unreleased]: https://github.com/organvm-vi-koinonia/community-hub/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/organvm-vi-koinonia/community-hub/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/organvm-vi-koinonia/community-hub/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/organvm-vi-koinonia/community-hub/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/organvm-vi-koinonia/community-hub/releases/tag/v0.1.0
