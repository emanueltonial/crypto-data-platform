# Data Dictionary

## Trade Entity

Source: Binance REST API — Recent Trades endpoint.

### Table: `trades`

| Column | Python Type | DB Type | Nullable | Description |
| --- | --- | --- | --- | --- |
| `id` | `int` | `BIGINT` | No | Internal PK, autoincrement |
| `trade_id` | `int` | `BIGINT` | No | Unique trade ID from Binance (UNIQUE) |
| `symbol` | `str` | `VARCHAR(20)` | No | Trading pair (e.g. BTCUSDT) |
| `price` | `Decimal` | `NUMERIC(20,8)` | No | Trade execution price |
| `quantity` | `Decimal` | `NUMERIC(20,8)` | No | Base asset amount traded |
| `quote_quantity` | `Decimal` | `NUMERIC(20,8)` | No | Quote asset value (`price * quantity`) |
| `time` | `datetime` | `TIMESTAMPTZ` | No | Trade timestamp (UTC) |
| `is_buyer_maker` | `bool` | `BOOLEAN` | No | `True` if the buyer is the order maker |
| `is_best_match` | `bool` | `BOOLEAN` | No | `True` if this is the best price match available |

### Indexes

- `ix_trades_symbol` — queries filtered by trading pair
- `ix_trades_time` — queries filtered by time range
- `ix_trades_symbol_time` — combined filter queries (primary query path)

## Standardized Format

- All monetary values: `NUMERIC(20, 8)` — 8 decimal places
- Timestamps: `TIMESTAMPTZ` (UTC), serialized as ISO 8601
- Symbols: uppercase string (e.g. `BTCUSDT`, `ETHUSDT`)
- No enum fields — `is_buyer_maker` replaces the conceptual `side` field

## Binance Field Mapping

| Binance field | Table column |
| --- | --- |
| `id` | `trade_id` |
| `price` | `price` |
| `qty` | `quantity` |
| `quoteQty` | `quote_quantity` |
| `time` | `time` |
| `isBuyerMaker` | `is_buyer_maker` |
| `isBestMatch` | `is_best_match` |
