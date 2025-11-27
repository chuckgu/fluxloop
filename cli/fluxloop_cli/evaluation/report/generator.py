"""
LLM-based evaluators for report generation (Per-Trace and Overall).
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ===================================================================
# Prompts for Per-Trace Evaluation (LLM-PT)
# ===================================================================

PT_SYSTEM_PROMPT = """You are an expert AI agent evaluator. Your task is to evaluate the provided JSON trace against 7 quality metrics, and provide detailed analysis when issues are found.

## Evaluation Goal

{evaluation_goal}

## Target Persona

- **Name**: {persona_name}
- **Description**: {persona_description}
- **Characteristics**:
{persona_characteristics}

## Metric Definitions

Evaluate the conversation against each metric below. For each metric, provide:
1. **eval**: The evaluation result (use ONLY the specified labels)
2. **reasoning**: A brief explanation in 2-3 sentences

### 1. Task Completion
- **Question**: Did the agent complete what was requested?
- **Definition**: Whether the agent actually completed the task requested by the user
- **Evaluation Labels**:
  - `PASS`: Fully completed the requested task
  - `PARTIAL`: Partially completed or provided an alternative
  - `FAIL`: Did not complete the task at all

### 2. Hallucination
- **Question**: Is the answer factually correct? Is there evidence?
- **Definition**: Whether specific facts (numbers, dates, references, etc.) match actual tool outputs or are fabricated
- **Evaluation Labels**:
  - `PASS`: All facts are grounded in tool output or verifiable information
  - `FAIL`: Contains ungrounded or fabricated facts

### 3. Relevance
- **Question**: Is the response on-topic?
- **Definition**: Whether the response is directly relevant to the user's question without excessive irrelevant information
- **Evaluation Labels**:
  - `PASS`: Directly relevant to the question, minimal irrelevant info
  - `FAIL`: Unrelated to the question or contains excessive irrelevant info

### 4. Tool Usage
- **Question**: Was the task performed with appropriate process?
- **Definition**: Whether tools were used in correct order and with logical steps
- **Evaluation Principles**:
  - Information gathering before action
  - User confirmation before destructive actions
  - Logical sequence of operations
  - Avoid excessive or unnecessary calls
- **Evaluation Labels**:
  - `APPROPRIATE`: Safe and logical process
  - `INAPPROPRIATE`: Risky, inefficient, or incorrect tool usage

### 5. User Satisfaction
- **Question**: Would a real user be satisfied?
- **Definition**: Whether tone, empathy, and verbosity match the situation and urgency
- **Evaluation Labels**:
  - `GOOD`: Satisfactory user experience
  - `FAIR`: Room for improvement
  - `BAD`: Unsatisfactory experience

### 6. Clarity
- **Question**: Is the response clear and easy to understand?
- **Definition**: Whether the response is well-structured, logical, and delivered without contradictions or duplication
- **Evaluation Labels**:
  - `PASS`: Clear and structured response
  - `FAIL`: Unclear, contradictory, duplicative, or unstructured

### 7. Persona Consistency
- **Question**: Did the agent respond appropriately for the user type?
- **Definition**: Whether tone, expertise level, and explanation style match the persona characteristics defined above
- **Evaluation Labels**:
  - `PASS`: Matches persona (appropriate tone, explanation depth)
  - `FAIL`: Mismatches persona (e.g., jargon for novice, over-explanation for expert)

## Analysis Section (Conditional)

**When to include `analysis`**: If ANY metric is NOT in the "pass" state (see table below), you MUST provide the `analysis` object.

| Metric | Pass State |
|--------|------------|
| task_completion | PASS |
| hallucination | PASS |
| relevance | PASS |
| tool_usage | APPROPRIATE |
| user_satisfaction | GOOD |
| clarity | PASS |
| persona_consistency | PASS |

**Analysis fields**:

### conversation_timeline
Summarize the conversation flow, focusing on key turns. Include:
- `turn`: Turn number (1-indexed)
- `role`: "user", "assistant", or "tool"
- `summary`: Brief summary of what happened (1 sentence)
- `is_highlight`: Set to `true` if this turn contains an issue or problem

