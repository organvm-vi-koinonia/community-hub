FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    "koinonia-db @ git+https://github.com/organvm-vi-koinonia/koinonia-db.git" \
    .

# Clone koinonia-db for Alembic migrations
RUN git clone --depth 1 https://github.com/organvm-vi-koinonia/koinonia-db.git /app/koinonia-db-migrations

EXPOSE 8000

ENTRYPOINT ["bash", "/app/scripts/entrypoint.sh"]
