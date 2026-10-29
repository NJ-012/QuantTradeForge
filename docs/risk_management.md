# Risk management

Independent of any ML model. Risk has final authority over trade approval **once implemented** (Phase 5). This file records **provisional engineering defaults**, not proven optimal parameters and **not** authorization to trade live.

## Provisional defaults

| Parameter | Initial proposed value |
| --------- | ---------------------: |
| Risk per trade | 0.5% of account equity |
| Daily loss limit | 2% |
| Maximum simultaneous positions | 10 |
| Maximum capital deployment | 80% |
| Overnight exposure | 0% |
| Stop-loss requirement | Mandatory |
| Kill switch | Mandatory |

All values must be configurable when the engine is built.

## Calculation conventions — Open until Phase 5

These affect whether a limit is hit. They are **not** decided in Phase 1.1:

| Topic | Open question |
| ----- | ------------- |
| Equity base | Last mark-to-market equity vs start-of-day equity |
| Daily loss | Realized only vs realized + unrealized |
| Risk per trade | Stop distance × size, with or without modelled costs |
| Capital deployment | Gross notional vs margin vs net exposure |
| Overnight 0% | Flat by session close; no positions through corporate-action gaps |

**Do not** treat a stop order as a guaranteed fill at the stop price.

## Future enforcement list (not implemented)

Maximum risk per trade; sizing from stop distance; funds/margin; portfolio exposure; position and sector concentration; daily loss; leverage; duplicate-order protection; instrument and price checks; stale-data protection; reconciliation; emergency halt; EOD closure.

Kill switch: block new risk; documented policy for open orders and existing positions (to be written before paper trading).

## Capital figures

Research/paper account size is configurable and **unset** here. ₹10,000 is a possible future small-live scenario only (ADR-012), not the research default.