### issue_summary
One concise sentence explaining what went wrong.

Must include these elements:
- **What**: The specific action or output that failed
- **Why**: The reason it's problematic (use "but", "despite", "resulting in")

Guidelines:
- Keep under 100 characters
- Be specific (mention tools, personas, concrete details)
- Avoid generic phrases like "didn't work properly"

Examples:
- "Agent retrieved booking info but failed to execute cancellation despite user confirmation."
- "Response duplicated 3× due to output error, showing identical refund explanation."
- "Expert-style request received novice-level verbose explanation."

### diagnostic_statement
A single, concise statement (under 80 characters) that captures the core issue. Be specific, not generic.

**Formats by issue type:**
- **Missing action**: `Expected: tool_name(args) but NOT called`
- **Wrong output**: `Output error: [specific problem]`
- **Ambiguity**: `Unclear if [action] satisfies [requirement]`
- **Process issue**: `[Action] performed without [required step]`
- **Content issue**: `Response contains [specific problem]`

### tag
Categorize the issue type in 2-3 words. Common tags:
- `confirmation_missing`, `hallucination`, `incomplete_task`, `wrong_tool_order`
- `content_duplicated`, `tone_mismatch`, `irrelevant_info`, `empty_response`

### root_cause
Analyze why this issue occurred. (1-2 sentences)

### quick_fixes
Array of 2-3 specific, actionable fix suggestions.

## Instructions

1. Read the conversation carefully from start to end
2. Evaluate each metric independently based on its definition
3. Use ONLY the specified evaluation labels for each metric
4. Provide brief reasoning (2-3 sentences) explaining your judgment
5. **If any metric is NOT in pass state**: Include the `analysis` object with all required fields
6. **If all metrics are in pass state**: Omit the `analysis` object entirely
7. Write all text in {output_language}

## Output Format

Return a valid JSON object with EXACTLY this structure:

```json
{{
  "metrics": {{
    "task_completion": {{ "eval": "PASS|PARTIAL|FAIL", "reasoning": "string" }},
    "hallucination": {{ "eval": "PASS|FAIL", "reasoning": "string" }},
    "relevance": {{ "eval": "PASS|FAIL", "reasoning": "string" }},
    "tool_usage": {{ "eval": "APPROPRIATE|INAPPROPRIATE", "reasoning": "string" }},
    "user_satisfaction": {{ "eval": "GOOD|FAIR|BAD", "reasoning": "string" }},
    "clarity": {{ "eval": "PASS|FAIL", "reasoning": "string" }},
    "persona_consistency": {{ "eval": "PASS|FAIL", "reasoning": "string" }}
  }},
  "analysis": {{  // Only if any metric is NOT in pass state
    "conversation_timeline": [...],
    "issue_summary": "string",
    "diagnostic_statement": "string",
    "tag": "string",
    "root_cause": "string",
    "quick_fixes": ["string", "string"]
  }}
}}
```

Return ONLY the JSON object, no additional text.
"""

PT_USER_MESSAGE_TEMPLATE = """Evaluate the following trace:

```json
{trace_json}
```
"""

# ===================================================================
# Prompts for Overall Evaluation (LLM-OV)
# ===================================================================

OV_PROMPT_TEMPLATE = """You are an expert AI agent evaluation analyst. Your task is to analyze evaluation results across multiple traces, identify common patterns, and provide actionable recommendations.

**Important**: Individual trace analysis has already been completed (LLM-PT). Your role is to:
1. Synthesize findings across all traces
2. Discover common patterns and group related issues
3. Interpret performance/efficiency metrics
4. Prioritize recommendations by criticality

---

## Evaluation Goal

{evaluation_goal}

---

## Aggregated Statistics

```json
{aggregated_stats}
```

This includes:
- `pass_rate`, `total_traces`, `passed` - Overall success metrics
- `metric_rows[]` - Per-metric statistics (percent, passed, total, status)
- `badges[]` - Status counts (marginal, failed, review)

