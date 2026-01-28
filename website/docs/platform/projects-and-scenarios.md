# Projects and Scenarios

Learn how to manage projects and scenarios on the FluxLoop Web Platform.

## Understanding the Hierarchy

FluxLoop's data structure is organized in the following hierarchy:

```
Organization
└── Projects
    └── Scenarios
        └── Test Runs
            └── Results
```

### Organization

Organization is the top-level entity:

- Company, team, or individual account
- Contains multiple projects
- Member and permission management

### Project

A project represents a specific AI agent or application:

- Examples: "Customer Support Bot", "Email Assistant", "Code Generator"
- Contains multiple scenarios
- Project-specific settings and configuration

### Scenario

A scenario represents a specific test case or use case:

- Examples: "New User Onboarding", "Password Reset", "Product Recommendation"
- Includes personas, inputs, and evaluation criteria
- Can be executed multiple times (each execution is a separate Test Run)

### Test Run

A test run represents a single execution of a specific scenario:

- Timestamp and version information
- Execution environment and parameters
- Results and metrics

## Creating Projects

### Via Web Platform

1. Log in to [app.fluxloop.ai](https://app.fluxloop.ai)
2. Navigate to the "Projects" tab
3. Click "Create New Project"
4. Enter project information:
   - **Name**: Project name (e.g., "customer-support-bot")
   - **Description**: Project description
   - **Tags**: Tags for search and filtering

### Via CLI

Create a project locally and sync to the web:

```bash
# Initialize local project
fluxloop init

# Connect to web platform project
fluxloop projects
```

When the project list appears:

1. Select an existing project, or
2. Select "Create New Project" to create a new project

### Via Claude Code

Set up a project directly from Claude Code:

```
/fluxloop setup
```

Follow the prompts to:
1. Enter API key
2. Select or create a project
3. Link to local directory

## Managing Scenarios

### Creating Scenarios

#### 1. Via Web Platform

The most intuitive method:

1. Select a project
2. Navigate to the "Scenarios" tab
3. Click "Create New Scenario"
4. Enter scenario information:

**Basic Info**
- Name: Scenario name
- Description: Scenario description
- Tags: Classification tags

**Personas**
- Define test personas
- User characteristics and behavior patterns
- Example: "New user, tech-savvy, prefers mobile"

**Inputs**
- Test input data
- Initial messages or context
- Example: "I forgot my password"

**Evaluation Criteria** (optional)
- Success/failure conditions
- Expected response patterns
- Performance thresholds

#### 2. Via Local Files

Define scenarios locally with YAML files:

```yaml
# scenarios/password-reset.yaml
name: password-reset
description: Test password reset flow
personas:
  - name: frustrated-user
    description: User who forgot password and is in a hurry
    traits:
      - impatient
      - non-technical
inputs:
  - text: "I can't login, forgot my password"
  - text: "I need to reset it now"
criteria:
  - type: contains
    field: response
    value: "reset link"
  - type: response_time
    threshold_ms: 3000
```

Then upload to the web:

```bash
fluxloop sync upload --scenario password-reset
```

#### 3. Via CLI Generate

Use CLI to automatically generate scenarios:

```bash
# Generate personas using AI
fluxloop personas generate \
  --description "E-commerce customer support scenarios" \
  --count 5

# Generate inputs based on personas
fluxloop inputs generate \
  --persona frustrated-user \
  --count 10

# Bundle them together
fluxloop bundles create \
  --name password-reset-suite \
  --scenarios scenarios/*.yaml
```

### Pulling Scenarios

Import scenarios created on the web to local:

```bash
# Pull all scenarios
fluxloop sync pull

# Pull specific scenario only
fluxloop sync pull --scenario password-reset
```

Pulled scenarios are saved in the `.fluxloop/scenarios/` directory.

### Editing Scenarios

#### Via Web

1. Select a scenario
2. Click the "Edit" button
3. Make changes and click "Save"
4. Changes are applied immediately and a version is created

#### Via Local Files

1. Edit local files (`scenarios/*.yaml`)
2. Push changes to the web:

```bash
fluxloop sync upload --scenario password-reset
```

3. If there are conflicts, choose a resolution method:
   - `--force`: Overwrite with local version
   - `--merge`: Manually resolve conflicts

### Deleting Scenarios

#### Via Web

1. Select a scenario
2. Click the "Delete" button
3. Click "Confirm" in the confirmation popup

⚠️ **Warning**: Deleted scenarios cannot be recovered. Associated test results are retained, but the scenario definition is deleted.

#### Via CLI

```bash
fluxloop scenarios delete --scenario password-reset

# Delete multiple scenarios
fluxloop scenarios delete --scenario "test-*"
```

## Scenario Templates

FluxLoop provides templates for common use cases:

### Customer Support

```yaml
name: customer-support-template
personas:
  - frustrated-customer
  - confused-new-user
  - technical-expert
common_inputs:
  - "I have a problem with {product}"
  - "How do I {action}?"
  - "Why is {feature} not working?"
criteria:
  - empathy_check
  - solution_provided
  - response_time_under_3s
```

### Code Generation

```yaml
name: code-generation-template
personas:
  - junior-developer
  - senior-engineer
  - non-programmer
common_inputs:
  - "Write a function to {task}"
  - "Debug this code: {code_snippet}"
  - "Explain how {concept} works"
criteria:
  - code_correctness
  - includes_explanation
  - follows_best_practices
```

### Data Analysis

```yaml
name: data-analysis-template
personas:
  - business-analyst
  - data-scientist
  - executive
common_inputs:
  - "Analyze {dataset}"
  - "What trends do you see in {data}?"
  - "Create a chart showing {metric}"
criteria:
  - accurate_analysis
  - clear_visualization
  - actionable_insights
```

## Best Practices

### Naming Conventions

Use consistent naming conventions:

```
# Projects
company-product-agent
team-usecase-bot

# Scenarios
feature-action-test
persona-workflow-validation

# Examples
acme-support-agent
payments-refund-test
newuser-onboarding-validation
```

### Organization

Group scenarios logically:

```
Projects/
├── customer-support/
│   ├── onboarding/
│   ├── troubleshooting/
│   └── escalation/
├── sales-assistant/
│   ├── lead-qualification/
│   ├── product-recommendation/
│   └── objection-handling/
```

### Versioning

Separate significant changes into new scenarios:

```
# Good
password-reset-v1
password-reset-v2-with-2fa

# Bad (continuous modification without versions)
password-reset (continuously modified)
```

### Documentation

Add clear descriptions to each scenario:

```yaml
name: checkout-flow-test
description: |
  Tests the complete checkout flow including:
  - Cart review
  - Address entry
  - Payment processing
  - Order confirmation

  Expected behavior:
  - Agent should guide user through each step
  - Validate input at each stage
  - Handle errors gracefully
```

## Collaboration Features

### Sharing Projects

Share projects with team members:

1. Select a project
2. "Settings" → "Members"
3. Click "Invite Member"
4. Enter email and select role:
   - **Viewer**: Read-only access
   - **Editor**: Can edit scenarios
   - **Admin**: Can change project settings

### Scenario Comments

Add comments to scenarios:

1. On the scenario detail page, go to the "Comments" tab
2. Write a comment
3. Can link to specific test runs
4. Team members are automatically notified

### Activity Feed

Track project activity:

- Scenario creation/modification/deletion
- Test executions
- Member additions/removals
- Setting changes

## Next Steps

- [Viewing Results](./viewing-results.md): View and analyze test results
- [API Keys](./api-keys.md): Create and manage API keys
- [CLI Commands](/cli/commands/scenarios): Manage scenarios with CLI
