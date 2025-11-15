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
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
</head>
<body class="bg-slate-950 text-slate-100">
  <main class="max-w-6xl mx-auto p-8 space-y-6">
    <header class="space-y-6">
      <div>
      <h1 class="text-3xl font-bold">[[TITLE]]</h1>
      <p class="text-sm text-slate-300">Generated at [[DATE]]</p>
      </div>
      <nav class="flex flex-wrap gap-2" role="tablist" aria-label="Report sections">
        <button class="tab-button px-4 py-2 rounded-full bg-sky-500/20 border border-sky-400 text-sky-200 font-semibold" data-tab-button="summary">Executive Summary</button>
        <button class="tab-button px-4 py-2 rounded-full bg-slate-800 border border-slate-700" data-tab-button="personas">Persona Insights</button>
        <button class="tab-button px-4 py-2 rounded-full bg-slate-800 border border-slate-700" data-tab-button="analysis">Deep Analysis</button>
        <button class="tab-button px-4 py-2 rounded-full bg-slate-800 border border-slate-700" data-tab-button="traces">Trace Explorer</button>
      </nav>
    </header>

    <section data-tab-panel="summary" class="tab-panel space-y-6">
      <div id="summaryCards" class="grid gap-4 md:grid-cols-2 xl:grid-cols-4"></div>

      <section class="space-y-4">
        <h2 class="text-xl font-semibold">Success Criteria</h2>
        <div id="criteriaList" class="space-y-3"></div>
      </section>

      <section class="space-y-3">
        <div class="flex items-center gap-2">
          <h2 class="text-xl font-semibold">Recommendations</h2>
          <span class="text-xs uppercase tracking-wide text-slate-400">Auto-generated</span>
        </div>
        <div id="recommendations" class="grid gap-4 md:grid-cols-2"></div>
      </section>

      <section class="space-y-3">
        <h2 class="text-xl font-semibold">Score Trend</h2>
        <canvas id="scoreChart" height="200"></canvas>
      </section>

      <section class="space-y-3">
        <h2 class="text-xl font-semibold">Top Failure Reasons</h2>
        <div id="topReasons" class="grid gap-3 md:grid-cols-2"></div>
      </section>
    </section>

    <section data-tab-panel="personas" class="tab-panel hidden space-y-4">
      <p class="text-sm text-slate-300">Compare persona-level performance to target thresholds.</p>
      <div id="personaSummary" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3"></div>
    </section>

    <section data-tab-panel="analysis" class="tab-panel hidden space-y-4">
      <div id="analysisContent" class="space-y-4"></div>
    </section>

    <section data-tab-panel="traces" class="tab-panel hidden space-y-4">
      <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
        <div>
          <label for="tracePersonaFilter" class="block text-sm text-slate-300 font-medium mb-1">Persona filter</label>
          <select id="tracePersonaFilter" class="bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400">
            <option value="all">All personas</option>
          </select>
        </div>
        <p id="traceCountHint" class="text-xs text-slate-400"></p>
      </div>
      <div class="overflow-x-auto border border-slate-800 rounded-lg">
        <table class="min-w-full divide-y divide-slate-800" id="traceTable">
          <thead class="bg-slate-900/60 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-4 py-3 text-left">Trace ID</th>
              <th class="px-4 py-3 text-left">Persona</th>
              <th class="px-4 py-3 text-left">Iteration</th>
              <th class="px-4 py-3 text-left">Final Score</th>
              <th class="px-4 py-3 text-left">Pass</th>
              <th class="px-4 py-3 text-left">Reasons</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-sm text-slate-200"></tbody>
        </table>
      </div>
      <details class="bg-slate-900 rounded-lg p-4 border border-slate-800">
        <summary class="cursor-pointer font-semibold">Raw per-trace payload</summary>
        <pre class="mt-4 text-xs whitespace-pre-wrap break-words bg-slate-950 rounded p-3 overflow-x-auto" id="rawTraceJson"></pre>
      </details>
    </section>
  </main>

  <script>
    const summary = [[SUMMARY_JSON]];
    const perTrace = [[PER_TRACE_JSON]];
    const criteria = [[CRITERIA_JSON]];
    const analysis = [[ANALYSIS_JSON]];

    const state = {
      activeTab: "summary",
      personaFilter: "all",
    };

    function setActiveTab(tab) {
      state.activeTab = tab;
      document.querySelectorAll("[data-tab-panel]").forEach((panel) => {
        panel.classList.toggle("hidden", panel.dataset.tabPanel !== tab);
      });
      document.querySelectorAll("[data-tab-button]").forEach((button) => {
        const isActive = button.dataset.tabButton === tab;
        button.classList.toggle("bg-sky-500/20", isActive);
        button.classList.toggle("text-sky-200", isActive);
        button.classList.toggle("border-sky-400", isActive);
        button.classList.toggle("bg-slate-800", !isActive);
        button.classList.toggle("text-slate-300", !isActive);
        button.classList.toggle("border-slate-700", !isActive);
        button.setAttribute("aria-selected", String(isActive));
      });
    }

    function initTabs() {
      document.querySelectorAll("[data-tab-button]").forEach((button) => {
        button.addEventListener("click", () => {
          setActiveTab(button.dataset.tabButton);
        });
      });
      setActiveTab(state.activeTab);
    }

    function formatPercent(value) {
      if (value == null) return "—";
      return `${(value * 100).toFixed(1)}%`;
    }

    function toTitleCase(value) {
      return (value || "")
        .replace(/_/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());
    }

    function renderSummaryCards() {
      const container = document.getElementById("summaryCards");
      if (!container || !summary) return;
      const cards = [
        { label: "Total Traces", value: summary.total_traces ?? "—" },
        { label: "Pass Rate", value: formatPercent(summary.pass_rate) },
        {
          label: "Average Score",
          value: summary.average_score != null ? summary.average_score.toFixed(3) : "—",
        },
        {
          label: "Threshold",
          value: summary.threshold != null ? summary.threshold.toFixed(2) : "—",
        },
      ];
      if (summary.llm_calls != null) {
        cards.push({
          label: "LLM Calls",
          value: `${summary.llm_calls} (sample ${(summary.llm_sample_rate ?? 0).toFixed(2)})`,
        });
      }
      if (summary.overall_success !== undefined) {
        cards.push({
          label: "Overall Success",
          value: summary.overall_success ? "✅ Met" : "❌ Not Met",
        });
      }
      container.innerHTML = cards
            .map(
          (card) => `
            <div class="bg-slate-900 rounded-xl p-4 border border-slate-800 shadow-inner">
              <p class="text-slate-400 text-xs uppercase tracking-wide">${card.label}</p>
              <p class="text-2xl font-semibold mt-2">${card.value}</p>
                </div>
              `
            )
        .join("");
    }

    function renderCriteria() {
      const container = document.getElementById("criteriaList");
      if (!container || !criteria || !Object.keys(criteria).length) {
        if (container) container.innerHTML = "<p class='text-sm text-slate-400'>No criteria configured.</p>";
        return;
      }
      const overall = criteria.overall_success;
      container.innerHTML = `
        ${
          overall !== undefined
            ? `<p class="text-sm text-slate-300">Overall success: ${
                overall ? "✅ Met" : "❌ Not met"
              }</p>`
            : ""
        }
      `;
      Object.entries(criteria)
        .filter(([key]) => key !== "overall_success")
        .forEach(([section, payload]) => {
          if (!payload) return;
          const checks = Object.entries(payload);
          if (!checks.length) return;
        const sectionTitle = section.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
          const wrapper = document.createElement("div");
          wrapper.className = "bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2";
          wrapper.innerHTML = `<h3 class="text-lg font-semibold">${sectionTitle}</h3>`;
        const list = document.createElement("ul");
        list.className = "space-y-1 text-sm text-slate-300";
        for (const [name, details] of checks) {
            const prettyName = toTitleCase(name);
          const status = details.met === true ? "✅ Met" : details.met === false ? "❌ Not met" : "⚪️ Not evaluated";
            const meta = { ...details };
            delete meta.met;
            const extra =
              Object.keys(meta).length > 0 ? `<span class="text-slate-400"> ${JSON.stringify(meta)}</span>` : "";
            list.innerHTML += `<li>${status} · ${prettyName}${extra}</li>`;
        }
          wrapper.appendChild(list);
          container.appendChild(wrapper);
        });
    }

    function renderRecommendations() {
      const container = document.getElementById("recommendations");
      if (!container) return;
      const recommendations = (analysis && analysis.recommendations) || [];
      if (!recommendations.length) {
        container.innerHTML = "<p class='text-sm text-slate-400'>No blocking action items detected.</p>";
        return;
      }
      container.innerHTML = recommendations
        .map(
          (item) => `
            <article class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2 shadow-inner">
              <div class="flex items-center justify-between gap-2">
                <h3 class="text-lg font-semibold">${item.title}</h3>
                <span class="text-xs px-2 py-1 rounded-full border ${
                  item.priority === "high"
                    ? "border-rose-400 text-rose-300"
                    : item.priority === "medium"
                    ? "border-amber-400 text-amber-300"
                    : "border-slate-500 text-slate-300"
                }">${item.priority?.toUpperCase() || "MEDIUM"}</span>
              </div>
              <p class="text-sm text-slate-300 leading-relaxed">${item.summary || ""}</p>
            </article>
          `
        )
        .join("");
    }

    function renderTopReasons() {
      const container = document.getElementById("topReasons");
      if (!container) return;
      const reasons = summary.top_reasons || [];
      if (!Array.isArray(reasons) || !reasons.length) {
        container.innerHTML = "<p class='text-sm text-slate-400'>No failure reasons recorded.</p>";
        return;
      }
      container.innerHTML = reasons
        .map(
          ([reason, count]) => `
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <p class="text-sm text-slate-300">${reason}</p>
              <p class="mt-2 text-2xl font-semibold">${count}</p>
            </div>
          `
        )
        .join("");
    }

    function renderPersonaSummary() {
      const container = document.getElementById("personaSummary");
      if (!container) return;
      const breakdown = summary.persona_breakdown || {};
      const entries = Object.entries(breakdown);
      if (!entries.length) {
        container.innerHTML = "<p class='text-sm text-slate-400'>Persona breakdown is not available.</p>";
        return;
      }
      container.innerHTML = entries
        .map(
          ([persona, stats]) => `
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold">${persona}</h3>
                <span class="text-xs text-slate-400">n=${stats.count ?? 0}</span>
              </div>
              <p class="text-sm text-slate-300">Pass rate: ${formatPercent(stats.pass_rate)}</p>
              <p class="text-sm text-slate-300">Average score: ${
                stats.average_score != null ? stats.average_score.toFixed(3) : "—"
              }</p>
            </div>
          `
        )
        .join("");
    }

    function renderAnalysisContent() {
      const container = document.getElementById("analysisContent");
      if (!container) return;
      if (!analysis || !Object.keys(analysis).length) {
        container.innerHTML = "<p class='text-sm text-slate-400'>No additional analysis computed.</p>";
        return;
      }
      const entries = Object.entries(analysis).filter(([key]) => key !== "recommendations");
      if (!entries.length) {
        container.innerHTML = "<p class='text-sm text-slate-400'>No additional analysis computed.</p>";
        return;
      }
      container.innerHTML = entries
        .map(
          ([key, value]) => `
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <h3 class="text-lg font-semibold mb-2">${toTitleCase(key)}</h3>
              <pre class="text-xs whitespace-pre-wrap break-words">${JSON.stringify(value, null, 2)}</pre>
            </div>
          `
        )
        .join("");
    }

    function renderScoreChart() {
      if (typeof Chart === "undefined" || !Array.isArray(perTrace) || !perTrace.length) return;
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

    function initTraceFilter() {
      const select = document.getElementById("tracePersonaFilter");
      if (!select) return;
      const personas = Array.from(
        new Set(
          perTrace
            .map((item) => item.persona || "default")
            .filter(Boolean)
        )
      ).sort();
      select.innerHTML = `<option value="all">All personas</option>` + personas.map((p) => `<option value="${p}">${p}</option>`).join("");
      select.value = state.personaFilter;
      select.addEventListener("change", (event) => {
        state.personaFilter = event.target.value;
        renderTraceTable();
      });
      renderTraceTable();
    }

    function renderTraceTable() {
      const table = document.getElementById("traceTable");
      const rawJson = document.getElementById("rawTraceJson");
      if (!table) return;
      const tbody = table.querySelector("tbody");
      const filtered = perTrace.filter((item) => {
        if (state.personaFilter === "all") return true;
        const persona = item.persona || "default";
        return persona === state.personaFilter;
      });
      if (!filtered.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="px-4 py-6 text-center text-sm text-slate-400">No traces match the selected filters.</td></tr>`;
      } else {
        tbody.innerHTML = filtered
          .map(
            (item) => `
              <tr class="hover:bg-slate-900/60">
                <td class="px-4 py-3">${item.trace_id ?? "—"}</td>
                <td class="px-4 py-3">${item.persona ?? "—"}</td>
                <td class="px-4 py-3">${item.iteration ?? "—"}</td>
                <td class="px-4 py-3">${item.final_score != null ? item.final_score.toFixed(3) : "—"}</td>
                <td class="px-4 py-3">${item.pass ? "✅" : "❌"}</td>
                <td class="px-4 py-3">
                  ${
                    item.reasons
                      ? Object.entries(item.reasons)
                          .map(([key, value]) => `<span class="block text-xs text-slate-300">${key}: ${Array.isArray(value) ? value.join(", ") : value}</span>`)
                          .join("")
                      : "<span class='text-xs text-slate-500'>—</span>"
                  }
                </td>
              </tr>
            `
          )
          .join("");
      }
      if (rawJson) {
        rawJson.textContent = JSON.stringify(filtered, null, 2);
      }
      const hint = document.getElementById("traceCountHint");
      if (hint) {
        const total = perTrace.length;
        const shown = filtered.length;
        const suffix = total === 1 ? "" : "s";
        hint.textContent = `${shown} of ${total} trace${suffix} shown`;
    }
    }

    initTabs();
    renderSummaryCards();
    renderCriteria();
    renderRecommendations();
    renderScoreChart();
    renderTopReasons();
    renderPersonaSummary();
    renderAnalysisContent();
    initTraceFilter();
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

