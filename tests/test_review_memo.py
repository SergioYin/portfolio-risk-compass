import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_risk_compass.cli import main
from portfolio_risk_compass.demo import build_demo_bundle
from portfolio_risk_compass.review_memo import (
    build_review_memo,
    render_review_memo_markdown,
)


class ReviewMemoTests(unittest.TestCase):
    def test_review_memo_combines_required_artifacts_with_boundaries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
                include_templates=False,
            )

            memo = build_review_memo(output_dir)
            markdown = render_review_memo_markdown(memo)

        self.assertEqual(
            set(memo["source_artifacts"]),
            {"exposure", "guardrails", "stress", "catalysts", "history", "watchlist"},
        )
        self.assertIn("# Portfolio Review Memo", markdown)
        self.assertIn("Non-advice boundary:", markdown)
        self.assertIn("not investment, tax, legal, accounting, or trading advice", markdown)
        self.assertIn("## Assumptions", markdown)
        self.assertIn("| exposure | exposure_report.json |", markdown)
        self.assertIn("- Portfolio value: 7350.00 USD", markdown)
        self.assertIn("- Guardrail status: FAIL", markdown)
        self.assertIn("Risk-off rotation", markdown)
        self.assertIn("## Human Review Checklist", markdown)

    def test_cli_review_memo_writes_markdown_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "outputs"
            build_demo_bundle(
                Path("examples/fixtures"),
                output_dir,
                as_of="2026-05-15",
                include_templates=False,
            )
            memo_path = output_dir / "memo.md"

            with patch("sys.stdout") as stdout:
                self.assertEqual(
                    main(
                        [
                            "review-memo",
                            "--outputs-dir",
                            str(output_dir),
                            "--markdown",
                            str(memo_path),
                            "--title",
                            "Committee Memo",
                        ]
                    ),
                    0,
                )

            markdown = memo_path.read_text(encoding="utf-8")

        self.assertEqual(stdout.write.call_args.args[0], str(memo_path) + "\n")
        self.assertIn("# Committee Memo", markdown)
        self.assertIn("## Rebalance Watchlist", markdown)

    def test_review_memo_requires_all_source_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            (output_dir / "exposure_report.json").write_text(
                json.dumps({"metadata": {}}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "missing required artifact"):
                build_review_memo(output_dir)


if __name__ == "__main__":
    unittest.main()
