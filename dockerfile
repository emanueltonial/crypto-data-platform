# syntax=docker/dockerfile:1.7

# builder
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# runtime
FROM python:3.12-slim-bookworm
WORKDIR /app

COPY --from=builder /app/.venv/ /app/.venv/
ENV PATH="/app/.venv/bin:$PATH"

# non root user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]