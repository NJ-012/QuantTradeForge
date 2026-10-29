"""Normalized instrument, bar, corporate-action, and dataset records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from quanttradeforge.data.enums import (
    AdjustmentPolicy,
    BarTimeConvention,
    CorporateActionType,
    InstrumentType,
    Timeframe,
    TradingStatus,
)


def _decimal(value: Decimal | int | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def require_aware(ts: datetime, field: str) -> None:
    if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
        raise ValueError(f"{field} must be timezone-aware; naive datetimes are forbidden")


@dataclass(frozen=True)
class Instrument:
    """One tradable listing. NSE and BSE rows with the same ticker stay distinct."""

    instrument_id: str
    exchange: str
    venue_symbol: str
    instrument_type: InstrumentType
    currency: str
    trading_status: TradingStatus
    isin: str | None = None
    tick_size: Decimal | None = None
    lot_size: int | None = None
    segment: str | None = None
    listing_date: date | None = None
    delisting_date: date | None = None
    venue_token: str | None = None

    def __post_init__(self) -> None:
        if not self.instrument_id.strip():
            raise ValueError("instrument_id is required")
        if not self.exchange.strip():
            raise ValueError("exchange is required")
        if not self.venue_symbol.strip():
            raise ValueError("venue_symbol is required")
        if self.tick_size is not None:
            object.__setattr__(self, "tick_size", _decimal(self.tick_size))
            if self.tick_size <= 0:
                raise ValueError("tick_size must be positive")
        if self.lot_size is not None and self.lot_size <= 0:
            raise ValueError("lot_size must be positive")
        if not isinstance(self.instrument_type, InstrumentType):
            object.__setattr__(self, "instrument_type", InstrumentType(self.instrument_type))
        if not isinstance(self.trading_status, TradingStatus):
            object.__setattr__(self, "trading_status", TradingStatus(self.trading_status))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Instrument:
        listing = payload.get("listing_date")
        delisting = payload.get("delisting_date")
        return cls(
            instrument_id=payload["instrument_id"],
            exchange=payload["exchange"],
            venue_symbol=payload["venue_symbol"],
            instrument_type=InstrumentType(payload["instrument_type"]),
            currency=payload["currency"],
            trading_status=TradingStatus(payload["trading_status"]),
            isin=payload.get("isin"),
            tick_size=None if payload.get("tick_size") is None else _decimal(payload["tick_size"]),
            lot_size=payload.get("lot_size"),
            segment=payload.get("segment"),
            listing_date=date.fromisoformat(listing) if listing else None,
            delisting_date=date.fromisoformat(delisting) if delisting else None,
            venue_token=payload.get("venue_token"),
        )


@dataclass(frozen=True)
class Bar:
    """OHLCV interval. `bar_open_ts` is the period start (ADR-013)."""

    instrument_id: str
    bar_open_ts: datetime
    timeframe: Timeframe
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    session_date: date
    dataset_version: str
    turnover: Decimal | None = None
    is_synthetic: bool = False
    source: str | None = None

    def __post_init__(self) -> None:
        require_aware(self.bar_open_ts, "bar_open_ts")
        if not isinstance(self.timeframe, Timeframe):
            object.__setattr__(self, "timeframe", Timeframe(self.timeframe))
        for name in ("open", "high", "low", "close", "volume"):
            object.__setattr__(self, name, _decimal(getattr(self, name)))
        if self.turnover is not None:
            object.__setattr__(self, "turnover", _decimal(self.turnover))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Bar:
        return cls(
            instrument_id=payload["instrument_id"],
            bar_open_ts=datetime.fromisoformat(payload["bar_open_ts"]),
            timeframe=Timeframe(payload["timeframe"]),
            open=_decimal(payload["open"]),
            high=_decimal(payload["high"]),
            low=_decimal(payload["low"]),
            close=_decimal(payload["close"]),
            volume=_decimal(payload["volume"]),
            session_date=date.fromisoformat(payload["session_date"]),
            dataset_version=payload["dataset_version"],
            turnover=None if payload.get("turnover") is None else _decimal(payload["turnover"]),
            is_synthetic=bool(payload.get("is_synthetic", False)),
            source=payload.get("source"),
        )


@dataclass(frozen=True)
class CorporateAction:
    """Event table row. Does not apply price adjustments (not implemented in Phase 1.2)."""

    instrument_id: str
    ex_date: date
    action_type: CorporateActionType
    numerator: Decimal | None = None
    denominator: Decimal | None = None
    cash_amount: Decimal | None = None
    currency: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.action_type, CorporateActionType):
            object.__setattr__(self, "action_type", CorporateActionType(self.action_type))
        for name in ("numerator", "denominator", "cash_amount"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, _decimal(value))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> CorporateAction:
        return cls(
            instrument_id=payload["instrument_id"],
            ex_date=date.fromisoformat(payload["ex_date"]),
            action_type=CorporateActionType(payload["action_type"]),
            numerator=None if payload.get("numerator") is None else _decimal(payload["numerator"]),
            denominator=None if payload.get("denominator") is None else _decimal(payload["denominator"]),
            cash_amount=None if payload.get("cash_amount") is None else _decimal(payload["cash_amount"]),
            currency=payload.get("currency"),
            notes=payload.get("notes"),
        )


@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    dataset_version: str
    source: str
    license: str
    is_synthetic: bool
    not_for_performance: bool
    adjustment_policy: AdjustmentPolicy
    bar_time_convention: BarTimeConvention
    timezone: str

    def __post_init__(self) -> None:
        if not isinstance(self.adjustment_policy, AdjustmentPolicy):
            object.__setattr__(self, "adjustment_policy", AdjustmentPolicy(self.adjustment_policy))
        if not isinstance(self.bar_time_convention, BarTimeConvention):
            object.__setattr__(self, "bar_time_convention", BarTimeConvention(self.bar_time_convention))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> DatasetManifest:
        return cls(
            dataset_id=payload["dataset_id"],
            dataset_version=payload["dataset_version"],
            source=payload["source"],
            license=payload["license"],
            is_synthetic=bool(payload["is_synthetic"]),
            not_for_performance=bool(payload["not_for_performance"]),
            adjustment_policy=AdjustmentPolicy(payload["adjustment_policy"]),
            bar_time_convention=BarTimeConvention(payload["bar_time_convention"]),
            timezone=payload["timezone"],
        )
