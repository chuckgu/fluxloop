# fluxloop inputs

Generate and manage test inputs.

## Synopsis

```bash
fluxloop inputs [command] [options]
```

## Description

The `inputs` command generates and manages test inputs. Inputs are the messages or data that personas will send to your agent during testing.

## Commands

### `fluxloop inputs generate`

Generate test inputs using AI.

**Usage:**

```bash
fluxloop inputs generate [options]
```

**Options:**

- `--persona <name>`: Generate inputs for specific persona (required unless --description is provided)
- `--description <desc>`: Description of inputs to generate
- `--count <n>`: Number of inputs to generate (default: 10)
- `--output <path>`: Output file path (default: .fluxloop/inputs.yaml)
- `--model <model>`: AI model to use (default: claude-3-sonnet)
- `--variety <level>`: Input variety: low, medium, high (default: medium)

**Examples:**

```bash
# Generate inputs for a specific persona
fluxloop inputs generate \
  --persona frustrated-customer \
  --count 10

# Generate inputs from description
fluxloop inputs generate \
  --description "Password reset requests from angry users" \
  --count 15

# Generate varied inputs
fluxloop inputs generate \
  --persona tech-savvy-user \
  --variety high \
  --count 20
```

**Interactive Flow:**

```
$ fluxloop inputs generate --persona frustrated-customer --count 10

Generating inputs for persona: frustrated-customer...

✨ Generated 10 inputs:

1. "I can't login! This is ridiculous!"
2. "I've been trying for 30 minutes, nothing works"
3. "Need help NOW! Can't access my account"
4. "This is the worst service I've ever experienced"
5. "I want my money back if this doesn't get fixed"
6. "WHY is this so complicated?!"
7. "I need to speak with someone who can actually help"
8. "Tried everything, still broken"
9. "This is unacceptable! Fix it immediately"
10. "I'm about to switch to your competitor"

✅ Inputs saved to: .fluxloop/inputs.yaml

Next steps:
• Review and edit inputs if needed
• Create a scenario: fluxloop scenarios create
• Or create a bundle: fluxloop bundles create
```

### `fluxloop inputs list`

List all available inputs.

**Usage:**

```bash
fluxloop inputs list [options]
```

**Options:**

- `--file <path>`: Inputs file to list from (default: .fluxloop/inputs.yaml)
- `--persona <name>`: Filter by persona
- `--json`: Output in JSON format

**Examples:**

```bash
# List all inputs
fluxloop inputs list

# List inputs for specific persona
fluxloop inputs list --persona frustrated-customer

# List from specific file
fluxloop inputs list --file inputs/custom.yaml
```

### `fluxloop inputs add`

Manually add a test input.

**Usage:**

```bash
fluxloop inputs add [options]
```

**Options:**

- `--text <text>`: Input text (required)
- `--persona <name>`: Associated persona
- `--tags <tags>`: Comma-separated list of tags
- `--file <path>`: Inputs file (default: .fluxloop/inputs.yaml)

**Examples:**

```bash
# Add a single input
fluxloop inputs add \
  --text "I forgot my password" \
  --persona frustrated-customer

# Add input with tags
fluxloop inputs add \
  --text "How do I reset my password?" \
  --persona tech-savvy-user \
  --tags password,auth,reset
```

### `fluxloop inputs edit`

Edit inputs manually.

**Usage:**

```bash
fluxloop inputs edit [options]
```

**Options:**

- `--file <path>`: Inputs file to edit (default: .fluxloop/inputs.yaml)
- `--editor <editor>`: Editor to use (default: $EDITOR)

**Examples:**

```bash
# Edit inputs in default editor
fluxloop inputs edit

# Edit with specific editor
fluxloop inputs edit --editor vim
```

### `fluxloop inputs validate`

Validate inputs file format.

**Usage:**

```bash
fluxloop inputs validate [options]
```

**Options:**

- `--file <path>`: Inputs file to validate (default: .fluxloop/inputs.yaml)

**Examples:**

```bash
# Validate inputs file
fluxloop inputs validate

# Validate specific file
fluxloop inputs validate --file inputs/custom.yaml
```

### `fluxloop inputs augment`

Augment existing inputs with variations.

**Usage:**

```bash
fluxloop inputs augment [options]
```

**Options:**

- `--file <path>`: Inputs file to augment (default: .fluxloop/inputs.yaml)
- `--factor <n>`: Augmentation factor (default: 2, creates 2x inputs)
- `--variation <type>`: Type of variation (paraphrase, typo, tone, length)

**Examples:**

```bash
# Double inputs with paraphrases
fluxloop inputs augment --factor 2

# Add typo variations
fluxloop inputs augment --variation typo

# Create shorter versions
fluxloop inputs augment --variation length
```

## Input File Format

Inputs are defined in YAML format:

```yaml
# .fluxloop/inputs.yaml
inputs:
  - id: input-001
    text: "I can't login! This is ridiculous!"
    persona: frustrated-customer
    tags:
      - authentication
      - urgent
      - negative_sentiment
    metadata:
      sentiment: negative
      urgency: high
      complexity: low

  - id: input-002
    text: "I've been trying for 30 minutes, nothing works"
    persona: frustrated-customer
    tags:
      - authentication
      - repeated_attempt
      - negative_sentiment
    metadata:
      sentiment: negative
      urgency: high
      complexity: low
      context:
        previous_attempts: 10+
        duration: 30min

  - id: input-003
    text: "Getting error code 500 when trying to reset password"
    persona: tech-savvy-user
    tags:
      - authentication
      - technical
      - error_report
    metadata:
      sentiment: neutral
      urgency: medium
      complexity: medium
      technical_details:
        error_code: 500
        action: password_reset

  - id: input-004
    text: |
      Hello, I'm having some trouble with my account.
      Could you please help me reset my password?
      Thank you for your assistance.
    persona: elderly-customer
    tags:
      - authentication
      - polite
      - needs_guidance
    metadata:
      sentiment: neutral
      urgency: low
      complexity: low
      multiline: true
```

