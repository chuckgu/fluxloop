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


FLUXLOOP_LOGO_DATA_URI = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAIRlWElmTU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUA"
    "AAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAABIAAAAAQAAAEgAAAABAAOgAQADAAAAAQABAACgAgAE"
    "AAAAAQAAABigAwAEAAAAAQAAABgAAAAAEQ8YrgAAAAlwSFlzAAALEwAACxMBAJqcGAAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4"
    "OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDYuMC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRm"
    "PSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9"
    "IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRh"
    "dGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KGV7h"
    "BwAABlJJREFUSA2VVQtwlFcVPvf+99/9N9lHsnlsaCAh4VEmkKAmhqZMcKmTzuAA6jhbYXA6RpxAHWxt61jHQbtapY8o1VHbxk6xltJaGK1a"
    "rDC1Ztu0IzAkpSVmAIEAee5uNg92N/v4/3uP9266gdpSxzOze+8959zvO/ec+58L8L8k2M0g8C8bBJHOuwZQWyl1ATnO6/7vyUG5+XrQGwAE"
    "Agc19buBGchHGrpQhx3EVLaF7efWmIJswYxoBhOdxORx3cSMkRWnjKz5u/6exveUX2PjSb23tym3R63z8mGCIDIIEqvyvuHlPGu9iOD+FM7E"
    "YpDlo2hBnYaGxpLxw4aJixxQuJpl4iGXSb725onVg35/NwuF1lt5cDVey6tavQ/u+8GVL1su91kOJAkzk/WR/ctKIy+taPCaE8WEpw4QRhs0"
    "K/VFkp6sJwg1nBkX/c0nv6DAFYmCysu1E7yfFt8jI5sQHX+BmcRDbiPz09kULaLZcHT48VtT+U1LNvRf1rO84Mzrq8uUbm1L35tOWtYK6dGN"
    "R3vX/PX6dM2dQBVT5rzm6bAPbfQlxFQUHcR/lXtmuF5xOZOtmPVtP//Q0qWv2hWggfy7Tkdl6afX9W5Ta4fGvyrMGOio/WnLqjcWqVrkC59P"
    "UW5MIvwQKiocqNExpOQ1IszNIhNrlxhv0ZIluxMttfsVoKBkhIoUMMQqtaYFtrCG5tsGaEyjtkeULhoty2VHFlRGL4ta80LYFzfZDpgOv119"
    "YWR9728+cCOerWg/u0tzLf5l+bb+tUYkS5jDAZSSmAKDdMZLCCmjIv2YAfSeu+p7vv9kqPViEJAyqBtQRcnOIm4EpwtIZnqXAvd1jpdzindi"
    "0myjs9wiafMZnBgcsAvawZmGAtOgJZKvKHxqadsZxSWMiCcMQnbqoG2W6p/DygFGYaoOlZNgpFWkpsaiHeWnyg5ElpkeOE0qKjophWaOxGdx"
    "8rywQ5Uu+CbQyBYrE9va07tu7LbWk18v1MseZIK//MI7ay8XAo47EZsU5qiRkukZC+UIZLSLkOIZZcgAhoSdldPYlc3R3VXFVZVjv3IXJTTd"
    "zp023V6sExx2CNF427q+syWs6mmeGj/nAtip9roFT7tBlKj5Ta64JPiMX80BCRKi4WTx78PbiMd7U5FIfzJ8d/Urm549em+p2/bbYiP5TqUt"
    "gR6YiVHOB3UhvlXIuQeTg4+tSEVuee7EmlhjY5fuEbDExTGRA5V/DKIDuRtECP5bUjRxEF9xJCIHLrUvPHXXHw7XMmLtnb46+FS1aYukHLoT"
    "U66FDoF/2/eP1rY8SH7clVxxv9dWUTiVHT6tdHXRqCxy7VwNGIOjWQHtlONECbHuCUuHpTDU5pKFH8Whzkr0PgA2K35yov7RFcU1P3u4uafJ"
    "za0nspSNOlMZpxO1ewWKQNoKgwHZY4pgyqiVKWqEXO8ocGdepZoIa273giL11UippeHK5bMDEKweHGomfe9+zjh3S7Bl3YsTF4bvX+xwby1n"
    "pT0LOL2w2OF7l1C+uoBYR2xkdozWT7+u9u/obbIoyNxAN7JL62vSRON7tNJCsDSRuwUL+ESsjp6H4TPnfA2xrudL+T/BIC1//Mnplr1b32jw"
    "oDX0DR3ie4YmJz+7wLjy+SJj9ksFLNV5x6E7eJesh+TIXSA54HxPKvnzxWMNRy4pUic+B4X8cBsm9q38jorI/HHlffiL5Zh64BNn8XuwSumU"
    "4Deh7L22zsnjtz7Tl1sDyKjnMOdaRe4Uc10wpmkb4iI+viEVmiKL+wpg4rVvMyv7I+z0leu7R/bCdOROnUV8yFednr27+cTU9tuP8/iuiN2Y"
    "SHv5kF8RQOAgJYpDSr4XAayXfbxbkmysnhr0GjcbItn3KO+PHHHurJQtuh9tpAf3lKwhD07v18zRRYIOdTB9xF3kTTRPmVf+7iVv3bzsePBq"
    "tz/IiEyRAlcyn5q5JYBfkoQUmZTHX364ozE9EKxL9haX0HEDMhwwZqUxK98Ji9p5xj5spj2dhb8+v0/5owIPBT/w4HyIQDmCfI8xAEI2sNwx"
    "J59cudaTHm+g2Wy1kO8A5TRipbVj7MJMNzkEuWgxENDIoUPzkedwPvZPFr6rq0PdhI8VDPqZjOKjA5U7b2i4HlWBAISu1WvOKEhw7hu63ve/"
    "5/8B6E/qF9KU55kAAAAASUVORK5CYII="
)


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
        "conversation": outcome.trace.get("conversation"),
        "conversation_state": outcome.trace.get("conversation_state"),
        "termination_reason": outcome.trace.get("termination_reason"),
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
  <meta name="report:generated_at" content="[[DATE]]" />
  <title>[[TITLE]]</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
