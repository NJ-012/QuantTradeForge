"""Phase 1.1: required documentation exists. Not a trading or data-quality test."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase11DocumentsExistTests(unittest.TestCase):
    required_paths = (
        "README.md",
        ".gitignore",
        "docs/architecture.md",
        "docs/roadmap.md",
        "docs/decisions.md",
        "docs/data_requirements.md",
        "docs/data_schema.md",
        "docs/strategy_specifications/tsmom_v0.1.md",
        "docs/testing.md",
        "docs/risk_management.md",
        "docs/operations.md",
    )

    def test_required_files_exist_and_non_empty(self) -> None:
        missing = []
        empty = []
        for rel in self.required_paths:
            path = ROOT / rel
            if not path.is_file():
                missing.append(rel)
                continue
            if path.stat().st_size == 0:
                empty.append(rel)
        self.assertEqual(missing, [], f"missing files: {missing}")
        self.assertEqual(empty, [], f"empty files: {empty}")


class Phase11ContentContractTests(unittest.TestCase):
    def _read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_readme_identifies_project_and_phase(self) -> None:
        text = self._read("README.md")
        self.assertIn("QuantTradeForge", text)
        self.assertIn("Phase 1", text)

    def test_roadmap_does_not_mark_phase_1_complete(self) -> None:
        text = self._read("docs/roadmap.md")
        self.assertIn("**Status:** In progress", text)
        self.assertIn("1.1", text)
        self.assertIn("Not complete", text)
        self.assertNotIn("Phase 1 — Market data infrastructure\n\n**Status:** Tested", text)

    def test_tsmom_preserved_and_not_claimed_backtested(self) -> None:
        text = self._read("docs/strategy_specifications/tsmom_v0.1.md")
        self.assertIn("TSMOM", text)
        self.assertIn("0.1", text)
        self.assertIn("10 candles", text)
        self.assertIn("Not backtested", text)
        self.assertIn("Unresolved", text)

    def test_data_requirements_cover_ten_questions_as_open_or_answered(self) -> None:
        text = self._read("docs/data_requirements.md")
        for heading in (
            "Required historical coverage",
            "Required bar frequencies",
            "Instrument-universe requirements",
            "Data licensing and permitted use",
            "Availability of historical intraday data",
            "Data-provider and broker API limitations",
            "Estimated costs and storage",
            "Timestamp and timezone conventions",
            "Corporate-action adjustment policies",
            "Missing, duplicate, stale, and out-of-order data",
        ):
            self.assertIn(heading, text)
        self.assertIn("Open", text)
        self.assertIn("Asia/Kolkata", text)

    def test_gitignore_excludes_secrets(self) -> None:
        text = self._read(".gitignore")
        self.assertIn(".env", text)
        self.assertIn("credentials.json", text)

    def test_live_trading_not_enabled(self) -> None:
        ops = self._read("docs/operations.md")
        self.assertIn("not enabled", ops.lower())
        risk = self._read("docs/risk_management.md")
        self.assertIn("not", risk.lower())
        self.assertIn("authorization", risk.lower())


if __name__ == "__main__":
    unittest.main()
