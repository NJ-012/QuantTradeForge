from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from quanttradeforge.data.enums import InstrumentType, TradingStatus
from quanttradeforge.data.models import Bar, Instrument
from quanttradeforge.strategies.models import PositionIntent, Signal, SignalAction
from quanttradeforge.strategies.tsmom import TSMOMConfig, TSMOMStrategy

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


def _bars(closes: list[str]) -> list[Bar]:
    start = datetime(2023, 10, 30, 9, 15, tzinfo=IST)
    return [
        Bar(
            instrument_id="QTF:NSE:EQ:ABC",
            bar_open_ts=start + timedelta(minutes=5 * index),
            timeframe="5m",
            open=close,
            high=close,
            low=close,
            close=close,
            volume="1000",
            session_date=date(2023, 10, 30),
            dataset_version="test-v1",
        )
        for index, close in enumerate(closes)
    ]


def _resolved_config() -> TSMOMConfig:
    return TSMOMConfig(
        momentum_formula="simple_close_to_close",
        volatility_ddof=1,
        short_entry_policy="disabled",
        reversal_exit_policy="exit_only",
        atr_method="wilder",
        gap_fill_policy="next_open",
        eod_square_off_policy="last_regular_bar",
        execution_policy="next_open_market",
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
        config = _resolved_config()
        config.require_resolved()
        self.assertEqual(config.stop_atr_multiple, "1.5")
        self.assertEqual(Decimal(config.target_r_multiple), Decimal("2"))


class TSMOMStrategyTests(unittest.TestCase):
    def test_long_entry_uses_completed_bars_and_explicit_metadata(self) -> None:
        strategy = TSMOMStrategy(_resolved_config(), _instrument())
        bars = _bars(["100"] * 20 + ["110"])
        signal = strategy.evaluate(bars)
        self.assertEqual(signal.action, SignalAction.ENTER)
        self.assertEqual(signal.position_intent, PositionIntent.LONG)
        self.assertEqual(signal.timestamp, bars[-1].bar_open_ts)
        self.assertEqual(signal.instrument.instrument_id, "QTF:NSE:EQ:ABC")

    def test_zero_volatility_is_hold(self) -> None:
        strategy = TSMOMStrategy(_resolved_config(), _instrument())
        signal = strategy.evaluate(_bars(["100"] * 21))
        self.assertEqual(signal.action, SignalAction.HOLD)
        self.assertEqual(signal.position_intent, PositionIntent.FLAT)

    def test_unresolved_config_cannot_construct_strategy(self) -> None:
        with self.assertRaisesRegex(ValueError, "unresolved decisions"):
            TSMOMStrategy(TSMOMConfig(), _instrument())

    def test_non_chronological_bars_are_rejected(self) -> None:
        strategy = TSMOMStrategy(_resolved_config(), _instrument())
        bars = _bars(["100"] * 20 + ["110"])
        with self.assertRaisesRegex(ValueError, "chronological"):
            strategy.evaluate([bars[1], bars[0], *bars[2:]])


if __name__ == "__main__":
    unittest.main()
