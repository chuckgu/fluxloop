---
sidebar_position: 4
---

# Evaluation Configuration

Define evaluation criteria, success thresholds, and reporting in `configs/evaluation.yaml`.

## Overview

The evaluation configuration controls how experiment results are scored and reported:

- **Evaluation Goal**: High-level objective description
- **Evaluators**: Rule-based checks and LLM judges that score each trace
- **Aggregation**: How individual scores combine
- **Limits**: Cost controls for LLM evaluations
- **Success Criteria** (Phase 2): Performance, quality, and functionality thresholds
- **Additional Analysis** (Phase 2): Persona breakdowns, outlier detection, trends
- **Report Configuration** (Phase 2): Customizable Markdown and HTML reports
- **Advanced Settings** (Phase 2): Statistical tests, alerts

## File Location

```
fluxloop/my-agent/
└── configs/
    └── evaluation.yaml    # ← This file
```

## Quick Start Example

```yaml
# Minimal evaluation config
evaluators:
  - name: basic_checks
    type: rule_based
    enabled: true
    weight: 1.0
    rules:
      - check: output_not_empty
      - check: success

aggregate:
  method: weighted_sum
  threshold: 0.7
```

---

## Evaluation Goal

**Type:** `object`  
**Phase:** Phase 2

High-level description of evaluation objectives.

```yaml
evaluation_goal:
  text: |
    Verify that the agent provides clear, persona-aware responses
    while meeting latency and accuracy targets.
```

**Purpose:**
- Appears in reports and dashboards
- Guides evaluator selection
- Communicates intent to stakeholders

---

## Evaluators

Evaluators score each trace based on specific criteria.

### Evaluator Types

| Type | Description | Use Case |
|------|-------------|----------|
| `rule_based` | Predefined checks (latency, keywords, etc.) | Objective, deterministic criteria |
| `llm_judge` | LLM scores subjective quality | Relevance, coherence, helpfulness |

### Rule-Based Evaluators

#### Structure

```yaml
evaluators:
  - name: string           # Unique evaluator identifier
    type: rule_based
    enabled: boolean       # Enable/disable
    weight: number         # Importance weight (0.0-1.0)
    rules:                 # List of checks
      - check: string
        ...parameters
```

#### Example

```yaml
- name: completeness
  type: rule_based
  enabled: true
  weight: 0.3
  rules:
    - check: output_not_empty
    - check: success
    - check: latency_under
      budget_ms: 1200
```

#### Available Rule Checks

##### output_not_empty

Verify output field is not empty.

```yaml
- check: output_not_empty
```

**Passes if:**
- `output` field exists and is non-empty string/object

##### success

Verify trace completed successfully.

```yaml
- check: success
```

**Passes if:**
- Trace status is `SUCCESS`
- No errors occurred

##### latency_under

Check execution time under budget.

```yaml
- check: latency_under
  budget_ms: 1000
```

**Parameters:**
- `budget_ms`: Maximum duration in milliseconds

**Passes if:**
- `duration_ms` < `budget_ms`

##### token_usage_under

Check token consumption.

```yaml
- check: token_usage_under
  max_total_tokens: 4000
  max_prompt_tokens: 2000
  max_completion_tokens: 2000
```

**Parameters:**
- `max_total_tokens`: Total token budget
- `max_prompt_tokens`: Input token budget (optional)
- `max_completion_tokens`: Output token budget (optional)

##### contains

Check if target field contains keywords.

```yaml
- check: contains
  target: output
  keywords: ["help", "assist", "support"]
```

**Parameters:**
- `target`: Field to check (`output`, `input`, `metadata.X`)
- `keywords`: List of keywords (case-insensitive)

**Passes if:**
- Target contains ANY keyword

##### not_contains

Check if target field does NOT contain keywords.

```yaml
- check: not_contains
  target: output
  keywords: ["error", "sorry", "unavailable"]
```

**Parameters:**
- `target`: Field to check
- `keywords`: List of forbidden keywords

