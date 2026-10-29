"""Data-quality checks. Never silently average duplicates or forward-fill OHLC."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Sequence

from quanttradeforge.data.enums import IssueSeverity, Timeframe
from quanttradeforge.data.models import Bar, Instrument
from quanttradeforge.data.session import session_bar_opens

ERROR = IssueSeverity.ERROR
WARNING = IssueSeverity.WARNING


@dataclass(frozen=True)
class QualityIssue:
    code: str
    message: str
    severity: IssueSeverity
    instrument_id: str | None = None
    bar_open_ts: datetime | None = None


def _tick_aligned(price: Decimal, tick: Decimal) -> bool:
    try:
        quotient = (price / tick).normalize()
    except (InvalidOperation, ZeroDivisionError):
        return False
    return quotient == quotient.to_integral_value()


def validate_instrument(instrument: Instrument) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    iid = instrument.instrument_id
    if ":" not in instrument.instrument_id:
        issues.append(
            QualityIssue(
                "INSTRUMENT_ID_SHAPE",
                "instrument_id should be a namespaced id (e.g. QTF:NSE:EQ:SYMBOL)",
                WARNING,
                iid,
            )
        )
    if instrument.exchange.upper() != instrument.exchange:
        issues.append(
            QualityIssue("EXCHANGE_CASE", "exchange code should be uppercase", WARNING, iid)
        )
    if instrument.delisting_date and instrument.listing_date:
        if instrument.delisting_date < instrument.listing_date:
            issues.append(
                QualityIssue(
                    "LISTING_DATES",
                    "delisting_date is before listing_date",
                    ERROR,
                    iid,
                )
            )
    return issues


def validate_bar(bar: Bar, instrument: Instrument | None = None) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    iid = bar.instrument_id
    ts = bar.bar_open_ts
    if bar.volume < 0:
        issues.append(QualityIssue("NEGATIVE_VOLUME", "volume must be >= 0", ERROR, iid, ts))
    if bar.high < bar.low:
        issues.append(QualityIssue("HIGH_LT_LOW", "high is less than low", ERROR, iid, ts))
    if bar.high < max(bar.open, bar.close, bar.low):
        issues.append(
            QualityIssue(
                "OHLC_HIGH",
                "high must be >= max(open, close, low)",
                ERROR,
                iid,
                ts,
            )
        )
    if bar.low > min(bar.open, bar.close, bar.high):
        issues.append(
            QualityIssue(
                "OHLC_LOW",
                "low must be <= min(open, close, high)",
                ERROR,
                iid,
                ts,
            )
        )
    if bar.volume == 0:
        issues.append(
            QualityIssue(
                "ZERO_VOLUME",
                "zero-volume bar kept but flagged for liquidity filters",
                WARNING,
                iid,
                ts,
            )
        )
    if bar.turnover is not None and bar.turnover < 0:
        issues.append(QualityIssue("NEGATIVE_TURNOVER", "turnover must be >= 0", ERROR, iid, ts))
    if instrument is not None:
        if instrument.instrument_id != bar.instrument_id:
            issues.append(
                QualityIssue(
                    "INSTRUMENT_MISMATCH",
                    "bar instrument_id does not match provided instrument",
                    ERROR,
                    iid,
                    ts,
                )
            )
        if instrument.tick_size is not None:
            for field_name in ("open", "high", "low", "close"):
                price = getattr(bar, field_name)
                if not _tick_aligned(price, instrument.tick_size):
                    issues.append(
                        QualityIssue(
                            "TICK_SIZE",
                            f"{field_name} is not a multiple of tick_size",
                            WARNING,
                            iid,
                            ts,
                        )
                    )
    if bar.is_synthetic and bar.source != "synthetic":
        issues.append(
            QualityIssue(
                "SYNTHETIC_SOURCE",
                "synthetic bars must set source='synthetic'",
                WARNING,
                iid,
                ts,
            )
        )
    return issues


def validate_bar_series(
    bars: Sequence[Bar],
    *,
    instrument: Instrument | None = None,
    expected_timeframe: Timeframe | None = None,
    check_session_gaps: bool = True,
) -> list[QualityIssue]:
    """Validate a series. Does not drop, average, or forward-fill bars."""
    issues: list[QualityIssue] = []
    for bar in bars:
        if expected_timeframe is not None and bar.timeframe != expected_timeframe:
            issues.append(
                QualityIssue(
                    "TIMEFRAME_MIX",
                    f"expected {expected_timeframe.value}, found {bar.timeframe.value}",
                    ERROR,
                    bar.instrument_id,
                    bar.bar_open_ts,
                )
            )
        issues.extend(validate_bar(bar, instrument))

    if not bars:
        return issues

    ids = {bar.instrument_id for bar in bars}
    if len(ids) > 1:
        issues.append(
            QualityIssue(
                "MULTI_INSTRUMENT_SERIES",
                "series contains more than one instrument_id; validate each listing separately",
                ERROR,
            )
        )
        return issues

    timestamps = [bar.bar_open_ts for bar in bars]
    if timestamps != sorted(timestamps):
        issues.append(
            QualityIssue(
                "OUT_OF_ORDER",
                "bars are not in chronological order; sort explicitly — do not drop",
                ERROR,
                bars[0].instrument_id,
            )
        )

    seen: dict[datetime, int] = {}
    for bar in bars:
        seen[bar.bar_open_ts] = seen.get(bar.bar_open_ts, 0) + 1
    for ts, count in seen.items():
        if count > 1:
            issues.append(
                QualityIssue(
                    "DUPLICATE_TIMESTAMP",
                    "duplicate bar_open_ts; never silently average",
                    ERROR,
                    bars[0].instrument_id,
                    ts,
                )
            )

    if check_session_gaps and expected_timeframe in {
        Timeframe.M1,
        Timeframe.M5,
        Timeframe.M15,
        Timeframe.D1,
    }:
        present = {bar.bar_open_ts for bar in bars}
        session_dates = {bar.session_date for bar in bars}
        for session_date in sorted(session_dates):
            expected = session_bar_opens(session_date, expected_timeframe or bars[0].timeframe)
            missing = [ts for ts in expected if ts not in present]
            extra = [
                bar.bar_open_ts
                for bar in bars
                if bar.session_date == session_date and bar.bar_open_ts not in set(expected)
            ]
            for ts in missing:
                issues.append(
                    QualityIssue(
                        "MISSING_BAR",
                        "expected session bar is absent; do not forward-fill",
                        WARNING,
                        bars[0].instrument_id,
                        ts,
                    )
                )
            for ts in extra:
                issues.append(
                    QualityIssue(
                        "OUTSIDE_SESSION",
                        "bar_open_ts is outside the regular continuous session grid",
                        WARNING,
                        bars[0].instrument_id,
                        ts,
                    )
                )
    return issues


def sort_bars(bars: Sequence[Bar]) -> list[Bar]:
    """Return a new list sorted by (instrument_id, bar_open_ts). Does not drop duplicates."""
    return sorted(bars, key=lambda bar: (bar.instrument_id, bar.bar_open_ts))
