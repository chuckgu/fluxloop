---
sidebar_position: 1
---

# Persona Design

Design effective personas to generate realistic synthetic test inputs.

## What Are Personas?

Personas are archetypal user profiles that represent different types of users interacting with your AI agent. They define:

- **User characteristics**: Background, expertise level, goals
- **Interaction patterns**: How they communicate, what they ask
- **Context**: Situations, constraints, motivations
- **Behavior**: Tone, language complexity, follow-up patterns

Personas enable FluxLoop to generate synthetic inputs that mimic real user diversity.

## Why Personas Matter

### 1. Realistic Testing

Without personas:
```
❌ "Test the chatbot"
   → Generic, unrealistic inputs
   → Misses edge cases
   → Limited coverage
```

With personas:
```
✅ Novice User: "um... how do i even start? 😅"
✅ Expert User: "What's the API rate limit for batch operations?"
✅ Frustrated User: "This STILL doesn't work after 3 tries!"
```

### 2. Edge Case Discovery

Different personas uncover different failures:

| Persona | Discovers |
|---------|-----------|
| Novice | Unclear instructions, jargon issues |
| Expert | Missing advanced features, incorrect details |
| Non-native English | Language understanding problems |
| Impatient | Verbosity issues, slow responses |

### 3. Behavior Consistency

Personas ensure generated inputs maintain consistent characteristics:

```yaml
persona: impatient_executive
inputs:
  - "Quick answer needed: revenue projections?"  ✅ Consistent
  - "I'd love to learn more about your methodology..." ❌ Inconsistent
```

## Core Persona Attributes

### 1. Demographics

**Age, Location, Role**

```yaml
persona_id: enterprise_admin
demographics:
  age_range: "35-50"
  role: "IT Administrator"
  company_size: "500+ employees"
  industry: "Enterprise SaaS"
```

Use demographics to inform:
- Language complexity
- Feature awareness
- Use case priorities

### 2. Expertise Level

**Novice → Intermediate → Expert**

```yaml
expertise:
  level: novice
  familiarity_with_product: "first_time_user"
  technical_background: "non-technical"
  domain_knowledge: "basic"
```

Affects:
- Question complexity
- Terminology usage
- Assumption of prior knowledge

### 3. Goals

**What the user wants to achieve**

```yaml
goals:
  primary: "Set up automated backups"
  secondary: "Understand pricing implications"
  constraints:
    - "Limited budget"
    - "Tight deadline"
```

Drives:
- Input content
- Follow-up questions
- Success criteria

### 4. Emotional State

**Current mood and frustration level**

```yaml
emotional_state:
  mood: "frustrated"
  reason: "Failed 3 times already"
  patience: "low"
  communication_style: "blunt"
```

Affects:
- Tone
- Politeness level
- Willingness to provide detail

### 5. Communication Style

**How they express themselves**

```yaml
communication:
  language: "english"
  proficiency: "native"
  formality: "casual"
  verbosity: "concise"
  emoji_usage: "frequent"
  abbreviations: true
```

Shapes:
- Sentence structure
- Word choice
- Message length

## Persona Templates

### Novice User

```yaml
persona_id: novice_user
name: "First-Time User"
description: "Brand new to the product, needs hand-holding"

attributes:
  expertise: novice
  patience: medium
  technical_background: non-technical
  goals:
    - "Get started quickly"
    - "Avoid making mistakes"

communication:
  formality: casual
  verbosity: brief
  uncertainty: high
  emoji_usage: occasional

example_inputs:
  - "How do I start?"
  - "Is this the right button to click?"
  - "What happens if I do this wrong?"
  - "um... where do i find the settings? 😅"
```

### Expert User

```yaml
persona_id: expert_user
name: "Power User"
description: "Experienced, wants advanced features"

attributes:
  expertise: expert
  patience: low
  technical_background: strong
  goals:
    - "Use advanced features"
    - "Optimize performance"
    - "Integrate with other tools"

communication:
  formality: technical
  verbosity: concise
  jargon: true
  precision: high

example_inputs:
  - "What's the API rate limit for batch operations?"
  - "Can I override the default retry policy?"
  - "Is there a webhook endpoint for real-time events?"
  - "SSO integration via SAML?"
```

### Frustrated User

