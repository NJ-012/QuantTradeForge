# Architecture

Logical responsibilities for QuantTradeForge. This is **not** a requirement to create a microservice per box. The initial form is a modular Python application.

Phase 1.2 implements in-process data **contracts** and quality checks. Ingestion adapters, databases, and live feeds are not implemented.

## Separation of pipelines

### Research and training

Historical ingestion → validation and normalization → features → strategies → backtesting → cost/slippage modelling → performance evaluation → out-of-sample and walk-forward work → strategy-performance datasets → ML training (later) → versioned approved artefacts.

Research code may use disk, databases, and expensive historical windows.

### Live trading (future)

Feed → ingest → in-memory market state → incremental features → regime assessment → eligibility/ranking → strategy evaluation → trade/no-trade → **independent risk** → order management → broker adapter → exchange.

The live decision path must not depend on synchronous database queries, CSV writes, or other blocking disk I/O. Persistence and monitoring belong off the critical path.

ML must never bypass the risk engine.

## Logical modules

| Module | Responsibility | Phase when implementation is in scope |
| ------ | -------------- | ------------------------------------- |
| Data ingestion | Historical and later live adapters behind a common interface | 1 |
| Data validation | Duplicates, gaps, stale/out-of-order timestamps, OHLC consistency | 1 |
| Instrument management | Internal instrument IDs; exchange-specific symbols; no NSE/BSE merge | 1 |
| Corporate actions | Splits, bonuses, dividends, rights, mergers as dataset versions | 1 |
| Feature engineering | Research batch vs live incremental | 2–4 |
| Strategy interface | Standard signals; no broker calls | 2 |
| Strategy library | Versioned specifications and implementations | 2 |
| Backtesting | Chronological events, costs, fills, EOD square-off | 3 |
| Performance metrics | Net/gross P&amp;L, drawdown, risk-adjusted stats | 3 |
| ML training/inference | Regime, ranking, strategy selection, abstain | 4 |
| Risk management | Final authority on trade approval | 5 |
| Order management | Lifecycle, not strategy-owned | 6 |
| Broker adapters | Paper first; vendor-specific later | 6–7 |
| Monitoring | Logs, latency, data age, reconciliation | 7–9 |

## Instrument abstraction

Internal representation must include at least:

- Internal instrument identifier
- Exchange (NSE and BSE are not interchangeable)
- Exchange-specific symbol or identifier
- ISIN where available
- Instrument type
- Currency
- Trading status
- Tick size and lot size where applicable

Duplicate listings across exchanges remain **separate** tradable instruments. Liquidity, costs, and prices are not blended.

NSE/BSE cash equity is the first **implementation target**, not a permanent limitation. Options-specific fields stay out of the equity path unless required by a shared interface.

## Execution abstraction (future)

Strategies emit signals only. They never submit broker orders.

Planned adapter kinds: paper broker, broker-specific adapter, later low-latency adapter. Strategy code must not depend on a vendor API.

## Latency stance

Design for in-memory live state and measurable timestamps. Do not build HFT infrastructure (FPGA, kernel bypass, colocation) without measured need. Python is the research and orchestration language until profiling justifies otherwise.

## What this document is not

- Not a deployed architecture
- Not a data-provider contract
- Not authorization for live trading