---

## Performance & Efficiency Statistics

```json
{performance_stats}
```

This includes:
- `overview.metrics[]` - Avg Output Tokens, Avg Turns, Avg Latency
- `overview.total_cost`, `overview.avg_cost_per_trace` - Cost metrics
- `cards[]` - Output Tokens, Conversation Depth, Latency each with:
  - `stats[]` - Mean, P50, P95, P99, Range, Std Dev
  - `outliers.cases[]` - Outlier cases detected
- `persona_gap.comparisons[]` - Per-persona comparison data

---

## Failed Cases (with PT Analysis)

These cases have `overall_eval == "FAIL"` due to Completeness/Correctness metric failures.

```json
{failed_cases}
```

---

## Marginal Cases (with PT Analysis)

These cases have `overall_eval == "PARTIAL"` - task completed but with quality/efficiency issues.

```json
{marginal_cases}
```

---

## Review Cases (with PT Analysis)

These cases require human review due to ambiguous judgment.

```json
{review_cases}
```

---

## Your Tasks

### Task 1: Executive Summary
Provide overall status assessment:
- `status_title`: One of "Production Ready", "Needs Work", or "Critical Issues"
- `status_subtitle`: One sentence explaining the overall state

### Task 2: Trace Matrix Description
Write a 1-2 sentence summary of the complete evaluation results.

### Task 3: Response Quality Analysis

#### 3.1 Observations
Identify 3-5 key observations about quality metrics. Mark significant issues with `highlight: true`.

#### 3.2 Improvement Patterns (Bottom-up Discovery)
Analyze cases with the following metric issues and group them by similarity:

**Target metrics for patterns**:
- `task_completion`: PARTIAL cases
- `user_satisfaction`: FAIR or BAD cases
- `clarity`: FAIL cases
- `persona_consistency`: FAIL cases

**Grouping criteria**:
1. Tag-based grouping: Cases with same or similar `tag`
2. Root cause similarity: Cases with related `root_cause`
3. Metric correlation: Cases failing same metrics

**Rules**:
- Generate 0 patterns if all cases are unique
- Generate as many patterns as you discover (no artificial limit)
- Each pattern must have 2+ affected traces
- Single-trace issues: include in `quick_wins` instead

#### 3.3 Quick Wins
Extract immediately actionable improvements from PT's `quick_fixes` that appear repeatedly.

### Task 4: Insights (Failed/Review Case Analysis)
For each failed case, provide:
- `llm_reasoning`: Detailed analysis of why it failed
- `root_cause`: Root cause of the failure
- `recommendation`: How to fix this specific issue

For each review case, provide:
- `llm_reasoning`: Why this case is ambiguous
- `why_review_needed`: Explanation for human reviewers
- `review_questions`: 2-3 questions for human review

### Task 5: Recommendations (Prioritized Action Items)
Collect all action items from insights and response_quality, then sort by criticality:
- **Critical**: Must fix before deployment (core function failures)
- **Important**: Address in next sprint (quality/efficiency issues)
- **Nice-to-have**: When time permits (optimizations)

### Task 6: Performance Interpretation
For each performance metric, provide interpretation and recommendation:

#### 6.1 Output Tokens
- Interpret token usage patterns (why P95 is high, trends, etc.)
- Recommend optimizations

#### 6.2 Conversation Depth
- Interpret conversation depth patterns (complex cases, etc.)
- Recommend improvements

#### 6.3 Latency
- Interpret latency patterns (outlier causes, etc.)
- Recommend optimizations

#### 6.4 Persona Gap
- Interpret the gap between personas
- Distinguish **expected gaps** (novice needs more explanation) from **concerning gaps** (inefficiencies)
- Recommend persona-specific optimizations

---

## Output Format

Return a valid JSON object with EXACTLY this structure:

