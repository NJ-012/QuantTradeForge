"""Instrument and bar contract tests."""

from __future__ import annotations

import unittest
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from quanttradeforge.data.enums import InstrumentType, Timeframe, TradingStatus
from quanttradeforge.data.models import Bar, Instrument

IST = ZoneInfo("Asia/Kolkata")


def _bar(**overrides: object) -> Bar:
    payload = {
        "instrument_id": "QTF:NSE:EQ:SYNTHA",
        "bar_open_ts": datetime(2024, 1, 15, 9, 15, tzinfo=IST),
        "timeframe": Timeframe.M5,
        "open": Decimal("100"),
        "high": Decimal("101"),
        "low": Decimal("99"),
        "close": Decimal("100.5"),
        "volume": Decimal("10"),
        "session_date": date(2024, 1, 15),
        "dataset_version": "0.1.0",
    }
    payload.update(overrides)
    return Bar(**payload)  # type: ignore[arg-type]


class InstrumentTests(unittest.TestCase):
    def test_nse_and_bse_same_ticker_are_distinct(self) -> None:
        nse = Instrument(
            instrument_id="QTF:NSE:EQ:SYNTHA",
            exchange="NSE",
            venue_symbol="SYNTHA",
            instrument_type=InstrumentType.EQUITY,
            currency="INR",
            trading_status=TradingStatus.ACTIVE,
        )
        bse = Instrument(
            instrument_id="QTF:BSE:EQ:SYNTHA",
            exchange="BSE",
            venue_symbol="SYNTHA",
            instrument_type=InstrumentType.EQUITY,
            currency="INR",
            trading_status=TradingStatus.ACTIVE,
        )
        self.assertNotEqual(nse.instrument_id, bse.instrument_id)
        self.assertEqual(nse.venue_symbol, bse.venue_symbol)

    def test_rejects_blank_exchange(self) -> None:
        with self.assertRaises(ValueError):
            Instrument(
                instrument_id="QTF:NSE:EQ:X",
                exchange="  ",
                venue_symbol="X",
                instrument_type=InstrumentType.EQUITY,
                currency="INR",
                trading_status=TradingStatus.ACTIVE,
            )


class BarTests(unittest.TestCase):
    def test_rejects_naive_timestamp(self) -> None:
        with self.assertRaises(ValueError):
            _bar(bar_open_ts=datetime(2024, 1, 15, 9, 15))

    def test_stores_decimals(self) -> None:
        bar = _bar(open="100.05")
        self.assertEqual(bar.open, Decimal("100.05"))
        self.assertEqual(bar.bar_open_ts.tzinfo, IST)


if __name__ == "__main__":
    unittest.main()
