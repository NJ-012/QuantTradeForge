"""Configuration boundary for the TSMOM v0.1 research specification."""

from __future__ import annotations

from dataclasses import dataclass

from quanttradeforge.data.enums import Timeframe


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
