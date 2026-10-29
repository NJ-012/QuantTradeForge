# Data schema (Phase 1.2)

Internal contracts for instruments, OHLCV bars, corporate-action events, and dataset identity. Implemented in `quanttradeforge.data`. No vendor ingestion (Phase 1.3).

## Instrument

| Field | Type | Notes |
| ----- | ---- | ----- |
| instrument_id | str | Namespaced, e.g. `QTF:NSE:EQ:SYNTHA` |
| exchange | str | Venue code (`NSE`, `BSE`, later others). Not interchangeable. |
| venue_symbol | str | Exchange-specific symbol |
| venue_token | str, optional | Exchange numeric/token id if a source provides one |
| isin | str, optional | |
| instrument_type | `EQUITY` or `INDEX` | Options fields are not in this equity schema |
| currency | str | `INR` for initial scope |
| trading_status | ACTIVE / SUSPENDED / DELISTED / UNKNOWN | |
| tick_size, lot_size | decimal / int, optional | |
| segment | str, optional | e.g. EQ |
| listing_date, delisting_date | date, optional | Survivorship |

Same ticker on NSE and BSE **must** use two instrument_ids.

## Bar

| Field | Type | Notes |
| ----- | ---- | ----- |
| instrument_id | str | |
| bar_open_ts | timezone-aware datetime | **Period start** (ADR-013). Naive timestamps rejected. |
| timeframe | `1m` / `5m` / `15m` / `1d` | |
| open, high, low, close, volume | Decimal | |
| turnover | Decimal, optional | |
| session_date | date | Calendar date of the cash session in `Asia/Kolkata` |
| dataset_version | str | Ties bars to a manifest |
| is_synthetic | bool | Must be true for synthetic fixtures |
| source | str, optional | `synthetic` for fixtures |

Vendor timestamp conventions are mapped **into** this period-start IST (or offset-aware) representation at ingestion time. Mapping is not implemented until a source is approved.

## Dataset manifest

Required flags for synthetic samples: `is_synthetic=true`, `not_for_performance=true`. Adjustment policy is recorded (`unadjusted` for the Phase 1.2 sample). Mixing unadjusted and adjusted bars under one version is a defect.

## Corporate actions

Event rows (`split`, `bonus`, `dividend`, `rights`, `merger`, `other`) with optional ratio and cash amount. **Phase 1.2 does not apply adjustments to prices.** Intraday bars on an ex-date: keep unadjusted prints; do not invent an overnight adjusted series. Rebuild rules belong in a later dataset version.

## Quality codes (non-exhaustive)

| Code | Typical severity | Repair? |
| ---- | ---------------- | ------- |
| DUPLICATE_TIMESTAMP | error | Never average |
| OUT_OF_ORDER | error | Caller may `sort_bars`; do not drop |
| MISSING_BAR | warning | Do not forward-fill OHLC |
| OHLC_HIGH / OHLC_LOW / HIGH_LT_LOW | error | Reject for research use |
| NEGATIVE_VOLUME | error | |
| ZERO_VOLUME | warning | Keep |
| OUTSIDE_SESSION | warning | |
| MULTI_INSTRUMENT_SERIES | error | Split by instrument_id |
| TICK_SIZE | warning | |

Regular-session grid for gap checks: 09:15–15:30 `Asia/Kolkata`, last 5-minute period-start 15:25. Auction/pre-open not on this grid. Holiday calendars are not implemented.

## Storage

Phase 1.2 stores the tiny sample as JSON under `tests/fixtures/synthetic/`. PostgreSQL/TimescaleDB is still not installed.
