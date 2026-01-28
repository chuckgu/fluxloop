---
sidebar_position: 2
---

# Input Configuration

Configure personas, base inputs, and input generation settings in `configs/input.yaml`.

## Overview

The input configuration file defines:

- **Personas**: Different user types with characteristics and goals
- **Base Inputs**: Core test inputs to generate variations from
- **Generation Settings**: How to create input variations (LLM or deterministic)
- **Variation Strategies**: Transformations to apply (rephrase, verbose, etc.)

This configuration drives the `fluxloop generate inputs` command.

## File Location

```
fluxloop/my-agent/
└── configs/
    └── input.yaml    # ← This file
```

## Complete Example

```yaml
# FluxLoop Input Configuration
# ------------------------------------------------------------
# Defines personas, base inputs, and generation modes.
# Adjust personas/goals/strategies based on your target scenarios.
personas:
  - name: novice_user
    description: A user new to the system
    characteristics:
      - Asks basic questions
      - May use incorrect terminology
      - Needs detailed explanations
    language: en
    expertise_level: novice
    goals:
      - Understand system capabilities
      - Complete basic tasks
    # Tip: Add persona-specific context that can be injected into prompts.

  - name: expert_user
    description: An experienced power user
    characteristics:
      - Uses technical terminology
      - Asks complex questions
      - Expects efficient responses
    language: en
    expertise_level: expert
    goals:
      - Optimize workflows
      - Access advanced features
    # Tip: Include any tone/style expectations in characteristics.

base_inputs:
  - input: "How do I get started?"
    expected_intent: help
    # Provide optional 'metadata' or 'expected' fields to guide evaluation.

# ------------------------------------------------------------
# Input generation settings
# - variation_strategies: transformations applied when synthesizing inputs.
# - variation_count / temperature: tune diversity of generated samples.
# - inputs_file: location where generated inputs will be saved/loaded.
variation_strategies:
  - rephrase
  - verbose
  - error_prone

variation_count: 2
variation_temperature: 0.7

inputs_file: inputs/generated.yaml

input_generation:
  mode: llm
  llm:
    enabled: true
    provider: openai
    model: gpt-4o-mini
    api_key: null
    # Replace provider/model/api_key according to your LLM setup.
```

---

## Personas

### Overview

Personas represent different user types that will interact with your agent. Each persona has:
- Identity (name, description)
- Characteristics (behavior patterns)
- Expertise level
- Goals and objectives
- Language preferences

### Persona Structure

```yaml
personas:
  - name: string              # Required: unique identifier
    description: string       # Required: human-readable description
    characteristics: list     # Optional: behavioral traits
    language: string          # Optional: ISO language code (default: "en")
    expertise_level: string   # Optional: novice/intermediate/expert
    goals: list              # Optional: user objectives
```

### Example Personas

#### Novice User

```yaml
- name: novice_user
  description: A user new to the system
  characteristics:
    - Asks basic questions
    - May use incorrect terminology
    - Needs detailed explanations
    - Prefers step-by-step guidance
  language: en
  expertise_level: novice
  goals:
    - Understand system capabilities
    - Complete basic tasks
    - Learn fundamental concepts
```

#### Expert User

```yaml
- name: expert_user
  description: An experienced power user
  characteristics:
    - Uses technical terminology
    - Asks complex questions
    - Expects efficient responses
    - Wants advanced features
  language: en
  expertise_level: expert
  goals:
    - Optimize workflows
    - Access advanced features
    - Automate repetitive tasks
```

#### Non-Native Speaker

```yaml
- name: non_native_speaker
  description: User with limited English proficiency
  characteristics:
    - Uses simple vocabulary
    - May have grammatical errors
    - Shorter sentences
    - Literal interpretations
  language: en
  expertise_level: intermediate
  goals:
    - Get clear, simple answers
    - Avoid complex terminology
```

#### Frustrated User

```yaml
- name: frustrated_user
  description: User experiencing issues or delays
  characteristics:
    - Expresses frustration or urgency
    - May be impatient
    - Wants quick solutions
    - Previous attempts failed
  language: en
  expertise_level: intermediate
  goals:
    - Resolve issue quickly
    - Get reassurance
    - Understand what went wrong
```

