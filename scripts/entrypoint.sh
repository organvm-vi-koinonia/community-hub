#!/usr/bin/env bash
set -euo pipefail

echo "=== ORGAN-VI Community Hub — Starting ==="

# Run Alembic migrations if koinonia-db is available
if [ -d "/app/koinonia-db-migrations" ]; then
    echo "Running database migrations..."
    cd /app/koinonia-db-migrations
    DATABASE_URL="$DATABASE_URL" alembic upgrade head
    echo "Migrations complete."
    cd /app
else
    echo "No migration directory found — skipping Alembic."
fi

echo "Starting uvicorn on port ${PORT:-8000}..."
exec uvicorn community_hub.app:app --host 0.0.0.0 --port "${PORT:-8000}"
