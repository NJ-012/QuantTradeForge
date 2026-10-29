# Synthetic fixtures

These files are **not** exchange market data. Prices, volumes, symbols (`SYNTHA`), and corporate actions are invented for schema and quality-check tests.

- Do not use for backtests, performance claims, or live trading.
- Manifest flags: `is_synthetic=true`, `not_for_performance=true`.
- The 5-minute series is a **partial** session (including a deliberate 09:30 gap and a zero-volume bar).
- `QTF:NSE:EQ:SYNTHA` and `QTF:BSE:EQ:SYNTHA` share a ticker on purpose: they are distinct instruments.