**Passes if:**
- Target contains NONE of the keywords

##### similarity

Check similarity between target and expected value.

```yaml
- check: similarity
  target: output
  expected_path: metadata.expected
  method: difflib
  threshold: 0.7
```

**Parameters:**
- `target`: Field to compare
- `expected_path`: Path to expected value
- `method`: `difflib` | `levenshtein` | `embedding`
- `threshold`: Minimum similarity (0.0-1.0)

---

### LLM Judge Evaluators

#### Structure

```yaml
evaluators:
  - name: string
    type: llm_judge
    enabled: boolean
    weight: number
    model: string
    model_parameters: object  # Optional
    prompt_template: string
    max_score: number
    parser: string
    metadata: object  # Optional
```

#### Example

```yaml
- name: response_quality
  type: llm_judge
  enabled: true
  weight: 0.5
  model: gpt-4o-mini
  model_parameters:
    reasoning:
      effort: medium
    text:
      verbosity: medium
  prompt_template: |
    Score the assistant's response from 1-10.
    
    User Input: {input}
    Assistant Output: {output}
    
    Consider:
    - Relevance to the question
    - Completeness of answer
    - Clarity and conciseness
    
    Provide only a number from 1-10.
  max_score: 10
  parser: first_number_1_10
  metadata:
    sample_response: "Score: 8"
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | `string` | Yes | LLM model name (e.g., `gpt-4o-mini`) |
| `model_parameters` | `object` | No | Model-specific parameters |
| `prompt_template` | `string` | Yes | Scoring prompt with placeholders |
| `max_score` | `number` | Yes | Maximum possible score |
| `parser` | `string` | Yes | How to extract score from LLM response |
| `metadata` | `object` | No | Additional metadata (sample responses, etc.) |

#### Model Parameters

For models supporting structured outputs (e.g., OpenAI):

```yaml
model_parameters:
  reasoning:
    effort: medium  # low | medium | high
  text:
    verbosity: medium  # low | medium | high
```

#### Prompt Templates

Use placeholders for trace data:

| Placeholder | Description |
|-------------|-------------|
| `{input}` | User input text |
| `{output}` | Agent output text |
| `{persona}` | Persona name |
| `{duration_ms}` | Execution time |
| `{metadata.X}` | Custom metadata field |
| `{observations}` | List of observations |

**Example:**

```yaml
prompt_template: |
  You are evaluating a customer support agent.
  
  Persona: {persona}
  User Question: {input}
  Agent Response: {output}
  Response Time: {duration_ms}ms
  
  Rate the response quality from 1-10 considering:
  1. Accuracy and correctness
  2. Helpfulness and completeness
  3. Appropriate tone for persona
  4. Response time efficiency
  
  Output only a number 1-10.
```

#### Parsers

| Parser | Description | Example Output |
|--------|-------------|----------------|
| `first_number_1_10` | Extract first number 1-10 | "The score is 8" → `8` |
| `json_score` | Parse JSON `{"score": X}` | `{"score": 7}` → `7` |
| `first_float` | Extract first floating point | "Score: 8.5/10" → `8.5` |

---

## Pre-Built Evaluators

FluxLoop provides pre-configured LLM judge evaluators:

### intent_recognition

Scores how well the agent recognized user intent.

```yaml
- name: intent_recognition
  type: llm_judge
  enabled: true
  weight: 0.25
  model: gpt-4o-mini
  prompt_template: |
    # Automatically populated from built-in template
  max_score: 10
  parser: first_number_1_10
```

### response_consistency

Checks if the response is logically consistent.

```yaml
- name: response_consistency
  type: llm_judge
  enabled: true
  weight: 0.25
  model: gpt-4o-mini
  max_score: 10
  parser: first_number_1_10
```

### response_clarity

Evaluates clarity and conciseness.

```yaml
- name: response_clarity
  type: llm_judge
  enabled: true
  weight: 0.2
  model: gpt-4o-mini
  max_score: 10
  parser: first_number_1_10
