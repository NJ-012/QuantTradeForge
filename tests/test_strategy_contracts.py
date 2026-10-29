from __future__ import annotations

import unittest
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from quanttradeforge.data.enums import InstrumentType, TradingStatus
from quanttradeforge.data.models import Instrument
from quanttradeforge.strategies.models import PositionIntent, Signal, SignalAction
from quanttradeforge.strategies.tsmom import TSMOMConfig

IST = ZoneInfo("Asia/Kolkata")


def _instrument() -> Instrument:
    return Instrument(
        instrument_id="QTF:NSE:EQ:ABC",
        exchange="NSE",
        venue_symbol="ABC",
        instrument_type=InstrumentType.EQUITY,
        currency="INR",
        trading_status=TradingStatus.ACTIVE,
    )


class SignalTests(unittest.TestCase):
    def test_hold_signal_is_explicitly_flat(self) -> None:
        signal = Signal(
            timestamp=datetime(2023, 10, 30, 9, 15, tzinfo=IST),
            instrument=_instrument(),
            strategy_id="TEST",
            strategy_version="0.1",
            action=SignalAction.HOLD,
            position_intent=PositionIntent.FLAT,
            reason="insufficient history",
        )
        self.assertEqual(signal.action, SignalAction.HOLD)

    def test_hold_cannot_have_position_intent(self) -> None:
        with self.assertRaises(ValueError):
            Signal(
                timestamp=datetime(2023, 10, 30, 9, 15, tzinfo=IST),
                instrument=_instrument(),
                strategy_id="TEST",
                strategy_version="0.1",
                action=SignalAction.HOLD,
                position_intent=PositionIntent.LONG,
                reason="invalid",
            )


class TSMOMConfigTests(unittest.TestCase):
    def test_recorded_defaults_and_unresolved_boundary(self) -> None:
        config = TSMOMConfig()
        self.assertEqual(config.momentum_lookback, 10)
        self.assertEqual(config.atr_period, 14)
        self.assertIn("momentum_formula", config.unresolved_fields())
        with self.assertRaisesRegex(ValueError, "unresolved decisions"):
            config.require_resolved()

    def test_resolved_configuration_can_be_checked(self) -> None:
        config = TSMOMConfig(
            momentum_formula="simple_close_to_close",
            volatility_ddof=1,
            short_entry_policy="disabled",
            reversal_exit_policy="exit_only",
            atr_method="wilder",
            gap_fill_policy="next_open",
            eod_square_off_policy="last_regular_bar",
            execution_policy="next_open_market",
        )
        config.require_resolved()
        self.assertEqual(config.stop_atr_multiple, "1.5")
        self.assertEqual(Decimal(config.target_r_multiple), Decimal("2"))


if __name__ == "__main__":
    unittest.main()
