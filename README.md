# Crypto Data Platform

Data pipeline for ingesting cryptocurrency market data from the Binance REST API,
transforming it, and exposing it via FastAPI.

```text
Binance REST API → worker/ → PostgreSQL → app/ → Clients
```

- **`worker/`** — ingestion and transformation (external I/O only)
- **`app/`** — HTTP API, domain logic, persistence

The worker never serves HTTP. The API never talks to Binance.

## Stack

Python 3.12 · FastAPI · SQLAlchemy async · PostgreSQL · httpx · pandas · Docker · uv

## Status

Current version: `v0.1`

- [x] Multi-symbol ingestion pipeline (`httpx` + `pandas`)
- [x] Data normalization and structured logging
- [x] Async database layer (SQLAlchemy async + asyncpg)
- [x] Trade ORM model with full Binance field mapping
- [x] Settings management via `pydantic-settings`
- [x] Docker + Postgres with healthcheck
- [ ] Alembic migrations
- [ ] `TradeRepository` + FastAPI endpoints
- [ ] Worker persisting to Postgres
- [ ] CI/CD via GitHub Actions

## Running locally

```bash
docker compose up db -d
uv sync
python -m worker.trade_pipeline
```

Environment variables are loaded from `.env`.
See [`docs/`](docs/) for architecture decisions and data dictionary.
