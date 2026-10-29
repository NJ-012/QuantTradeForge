# QuantTradeForge

Extensible algorithmic trading **research** platform. Initial scope: India cash equities (NSE and BSE), intraday, 5-minute and 15-minute bars. Overnight positions are prohibited in the initial design.

This is **not** a live trading bot. Live order submission is forbidden unless you explicitly authorize it and operational, broker, and regulatory requirements are met. No profitability or future return is guaranteed.

## Current status

| Phase | Status |
| ----- | ------ |
| 0 System definition | Recorded in `docs/` (planning-level; not a running system) |
| 1 Market data infrastructure | **In progress** — 1.1–1.2 implemented/tested; 1.3 daily NSE adapter and local sample implemented/tested |
| 2 Strategy contracts | **In progress** — common signal contract and TSMOM configuration boundary added |
| 3+ Backtest, ML, risk, execution | Planned — not started |

Status vocabulary used in this repo: **Planned**, **In progress**, **Implemented**, **Tested**, **Validated**, **Approved for deployment**. These are not interchangeable. Passing a documentation test is not validation of a strategy.

See [docs/roadmap.md](docs/roadmap.md).

## What exists in Phase 1.3

- Architecture, decisions, data requirements, and schema notes under `docs/`
- `quanttradeforge.data`: instrument/bar/CA models and quality checks
- Labelled **synthetic** JSON fixtures (not market data, not for performance)
- Preserved TSMOM v0.1 **research specification** (not implemented, not backtested)
- NSE daily bhavcopy adapter, JSON persistence/loader, and one local exploratory
  sample (not committed, not for performance, and not sufficient for intraday research)
- Cross-file dataset validation for manifest, instrument, and bar identity
- Parser safeguards that reject malformed numeric fields and duplicate EQ symbols
- Phase 2 strategy contracts and an explicit unresolved-decision boundary for TSMOM v0.1
- Initial executable TSMOM entry/hold evaluator using completed bars only
- Configured Wilder ATR stop/target metadata on TSMOM entry signals
- No intraday market-data download, no broker adapters, no ML models

## Setup

Python 3.11+ is the intended research language. **No third-party packages are required for the current Phase 1 implementation.** Run tests from the repository root:

```text
python -m unittest discover -s tests -v
```

To reproduce the bounded NSE sample download (requires network access):

```text
python -m scripts.download_nse_bhavcopy --date 2023-10-30 --output data/local/nse_bhavcopy_2023-10-30
```

The output is intentionally ignored by git. The loader can reopen the
normalized files with `quanttradeforge.data.nse.load_dataset`. Review the
source terms before sharing or using the sample for research claims.

Validate a persisted sample before using it:

```text
python -m scripts.validate_dataset data/local/nse_bhavcopy_2023-10-30
```

The command reports errors and warnings and exits non-zero when blocking
integrity errors are found.

The current sample is daily only. It does not satisfy the required 5-minute
and 15-minute intraday data requirements. Do not install NumPy, Polars,
databases, or ML libraries until a later phase needs them.

Phase 2 currently contains contracts and an initial TSMOM entry/hold evaluator
with ATR-derived risk metadata. Exits, backtesting, and validation are not
implemented. See
[docs/strategy_interface.md](docs/strategy_interface.md).

## Configuration and secrets

Keep credentials out of the repository. Use environment variables or an untracked `.env` (see `.gitignore`). Never commit API keys, tokens, or account identifiers.

## Documentation map

| Document | Purpose |
| -------- | ------- |
| [docs/architecture.md](docs/architecture.md) | Logical components and research vs live split |
| [docs/roadmap.md](docs/roadmap.md) | Phases, status, completion criteria |
| [docs/decisions.md](docs/decisions.md) | Architecture decisions and rationale |
| [docs/data_requirements.md](docs/data_requirements.md) | Data needs, open source questions, licensing |
| [docs/data_schema.md](docs/data_schema.md) | Instrument/bar/CA contracts and quality codes |
| [docs/strategy_specifications/tsmom_v0.1.md](docs/strategy_specifications/tsmom_v0.1.md) | TSMOM v0.1 rules and unresolved items |
| [docs/testing.md](docs/testing.md) | Testing methodology |
| [docs/risk_management.md](docs/risk_management.md) | Provisional risk defaults |
| [docs/operations.md](docs/operations.md) | Paper/live safeguards |

## Development order

Data → strategies → backtesting → ML → risk/execution integration.

Do not skip Phase 1 because documentation folders exist.