```json
{{
  "executive_summary": {{
    "status_title": "Production Ready | Needs Work | Critical Issues",
    "status_subtitle": "One sentence summary"
  }},

  "trace_matrix": {{
    "description": "1-2 sentence summary of all evaluation results"
  }},

  "response_quality": {{
    "observations": [
      {{ "text": "Observation 1", "highlight": false }},
      {{ "text": "Critical observation", "highlight": true }}
    ],

    "improvement_patterns": [
      {{
        "icon": "emoji",
        "icon_class": "persona | tokens | intent | task | clarity",
        "title": "Pattern title",
        "case_count": 4,
        "evidence_list": ["PT issue_summary quote 1", "PT issue_summary quote 2"],
        "root_cause": "Grouped root cause",
        "context": "Detailed context with specific examples",
        "action": "Recommended action"
      }}
    ],

    "quick_wins": [
      "Quick improvement 1",
      "Quick improvement 2"
    ]
  }},

  "insights": {{
    "failed_cases_analysis": [
      {{
        "trace_id": "xxx",
        "llm_reasoning": "Detailed failure analysis",
        "root_cause": "Root cause description",
        "recommendation": "Fix recommendation"
      }}
    ],

    "review_cases_analysis": [
      {{
        "trace_id": "xxx",
        "llm_reasoning": "Why this is ambiguous",
        "why_review_needed": "Explanation for reviewers",
        "review_questions": ["Question 1", "Question 2"]
      }}
    ]
  }},

  "recommendations": {{
    "priority_groups": [
      {{
        "priority": "critical",
        "title": "Critical",
        "subtitle": "Must fix before deployment",
        "issue_list": [
          {{
            "title": "Issue title",
            "problem": "Problem description",
            "trace": {{ "id": "xxx", "input": "..." }},
            "root_cause": "Root cause",
            "evidence": [
              {{ "status": "fail", "icon": "✗", "text": "Evidence 1" }}
            ],
            "fix_steps": ["Fix step 1", "Fix step 2"],
            "expected_impact": "Expected impact"
          }}
        ]
      }},
      {{
        "priority": "important",
        "title": "Important",
        "subtitle": "Address in next sprint",
        "issue_list": []
      }},
      {{
        "priority": "nice-to-have",
        "title": "Nice-to-Have",
        "subtitle": "When time permits",
        "issue_list": []
      }}
    ]
  }},

  "performance": {{
    "output_tokens": {{
      "interpretation": "Token usage interpretation",
      "recommendation": "Optimization recommendation"
    }},

    "conversation_depth": {{
      "interpretation": "Conversation depth interpretation",
      "recommendation": "Improvement recommendation"
    }},

    "latency": {{
      "interpretation": "Latency interpretation",
      "recommendation": "Optimization recommendation"
    }},

    "persona_gap": {{
      "interpretation": "Persona gap interpretation (expected vs concerning)",
      "recommendations": [
        "Persona optimization 1",
        "Persona optimization 2"
      ]
    }}
  }}
}}
```

---

## Guidelines

1. **Do NOT rewrite individual analyses** - Reference and quote PT results, don't recreate them
2. **Focus on patterns** - Look for commonalities across cases, not individual details
3. **Quote evidence specifically** - Use PT's `issue_summary` directly in `evidence_list`
4. **Interpret, don't just list** - Provide meaning behind numbers, not just the numbers
5. **Contextualize persona gaps** - Distinguish expected gaps (novice needs more detail) from problematic gaps
6. **Be actionable** - Every recommendation should be specific and implementable
7. **Write all text in {output_language}**

---

## Icon Classes Reference

Use these `icon_class` values for `improvement_patterns`:
- `persona` - Persona consistency issues
- `tokens` - Verbose response / token efficiency issues
- `intent` - Intent recognition / implicit question issues
- `task` - Task completion issues
- `clarity` - Response clarity issues

---

