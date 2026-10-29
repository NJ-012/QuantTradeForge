from __future__ import annotations

import csv
import io
import tempfile
import unittest
import zipfile
from datetime import date
from decimal import Decimal
from pathlib import Path

from quanttradeforge.data.enums import Timeframe
from quanttradeforge.data.nse import bhavcopy_url, load_dataset, parse_bhavcopy, write_dataset


def _archive() -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        text = io.StringIO()
        writer = csv.DictWriter(
            text,
            fieldnames=[
                "SYMBOL", "SERIES", "OPEN", "HIGH", "LOW", "CLOSE",
                "TOTTRDQTY", "TOTTRDVAL", "ISIN",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "SYMBOL": "ABC", "SERIES": "EQ", "OPEN": "100.00",
            "HIGH": "105.00", "LOW": "99.00", "CLOSE": "102.00",
            "TOTTRDQTY": "1000", "TOTTRDVAL": "102000", "ISIN": "IN0000000001",
        })
        writer.writerow({
            "SYMBOL": "IGNORED", "SERIES": "BE", "OPEN": "1",
            "HIGH": "1", "LOW": "1", "CLOSE": "1", "TOTTRDQTY": "1",
            "TOTTRDVAL": "1", "ISIN": "",
        })
        archive.writestr("cm30OCT2023bhav.csv", text.getvalue())
    return output.getvalue()


class NSEIngestionTests(unittest.TestCase):
    def test_url_uses_official_archive_shape(self) -> None:
        self.assertEqual(
            bhavcopy_url(date(2023, 10, 30)),
            "https://archives.nseindia.com/content/historical/EQUITIES/2023/OCT/cm30OCT2023bhav.csv.zip",
        )

    def test_parse_normalizes_eq_daily_bar(self) -> None:
        dataset = parse_bhavcopy(
            _archive(),
            session_date=date(2023, 10, 30),
            dataset_version="sample-v1",
            source_url="https://example.invalid/sample.zip",
        )
        self.assertEqual(len(dataset.bars), 1)
        self.assertEqual(dataset.bars[0].timeframe, Timeframe.D1)
        self.assertEqual(dataset.bars[0].open, Decimal("100.00"))
        self.assertEqual(dataset.bars[0].bar_open_ts.hour, 9)
        self.assertFalse(dataset.manifest.is_synthetic)
        self.assertTrue(dataset.manifest.not_for_performance)

    def test_persisted_dataset_round_trips(self) -> None:
        dataset = parse_bhavcopy(
            _archive(),
            session_date=date(2023, 10, 30),
            dataset_version="sample-v1",
            source_url="https://example.invalid/sample.zip",
        )
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            write_dataset(dataset, output_dir)
            loaded = load_dataset(output_dir)
        self.assertEqual(loaded.manifest.dataset_id, dataset.manifest.dataset_id)
        self.assertEqual(loaded.instruments, dataset.instruments)
        self.assertEqual(loaded.bars, dataset.bars)


if __name__ == "__main__":
    unittest.main()
