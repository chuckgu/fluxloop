# fluxloop criteria

Manage evaluation criteria.

## Synopsis

```bash
fluxloop criteria [command] [options]
```

## Description

The `criteria` command manages evaluation criteria for test scenarios. Criteria define what makes a test pass or fail.

## Commands

### `fluxloop criteria list`

List all evaluation criteria.

**Usage:**

```bash
fluxloop criteria list [options]
```

**Options:**

- `--scenario <name>`: List criteria for specific scenario
- `--type <type>`: Filter by criteria type
- `--json`: Output in JSON format

**Examples:**

```bash
# List all criteria
fluxloop criteria list

# List criteria for specific scenario
fluxloop criteria list --scenario password-reset

# List criteria of specific type
fluxloop criteria list --type contains
```

**Output:**

```
Evaluation Criteria

Scenario: password-reset
┌──────────────────────────────────────────────────────────────────┐
│ contains-reset-link                                              │
│ Type: contains                                                   │
│ Field: response                                                  │
│ Value: "reset link"                                              │
│ Required: Yes | Weight: 0.3                                      │
│ Pass rate: 95% (last 30 days)                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ response-time                                                    │
│ Type: response_time                                              │
│ Threshold: < 3000ms                                              │
│ Required: Yes | Weight: 0.2                                      │
│ Pass rate: 82% (last 30 days)                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ empathy-check                                                    │
│ Type: sentiment                                                  │
│ Min score: 0.6                                                   │
│ Required: No | Weight: 0.3                                       │
│ Pass rate: 78% (last 30 days)                                   │
└──────────────────────────────────────────────────────────────────┘

Total: 4 criteria
```

### `fluxloop criteria create`

Create a new evaluation criterion.

**Usage:**

```bash
fluxloop criteria create [options]
```

**Options:**

- `--scenario <name>`: Scenario to add criterion to (required)
- `--type <type>`: Criterion type (required)
- `--name <name>`: Criterion name/ID
- `--required`: Mark as required (default: true)
- `--weight <weight>`: Weight for scoring (0.0-1.0, default: 1.0)

**Type-specific options:**

For `contains` type:
- `--field <field>`: Field to check (response, metadata, etc.)
- `--value <value>`: Value to search for

For `response_time` type:
- `--threshold <ms>`: Max response time in milliseconds

For `sentiment` type:
- `--min-score <score>`: Minimum sentiment score (0.0-1.0)

For `regex` type:
- `--pattern <regex>`: Regular expression pattern

**Examples:**

```bash
# Create "contains" criterion
fluxloop criteria create \
  --scenario password-reset \
  --type contains \
  --name "mentions-email" \
  --field response \
  --value "email"

# Create response time criterion
fluxloop criteria create \
  --scenario password-reset \
  --type response_time \
  --threshold 3000 \
  --required

# Create sentiment criterion
fluxloop criteria create \
  --scenario password-reset \
  --type sentiment \
  --min-score 0.6 \
  --weight 0.3

# Create regex criterion
fluxloop criteria create \
  --scenario order-tracking \
  --type regex \
  --name "order-number-format" \
  --pattern "^#[0-9]{6}$"
```

**Interactive Flow:**

```
$ fluxloop criteria create --scenario password-reset

Create Evaluation Criterion

Scenario: password-reset

Criterion types:
  1. contains - Response contains specific text
  2. not_contains - Response doesn't contain text
  3. response_time - Response time under threshold
  4. sentiment - Sentiment analysis score
  5. regex - Regular expression match
  6. json_schema - JSON schema validation
  7. custom - Custom evaluation function

Select type (1-7): 1

Field to check:
  1. response - Agent response text
  2. metadata - Response metadata
  3. tool_calls - Tool invocations
  4. all - All fields

Select field (1-4): 1

Value to search for: reset link

Criterion name (optional): contains-reset-link

Required? (y/n): y

Weight (0.0-1.0, default 1.0): 0.3

✅ Criterion created: contains-reset-link

Criterion added to: scenarios/password-reset.yaml

Next steps:
• Run test to validate: fluxloop test --scenario password-reset
• View criteria: fluxloop criteria list --scenario password-reset
```

