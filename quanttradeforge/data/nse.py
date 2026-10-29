"""NSE daily bhavcopy download and normalization.

This adapter is intentionally small: it supports the official zipped daily
equity bhavcopy format for a reproducible engineering sample. It is not an
intraday feed and does not apply corporate-action adjustments.
"""

from __future__ import annotations

import csv
import io
import json
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from quanttradeforge.data.enums import (
    AdjustmentPolicy,
    BarTimeConvention,
    InstrumentType,
    Timeframe,
    TradingStatus,
)
from quanttradeforge.data.models import Bar, DatasetManifest, Instrument

IST = ZoneInfo("Asia/Kolkata")
NSE_BHAVCOPY_SOURCE = "NSE official equity bhavcopy archive"


@dataclass(frozen=True)
class NSEBhavcopyDataset:
    manifest: DatasetManifest
    instruments: list[Instrument]
    bars: list[Bar]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def bhavcopy_url(session_date: date) -> str:
    """Return the official archive URL for one trading date."""
    month = session_date.strftime("%b").upper()
    filename = f"cm{session_date:%d}{month}{session_date:%Y}bhav.csv.zip"
    return (
        "https://archives.nseindia.com/content/historical/EQUITIES/"
        f"{session_date:%Y}/{month}/{filename}"
    )


def _read_csv_from_zip(payload: bytes) -> list[dict[str, str]]:
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(csv_names) != 1:
                raise ValueError("NSE archive must contain exactly one CSV file")
            with archive.open(csv_names[0]) as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
                return list(csv.DictReader(text))
    except zipfile.BadZipFile as exc:
        raise ValueError("NSE response is not a valid ZIP archive") from exc


def _decimal_field(row: dict[str, str], field: str, row_number: int) -> Decimal:
    value = (row.get(field) or "").strip()
    if not value:
        raise ValueError(f"NSE EQ row {row_number} has an empty {field} field")
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(
            f"NSE EQ row {row_number} has invalid {field}: {value!r}"
        ) from exc
    if not parsed.is_finite():
        raise ValueError(f"NSE EQ row {row_number} has non-finite {field}: {value!r}")
    return parsed


def parse_bhavcopy(
    payload: bytes,
    *,
    session_date: date,
    dataset_version: str,
    source_url: str,
) -> NSEBhavcopyDataset:
    """Normalize one official NSE daily equity archive."""
    rows = _read_csv_from_zip(payload)
    if not rows:
        raise ValueError("NSE bhavcopy contains no rows")
    required = {"SYMBOL", "SERIES", "OPEN", "HIGH", "LOW", "CLOSE", "TOTTRDQTY"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"NSE bhavcopy is missing columns: {sorted(missing)}")

    instruments: list[Instrument] = []
    bars: list[Bar] = []
    bar_ts = datetime.combine(session_date, datetime.min.time(), tzinfo=IST).replace(
        hour=9, minute=15
    )
    seen_symbols: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        if (row.get("SERIES") or "").strip().upper() != "EQ":
            continue
        symbol = (row.get("SYMBOL") or "").strip()
        if not symbol:
            raise ValueError(f"NSE EQ row {row_number} has an empty SYMBOL field")
        if symbol in seen_symbols:
            raise ValueError(f"NSE bhavcopy contains duplicate EQ symbol: {symbol}")
        seen_symbols.add(symbol)
        instrument_id = f"QTF:NSE:EQ:{symbol}"
        instruments.append(
            Instrument(
                instrument_id=instrument_id,
                exchange="NSE",
                venue_symbol=symbol,
                instrument_type=InstrumentType.EQUITY,
                currency="INR",
                trading_status=TradingStatus.ACTIVE,
                isin=row.get("ISIN") or None,
                segment="EQ",
            )
        )
        bars.append(
            Bar(
                instrument_id=instrument_id,
                bar_open_ts=bar_ts,
                timeframe=Timeframe.D1,
                open=_decimal_field(row, "OPEN", row_number),
                high=_decimal_field(row, "HIGH", row_number),
                low=_decimal_field(row, "LOW", row_number),
                close=_decimal_field(row, "CLOSE", row_number),
                volume=_decimal_field(row, "TOTTRDQTY", row_number),
                session_date=session_date,
                dataset_version=dataset_version,
                turnover=(
                    _decimal_field(row, "TOTTRDVAL", row_number)
                    if (row.get("TOTTRDVAL") or "").strip()
                    else None
                ),
                source=NSE_BHAVCOPY_SOURCE,
            )
        )

    if not bars:
        raise ValueError("NSE bhavcopy contains no EQ-series rows")
    manifest = DatasetManifest(
        dataset_id=f"nse-bhavcopy-{session_date:%Y-%m-%d}",
        dataset_version=dataset_version,
        source=f"{NSE_BHAVCOPY_SOURCE}: {source_url}",
        license="NSE archive terms apply; verify permitted storage and redistribution before reuse",
        is_synthetic=False,
        not_for_performance=True,
        adjustment_policy=AdjustmentPolicy.UNADJUSTED,
        bar_time_convention=BarTimeConvention.PERIOD_START,
        timezone="Asia/Kolkata",
    )
    return NSEBhavcopyDataset(manifest, instruments, bars)


def download_bhavcopy(
    session_date: date,
    *,
    dataset_version: str | None = None,
    timeout_seconds: int = 30,
) -> NSEBhavcopyDataset:
    """Download and normalize one bounded NSE sample."""
    url = bhavcopy_url(session_date)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "QuantTradeForge research data adapter"},
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read()
    version = dataset_version or f"nse-bhavcopy-{session_date:%Y-%m-%d}-v1"
    return parse_bhavcopy(
        payload,
        session_date=session_date,
        dataset_version=version,
        source_url=url,
    )


def write_dataset(dataset: NSEBhavcopyDataset, output_dir: Path) -> None:
    """Write normalized JSON artefacts without overwriting an existing sample."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "dataset.json"
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite existing dataset: {output_dir}")
    manifest_path.write_text(json.dumps(dataset.manifest.__dict__, default=str, indent=2) + "\n")
    (output_dir / "instruments.json").write_text(
        json.dumps([instrument.__dict__ for instrument in dataset.instruments], default=str, indent=2)
        + "\n"
    )
    (output_dir / "bars_1d.json").write_text(
        json.dumps([bar.__dict__ for bar in dataset.bars], default=str, indent=2) + "\n"
    )


def load_dataset(output_dir: Path) -> NSEBhavcopyDataset:
    """Load a dataset written by :func:`write_dataset`."""
    manifest_path = output_dir / "dataset.json"
    instruments_path = output_dir / "instruments.json"
    bars_path = output_dir / "bars_1d.json"
    missing = [
        str(path.name)
        for path in (manifest_path, instruments_path, bars_path)
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(
            f"dataset directory is missing required files: {', '.join(missing)}"
        )
    return NSEBhavcopyDataset(
        manifest=DatasetManifest.from_dict(_read_json(manifest_path)),
        instruments=[Instrument.from_dict(item) for item in _read_json(instruments_path)],
        bars=[Bar.from_dict(item) for item in _read_json(bars_path)],
    )
