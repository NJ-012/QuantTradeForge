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