```

### information_completeness

Checks if all necessary information is provided.

```yaml
- name: information_completeness
  type: llm_judge
  enabled: false  # Disabled by default
  weight: 0.1
  model: gpt-4o-mini
  max_score: 10
  parser: first_number_1_10
```

---

## Aggregation

### aggregate.method

**Type:** `string`  
**Options:** `weighted_sum` | `average`  
**Default:** `weighted_sum`

How to combine evaluator scores.

```yaml
aggregate:
  method: weighted_sum
```

**weighted_sum:**
```
final_score = Σ(evaluator_score × evaluator_weight) / Σ(evaluator_weight)
```

**average:**
```
final_score = Σ(evaluator_score) / count(evaluators)
```

### aggregate.threshold

**Type:** `number`  
**Range:** `0.0-1.0`  
**Default:** `0.7`

Pass/fail threshold.

```yaml
aggregate:
  threshold: 0.75  # 75% to pass
```

**Behavior:**
- `final_score >= threshold` → PASS
- `final_score < threshold` → FAIL

### aggregate.by_persona

**Type:** `boolean`  
**Default:** `true`

Group statistics by persona.

```yaml
aggregate:
  by_persona: true
```

**Enables:**
- Per-persona scores in reports
- Persona-specific analysis
- Identifying persona-specific issues

---

## Limits (Cost Controls)

### limits.sample_rate

**Type:** `number`  
**Range:** `0.0-1.0`  
**Default:** `1.0`

Fraction of traces to evaluate with LLM judges.

```yaml
limits:
  sample_rate: 0.3  # Evaluate 30% of traces
```

**Use Cases:**

| Rate | Use Case |
|------|----------|
| `1.0` | Full evaluation, < 100 traces |
| `0.5` | Moderate sampling, 100-500 traces |
| `0.1-0.3` | Large experiments, 1000+ traces |

### limits.max_llm_calls

**Type:** `integer`  
**Default:** `50`

Maximum LLM API calls.

```yaml
limits:
  max_llm_calls: 100
```

**Stops evaluation after reaching limit to control costs.**

### limits.timeout_seconds

**Type:** `integer`  
**Default:** `60`

Timeout per LLM evaluation call.

```yaml
limits:
  timeout_seconds: 30
```

### limits.cache

**Type:** `string | null`  
**Default:** `evaluation_cache.jsonl`

Cache file for LLM responses.

```yaml
limits:
  cache: evaluation_cache.jsonl
```

**Benefits:**
- Avoid re-evaluating same traces
- Reduce API costs
- Speed up re-runs

---

## Success Criteria (Phase 2)

Define pass/fail thresholds across multiple dimensions.

### Performance Criteria

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
```

| Criterion | Description |
|-----------|-------------|
| `all_traces_successful` | All traces must succeed (no errors) |
| `avg_response_time` | Average latency under threshold |
| `max_response_time` | Maximum latency under threshold |
| `error_rate` | Error percentage under threshold |

### Quality Criteria

```yaml
success_criteria:
  quality:
    intent_recognition: true
    response_consistency: true
    response_clarity: true
    information_completeness: false
```

**Evaluator names that must pass their thresholds.**

### Functionality Criteria

```yaml
success_criteria:
  functionality:
    tool_calling:
      enabled: true
      all_calls_successful: true
      appropriate_selection: true
      correct_parameters: true
      proper_timing: true
      handles_failures: true
```

**Tool calling requirements:**

| Check | Description |
|-------|-------------|
| `all_calls_successful` | All tool calls succeed |
| `appropriate_selection` | Correct tools chosen |
| `correct_parameters` | Valid parameters passed |
| `proper_timing` | Tools called in logical order |
| `handles_failures` | Gracefully handles tool errors |

---

## Additional Analysis (Phase 2)

### Persona Analysis

