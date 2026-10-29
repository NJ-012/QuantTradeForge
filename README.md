# QuantTradeForge

Extensible algorithmic trading **research** platform. Initial scope: India cash equities (NSE and BSE), intraday, 5-minute and 15-minute bars. Overnight positions are prohibited in the initial design.

This is **not** a live trading bot. Live order submission is forbidden unless you explicitly authorize it and operational, broker, and regulatory requirements are met. No profitability or future return is guaranteed.

## Current status

| Phase | Status |
| ----- | ------ |
| 0 System definition | Recorded in `docs/` (planning-level; not a running system) |
| 1 Market data infrastructure | **In progress** — 1.1–1.2 implemented and tested; 1.3 (ingestion) not started |
| 2+ Strategies, backtest, ML, risk, execution | Planned — not started |

Status vocabulary used in this repo: **Planned**, **In progress**, **Implemented**, **Tested**, **Validated**, **Approved for deployment**. These are not interchangeable. Passing a documentation test is not validation of a strategy.

See [docs/roadmap.md](docs/roadmap.md).

## What exists after Phase 1.2

- Architecture, decisions, data requirements, and schema notes under `docs/`
- `quanttradeforge.data`: instrument/bar/CA models and quality checks
- Labelled **synthetic** JSON fixtures (not market data, not for performance)
- Preserved TSMOM v0.1 **research specification** (not implemented, not backtested)
- No market-data download, no broker adapters, no ML models

## Setup

Python 3.11+ is the intended research language. **No third-party packages are required for Phase 1.2.** Run tests from the repository root so the `quanttradeforge` package imports:

```text
python -m unittest discover -s tests -v
```

Do not install NumPy, Polars, databases, or ML libraries until a later phase needs them.

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
