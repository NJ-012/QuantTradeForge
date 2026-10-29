# Testing and validation

## Levels (do not collapse)

| Level | What it proves | What it does not prove |
| ----- | -------------- | ---------------------- |
| Documentation / contract tests | Required files and stated decisions exist | Data quality, alpha, safety in production |
| Unit tests | Functions behave on fixtures | Strategy profitability |
| Integration tests | Modules compose | Live broker correctness |
| Walk-forward / OOS backtest | Historical behaviour under stated assumptions | Future returns |
| Paper trading | Operational path with simulated fills | Filled live orders |
| Live | Explicitly authorized production | — |

A toy test that a signal function returns `BUY` is not validation.

## Methodology for later trading logic

When strategies and backtests exist, tests must cover:

- Signal timing (no look-ahead; entry on next open if specified)
- Stop/target order when both trade in one bar
- Position state (long/short/flat; no ambiguous SELL)
- Transaction costs as configuration
- EOD square-off
- Timestamp timezone awareness
- Failure paths (missing data, invalid OHLC)

Chronological splits: do not tune on the final test period.

## Phase 1.1 tests

`tests/test_phase11_docs.py` asserts that Phase 1.1 required documents exist and contain a few non-negotiable phrases (project name, TSMOM preservation, open data questions).

## Phase 1.2 tests

- `tests/test_data_models.py` — instrument identity, timezone-aware bars
- `tests/test_data_quality.py` — OHLC, duplicates, order, gaps, zero volume (no silent repair)
- `tests/test_synthetic_fixtures.py` — labelled synthetic sample load

Synthetic fixture tests are **not** evidence of market-data quality or strategy performance.

Run:

```text
python -m unittest discover -s tests -v
```

Stdlib `unittest` only. pytest is not required in this phase.

## Reporting rule

Report exactly which tests passed or failed. Do not fabricate outcomes or backtest statistics.
