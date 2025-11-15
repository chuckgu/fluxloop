---
sidebar_position: 4
---

# Evaluation Configuration

Define how FluxLoop evaluates experiment outputs in `configs/evaluation.yaml`.

## Overview

Evaluation configuration controls:

- **Evaluators**: Rule-based checks and LLM judges that score each trace
- **Aggregation**: How individual evaluator scores combine into a final score
- **Limits**: Cost and performance controls for LLM evaluations
- **Success Criteria** (Phase 2): Performance, quality, and functionality thresholds
- **Additional Analysis** (Phase 2): Persona breakdowns, outlier detection, baseline comparison
- **Reporting** (Phase 2): Markdown and HTML report customization

## Basic Structure (Phase 1)

```yaml
evaluators:
  - name: completeness
    type: rule_based
    enabled: true
    weight: 1.0
    rules:
      - check: output_not_empty
      - check: latency_under
        budget_ms: 1000

  - name: response_quality
    type: llm_judge
    enabled: false
    weight: 0.5
    model: gpt-5-mini
    prompt_template: |
      Score the assistant's response from 1-10.
      Input: {input}
      Output: {output}
    max_score: 10
    parser: first_number_1_10

aggregate:
  method: weighted_sum
  threshold: 0.7
  by_persona: true

limits:
  sample_rate: 0.3
  max_llm_calls: 50
  timeout_seconds: 60
  cache: evaluation_cache.jsonl
```

## Evaluators

### Rule-Based Evaluators

Check trace data against predefined rules:

```yaml
- name: completeness
  type: rule_based
  enabled: true
  weight: 1.0
  rules:
    - check: output_not_empty
    - check: success
    - check: latency_under
      budget_ms: 1200
    - check: contains
      target: output
      keywords: ["help", "assist"]
    - check: not_contains
      target: output
      keywords: ["error", "sorry"]
    - check: similarity
      target: output
      expected_path: metadata.expected
      method: difflib
```

#### Available Checks

| Check | Parameters | Description |
|-------|------------|-------------|
| `output_not_empty` | None | Output field must be non-empty |
| `success` | None | Trace success flag must be true |
| `latency_under` | `budget_ms` | duration_ms must be < budget |
| `contains` | `target`, `keywords` | Target field contains any keyword |
| `not_contains` | `target`, `keywords` | Target field contains no keywords |
| `similarity` | `target`, `expected_path`, `method` | Similarity score between target and expected |

### LLM Judge Evaluators

Use language models to score subjective quality:

```yaml
- name: semantic_quality
  type: llm_judge
  enabled: true
  weight: 0.7
  model: gpt-5-mini
  prompt_template: |
    You are an expert judge. Score the assistant's response from 1-10.
    
    User Input: {input}
    Agent Output: {output}
    
    Consider:
    - Relevance to the user's question
    - Completeness of the answer
    - Clarity and coherence
    
    Respond with: "Score: <number>/10" and a brief reason.
  max_score: 10
  parser: first_number_1_10
  model_parameters:
    reasoning:
      effort: medium
    text:
      verbosity: medium
```

#### Supported Parsers

| Parser | Expected Format | Example |
|--------|----------------|---------|
| `first_number_1_10` | Any text with number 1-10 | `"Score: 8/10"` → 0.8 |
| `json_score` | `{"score": N}` | `{"score": 7}` → 0.7 |
| `regex_score` | Custom pattern | Configurable |

## Aggregation

Combine evaluator scores into a single final score:

```yaml
aggregate:
  method: weighted_sum  # or "average"
  threshold: 0.7        # Pass/fail threshold
  by_persona: true      # Group stats by persona
```

### Methods

- **`weighted_sum`**: `final_score = Σ(evaluator_score × weight) / Σ(weight)`
- **`average`**: `final_score = Σ(evaluator_score) / count`

#### GPT-5 parameter compatibility

- `gpt-5` 계열은 `temperature`, `top_p`, `logprobs` 파라미터를 지원하지 않습니다. 해당 필드를 포함하면 호출이 실패합니다.
- 대신 아래 컨트롤을 사용하세요.
  - `reasoning: { effort: "minimal" | "low" | "medium" | "high" }`
  - `text: { verbosity: "low" | "medium" | "high" }`
  - `max_output_tokens` (선택값, 응답 길이 제한이 필요할 때만 설정)