</head>
<body class="bg-slate-950 text-slate-100">
  <main class="max-w-6xl mx-auto p-8 space-y-6">
    <header class="space-y-6">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="flex items-center gap-3">
          <img src="[[LOGO_DATA_URI]]" alt="FluxLoop logo" class="h-12 w-12 rounded-full border border-sky-400/40 bg-slate-900/80 p-1.5 shadow-md shadow-sky-900/60" />
      <div>
      <h1 class="text-3xl font-bold">[[TITLE]]</h1>
            <p class="text-sm text-slate-300">[[SUBTITLE]]</p>
          </div>
        </div>
        <a
          href="https://fluxloop.ai/"
          class="inline-flex items-center gap-2 self-start rounded-full border border-sky-400 px-4 py-2 text-sm font-semibold text-sky-200 transition hover:bg-sky-500/10 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:ring-offset-2 focus:ring-offset-slate-950"
          target="_blank"
          rel="noopener noreferrer"
        >
          <img src="[[LOGO_DATA_URI]]" alt="" aria-hidden="true" class="h-5 w-5 rounded-full border border-sky-400/50 bg-slate-950/70 p-0.5" />
          <span>Built with FluxLoop</span>
        </a>
      </div>
      <nav class="flex flex-wrap gap-2" role="tablist" aria-label="Report sections">
        <button class="tab-button px-4 py-2 rounded-full bg-sky-500/20 border border-sky-400 text-sky-200 font-semibold" data-tab-button="summary">Executive Summary</button>
        <button class="tab-button px-4 py-2 rounded-full bg-slate-800 border border-slate-700" data-tab-button="personas">Persona Insights</button>
        <button class="tab-button px-4 py-2 rounded-full bg-slate-800 border border-slate-700" data-tab-button="analysis">Deep Analysis</button>
        <button class="tab-button px-4 py-2 rounded-full bg-slate-800 border border-slate-700" data-tab-button="conversation">Conversation View</button>
        <button class="tab-button px-4 py-2 rounded-full bg-slate-800 border border-slate-700" data-tab-button="traces">Trace Explorer</button>
      </nav>
    </header>

    <section data-tab-panel="summary" class="tab-panel space-y-6">
      <div id="summaryCards" class="grid gap-4 md:grid-cols-2 xl:grid-cols-4"></div>

      <section class="space-y-4">
        <h2 class="text-xl font-semibold">Evaluation Goal</h2>
        <div id="evaluationGoal" class="whitespace-pre-wrap rounded-xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300"></div>
      </section>

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

    <section data-tab-panel="conversation" class="tab-panel hidden space-y-4">
      <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div class="w-full md:w-1/2">
          <label for="conversationTraceSelect" class="block text-sm text-slate-300 font-medium mb-1">Select Trace</label>
          <select id="conversationTraceSelect" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400">
            <option value="">Choose a trace</option>
          </select>
        </div>
        <div class="text-xs text-slate-400">
          Messages are ordered chronologically. Expand each turn to view captured actions.
        </div>
      </div>
      <div id="conversationSummary" class="text-sm text-slate-300"></div>
      <div id="conversationTimeline" class="space-y-3"></div>
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
      conversationTraceId: (Array.isArray(perTrace) && perTrace.length > 0 && (perTrace[0].trace_id ?? perTrace[0].iteration ?? null)) || null,
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

    function initConversationSelect() {
      const select = document.getElementById("conversationTraceSelect");
      if (!select) return;
      const options = Array.isArray(perTrace) ? perTrace : [];
      if (!options.length) {
        select.innerHTML = `<option value="">No traces available</option>`;
        select.disabled = true;
        return;
      }
      select.innerHTML = options
        .map((trace) => {
          const label = trace.trace_id || `Iteration ${trace.iteration ?? ""}` || "Trace";
          const value = trace.trace_id || `iteration-${trace.iteration ?? 0}`;
          return `<option value="${value}">${label}</option>`;
        })
        .join("");
      if (state.conversationTraceId) {
        select.value = state.conversationTraceId;
      } else {
        state.conversationTraceId = options[0].trace_id || `iteration-${options[0].iteration ?? 0}`;
        select.value = state.conversationTraceId;
      }
      select.addEventListener("change", (event) => {
        state.conversationTraceId = event.target.value || null;
        renderConversationTimeline();
      });
      renderConversationTimeline();
    }

    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, (char) => {
        switch (char) {
          case "&":
            return "&amp;";
          case "<":
            return "&lt;";
          case ">":
            return "&gt;";
          case '"':
            return "&quot;";
          case "'":
            return "&#39;";
          default:
            return char;
        }
      });
    }

    function formatPlainText(value) {
      return escapeHtml(value || "").replace(/\n/g, "<br>");
    }

    function tryParseJson(text) {
      if (typeof text !== "string") return text;
      const trimmed = text.trim();
      if (
        !trimmed ||
        ((trimmed.startsWith("{") && trimmed.endsWith("}")) ||
          (trimmed.startsWith("[") && trimmed.endsWith("]"))) === false
      ) {
        return text;
      }
      try {
        return JSON.parse(trimmed);
      } catch (error) {
        return text;
      }
    }

    function renderTranscriptObject(obj) {
      const transcript = Array.isArray(obj.transcript) ? obj.transcript : [];
      if (!transcript.length) {
        return `
          <pre class="mt-3 bg-slate-900/70 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 whitespace-pre-wrap">${escapeHtml(JSON.stringify(obj, null, 2))}</pre>
        `;
      }
      const threadId = obj.thread_id ? `<p class="text-xs text-slate-400">Thread: ${escapeHtml(obj.thread_id)}</p>` : "";
      const provider = obj.provider ? `<p class="text-xs text-slate-400">Provider: ${escapeHtml(obj.provider)}</p>` : "";
      const exchanges = transcript
        .map((turn, index) => {
          const user = turn.user
            ? `<p class="text-sm text-slate-200"><span class="font-semibold">Human:</span> ${formatPlainText(turn.user)}</p>`
            : "";
          const assistant = turn.assistant
            ? `<p class="text-sm text-sky-200 mt-2"><span class="font-semibold">AI:</span> ${formatPlainText(
                turn.assistant
              )}</p>`
            : "";
          return `
            <div class="rounded-lg border border-slate-800 bg-slate-900/70 p-3 space-y-2">
              <p class="text-xs text-slate-400 uppercase tracking-wide">Exchange ${index + 1}</p>
              ${user}
              ${assistant}
            </div>
          `;
        })
        .join("");
      return `
        <div class="mt-3 space-y-3">
          ${threadId}
          ${provider}
          <div class="space-y-3">${exchanges}</div>
        </div>
      `;
    }

    function formatConversationContent(rawContent) {
      if (rawContent == null) return "";
      let value = rawContent;
      if (typeof value === "string") {
        value = tryParseJson(value);
      }
      if (typeof value === "string") {
        return `<p class="text-sm text-slate-200 whitespace-pre-wrap">${formatPlainText(value)}</p>`;
      }
      if (Array.isArray(value)) {
        return `
          <pre class="mt-3 bg-slate-900/70 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 whitespace-pre-wrap">${escapeHtml(
            JSON.stringify(value, null, 2)
          )}</pre>
        `;
      }
      if (typeof value === "object") {
        if (value && Array.isArray(value.transcript)) {
          return renderTranscriptObject(value);
        }
        return `
          <pre class="mt-3 bg-slate-900/70 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 whitespace-pre-wrap">${escapeHtml(
            JSON.stringify(value, null, 2)
          )}</pre>
        `;
      }
      return `<p class="text-sm text-slate-200">${escapeHtml(String(value))}</p>`;
    }

    function formatTraceSummary(trace) {
      if (!trace) return "";
      const parts = [];
      if (trace.trace_id) parts.push(`Trace ID: ${trace.trace_id}`);
      if (trace.iteration != null) parts.push(`Iteration: ${trace.iteration}`);
      if (trace.persona) parts.push(`Persona: ${trace.persona}`);
      const termination = trace.termination_reason;
      if (termination) parts.push(`Termination: ${termination}`);
      return parts.join(" · ");
    }

    function renderConversationTimeline() {
      const container = document.getElementById("conversationTimeline");
      const summaryEl = document.getElementById("conversationSummary");
      if (!container) return;
      container.innerHTML = "";
      if (!Array.isArray(perTrace) || !perTrace.length || !state.conversationTraceId) {
        if (summaryEl) summaryEl.textContent = "No conversation data available.";
        return;
      }
      const trace = perTrace.find(
        (item) =>
          item.trace_id === state.conversationTraceId ||
          `iteration-${item.iteration ?? 0}` === state.conversationTraceId
      );
      if (!trace) {
        if (summaryEl) summaryEl.textContent = "Conversation data not found for the selected trace.";
        return;
      }
      if (summaryEl) {
        summaryEl.textContent = formatTraceSummary(trace);
      }
      const conversation = Array.isArray(trace.conversation) ? trace.conversation : [];
      if (!conversation.length) {
        container.innerHTML = `<p class="text-sm text-slate-400">No conversation recorded for this trace.</p>`;
        return;
      }
      conversation.forEach((entry, index) => {
        const role = entry.role || "unknown";
        const isAssistant = role === "assistant";
        const isUser = role === "user";
        const bubbleClasses = [
          "rounded-xl",
          "p-4",
          "border",
          "shadow-inner",
          isAssistant ? "bg-sky-500/10 border-sky-400/40" : "bg-slate-900 border-slate-800",
        ].join(" ");
        const roleLabel = isAssistant ? "AI" : isUser ? "Human" : role.toUpperCase();
        const source = entry.source ? `<span class="text-xs uppercase tracking-wide text-slate-400">${escapeHtml(entry.source)}</span>` : "";
        const metadata = entry.metadata || {};
        const actions = Array.isArray(metadata.actions) ? metadata.actions.map((action) => escapeHtml(action)) : [];
        const closing = metadata.closing ? " • Closing turn" : "";
        const persona = metadata.persona ? ` • Persona: ${escapeHtml(metadata.persona)}` : "";
        const detailLabel = actions.length ? actions.join(", ") : "No recorded actions for this turn.";
        const detailContent = actions.length
          ? actions.map((item) => `<li>${item}</li>`).join("")
          : "";
        const formattedContent = formatConversationContent(entry.content);
        const detailsMarkup = `
          <details class="mt-3 bg-slate-900/60 border border-slate-800 rounded-lg">
            <summary class="cursor-pointer text-xs text-slate-300 px-3 py-2">Turn details</summary>
            <div class="px-4 py-3 text-xs text-slate-300">
              <p>${detailLabel}</p>
              ${actions.length ? `<ul class="list-disc list-inside mt-2 space-y-1 text-slate-400">${detailContent}</ul>` : ""}
            </div>
          </details>
        `;
        container.innerHTML += `
          <article class="${bubbleClasses}">
            <header class="flex items-center justify-between gap-2 mb-2">
              <div class="flex items-center gap-2">
                <span class="text-sm font-semibold">${roleLabel}</span>
                ${source}
              </div>
              <span class="text-xs text-slate-400">Turn ${entry.turn_index ?? index + 1}${closing}${persona}</span>
            </header>
            ${formattedContent}
            ${detailsMarkup}
          </article>
        `;
      });
    }

    function renderEvaluationGoal() {
      const container = document.getElementById("evaluationGoal");
      if (!container) return;
      const goal = summary?.evaluation_goal;
      if (!goal) {
        container.textContent = "No evaluation goal provided.";
        container.classList.remove("text-slate-300");
        container.classList.add("text-slate-400");
        return;
      }
      container.classList.remove("text-slate-400");
      container.classList.add("text-slate-300");
      container.textContent = goal;
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
    renderEvaluationGoal();
    renderCriteria();
    renderRecommendations();
    renderScoreChart();
    renderTopReasons();
    renderPersonaSummary();
    renderAnalysisContent();
    initConversationSelect();
    initTraceFilter();
  </script>
</body>
</html>
"""


def _resolve_experiment_label(summary: Dict[str, Any], output_path: Path) -> Optional[str]:
    def _stringify(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, (list, tuple, set)):
            parts = [str(item) for item in value if item not in (None, "")]
            if not parts:
                return None
            return ", ".join(parts)
        if isinstance(value, str):
            return value.strip() or None
        return str(value)

    for key in ("experiment_id", "experiment_name"):
        candidate = _stringify(summary.get(key))
        if candidate:
            return candidate

    experiment_meta = summary.get("experiment")
    if isinstance(experiment_meta, dict):
        for key in ("name", "id", "label"):
            candidate = _stringify(experiment_meta.get(key))
            if candidate:
                return candidate

    output_dir = output_path.parent
    if output_dir != output_path:
        experiment_dir = output_dir.parent
        if experiment_dir and experiment_dir != output_dir:
            candidate = _stringify(experiment_dir.name)
            if candidate:
                return candidate
        candidate = _stringify(output_dir.name)
        if candidate:
            return candidate

    return None


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

    generated_at = datetime.now(UTC)
    generated_iso = generated_at.isoformat(timespec="seconds").replace("+00:00", "Z")
    human_readable = generated_at.strftime("%Y-%m-%d %H:%M:%SZ")
    experiment_label = _resolve_experiment_label(summary, output_path)
    subtitle_parts = [f"Generated on {human_readable}"]
    if experiment_label:
        subtitle_parts.append(f"Experiment: {experiment_label}")
    subtitle = " · ".join(subtitle_parts)

    replacements = {
        "[[TITLE]]": "FluxLoop Evaluation Report",
        "[[DATE]]": generated_iso,
        "[[SUBTITLE]]": subtitle,
        "[[LOGO_DATA_URI]]": FLUXLOOP_LOGO_DATA_URI,
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
    "FLUXLOOP_LOGO_DATA_URI",
    "serialize_trace_outcome",
    "load_template_from_path",
    "select_html_template",
    "write_html_report",
]

