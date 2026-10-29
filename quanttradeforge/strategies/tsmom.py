"""Configuration boundary for the TSMOM v0.1 research specification."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence
from decimal import Decimal
from statistics import mean
from typing import Final

from quanttradeforge.data.enums import Timeframe
from quanttradeforge.data.models import Bar, Instrument
from quanttradeforge.strategies.base import Strategy
from quanttradeforge.strategies.models import PositionIntent, Signal, SignalAction

_SIMPLE_CLOSE_TO_CLOSE: Final[str] = "simple_close_to_close"


@dataclass(frozen=True)
class TSMOMConfig:
    """Recorded TSMOM defaults plus explicit unresolved decisions.

    This class does not implement signal generation. ``require_resolved`` is
    intentionally strict so a future implementation cannot silently choose
    unresolved rules.
    """

    strategy_id: str = "TSMOM"
    version: str = "0.1"
    timeframe: Timeframe = Timeframe.M5
    momentum_lookback: int = 10
    volatility_observations: int = 20
    momentum_threshold_stddev: str = "1"
    atr_period: int = 14
    stop_atr_multiple: str = "1.5"
    target_r_multiple: str = "2"
    momentum_formula: str | None = None
    volatility_ddof: int | None = None
    short_entry_policy: str | None = None
    reversal_exit_policy: str | None = None
    atr_method: str | None = None
    gap_fill_policy: str | None = None
    eod_square_off_policy: str | None = None
    execution_policy: str | None = None

    def __post_init__(self) -> None:
        if self.timeframe != Timeframe.M5:
            raise ValueError("TSMOM v0.1 requires 5-minute bars")
        for field_name in (
            "momentum_lookback",
            "volatility_observations",
            "atr_period",
        ):
            if getattr(self, field_name) <= 0:
                raise ValueError(f"{field_name} must be positive")
        if self.volatility_ddof is not None and self.volatility_ddof not in (0, 1):
            raise ValueError("volatility_ddof must be 0 or 1")

    def unresolved_fields(self) -> tuple[str, ...]:
        fields = (
            "momentum_formula",
            "volatility_ddof",
            "short_entry_policy",
            "reversal_exit_policy",
            "atr_method",
            "gap_fill_policy",
            "eod_square_off_policy",
            "execution_policy",
        )
        return tuple(field for field in fields if getattr(self, field) is None)

    def require_resolved(self) -> None:
        unresolved = self.unresolved_fields()
        if unresolved:
            raise ValueError(
                "TSMOM v0.1 has unresolved decisions: " + ", ".join(unresolved)
            )


class TSMOMStrategy(Strategy):
    """Initial TSMOM signal evaluator using completed bars only.

    This increment implements the entry threshold and initial ATR-derived
    risk distances. Reversal exits and execution are intentionally deferred.
    """

    def __init__(self, config: TSMOMConfig, instrument: Instrument) -> None:
        config.require_resolved()
        if config.momentum_formula != _SIMPLE_CLOSE_TO_CLOSE:
            raise ValueError(
                "TSMOMStrategy currently supports only simple_close_to_close"
            )
        if config.atr_method != "wilder":
            raise ValueError("TSMOMStrategy currently supports only Wilder ATR")
        self.config = config
        self.instrument = instrument
        self.strategy_id = config.strategy_id
        self.version = config.version

    def evaluate(self, bars: Sequence[Bar]) -> Signal:
        if not bars:
            raise ValueError("TSMOMStrategy requires at least one completed bar")
        self._validate_bars(bars)
        latest = bars[-1]
        minimum_bars = max(
            self.config.momentum_lookback + 1,
            self.config.volatility_observations + 1,
            self.config.atr_period + 1,
        )
        if len(bars) < minimum_bars:
            return self._hold(latest, "insufficient completed bars")

        momentum = (
            latest.close / bars[-1 - self.config.momentum_lookback].close
        ) - Decimal("1")
        returns = [
            (bars[index].close / bars[index - 1].close) - Decimal("1")
            for index in range(1, len(bars))
        ][-self.config.volatility_observations :]
        volatility = self._stddev(returns, self.config.volatility_ddof or 1)
        threshold = Decimal(self.config.momentum_threshold_stddev) * volatility
        atr = self._wilder_atr(bars)

        if volatility == 0:
            return self._hold(latest, "zero trailing return volatility")
        if atr <= 0:
            return self._hold(latest, "zero trailing true range")
        if momentum > threshold:
            return self._signal(
                latest,
                PositionIntent.LONG,
                f"momentum {momentum} exceeded +{threshold} threshold",
                stop_distance=atr * Decimal(self.config.stop_atr_multiple),
                target_distance=atr
                * Decimal(self.config.stop_atr_multiple)
                * Decimal(self.config.target_r_multiple),
            )
        if momentum < -threshold and self.config.short_entry_policy == "enabled":
            return self._signal(
                latest,
                PositionIntent.SHORT,
                f"momentum {momentum} exceeded -{threshold} threshold",
                stop_distance=atr * Decimal(self.config.stop_atr_multiple),
                target_distance=atr
                * Decimal(self.config.stop_atr_multiple)
                * Decimal(self.config.target_r_multiple),
            )
        return self._hold(latest, "momentum remained inside threshold")

    @staticmethod
    def _stddev(values: Sequence[Decimal], ddof: int) -> Decimal:
        if len(values) <= ddof:
            return Decimal("0")
        average = Decimal(str(mean(values)))
        variance = sum((value - average) ** 2 for value in values) / Decimal(len(values) - ddof)
        return variance.sqrt()

    def _wilder_atr(self, bars: Sequence[Bar]) -> Decimal:
        true_ranges = [
            max(
                bar.high - bar.low,
                abs(bar.high - bars[index - 1].close),
                abs(bar.low - bars[index - 1].close),
            )
            for index, bar in enumerate(bars[1:], start=1)
        ]
        period = self.config.atr_period
        atr = sum(true_ranges[:period], Decimal("0")) / Decimal(period)
        for true_range in true_ranges[period:]:
            atr = ((atr * Decimal(period - 1)) + true_range) / Decimal(period)
        return atr

    def _validate_bars(self, bars: Sequence[Bar]) -> None:
        if any(bar.timeframe != self.config.timeframe for bar in bars):
            raise ValueError("TSMOMStrategy received a bar with the wrong timeframe")
        instrument_ids = {bar.instrument_id for bar in bars}
        if len(instrument_ids) != 1:
            raise ValueError("TSMOMStrategy requires one instrument series")
        if self.instrument.instrument_id not in instrument_ids:
            raise ValueError("TSMOMStrategy instrument does not match bar series")
        timestamps = [bar.bar_open_ts for bar in bars]
        if timestamps != sorted(timestamps):
            raise ValueError("TSMOMStrategy requires chronological bars")
        if any(bar.close <= 0 for bar in bars):
            raise ValueError("TSMOMStrategy requires positive close prices")
        if any(bar.high < bar.low for bar in bars):
            raise ValueError("TSMOMStrategy requires high >= low")

    def _hold(self, bar: Bar, reason: str) -> Signal:
        return self._signal(bar, PositionIntent.FLAT, reason, action=SignalAction.HOLD)

    def _signal(
        self,
        bar: Bar,
        position_intent: PositionIntent,
        reason: str,
        *,
        action: SignalAction = SignalAction.ENTER,
        stop_distance: Decimal | None = None,
        target_distance: Decimal | None = None,
    ) -> Signal:
        return Signal(
            timestamp=bar.bar_open_ts,
            instrument=self.instrument,
            strategy_id=self.strategy_id,
            strategy_version=self.version,
            action=action,
            position_intent=position_intent,
            reason=reason,
            stop_distance=stop_distance,
            target_distance=target_distance,
        )
