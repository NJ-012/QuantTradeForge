# Architecture decisions

Decisions recorded from the master project specification (2026-10-15). Newer dated entries in this file override older ones. The empty repository contained no conflicting decisions.

Each record: status is **Accepted** unless marked **Open** or **Provisional**.

## ADR-001 — Project identity

- **Decision:** The project name is QuantTradeForge. Do not rename or merge with unrelated trading bots.
- **Rationale:** Single research and execution lineage.
- **Status:** Accepted.

## ADR-002 — Initial market scope

- **Decision:** First implementation target is India cash equities on NSE and BSE. Trading style is intraday. Initial strategy timeframes are 5-minute and 15-minute. Overnight positions are prohibited initially.
- **Rationale:** Narrow, testable first market without encoding exchange logic into strategies.
- **Status:** Accepted.
- **Notes:** NSE/BSE equity is not a permanent architectural limit. Do not add options-specific behaviour to the equity path unless a shared interface requires it.

## ADR-003 — Exchange and listing identity

- **Decision:** NSE and BSE identifiers are not interchangeable. Cross-listed names remain separate internal instruments. Do not auto-combine duplicates.
- **Rationale:** Prices, costs, liquidity, and trading rules differ by venue.
- **Status:** Accepted.

## ADR-004 — Research vs live

- **Decision:** Research may use expensive historical computation and disk. Live decisioning uses in-memory / incremental state and must not block on synchronous DB or CSV I/O.
- **Rationale:** Reproducibility in research; predictable latency in live.
- **Status:** Accepted (design). Not implemented.

## ADR-005 — Development order

- **Decision:** Data → strategies → backtesting → ML → risk/execution integration. Initial mode is research and paper trading.
- **Rationale:** ML and execution without validated data and costs produce false confidence.
- **Status:** Accepted.

## ADR-006 — Language and stack

- **Decision:** Research language is Python. Do not install the full candidate stack (NumPy, Polars, scikit-learn, XGBoost, PyTorch, PostgreSQL, Redis, Docker, Prometheus) until a phase needs it. C++ or specialised infrastructure only if measured need.
- **Rationale:** Avoid unused dependency and HFT theatre.
- **Status:** Accepted.
- **Phase 1.1–1.2:** stdlib only.

## ADR-007 — ML cannot bypass risk

- **Decision:** The ML model never bypasses the independent risk engine. A passing backtest never auto-enables live trading. Real orders require explicit user authorization plus broker/regulatory/operational checks.
- **Rationale:** Safety and auditability.
- **Status:** Accepted.

## ADR-008 — Strategy signals

- **Decision:** Strategies emit standardized signals (at least BUY, SELL, HOLD/NO SIGNAL) with explicit position semantics so SELL is not ambiguous between closing a long and opening a short. Strategies do not submit broker orders.
- **Rationale:** Testable interface; broker independence.
- **Status:** Accepted (design). Implementation in Phase 2.

## ADR-009 — TSMOM v0.1 preservation

- **Decision:** TSMOM v0.1 is an existing research specification. Do not silently replace it. Unresolved rules stay listed until decided in this file or the strategy spec.
- **Rationale:** Continuity of prior research notes.
- **Status:** Accepted.
- **See:** `docs/strategy_specifications/tsmom_v0.1.md`.

## ADR-010 — Experiment reproducibility

- **Decision:** Experiments record strategy id/version, parameters, data source and dataset version, period, cost and execution assumptions, seed if any, metrics, validation results, and software/model version. Do not overwrite historical results without retaining identity.
- **Rationale:** Prevent silent retuning and leakage.
- **Status:** Accepted (design).

## ADR-011 — Configuration vs code

- **Decision:** Trading and risk parameters are configuration, not scattered literals. Secrets stay out of git.
- **Rationale:** Audit and safety.
- **Status:** Accepted.

## ADR-012 — Personal capital vs research account

- **Decision:** A historical personal figure of ₹10,000 may be a **future** small-live scenario only. It is not the research/paper account size. Research capital is configurable and unset in Phase 1.1.
- **Rationale:** Avoid confusing paper metrics with a live bankroll.
- **Status:** Accepted.

## ADR-013 — Internal bar timestamp convention

- **Decision:** Internal OHLCV bars use **period-start**, timezone-aware timestamps. Session logic uses `Asia/Kolkata`. Naive datetimes are rejected.
- **Rationale:** Unambiguous interval identity for 5-minute and 15-minute strategies; vendor period-end stamps must be converted at ingestion (Phase 1.3), not mixed in strategy code.
- **Status:** Accepted for internal schema. Vendor mapping unverified until a source is chosen.
- **Closes:** OPEN-005.

## ADR-014 — Synthetic fixtures are not market data

- **Decision:** Until OPEN-001 is answered, the only in-repo sample is labelled synthetic JSON (`is_synthetic`, `not_for_performance`). It must not be used for performance claims or as a production path.
- **Rationale:** User authorized Phase 1.2 without a data-budget or vendor choice. Synthetic contracts unblock quality tests without downloading or licensing history.
- **Status:** Accepted for Phase 1.2.

## ADR-015 — Corporate actions stored, not applied

- **Decision:** Persist CA events beside unadjusted bars. Do not auto-adjust OHLC in Phase 1.2. Ex-date intraday handling: leave unadjusted; document dataset version when an adjustment method is implemented.
- **Rationale:** Silent mixed adjustment is a common backtest defect.
- **Status:** Accepted.

## Open decisions (material — do not silently close)

| ID | Question | Impact |
| -- | -------- | ------ |
| OPEN-001 | Data budget: free/sample vs paid historical intraday | Licensing, realism of backtests, cost |
| OPEN-002 | Broker already in use (if any) | Later paper API shape only |
| OPEN-003 | Initial universe (e.g. index constituents vs custom) | Storage, survivorship, liquidity filters |
| OPEN-004 | Git remote / GitHub | Collaboration; no push without request |

OPEN-005 closed by ADR-013.

### Working defaults used in Phase 1.2 (not vendor facts)

- **Timezone:** `Asia/Kolkata`
- **Bar labels:** period-start
- **Sample:** synthetic only; no purchase; no bulk download
- **Broker:** none
- **Universe:** schema is universe-agnostic; fixture has two synthetic listings (NSE and BSE) sharing ticker `SYNTHA`

## Superseded decisions

None.
