FROM python:3.11-slim

WORKDIR /app

COPY koinonia-db/ ./koinonia-db/
COPY community-hub/ ./community-hub/

RUN pip install --no-cache-dir ./koinonia-db ./community-hub

EXPOSE 8000

CMD ["uvicorn", "community_hub.app:app", "--host", "0.0.0.0", "--port", "8000"]
