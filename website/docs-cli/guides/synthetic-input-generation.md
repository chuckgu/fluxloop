---
sidebar_position: 2
---

# Synthetic Input Generation

Generate realistic test inputs using personas and AI-powered synthesis.

## What is Synthetic Input Generation?

Synthetic input generation creates realistic test data programmatically, rather than manually writing each test case. Using **personas** as templates, FluxLoop generates diverse, realistic inputs that mimic how real users interact with your AI agent.

### Manual vs Synthetic Testing

**Manual Testing:**
```yaml
# tests/manual_inputs.yaml
inputs:
  - "How do I start?"
  - "What are the features?"
  - "How much does it cost?"
  # ... writing 100+ inputs by hand 😩
```

**Synthetic Testing:**
```yaml
# personas.yaml
personas:
  - novice_user
  - expert_user
  - frustrated_user

# Generate 100 diverse inputs automatically
$ fluxloop inputs generate --count 100
✅ Generated 100 inputs from 3 personas
```

## Benefits

### 1. Scale Testing

Generate hundreds or thousands of test inputs in minutes:

```bash
# Manual: Days to write 1000 inputs
# Synthetic: Minutes to generate 1000 inputs
fluxloop inputs generate --count 1000
```

### 2. Uncover Edge Cases

Personas generate unexpected variations you wouldn't think of manually:

```yaml
# Manual inputs (predictable)
- "How do I reset my password?"
- "How do I change my password?"

# Synthetic inputs (diverse)
- "password reset???"
- "i forgot my pwd help"
- "Can't login. Need to change credentials ASAP"
- "where is option for changing authentication"
- "🔐 reset?"
```

### 3. Maintain Test Coverage

As your product evolves, regenerate inputs automatically:

```bash
# Product adds new features
$ update_personas.sh

# Regenerate tests
$ fluxloop inputs generate --refresh
✅ Generated 150 inputs covering new features
```

### 4. Realistic Diversity

Personas ensure inputs reflect real user diversity:
- Language variations
- Expertise levels
- Emotional states
- Communication styles

## How It Works

### 1. Define Personas

Create personas representing your users:

```yaml
# personas/novice_user.yaml
persona_id: novice_user
attributes:
  expertise: beginner
  patience: high
  technical_background: none

communication:
  formality: casual
  verbosity: brief
  emoji_usage: occasional
```

See [Persona Design](./persona-design) for details.

### 2. Generate Inputs

Use personas to generate synthetic inputs:

```bash
fluxloop inputs generate --persona novice_user --count 50
```

FluxLoop uses an LLM to generate realistic inputs matching the persona:

```yaml
generated_inputs:
  - id: input_001
    persona: novice_user
    text: "um... how do i even start? 😅"
    metadata:
      complexity: simple
      tone: uncertain

  - id: input_002
    persona: novice_user
    text: "is there a tutorial or something?"
    metadata:
      complexity: simple
      tone: curious
```

### 3. Review and Refine

Review generated inputs:

```bash
# List generated inputs
fluxloop inputs list

# View specific input
fluxloop inputs show input_001
```

Refine if needed:

```bash
# Regenerate with different temperature
fluxloop inputs generate --temperature 0.8

# Add constraints
fluxloop inputs generate --topic "authentication"
```

### 4. Create Bundles

Bundle inputs for testing:

```bash
# Create test bundle
fluxloop bundles create --name "regression_v1"
```

### 5. Run Tests

Test your agent with generated inputs:

```bash
fluxloop test --bundle regression_v1
```

## Generation Strategies

### Basic Generation

Generate inputs from a single persona:

```bash
fluxloop inputs generate \
  --persona novice_user \
  --count 50
```

### Multi-Persona Generation

Generate inputs from multiple personas:

```bash
fluxloop inputs generate \
  --personas novice_user,expert_user,frustrated_user \
  --count 150
```

Each persona contributes proportionally (50 inputs each).

### Weighted Generation

Weight personas by frequency:

```bash
fluxloop inputs generate \
  --personas novice_user:60,expert_user:30,frustrated_user:10 \
  --count 100
```

Generates:
- 60 inputs from novice_user
- 30 inputs from expert_user
- 10 inputs from frustrated_user

### Topic-Constrained Generation

Generate inputs about specific topics:

```bash
fluxloop inputs generate \
  --persona expert_user \
  --topic "API authentication" \
  --count 30
```

Example outputs:
```
- "What's the OAuth2 flow?"
- "Rate limits for /auth/token?"
- "Refresh token rotation strategy?"
```

