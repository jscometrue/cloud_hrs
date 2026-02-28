FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
# Ensure email-validator is installed for Pydantic EmailStr (avoids Render/cache issues)
RUN python -m pip install --no-cache-dir email-validator
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

# Render sets PORT inside the container (usually 10000).
# Use that if available, otherwise fall back to 8000 for local runs.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