```yaml
additional_analysis:
  persona:
    enabled: true
    focus_personas: ["expert_user", "novice_user"]
```

**Generates:**
- Per-persona performance breakdown
- Persona-specific failure patterns
- Comparative persona analysis

### Performance Analysis

```yaml
additional_analysis:
  performance:
    detect_outliers: true
    trend_analysis: true
```

**Features:**
- Outlier detection (statistical anomalies)
- Trend analysis over time
- Performance distribution charts

### Failure Analysis

```yaml
additional_analysis:
  failures:
    enabled: true
    categorize_causes: true
```

**Provides:**
- Failure categorization
- Root cause analysis
- Common failure patterns

### Baseline Comparison

```yaml
additional_analysis:
  comparison:
    enabled: true
    baseline_path: "experiments/baseline_v1/evaluation/summary.json"
```

**Compares:**
- Score changes vs baseline
- Performance regression detection
- Improvement/degradation analysis

---

## Report Configuration (Phase 2)

### report.style

**Type:** `string`  
**Options:** `quick` | `standard` | `detailed`  
**Default:** `standard`

Report detail level.

```yaml
report:
  style: standard
```

| Style | Sections | Use Case |
|-------|----------|----------|
| `quick` | Executive summary, key metrics | Quick checks, CI/CD |
| `standard` | + Detailed results, recommendations | Regular testing |
| `detailed` | + Statistical analysis, examples | Deep analysis |

### report.sections

```yaml
report:
  sections:
    executive_summary: true
    key_metrics: true
    detailed_results: true
    statistical_analysis: false
    failure_cases: true
    success_examples: false
    recommendations: true
    action_items: true
```

**Available Sections:**

| Section | Description |
|---------|-------------|
| `executive_summary` | High-level overview |
| `key_metrics` | Core statistics |
| `detailed_results` | Per-evaluator breakdown |
| `statistical_analysis` | Advanced stats |
| `failure_cases` | Failed trace examples |
| `success_examples` | Successful trace examples |
| `recommendations` | Improvement suggestions |
| `action_items` | Specific next steps |

### report.visualizations

```yaml
report:
  visualizations:
    charts_and_graphs: true
    tables: true
    interactive: true
```

**Options:**
- `charts_and_graphs`: Include charts in HTML report
- `tables`: Data tables
- `interactive`: Interactive HTML elements

### report.tone

**Type:** `string`  
**Options:** `technical` | `executive` | `balanced`  
**Default:** `balanced`

Report writing style.

```yaml
report:
  tone: executive
```

| Tone | Audience | Style |
|------|----------|-------|
| `technical` | Engineers | Detailed, metrics-focused |
| `executive` | Leadership | High-level, business impact |
| `balanced` | Mixed | Both technical and business |

### report.output

**Type:** `string`  
**Options:** `md` | `html` | `both`  
**Default:** `both`

Report format(s) to generate.

```yaml
report:
  output: both
```

**Generates:**
- `md`: `report.md` (Markdown)
- `html`: `report.html` (Interactive HTML)
- `both`: Both formats

### report.template_path

**Type:** `string | null`  
**Default:** `null`

Custom HTML template path.

```yaml
report:
  template_path: "templates/custom_report.html"
```

**Use for:**
- Company branding
- Custom visualizations
- Specific formatting requirements

---

## Advanced Settings (Phase 2)

### Statistical Tests

```yaml
advanced:
  statistical_tests:
    enabled: true
    significance_level: 0.05
    confidence_interval: 0.95
```

**Enables:**
- Hypothesis testing
- Confidence intervals
- Statistical significance checks

### Outlier Handling

```yaml
advanced:
  outliers:
    detection: true
    handling: analyze_separately  # remove | analyze_separately | include
```

| Handling | Description |
|----------|-------------|
| `remove` | Exclude outliers from aggregate stats |
| `analyze_separately` | Include but call out in reports |
| `include` | Treat as normal data points |

### Alerts

