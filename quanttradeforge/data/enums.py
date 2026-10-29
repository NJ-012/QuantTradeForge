"""Enumerations for market-data contracts. Exchange codes are free strings so new venues can be added without rewriting strategies."""

from enum import Enum


class InstrumentType(str, Enum):
    EQUITY = "EQUITY"
    INDEX = "INDEX"


class TradingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELISTED = "DELISTED"
    UNKNOWN = "UNKNOWN"


class Timeframe(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    D1 = "1d"


class AdjustmentPolicy(str, Enum):
    UNADJUSTED = "unadjusted"
    SPLIT_BONUS = "split_bonus"
    TOTAL_RETURN = "total_return"


class BarTimeConvention(str, Enum):
    """Internal bars are labelled at the start of the interval (ADR-013)."""

    PERIOD_START = "period_start"
    PERIOD_END = "period_end"


class CorporateActionType(str, Enum):
    SPLIT = "split"
    BONUS = "bonus"
    DIVIDEND = "dividend"
    RIGHTS = "rights"
    MERGER = "merger"
    OTHER = "other"


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
