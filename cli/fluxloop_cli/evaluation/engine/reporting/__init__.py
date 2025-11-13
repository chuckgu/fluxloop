from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .html import DEFAULT_TEMPLATE, select_html_template, write_html_report
from .markdown import write_markdown_report

if TYPE_CHECKING:
    from ..core import EvaluationOptions, TraceOutcome
    from ...config import EvaluationConfig


def prepare_report_plan(options: "EvaluationOptions", config: "EvaluationConfig") -> Dict[str, Any]:
    report_format = (options.report_format or config.report.output or "both").lower()
    if report_format not in {"md", "html", "both"}:
        report_format = "both"

    template_text: Optional[str] = None
    template_source: Optional[str] = None
    if report_format in {"html", "both"}:
        template_text, template_source = select_html_template(options, config)

    return {
        "format": report_format,
        "template_text": template_text,
        "template_source": template_source or "default",
    }


def write_reports(
    summary: Dict[str, Any],
    results: List["TraceOutcome"],
    options: "EvaluationOptions",
    report_plan: Dict[str, Any],
) -> None:
    report_format = report_plan.get("format", "both")
    template_text: Optional[str] = report_plan.get("template_text")

    if report_format in {"md", "both"}:
        write_markdown_report(summary, results, options.output_dir)

    if report_format in {"html", "both"}:
        template_text = template_text or DEFAULT_TEMPLATE
        html_path = options.output_dir / "report.html"
        write_html_report(summary, results, html_path, template_text)


__all__ = ["prepare_report_plan", "write_reports"]

