"""Portfolio exposure analysis from plain holdings files."""

from .analysis import analyze_portfolio
from .config import AnalysisConfig
from .holdings import Holding, read_holdings_csv
from .reports import render_json_report, render_markdown_report

__all__ = [
    "AnalysisConfig",
    "Holding",
    "analyze_portfolio",
    "read_holdings_csv",
    "render_json_report",
    "render_markdown_report",
]

__version__ = "0.4.0"
