# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/organvm-vi-koinonia/community-hub/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/organvm-vi-koinonia/community-hub/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/organvm-vi-koinonia/community-hub/releases/tag/v0.1.0
