"""
HTML report generation utilities.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from ..core import TraceOutcome, EvaluationOptions
    from ...config import EvaluationConfig


def serialize_trace_outcome(outcome: "TraceOutcome") -> Dict[str, Any]:
    return {
        "trace_id": outcome.trace.get("trace_id"),
        "iteration": outcome.trace.get("iteration"),
        "persona": outcome.trace.get("persona"),
        "success": outcome.trace.get("success"),
        "duration_ms": outcome.trace.get("duration_ms"),
        "scores": outcome.scores,
        "final_score": outcome.final_score,
        "pass": outcome.passed,
        "reasons": outcome.reasons,
    }


def load_template_from_path(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


DEFAULT_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>[[TITLE]]</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.1/dist/tailwind.min.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
</head>
<body class="bg-slate-950 text-slate-100">
  <main class="max-w-5xl mx-auto p-8 space-y-8">
    <header class="space-y-2">
      <h1 class="text-3xl font-bold">[[TITLE]]</h1>
      <p class="text-sm text-slate-300">Generated at [[DATE]]</p>
    </header>

    <section id="summary" class="grid gap-4"></section>

    <section id="criteria" class="space-y-2"></section>

    <section>
      <canvas id="scoreChart" height="160"></canvas>
    </section>

    <section id="analysis" class="space-y-2"></section>

    <section>
      <details class="bg-slate-900 rounded-lg p-4">
        <summary class="cursor-pointer font-semibold">Per-trace Details</summary>
        <pre class="mt-4 text-xs whitespace-pre-wrap break-words bg-slate-950 rounded p-3 overflow-x-auto" id="per-trace"></pre>
      </details>
    </section>
  </main>

  <script>
    const summary = [[SUMMARY_JSON]];
    const perTrace = [[PER_TRACE_JSON]];
    const criteria = [[CRITERIA_JSON]];
    const analysis = [[ANALYSIS_JSON]];

    function renderSummary() {
      const container = document.getElementById("summary");
      if (!container || !summary) return;
      const items = [
        { label: "Total Traces", value: summary.total_traces ?? "—" },
        { label: "Pass Rate", value: summary.pass_rate != null ? (summary.pass_rate * 100).toFixed(1) + "%" : "—" },
        { label: "Average Score", value: summary.average_score != null ? summary.average_score.toFixed(3) : "—" },
        { label: "Threshold", value: summary.threshold ?? "—" },
      ];
      container.innerHTML = `
        <div class="grid gap-4 md:grid-cols-2">
          ${items
            .map(
              (item) => `
                <div class="bg-slate-900 rounded-xl p-4 border border-slate-800">
                  <p class="text-slate-400 text-xs uppercase tracking-wide">${item.label}</p>
                  <p class="text-2xl font-semibold mt-2">${item.value}</p>
                </div>
              `
            )
            .join("")}
        </div>
      `;
    }

    function renderCriteria() {
      const container = document.getElementById("criteria");
      if (!container || !criteria) return;
      const overall = criteria.overall_success;
      const sections = Object.entries(criteria)
        .filter(([key]) => key !== "overall_success")
        .map(([section, payload]) => [section, Object.entries(payload || {})]);
      if (!sections.length) {
        container.innerHTML = "";
        return;
      }
      container.innerHTML = `
        <h2 class="text-xl font-semibold">Success Criteria</h2>
        ${overall !== undefined ? `<p class="text-sm text-slate-300">Overall success: ${overall ? "✅ Met" : "❌ Not met"}</p>` : ""}
      `;
      for (const [section, checks] of sections) {
        if (!checks.length) continue;
        const sectionTitle = section.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
        const block = document.createElement("div");
        block.className = "bg-slate-900 rounded-xl border border-slate-800 p-4 space-y-2";
        block.innerHTML = `<h3 class="text-lg font-semibold">${sectionTitle}</h3>`;
        const list = document.createElement("ul");
        list.className = "space-y-1 text-sm text-slate-300";
        for (const [name, details] of checks) {
          const prettyName = name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
          const status = details.met === true ? "✅ Met" : details.met === false ? "❌ Not met" : "⚪️ Not evaluated";
          list.innerHTML += `<li>${status} · ${prettyName}</li>`;
        }
        block.appendChild(list);
        container.appendChild(block);
      }
    }

    function renderChart() {
      if (typeof Chart === "undefined" || !Array.isArray(perTrace) || !perTrace.length) {
        return;
      }
      const ctx = document.getElementById("scoreChart");
      if (!ctx) return;
      const labels = perTrace.map((item) => item.trace_id ?? item.iteration ?? "");
      const data = perTrace.map((item) => item.final_score ?? 0);
      new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Final Score",
              data,
              tension: 0.3,
              fill: false,
              borderColor: "#38bdf8",
              backgroundColor: "#38bdf8",
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: { suggestedMin: 0, suggestedMax: 1 },
          },
        },
      });
    }

    function renderAnalysis() {
      const container = document.getElementById("analysis");
      if (!container || !analysis || !Object.keys(analysis).length) return;
      container.innerHTML = "<h2 class='text-xl font-semibold'>Additional Analysis</h2>";
      for (const [key, value] of Object.entries(analysis)) {
        const prettyKey = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
        const block = document.createElement("div");
        block.className = "bg-slate-900 rounded-xl border border-slate-800 p-4";
        block.innerHTML = `
          <h3 class="font-semibold mb-2">${prettyKey}</h3>
          <pre class="text-xs whitespace-pre-wrap break-words">${JSON.stringify(value, null, 2)}</pre>
        `;
        container.appendChild(block);
      }
    }

    function renderPerTrace() {
      const container = document.getElementById("per-trace");
      if (!container) return;
      if (!Array.isArray(perTrace) || !perTrace.length) {
        container.textContent = "No per-trace data available.";
        return;
      }
      container.textContent = JSON.stringify(perTrace, null, 2);
    }

    renderSummary();
    renderCriteria();
    renderChart();
    renderAnalysis();
    renderPerTrace();
  </script>
</body>
</html>
"""


