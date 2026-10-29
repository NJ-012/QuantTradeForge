"""Load labelled synthetic fixtures. These are not market data and not performance evidence."""

from __future__ import annotations

import json
from pathlib import Path

from quanttradeforge.data.models import Bar, CorporateAction, DatasetManifest, Instrument

DEFAULT_FIXTURE_DIR = (
    Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "synthetic"
)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_synthetic_dataset(fixture_dir: Path | None = None) -> tuple[
    DatasetManifest,
    list[Instrument],
    list[Bar],
    list[CorporateAction],
]:
    root = fixture_dir or DEFAULT_FIXTURE_DIR
    manifest = DatasetManifest.from_dict(load_json(root / "dataset.json"))  # type: ignore[arg-type]
    if not manifest.is_synthetic or not manifest.not_for_performance:
        raise ValueError("refusing to load a dataset that is not labelled synthetic/not-for-performance")
    instruments = [Instrument.from_dict(row) for row in load_json(root / "instruments.json")]  # type: ignore[arg-type]
    bars = [Bar.from_dict(row) for row in load_json(root / "bars_5m.json")]  # type: ignore[arg-type]
    actions = [CorporateAction.from_dict(row) for row in load_json(root / "corporate_actions.json")]  # type: ignore[arg-type]
    if any(not bar.is_synthetic for bar in bars):
        raise ValueError("synthetic fixture contains a bar not flagged is_synthetic")
    return manifest, instruments, bars, actions
