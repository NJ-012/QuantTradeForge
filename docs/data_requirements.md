# Data requirements

Phase 1.1: define **what** we need and **how** we will evaluate sources. This document does **not** select a vendor, download history, or assert current prices, API limits, or commercial terms that have not been verified.

Free historical data is **not** assumed sufficient for production-grade intraday backtests.

## Required data categories

### Historical market data

| Series | Initial need | Notes |
| ------ | ------------ | ----- |
| 5-minute OHLCV | Required for TSMOM v0.1 and initial strategies | Primary research bar |
| 15-minute OHLCV | Required | Second strategy timeframe |
| Daily OHLCV | Required | Session context, CA checks, universe filters |
| 1-minute OHLCV | Optional until justified | Execution/slippage research later |
| Tick / trade prints | Deferred | Later execution quality; not Phase 1.1 |

OHLCV means open, high, low, close, volume. Turnover/value is desirable when the source provides it. Open interest is not required for cash equity Phase 1.

### Reference data (security master)

- Exchange (NSE vs BSE as distinct venues)
- Exchange-specific symbol / token
- ISIN where available
- Instrument type (equity first)
- Currency (INR for initial scope)
- Trading status
- Listing and delisting dates where available (survivorship)
- Tick size and lot size where applicable (cash equity lot size is typically 1; still store if provided)
- Segment / series (e.g. EQ) where the venue uses it

### Corporate actions

Splits, bonuses, dividends, rights, mergers and other material adjustments. Research must know whether a price series is **raw**, **split-adjusted**, or **total-return / dividend-adjusted**. Mixing these without a dataset version is a defect.

### Market context (later ingestion; schema should allow)

- Market indices (e.g. Nifty, Sensex — **source TBD**)
- Sector indices
- India VIX where available and licensed
- Breadth / advances-declines where available

Do not invent index methodologies or claim a feed includes these until verified.

### Future live data (not Phase 1)

Timestamped trades or prices, best bid/ask, volume, trading status, market depth if licensed and justified.

## Answers to the ten Phase 1 questions

### 1. Required historical coverage

**Working requirement:** enough **calendar** history to support chronological train/validation/test for 5m/15m strategies, including multiple market regimes.

**Open (OPEN-001 / OPEN-003):** exact start date and universe size are not fixed. A later sample may be weeks-to-months for engineering; multi-year history is a research goal, not a Phase 1.1 download.

**Do not:** download multi-year intraday files in this phase.

### 2. Required bar frequencies

**Required now (as requirements):** daily, 15-minute, 5-minute.  
**Optional later:** 1-minute, ticks.

### 3. Instrument-universe requirements

**Working requirement:** cash equities listed on NSE and/or BSE, stored as **separate** instruments if listed on both.

**Open (OPEN-003):** Nifty 50 / 100 / 500 vs broader listed universe vs user list. Survivorship: prefer sources that include delisted names or document the bias if they do not.

### 4. Data licensing and permitted use

**Policy:** do not ingest or redistribute data whose licence forbids research storage, backtesting, or (later) commercial use. Vendor terms must be read before any bulk download. Sample fixtures in git must be either synthetic (labelled, not for performance claims) or explicitly licensed for repository inclusion.

**Open (OPEN-001):** which licence we will operate under.

### 5. Availability of historical intraday data

**Not verified.** Many retail APIs offer limited lookback; exchange historical products and licensed vendors differ. Phase 1.3 may begin only after a source is checked against this list **from primary documentation**, not from memory.

### 6. Data-provider and broker API limitations

**Not verified.** Rate limits, symbol mapping, adjustment flags, and session calendars are source-specific. Broker choice is **OPEN-002** and is not required to write schemas.

### 7. Estimated costs and storage

**Order-of-magnitude engineering estimate only** (not a quote):

- Rough uncompressed CSV scale: on the order of **tens of MB per liquid name per year** at 5-minute bars, highly dependent on fields and session length.
- A 50-name, 2-year, 5m+15m+daily set is likely **low hundreds of MB to a few GB**; ticks are orders of magnitude larger.

**Open:** actual vendor price and compressed on-disk size. No purchase without approval.

### 8. Timestamp and timezone conventions

**Session timezone:** `Asia/Kolkata`.

**Regular cash equity session (design assumption, confirm against exchange circulars when implementing):** typically 09:15–15:30 IST, with pre-open/auction phases **not** to be treated as 5-minute strategy bars unless explicitly modelled.

**Bar timestamp:** Internal convention is **period-start**, timezone-aware (ADR-013). Inspect the chosen source’s convention before writing ingestion and convert into this representation. Never store naive local clocks.

**Do not** assume NSE and BSE clocks or holiday calendars are identical without a calendar table.

### 9. Corporate-action adjustment policies

**Working policy:**

- Store a **dataset version** that states adjustment type.
- Prefer retaining **unadjusted** prices plus a CA event table so adjustments can be rebuilt.
- Split/bonus adjustments must not be applied as if they were dividends (and vice versa).
- Intraday bars on CA dates: keep **unadjusted** prints in this dataset version; do not invent overnight adjusted OHLC (ADR-015).

**Open:** vendor default adjustment; whether dividends adjust OHLC.

### 10. Missing, duplicate, stale, and out-of-order data

**Working quality rules (to be implemented as tests in Phase 1.2):**

| Issue | Intended handling |
| ----- | ----------------- |
| Duplicate timestamps | Reject or collapse only with an explicit rule; never silently average |
| Out-of-order bars | Sort then flag; do not drop without log |
| Missing bars | Record gap; do not forward-fill close into OHLC for signal generation |
| Stale bars | Max age relative to session clock (live later); historical: calendar vs expected session grid |
| OHLC inconsistency | high ≥ max(open,close,low), low ≤ min(open,close,high); volume ≥ 0 |
| Zero-volume bars | Keep if the venue published them; flag for liquidity filters |
| Trading halt | Status field if available; do not invent prints |
| Halt / auction / special session | Separate from regular continuous session bars |

## Feasible source evaluation (checklist, not a ranking)

Evaluate each candidate against **primary** docs/licence before any integration:

1. Permitted use (research, storage, redistribution, commercial).
2. Historical **intraday** depth (years vs days).
3. NSE and BSE coverage and identifier mapping (ISIN, tokens).
4. Adjustment flags and CA completeness.
5. Timezone and bar alignment.
6. Holiday/session calendar.
7. Delisted/suspended instruments (survivorship).
8. Rate limits and cost.
9. Whether data may be stored locally for reproducibility.
10. Paper/live feed compatibility (nice-to-have, not a Phase 1.1 blocker).

**Candidate classes to evaluate later (none selected):** exchange historical products; licensed market-data vendors; broker historical APIs; regulated data redistributors. **Do not** treat blog lists or unofficial scrapers as a source.

No candidate is marked “available” or “sufficient” in this document.

## Sample vs production data

| Kind | Allowed now | Use |
| ---- | ----------- | --- |
| Production vendor dumps | No | Requires approval and licence |
| Small licensed sample | Not yet | Phase 1.3 after OPEN-001 |
| Synthetic bars labelled `synthetic` | Yes (`tests/fixtures/synthetic/`) | Unit tests only; **not** performance evidence |

Do not put fake market data on any path described as production or live.

## Storage direction (not implemented)

- Research storage will be versioned datasets (files or a later database). PostgreSQL/TimescaleDB remains a **candidate**, not an install for 1.1.
- Live state remains in-memory in a future phase.

## Phase 1.1 acceptance for this file

- The ten questions have an explicit answer or an **Open** marker.
- No vendor capability is invented.
- No bulk download instructions that pull market history.
