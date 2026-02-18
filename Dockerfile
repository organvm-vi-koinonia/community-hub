FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    "koinonia-db @ git+https://github.com/organvm-vi-koinonia/koinonia-db.git" \
    .

EXPOSE 8000

CMD ["uvicorn", "community_hub.app:app", "--host", "0.0.0.0", "--port", "8000"]
