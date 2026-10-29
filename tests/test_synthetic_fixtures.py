"""Synthetic sample is labelled, loadable, and not treated as market performance data."""

from __future__ import annotations

import unittest

from quanttradeforge.data.enums import Timeframe
from quanttradeforge.data.fixtures import load_synthetic_dataset
from quanttradeforge.data.quality import validate_bar_series, validate_instrument


class SyntheticFixtureTests(unittest.TestCase):
    def test_manifest_forbids_performance_use(self) -> None:
        manifest, instruments, bars, actions = load_synthetic_dataset()
        self.assertTrue(manifest.is_synthetic)
        self.assertTrue(manifest.not_for_performance)
        self.assertEqual(manifest.source, "synthetic")
        self.assertEqual(manifest.timezone, "Asia/Kolkata")
        self.assertEqual(manifest.bar_time_convention.value, "period_start")
        self.assertEqual(len(instruments), 2)
        self.assertEqual(len(actions), 1)
        self.assertTrue(all(bar.is_synthetic for bar in bars))
        self.assertTrue(all(bar.source == "synthetic" for bar in bars))

    def test_cross_listing_not_merged(self) -> None:
        _, instruments, bars, _ = load_synthetic_dataset()
        ids = {inst.instrument_id for inst in instruments}
        self.assertEqual(ids, {"QTF:NSE:EQ:SYNTHA", "QTF:BSE:EQ:SYNTHA"})
        nse_px = next(b.close for b in bars if b.instrument_id.endswith(":NSE:EQ:SYNTHA") or b.instrument_id == "QTF:NSE:EQ:SYNTHA")
        bse_px = next(b.close for b in bars if b.instrument_id == "QTF:BSE:EQ:SYNTHA")
        self.assertNotEqual(nse_px, bse_px)

    def test_instruments_pass_validation(self) -> None:
        _, instruments, _, _ = load_synthetic_dataset()
        for inst in instruments:
            errors = [i for i in validate_instrument(inst) if i.severity.value == "error"]
            self.assertEqual(errors, [])

    def test_nse_partial_session_flags_gaps_not_errors_on_ohlc(self) -> None:
        _, _, bars, _ = load_synthetic_dataset()
        nse = [b for b in bars if b.instrument_id == "QTF:NSE:EQ:SYNTHA"]
        issues = validate_bar_series(nse, expected_timeframe=Timeframe.M5, check_session_gaps=True)
        ohlc_errors = [i for i in issues if i.code in {"OHLC_HIGH", "OHLC_LOW", "HIGH_LT_LOW", "NEGATIVE_VOLUME"}]
        self.assertEqual(ohlc_errors, [])
        self.assertTrue(any(i.code == "MISSING_BAR" for i in issues))
        self.assertTrue(any(i.code == "ZERO_VOLUME" for i in issues))
        gap_0930 = [
            i
            for i in issues
            if i.code == "MISSING_BAR"
            and i.bar_open_ts is not None
            and i.bar_open_ts.hour == 9
            and i.bar_open_ts.minute == 30
        ]
        self.assertEqual(len(gap_0930), 1)

    def test_corporate_action_not_applied_to_bars(self) -> None:
        _, _, bars, actions = load_synthetic_dataset()
        self.assertEqual(actions[0].action_type.value, "split")
        nse_dates = {b.session_date for b in bars if b.instrument_id == "QTF:NSE:EQ:SYNTHA"}
        self.assertNotIn(actions[0].ex_date, nse_dates)


if __name__ == "__main__":
    unittest.main()
