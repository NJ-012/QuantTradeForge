"""Regular-session grid assumptions for quality checks.

These hours are a **design assumption** for cash-equity continuous session
(09:15–15:30 Asia/Kolkata). Confirm against exchange circulars before live use.
Pre-open and closing auction are not modelled as strategy bars.
NSE and BSE holiday calendars are not implemented; gap checks run only on
session dates already present in the series.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from quanttradeforge.data.enums import Timeframe

IST = ZoneInfo("Asia/Kolkata")
REGULAR_OPEN = time(9, 15)
REGULAR_CLOSE = time(15, 30)

_TIMEFRAME_MINUTES = {
    Timeframe.M1: 1,
    Timeframe.M5: 5,
    Timeframe.M15: 15,
}


def session_bar_opens(session_date: date, timeframe: Timeframe) -> list[datetime]:
    """Period-start timestamps for the continuous session, excluding the close instant."""
    if timeframe == Timeframe.D1:
        return [datetime.combine(session_date, REGULAR_OPEN, tzinfo=IST)]
    minutes = _TIMEFRAME_MINUTES.get(timeframe)
    if minutes is None:
        raise ValueError(f"unsupported timeframe for session grid: {timeframe}")
    start = datetime.combine(session_date, REGULAR_OPEN, tzinfo=IST)
    end = datetime.combine(session_date, REGULAR_CLOSE, tzinfo=IST)
    step = timedelta(minutes=minutes)
    opens: list[datetime] = []
    cursor = start
    while cursor + step <= end:
        opens.append(cursor)
        cursor += step
    return opens
