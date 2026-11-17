FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

COPY alembic.ini .
COPY alembic/ ./alembic/

USER appuser

EXPOSE 8000 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["python", "-c", "import os, urllib.request; port = int(os.getenv('PORT', '8000')); urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=3)"]

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]