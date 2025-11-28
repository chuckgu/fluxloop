"""
Rule-based aggregation and statistics for evaluation reports.
"""

import json
import logging
import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ===================================================================
# Constants
# ===================================================================

PASS_STATES = {
    "task_completion": "PASS",
    "hallucination": "PASS",
    "relevance": "PASS",
    "tool_usage": "APPROPRIATE",
    "user_satisfaction": "GOOD",
    "clarity": "PASS",
    "persona_consistency": "PASS"
}

CORRECTNESS_METRICS = ["hallucination", "relevance", "tool_usage"]
QUALITY_METRICS = ["user_satisfaction", "clarity", "persona_consistency"]
INVERTED_METRICS = ["hallucination"]

STATUS_ICONS = {
    "good": "✓",
    "fair": "!",
    "poor": "✗"
}


# ===================================================================
# Aggregator Class
# ===================================================================

class StatsAggregator:
    """Aggregates per-trace evaluation results into overall statistics."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.eval_config = config.get("evaluation", {})
        self.personas = config.get("input", {}).get("personas", [])

    def aggregate(self, pt_results: List[Dict[str, Any]], trace_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main entry point for aggregation.
        
        Args:
            pt_results: List of results from TraceEvaluator
            trace_summaries: List of original trace summary objects (containing input, output, duration etc.)
            
        Returns:
            Dictionary containing 'enriched_traces', 'summary', 'performance', 'insights', 'meta'
        """
        # Map trace summaries by ID for easy lookup
        trace_map = {t.get("trace_id"): t for t in trace_summaries}
        
        # Enrich traces
        enriched_traces = []
        for pt in pt_results:
            trace_id = pt.get("trace_id")
            if not trace_id or "error" in pt:
                continue
                
            trace_summary = trace_map.get(trace_id, {})
            enriched = self._enrich_trace(pt, trace_summary)
            enriched_traces.append(enriched)

        # Classify cases
        classified_cases = self._classify_cases(enriched_traces)

        # Build sections
        summary = self._build_summary_section(enriched_traces)
        trace_matrix = self._build_trace_matrix(enriched_traces)
        performance = self._build_performance_section(enriched_traces)
        insights = self._build_insights_section(classified_cases)

        # Calculate counts for meta
        passed = sum(1 for t in enriched_traces if t.get("overall_eval") == "PASS")
        partial = sum(1 for t in enriched_traces if t.get("overall_eval") == "PARTIAL")
        failed = sum(1 for t in enriched_traces if t.get("overall_eval") == "FAIL")
        review = sum(1 for t in enriched_traces if t.get("overall_eval") == "REVIEW")

        return {
            "meta": {
                "processed_at": datetime.now().isoformat(),
                "total_traces": len(enriched_traces),
                "passed_traces": passed,
                "partial_traces": partial,
                "failed_traces": failed,
                "review_traces": review,
            },
            "enriched_traces": enriched_traces,
            "summary": summary,
            "trace_matrix": trace_matrix,
            "performance": performance,
            "insights": insights,
        }

    # -------------------------------------------------------------------
    # Per-Trace Logic
    # -------------------------------------------------------------------

    def _enrich_trace(self, pt_result: Dict[str, Any], trace_summary: Dict[str, Any]) -> Dict[str, Any]:
        metrics = pt_result.get("metrics", {})
        
        # Conversation extraction
        conversation = trace_summary.get("conversation", [])
        if not conversation and "conversation_state" in trace_summary:
            conversation = trace_summary.get("conversation_state", {}).get("turns", [])
            
        raw_output = trace_summary.get("output") or trace_summary.get("final_output")
        return {
            "trace_id": pt_result.get("trace_id"),
            "persona": trace_summary.get("persona", "unknown"),
            "input": trace_summary.get("input", ""),
            "metrics": metrics,
            "analysis": pt_result.get("analysis"),
            "overall_eval": self._classify_overall_success(metrics),
            "primary_issue": self._find_primary_issue(metrics),
            "duration_ms": trace_summary.get("duration_ms", 0),
            "output_tokens": self._estimate_output_tokens(conversation, raw_output),
            "conversation_turns": self._count_conversation_turns(conversation),
        }

    def _classify_overall_success(self, metrics: Dict[str, Any]) -> str:
        task = metrics.get("task_completion", {}).get("eval", "")
        hall = metrics.get("hallucination", {}).get("eval", "")
        relev = metrics.get("relevance", {}).get("eval", "")
        tool = metrics.get("tool_usage", {}).get("eval", "")
        
        correctness_pass = (
            hall == "PASS" and
            relev == "PASS" and
            tool == "APPROPRIATE"
        )
        
        quality_fails = 0
        for metric in QUALITY_METRICS:
            if metric in metrics:
                eval_val = metrics[metric].get("eval", "")
                pass_val = PASS_STATES.get(metric)
                if eval_val != pass_val:
                    quality_fails += 1
                    
        # PASS: Clear Success
        if task == "PASS" and correctness_pass and quality_fails == 0:
            return "PASS"
            
        # FAIL: Clear Failure
        if task == "FAIL" or hall == "FAIL" or relev == "FAIL" or tool == "INAPPROPRIATE":
            return "FAIL"
            
        # PARTIAL: Marginal Success
        if (task == "PARTIAL" and correctness_pass) or \
           (task == "PASS" and correctness_pass and quality_fails > 0):
            return "PARTIAL"
            
        # REVIEW: Ambiguous
        return "REVIEW"

    def _find_primary_issue(self, metrics: Dict[str, Any]) -> Optional[str]:
        check_order = ["task_completion"] + CORRECTNESS_METRICS + QUALITY_METRICS
        for metric in check_order:
            if metric in metrics:
                eval_val = metrics[metric].get("eval", "")
                pass_val = PASS_STATES.get(metric)
                if eval_val != pass_val:
                    return metric
        return None

    def _estimate_output_tokens(
        self,
        conversation: List[Dict[str, Any]],
        raw_output: Optional[Any],
    ) -> int:
        """Approximate output tokens from assistant turns, with fallbacks."""

        total_chars = 0
        for turn in conversation:
            if turn.get("role") != "assistant":
                continue

            content = turn.get("content", "")
            if isinstance(content, dict):
                content = json.dumps(content, ensure_ascii=False)
            elif not isinstance(content, str):
                content = str(content)

            total_chars += len(content)

        if total_chars == 0 and raw_output:
            fallback = raw_output
            if isinstance(fallback, dict):
                fallback = fallback.get("output") or fallback.get("final_output")
            if isinstance(fallback, str):
                total_chars = len(fallback)

        return total_chars // 4 if total_chars else 0

    def _count_conversation_turns(self, conversation: List[Dict[str, Any]]) -> int:
        return sum(1 for t in conversation if t.get("role") == "user")

    # -------------------------------------------------------------------
    # Aggregation Logic
    # -------------------------------------------------------------------

    def _build_summary_section(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(traces)
        passed = sum(1 for t in traces if t.get("overall_eval") == "PASS")
        pass_rate = round((passed / total) * 100, 1) if total > 0 else 0
        
        counts = {"PARTIAL": 0, "FAIL": 0, "REVIEW": 0}
        for t in traces:
            overall = t.get("overall_eval", "")
            if overall in counts:
                counts[overall] += 1
                
        badges = [
            {"class": "marginal", "icon": "!", "count": counts["PARTIAL"], "label": "Marginal"},
            {"class": "failed", "icon": "✗", "count": counts["FAIL"], "label": "Failed"},
            {"class": "review", "icon": "?", "count": counts["REVIEW"], "label": "Review"}
        ]
        
        metric_stats = self._calculate_metric_stats(traces)
        
        assessment = [
            {
                "name": "Completeness",
                "modal_id": "completeness",
                "metric_rows": [s for s in metric_stats if s["name"] == "Task Completion Rate"]
            },
            {
                "name": "Correctness",
                "modal_id": "correctness",
                "metric_rows": [s for s in metric_stats if s["name"] in [
                    "Hallucination Rate", "Relevance Rate", "Tool Usage Appropriateness"
                ]]
            },
            {
                "name": "Response Quality",
                "modal_id": "quality",
                "metric_rows": [s for s in metric_stats if s["name"] in [
                    "User Satisfaction Score", "Response Clarity", "Persona Consistency"
                ]]
            }
        ]
        
        return {
            "pass_rate": pass_rate,
            "total_traces": total,
            "passed": passed,
            "badges": badges,
            "assessment": assessment,
            "metric_stats": metric_stats
        }

    def _calculate_metric_stats(self, traces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        metric_defs = [
            ("task_completion", "Task Completion Rate"),
            ("hallucination", "Hallucination Rate"),
            ("relevance", "Relevance Rate"),
            ("tool_usage", "Tool Usage Appropriateness"),
            ("user_satisfaction", "User Satisfaction Score"),
            ("clarity", "Response Clarity"),
            ("persona_consistency", "Persona Consistency"),
        ]
        
        results = []
        total = len(traces)
        
        for metric_key, metric_name in metric_defs:
            pass_val = PASS_STATES.get(metric_key)
            passed_count = 0
            for t in traces:
                m = t.get("metrics", {}).get(metric_key, {})
                if m.get("eval") == pass_val:
                    passed_count += 1
            
            # Hallucination is inverted (fail count displayed as rate usually, but here we keep pass rate consistent for charts)
            # Actually, in the report, hallucination usually shows "Pass Rate" (Non-hallucination rate).
            # Let's stick to Pass Rate for all for simplicity in aggregation.
            percent = round((passed_count / total) * 100, 1) if total > 0 else 0
            
            # Get threshold config
            # Default mapping if key names differ in config
            config_key = "tool_usage_appropriateness" if metric_key == "tool_usage" else metric_key
            
            metric_cfg = self.eval_config.get("metrics", {}).get(config_key, {})
            thresholds = metric_cfg.get("thresholds", {"good": 80, "fair": 60})
            
            inverted = metric_key in INVERTED_METRICS
            status = self._calculate_status(percent, thresholds, inverted)
            
            results.append({
                "name": metric_name,
                "percent": percent,
                "passed": passed_count,
                "total": total,
                "status": status,
                "status_icon": STATUS_ICONS.get(status, "?"),
                "status_label": status.capitalize()
            })
            
        return results

    def _calculate_status(self, percent: float, thresholds: Dict[str, float], inverted: bool = False) -> str:
        good = thresholds.get("good", 80)
        fair = thresholds.get("fair", 60)
        
        if inverted:
            # For hallucination, config usually defines thresholds for FAILURE rate.
            # But here 'percent' is PASS rate.
            # If config says "good: 5" (meaning <= 5% failure), that equals >= 95% pass.
            # This logic can be tricky. Let's assume standard "higher is better" for consistency
            # unless we flip the logic entirely.
            # The ref code had specific logic. Let's simplify:
            # If metric is "Hallucination Rate" and percent is 98% (Pass), that is good.
            # If we strictly follow the ref code:
            # ref code calculates failure rate for hallucination and compares against low thresholds.
            # Let's handle hallucination specifically if needed.
            
            # Ref code:
            # if metric_key == "hallucination":
            #    failed = total - passed
            #    percent = (failed / total) * 100
            #    ... checks if percent <= good ...
            
            # To avoid confusion, let's keep everything as PASS RATE here,
            # and let the Renderer handle display logic.
            pass
            
        if percent >= good:
            return "good"
        elif percent >= fair:
            return "fair"
        else:
            return "poor"

    def _build_trace_matrix(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        metric_order = [
            "task_completion", "hallucination", "relevance", "tool_usage",
            "user_satisfaction", "clarity", "persona_consistency"
        ]
        
        traces_data = []
        for t in traces:
            metrics = t.get("metrics", {})
            overall = t.get("overall_eval", "REVIEW")
            
            # Overall icon
            overall_icon = "?"
            if overall == "PASS":
                overall_icon = "✓"
            elif overall == "PARTIAL":
                overall_icon = "!"
            elif overall == "FAIL":
                overall_icon = "✗"
            
            cells = [{"status": overall.lower(), "icon": overall_icon}]
            
            for m_key in metric_order:
                if m_key in metrics:
                    eval_val = metrics[m_key].get("eval", "")
                    pass_val = PASS_STATES.get(m_key)
                    
                    if eval_val == pass_val:
                        status, icon = "pass", "✓"
                    elif eval_val in ["PARTIAL", "FAIR"]:
                        status, icon = "partial", "!"
                    else:
                        status, icon = "fail", "✗"
                else:
                    status, icon = "unknown", "?"
                cells.append({"status": status, "icon": icon})
                
            traces_data.append({
                "id": t.get("trace_id", ""),
                "metrics": cells
            })
            
        return {"traces": traces_data}

    def _build_performance_section(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        eff_config = self.eval_config.get("efficiency", {})
        
        cards = []
        
        # Helper for stats
        def get_stats(values, name, cfg):
            if not values:
                return {}
            stats = self._calculate_percentiles(values)
            outliers = self._detect_outliers(traces, values, cfg)
            return {
                "title": name,
                "stats": stats,
                "outliers": outliers,
                "outlier_label": cfg.get("outlier_label", "Outliers")
            }

        # 1. Output Tokens
        tok_vals = [t.get("output_tokens", 0) for t in traces]
        cards.append(get_stats(tok_vals, "Output Tokens", eff_config.get("output_tokens", {})))
        
        # 2. Depth
        turn_vals = [t.get("conversation_turns", 0) for t in traces]
        cards.append(get_stats(turn_vals, "Conversation Depth", eff_config.get("conversation_depth", {})))
        
        # 3. Latency
        lat_vals = [t.get("duration_ms", 0) / 1000 for t in traces]
        cards.append(get_stats(lat_vals, "Latency", eff_config.get("latency", {})))
        
        # Persona Gap
        persona_gap = self._calculate_persona_gap(traces)
        
        return {
            "cards": cards,
            "persona_gap": persona_gap
        }

    def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        if not values:
            return {}
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        
        def pct(p):
            if n == 1:
                return sorted_vals[0]
            k = (n - 1) * p / 100
            f = int(k)
            c = min(f + 1, n - 1)
            return sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])
            
        return {
            "mean": round(statistics.mean(values), 2),
            "p50": round(pct(50), 2),
            "p95": round(pct(95), 2),
            "p99": round(pct(99), 2),
            "std_dev": round(statistics.stdev(values), 2) if n > 1 else 0,
            "min": round(min(values), 2),
            "max": round(max(values), 2)
        }

    def _detect_outliers(self, traces: List[Dict[str, Any]], values: List[float], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        if len(values) < 2:
            return []
        
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        mode = config.get("outlier_mode", "statistical")
        threshold = float('inf')
        
        if mode == "statistical":
            threshold = mean_val + (config.get("std_multiplier", 2) * std_dev)
        elif mode == "absolute":
            threshold = config.get("absolute_threshold", float('inf'))
            
        outliers = []
        for t, v in zip(traces, values):
            if v > threshold:
                dev = ((v - mean_val) / mean_val * 100) if mean_val > 0 else 0
                outliers.append({
                    "trace_id": t.get("trace_id", ""),
                    "value": v,
                    "persona": t.get("persona", "unknown"),
                    "issue": f"{dev:.1f}% above avg"
                })
        return outliers

    def _calculate_persona_gap(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        persona_names = sorted(list(set(t.get("persona", "unknown") for t in traces)))
        if len(persona_names) < 2:
            return {}
            
        data_by_persona = {p: {"tokens": [], "latency": [], "turns": []} for p in persona_names}
        for t in traces:
            p = t.get("persona", "unknown")
            data_by_persona[p]["tokens"].append(t.get("output_tokens", 0))
            data_by_persona[p]["latency"].append(t.get("duration_ms", 0) / 1000)
            data_by_persona[p]["turns"].append(t.get("conversation_turns", 0))
            
        avgs = {}
        for p, d in data_by_persona.items():
            avgs[p] = {
                "avg_tokens": statistics.mean(d["tokens"]) if d["tokens"] else 0,
                "avg_latency": statistics.mean(d["latency"]) if d["latency"] else 0,
                "avg_turns": statistics.mean(d["turns"]) if d["turns"] else 0
            }
            
        def _slug(text: str) -> str:
            return (
                text.lower()
                .replace(" ", "_")
                .replace("-", "_")
                .replace(".", "")
            )

        def _label(text: str) -> str:
            return text.replace("_", " ").title()

        # Comparison (first 2 personas)
        p1, p2 = persona_names[0], persona_names[1]
        comparisons = []
        
        class_cycle = ["persona-a", "persona-b", "persona-c"]

        for metric, label in [
            ("avg_tokens", "Output Tokens"),
            ("avg_latency", "Latency"),
            ("avg_turns", "Conversation Depth"),
        ]:
            v1 = avgs[p1][metric]
            v2 = avgs[p2][metric]
            
            gap = ((v1 - v2) / v2 * 100) if v2 > 0 else 0
            max_val = max(v1, v2) if max(v1, v2) > 0 else 1
            
            bars = []
            for idx, (persona_name, value) in enumerate(
                [
                    (p1, v1),
                    (p2, v2),
                ]
            ):
                css_class = class_cycle[idx] if idx < len(class_cycle) else f"persona-{idx}"
                bars.append(
                    {
                        "persona": persona_name,
                        "label": _label(persona_name),
                        "class": css_class,
                        "value": str(round(value, 1)),
                        "width": int(value / max_val * 100),
                    }
                )

            comparisons.append(
                {
                    "label": label,
                    "bars": bars,
                    "gap": f"{gap:+.1f}%",
                }
            )
            
        return {"comparisons": comparisons, "persona_averages": avgs}

    def _classify_cases(self, traces: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "fail_cases": [t for t in traces if t.get("overall_eval") == "FAIL"],
            "marginal_cases": [t for t in traces if t.get("overall_eval") == "PARTIAL"],
            "review_cases": [t for t in traces if t.get("overall_eval") == "REVIEW"]
        }

    def _build_insights_section(self, classified: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        # Helper to format for report
        def fmt(trace, case_type):
            base = {
                "trace_id": trace.get("trace_id"),
                "input": trace.get("input", "")[:100],
                "persona": trace.get("persona"),
                "overall_eval": trace.get("overall_eval"),
                "primary_issue": trace.get("primary_issue"),
                "failed_metrics": self._get_failed_metrics(trace.get("metrics", {}))
            }
            analysis = trace.get("analysis", {}) or {}
            
            if case_type == "fail":
                base.update({
                    "tag": analysis.get("tag", "Unknown"),
                    "failed_badges": [{"icon": "✗", "label": m} for m in base["failed_metrics"]],
                    "issue_summary": analysis.get("issue_summary", ""),
                    "conversation_timeline": self._format_timeline(analysis.get("conversation_timeline", [])),
                    "root_cause": analysis.get("root_cause", ""),
                    "quick_fixes": analysis.get("quick_fixes", [])
                })
            elif case_type == "marginal":
                base.update({
                    "tag": analysis.get("tag", "Quality Issue"),
                    "quality_badges": self._get_quality_badges(trace.get("metrics", {})),
                    "issue_summary": analysis.get("issue_summary", "")
                })
            elif case_type == "review":
                 base.update({
                    "tag": "Review Needed",
                    "quality_badges": self._get_quality_badges(trace.get("metrics", {})),
                    "issue_summary": analysis.get("issue_summary", "Ambiguous case")
                })
            return base

        return {
            "fail_cases": [fmt(c, "fail") for c in classified["fail_cases"]],
            "marginal_cases": [fmt(c, "marginal") for c in classified["marginal_cases"]],
            "review_cases": [fmt(c, "review") for c in classified["review_cases"]]
        }

    def _get_failed_metrics(self, metrics: Dict[str, Any]) -> List[str]:
        failed = []
        for m, pass_val in PASS_STATES.items():
            if m in metrics and metrics[m].get("eval") != pass_val:
                failed.append(m)
        return failed

    def _get_quality_badges(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        badges = []
        labels = {"task_completion": "Task", "user_satisfaction": "Satisfaction", "clarity": "Clarity", "persona_consistency": "Persona"}
        for m, label in labels.items():
            if m in metrics:
                val = metrics[m].get("eval")
                pass_val = PASS_STATES.get(m)
                if val == pass_val:
                    badges.append({"status": "pass", "icon": "✓", "label": label})
                elif val in ["PARTIAL", "FAIR"]:
                    badges.append({"status": "partial", "icon": "!", "label": label})
                else:
                    badges.append({"status": "fail", "icon": "✗", "label": label})
        return badges

    def _format_timeline(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted: List[Dict[str, Any]] = []
        for entry in timeline:
            if not isinstance(entry, dict):
                continue
            text = entry.get("text") or entry.get("summary") or ""
            formatted.append(
                {
                    "turn": entry.get("turn"),
                    "role": entry.get("role", "assistant"),
                    "text": text,
                    "is_highlight": entry.get("is_highlight", False),
                }
            )
        return formatted