### `fluxloop criteria show`

Display details for a specific criterion.

**Usage:**

```bash
fluxloop criteria show <criterion-id> [options]
```

**Options:**

- `--scenario <name>`: Scenario containing the criterion (required)
- `--json`: Output in JSON format

**Examples:**

```bash
# Show criterion details
fluxloop criteria show contains-reset-link \
  --scenario password-reset
```

**Output:**

```
Criterion: contains-reset-link

Scenario: password-reset
Type: contains
Field: response
Value: "reset link"

Configuration:
  Required: Yes
  Weight: 0.3
  Case sensitive: No

Performance (Last 30 days):
  Tests run: 156
  Passed: 148 (95%)
  Failed: 8 (5%)

  Avg check time: 12ms

Recent failures:
  • Jan 15 14:30 - "password reset" (missing "link")
  • Jan 14 11:20 - "sent reset email" (missing "link")
  • Jan 13 16:45 - "check your inbox" (missing "reset link")

Suggestions:
  • Consider accepting variations: "reset email", "reset message"
  • Current strict matching may be too rigid
  • 5% failure rate is within acceptable range
```

### `fluxloop criteria update`

Update an existing criterion.

**Usage:**

```bash
fluxloop criteria update <criterion-id> [options]
```

**Options:**

- `--scenario <name>`: Scenario containing the criterion (required)
- `--required <bool>`: Update required flag
- `--weight <weight>`: Update weight
- `--value <value>`: Update value (for contains/regex types)
- `--threshold <ms>`: Update threshold (for response_time type)

**Examples:**

```bash
# Update criterion weight
fluxloop criteria update contains-reset-link \
  --scenario password-reset \
  --weight 0.5

# Make criterion optional
fluxloop criteria update empathy-check \
  --scenario password-reset \
  --required false

# Update threshold
fluxloop criteria update response-time \
  --scenario password-reset \
  --threshold 5000
```

### `fluxloop criteria delete`

Delete a criterion.

**Usage:**

```bash
fluxloop criteria delete <criterion-id> [options]
```

**Options:**

- `--scenario <name>`: Scenario containing the criterion (required)
- `--force`: Skip confirmation prompt

**Examples:**

```bash
# Delete criterion (with confirmation)
fluxloop criteria delete old-criterion \
  --scenario password-reset

# Delete without confirmation
fluxloop criteria delete old-criterion \
  --scenario password-reset \
  --force
```

### `fluxloop criteria pull`

Pull criteria from the cloud.

**Usage:**

```bash
fluxloop criteria pull [options]
```

**Options:**

- `--scenario <name>`: Pull criteria for specific scenario
- `--all`: Pull criteria for all scenarios (default)

**Examples:**

```bash
# Pull all criteria
fluxloop criteria pull

# Pull criteria for specific scenario
fluxloop criteria pull --scenario password-reset
```

### `fluxloop criteria push`

Push criteria to the cloud.

**Usage:**

```bash
fluxloop criteria push [options]
```

**Options:**

- `--scenario <name>`: Push criteria for specific scenario
- `--all`: Push criteria for all scenarios (default)

**Examples:**

```bash
# Push all criteria
fluxloop criteria push

# Push criteria for specific scenario
fluxloop criteria push --scenario password-reset
```

## Criterion Types

### 1. Contains

Check if response contains specific text:

```yaml
- id: contains-reset-link
  type: contains
  field: response
  value: "reset link"
  required: true
  weight: 0.3
  case_sensitive: false
```

### 2. Not Contains

Check if response doesn't contain specific text:

```yaml
- id: no-error-messages
  type: not_contains
  field: response
  value: ["error", "failed", "cannot"]
  required: true
  weight: 0.2
```

### 3. Response Time

Check if response time is under threshold:

```yaml
- id: response-time
  type: response_time
  threshold_ms: 3000
  required: true
  weight: 0.2
```

### 4. Sentiment

Analyze sentiment of response:

```yaml
- id: empathy-check
  type: sentiment
  min_score: 0.6
  max_score: 1.0
  required: false
  weight: 0.3
```

### 5. Regex

Match response against regular expression:

