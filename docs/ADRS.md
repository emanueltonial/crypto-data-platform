# Architectural Decision Records

## ADR 001 — Async over sync

**Decision:** Use `asyncio`, `httpx`, and async SQLAlchemy throughout.

**Why:** The system handles multiple crypto pairs simultaneously. Blocking I/O on one symbol would delay all others.

**Trade-off:** Slightly more complexity than sync code, but necessary for throughput at scale.

---

## ADR 002 — pandas in the worker, not in the API

**Decision:** `pandas` is used exclusively in `worker/` for transformation. `app/` does not import it.

**Why:** The worker needs expressive multi-column operations — type casting, renaming, timestamp parsing. The API layer serves already-normalized data and must stay lightweight for request throughput.

**Trade-off:** Two mental models (DataFrame vs ORM), but clear boundary between concerns.

---

## ADR 003 — Repository pattern for all DB access

**Decision:** All SQLAlchemy queries live in `app/repositories/`. No other layer touches the session directly.

**Why:** Decouples persistence from business logic. Swapping storage (Excel → Postgres, or Postgres → another DB) requires changes only in the repository layer.

**Trade-off:** More files, but business logic and transport layers become independently testable.

---

## ADR 004 — httpx over requests in the worker

**Decision:** The worker uses `httpx.Client` instead of `requests`.

**Why:** `httpx` is API-compatible with `httpx.AsyncClient`. When the worker migrates to fully async ingestion (`asyncio.gather` across symbols), only the client instantiation changes — no logic rewrite needed.

**Trade-off:** Currently runs synchronously (sequential symbols). Parallel ingestion is the planned next step.

---

## ADR 005 — pydantic-settings for configuration

**Decision:** All environment variables are loaded through a typed `Settings` class via `pydantic-settings`.

**Why:** `os.environ` returns raw strings. `pydantic-settings` validates types at boot time — a missing `DATABASE_URL` raises immediately on startup, not on the first DB query in production.

**Trade-off:** One additional dependency, but eliminates a class of silent runtime failures.

## ADR 006 — on_conflict_do_nothing for duplicate trades

**Decision:** The repository uses `on_conflict_do_nothing` based on `trade_id`.

**Why:** Binance trade data is immutable — a `trade_id` never changes after execution. Ignoring duplicates is the correct behavior.

**Trade-off:** No visibility into how many records were actually inserted vs. ignored. Acceptable given that the pipeline is idempotent by design.

## ADR 007 — Layered testing strategy

**Decision:** Tests mirror the architecture in three layers: unit/ (pure
transform, no I/O), service/ (TradeService with FakeTradeRepository, no DB),
api/ (endpoints against real Postgres via httpx ASGITransport).

**Why:** Each layer fails for a distinct reason — unit catches logic bugs,
service catches business-rule bugs, api catches wiring/SQL bugs. Mocking only
the repository in service/ keeps those tests fast and DB-free; api/ stays
un-mocked on purpose to catch what the service mock hides.

**Trade-off:** api/ requires a running Postgres (crypto_test), so the full
suite isn't fully hermetic. Acceptable — the project's types (NUMERIC,
TIMESTAMPTZ, on_conflict) are Postgres-specific and can't be validated on SQLite.
