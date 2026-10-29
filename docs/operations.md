# Operations

Paper and live safeguards. **Live trading is not enabled.**

## Modes

| Mode | Meaning | When |
| ---- | ------- | ---- |
| Research | Offline data, experiments, no orders | Current |
| Paper | Live or delayed data, simulated or paper-broker fills, real risk logic | After Phases 1–6 as applicable |
| Live | Real orders | Only after validation **and** explicit written/user authorization |

A passing backtest must not switch the process into live mode.

## Secrets

API keys, tokens, and account IDs stay in the environment or an untracked `.env`. Rotate if leaked. Do not paste secrets into docs or issues.

## Paper-trading expectations (future)

- Independent risk engine on the path
- Kill switch
- EOD square-off policy
- Reconciliation of intended vs paper positions
- Logging of data age, decisions, and simulated orders
- No silent failover to a live adapter

## Live (blocked)

Do not submit real orders until:

1. User explicitly authorizes live execution
2. Broker, regulatory, and operational requirements are addressed
3. Mode is configured live **on purpose**, not by default

Network, broker, and exchange delay are outside this application’s sole control. Latency instrumentation is a later phase; this project does not claim nanosecond execution.

## Recovery

Not implemented. Future work: restart from in-memory snapshot + audit log, never from an ambiguous CSV in the live path.

## Incident defaults (documented now)

- If data is stale or invalid: do not enter new risk
- If kill switch is on: no new risk; flatten policy TBD before paper
- If session is closed: no overnight inventory in initial scope
