# Roadmap

Honest status of QuantTradeForge. Folder presence does not complete a phase.

## Status vocabulary

| Status | Meaning |
| ------ | ------- |
| Planned | Described; not built |
| In progress | Active work in this phase |
| Implemented | Code or artefacts exist |
| Tested | Automated or documented tests have been run and reported |
| Validated | Research evidence (e.g. realistic out-of-sample backtest) supports the claim |
| Approved for deployment | Explicit human authorization for paper or live use |

These statuses are not interchangeable. A documentation test is not strategy validation.

## Phase 0 — System definition

**Status:** Recorded in `docs/` (planning-level).

Includes market scope, trading style, risk philosophy, strategy-library goals, AI responsibilities, latency principles, and technology direction.

**Completion criteria:** Decisions written in `docs/decisions.md` and this roadmap. Met at documentation level in Phase 1.1. Not a running system.

## Phase 1 — Market data infrastructure

**Status:** In progress (1.1–1.2 done; ingestion and a licensed/historical sample are not).

| Sub-phase | Intent | Status |
| --------- | ------ | ------ |
| 1.1 Data requirements and source evaluation | Requirements, licensing questions, no bulk download | **Implemented** (docs) and **Tested** (`tests/test_phase11_docs.py`). Not a data-vendor validation. |
| 1.2 Schemas, quality rules, small sample fixtures | Contracts before scale | **Implemented** and **Tested** (`quanttradeforge.data`, synthetic fixtures). Sample is synthetic — not **Validated** market data. |
| 1.3 Ingestion adapters and storage for approved sample | Bounded NSE daily adapter and local sample; intraday source still open | **In progress** |

**Phase 1 completion criteria (not yet met):**

- Data requirements documented (1.1)
- Feasible sources evaluated without unverified vendor claims (1.1)
- Normalized instrument and bar schemas
- Data-quality checks implemented and tested
- Reproducible historical storage for a **small** sample
- Timestamp/timezone and corporate-action policy recorded
- No large unpaid/unlicensed dataset in the repo

### Phase 1.3 progress

- Implemented: official NSE daily bhavcopy URL construction and ZIP/CSV parsing.
- Implemented: normalized NSE EQ instruments and daily bars with source metadata.
- Implemented: local JSON persistence that refuses accidental overwrite.
- Implemented: cross-file dataset validation and a command-line validator.
- Implemented: row-level numeric validation and duplicate-symbol rejection in
  the NSE adapter.
- Downloaded locally: one 30 October 2023 NSE daily sample; it is ignored by git
  and marked not-for-performance.
- Outstanding: primary-document licensing review, 5-minute/15-minute source,
  corporate-action ingestion, and versioned multi-file storage acceptance.

**Not complete** when this file exists.

## Phase 2 — Strategy library

**Status:** In progress (contract foundation only; Phase 1 remains incomplete).

Common strategy interface; preserve TSMOM v0.1; additional strategies only with distinguishable rules. Target of ~40 is a library goal, not a requirement to activate 40.

### Phase 2 progress

- Implemented: broker-independent `Strategy` and standardized `Signal`
  contracts with explicit position semantics.
- Implemented: TSMOM v0.1 configuration boundary that refuses unresolved
  specification decisions.
- Outstanding: resolve TSMOM decisions, implement the strategy, add
  chronological signal tests, and backtest only after suitable intraday data
  is approved.

## Phase 3 — Backtesting and validation

**Status:** Planned.

Chronological engine, costs, metrics, OOS and walk-forward when data allow. No fabricated results.

## Phase 4 — AI/ML

**Status:** Planned. Do not start before reliable data, strategy outputs, and evaluation datasets exist.

## Phase 5 — Risk engine

**Status:** Planned. Independent of ML. Provisional defaults in `docs/risk_management.md`.

## Phase 6 — Execution engine

**Status:** Planned. Paper execution and broker abstraction. No live orders by default.

## Phase 7 — Paper trading

**Status:** Planned.

## Phase 8 — Controlled live deployment

**Status:** Planned. Only after validation **and** explicit authorization.

## Phase 9 — Monitoring and retraining

**Status:** Planned.

## Future expansion

Futures, options, other markets, specialized latency infrastructure — when justified.

## Next authorized task after 1.2

Phase 1.3: ingestion adapters behind an interface for an **approved** source, plus persistence of a small licensed or explicitly allowed sample. A bounded NSE daily engineering sample is now available locally, but OPEN-001 remains open for reuse rights and an intraday source. Do not begin Phase 2 unless Phase 1 completion criteria are met or you explicitly authorize a scoped exception.

Phase 1 is still **not complete**: no vendor evaluation from primary docs, no
approved 5-minute/15-minute historical source. Phase 2 work is limited to
contracts and specification preservation until those data blockers are
resolved.
