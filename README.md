# community-hub

ORGAN-VI flagship — the community portal for salons, reading groups, adaptive syllabi, and contributor profiles.

[![CI](https://github.com/organvm-vi-koinonia/community-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/organvm-vi-koinonia/community-hub/actions/workflows/ci.yml)

## Overview

community-hub is a FastAPI web application that serves as the public face of ORGAN-VI Koinonia. It provides both HTML pages (Jinja2 templates) and a JSON API for browsing salon archives, reading curricula, taxonomy, community events, contributor profiles, personalized learning paths, full-text search, and Atom syndication feeds.

**122 tests** | **CSRF protection** | **Rate limiting** | **WebSocket live rooms** | **Atom 1.0 feeds**

## Routes

### Web Pages

| Path | Description |
|------|-------------|
| `/` | Landing page |
| `/salons` | Browse archived salon sessions |
| `/salons/{id}` | Salon detail with transcript viewer |
| `/salons/{id}/live` | Live salon room (WebSocket-powered) |
| `/curricula` | Browse reading group curricula |
| `/curricula/{id}` | Curriculum detail with session list |
| `/curricula/{id}/sessions/{sid}` | Session detail with questions and guide |
| `/community/events` | Community events listing |
| `/community/contributors` | Contributor directory |
| `/community/contributors/{handle}` | Contributor profile with contribution history |
| `/community/stats` | System-wide statistics dashboard |
| `/search?q=` | Full-text search across all content |
| `/syllabus` | Personalized learning path generator (form) |
| `/syllabus/{path_id}` | View a generated learning path |
| `/health` | Health check endpoint |

### JSON API

| Endpoint | Description |
|----------|-------------|
| `GET /api/salons` | Paginated salon sessions |
| `GET /api/salons/{id}` | Salon with participants and transcript |
| `GET /api/curricula` | Paginated curricula |
| `GET /api/curricula/{id}` | Curriculum with sessions |
| `GET /api/taxonomy` | Organ taxonomy tree |
| `GET /api/contributors` | Paginated contributor list |
| `GET /api/contributors/{handle}` | Contributor profile with contributions |
| `GET /api/stats` | Aggregate statistics |
| `GET /api/health/deep` | Deep health check (DB connectivity + counts) |
| `GET /api/manifest` | Organ manifest for ORGAN-IV orchestration |
| `GET /api/search?q=` | Full-text search (JSON) |
| `GET /api/syllabus/generate?organs=I,II&level=beginner` | Generate learning path (JSON) |

### Syndication Feeds

| Endpoint | Description |
|----------|-------------|
| `GET /feeds/salons.xml` | Atom 1.0 feed of salon sessions |
| `GET /feeds/events.xml` | Atom 1.0 feed of community events |
| `GET /feeds/curricula.xml` | Atom 1.0 feed of reading curricula |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `WS /ws/salons/{id}` | Live salon participation (token-authenticated, rate-limited) |

## Architecture

```
community-hub/
├── src/community_hub/
│   ├── app.py              # FastAPI app with lifespan, CORS, CSRF, rate limiting
│   ├── config.py           # Environment-based settings
│   ├── csrf.py             # Double-submit cookie CSRF middleware
│   ├── logging_config.py   # Structured logging
│   ├── routes/
│   │   ├── api.py          # JSON API endpoints
│   │   ├── salons.py       # Salon HTML routes
│   │   ├── curricula.py    # Curricula HTML routes
│   │   ├── community.py    # Events, contributors, stats
│   │   ├── search.py       # Full-text search (HTML + JSON)
│   │   ├── syllabus.py     # Learning path generation
│   │   ├── feeds.py        # Atom 1.0 syndication feeds
│   │   └── live.py         # WebSocket live salon rooms
│   ├── templates/          # Jinja2 templates
│   └── static/             # CSS
├── scripts/
│   └── entrypoint.sh       # Docker entrypoint (runs Alembic then uvicorn)
├── tests/                  # 122 tests
├── Dockerfile
├── render.yaml
└── pyproject.toml
```

**Key dependencies:**
- **koinonia-db** — shared SQLAlchemy models, Alembic migrations (installed from git)
- **FastAPI** — async web framework
- **psycopg 3** — PostgreSQL async driver (Neon-compatible)
- **Jinja2** — HTML templating
- **slowapi** — rate limiting (per-IP)

**Security:**
- CSRF protection via double-submit cookie on all POST routes
- Rate limiting on syllabus generation endpoints (10-20/min)
- WebSocket rate limiting (10 msg/sec) and message size limits (4 KB)
- HTML escaping on all WebSocket broadcast messages
- CORS configurable via `ALLOWED_ORIGINS`

## Development

```bash
# Install koinonia-db + community-hub
pip install "koinonia-db @ git+https://github.com/organvm-vi-koinonia/koinonia-db.git"
pip install -e ".[dev]"

# Run locally
DATABASE_URL=postgresql://... community-hub

# Run tests
pytest tests/ -v

# Interactive API docs
open http://localhost:8000/docs
```

## Deployment

### Docker

```bash
docker build -t community-hub .
docker run -e DATABASE_URL=postgresql://... -p 8000:8000 community-hub
```

The Docker entrypoint automatically runs Alembic migrations before starting uvicorn.

### Render

Push to GitHub and connect via `render.yaml`. Set `DATABASE_URL` in the Render dashboard to the Neon connection string.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | (required) | PostgreSQL connection string (Neon-compatible) |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |
| `DEBUG` | `false` | Enable auto-reload |
| `ALLOWED_ORIGINS` | (empty) | Comma-separated CORS origins |

## Part of ORGAN-VI

This is the flagship application for [organvm-vi-koinonia](https://github.com/organvm-vi-koinonia) — the community and fellowship layer of the eight-organ system.
