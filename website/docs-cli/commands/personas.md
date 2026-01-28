# fluxloop personas

Generate and manage test personas.

## Synopsis

```bash
fluxloop personas [command] [options]
```

## Description

The `personas` command generates and manages test personas. Personas represent different types of users with distinct characteristics, behaviors, and communication styles.

## Commands

### `fluxloop personas generate`

Generate personas using AI.

**Usage:**

```bash
fluxloop personas generate [options]
```

**Options:**

- `--description <desc>`: Description of what personas to generate (required)
- `--count <n>`: Number of personas to generate (default: 3)
- `--output <path>`: Output file path (default: .fluxloop/personas.yaml)
- `--model <model>`: AI model to use (default: claude-3-sonnet)
- `--diversity <level>`: Diversity level: low, medium, high (default: medium)

**Examples:**

```bash
# Generate 3 customer support personas
fluxloop personas generate \
  --description "Customer support scenarios for e-commerce" \
  --count 3

# Generate diverse personas
fluxloop personas generate \
  --description "Software development team members" \
  --count 5 \
  --diversity high

# Save to specific file
fluxloop personas generate \
  --description "Healthcare patient types" \
  --output personas/healthcare.yaml
```

**Interactive Flow:**

```
$ fluxloop personas generate --description "E-commerce customer support"

Generating personas...

✨ Generated 3 personas:

┌──────────────────────────────────────────────────────────────────┐
│ 1. frustrated-customer                                           │
│                                                                  │
│ Demographics:                                                    │
│   Age: 35-50                                                     │
│   Tech Comfort: Low                                              │
│   Urgency: High                                                  │
│                                                                  │
│ Characteristics:                                                 │
│   • Impatient and stressed                                       │
│   • Expects immediate resolution                                 │
│   • May be emotional or upset                                    │
│   • Prefers simple, direct communication                         │
│                                                                  │
│ Communication Style:                                             │
│   • Short, urgent messages                                       │
│   • May use exclamation marks                                    │
│   • Focuses on problem, not pleasantries                         │
│                                                                  │
│ Example messages:                                                │
│   - "I need help NOW!"                                           │
│   - "This isn't working and I'm very upset"                      │
│   - "I want to speak to a manager"                               │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ 2. tech-savvy-user                                               │
│                                                                  │
│ Demographics:                                                    │
│   Age: 25-35                                                     │
│   Tech Comfort: High                                             │
│   Urgency: Medium                                                │
│                                                                  │
│ Characteristics:                                                 │
│   • Comfortable with technology                                  │
│   • May have already tried troubleshooting                       │
│   • Provides detailed information                                │
│   • Appreciates technical explanations                           │
│                                                                  │
│ Communication Style:                                             │
│   • Clear and concise                                            │
│   • Includes error messages or codes                             │
│   • Asks specific questions                                      │
│                                                                  │
│ Example messages:                                                │
│   - "Getting error code 500 when checking out"                   │
│   - "Already cleared cache, still not working"                   │
│   - "Can you check the server logs?"                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ 3. elderly-customer                                              │
│                                                                  │
│ Demographics:                                                    │
│   Age: 65+                                                       │
│   Tech Comfort: Low                                              │
│   Urgency: Low                                                   │
│                                                                  │
│ Characteristics:                                                 │
│   • Needs patient guidance                                       │
│   • May not understand technical terms                           │
│   • Appreciates step-by-step instructions                        │
│   • Polite and courteous                                         │
│                                                                  │
│ Communication Style:                                             │
│   • Formal and polite                                            │
│   • May include unnecessary details                              │
│   • Asks clarifying questions                                    │
│                                                                  │
│ Example messages:                                                │
│   - "Hello, I'm having trouble with the website"                 │
│   - "Could you please explain that again?"                       │
│   - "Thank you for your patience"                                │
└──────────────────────────────────────────────────────────────────┘

✅ Personas saved to: .fluxloop/personas.yaml

Next steps:
• Review and edit personas if needed
• Generate inputs: fluxloop inputs generate
• Create scenario: fluxloop scenarios create
```

### `fluxloop personas list`

List all available personas.

**Usage:**

```bash
fluxloop personas list [options]
```

**Options:**

- `--file <path>`: Personas file to list from (default: .fluxloop/personas.yaml)
- `--json`: Output in JSON format

**Examples:**

```bash
# List personas
fluxloop personas list

# List from specific file
fluxloop personas list --file personas/custom.yaml
```

### `fluxloop personas show`

Display details for a specific persona.

**Usage:**

```bash
fluxloop personas show <name> [options]
```

**Options:**

- `--file <path>`: Personas file (default: .fluxloop/personas.yaml)

**Examples:**

```bash
# Show persona details
fluxloop personas show frustrated-customer
```

### `fluxloop personas edit`

Edit personas manually.

**Usage:**

```bash
fluxloop personas edit [options]
```

**Options:**

- `--file <path>`: Personas file to edit (default: .fluxloop/personas.yaml)
- `--editor <editor>`: Editor to use (default: $EDITOR)