Return ONLY the JSON object, no additional text.
"""


# ===================================================================
# Helpers
# ===================================================================

def parse_json_response(output: str) -> dict:
    """Extract and parse JSON from LLM output."""
    if "```json" in output:
        start = output.find("```json") + 7
        end = output.find("```", start)
        output = output[start:end].strip()
    elif "```" in output:
        start = output.find("```") + 3
        end = output.find("```", start)
        output = output[start:end].strip()

    return json.loads(output)


# ===================================================================
# Classes
# ===================================================================

class ReportLLMClient:
    """Lightweight wrapper for LLM calls used in reporting."""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            self.client = None
            logger.warning("openai package not installed. Report evaluation requires 'pip install openai'.")

    async def invoke(self, system_prompt: str, user_message: str, model: str) -> Tuple[Optional[str], Optional[str]]:
        if not self.client:
            return None, "OpenAI client unavailable"

        try:
            # gpt-5 or o1 series (reasoning models)
            if model.startswith("gpt-5") or model.startswith("o1"):
                # Use combined input for reasoning models if they don't support system/user split well
                # But typically they are supported via chat completions or responses API.
                # Here we stick to Chat Completions for broad compatibility unless 'responses' API is available.
                
                # Note: If 'responses' API is required for gpt-5, this would need update.
                # Assuming standard chat completion interface for now.
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ]
                
                # Check for reasoning parameter support or model specific params
                # For simplicity in this migration, using standard call
                completion = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.0,
                )
                return completion.choices[0].message.content, None

            # Standard gpt-4/3.5
            else:
                completion = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.0,
                )
                return completion.choices[0].message.content, None

        except Exception as e:
            return None, str(e)


class TraceEvaluator:
    """Evaluates individual traces (LLM-PT)."""

    def __init__(self, client: ReportLLMClient, config: Dict[str, Any]):
        self.client = client
        self.config = config
        self.eval_config = config.get("evaluation", {})
        self.personas = {p["name"]: p for p in config.get("input", {}).get("personas", [])}

    async def evaluate_trace(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        trace_id = trace.get("trace_id", "unknown")
        persona_name = trace.get("persona", "unknown")
        persona = self.personas.get(persona_name, {"name": persona_name, "description": "", "characteristics": []})

        system_prompt = self._build_system_prompt(persona)
        prompt_payload = self._build_prompt_payload(trace)
        user_message = PT_USER_MESSAGE_TEMPLATE.format(
            trace_json=json.dumps(prompt_payload, ensure_ascii=False, indent=2)
        )

        model = self.eval_config.get("advanced", {}).get("llm_judge", {}).get("model", "gpt-4o")

        output, error = await self.client.invoke(system_prompt, user_message, model)

        if error:
            logger.error(f"Trace evaluation failed for {trace_id}: {error}")
            return {"trace_id": trace_id, "error": error}

        try:
            result = parse_json_response(output)
            result["trace_id"] = trace_id
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for {trace_id}: {e}")
            return {"trace_id": trace_id, "error": f"JSON parse error: {e}", "raw_output": output}

    def _build_system_prompt(self, persona: Dict[str, Any]) -> str:
        characteristics = "\n".join(f"  - {c}" for c in persona.get("characteristics", []))
        
        # Handle cases where evaluation_goal is a dict (from new template) or str
        goal = self.eval_config.get("evaluation_goal", "Evaluate the agent's performance")
        if isinstance(goal, dict):
            goal = goal.get("text", str(goal))

        output_lang = self._resolve_output_language(persona.get("language"))

        return PT_SYSTEM_PROMPT.format(
            evaluation_goal=goal,
            persona_name=persona.get("name", "unknown"),
            persona_description=persona.get("description", ""),
            persona_characteristics=characteristics,
            output_language=output_lang
        )

    def _resolve_output_language(self, persona_language: Optional[str]) -> str:
        """
        Determine the best output language with backwards compatibility.

        Preference order:
        1. Explicit language inside report.output.language
        2. Legacy report.language (if added later)
        3. Persona language metadata
        4. Default to English
        """
        report_cfg = self.eval_config.get("report") or {}
        output_cfg = report_cfg.get("output")

        if isinstance(output_cfg, dict):
            lang = output_cfg.get("language")
            if isinstance(lang, str) and lang.strip():
                return lang.strip()

        legacy_lang = report_cfg.get("language")
        if isinstance(legacy_lang, str) and legacy_lang.strip():
            return legacy_lang.strip()

        if isinstance(persona_language, str) and persona_language.strip():
            return persona_language.strip()

        return "en"

    def _build_prompt_payload(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """Create a compact payload for prompt construction."""

        allowed_fields = [
            "trace_id",
            "iteration",
            "persona",
            "input",
            "output",
            "final_output",
            "duration_ms",
            "success",
            "token_usage",
            "observation_count",
        ]

        payload = {field: trace.get(field) for field in allowed_fields if field in trace}

        conversation = trace.get("conversation")
        if not conversation and isinstance(trace.get("conversation_state"), dict):
            conversation = trace["conversation_state"].get("turns")
        simplified_conversation = self._simplify_conversation(conversation)
        if simplified_conversation:
            payload["conversation"] = simplified_conversation

        timeline = trace.get("timeline")
        if isinstance(timeline, list):
            simplified_timeline = [
                self._simplify_timeline_entry(entry)
                for entry in timeline
                if isinstance(entry, dict)
            ]
            simplified_timeline = [entry for entry in simplified_timeline if entry]
            if simplified_timeline:
                payload["timeline"] = simplified_timeline

        metadata = trace.get("metadata")
        if isinstance(metadata, dict):
            payload["metadata"] = self._sanitize_mapping(metadata)

        return payload

    def _simplify_conversation(self, conversation: Optional[List[Any]]) -> Optional[List[Dict[str, str]]]:
        if not conversation or not isinstance(conversation, list):
            return None

        simplified: List[Dict[str, str]] = []
        for entry in conversation:
            if not isinstance(entry, dict):
                continue
            role = entry.get("role") or "assistant"
            content = self._normalize_content(entry.get("content"))
            if content:
                simplified.append({"role": role, "content": content})
        return simplified or None

    def _normalize_content(self, content: Any) -> Optional[str]:
        if content is None:
            return None
        if isinstance(content, str):
            text = content.strip()
            if text.startswith("{") and text.endswith("}"):
                try:
                    parsed = json.loads(text)
                    return self._normalize_content(parsed)
                except json.JSONDecodeError:
                    return text
            return text
        if isinstance(content, dict):
            transcript = content.get("transcript")
            if isinstance(transcript, list):
                lines: List[str] = []
                for item in transcript:
                    if not isinstance(item, dict):
                        continue
                    user_text = item.get("user")
                    assistant_text = item.get("assistant")
                    if user_text:
                        lines.append(f"User: {user_text}")
                    if assistant_text:
                        lines.append(f"Assistant: {assistant_text}")
                if lines:
                    return "\n".join(lines)
            text_value = content.get("text")
            if isinstance(text_value, str):
                return text_value
            if "content" in content and isinstance(content["content"], str):
                return content["content"]
            return json.dumps(content, ensure_ascii=False)
        if isinstance(content, list):
            joined = "\n".join(
                part for part in (self._normalize_content(item) for item in content) if part
            )
            return joined or None
        return str(content)

    def _simplify_timeline_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        simplified = {
            "type": entry.get("type"),
            "name": entry.get("name"),
            "start_time": entry.get("start_time"),
            "end_time": entry.get("end_time"),
            "duration_ms": entry.get("duration_ms"),
            "level": entry.get("level"),
        }
        actions = entry.get("actions")
        if isinstance(actions, (list, str)) and actions:
            simplified["actions"] = actions
        status = entry.get("status")
        if status:
            simplified["status"] = status
        return {k: v for k, v in simplified.items() if v is not None}

    def _sanitize_mapping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove heavy/raw fields recursively."""

        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if key == "raw" or value is None:
                continue
            cleaned[key] = self._strip_raw_fields(value)
        return cleaned

    def _strip_raw_fields(self, value: Any, depth: int = 0) -> Any:
        if depth > 3:
            return value
        if isinstance(value, dict):
            return {
                k: self._strip_raw_fields(v, depth + 1)
                for k, v in value.items()
                if k != "raw" and v is not None
            }
        if isinstance(value, list):
            return [self._strip_raw_fields(item, depth + 1) for item in value]
        return value