### Context-Aware Generation

Provide context for generation:

```bash
fluxloop inputs generate \
  --persona support_agent \
  --context "User is trying to integrate the API" \
  --count 40
```

Generates inputs relevant to API integration context.

## Configuration

### Input Config File

Define generation settings:

```yaml
# configs/input.yaml
generation:
  provider: openai  # or anthropic
  model: gpt-4o
  temperature: 0.7
  max_tokens: 100

personas:
  - id: novice_user
    count: 60
  - id: expert_user
    count: 30
  - id: frustrated_user
    count: 10

constraints:
  topics:
    - authentication
    - user_management
    - billing

  max_length: 200
  min_length: 10
  language: english
```

Use config:

```bash
fluxloop inputs generate --config configs/input.yaml
```

### Generation Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--provider` | LLM provider (openai, anthropic) | openai |
| `--model` | Model name | gpt-4o |
| `--temperature` | Sampling temperature (0.0-1.0) | 0.7 |
| `--count` | Number of inputs to generate | 50 |
| `--topic` | Topic constraint | None |
| `--context` | Additional context | None |

Higher temperature = more diverse, creative inputs
Lower temperature = more predictable, conservative inputs

## Quality Control

### Review Generated Inputs

Always review generated inputs before using in production:

```bash
# Generate and review
fluxloop inputs generate --count 50 --output inputs/review.yaml

# Review in editor
code inputs/review.yaml

# Approve
fluxloop inputs approve inputs/review.yaml
```

### Filter Low-Quality Inputs

Automatically filter:

```yaml
# config.yaml
generation:
  filters:
    min_length: 10
    max_length: 500
    remove_duplicates: true
    remove_offensive: true
    language: english
```

### Manual Curation

Combine synthetic and manual inputs:

```yaml
# inputs/curated.yaml
inputs:
  # Synthetic (auto-generated)
  - text: "How do I start?"
    source: synthetic
    persona: novice_user

  # Manual (hand-written edge case)
  - text: "What if I have 10,000,000 users?"
    source: manual
    importance: critical
```

### Validation

Validate generated inputs:

```bash
fluxloop inputs validate
```

Checks:
- ✅ No duplicates
- ✅ Appropriate length
- ✅ Matches persona
- ✅ No offensive content
- ✅ Language correctness

## Advanced Techniques

### Chain-of-Thought Generation

Generate inputs with reasoning:

```yaml
generation:
  chain_of_thought: true
```

Example:

```yaml
input:
  thought_process: |
    User is a novice trying to complete their first task.
    They're uncertain and need reassurance.
    They likely don't know technical terms.

  generated_text: "is it ok if i click here? will it break anything?"
```

Produces more realistic, nuanced inputs.

### Few-Shot Examples

Provide examples to guide generation:

```yaml
generation:
  few_shot_examples:
    - persona: expert_user
      examples:
        - "What's the rate limit for POST /api/v2/users?"
        - "Any bulk update endpoints?"
        - "Webhook retry policy?"
```

Ensures generated inputs match desired style.

### Conversation Simulation

Generate multi-turn conversations:

```bash
fluxloop inputs generate \
  --multi-turn \
  --max-turns 5 \
  --persona frustrated_user
```

Generates realistic conversation flows:

```yaml
conversation:
  - turn: 1
    input: "This isn't working"
  - turn: 2
    input: "I already tried that!"
  - turn: 3
    input: "Can I just talk to a human?"
```

### Domain-Specific Generation

Use domain vocabulary:

```yaml
generation:
  domain: healthcare
  vocabulary:
    - "patient records"
    - "HIPAA compliance"
    - "clinical notes"
    - "medication history"
```

Generates domain-appropriate inputs:
```
- "How do I access patient records securely?"
- "Is this HIPAA compliant?"
- "Where are clinical notes stored?"
```

## Best Practices

### 1. Start Small

❌ Don't generate 1000 inputs immediately
```bash
fluxloop inputs generate --count 1000  # Overwhelming
```

✅ Start with small batches
```bash
fluxloop inputs generate --count 50
# Review and refine
fluxloop inputs generate --count 50
# Iterate
```

### 2. Balance Personas

❌ Don't focus on one persona
```yaml
personas:
  novice_user: 100%  # Misses expert scenarios
```

✅ Reflect real user distribution
```yaml
personas:
  novice_user: 40%
  intermediate_user: 35%
  expert_user: 25%
```

### 3. Validate Outputs