### Persona Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Unique persona identifier (snake_case) |
| `description` | `string` | Yes | Human-readable persona description |
| `characteristics` | `list[string]` | No | Behavioral traits and patterns |
| `language` | `string` | No | ISO language code (e.g., `en`, `es`, `fr`) |
| `expertise_level` | `string` | No | `novice`, `intermediate`, `expert` |
| `goals` | `list[string]` | No | User objectives and motivations |

### How Personas Are Used

1. **Input Generation**: LLM uses persona characteristics to generate realistic variations
2. **Multi-Turn**: Supervisor uses persona to craft follow-up questions
3. **Evaluation**: Results can be grouped by persona for analysis
4. **Reporting**: Dashboard shows performance per persona type

---

## Base Inputs

### Overview

Base inputs are the core test cases from which variations are generated. Each base input represents a distinct user intent or scenario.

### Base Input Structure

```yaml
base_inputs:
  - input: string             # Required: the actual input text
    expected_intent: string   # Optional: expected intent/category
    metadata: object          # Optional: custom fields
    persona: string           # Optional: default persona for this input
```

### Example Base Inputs

#### Simple Base Inputs

```yaml
base_inputs:
  - input: "How do I get started?"
    expected_intent: help
    
  - input: "What are the pricing plans?"
    expected_intent: pricing_inquiry
    
  - input: "I can't log in to my account"
    expected_intent: troubleshooting
```

#### With Metadata

```yaml
base_inputs:
  - input: "How do I reset my password?"
    expected_intent: account_management
    metadata:
      category: authentication
      priority: high
      typical_persona: novice_user
      
  - input: "Show me advanced filtering options"
    expected_intent: feature_inquiry
    metadata:
      category: features
      complexity: high
      typical_persona: expert_user
```

#### With Expected Outputs

```yaml
base_inputs:
  - input: "What's the status of order #12345?"
    expected_intent: order_inquiry
    metadata:
      expected_tool_calls: ["get_order_status"]
      expected_response_type: "structured_data"
      test_data:
        order_id: "12345"
```

### Base Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input` | `string` | Yes | The actual input text |
| `expected_intent` | `string` | No | Expected intent/category (for evaluation) |
| `metadata` | `object` | No | Any custom metadata |
| `persona` | `string` | No | Default persona for this input |

### Design Guidelines

**Good Base Inputs:**
- Cover diverse user intents
- Represent real-world scenarios
- Include edge cases (errors, ambiguity)
- Vary in complexity
- Test different features

**Examples:**

```yaml
base_inputs:
  # Happy path
  - input: "How do I create a new project?"
    expected_intent: getting_started
  
  # Edge case - ambiguous
  - input: "Can you help me?"
    expected_intent: help_general
  
  # Edge case - error scenario
  - input: "Why isn't this working?!?"
    expected_intent: troubleshooting
  
  # Complex multi-step
  - input: "I need to export my data, format it as CSV, and email it"
    expected_intent: complex_task
  
  # Non-English (if supported)
  - input: "¿Cómo puedo empezar?"
    expected_intent: help
    metadata:
      language: es
```

---

## Variation Strategies

### Available Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `rephrase` | Reword input keeping same meaning | Test semantic understanding |
| `verbose` | Add more details and context | Test handling of lengthy input |
| `concise` | Shorten to minimal form | Test with terse users |
| `error_prone` | Add typos, grammar errors | Test robustness |
| `formal` | Use formal language | Test tone adaptation |
| `casual` | Use casual/slang language | Test informal input |
| `technical` | Add technical terminology | Test expert users |
| `simple` | Simplify vocabulary | Test novice users |

### Configuration

```yaml
variation_strategies:
  - rephrase     # Always useful
  - verbose      # Test long-winded users
  - error_prone  # Test robustness
```

### Examples of Variations

**Base Input:**
```
"How do I get started?"
```

**Variations:**