- 복잡한 평가 작업(o3·o4-mini 계열을 사용하던 작업 등)은 `gpt-5` 모델 + `reasoning.effort: high`로 대체하면 더 나은 추론 품질을 기대할 수 있습니다.

```python
from openai import OpenAI

client = OpenAI()

result = client.responses.create(
    model="gpt-5",
    input="Find the null pointer exception: ...your code here...",
    reasoning={"effort": "high"},
)

print(result.output_text)
```

## Limits

Control LLM evaluation costs:

```yaml
limits:
  sample_rate: 0.3        # Evaluate 30% of traces with LLM
  max_llm_calls: 50       # Cap total LLM API calls
  timeout_seconds: 60     # Per-LLM-call timeout
  cache: evaluation_cache.jsonl  # Cache file for LLM results
```

## Phase 2: Extended Configuration

### Evaluation Goal

Describe the evaluation purpose (appears in reports):

```yaml
evaluation_goal:
  text: |
    Verify that the customer support agent provides accurate,
    persona-aware responses with average latency below 2 seconds.
```

### Success Criteria

Define pass/fail conditions beyond simple threshold:

```yaml
success_criteria:
  performance:
    all_traces_successful: true
    avg_response_time:
      enabled: true
      threshold_ms: 2000
    max_response_time:
      enabled: true
      threshold_ms: 5000
    error_rate:
      enabled: true
      threshold_percent: 5

  quality:
    intent_recognition: true       # Requires matching evaluator
    response_consistency: true
    response_clarity: true
    information_completeness: false

  functionality:
    tool_calling:
      enabled: false
      all_calls_successful: true
      appropriate_selection: true
      correct_parameters: true
      proper_timing: false
      handles_failures: false
```

### Additional Analysis

Enable advanced analytics:

```yaml
additional_analysis:
  persona:
    enabled: true
    focus_personas: ["expert_user", "novice_user"]

  performance:
    detect_outliers: true
    trend_analysis: true

  failures:
    enabled: true
    categorize_causes: true

  comparison:
    enabled: true
    baseline_path: "experiments/baseline_run/summary.json"
```

### Report Configuration

Customize output format and content:

```yaml
report:
  style: detailed  # quick | standard | detailed
  
  sections:
    executive_summary: true
    key_metrics: true
    detailed_results: true
    statistical_analysis: false
    failure_cases: true
    success_examples: false
    recommendations: true
    action_items: true
  
  visualizations:
    charts_and_graphs: true
    tables: true
    interactive: true
  
  tone: balanced  # technical | executive | balanced
  output: both    # md | html | both
  template_path: null  # Custom HTML template path
```

### Advanced Settings

Fine-tune analysis behavior:

```yaml
advanced:
  statistical_tests:
    enabled: false
    significance_level: 0.05
    confidence_interval: 0.95
  
  outliers:
    detection: true
    handling: analyze_separately  # remove | analyze_separately | include
  
  alerts:
    enabled: false
    conditions:
      - metric: "error_rate"
        threshold: 10
        operator: ">"
```

## Complete Example

See the [evaluate command documentation](../commands/evaluate.md) for complete configuration examples and CLI usage.

## Generated Files

After running `fluxloop evaluate experiment`, the output directory contains:

```
evaluation/
├── summary.json          # Aggregate statistics + Phase 2 analysis
├── per_trace.jsonl       # Per-trace scores and reasons
├── report.md             # Markdown report
└── report.html           # Interactive HTML report (Phase 2)
```

## Best Practices

1. **Start simple**: Begin with rule-based evaluators only
2. **Enable LLM gradually**: Use low `sample_rate` (0.1-0.3) initially
3. **Monitor costs**: Set `max_llm_calls` to prevent runaway expenses
4. **Cache results**: Keep `cache` enabled to avoid re-evaluation
5. **Use personas**: Enable `by_persona: true` to identify persona-specific issues
6. **Iterate on thresholds**: Adjust `aggregate.threshold` based on actual results
7. **Leverage Phase 2 analysis**: Enable outlier detection and trend analysis for deeper insights

## Related

- [evaluate Command](../commands/evaluate.md)
- [Basic Workflow](../workflows/basic-workflow.md)