def select_html_template(options: "EvaluationOptions", config: "EvaluationConfig") -> Tuple[str, Optional[str]]:
    if options.report_template:
        template_text = load_template_from_path(options.report_template)
        if template_text:
            return template_text, str(options.report_template)
    template_path = config.report.template_path
    if template_path:
        candidate = Path(template_path)
        if not candidate.is_absolute():
            candidate = (Path.cwd() / candidate).resolve()
        template_text = load_template_from_path(candidate)
        if template_text:
            return template_text, str(candidate)
    return DEFAULT_TEMPLATE, None


def write_html_report(
    summary: Dict[str, Any],
    results: List["TraceOutcome"],
    output_path: Path,
    template_text: str,
) -> None:
    per_trace_payload = [serialize_trace_outcome(result) for result in results]
    success_criteria = summary.get("success_criteria_results") or {}
    analysis = summary.get("analysis") or {}

    replacements = {
        "[[TITLE]]": summary.get("evaluation_goal") or "FluxLoop Evaluation Report",
        "[[DATE]]": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "[[SUMMARY_JSON]]": json.dumps(summary, ensure_ascii=False),
        "[[PER_TRACE_JSON]]": json.dumps(per_trace_payload, ensure_ascii=False),
        "[[CRITERIA_JSON]]": json.dumps(success_criteria, ensure_ascii=False),
        "[[ANALYSIS_JSON]]": json.dumps(analysis, ensure_ascii=False),
    }

    rendered = template_text
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    output_path.write_text(rendered, encoding="utf-8")


__all__ = [
    "DEFAULT_TEMPLATE",
    "serialize_trace_outcome",
    "load_template_from_path",
    "select_html_template",
    "write_html_report",
]