```yaml
persona_id: frustrated_user
name: "Frustrated User"
description: "Having problems, losing patience"

attributes:
  expertise: intermediate
  patience: very_low
  emotional_state: frustrated
  previous_attempts: 3
  goals:
    - "Solve problem NOW"
    - "Escalate if needed"

communication:
  formality: blunt
  verbosity: terse
  caps_usage: frequent
  emotional_expression: high

example_inputs:
  - "This STILL doesn't work!"
  - "I've tried everything. Nothing works."
  - "Can I just talk to a human?"
  - "Why is this so complicated?!"
```

### Non-Native English Speaker

```yaml
persona_id: non_native_english
name: "Non-Native English Speaker"
description: "Fluent but not native, occasional grammar issues"

attributes:
  expertise: intermediate
  language_proficiency: "B2"
  native_language: "spanish"
  goals:
    - "Complete task despite language barrier"

communication:
  formality: polite
  grammar: occasional_errors
  word_choice: simpler
  idioms: avoids

example_inputs:
  - "How I can do to export the data?"
  - "The button is not working for me"
  - "I need help with configure the settings"
  - "Is possible to change this option?"
```

### Mobile User

```yaml
persona_id: mobile_user
name: "On-the-Go User"
description: "Using mobile device, wants quick answers"

attributes:
  expertise: intermediate
  device: mobile
  context: "on the go"
  patience: low
  goals:
    - "Quick answers"
    - "Simple tasks only"

communication:
  formality: very_casual
  verbosity: extremely_brief
  typos: occasional
  abbreviations: frequent
  emoji_usage: high

example_inputs:
  - "quick q: pricing?"
  - "how 2 reset pwd"
  - "thx! one more thing..."
  - "👍 got it"
```

## Creating Custom Personas

### 1. Identify Real User Segments

Analyze your actual users:

```bash
# Review support tickets
$ analyze_tickets.py --segment-by frustration_level

# Check user interviews
$ user_research/segments.md
```

Identify patterns:
- Common user types
- Typical problems
- Communication styles

### 2. Define Persona Characteristics

```yaml
persona_id: api_developer
name: "API Integration Developer"
description: "Developer integrating our API into their app"

# Start with demographics
demographics:
  role: "Backend Developer"
  experience: "3-5 years"
  company_size: "Startup (10-50)"

# Define expertise
expertise:
  product_knowledge: intermediate
  technical_skills: expert
  api_experience: expert

# Specify goals
goals:
  primary: "Integrate authentication API"
  constraints:
    - "Launch deadline in 2 weeks"
    - "Limited documentation time"

# Communication style
communication:
  formality: professional
  verbosity: concise
  technical_jargon: high
  prefers_code_examples: true
```

### 3. Write Example Inputs

Test your persona definition:

```yaml
example_inputs:
  # Initial questions
  - "What's the OAuth2 flow? PKCE supported?"
  - "Rate limits for /auth/token endpoint?"

  # Follow-ups
  - "Getting 401 on callback. CORS issue?"
  - "Can I cache tokens client-side or security risk?"

  # Edge cases
  - "Refresh token rotation? Or fixed lifetime?"
  - "MFA support roadmap?"
```

Verify examples:
- ✅ Match persona characteristics
- ✅ Realistic for this user type
- ✅ Cover different scenarios

### 4. Test and Refine

```bash
# Generate inputs with persona
fluxloop personas create api_developer

# Generate test inputs
fluxloop inputs generate --persona api_developer --count 20

# Review generated inputs
fluxloop inputs list --persona api_developer
```

Check if generated inputs feel authentic:
- Are they realistic?
- Do they match the persona?
- Would a real user ask this?

Refine persona definition based on results.

## Persona Composition

### Combine Attributes

Create nuanced personas by combining multiple attributes:

```yaml
persona_id: junior_dev_frustrated
name: "Frustrated Junior Developer"
description: "Junior dev stuck on API integration, getting frustrated"

# Combines:
# - Junior expertise
# - Technical background
# - Frustrated emotional state

attributes:
  expertise: junior
  technical_background: intermediate
  emotional_state: frustrated
  time_pressure: high

communication:
  formality: casual
  technical_terms: basic
  frustration_expression: high
  caps_usage: occasional

example_inputs:
  - "The docs say to use Bearer token but WHERE do I get it?"
  - "I've been stuck on this for 2 hours 😭"
  - "Why isn't there a simple example that just WORKS?"
```

### Persona Evolution

Model persona changes over time:

