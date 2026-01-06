FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml /app/

RUN uv sync --group prod

COPY . /app
COPY scripts /scripts
RUN chmod +x /scripts/run.sh

EXPOSE 8000
