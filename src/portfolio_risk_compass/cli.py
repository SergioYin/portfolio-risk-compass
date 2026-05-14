"""Command line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .analysis import analyze_portfolio
from .catalysts import (
    build_catalyst_checklist,
    read_catalysts_json,
    render_catalyst_json,
    render_catalyst_markdown,
)
from .config import read_config_json
from .guardrails import (
    ReviewDates,
    evaluate_guardrails,
    parse_review_date,
    render_guardrail_json,
    render_guardrail_markdown,
)
from .demo import (
    DEFAULT_AS_OF,
    DEFAULT_FIXTURES_DIR,
    DEFAULT_OUTPUT_DIR,
    build_demo_bundle,
)
from .dashboard import DEFAULT_DASHBOARD_TITLE, write_dashboard_html
from .holdings import read_holdings_csv
from .integrations import (
    INTEGRATION_PROFILES,
    build_integration_export,
    render_integration_export_json,
    write_integration_export,
)
from .packaging import (
    DEFAULT_RELEASE_MANIFEST_JSON,
    DEFAULT_RELEASE_MANIFEST_MARKDOWN,
    DEFAULT_RELEASE_OUTPUTS_DIR,
    build_package_audit,
    render_package_audit_json,
    render_package_audit_markdown,
    write_release_manifest,
)
from .reports import render_json_report, render_markdown_report
from .snapshots import (
    build_snapshot,
    diff_snapshots,
    read_snapshot,
    render_diff_markdown,
    render_snapshot_json,
    write_snapshot,
)
from .stress import (
    read_scenario_json,
    render_stress_json,
    render_stress_markdown,
    stress_portfolio,
)
from .templates import (
    DEFAULT_TEMPLATES_DIR,
    render_template_list_json,
    render_template_list_markdown,
    template_manifest,
)

COMMAND_NAMES = (
    "analyze",
    "snapshot",
    "diff",
    "catalysts",
    "guardrails",
    "stress",
    "template-list",
    "demo-bundle",
    "dashboard",
    "integration-export",
    "package-audit",
    "release-manifest",
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return _run_analyze(args)
    if args.command == "snapshot":
        return _run_snapshot(args)
    if args.command == "diff":
        return _run_diff(args)
    if args.command == "catalysts":
        return _run_catalysts(args)
    if args.command == "guardrails":
        return _run_guardrails(args)
    if args.command == "stress":
        return _run_stress(args)
    if args.command == "template-list":
        return _run_template_list(args)
    if args.command == "demo-bundle":
        return _run_demo_bundle(args)
    if args.command == "dashboard":
        return _run_dashboard(args)
    if args.command == "integration-export":
        return _run_integration_export(args)
    if args.command == "package-audit":
        return _run_package_audit(args)
    if args.command == "release-manifest":
        return _run_release_manifest(args)

    parser.error("a command is required")
    return 2


def _run_analyze(args: argparse.Namespace) -> int:
    holdings = read_holdings_csv(args.holdings_csv)
    config = read_config_json(args.config) if args.config else None
    report = analyze_portfolio(holdings, config)

    json_report = render_json_report(report)
    markdown_report = render_markdown_report(report)

    wrote_file = False
    if args.json:
        _write_text(args.json, json_report)
        wrote_file = True
    if args.markdown:
        _write_text(args.markdown, markdown_report)
        wrote_file = True

    if not wrote_file:
        sys.stdout.write(json_report)
    return 0


def _run_snapshot(args: argparse.Namespace) -> int:
    holdings = read_holdings_csv(args.holdings_csv)
    config = read_config_json(args.config) if args.config else None
    report = analyze_portfolio(holdings, config)
    snapshot = build_snapshot(report, snapshot_date=args.date, snapshot_id=args.id)
    write_snapshot(args.output_json, snapshot)
    return 0


def _run_diff(args: argparse.Namespace) -> int:
    before = read_snapshot(args.before_snapshot)
    after = read_snapshot(args.after_snapshot)
    diff = diff_snapshots(before, after)

    if args.json:
        sys.stdout.write(render_snapshot_json(diff))
    else:
        sys.stdout.write(render_diff_markdown(diff))
    return 0


def _run_catalysts(args: argparse.Namespace) -> int:
    catalysts = read_catalysts_json(args.catalysts_json)
    checklist = build_catalyst_checklist(catalysts, as_of=args.as_of)

    json_checklist = render_catalyst_json(checklist)
    markdown_checklist = render_catalyst_markdown(checklist)

    wrote_file = False
    if args.json:
        _write_text(args.json, json_checklist)
        wrote_file = True
    if args.markdown:
        _write_text(args.markdown, markdown_checklist)
        wrote_file = True

    if not wrote_file:
        sys.stdout.write(json_checklist)
    return 0


def _run_guardrails(args: argparse.Namespace) -> int:
    holdings = read_holdings_csv(args.holdings_csv)
    config = read_config_json(args.config)
    review = evaluate_guardrails(
        holdings,
        config,
        ReviewDates(
            snapshot_date=parse_review_date(args.snapshot_date, "snapshot_date"),
            last_review_date=parse_review_date(args.last_review_date, "last_review_date"),
        ),
    )

    json_review = render_guardrail_json(review)
    markdown_review = render_guardrail_markdown(review)

    wrote_file = False
    if args.json:
        _write_text(args.json, json_review)
        wrote_file = True
    if args.markdown:
        _write_text(args.markdown, markdown_review)
        wrote_file = True

    if not wrote_file:
        if args.format == "markdown":
            sys.stdout.write(markdown_review)
        else:
            sys.stdout.write(json_review)
    return 0


def _run_stress(args: argparse.Namespace) -> int:
    holdings = read_holdings_csv(args.holdings_csv)
    scenario = read_scenario_json(args.scenario_json)
    report = stress_portfolio(holdings, scenario)

    json_report = render_stress_json(report)
    markdown_report = render_stress_markdown(report)

    wrote_file = False
    if args.json:
        _write_text(args.json, json_report)
        wrote_file = True
    if args.markdown:
        _write_text(args.markdown, markdown_report)
        wrote_file = True

    if not wrote_file:
        if args.format == "markdown":
            sys.stdout.write(markdown_report)
        else:
            sys.stdout.write(json_report)
    return 0


def _run_template_list(args: argparse.Namespace) -> int:
    manifest = template_manifest(args.templates_dir)
    if args.format == "markdown":
        sys.stdout.write(render_template_list_markdown(manifest))
    else:
        sys.stdout.write(render_template_list_json(manifest))
    return 0


def _run_demo_bundle(args: argparse.Namespace) -> int:
    build_demo_bundle(
        args.fixtures_dir,
        args.output_dir,
        args.as_of,
        templates_dir=args.templates_dir,
        include_templates=not args.no_templates,
    )
    sys.stdout.write(str(args.output_dir / "index.json") + "\n")
    return 0


def _run_dashboard(args: argparse.Namespace) -> int:
    write_dashboard_html(args.input_json, args.output_html, title=args.title)
    sys.stdout.write(str(args.output_html) + "\n")
    return 0


def _run_integration_export(args: argparse.Namespace) -> int:
    if args.json:
        write_integration_export(args.outputs_dir, args.profile, args.json)
        sys.stdout.write(str(args.json) + "\n")
    else:
        export = build_integration_export(args.outputs_dir, args.profile)
        sys.stdout.write(render_integration_export_json(export))
    return 0


def _run_package_audit(args: argparse.Namespace) -> int:
    report = build_package_audit(
        args.root,
        command_count=len(COMMAND_NAMES),
        run_tests=args.run_tests,
    )
    if args.format == "markdown":
        sys.stdout.write(render_package_audit_markdown(report))
    else:
        sys.stdout.write(render_package_audit_json(report))
    return 0 if not report["tests"]["run"] or report["tests"]["passed"] else 1


def _run_release_manifest(args: argparse.Namespace) -> int:
    write_release_manifest(args.outputs_dir, args.json, args.markdown)
    sys.stdout.write(str(args.json) + "\n")
    sys.stdout.write(str(args.markdown) + "\n")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portfolio-risk-compass",
        description="Generate portfolio exposure reports from holdings CSV files.",
    )
    subparsers = parser.add_subparsers(dest="command")

    analyze = subparsers.add_parser(
        "analyze",
        help="Analyze holdings exposure.",
        description="Analyze holdings exposure and write JSON or Markdown reports.",
    )
    analyze.add_argument("holdings_csv", type=Path, help="Path to holdings CSV.")
    analyze.add_argument(
        "--config",
        type=Path,
        help="Optional JSON config with grouping, targets, and limits.",
    )
    analyze.add_argument("--json", type=Path, help="Write JSON report to this path.")
    analyze.add_argument(
        "--markdown", type=Path, help="Write Markdown report to this path."
    )

    snapshot = subparsers.add_parser(
        "snapshot",
        help="Save an analyzed report as a dated JSON snapshot.",
        description="Analyze holdings and save a JSON snapshot with date and id metadata.",
    )
    snapshot.add_argument("holdings_csv", type=Path, help="Path to holdings CSV.")
    snapshot.add_argument("output_json", type=Path, help="Path to write snapshot JSON.")
    snapshot.add_argument(
        "--config",
        type=Path,
        help="Optional JSON config with grouping, targets, and limits.",
    )
    snapshot.add_argument(
        "--date",
        help="Snapshot date metadata. Defaults to today's date.",
    )
    snapshot.add_argument(
        "--id",
        help="Snapshot id metadata. Defaults to a generated id.",
    )

    diff = subparsers.add_parser(
        "diff",
        help="Compare two saved portfolio snapshots.",
        description=(
            "Compare total value, allocation buckets, concentration, and target drift "
            "between two snapshot JSON files."
        ),
    )
    diff.add_argument("before_snapshot", type=Path, help="Earlier snapshot JSON.")
    diff.add_argument("after_snapshot", type=Path, help="Later snapshot JSON.")
    diff.add_argument(
        "--json", action="store_true", help="Print JSON instead of Markdown."
    )

    catalysts = subparsers.add_parser(
        "catalysts",
        help="Render a catalyst calendar checklist.",
        description=(
            "Read a catalysts JSON fixture and render a date-ordered checklist "
            "with overdue, today, and upcoming flags relative to --as-of."
        ),
    )
    catalysts.add_argument("catalysts_json", type=Path, help="Path to catalysts JSON.")
    catalysts.add_argument(
        "--as-of",
        help="Reference date for overdue and upcoming flags. Defaults to today's date.",
    )
    catalysts.add_argument("--json", type=Path, help="Write JSON checklist to this path.")
    catalysts.add_argument(
        "--markdown", type=Path, help="Write Markdown checklist to this path."
    )

    guardrails = subparsers.add_parser(
        "guardrails",
        help="Evaluate configured portfolio guardrail policy checks.",
        description=(
            "Evaluate position, sector, cash, leverage, and review cadence guardrails "
            "against holdings and config."
        ),
    )
    guardrails.add_argument("holdings_csv", type=Path, help="Path to holdings CSV.")
    guardrails.add_argument(
        "--config",
        type=Path,
        required=True,
        help="JSON config with guardrail policy fields.",
    )
    guardrails.add_argument(
        "--snapshot-date",
        help="Portfolio snapshot date for review cadence checks. Defaults to today.",
    )
    guardrails.add_argument(
        "--last-review-date",
        help="Last completed portfolio review date. Overrides config last_review_date.",
    )
    guardrails.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Stdout format when no output path is provided.",
    )
    guardrails.add_argument("--json", type=Path, help="Write JSON review to this path.")
    guardrails.add_argument(
        "--markdown", type=Path, help="Write Markdown review to this path."
    )

    stress = subparsers.add_parser(
        "stress",
        help="Estimate stressed market value under scenario shocks.",
        description=(
            "Apply named percentage price shocks by symbol, sector, asset_class, "
            "region, or currency and report stressed market value plus contribution deltas."
        ),
    )
    stress.add_argument("holdings_csv", type=Path, help="Path to holdings CSV.")
    stress.add_argument("scenario_json", type=Path, help="Path to scenario JSON.")
    stress.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Stdout format when no output path is provided.",
    )
    stress.add_argument(
        "--json", type=Path, help="Write JSON stress report to this path."
    )
    stress.add_argument(
        "--markdown", type=Path, help="Write Markdown stress report to this path."
    )

    template_list = subparsers.add_parser(
        "template-list",
        help="List example portfolio templates.",
        description=(
            "List named example portfolio templates with their holdings, config, "
            "catalysts, and scenario fixture files."
        ),
    )
    template_list.add_argument(
        "--templates-dir",
        type=Path,
        default=DEFAULT_TEMPLATES_DIR,
        help=f"Directory containing template fixtures. Defaults to {DEFAULT_TEMPLATES_DIR}.",
    )
    template_list.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format. Defaults to JSON.",
    )

    demo_bundle = subparsers.add_parser(
        "demo-bundle",
        help="Regenerate example output artifacts from fixtures.",
        description=(
            "Regenerate examples/outputs artifacts from examples/fixtures, including "
            "reports, snapshot, catalyst checklist, guardrails, stress results, "
            "template gallery outputs, and index manifest."
        ),
    )
    demo_bundle.add_argument(
        "--fixtures-dir",
        type=Path,
        default=DEFAULT_FIXTURES_DIR,
        help=f"Directory containing demo fixtures. Defaults to {DEFAULT_FIXTURES_DIR}.",
    )
    demo_bundle.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to write demo artifacts. Defaults to {DEFAULT_OUTPUT_DIR}.",
    )
    demo_bundle.add_argument(
        "--as-of",
        default=DEFAULT_AS_OF,
        help=f"Reference date for date-sensitive demo outputs. Defaults to {DEFAULT_AS_OF}.",
    )
    demo_bundle.add_argument(
        "--templates-dir",
        type=Path,
        default=DEFAULT_TEMPLATES_DIR,
        help=f"Directory containing template fixtures. Defaults to {DEFAULT_TEMPLATES_DIR}.",
    )
    demo_bundle.add_argument(
        "--no-templates",
        action="store_true",
        help="Only render the base demo fixtures, without template gallery outputs.",
    )

    dashboard = subparsers.add_parser(
        "dashboard",
        help="Export a static HTML dashboard from a report JSON or demo manifest.",
        description=(
            "Read an exposure report JSON or demo-bundle index manifest and write a "
            "single self-contained HTML dashboard with no JavaScript."
        ),
    )
    dashboard.add_argument(
        "input_json",
        type=Path,
        help="Path to exposure_report.json or a demo-bundle index.json manifest.",
    )
    dashboard.add_argument(
        "output_html",
        type=Path,
        help="Path to write the static dashboard HTML.",
    )
    dashboard.add_argument(
        "--title",
        default=DEFAULT_DASHBOARD_TITLE,
        help=f"Dashboard title. Defaults to {DEFAULT_DASHBOARD_TITLE!r}.",
    )

    integration_export = subparsers.add_parser(
        "integration-export",
        help="Export neutral adapter JSON for adjacent artifact consumers.",
        description=(
            "Read generated output artifacts and write deterministic adapter JSON "
            "for optional downstream workflows without importing or depending on them."
        ),
    )
    integration_export.add_argument(
        "profile",
        choices=INTEGRATION_PROFILES,
        help="Adapter profile to render.",
    )
    integration_export.add_argument(
        "--outputs-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory containing generated artifacts. Defaults to {DEFAULT_OUTPUT_DIR}.",
    )
    integration_export.add_argument(
        "--json",
        type=Path,
        help="Path to write adapter JSON. Prints JSON to stdout when omitted.",
    )

    package_audit = subparsers.add_parser(
        "package-audit",
        help="Report packaging readiness counts and missing items.",
        description=(
            "Report the package version, CLI command count, fixture count, output "
            "artifact count, missing packaging items, and optionally run tests."
        ),
    )
    package_audit.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to audit. Defaults to the current working directory.",
    )
    package_audit.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Report format. Defaults to JSON.",
    )
    package_audit.add_argument(
        "--run-tests",
        action="store_true",
        help="Run the unittest suite and include the result in the report.",
    )

    release_manifest = subparsers.add_parser(
        "release-manifest",
        help="Write JSON and Markdown inventories for output artifacts.",
        description=(
            "Create JSON and Markdown release artifact inventories for examples/outputs "
            "with byte sizes and SHA-256 hashes."
        ),
    )
    release_manifest.add_argument(
        "--outputs-dir",
        type=Path,
        default=DEFAULT_RELEASE_OUTPUTS_DIR,
        help=f"Directory to inventory. Defaults to {DEFAULT_RELEASE_OUTPUTS_DIR}.",
    )
    release_manifest.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_RELEASE_MANIFEST_JSON,
        help=f"Path to write JSON manifest. Defaults to {DEFAULT_RELEASE_MANIFEST_JSON}.",
    )
    release_manifest.add_argument(
        "--markdown",
        type=Path,
        default=DEFAULT_RELEASE_MANIFEST_MARKDOWN,
        help=(
            "Path to write Markdown manifest. Defaults to "
            f"{DEFAULT_RELEASE_MANIFEST_MARKDOWN}."
        ),
    )
    return parser


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