```yaml
advanced:
  alerts:
    enabled: true
    conditions:
      - metric: "error_rate"
        threshold: 10
        operator: ">"
      - metric: "avg_score"
        threshold: 0.7
        operator: "<"
```

**Alert Conditions:**
- `metric`: Metric to monitor
- `threshold`: Threshold value
- `operator`: `>`, `<`, `>=`, `<=`, `==`

---

## Complete Examples

### Minimal (Quick Start)

```yaml
evaluators:
  - name: basic
    type: rule_based
    enabled: true
    weight: 1.0
    rules:
      - check: output_not_empty
      - check: success

aggregate:
  method: weighted_sum
  threshold: 0.7
```

### Standard Testing

```yaml
evaluation_goal:
  text: "Validate agent provides accurate, helpful responses"

evaluators:
  - name: completeness
    type: rule_based
    enabled: true
    weight: 0.3
    rules:
      - check: output_not_empty
      - check: success
      - check: latency_under
        budget_ms: 2000

  - name: intent_recognition
    type: llm_judge
    enabled: true
    weight: 0.35
    model: gpt-4o-mini
    max_score: 10
    parser: first_number_1_10

  - name: response_clarity
    type: llm_judge
    enabled: true
    weight: 0.35
    model: gpt-4o-mini
    max_score: 10
    parser: first_number_1_10

aggregate:
  method: weighted_sum
  threshold: 0.75
  by_persona: true

limits:
  sample_rate: 0.5
  max_llm_calls: 100
  cache: evaluation_cache.jsonl
```

### Production Validation (Phase 2)

```yaml
evaluation_goal:
  text: |
    Comprehensive validation before production deployment.
    Ensure quality, performance, and reliability targets.

evaluators:
  - name: not_empty
    type: rule_based
    enabled: true
    weight: 0.2
    rules:
      - check: output_not_empty

  - name: token_budget
    type: rule_based
    enabled: true
    weight: 0.2
    rules:
      - check: token_usage_under
        max_total_tokens: 4000

  - name: intent_recognition
    type: llm_judge
    enabled: true
    weight: 0.3
    model: gpt-4o
    max_score: 10
    parser: first_number_1_10

  - name: response_quality
    type: llm_judge
    enabled: true
    weight: 0.3
    model: gpt-4o
    max_score: 10
    parser: first_number_1_10

aggregate:
  method: weighted_sum
  threshold: 0.8
  by_persona: true

limits:
  sample_rate: 1.0
  max_llm_calls: 500
  cache: prod_eval_cache.jsonl

success_criteria:
  performance:
    all_traces_successful: true
    avg_response_time:
      enabled: true
      threshold_ms: 1500
    error_rate:
      enabled: true
      threshold_percent: 2

  quality:
    intent_recognition: true
    response_quality: true

additional_analysis:
  persona:
    enabled: true
  performance:
    detect_outliers: true
    trend_analysis: true
  failures:
    enabled: true
    categorize_causes: true
  comparison:
    enabled: true
    baseline_path: "experiments/baseline/evaluation/summary.json"

report:
  style: detailed
  sections:
    executive_summary: true
    key_metrics: true
    detailed_results: true
    statistical_analysis: true
    failure_cases: true
    recommendations: true
    action_items: true
  visualizations:
    charts_and_graphs: true
    tables: true
    interactive: true
  tone: balanced
  output: both

advanced:
  statistical_tests:
    enabled: true
    significance_level: 0.05
  outliers:
    detection: true
    handling: analyze_separately
  alerts:
    enabled: true
    conditions:
      - metric: "error_rate"
        threshold: 5
        operator: ">"
```

---

## See Also

- [evaluate Command](/cli/commands/evaluate) - Evaluation CLI reference
- [Basic Workflow](/cli/workflows/basic-workflow) - Complete workflow guide
- [Simulation Configuration](/cli/configuration/simulation-config) - Experiment settings
- [Input Configuration](/cli/configuration/input-config) - Input generation
