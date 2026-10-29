# Strategy interface

Phase 2 begins with contracts, not a trading signal implementation. The
`quanttradeforge.strategies` package defines:

- `Strategy.evaluate(bars) -> Signal` for broker-independent strategy logic.
- `SignalAction` with explicit `HOLD`, `ENTER`, and `EXIT` actions.
- `PositionIntent` with explicit `FLAT`, `LONG`, and `SHORT` semantics.
- `Signal` metadata containing timestamp, instrument, strategy identity,
  reason, and optional stop/target distances.

Signals are decisions only. They do not submit orders or call a broker.
Timestamps must be timezone-aware, and `HOLD` must explicitly use a `FLAT`
position intent.

`TSMOMConfig` preserves the recorded TSMOM v0.1 defaults while requiring all
previously unresolved decisions to be supplied before a future implementation
can use the configuration. TSMOM signal generation is not implemented,
backtested, validated, or approved for deployment.

The initial evaluator now supports the explicitly configured
`simple_close_to_close` formula and `volatility_ddof` of 0 or 1. It evaluates
only the completed bars supplied to it, requires chronological single-instrument
5-minute data, emits `ENTER` or `HOLD`, and refuses unresolved configurations.
The evaluator now computes Wilder ATR from completed bars and attaches fixed
initial stop and target distances to entry signals using the configured
`1.5 × ATR` and `2R` values. Reversal exits, end-of-day handling, gap
resolution, and execution are not yet implemented.
