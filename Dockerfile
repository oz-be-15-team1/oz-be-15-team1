FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml /app/

RUN uv pip install --system --no-cache \
    celery \
    django \
    django-celery-beat \
    django-celery-results \
    django-cors-headers \
    "django-extensions>=4.1" \
    djangorestframework \
    drf-yasg \
    matplotlib \
    pandas \
    "pre-commit>=4.5.1" \
    "psycopg[binary]" \
    pillow \
    redis \
    "ruff>=0.14.10" \
    gunicorn \
    "djangorestframework-simplejwt>=5.5.1" \
    "python-dotenv>=1.2.1"

COPY . /app
RUN rm -rf /app/.venv || true
COPY scripts /scripts
RUN chmod +x /scripts/run.sh

EXPOSE 8000