```yaml
# Day 1: New user
persona: novice_user_day1
expertise: novice
patience: high
questions: "How do I start?"

# Week 2: Learning
persona: novice_user_week2
expertise: basic
patience: medium
questions: "Can I customize X?"

# Month 3: Proficient
persona: intermediate_user
expertise: intermediate
patience: medium
questions: "What's the best practice for Y?"
```

## Best Practices

### 1. Base on Real Users

❌ Don't invent random personas
```yaml
persona: alien_user
description: "User from Mars"  # Not realistic
```

✅ Use real user research
```yaml
persona: enterprise_security_admin
description: "Security-focused admin at F500 company"
# Based on 15 customer interviews
```

### 2. Focus on Behavior, Not Demographics Alone

❌ Demographics only
```yaml
persona: millennial_user
age: "25-35"  # Age doesn't predict behavior
```

✅ Behavior-driven
```yaml
persona: mobile_first_user
device_preference: mobile
interaction_pattern: quick_tasks
communication: brief_and_casual
```

### 3. Create Diverse Personas

Cover different dimensions:
- ✅ Expertise: Novice, Intermediate, Expert
- ✅ Patience: Low, Medium, High
- ✅ Context: Work, Personal, Mobile
- ✅ Language: Native, Non-native
- ✅ Emotional: Happy, Neutral, Frustrated

### 4. Keep Personas Focused

❌ Too many attributes
```yaml
persona: complex_user
# 50+ attributes
# Impossible to maintain
```

✅ Essential attributes only
```yaml
persona: power_user
# 5-8 key attributes
# Easy to understand and use
```

### 5. Test with Real Users

Validate generated inputs:

```bash
# Generate inputs
fluxloop inputs generate --persona enterprise_admin

# Show to real enterprise admins
# "Would you ask this question?"
```

## Common Pitfalls

### Overly Generic Personas

❌ Too broad:
```yaml
persona: generic_user
description: "A user"
```

✅ Specific:
```yaml
persona: saas_trial_user_day3
description: "SaaS trial user on day 3, evaluating for team"
```

### Stereotypical Personas

❌ Based on stereotypes:
```yaml
persona: boomer
description: "Old person who doesn't understand technology"
```

✅ Based on real behavior:
```yaml
persona: late_tech_adopter
description: "Cautious user preferring proven solutions"
```

### Static Personas

❌ Never updated:
```yaml
# Created 2 years ago, never revised
persona: mobile_user_2022
```

✅ Regularly refined:
```yaml
# Updated based on recent user research
persona: mobile_user
last_updated: "2024-11-01"
based_on: "Q3 2024 user interviews"
```

## Advanced Techniques

### Persona Weighting

Weight personas by frequency in production:

```yaml
personas:
  - id: novice_user
    weight: 0.40  # 40% of users
  - id: intermediate_user
    weight: 0.35  # 35% of users
  - id: expert_user
    weight: 0.25  # 25% of users
```

Generate inputs proportionally:

```bash
fluxloop inputs generate --count 100 --weighted
# 40 novice, 35 intermediate, 25 expert inputs
```

### Conditional Attributes

Attributes that depend on context:

```yaml
persona: support_agent
attributes:
  during_high_volume:
    patience: very_low
    verbosity: terse
    response_speed: fast
  during_normal_hours:
    patience: high
    verbosity: detailed
    response_speed: normal
```

### Multi-Turn Personas

Define how personas behave across conversation turns:

```yaml
persona: impatient_customer
turn_1:
  patience: medium
  question: "How does this work?"
turn_2:
  patience: low
  question: "Ok but specifically for my use case?"
turn_3:
  patience: very_low
  question: "Can I just get a simple yes or no?"
```

## Tools and Resources

### FluxLoop Commands

```bash
# Create persona
fluxloop personas create enterprise_admin

# Generate inputs from persona
fluxloop inputs generate --persona enterprise_admin

# Test persona
fluxloop test --persona enterprise_admin
```

### External Resources

- User research interviews
- Support ticket analysis
- User analytics data
- Community forum posts

## Next Steps

- [Synthetic Input Generation](./synthetic-input-generation) - Generate inputs from personas
- [Testing Best Practices](./testing-best-practices) - Use personas effectively
- [Personas Command](../commands/personas) - Manage personas

## Examples Repository

See [FluxLoop Examples](https://github.com/chuckgu/fluxloop/tree/main/examples/personas) for:
- 20+ ready-to-use personas
- Industry-specific personas (SaaS, E-commerce, Healthcare)
- Multi-language personas
- Persona templates
