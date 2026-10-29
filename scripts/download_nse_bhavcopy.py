"""Download one small NSE daily bhavcopy sample for local research."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from quanttradeforge.data.nse import download_bhavcopy, write_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, type=date.fromisoformat)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    dataset = download_bhavcopy(args.date)
    write_dataset(dataset, args.output)
    print(f"wrote {len(dataset.bars)} bars for {len(dataset.instruments)} instruments to {args.output}")


if __name__ == "__main__":
    main()