**Examples:**

```bash
# Edit personas in default editor
fluxloop personas edit

# Edit with specific editor
fluxloop personas edit --editor vim
```

### `fluxloop personas validate`

Validate personas file format.

**Usage:**

```bash
fluxloop personas validate [options]
```

**Options:**

- `--file <path>`: Personas file to validate (default: .fluxloop/personas.yaml)

**Examples:**

```bash
# Validate personas file
fluxloop personas validate

# Validate specific file
fluxloop personas validate --file personas/custom.yaml
```

## Persona File Format

Personas are defined in YAML format:

```yaml
# .fluxloop/personas.yaml
personas:
  - name: frustrated-customer
    description: Customer who is upset and needs immediate help
    demographics:
      age_range: "35-50"
      tech_comfort: low
      urgency: high
      education_level: varied
      location: urban

    traits:
      - impatient
      - stressed
      - emotional
      - direct
      - demanding

    communication_style:
      tone: urgent
      formality: informal
      verbosity: concise
      punctuation: excessive_exclamation
      grammar: sometimes_incorrect

    behaviors:
      - expects_immediate_response
      - may_escalate_quickly
      - focuses_on_problem_not_pleasantries
      - wants_clear_solutions
      - may_mention_competitors

    example_messages:
      - "I need help NOW!"
      - "This is ridiculous!"
      - "I want to speak to a manager"
      - "This isn't working and I'm very upset"
      - "I'm going to cancel my account"

    preferred_response_style:
      - empathetic
      - solution-focused
      - clear_and_direct
      - acknowledges_frustration
      - provides_timeline

  - name: tech-savvy-user
    description: Technical user who understands systems
    demographics:
      age_range: "25-35"
      tech_comfort: high
      urgency: medium
      education_level: high
      location: varied

    traits:
      - analytical
      - patient
      - detail-oriented
      - self-sufficient
      - knowledgeable

    communication_style:
      tone: neutral
      formality: semi-formal
      verbosity: detailed
      punctuation: proper
      grammar: correct

    behaviors:
      - provides_detailed_context
      - includes_error_messages
      - tries_troubleshooting_first
      - asks_specific_questions
      - appreciates_technical_explanations

    example_messages:
      - "Getting error code 500 when submitting the form"
      - "Tried clearing cache, issue persists"
      - "Can you check server logs for request ID abc123?"
      - "The API returns 400 with this payload: {...}"

    preferred_response_style:
      - technical_but_clear
      - includes_root_cause
      - provides_documentation_links
      - offers_workarounds
```

## AI Generation Options

### Diversity Levels

Control persona variety:

- **low**: Similar personas with minor variations
- **medium**: Balanced mix of different persona types (default)
- **high**: Maximum diversity across demographics and traits

```bash
# Generate diverse personas
fluxloop personas generate \
  --description "Product feedback scenarios" \
  --diversity high
```

### Model Selection

Choose AI model for generation:

- `claude-3-opus`: Most creative and diverse (slower, more expensive)
- `claude-3-sonnet`: Balanced quality and speed (default)
- `claude-3-haiku`: Fast and economical (less diverse)

```bash
# Use Opus for maximum quality
fluxloop personas generate \
  --description "Complex healthcare scenarios" \
  --model claude-3-opus
```

## Best Practices

### 1. Be Specific in Descriptions

```bash
# Good: Specific context
fluxloop personas generate \
  --description "E-commerce customers dealing with shipping delays"

# Bad: Too vague
fluxloop personas generate \
  --description "users"
```

### 2. Generate Sufficient Diversity

```bash
# Generate enough personas to cover edge cases
fluxloop personas generate \
  --description "SaaS product support" \
  --count 5 \
  --diversity high
```

### 3. Review and Refine

Always review generated personas:

```bash
# Generate
fluxloop personas generate --description "..."

# Review
fluxloop personas list

# Edit if needed
fluxloop personas edit
```

### 4. Use Realistic Traits

Ensure personas reflect real user types:

```yaml
# Good: Realistic persona
- name: busy-executive
  traits:
    - time-constrained
    - results-oriented
    - delegates_details
    - prefers_summaries

# Bad: Unrealistic persona
- name: perfect-user
  traits:
    - always_patient
    - never_confused
    - reads_all_documentation
```

### 5. Document Use Cases

Add context about when to use each persona:

```yaml
- name: frustrated-customer
  description: Use for testing escalation and conflict resolution
  use_cases:
    - password_reset_failures
    - billing_disputes
    - service_outages
    - product_defects
```

## Related Commands

- [`fluxloop inputs generate`](./inputs): Generate test inputs from personas
- [`fluxloop scenarios create`](./scenarios): Create scenarios with personas
- [`fluxloop bundles create`](./bundles): Bundle personas with inputs

## See Also

- [Persona Design Guide](../guides/persona-design): Best practices for persona design
- [Synthetic Input Generation](../guides/synthetic-input-generation): Generating test data
