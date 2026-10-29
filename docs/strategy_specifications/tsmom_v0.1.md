# TSMOM v0.1 — time-series momentum (research specification)

**Strategy identifier:** `TSMOM`  
**Version:** `0.1`  
**Family:** Momentum  
**Status:** Specified (preliminary). **Not implemented. Not tested as code. Not backtested. Not validated. Not approved for deployment.**

This file preserves prior project notes. Do not silently replace these rules with a different strategy. Changes require a new version and an ADR.

## Recorded rules

| Parameter | Recorded value |
| --------- | -------------- |
| Primary data | 5-minute OHLCV |
| Momentum lookback | 10 candles |
| Volatility estimate | Standard deviation of returns over 20 observations |
| Momentum threshold | 1 standard deviation |
| Stop-loss distance | 1.5 × ATR(14) |
| Profit target | 2R, where R is the initial stop-loss distance |
| Entry | Next candle **open** after the signal candle **closes** |
| Stop vs target in the same candle | Conservatively assume the **stop** is hit first |
| End of day | Forced position closure |
| Pyramiding | None |
| Overnight positions | None |
| Costs | Brokerage, statutory charges, slippage, and other applicable costs **configurable** |

## Unresolved decisions (do not invent when coding)

Documented so Phase 2 cannot quietly fill gaps.

### 1. Momentum-return formula

Not specified. Candidates to decide later:

- Simple close-to-close: \(P_t / P_{t-10} - 1\)
- Log: \(\ln P_t - \ln P_{t-10}\)
- Sum of 10 one-bar returns

Inclusive vs exclusive window endpoints are unspecified.

### 2. Rolling standard deviation

Not specified: population (`n`) vs sample (`n-1`); which return series (one-bar vs lookback momentum); whether the 20 observations are trailing **completed** bars only (required to avoid look-ahead).

### 3. Long and short entry thresholds

Not specified whether:

- Long when momentum \(> +1\sigma\) and short when momentum \(< -1\sigma\)
- Long-only
- A dead zone of \(|m| \le \sigma\) is HOLD

Cash-equity **short availability** (borrow, exchange product) is **Open** and may force long-only regardless of the statistical rule.

### 4. Momentum-reversal exit

Not specified whether an opposite-threshold signal exits (and/or flips) before stop, target, or EOD. Recorded rules name stop, target, and EOD; reversal is **unresolved**.

### 5. ATR calculation and availability

Not specified: Wilder RMA vs SMA of true range; first bar when ATR(14) is valid; whether ATR uses the signal bar (known at close) for the **next** bar’s stop distance.

### 6. Stop and target updates

Recorded text says “initial” stop-loss distance for R. **Provisional reading:** stop and target are **fixed at entry**. Trailing is **not** in v0.1 unless a later version says so.

### 7. Gaps, missing candles, halts, EOD timing

Unresolved:

- Gap through stop: fill at next open vs stop price (realism vs spec conservatism)
- Missing bars: skip vs treat as no signal
- Halts: no new entries; exits unspecified
- EOD clock: square-off at or before 15:30 IST; which bar is last tradable 5-minute bar; auction period excluded or not
- Holiday calendars per exchange

### 8. Execution price and orders

Unresolved: marketable order at next open; slippage model; bid/ask (often unavailable on OHLC-only data); partial fills; rejection. Costs must remain configurable; **no default rupee schedule is claimed** here (avoid inventing brokerage tariffs).

## Position semantics (for future interface)

When implemented, signals must distinguish opening long, opening short, closing long, closing short, and HOLD. Ambiguous `SELL` is not acceptable.

Entry is **not** on the signal bar close. Evaluation of bar \(t\) may use data through \(t\)’s close only; the earliest fill is bar \(t+1\) open.

## Implementation and results

| Claim | Allowed now |
| ----- | ----------- |
| Spec file exists | Yes |
| Python strategy class | No |
| Reproducible backtest metrics | **No — none exist** |
| Profitability | Not claimed |

## Versioning

- Editorial clarification of unresolved items: stay on v0.1 and edit this file.
- Change of a **recorded** rule: bump to v0.2 and add an ADR.
