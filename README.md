# community-hub

ORGAN-VI flagship — the community portal for salons, reading groups, and contributor stats.

[![CI](https://github.com/organvm-vi-koinonia/community-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/organvm-vi-koinonia/community-hub/actions/workflows/ci.yml)

## Overview

community-hub is a FastAPI web application that serves as the public face of ORGAN-VI Koinonia. It provides both HTML pages (Jinja2 templates) and a JSON API for browsing salon archives, reading curricula, taxonomy, community events, and system-wide statistics.

## Routes

### Web Pages
| Path | Description |
|------|-------------|
| `/` | Landing page |
| `/salons` | Browse archived salon sessions |
| `/salons/{id}` | Salon detail with transcript viewer |
| `/curricula` | Browse reading group curricula |
| `/curricula/{id}` | Curriculum detail with session list |
| `/curricula/{id}/sessions/{sid}` | Session detail with questions and guide |
| `/community/events` | Community events listing |
| `/community/stats` | System-wide statistics dashboard |
| `/health` | Health check endpoint |

### JSON API
| Endpoint | Description |
|----------|-------------|
| `GET /api/salons` | All salon sessions |
| `GET /api/salons/{id}` | Salon with participants and transcript |
| `GET /api/curricula` | All curricula |
| `GET /api/curricula/{id}` | Curriculum with sessions |
| `GET /api/taxonomy` | Organ taxonomy tree |
| `GET /api/stats` | Aggregate statistics |

## Architecture

```
community-hub/
├── src/community_hub/
│   ├── app.py          # FastAPI app with lifespan, CORS, health check
│   ├── config.py       # Environment-based settings
│   ├── routes/
│   │   ├── api.py      # JSON API endpoints
│   │   ├── salons.py   # Salon HTML routes
│   │   ├── curricula.py # Curricula HTML routes
│   │   └── community.py # Events and stats
│   ├── templates/      # Jinja2 templates
│   └── static/         # CSS
├── tests/
├── Dockerfile
├── render.yaml
└── pyproject.toml
```

**Key dependencies:**
- **koinonia-db** — shared SQLAlchemy models (installed from git)
- **FastAPI** — async web framework
- **psycopg 3** — PostgreSQL async driver
- **Jinja2** — HTML templating

## Development

```bash
# Install koinonia-db + community-hub
pip install "koinonia-db @ git+https://github.com/organvm-vi-koinonia/koinonia-db.git"
pip install -e ".[dev]"

# Run locally
DATABASE_URL=postgresql://... community-hub
```

## Deployment

### Docker
```bash
docker build -t community-hub .
docker run -e DATABASE_URL=postgresql://... -p 8000:8000 community-hub
```

### Render
Push to GitHub and connect via `render.yaml`. Set `DATABASE_URL` in Render dashboard.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | (required) | PostgreSQL connection string |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |
| `DEBUG` | `false` | Enable auto-reload |
| `ALLOWED_ORIGINS` | (empty) | Comma-separated CORS origins |

## Part of ORGAN-VI

This is the flagship application for [organvm-vi-koinonia](https://github.com/organvm-vi-koinonia) — the community and fellowship layer of the eight-organ system.