```yaml
# rephrase
- "What are the first steps to begin?"
- "Where should I start?"
- "How can I initiate the process?"

# verbose
- "Hello, I'm completely new to this system and I was wondering if you could help me understand how I should get started with using it?"

# error_prone
- "how do i get strated?"
- "How do i gte started?"

# casual
- "yo how do i get going with this?"

# formal
- "I would like to inquire about the initial steps required to commence."

# technical (if applicable)
- "What's the initialization procedure for the system?"
```

---

## Input Generation Settings

### variation_count

**Type:** `integer`  
**Default:** `2`  
**Range:** `1-10`

Number of variations to generate per base input × persona combination.

```yaml
variation_count: 2  # Generate 2 variations each
```

**Formula:**
```
Total Inputs = base_inputs × personas × variation_count
```

**Example:**
- 5 base inputs
- 2 personas  
- 3 variations
- **Total: 30 generated inputs**

### variation_temperature

**Type:** `float`  
**Default:** `0.7`  
**Range:** `0.0-2.0`

Controls diversity of LLM-generated variations.

```yaml
variation_temperature: 0.7  # Balanced diversity
```

| Temperature | Effect | Use Case |
|-------------|--------|----------|
| `0.0-0.3` | Very conservative, minimal changes | Subtle rephrasing |
| `0.4-0.7` | Balanced diversity | General use (recommended) |
| `0.8-1.2` | More creative variations | Stress testing |
| `1.3-2.0` | Highly diverse, unpredictable | Edge case discovery |

### inputs_file

**Type:** `string`  
**Default:** `inputs/generated.yaml`

Path where generated inputs will be saved (relative to project root).

```yaml
inputs_file: inputs/generated.yaml
```

**File Structure:**

```yaml
# inputs/generated.yaml
- input: "How can I begin?"
  persona: novice_user
  metadata:
    base_input: "How do I get started?"
    variation_strategy: rephrase
    variation_index: 0
    generated_at: "2025-01-17T14:30:22Z"

- input: "Hello, I'm new and wondering how to get started..."
  persona: novice_user
  metadata:
    base_input: "How do I get started?"
    variation_strategy: verbose
    variation_index: 1
```

---

## LLM Configuration

### input_generation.mode

**Type:** `string`  
**Options:** `llm` | `deterministic`  
**Default:** `llm`

Generation mode to use.

```yaml
input_generation:
  mode: llm  # or deterministic
```

**LLM Mode:**
- Uses language model to generate variations
- More natural and diverse
- Requires API key
- Non-deterministic (different each run)

**Deterministic Mode:**
- Uses rule-based transformations
- Reproducible results
- No API key needed
- Faster and cheaper

### LLM Settings

```yaml
input_generation:
  mode: llm
  llm:
    enabled: true
    provider: openai
    model: gpt-4o-mini
    api_key: null  # Set via OPENAI_API_KEY env var
```

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | `boolean` | Enable LLM generation |
| `provider` | `string` | `openai`, `anthropic`, `gemini` |
| `model` | `string` | Model name (e.g., `gpt-4o-mini`) |
| `api_key` | `string \| null` | API key (use env var instead) |

### Supported Providers

#### OpenAI

```yaml
llm:
  provider: openai
  model: gpt-4o-mini  # or gpt-4o, gpt-4-turbo
  api_key: null  # Set OPENAI_API_KEY
```

#### Anthropic

```yaml
llm:
  provider: anthropic
  model: claude-3-haiku-20240307  # or claude-3-5-sonnet-20241022
  api_key: null  # Set ANTHROPIC_API_KEY
```

#### Google Gemini

```yaml
llm:
  provider: gemini
  model: gemini-2.0-flash-exp  # or gemini-2.5-flash
  api_key: null  # Set GEMINI_API_KEY
```

### Setting API Keys

**Via CLI:**
```bash
fluxloop config set-llm openai sk-your-key --model gpt-4o-mini
```

**Via .env file:**
```bash
# .env
OPENAI_API_KEY=sk-your-key
```

---

## Complete Examples

### Minimal Configuration

```yaml
personas:
  - name: user
    description: Regular user

base_inputs:
  - input: "Hello"
  - input: "Help me"

input_generation:
  mode: deterministic
```

