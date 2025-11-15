"""
Markdown report generation utilities.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from ..core import TraceOutcome


def write_markdown_report(summary: Dict[str, Any], results: List["TraceOutcome"], output_dir: Path) -> None:
    lines: List[str] = []
    lines.append("# Evaluation Summary\n")
    lines.append(f"- Total traces: {summary['total_traces']}")
    lines.append(f"- Passed traces: {summary['passed_traces']}")
    lines.append(f"- Pass rate: {summary['pass_rate'] * 100:.1f}% (threshold {summary['threshold']})")
    lines.append(f"- Average score: {summary['average_score']:.3f}")
    if "llm_calls" in summary:
        lines.append(f"- LLM calls: {summary['llm_calls']} (sample rate {summary.get('llm_sample_rate', 0):.2f})")
    overall_success = summary.get("overall_success")
    if overall_success is not None:
        icon = "✅" if overall_success else "❌"
        status_text = "met" if overall_success else "not met"
        lines.append(f"- Overall success: {icon} ({status_text})")
    lines.append("")

    goal = summary.get("evaluation_goal")
    if goal:
        lines.append("## Evaluation Goal\n")
        lines.append(str(goal).strip())
        lines.append("")

    success_results = summary.get("success_criteria_results")
    if isinstance(success_results, dict):
        sections = {
            name: payload
            for name, payload in success_results.items()
            if name != "overall_success" and payload
        }
        if sections:
            lines.append("## Success Criteria\n")
            for section_name, checks in sections.items():
                if not checks:
                    continue
                pretty_section = section_name.replace("_", " ").title()
                lines.append(f"### {pretty_section}")
                for check_name, payload in checks.items():
                    status = payload.get("met")
                    if status is True:
                        status_label = "Met"
                        icon = "✅"
                    elif status is False:
                        status_label = "Not met"
                        icon = "❌"
                    else:
                        status_label = "Not evaluated"
                        icon = "⚪️"
                    pretty_check = check_name.replace("_", " ").title()
                    detail_payload = {
                        key: value
                        for key, value in payload.items()
                        if key != "met" and value is not None
                    }
                    if detail_payload:
                        detail_str = json.dumps(detail_payload, ensure_ascii=False)
                        lines.append(f"- {icon} {pretty_check}: {status_label} {detail_str}")
                    else:
                        lines.append(f"- {icon} {pretty_check}: {status_label}")
                lines.append("")

    analysis = summary.get("analysis")
    if isinstance(analysis, dict) and analysis:
        lines.append("## Additional Analysis\n")
        persona_analysis = analysis.get("persona")
        if isinstance(persona_analysis, dict) and persona_analysis.get("breakdown"):
            lines.append("### Persona")
            focus = persona_analysis.get("focus_personas")
            if focus:
                lines.append(f"- Focus personas: {', '.join(focus)}")
            breakdown = persona_analysis.get("breakdown", {})
            for persona, stats in breakdown.items():
                lines.append(f"- {persona}: {json.dumps(stats, ensure_ascii=False)}")
            lines.append("")

        performance_analysis = analysis.get("performance")
        if isinstance(performance_analysis, dict):
            lines.append("### Performance")
            outliers = performance_analysis.get("outliers")
            if isinstance(outliers, dict):
                for metric, entries in outliers.items():
                    if entries:
                        lines.append(f"- Outliers detected for {metric}: {json.dumps(entries, ensure_ascii=False)}")
            trends = performance_analysis.get("trends")
            if isinstance(trends, dict):
                for metric, data in trends.items():
                    lines.append(f"- Trend for {metric}: {json.dumps(data, ensure_ascii=False)}")
            lines.append("")

        failures_analysis = analysis.get("failures")
        if isinstance(failures_analysis, dict):
            lines.append("### Failures")
            top_reasons = failures_analysis.get("top_reasons")
            if top_reasons:
                lines.append(f"- Top reasons: {json.dumps(top_reasons, ensure_ascii=False)}")
            categorized = failures_analysis.get("categorized")
            if categorized:
                lines.append(f"- Categorized counts: {json.dumps(categorized, ensure_ascii=False)}")
            lines.append("")

        comparison_analysis = analysis.get("comparison")
        if isinstance(comparison_analysis, dict) and comparison_analysis:
            lines.append("### Comparison")
            if "message" in comparison_analysis:
                lines.append(f"- {comparison_analysis['message']}")
            else:
                for key, value in comparison_analysis.items():
                    if key == "baseline_path":
                        lines.append(f"- Baseline: {value}")
                        continue
                    lines.append(f"- {key}: {json.dumps(value, ensure_ascii=False)}")
            lines.append("")

        recommendations = analysis.get("recommendations")
        if recommendations:
            lines.append("### Recommendations")
            for recommendation in recommendations:
                title = recommendation.get("title", "Recommendation")
                priority = recommendation.get("priority", "medium").title()
                summary_text = recommendation.get("summary", "")
                lines.append(f"- **{title}** ({priority}): {summary_text}")
            lines.append("")

    lines.append("## Evaluator Stats\n")
    lines.append("| Evaluator | Avg | Min | Max | Count |")
    lines.append("|-----------|-----|-----|-----|-------|")
    for name, stats in summary["evaluator_stats"].items():
        lines.append(
            f"| {name} | {stats['average']:.3f} | {stats['min']:.3f} | "
            f"{stats['max']:.3f} | {stats['count']} |"
        )
    lines.append("")

    if summary.get("persona_breakdown"):
        lines.append("## Persona Breakdown\n")
        for persona, stats in summary["persona_breakdown"].items():
            lines.append(f"### {persona}")
            lines.append(f"- Count: {stats['count']}")
            lines.append(f"- Average score: {stats['average_score']:.3f}")
            lines.append(f"- Pass rate: {stats['pass_rate'] * 100:.1f}%")
            lines.append("")

    if summary.get("top_reasons"):
        lines.append("## Top Failure Reasons\n")
        for reason, count in summary["top_reasons"]:
            lines.append(f"- {reason} ({count})")
        lines.append("")

    (output_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


__all__ = ["write_markdown_report"]