## Input Variations

### Paraphrase Variations

Generate semantically similar inputs:

```bash
fluxloop inputs augment --variation paraphrase
```

Original:
- "I can't login"

Variations:
- "Unable to sign in"
- "Login not working"
- "Can't access my account"

### Typo Variations

Add realistic typos:

```bash
fluxloop inputs augment --variation typo
```

Original:
- "I forgot my password"

Variations:
- "I fogot my password"
- "I forgot my passwrd"
- "I forgot my passowrd"

### Tone Variations

Change communication tone:

```bash
fluxloop inputs augment --variation tone
```

Original (neutral):
- "I need to reset my password"

Variations:
- Polite: "Could you please help me reset my password?"
- Urgent: "NEED PASSWORD RESET NOW!"
- Casual: "Hey, gotta reset my password"

### Length Variations

Create shorter/longer versions:

```bash
fluxloop inputs augment --variation length
```

Original:
- "I can't login to my account"

Variations:
- Short: "Can't login"
- Long: "I'm having trouble logging in to my account and need assistance"

## AI Generation Options

### Variety Levels

Control input diversity:

- **low**: Similar inputs with minor variations
- **medium**: Balanced mix of different input types (default)
- **high**: Maximum variety in phrasing and approach

```bash
# Generate highly varied inputs
fluxloop inputs generate \
  --persona frustrated-customer \
  --variety high
```

### Model Selection

Choose AI model for generation:

- `claude-3-opus`: Most creative and diverse
- `claude-3-sonnet`: Balanced quality and speed (default)
- `claude-3-haiku`: Fast and economical

```bash
# Use Opus for maximum variety
fluxloop inputs generate \
  --persona tech-savvy-user \
  --model claude-3-opus \
  --count 50
```

## Best Practices

### 1. Generate Sufficient Volume

Create enough inputs to cover edge cases:

```bash
# Generate 50+ inputs per persona
fluxloop inputs generate \
  --persona frustrated-customer \
  --count 50
```

### 2. Include Edge Cases

Manually add edge case inputs:

```bash
# Empty input
fluxloop inputs add --text ""

# Very long input
fluxloop inputs add --text "$(cat long-text.txt)"

# Special characters
fluxloop inputs add --text "!@#$%^&*()"

# Multiple languages
fluxloop inputs add --text "Ich kann mich nicht anmelden"
```

### 3. Tag Appropriately

Use tags for filtering:

```yaml
inputs:
  - text: "Can't login"
    tags:
      - authentication
      - error
      - urgent
      - requires_validation
```

### 4. Add Metadata

Include useful metadata:

```yaml
inputs:
  - text: "Getting error 500"
    metadata:
      error_code: 500
      expected_response: troubleshooting_steps
      should_escalate: false
      complexity: medium
```

### 5. Test Realistic Scenarios

Include realistic user behaviors:

```yaml
inputs:
  # Incomplete information
  - text: "It's broken"

  # Multiple issues
  - text: "Can't login AND forgot password"

  # Spam/abuse
  - text: "asdfghjkl"

  # Copy-pasted errors
  - text: "Error: Uncaught TypeError at line 42"
```

## Multi-turn Inputs

For multi-turn conversations:

```yaml
# .fluxloop/inputs.yaml
multi_turn_inputs:
  - id: conversation-001
    persona: frustrated-customer
    turns:
      - text: "I can't login"
        expected_response_type: request_details

      - text: "Already tried resetting password"
        expected_response_type: offer_alternative

      - text: "Nothing works!"
        expected_response_type: escalation_or_patience

  - id: conversation-002
    persona: tech-savvy-user
    turns:
      - text: "Getting error 500 on login"
        expected_response_type: request_technical_details

      - text: "Request ID: abc123, timestamp: 2024-01-15 14:30"
        expected_response_type: investigation_acknowledgment

      - text: "Any updates?"
        expected_response_type: status_update
```

## Troubleshooting

### Generation Failed

```
❌ Error: Failed to generate inputs

Possible causes:
  • API key expired
  • Rate limit exceeded
  • Invalid persona reference

Solution:
  • Check authentication: fluxloop auth status
  • Wait a few minutes and retry
  • Verify persona exists: fluxloop personas list
```

### Invalid Input Format

```
❌ Error: Invalid input file format

File: .fluxloop/inputs.yaml
Line 15: Missing required field 'text'

Solution:
  • Check YAML syntax
  • Ensure all inputs have 'text' field
  • Run: fluxloop inputs validate
```

## Related Commands

- [`fluxloop personas generate`](./personas): Generate personas
- [`fluxloop bundles create`](./bundles): Bundle inputs with personas
- [`fluxloop scenarios create`](./scenarios): Create scenarios with inputs

## See Also

- [Synthetic Input Generation](../guides/synthetic-input-generation): Input generation guide
- [Testing Best Practices](../guides/testing-best-practices): Testing strategies
