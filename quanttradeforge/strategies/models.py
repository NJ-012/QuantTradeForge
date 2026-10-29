"""Standardized strategy signal types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from quanttradeforge.data.models import Instrument


class SignalAction(str, Enum):
    HOLD = "HOLD"
    ENTER = "ENTER"
    EXIT = "EXIT"


class PositionIntent(str, Enum):
    FLAT = "FLAT"
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass(frozen=True)
class Signal:
    """A strategy decision; it is not an order and cannot submit one."""

    timestamp: datetime
    instrument: Instrument
    strategy_id: str
    strategy_version: str
    action: SignalAction
    position_intent: PositionIntent
    reason: str
    stop_distance: Decimal | None = None
    target_distance: Decimal | None = None

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("signal timestamp must be timezone-aware")
        if not self.strategy_id.strip():
            raise ValueError("strategy_id is required")
        if not self.strategy_version.strip():
            raise ValueError("strategy_version is required")
        if not self.reason.strip():
            raise ValueError("signal reason is required")
        if self.action == SignalAction.HOLD and self.position_intent != PositionIntent.FLAT:
            raise ValueError("HOLD signals must use FLAT position_intent")
        for field_name in ("stop_distance", "target_distance"):
            value = getattr(self, field_name)
            if value is not None and value <= 0:
                raise ValueError(f"{field_name} must be positive")