class OverallEvaluator:
    """Analyzes aggregated results (LLM-OV)."""

    def __init__(self, client: ReportLLMClient, config: Dict[str, Any]):
        self.client = client
        self.config = config
        self.eval_config = config.get("evaluation", {})

    async def analyze(self, rule_based_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_prompt(rule_based_data)
        model = self.eval_config.get("advanced", {}).get("llm_judge", {}).get("model", "gpt-4o")

        # Reuse invoke but pass empty system prompt as OV template is self-contained
        output, error = await self.client.invoke("", prompt, model)

        if error:
            logger.error(f"Overall analysis failed: {error}")
            return {"error": error}

        try:
            return parse_json_response(output)
        except json.JSONDecodeError as e:
            logger.error(f"Overall analysis JSON parse error: {e}")
            return {"error": f"JSON parse error: {e}", "raw_output": output}

    def _build_prompt(self, data: Dict[str, Any]) -> str:
        summary = data.get("summary", {})
        perf = data.get("performance", {})
        insights = data.get("insights", {})

        # Prepare sub-JSONs
        aggregated_stats = {
            "pass_rate": summary.get("pass_rate", 0),
            "total_traces": summary.get("total_traces", 0),
            "passed": summary.get("passed", 0),
            "badges": summary.get("badges", []),
            "metric_rows": summary.get("metric_stats", [])
        }

        # Prepare performance stats
        cards = perf.get("cards", [])
        overview_metrics = []
        for card in cards:
            title = card.get("title", "")
            stats = card.get("stats", {})
            if title == "Output Tokens":
                overview_metrics.append({"value": str(stats.get("mean", 0)), "label": "Avg Output Tokens"})
            elif title == "Conversation Depth":
                overview_metrics.append({"value": str(stats.get("mean", 0)), "label": "Avg Conversation Turns"})
            elif title == "Latency":
                overview_metrics.append({"value": f"{stats.get('mean', 0):.1f}s", "label": "Avg Latency"})

        performance_stats = {
            "overview": {
                "metrics": overview_metrics,
                "total_cost": "$0.00", # Placeholder
                "avg_cost_per_trace": "$0.00"
            },
            "cards": cards,
            "persona_gap": perf.get("persona_gap", {})
        }

        # Handle cases where evaluation_goal is a dict
        goal = self.eval_config.get("evaluation_goal", "Evaluate the agent's performance")
        if isinstance(goal, dict):
            goal = goal.get("text", str(goal))
            
        output_lang = self._resolve_output_language()

        return OV_PROMPT_TEMPLATE.format(
            evaluation_goal=goal,
            aggregated_stats=json.dumps(aggregated_stats, ensure_ascii=False, indent=2),
            performance_stats=json.dumps(performance_stats, ensure_ascii=False, indent=2),
            failed_cases=json.dumps(insights.get("fail_cases", []), ensure_ascii=False, indent=2),
            marginal_cases=json.dumps(insights.get("marginal_cases", []), ensure_ascii=False, indent=2),
            review_cases=json.dumps(insights.get("review_cases", []), ensure_ascii=False, indent=2),
            output_language=output_lang
        )

    def _resolve_output_language(self) -> str:
        """
        Determine the preferred language for overall evaluation prompts.

        Mirrors TraceEvaluator logic but without persona metadata fallback.
        """
        report_cfg = self.eval_config.get("report") or {}
        output_cfg = report_cfg.get("output")

        if isinstance(output_cfg, dict):
            lang = output_cfg.get("language")
            if isinstance(lang, str) and lang.strip():
                return lang.strip()

        legacy_lang = report_cfg.get("language")
        if isinstance(legacy_lang, str) and legacy_lang.strip():
            return legacy_lang.strip()

        return "en"

