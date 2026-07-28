# Data Dictionary

## Trade Entity

Source: Binance REST API — Recent Trades endpoint.

### Table: `trades`

| Column           | Python Type | DB Type         | Nullable | Description                                      |
| ---------------- | ----------- | --------------- | -------- | ------------------------------------------------ |
| `id`             | `int`       | `BIGINT`        | No       | Internal PK, autoincrement                       |
| `trade_id`       | `int`       | `BIGINT`        | No       | Unique trade ID from Binance (UNIQUE)            |
| `symbol`         | `str`       | `VARCHAR(20)`   | No       | Trading pair (e.g. BTCUSDT)                      |
| `price`          | `Decimal`   | `NUMERIC(20,8)` | No       | Trade execution price                            |
| `quantity`       | `Decimal`   | `NUMERIC(20,8)` | No       | Base asset amount traded                         |
| `quote_quantity` | `Decimal`   | `NUMERIC(20,8)` | No       | Quote asset value (`price * quantity`)           |
| `time`           | `datetime`  | `TIMESTAMPTZ`   | No       | Trade timestamp (UTC)                            |
| `is_buyer_maker` | `bool`      | `BOOLEAN`       | No       | `True` if the buyer is the order maker           |
| `is_best_match`  | `bool`      | `BOOLEAN`       | No       | `True` if this is the best price match available |

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

## Klines Entity

### Table: `Klines`

| Column                   | Python Type | DB Type         | Nullable | Descrição                   |
| ------------------------ | ----------- | --------------- | -------- | --------------------------- |
| `id`                     | `int`       | `BIGINT`        | No       | PK, autoincrement           |
| `symbol`                 | `str`       | `VARCHAR(20)`   | No       | Trading pair                |
| `interval`               | `str`       | `VARCHAR(5)`    | No       | Kline interval (ex: `1h`)   |
| `open_time`              | `datetime`  | `TIMESTAMPTZ`   | No       | Open of the candle (UTC)    |
| `open_price`             | `Decimal`   | `NUMERIC(20,8)` | No       |                             |
| `high_price`             | `Decimal`   | `NUMERIC(20,8)` | No       |                             |
| `low_price`              | `Decimal`   | `NUMERIC(20,8)` | No       |                             |
| `close_price`            | `Decimal`   | `NUMERIC(20,8)` | No       |                             |
| `volume`                 | `Decimal`   | `NUMERIC(20,8)` | No       | Volume in base asset        |
| `close_time`             | `datetime`  | `TIMESTAMPTZ`   | No       | Candle close (UTC)          |
| `quote_volume`           | `Decimal`   | `NUMERIC(20,8)` | No       | Volume in quote asset       |
| `trades_count`           | `int`       | `INTEGER`       | No       | Num of trades in the candle |
| `taker_buy_base_volume`  | `Decimal`   | `NUMERIC(20,8)` | No       |                             |
| `taker_buy_quote_volume` | `Decimal`   | `NUMERIC(20,8)` | No       |                             |
