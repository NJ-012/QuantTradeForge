"""Quality-check behaviour: flag, do not silently repair."""

from __future__ import annotations

import unittest
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from quanttradeforge.data.enums import InstrumentType, IssueSeverity, Timeframe, TradingStatus
from quanttradeforge.data.models import Bar, DatasetManifest, Instrument
from quanttradeforge.data.quality import sort_bars, validate_bar, validate_bar_series, validate_dataset
from quanttradeforge.data.session import session_bar_opens

IST = ZoneInfo("Asia/Kolkata")


def _instrument() -> Instrument:
    return Instrument(
        instrument_id="QTF:NSE:EQ:SYNTHA",
        exchange="NSE",
        venue_symbol="SYNTHA",
        instrument_type=InstrumentType.EQUITY,
        currency="INR",
        trading_status=TradingStatus.ACTIVE,
        tick_size=Decimal("0.05"),
        lot_size=1,
    )


def _bar(*, minute: int, **overrides: object) -> Bar:
    payload = {
        "instrument_id": "QTF:NSE:EQ:SYNTHA",
        "bar_open_ts": datetime(2024, 1, 15, 9, minute, tzinfo=IST),
        "timeframe": Timeframe.M5,
        "open": Decimal("100.00"),
        "high": Decimal("100.40"),
        "low": Decimal("99.90"),
        "close": Decimal("100.20"),
        "volume": Decimal("1000"),
        "session_date": date(2024, 1, 15),
        "dataset_version": "0.1.0",
        "is_synthetic": True,
        "source": "synthetic",
    }
    payload.update(overrides)
    return Bar(**payload)  # type: ignore[arg-type]


def _codes(issues) -> set[str]:
    return {issue.code for issue in issues}


class QualityTests(unittest.TestCase):
    def test_dataset_cross_file_identity(self) -> None:
        manifest = DatasetManifest(
            dataset_id="sample",
            dataset_version="v1",
            source="test",
            license="test",
            is_synthetic=True,
            not_for_performance=True,
            adjustment_policy="unadjusted",
            bar_time_convention="period_start",
            timezone="Asia/Kolkata",
        )
        issues = validate_dataset(
            manifest,
            [_instrument()],
            [_bar(minute=15, dataset_version="v1")],
        )
        self.assertNotIn("DATASET_VERSION_MISMATCH", _codes(issues))
        self.assertNotIn("UNKNOWN_INSTRUMENT", _codes(issues))

    def test_dataset_flags_unknown_instrument_and_version(self) -> None:
        manifest = DatasetManifest(
            dataset_id="sample",
            dataset_version="v1",
            source="test",
            license="test",
            is_synthetic=True,
            not_for_performance=True,
            adjustment_policy="unadjusted",
            bar_time_convention="period_start",
            timezone="Asia/Kolkata",
        )
        bar = _bar(minute=15, instrument_id="QTF:NSE:EQ:UNKNOWN", dataset_version="v2")
        codes = _codes(validate_dataset(manifest, [_instrument()], [bar]))
        self.assertIn("DATASET_VERSION_MISMATCH", codes)
        self.assertIn("UNKNOWN_INSTRUMENT", codes)

    def test_ohlc_inconsistency(self) -> None:
        bar = _bar(minute=15, high=Decimal("99.00"), low=Decimal("98.00"), open=Decimal("100.00"))
        codes = _codes(validate_bar(bar))
        self.assertIn("OHLC_HIGH", codes)

    def test_negative_volume(self) -> None:
        bar = _bar(minute=15, volume=Decimal("-1"))
        self.assertIn("NEGATIVE_VOLUME", _codes(validate_bar(bar)))

    def test_zero_volume_is_warning_not_drop(self) -> None:
        bar = _bar(minute=15, volume=Decimal("0"))
        issues = validate_bar(bar)
        zero = [i for i in issues if i.code == "ZERO_VOLUME"]
        self.assertEqual(len(zero), 1)
        self.assertEqual(zero[0].severity, IssueSeverity.WARNING)

    def test_duplicate_timestamps_are_errors(self) -> None:
        bars = [_bar(minute=15), _bar(minute=15, volume=Decimal("2"))]
        issues = validate_bar_series(bars, expected_timeframe=Timeframe.M5, check_session_gaps=False)
        self.assertIn("DUPLICATE_TIMESTAMP", _codes(issues))

    def test_out_of_order_flagged_sort_does_not_drop(self) -> None:
        bars = [_bar(minute=20), _bar(minute=15)]
        issues = validate_bar_series(bars, expected_timeframe=Timeframe.M5, check_session_gaps=False)
        self.assertIn("OUT_OF_ORDER", _codes(issues))
        ordered = sort_bars(bars)
        self.assertEqual(len(ordered), 2)
        self.assertEqual(ordered[0].bar_open_ts.minute, 15)

    def test_gap_is_warning_not_forward_fill(self) -> None:
        bars = [_bar(minute=15), _bar(minute=20), _bar(minute=30)]
        issues = validate_bar_series(bars, expected_timeframe=Timeframe.M5, check_session_gaps=True)
        missing = [i for i in issues if i.code == "MISSING_BAR"]
        self.assertTrue(any(i.bar_open_ts.minute == 25 for i in missing))
        self.assertEqual(len(bars), 3)

    def test_mixed_instruments_rejected_as_one_series(self) -> None:
        other = _bar(minute=15, instrument_id="QTF:BSE:EQ:SYNTHA")
        issues = validate_bar_series(
            [_bar(minute=15), other],
            expected_timeframe=Timeframe.M5,
            check_session_gaps=False,
        )
        self.assertIn("MULTI_INSTRUMENT_SERIES", _codes(issues))

    def test_session_grid_length_5m(self) -> None:
        opens = session_bar_opens(date(2024, 1, 15), Timeframe.M5)
        self.assertEqual(opens[0], datetime(2024, 1, 15, 9, 15, tzinfo=IST))
        self.assertEqual(opens[-1], datetime(2024, 1, 15, 15, 25, tzinfo=IST))
        self.assertEqual(len(opens), 75)

    def test_tick_size_warning(self) -> None:
        bar = _bar(minute=15, open=Decimal("100.01"))
        issues = validate_bar(bar, _instrument())
        self.assertIn("TICK_SIZE", _codes(issues))


if __name__ == "__main__":
    unittest.main()
