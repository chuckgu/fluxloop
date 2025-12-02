"""
Data preparation and HTML rendering for evaluation reports.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


DEFAULT_METRIC_THRESHOLDS = {
    "task_completion": {"good": 80, "fair": 60},
    "hallucination": {"good": 5, "fair": 15},
    "relevance": {"good": 90, "fair": 80},
    "tool_usage": {"good": 90, "fair": 80},
    "user_satisfaction": {"good": 70, "fair": 50},
    "clarity": {"good": 90, "fair": 80},
    "persona_consistency": {"good": 85, "fair": 70},
}

DISPLAY_TO_CONFIG_METRIC_KEYS = {"tool_usage": "tool_usage_appropriateness"}
CONFIG_TO_DISPLAY_METRIC_KEYS = {
    config_key: display_key for display_key, config_key in DISPLAY_TO_CONFIG_METRIC_KEYS.items()
}
GENERIC_THRESHOLD_FALLBACK = {"good": 80, "fair": 60}
INVERTED_METRICS = {"hallucination"}


class ReportRenderer:
    """Prepares data and renders the HTML report."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        # Locate template relative to this file
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.template_name = "report.html.j2"

    def render(self, rule_based_data: Dict[str, Any], llm_ov_data: Optional[Dict[str, Any]], 
               traces_data: List[Dict[str, Any]], config: Dict[str, Any]) -> Path:
        """
        Render the report to HTML.
        
        Args:
            rule_based_data: Result from StatsAggregator
            llm_ov_data: Result from OverallEvaluator
            traces_data: Original trace objects (for conversation viewer)
            config: Full project configuration
            
        Returns:
            Path to the generated HTML file
        """
        # Prepare data
        prepared_data = self._prepare_data(rule_based_data, llm_ov_data, traces_data, config)
        
        # Setup Jinja2
        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")
            
        env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        template = env.get_template(self.template_name)
        html_content = template.render(**prepared_data)
        
        # Save file
        output_path = self.output_dir / "report.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        logger.info(f"Report generated at {output_path}")
        return output_path

    def _prepare_data(self, rule_based: Dict[str, Any], llm_ov: Optional[Dict[str, Any]], 
                      traces_data: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        
        eval_config = config.get("evaluation", {})
        
        # Transform each section
        meta = self._transform_meta(config)
        conf_section = self._transform_config(config, rule_based)
        criteria = self._transform_eval_criteria(eval_config)
        summary = self._transform_summary(rule_based, llm_ov)
        matrix = self._transform_trace_matrix(rule_based, llm_ov)
        quality = self._transform_response_quality(rule_based, llm_ov)
        insights = self._transform_insights(rule_based, llm_ov) # llm_ov implies insights analysis logic
        recommendations = self._transform_recommendations(llm_ov)
        performance = self._transform_performance(rule_based, llm_ov)
        conversations = self._transform_conversations(traces_data)
        
        return {
            "meta": meta,
            "config": conf_section,
            "eval_criteria": criteria,
            "summary": summary,
            "trace_matrix": matrix,
            "response_quality": quality,
            "insights": insights,
            "recommendations": recommendations,
            "performance": performance,
            "conversations": conversations
        }

    # -------------------------------------------------------------------
    # Transformation Logic
    # -------------------------------------------------------------------

    def _transform_meta(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "agent_name": config.get("name", "AI Agent").replace("_", " ").title(),
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _transform_config(self, config: Dict[str, Any], rule_based: Dict[str, Any]) -> Dict[str, Any]:
        input_cfg = config.get("input", {})
        eval_cfg = config.get("evaluation", {})
        generated_inputs = config.get("generated_inputs", {}) or {}
        
        personas = input_cfg.get("personas", [])
        base_inputs = input_cfg.get("base_inputs", [])
        variation_entries = generated_inputs.get("variations") or []
        
        # Extract variations from traces if possible, otherwise placeholder
        # In fluxloop execution, we might not have 'generated.yaml' equivalent handy here unless passed.
        # We'll approximate from input config.
        goal_value = eval_cfg.get("evaluation_goal", "Evaluate AI agent performance")
        if isinstance(goal_value, dict):
            goal_value = goal_value.get("text") or ""
        if goal_value is None:
            goal_value = ""
        goal_value = str(goal_value).strip()
        if not goal_value:
            goal_value = "Evaluate AI agent performance"
        
        generator_model = (
            generated_inputs.get("generator_model")
            or input_cfg.get("input_generation", {}).get("llm", {}).get("model")
            or "N/A"
        )
        variation_strategies = generated_inputs.get("strategies") or input_cfg.get("variation_strategies", [])

        return {
            "goal": goal_value,
            "test_design": {
                "total_traces": rule_based.get("meta", {}).get("total_traces", 0),
                "personas_count": len(personas),
                "iterations": config.get("simulation", {}).get("iterations", 1),
                "execution_date": datetime.now().strftime("%Y-%m-%d %H:%M")
            },
            "input_generation": {
                "base_inputs": len(base_inputs),
                "generated_count": len(variation_entries),
                "generator_model": generator_model,
                "strategies": variation_strategies,
            },
            "evaluation": {
                "judge_model": eval_cfg.get("advanced", {}).get("llm_judge", {}).get("model", "gpt-4o"),
                "enabled_metrics": [k for k, v in eval_cfg.get("metrics", {}).items() if v.get("enabled", True)]
            },
            "personas": personas,
            "tested_inputs": {
                "base_input": base_inputs[0].get("input", "") if base_inputs else "",
                "variations": variation_entries,
            }
        }

    def _transform_eval_criteria(self, eval_config: Dict[str, Any]) -> Dict[str, Any]:
        metrics_cfg = eval_config.get("metrics", {}) or {}
        efficiency = eval_config.get("efficiency", {}) or {}
        thresholds: Dict[str, Dict[str, str]] = {}

        def _coerce_number(value: Any, fallback: float) -> float:
            if isinstance(value, (int, float)):
                return float(value)
            try:
                return float(value)
            except (TypeError, ValueError):
                return float(fallback)

        def _format_number(value: float) -> str:
            if value.is_integer():
                return str(int(value))
            return str(value)

        def _register_threshold(display_key: str, good_val: float, fair_val: float) -> None:
            good_text, fair_text = _format_number(good_val), _format_number(fair_val)
            if display_key in INVERTED_METRICS:
                thresholds[display_key] = {
                    "good": f"<={good_text}%",
                    "fair": f"{good_text}-{fair_text}%",
                    "poor": f">{fair_text}%",
                }
            else:
                thresholds[display_key] = {
                    "good": f">={good_text}%",
                    "fair": f"{fair_text}-{good_text}%",
                    "poor": f"<{fair_text}%",
                }

        def _resolve_thresholds(display_key: str, metric_cfg: Dict[str, Any]) -> None:
            defaults = DEFAULT_METRIC_THRESHOLDS.get(display_key, GENERIC_THRESHOLD_FALLBACK)
            thresholds_cfg = metric_cfg.get("thresholds", {})
            good_val = _coerce_number(thresholds_cfg.get("good"), defaults["good"])
            fair_val = _coerce_number(thresholds_cfg.get("fair"), defaults["fair"])
            _register_threshold(display_key, good_val, fair_val)

        for cfg_key, cfg_value in metrics_cfg.items():
            display_key = CONFIG_TO_DISPLAY_METRIC_KEYS.get(cfg_key, cfg_key)
            _resolve_thresholds(display_key, cfg_value)

        for display_key, defaults in DEFAULT_METRIC_THRESHOLDS.items():
            if display_key not in thresholds:
                _register_threshold(
                    display_key,
                    float(defaults["good"]),
                    float(defaults["fair"]),
                )
                    
        eff_flags = {}
        if "output_tokens" in efficiency:
            eff_flags["verbose"] = efficiency["output_tokens"].get("std_multiplier", 2) * 1000 # Approximation
        if "conversation_depth" in efficiency:
            eff_flags["deep"] = 6
        if "latency" in efficiency:
             eff_flags["slow"] = 60
             
        return {"thresholds": thresholds, "efficiency_flags": eff_flags}

    def _transform_summary(self, rule_based: Dict[str, Any], llm_ov: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        # Merge rule based summary with LLM-OV titles
        summary = rule_based.get("summary", {})
        meta = rule_based.get("meta", {})
        
        pass_rate = summary.get("pass_rate", 0)
        status_icon = "✓" if pass_rate >= 80 else ("!" if pass_rate >= 50 else "✗")
        
        # Attention required (FAIL/PARTIAL traces)
        traces = rule_based.get("enriched_traces", [])
        attention = []
        for t in traces:
            if t.get("overall_eval") in ["FAIL", "PARTIAL", "REVIEW"]:
                status = t.get("overall_eval").lower()
                if status == "partial":
                    status = "marginal"  # map to css class
                
                icon_map = {"fail": "✗", "marginal": "!", "review": "?"}
                attention.append({
                    "trace_id": t.get("trace_id"),
                    "input": t.get("input", ""),
                    "status": status,
                    "status_icon": icon_map.get(status, "?"),
                    "status_label": t.get("overall_eval").title(),
                    "issue": t.get("primary_issue", "").replace("_", " ").title(),
                    "reason": t.get("analysis", {}).get("issue_summary", "")
                })

        return {
            **summary,
            "status_icon": status_icon,
            "attention_required": attention[:6],
            "status_title": "Pass Rate",
            "status_subtitle": "Percentage of traces that met the evaluation criteria.",
            "executive_subtitle": f"{meta.get('passed_traces')}/{meta.get('total_traces')} traces passed",
        }

    def _transform_trace_matrix(self, rule_based: Dict[str, Any], llm_ov: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        matrix = rule_based.get("trace_matrix", {})
        desc = "Evaluation results for all traces."
        if llm_ov:
            desc = llm_ov.get("trace_matrix", {}).get("description", desc)
        matrix["description"] = desc
        return matrix

    def _transform_response_quality(self, rule_based: Dict[str, Any], llm_ov: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        # Need to reconstruct quality metrics gauge data from rule_based stats
        stats = rule_based.get("summary", {}).get("metric_stats", [])
        qual_keys = ["User Satisfaction Score", "Response Clarity", "Persona Consistency"]
        qual_metrics = [s for s in stats if s["name"] in qual_keys]
        
        result = {
            "quality_metrics": qual_metrics,
            "observations": [], "improvement_patterns": [], "quick_wins": [], "marginal_cases": []
        }
        
        if llm_ov and "response_quality" in llm_ov:
            rq = llm_ov["response_quality"]
            result.update({k: rq.get(k, []) for k in ["observations", "improvement_patterns", "quick_wins"]})
            
        # Marginal cases from traces
        traces = rule_based.get("enriched_traces", [])
        for t in traces:
            if t.get("overall_eval") == "PARTIAL":
                analysis = t.get("analysis", {})
                result["marginal_cases"].append({
                    "trace_id": t.get("trace_id"),
                    "tag": analysis.get("tag", "Quality Issue"),
                    "input": t.get("input", ""),
                    "persona": t.get("persona", ""),
                    "quality_badges": [], # Simplified for now
                    "issue_point": {"issue": analysis.get("issue_summary", ""), "turns": []},
                    "recommendation": (analysis.get("quick_fixes", []) or [""])[0]
                })
        return result

    def _transform_insights(self, rule_based: Dict[str, Any], llm_ov: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        # LLM-OV insights usually contains better formatted fail/review cases
        # But we need to ensure table_traces are present
        
        insights = rule_based.get("insights", {}) # fail_cases, review_cases lists
        
        # Build table_traces from enriched traces for the matrix view in insights tab
        traces = rule_based.get("enriched_traces", [])
        table_traces = []
        metric_order = ["task_completion", "hallucination", "relevance", "tool_usage", "user_satisfaction", "clarity", "persona_consistency"]
        
        for t in traces:
            if t.get("overall_eval") in ["FAIL", "REVIEW"]:
                 metrics = t.get("metrics", {})
                 cells = [{"status": t.get("overall_eval").lower(), "icon": "✗" if t.get("overall_eval") == "FAIL" else "?"}]
                 for k in metric_order:
                     val = metrics.get(k, {}).get("eval", "")
                     status = "fail" if val not in ["PASS", "GOOD", "APPROPRIATE", "PARTIAL", "FAIR", "REVIEW"] else ("partial" if val in ["PARTIAL", "FAIR"] else "pass")
                     icon = "✗" if status == "fail" else ("!" if status == "partial" else "✓")
                     cells.append({"status": status, "icon": icon})
                 
                 table_traces.append({"id": t.get("trace_id"), "metrics": cells})
        
        # Merge with LLM-OV detailed reasoning if available
        # Currently llm_ov outputs 'insights' with 'failed_cases_analysis'
        # We might need to merge that into rule_based['insights']['fail_cases']
        # For simplicity, we stick to rule_based insights as they are quite detailed already (contain root_cause etc from PT)
        
        return {
            "table_traces": table_traces[:10],
            "failed_cases": insights.get("fail_cases", [])[:10],
            "review_cases": insights.get("review_cases", [])[:10]
        }

    def _transform_recommendations(self, llm_ov: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not llm_ov:
            return {}
        
        recs = llm_ov.get("recommendations", {})
        # Ensure default structure and badges
        for group in recs.get("priority_groups", []):
            group["icon"] = "!" if group["priority"] in ["critical", "important"] else "✓"
            for issue in group.get("issue_list", []):
                if not issue.get("impact_badge"):
                    cls = "fail" if group["priority"] == "critical" else ("warn" if group["priority"] == "important" else "info")
                    issue["impact_badge"] = {"class": cls, "text": group["priority"].title()}
        return recs

    def _transform_performance(self, rule_based: Dict[str, Any], llm_ov: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        perf = rule_based.get("performance", {})
        
        # Inject interpretation from LLM-OV
        if llm_ov:
            ov_perf = llm_ov.get("performance", {})
            for card in perf.get("cards", []):
                key = card["title"].lower().replace(" ", "_")
                if key in ov_perf:
                    card["recommendation"] = ov_perf[key].get("recommendation", "")
            
            pg = perf.get("persona_gap", {})
            if "persona_gap" in ov_perf:
                pg["interpretation"] = ov_perf["persona_gap"].get("interpretation", "")
                pg["recommendations"] = ov_perf["persona_gap"].get("recommendations", [])

        # Add visual helpers (bars, axis)
        for card in perf.get("cards", []):
            stats = card.get("stats", {})
            card["distribution_bars"] = self._gen_bars()
            card["axis_labels"] = ["Min", "Avg", "Max"] # Simplified
            
            # Format stats list for display
            card["stats"] = [
                {"label": "Mean", "value": str(stats.get("mean", 0))},
                {"label": "P95", "value": str(stats.get("p95", 0))},
            ]
            
        # Create overview metrics
        overview = {
            "metrics": [], "total_cost": "N/A", "avg_cost_per_trace": "N/A"
        }
        # Populate metrics from cards
        for card in perf.get("cards", []):
            if "Tokens" in card["title"]:
                overview["metrics"].append({"label": "Avg Tokens", "value": str(card["stats"][0]["value"])})
        
        return {"cards": perf.get("cards", []), "persona_gap": perf.get("persona_gap", {}), "overview": overview}

    def _gen_bars(self) -> List[Dict[str, Any]]:
        # Dummy bars for UI if actual distribution not calculated
        return [{"height": 20}, {"height": 40}, {"height": 80}, {"height": 60}, {"height": 30}]

    def _transform_conversations(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        convs = {}
        for t in traces:
            tid = t.get("trace_id")
            if not tid:
                continue
            
            # Extract turns
            turns = []
            if "conversation" in t:
                for msg in t["conversation"]:
                    role = msg.get("role")
                    content = self._normalize_conversation_content(msg.get("content"))
                    if role == "assistant":
                        turns.append({
                            "role": "assistant",
                            "content": content,
                            "turn_index": msg.get("turn_index", 0)
                        })
            else:
                # Single turn fallback
                if t.get("input"):
                    pass  # User input already visible elsewhere
                if t.get("output"):
                    turns.append({"role": "assistant", "content": self._normalize_conversation_content(t["output"]), "turn_index": 1})

            summary_section = t.get("summary") or {}
            success_flag = t.get("success")
            if success_flag is None:
                success_flag = summary_section.get("success")
            if isinstance(success_flag, str):
                success_flag = success_flag.lower() == "true"
            duration_ms = t.get("duration_ms")
            if duration_ms is None:
                duration_ms = summary_section.get("duration_ms")
                if isinstance(duration_ms, str) and duration_ms.isdigit():
                    duration_ms = float(duration_ms)

            convs[tid] = {
                "trace_id": tid,
                "persona": t.get("persona", ""),
                "turn_count": len([x for x in turns if x["role"] == "user"]),
                "turns": turns,
                "duration_ms": duration_ms,
                "success": success_flag,
                "overall_eval": t.get("overall_eval") or summary_section.get("overall_eval"),
            }
        return convs

    def _normalize_conversation_content(self, content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            transcript = content.get("transcript")
            if isinstance(transcript, list):
                lines: List[str] = []
                for entry in transcript:
                    if not isinstance(entry, dict):
                        continue
                    user_text = entry.get("user")
                    assistant_text = entry.get("assistant")
                    if user_text:
                        lines.append(f"User: {user_text}")
                    if assistant_text:
                        lines.append(f"Assistant: {assistant_text}")
                if lines:
                    return "\n".join(lines)
            if "text" in content and isinstance(content["text"], str):
                return content["text"]
            return json.dumps(content, ensure_ascii=False)
        if isinstance(content, list):
            return "\n".join(self._normalize_conversation_content(item) for item in content if item)
        return str(content)

