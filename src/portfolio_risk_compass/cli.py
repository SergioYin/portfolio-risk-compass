"""Command line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .analysis import analyze_portfolio
from .case_study import (
    DEFAULT_CASE_STUDY_JSON,
    DEFAULT_CASE_STUDY_MARKDOWN,
    write_case_study_comparison,
)
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
from .demo_capture_receipt import (
    DEFAULT_DEMO_CAPTURE_RECEIPT_JSON,
    DEFAULT_DEMO_CAPTURE_RECEIPT_MARKDOWN,
    write_demo_capture_receipt,
)
from .dashboard import (
    DEFAULT_DASHBOARD_TITLE,
    DEFAULT_WALKTHROUGH_JSON,
    DEFAULT_WALKTHROUGH_MARKDOWN,
    write_dashboard_html,
    write_showcase_walkthrough,
)
from .docs_export import DEFAULT_DOCS_EXPORT, write_docs_export
from .holdings import read_holdings_csv
from .history import (
    build_history_ledger,
    render_history_json,
    render_history_markdown,
)
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
from .public_review import (
    DEFAULT_PUBLIC_REVIEW_JSON,
    DEFAULT_PUBLIC_REVIEW_MARKDOWN,
    write_public_review_walkthrough,
)
from .rebalance_watchlist import (
    build_rebalance_watchlist,
    render_rebalance_watchlist_json,
    render_rebalance_watchlist_markdown,
)
from .reports import render_json_report, render_markdown_report
from .review_memo import build_review_memo, render_review_memo_markdown
from .reviewer_evidence import (
    DEFAULT_REVIEWER_EVIDENCE_JSON,
    DEFAULT_REVIEWER_EVIDENCE_MARKDOWN,
    write_reviewer_evidence,
)
from .scenario_evidence import (
    DEFAULT_SCENARIO_EVIDENCE_JSON,
    DEFAULT_SCENARIO_EVIDENCE_MARKDOWN,
    write_scenario_evidence_receipt,
)
from .screenshot_guide import (
    DEFAULT_SCREENSHOT_GUIDE_JSON,
    DEFAULT_SCREENSHOT_GUIDE_MARKDOWN,
    DEFAULT_SCREENSHOT_PATH,
    write_screenshot_guide,
)
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
from .visual_evidence import (
    DEFAULT_VISUAL_EVIDENCE_JSON,
    DEFAULT_VISUAL_EVIDENCE_MARKDOWN,
    write_visual_evidence_receipt,
)
from .visual_capture_audit import (
    DEFAULT_VISUAL_CAPTURE_AUDIT_JSON,
    DEFAULT_VISUAL_CAPTURE_AUDIT_MARKDOWN,
    build_visual_capture_audit,
    render_visual_capture_audit_json,
    render_visual_capture_audit_markdown,
    write_visual_capture_audit,
)
from .visual_capture_compare import (
    DEFAULT_VISUAL_CAPTURE_COMPARE_JSON,
    DEFAULT_VISUAL_CAPTURE_COMPARE_MARKDOWN,
    compare_visual_capture_audits,
    read_visual_capture_audit,
    render_visual_capture_compare_json,
    render_visual_capture_compare_markdown,
    write_visual_capture_compare,
)

COMMAND_NAMES = (
    "analyze",
    "snapshot",
    "diff",
    "history",
    "catalysts",
    "guardrails",
    "stress",
    "rebalance-watchlist",
    "review-memo",
    "template-list",
    "demo-bundle",
    "case-study",
    "showcase",
    "reviewer-evidence",
    "scenario-evidence-receipt",
    "public-review",
    "visual-evidence-receipt",
    "screenshot-guide",
    "demo-capture-receipt",
    "visual-capture-audit",
    "visual-capture-compare",
    "dashboard",
    "integration-export",
    "docs-export",
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
    if args.command == "history":
        return _run_history(args)
    if args.command == "catalysts":
        return _run_catalysts(args)
    if args.command == "guardrails":
        return _run_guardrails(args)
    if args.command == "stress":
        return _run_stress(args)
    if args.command == "rebalance-watchlist":
        return _run_rebalance_watchlist(args)
    if args.command == "review-memo":
        return _run_review_memo(args)
    if args.command == "template-list":
        return _run_template_list(args)
    if args.command == "demo-bundle":
        return _run_demo_bundle(args)
    if args.command == "case-study":
        return _run_case_study(args)
    if args.command == "showcase":
        return _run_showcase(args)
    if args.command == "reviewer-evidence":
        return _run_reviewer_evidence(args)
    if args.command == "scenario-evidence-receipt":
        return _run_scenario_evidence_receipt(args)
    if args.command == "public-review":
        return _run_public_review(args)
    if args.command == "visual-evidence-receipt":
        return _run_visual_evidence_receipt(args)
    if args.command == "screenshot-guide":
        return _run_screenshot_guide(args)
    if args.command == "demo-capture-receipt":
        return _run_demo_capture_receipt(args)
    if args.command == "visual-capture-audit":
        return _run_visual_capture_audit(args)
    if args.command == "visual-capture-compare":
        return _run_visual_capture_compare(args)
    if args.command == "dashboard":
        return _run_dashboard(args)
    if args.command == "integration-export":
        return _run_integration_export(args)
    if args.command == "docs-export":
        return _run_docs_export(args)
    if args.command == "package-audit":
        return _run_package_audit(args)
    if args.command == "release-manifest":
        return _run_release_manifest(args)

    parser.error("a command is required")
    return 2


def visual_capture_audit_main(argv: Sequence[str] | None = None) -> int:
    args = ["visual-capture-audit"]
    if argv is None:
        args.extend(sys.argv[1:])
    else:
        args.extend(argv)
    return main(args)


def visual_capture_compare_main(argv: Sequence[str] | None = None) -> int:
    args = ["visual-capture-compare"]
    if argv is None:
        args.extend(sys.argv[1:])
    else:
        args.extend(argv)
    return main(args)


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


def _run_history(args: argparse.Namespace) -> int:
    ledger = build_history_ledger(args.snapshots_dir)
    json_ledger = render_history_json(ledger)
    markdown_ledger = render_history_markdown(ledger)

    wrote_file = False
    if args.json:
        _write_text(args.json, json_ledger)
        wrote_file = True
    if args.markdown:
        _write_text(args.markdown, markdown_ledger)
        wrote_file = True

    if not wrote_file:
        if args.format == "markdown":
            sys.stdout.write(markdown_ledger)
        else:
            sys.stdout.write(json_ledger)
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


def _run_rebalance_watchlist(args: argparse.Namespace) -> int:
    holdings = read_holdings_csv(args.holdings_csv)
    config = read_config_json(args.config)
    scenario = read_scenario_json(args.scenario_json)
    exposure_report = analyze_portfolio(holdings, config)
    guardrail_review = evaluate_guardrails(
        holdings,
        config,
        ReviewDates(
            snapshot_date=parse_review_date(args.snapshot_date, "snapshot_date"),
            last_review_date=parse_review_date(args.last_review_date, "last_review_date"),
        ),
    )
    stress_report = stress_portfolio(holdings, scenario)
    watchlist = build_rebalance_watchlist(
        exposure_report,
        guardrail_review,
        stress_report,
    )

    json_report = render_rebalance_watchlist_json(watchlist)
    markdown_report = render_rebalance_watchlist_markdown(watchlist)

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


def _run_review_memo(args: argparse.Namespace) -> int:
    memo = build_review_memo(args.outputs_dir, title=args.title)
    markdown = render_review_memo_markdown(memo)

    if args.markdown:
        _write_text(args.markdown, markdown)
        sys.stdout.write(str(args.markdown) + "\n")
    else:
        sys.stdout.write(markdown)
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


def _run_showcase(args: argparse.Namespace) -> int:
    paths = write_showcase_walkthrough(args.manifest, args.markdown, args.json)
    sys.stdout.write(str(paths["markdown"]) + "\n")
    sys.stdout.write(str(paths["json"]) + "\n")
    return 0


def _run_reviewer_evidence(args: argparse.Namespace) -> int:
    paths = write_reviewer_evidence(args.manifest, args.markdown, args.json)
    sys.stdout.write(str(paths["markdown"]) + "\n")
    sys.stdout.write(str(paths["json"]) + "\n")
    return 0


def _run_scenario_evidence_receipt(args: argparse.Namespace) -> int:
    paths = write_scenario_evidence_receipt(args.manifest, args.markdown, args.json)
    sys.stdout.write(str(paths["markdown"]) + "\n")
    sys.stdout.write(str(paths["json"]) + "\n")
    return 0


def _run_public_review(args: argparse.Namespace) -> int:
    paths = write_public_review_walkthrough(args.manifest, args.markdown, args.json)
    sys.stdout.write(str(paths["markdown"]) + "\n")
    sys.stdout.write(str(paths["json"]) + "\n")
    return 0


def _run_visual_evidence_receipt(args: argparse.Namespace) -> int:
    paths = write_visual_evidence_receipt(args.manifest, args.markdown, args.json)
    sys.stdout.write(str(paths["markdown"]) + "\n")
    sys.stdout.write(str(paths["json"]) + "\n")
    return 0


def _run_screenshot_guide(args: argparse.Namespace) -> int:
    paths = write_screenshot_guide(
        args.manifest,
        args.markdown,
        args.json,
        screenshot_path=args.screenshot_path,
    )
    sys.stdout.write(str(paths["markdown"]) + "\n")
    sys.stdout.write(str(paths["json"]) + "\n")
    return 0


def _run_demo_capture_receipt(args: argparse.Namespace) -> int:
    paths = write_demo_capture_receipt(args.manifest, args.markdown, args.json)
    sys.stdout.write(str(paths["markdown"]) + "\n")
    sys.stdout.write(str(paths["json"]) + "\n")
    return 0


def _run_visual_capture_audit(args: argparse.Namespace) -> int:
    if args.output:
        write_visual_capture_audit(args.root, args.output, args.format)
        sys.stdout.write(str(args.output) + "\n")
        return 0
    audit = build_visual_capture_audit(args.root)
    if args.format == "markdown":
        sys.stdout.write(render_visual_capture_audit_markdown(audit))
    else:
        sys.stdout.write(render_visual_capture_audit_json(audit))
    return 0


def _run_visual_capture_compare(args: argparse.Namespace) -> int:
    try:
        if args.output:
            write_visual_capture_compare(args.before, args.after, args.output, args.format)
            sys.stdout.write(str(args.output) + "\n")
            return 0
        comparison = compare_visual_capture_audits(
            read_visual_capture_audit(args.before),
            read_visual_capture_audit(args.after),
        )
    except ValueError as exc:
        sys.stderr.write(f"visual-capture-compare: {exc}\n")
        return 2
    if args.format == "markdown":
        sys.stdout.write(render_visual_capture_compare_markdown(comparison))
    else:
        sys.stdout.write(render_visual_capture_compare_json(comparison))
    return 0


def _run_case_study(args: argparse.Namespace) -> int:
    paths = write_case_study_comparison(args.manifest, args.markdown, args.json)
    sys.stdout.write(str(paths["markdown"]) + "\n")
    sys.stdout.write(str(paths["json"]) + "\n")
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


def _run_docs_export(args: argparse.Namespace) -> int:
    write_docs_export(
        _build_parser(),
        args.output,
        outputs_dir=args.outputs_dir,
        output_format=args.format,
        title=args.title,
    )
    sys.stdout.write(str(args.output) + "\n")
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

    history = subparsers.add_parser(
        "history",
        help="Render a trend ledger from a directory of snapshots.",
        description=(
            "Read snapshot JSON files from a directory and render total value trends, "
            "target exposure drift, guardrail status when present, and catalyst counts "
            "when present."
        ),
    )
    history.add_argument(
        "snapshots_dir",
        type=Path,
        help="Directory containing snapshot JSON files.",
    )
    history.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Stdout format when no output path is provided.",
    )
    history.add_argument("--json", type=Path, help="Write JSON ledger to this path.")
    history.add_argument(
        "--markdown", type=Path, help="Write Markdown ledger to this path."
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

    watchlist = subparsers.add_parser(
        "rebalance-watchlist",
        help="Build an educational review watchlist without trade recommendations.",
        description=(
            "Combine target drift, guardrail WARN/FAIL items, concentration, and "
            "stress drawdowns into a broker-free educational review watchlist with "
            "reason codes and severity. The output does not recommend trades or quantities."
        ),
    )
    watchlist.add_argument("holdings_csv", type=Path, help="Path to holdings CSV.")
    watchlist.add_argument("scenario_json", type=Path, help="Path to scenario JSON.")
    watchlist.add_argument(
        "--config",
        type=Path,
        required=True,
        help="JSON config with targets and guardrail policy fields.",
    )
    watchlist.add_argument(
        "--snapshot-date",
        help="Portfolio snapshot date for review cadence checks. Defaults to today.",
    )
    watchlist.add_argument(
        "--last-review-date",
        help="Last completed portfolio review date. Overrides config last_review_date.",
    )
    watchlist.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Stdout format when no output path is provided.",
    )
    watchlist.add_argument(
        "--json", type=Path, help="Write JSON watchlist to this path."
    )
    watchlist.add_argument(
        "--markdown", type=Path, help="Write Markdown watchlist to this path."
    )

    review_memo = subparsers.add_parser(
        "review-memo",
        help="Assemble generated artifacts into a human review Markdown memo.",
        description=(
            "Read exposure, guardrails, stress, catalysts, history, and rebalance "
            "watchlist JSON artifacts from an outputs directory and combine them "
            "into a single Markdown memo with assumptions and a non-advice boundary."
        ),
    )
    review_memo.add_argument(
        "--outputs-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory containing generated JSON artifacts. Defaults to {DEFAULT_OUTPUT_DIR}.",
    )
    review_memo.add_argument(
        "--markdown",
        type=Path,
        help="Path to write the Markdown memo. Prints Markdown to stdout when omitted.",
    )
    review_memo.add_argument(
        "--title",
        default="Portfolio Review Memo",
        help="Memo title. Defaults to 'Portfolio Review Memo'.",
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

    case_study = subparsers.add_parser(
        "case-study",
        help="Write a deterministic base and template comparison from a demo manifest.",
        description=(
            "Read a demo-bundle index manifest and generated JSON artifacts, then "
            "write Markdown and JSON case-study comparison artifacts for the base "
            "demo, ETF core, leveraged sleeve, and cash rebalance examples. The "
            "comparison is static and does not provide investment advice."
        ),
    )
    case_study.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "index.json",
        help=f"Demo-bundle manifest to read. Defaults to {DEFAULT_OUTPUT_DIR / 'index.json'}.",
    )
    case_study.add_argument(
        "--markdown",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_CASE_STUDY_MARKDOWN,
        help=(
            "Path to write the Markdown comparison. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_CASE_STUDY_MARKDOWN}."
        ),
    )
    case_study.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_CASE_STUDY_JSON,
        help=(
            "Path to write the machine-readable comparison. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_CASE_STUDY_JSON}."
        ),
    )

    showcase = subparsers.add_parser(
        "showcase",
        help="Write a guided multi-template walkthrough from a demo manifest.",
        description=(
            "Read a demo-bundle index manifest and write deterministic Markdown and "
            "JSON walkthrough artifacts for the base demo plus every generated template. "
            "The walkthrough is a static review guide and does not provide investment advice."
        ),
    )
    showcase.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "index.json",
        help=f"Demo-bundle manifest to read. Defaults to {DEFAULT_OUTPUT_DIR / 'index.json'}.",
    )
    showcase.add_argument(
        "--markdown",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_WALKTHROUGH_MARKDOWN,
        help=(
            "Path to write the Markdown walkthrough. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_WALKTHROUGH_MARKDOWN}."
        ),
    )
    showcase.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_WALKTHROUGH_JSON,
        help=(
            "Path to write the machine-readable walkthrough. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_WALKTHROUGH_JSON}."
        ),
    )

    evidence = subparsers.add_parser(
        "reviewer-evidence",
        help="Write reviewer evidence for static demo artifacts.",
        description=(
            "Read a demo-bundle index manifest and write deterministic Markdown and "
            "JSON evidence showing which dashboard and case-study artifacts exist "
            "and which fixture files feed them."
        ),
    )
    evidence.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "index.json",
        help=f"Demo-bundle manifest to read. Defaults to {DEFAULT_OUTPUT_DIR / 'index.json'}.",
    )
    evidence.add_argument(
        "--markdown",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_REVIEWER_EVIDENCE_MARKDOWN,
        help=(
            "Path to write the Markdown evidence. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_REVIEWER_EVIDENCE_MARKDOWN}."
        ),
    )
    evidence.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_REVIEWER_EVIDENCE_JSON,
        help=(
            "Path to write the machine-readable evidence. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_REVIEWER_EVIDENCE_JSON}."
        ),
    )

    scenario_evidence = subparsers.add_parser(
        "scenario-evidence-receipt",
        help="Write scenario evidence receipt for static review artifacts.",
        description=(
            "Read a demo-bundle index manifest and write deterministic Markdown and "
            "JSON receipts tying static holdings, config, and scenario fixtures to "
            "stress, guardrail, and dashboard artifacts. The receipt records hashes "
            "and broker-free, no-live-data, no-advice boundaries."
        ),
    )
    scenario_evidence.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "index.json",
        help=f"Demo-bundle manifest to read. Defaults to {DEFAULT_OUTPUT_DIR / 'index.json'}.",
    )
    scenario_evidence.add_argument(
        "--markdown",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_SCENARIO_EVIDENCE_MARKDOWN,
        help=(
            "Path to write the Markdown receipt. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_SCENARIO_EVIDENCE_MARKDOWN}."
        ),
    )
    scenario_evidence.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_SCENARIO_EVIDENCE_JSON,
        help=(
            "Path to write the machine-readable receipt. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_SCENARIO_EVIDENCE_JSON}."
        ),
    )

    public_review = subparsers.add_parser(
        "public-review",
        help="Write a public static dashboard walkthrough and evidence packet.",
        description=(
            "Read a demo-bundle index manifest and write deterministic Markdown and "
            "JSON public-review artifacts with exact rerun commands, SHA-256 hashes, "
            "and no-live-data, no-broker, no-advice boundaries."
        ),
    )
    public_review.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "index.json",
        help=f"Demo-bundle manifest to read. Defaults to {DEFAULT_OUTPUT_DIR / 'index.json'}.",
    )
    public_review.add_argument(
        "--markdown",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_PUBLIC_REVIEW_MARKDOWN,
        help=(
            "Path to write the Markdown public-review packet. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_PUBLIC_REVIEW_MARKDOWN}."
        ),
    )
    public_review.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_PUBLIC_REVIEW_JSON,
        help=(
            "Path to write the machine-readable public-review packet. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_PUBLIC_REVIEW_JSON}."
        ),
    )

    visual_evidence = subparsers.add_parser(
        "visual-evidence-receipt",
        help="Write a visual evidence receipt for static dashboard review artifacts.",
        description=(
            "Read a demo-bundle index manifest and write deterministic Markdown and "
            "JSON receipts tying the static dashboard, public-review walkthrough, "
            "scenario evidence, reviewer evidence export, and broker-free/no-advice "
            "boundaries into one visual review route."
        ),
    )
    visual_evidence.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "index.json",
        help=f"Demo-bundle manifest to read. Defaults to {DEFAULT_OUTPUT_DIR / 'index.json'}.",
    )
    visual_evidence.add_argument(
        "--markdown",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_VISUAL_EVIDENCE_MARKDOWN,
        help=(
            "Path to write the Markdown visual evidence receipt. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_VISUAL_EVIDENCE_MARKDOWN}."
        ),
    )
    visual_evidence.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_VISUAL_EVIDENCE_JSON,
        help=(
            "Path to write the machine-readable visual evidence receipt. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_VISUAL_EVIDENCE_JSON}."
        ),
    )

    screenshot_guide = subparsers.add_parser(
        "screenshot-guide",
        help="Write exact dashboard screenshot capture instructions and hashes.",
        description=(
            "Read a demo-bundle index manifest and write deterministic Markdown and "
            "JSON guide artifacts tying the static public dashboard route to an exact "
            "Chromium screenshot command, source artifact hashes, screenshot hashes, "
            "and no-live-data, no-broker, no-advice boundaries."
        ),
    )
    screenshot_guide.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "index.json",
        help=f"Demo-bundle manifest to read. Defaults to {DEFAULT_OUTPUT_DIR / 'index.json'}.",
    )
    screenshot_guide.add_argument(
        "--markdown",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_SCREENSHOT_GUIDE_MARKDOWN,
        help=(
            "Path to write the Markdown screenshot guide. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_SCREENSHOT_GUIDE_MARKDOWN}."
        ),
    )
    screenshot_guide.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_SCREENSHOT_GUIDE_JSON,
        help=(
            "Path to write the machine-readable screenshot guide. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_SCREENSHOT_GUIDE_JSON}."
        ),
    )
    screenshot_guide.add_argument(
        "--screenshot-path",
        default=DEFAULT_SCREENSHOT_PATH,
        help=(
            "Screenshot path relative to the manifest directory. Defaults to "
            f"{DEFAULT_SCREENSHOT_PATH}."
        ),
    )

    demo_capture = subparsers.add_parser(
        "demo-capture-receipt",
        help="Write a public demo capture receipt and evidence index.",
        description=(
            "Read a demo-bundle index manifest and write deterministic Markdown and "
            "JSON artifacts tying the static dashboard screenshot/capture evidence "
            "to the screenshot guide, visual evidence receipt, public walkthrough, "
            "scenario receipt, reviewer evidence, and public-safe no-live-data, "
            "no-broker, no-order, no-position-sizing, no-recommendation, no-advice "
            "boundaries."
        ),
    )
    demo_capture.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "index.json",
        help=f"Demo-bundle manifest to read. Defaults to {DEFAULT_OUTPUT_DIR / 'index.json'}.",
    )
    demo_capture.add_argument(
        "--markdown",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_DEMO_CAPTURE_RECEIPT_MARKDOWN,
        help=(
            "Path to write the Markdown capture receipt. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_DEMO_CAPTURE_RECEIPT_MARKDOWN}."
        ),
    )
    demo_capture.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / DEFAULT_DEMO_CAPTURE_RECEIPT_JSON,
        help=(
            "Path to write the machine-readable capture receipt. Defaults to "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_DEMO_CAPTURE_RECEIPT_JSON}."
        ),
    )

    visual_capture_audit = subparsers.add_parser(
        "visual-capture-audit",
        help="Audit static visual/demo capture artifacts for gaps.",
        description=(
            "Read local visual/demo evidence artifacts under --root and write a "
            "deterministic JSON or Markdown audit with hashes, missing capture "
            "items, regeneration commands, and no-live-data/no-broker/no-order/"
            "no-position-sizing/no-recommendation/no-file-contents/no-advice "
            "boundaries."
        ),
    )
    visual_capture_audit.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Artifact directory to audit. Defaults to {DEFAULT_OUTPUT_DIR}.",
    )
    visual_capture_audit.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format. Defaults to JSON.",
    )
    visual_capture_audit.add_argument(
        "--output",
        type=Path,
        help=(
            "Optional output path. Defaults are "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_VISUAL_CAPTURE_AUDIT_JSON} for JSON "
            f"or {DEFAULT_OUTPUT_DIR / DEFAULT_VISUAL_CAPTURE_AUDIT_MARKDOWN} for Markdown "
            "when used in examples."
        ),
    )

    visual_capture_compare = subparsers.add_parser(
        "visual-capture-compare",
        help="Compare two static visual capture audit JSON files.",
        description=(
            "Compare release-to-release static/local visual capture audit JSON files "
            "by relative artifact path or artifact key and report added, removed, "
            "changed, and unchanged entries. Changed entries include bytes, hash, "
            "present, role, route, render, and capture command differences when "
            "available. The comparison has no live data, broker, order, position "
            "sizing, recommendation, advice, or private-data surface."
        ),
    )
    visual_capture_compare.add_argument(
        "--before",
        type=Path,
        required=True,
        help="Earlier visual_capture_audit.json file.",
    )
    visual_capture_compare.add_argument(
        "--after",
        type=Path,
        required=True,
        help="Later visual_capture_audit.json file.",
    )
    visual_capture_compare.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format. Defaults to JSON.",
    )
    visual_capture_compare.add_argument(
        "--output",
        type=Path,
        help=(
            "Optional output path. Defaults are "
            f"{DEFAULT_OUTPUT_DIR / DEFAULT_VISUAL_CAPTURE_COMPARE_JSON} for JSON "
            f"or {DEFAULT_OUTPUT_DIR / DEFAULT_VISUAL_CAPTURE_COMPARE_MARKDOWN} for Markdown "
            "when used in examples."
        ),
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

    docs_export = subparsers.add_parser(
        "docs-export",
        help="Write a deterministic single-file CLI and artifact reference.",
        description=(
            "Write CLI reference, input schemas, artifact inventory, safety boundary, "
            "and generated example output to one no-JavaScript Markdown or HTML file."
        ),
    )
    docs_export.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_DOCS_EXPORT,
        help=f"Path to write the docs file. Defaults to {DEFAULT_DOCS_EXPORT}.",
    )
    docs_export.add_argument(
        "--outputs-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to inventory. Defaults to {DEFAULT_OUTPUT_DIR}.",
    )
    docs_export.add_argument(
        "--format",
        choices=("markdown", "html"),
        default="markdown",
        help="Docs format. Defaults to Markdown.",
    )
    docs_export.add_argument(
        "--title",
        default="Portfolio Risk Compass Docs Export",
        help="Document title.",
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