### Standard Configuration

```yaml
personas:
  - name: novice_user
    description: New to the system
    expertise_level: novice
  
  - name: expert_user
    description: Experienced user
    expertise_level: expert

base_inputs:
  - input: "How do I get started?"
    expected_intent: help
  
  - input: "What are the advanced features?"
    expected_intent: features

variation_strategies:
  - rephrase
  - verbose

variation_count: 3
variation_temperature: 0.7

inputs_file: inputs/generated.yaml

input_generation:
  mode: llm
  llm:
    provider: openai
    model: gpt-4o-mini
```

### Advanced Configuration

```yaml
personas:
  - name: novice_user
    description: First-time user
    characteristics:
      - Asks basic questions
      - Needs guidance
      - May make mistakes
    language: en
    expertise_level: novice
    goals:
      - Learn the basics
      - Complete first task
  
  - name: expert_user
    description: Power user
    characteristics:
      - Uses shortcuts
      - Expects efficiency
      - Knows advanced features
    language: en
    expertise_level: expert
    goals:
      - Automate workflows
      - Optimize performance
  
  - name: non_english_user
    description: ESL user
    characteristics:
      - Simple vocabulary
      - Grammatical errors
      - Direct questions
    language: en
    expertise_level: intermediate
    goals:
      - Clear communication
      - Avoid confusion

base_inputs:
  - input: "How do I create a new project?"
    expected_intent: project_creation
    metadata:
      category: getting_started
      complexity: easy
  
  - input: "I need to bulk import 1000 items from CSV"
    expected_intent: data_import
    metadata:
      category: advanced
      complexity: high
  
  - input: "Error 500 when I click submit"
    expected_intent: error_report
    metadata:
      category: troubleshooting
      priority: high

variation_strategies:
  - rephrase
  - verbose
  - error_prone
  - casual
  - formal

variation_count: 5
variation_temperature: 0.8

inputs_file: inputs/generated.yaml

input_generation:
  mode: llm
  llm:
    enabled: true
    provider: openai
    model: gpt-4o
    api_key: null
```

---

## Usage

### Generate Inputs

```bash
# Generate with default settings
fluxloop generate inputs

# Generate specific number
fluxloop generate inputs --limit 50

# Use LLM mode
fluxloop generate inputs --mode llm

# Use deterministic mode
fluxloop generate inputs --mode deterministic

# Overwrite existing
fluxloop generate inputs --overwrite
```

### View Generated Inputs

```bash
# View in terminal
cat inputs/generated.yaml

# Count total
wc -l inputs/generated.yaml

# View with syntax highlighting
bat inputs/generated.yaml
```

---

## Tips and Best Practices

### Persona Design

1. **Start with 2-3 personas** - Don't overcomplicate initially
2. **Make them distinct** - Clear differences in behavior
3. **Based on real users** - Draw from actual user research
4. **Document reasoning** - Add comments explaining choices

### Base Input Selection

1. **Cover main user journeys** - Critical paths first
2. **Include edge cases** - Errors, ambiguity, unusual requests
3. **Test boundaries** - Very short, very long inputs
4. **Real-world examples** - Use actual user queries if available

### Generation Strategy

For **Development:**
```yaml
mode: deterministic      # Fast, reproducible
variation_count: 2       # Minimal
variation_strategies:
  - rephrase
```

For **Testing:**
```yaml
mode: llm               # Diverse, realistic
variation_count: 3      # Moderate
variation_temperature: 0.7
variation_strategies:
  - rephrase
  - verbose
  - error_prone
```

For **Production Validation:**
```yaml
mode: llm               # Maximum coverage
variation_count: 5      # Extensive
variation_temperature: 0.9
variation_strategies:
  - rephrase
  - verbose
  - error_prone
  - casual
  - formal
```

---

## See Also

- [Simulation Configuration](/cli/configuration/simulation-config) - Runner and experiment settings
- [generate Command](/cli/commands/generate) - Input generation CLI
- [Basic Workflow](/cli/workflows/basic-workflow) - Complete workflow guide
