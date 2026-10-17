# Optional future deployment image. No demo exposure by default.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /data && chown appuser:appuser /data
COPY backend/ /app/
USER appuser
ENV FRAMEFORGE_DB_PATH=/data/frameforge.db
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3)' || exit 1
CMD ["python", "-m", "uvicorn", "frameforge.api:app", "--host", "0.0.0.0", "--port", "8000"]
