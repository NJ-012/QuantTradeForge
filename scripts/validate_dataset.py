"""Validate a persisted QuantTradeForge dataset directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from quanttradeforge.data.nse import load_dataset
from quanttradeforge.data.quality import ERROR, validate_dataset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()
    dataset = load_dataset(args.dataset)
    issues = validate_dataset(dataset.manifest, dataset.instruments, dataset.bars)
    errors = [issue for issue in issues if issue.severity == ERROR]
    for issue in issues:
        print(f"{issue.severity.value.upper()} {issue.code}: {issue.message}")
    print(
        f"dataset={dataset.manifest.dataset_id} "
        f"instruments={len(dataset.instruments)} bars={len(dataset.bars)} "
        f"errors={len(errors)} warnings={len(issues) - len(errors)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