❌ Don't use generated inputs blindly
```bash
fluxloop inputs generate --count 500
fluxloop test  # Without review!
```

✅ Always review first
```bash
fluxloop inputs generate --count 500
fluxloop inputs review
fluxloop inputs approve
fluxloop test
```

### 4. Combine with Manual Inputs

❌ Don't rely 100% on synthetic data
```yaml
# All synthetic, misses critical edge cases
```

✅ Mix synthetic and manual
```yaml
inputs:
  synthetic: 80%  # Bulk coverage
  manual: 20%     # Critical edge cases
```

### 5. Iterate Based on Results

❌ Don't generate once and forget
```bash
# Generated 6 months ago, never updated
fluxloop test --bundle old_bundle
```

✅ Regenerate regularly
```bash
# Update personas based on new learnings
fluxloop personas update

# Regenerate inputs
fluxloop inputs generate --refresh

# Test
fluxloop test
```

### 6. Version Control

Store inputs in version control:

```bash
git add inputs/
git commit -m "Update synthetic inputs for v2 API"
```

Benefits:
- Track changes
- Collaborate with team
- Rollback if needed

## Common Pitfalls

### Over-Generation

❌ Generating too many similar inputs:
```yaml
# 100 nearly identical inputs
- "How do I start?"
- "How do I begin?"
- "How to start?"
- ...
```

✅ Use diversity constraints:
```yaml
generation:
  diversity:
    min_similarity: 0.3  # Prevent too-similar inputs
```

### Unrealistic Inputs

❌ Generated inputs that no real user would ask:
```
- "Please enumerate the comprehensive list of all functionalities..."
```

✅ Ground in real user language:
```
- "what can this do?"
```

### Ignoring Context

❌ Generating inputs without product context:
```
- "How do I purchase a widget?"
# (Your product doesn't have widgets)
```

✅ Provide product context:
```yaml
generation:
  context: |
    Product: AI agent testing platform
    Features: Synthetic testing, scenarios, bundles
    No: widgets, physical products, e-commerce
```

## Cost Optimization

### LLM API Costs

Generation uses LLM API calls. Optimize costs:

#### Use Smaller Models

```yaml
generation:
  model: gpt-4o-mini  # Cheaper than gpt-4o
  # or
  model: claude-3-haiku  # Cheaper than sonnet
```

#### Batch Generation

```bash
# Efficient: One API call, 100 inputs
fluxloop inputs generate --count 100

# Inefficient: 100 API calls
for i in {1..100}; do
  fluxloop inputs generate --count 1
done
```

#### Cache Common Patterns

```yaml
generation:
  caching: true  # Reuse similar generations
```

### Monitor Costs

```bash
fluxloop inputs generate --count 100 --dry-run
# Estimated cost: $0.15
# Proceed? (y/n)
```

## Troubleshooting

### Low-Quality Outputs

**Problem**: Generated inputs are nonsensical

**Solution**: Adjust temperature

```bash
# Too high temperature (1.0) = nonsense
fluxloop inputs generate --temperature 0.6  # More focused
```

### Repetitive Outputs

**Problem**: All inputs are too similar

**Solution**: Increase temperature or add diversity constraint

```bash
fluxloop inputs generate --temperature 0.8 --diversity-threshold 0.4
```

### Off-Topic Outputs

**Problem**: Inputs don't match your product

**Solution**: Add context and constraints

```yaml
generation:
  context: "AI agent testing platform"
  constraints:
    topics:
      - testing
      - agents
      - synthetic_data
    forbidden_topics:
      - cooking
      - sports
```

### API Errors

**Problem**: Generation fails with API errors

**Solution**: Check API key and rate limits

```bash
export OPENAI_API_KEY=your_key
fluxloop inputs generate --provider openai
```

## Related Commands

- [`personas`](../commands/personas) - Manage personas
- [`inputs`](../commands/inputs) - Manage generated inputs
- [`bundles`](../commands/bundles) - Bundle inputs for testing
- [`test`](../commands/test) - Test with generated inputs

## Next Steps

- [Persona Design](./persona-design) - Create effective personas
- [Testing Best Practices](./testing-best-practices) - Use synthetic inputs effectively
- [Input Config](../configuration/input-config) - Configure generation

## Examples

See [FluxLoop Examples](https://github.com/chuckgu/fluxloop/tree/main/examples/synthetic-generation) for:
- Complete generation workflows
- Domain-specific examples (SaaS, E-commerce, Healthcare)
- Advanced techniques
- Cost optimization strategies