```yaml
- id: order-number-format
  type: regex
  field: response
  pattern: "#[0-9]{6}"
  required: true
  weight: 0.3
```

### 6. JSON Schema

Validate JSON response structure:

```yaml
- id: api-response-schema
  type: json_schema
  schema:
    type: object
    required: ["status", "data"]
    properties:
      status:
        type: string
        enum: ["success", "error"]
      data:
        type: object
  required: true
  weight: 0.4
```

### 7. Custom Function

Custom evaluation logic:

```yaml
- id: custom-validation
  type: custom
  function: |
    def evaluate(response, context):
        # Custom validation logic
        if "password" in response.lower():
            if "reset" in response.lower():
                return True, "Mentions password reset"
            else:
                return False, "Mentions password but not reset"
        return False, "Doesn't mention password"
  required: true
  weight: 0.3
```

## Criteria File Format

Criteria are typically embedded in scenario files:

```yaml
# scenarios/password-reset.yaml
name: password-reset
description: Test password reset flow

personas:
  - frustrated-user
  - tech-savvy-user

inputs:
  - "I can't login"
  - "Forgot my password"

criteria:
  - id: contains-reset-link
    type: contains
    field: response
    value: "reset link"
    required: true
    weight: 0.3
    description: "Agent mentions sending a reset link"

  - id: response-time
    type: response_time
    threshold_ms: 3000
    required: true
    weight: 0.2
    description: "Response within 3 seconds"

  - id: empathy-check
    type: sentiment
    min_score: 0.6
    required: false
    weight: 0.3
    description: "Empathetic and helpful tone"

  - id: follow-up-offered
    type: contains
    field: response
    value: ["help", "contact", "support", "assist"]
    required: false
    weight: 0.2
    description: "Offers additional help"
```

## Best Practices

### 1. Balance Required and Optional

```yaml
criteria:
  # Required criteria (must pass)
  - id: core-functionality
    required: true
    weight: 0.5

  # Optional criteria (nice to have)
  - id: extra-feature
    required: false
    weight: 0.2
```

### 2. Use Appropriate Weights

```yaml
criteria:
  # Critical (high weight)
  - id: security-check
    weight: 0.4

  # Important (medium weight)
  - id: functionality-check
    weight: 0.3

  # Nice-to-have (low weight)
  - id: tone-check
    weight: 0.1
```

### 3. Provide Clear Descriptions

```yaml
- id: mentions-timeline
  type: contains
  value: ["minutes", "hours", "shortly", "soon"]
  description: |
    Agent provides a timeline for resolution.
    Helps set user expectations.
    Pass examples: "within 10 minutes", "shortly"
    Fail examples: no timeline mentioned
```

### 4. Test Criteria Independently

```bash
# Test single criterion
fluxloop test \
  --scenario password-reset \
  --criterion contains-reset-link
```

### 5. Monitor Criterion Performance

```bash
# View criterion statistics
fluxloop criteria show contains-reset-link \
  --scenario password-reset
```

## Troubleshooting

### Criterion Always Fails

```
⚠️  Warning: Criterion 'contains-reset-link' has 0% pass rate

Scenario: password-reset
Tests run: 10
Passed: 0 (0%)

Recent responses:
  • "I've sent a password reset email"
  • "Check your inbox for reset instructions"
  • "You'll receive a reset message shortly"

Suggestion:
  • Value "reset link" is too specific
  • Consider accepting variations: ["reset", "password reset"]
  • Or use regex: "reset.*(link|email|message)"
```

### Criterion Too Lenient

```
⚠️  Warning: Criterion 'mentions-help' has 100% pass rate

This criterion might be too lenient and not providing value.

Suggestion:
  • Review criterion requirements
  • Make it more specific
  • Or remove if not needed
```

## Related Commands

- [`fluxloop test`](./test): Run tests with criteria
- [`fluxloop scenarios`](./scenarios): Manage scenarios
- [`fluxloop sync`](./sync): Sync criteria with cloud

## See Also

- [Evaluation Guide](../guides/evaluation): Writing effective criteria
- [Testing Best Practices](../guides/testing-best-practices): Testing strategies
