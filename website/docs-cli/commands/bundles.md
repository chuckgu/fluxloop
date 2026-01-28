# fluxloop bundles

Create and manage test bundles.

## Synopsis

```bash
fluxloop bundles [command] [options]
```

## Description

The `bundles` command creates and manages test bundles. Bundles group related personas, inputs, and scenarios together for organized testing.

## Commands

### `fluxloop bundles create`

Create a new test bundle.

**Usage:**

```bash
fluxloop bundles create [options]
```

**Options:**

- `--name \<name\>`: Bundle name (required)
- `--description <desc>`: Bundle description
- `--personas <file>`: Personas file to include
- `--inputs <file>`: Inputs file to include
- `--scenarios <pattern>`: Scenario files to include (supports glob patterns)
- `--output <path>`: Output file path (default: .fluxloop/bundles/\<name\>.yaml)

**Examples:**

```bash
# Create bundle with personas and inputs
fluxloop bundles create \
  --name "password-reset-suite" \
  --description "Complete password reset test suite" \
  --personas personas/auth-personas.yaml \
  --inputs inputs/password-reset.yaml

# Create bundle with scenarios
fluxloop bundles create \
  --name "onboarding-suite" \
  --scenarios "scenarios/onboarding-*.yaml"

# Create comprehensive bundle
fluxloop bundles create \
  --name "full-auth-suite" \
  --personas personas/auth-personas.yaml \
  --inputs inputs/auth-inputs.yaml \
  --scenarios "scenarios/auth-*.yaml"
```

**Interactive Flow:**

```
$ fluxloop bundles create

Create New Bundle

Bundle name: customer-support-suite
Description: Complete customer support test scenarios

Select components to include:

Personas:
  ☑ frustrated-customer
  ☑ tech-savvy-user
  ☑ elderly-customer
  ☐ VIP-customer

Inputs:
  ☑ .fluxloop/inputs/password-reset.yaml (10 inputs)
  ☑ .fluxloop/inputs/account-issues.yaml (15 inputs)
  ☑ .fluxloop/inputs/billing.yaml (8 inputs)

Scenarios:
  ☑ password-reset
  ☑ account-creation
  ☑ order-tracking
  ☐ refund-request

✅ Bundle created: customer-support-suite

Bundle saved to: .fluxloop/bundles/customer-support-suite.yaml

Contents:
  • 3 personas
  • 33 inputs
  • 3 scenarios

Next steps:
• Run the bundle: fluxloop test --bundle customer-support-suite
• Share with team: fluxloop sync upload
```

### `fluxloop bundles list`

List all available bundles.

**Usage:**

```bash
fluxloop bundles list [options]
```

**Options:**

- `--json`: Output in JSON format

**Examples:**

```bash
# List all bundles
fluxloop bundles list

# List in JSON format
fluxloop bundles list --json
```

**Output:**

```
Test Bundles

┌──────────────────────────────────────────────────────────────────┐
│ customer-support-suite                                           │
│ Complete customer support test scenarios                         │
│ Created: Jan 15, 2024                                            │
│ Components: 3 personas, 33 inputs, 3 scenarios                   │
│ Last run: 2 hours ago | Success: 87%                            │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ authentication-suite                                             │
│ All authentication-related tests                                 │
│ Created: Jan 10, 2024                                            │
│ Components: 5 personas, 50 inputs, 8 scenarios                   │
│ Last run: 1 day ago | Success: 92%                              │
└──────────────────────────────────────────────────────────────────┘

Total: 2 bundles
```

### `fluxloop bundles show`

Display bundle details.

**Usage:**

```bash
fluxloop bundles show \<name\> [options]
```

**Options:**

- `--json`: Output in JSON format

**Examples:**

```bash
# Show bundle details
fluxloop bundles show customer-support-suite

# Get details in JSON format
fluxloop bundles show customer-support-suite --json
```

**Output:**

```
Bundle: customer-support-suite

Description: Complete customer support test scenarios
Created: Jan 15, 2024
Updated: Jan 15, 2024

Personas (3):
  • frustrated-customer
  • tech-savvy-user
  • elderly-customer

Inputs (33):
  From password-reset.yaml:
    • "I can't login! This is ridiculous!" (frustrated-customer)
    • "I've been trying for 30 minutes" (frustrated-customer)
    • "Getting error 500 when resetting" (tech-savvy-user)
    ... 7 more

  From account-issues.yaml:
    • "My account is locked" (frustrated-customer)
    • "Can't update my email" (tech-savvy-user)
    ... 13 more

  From billing.yaml:
    • "Wrong charge on my card" (frustrated-customer)
    ... 7 more

Scenarios (3):
  1. password-reset
     • 10 inputs across 3 personas
     • 4 evaluation criteria

  2. account-creation
     • 15 inputs across 3 personas
     • 6 evaluation criteria

  3. order-tracking
     • 8 inputs across 3 personas
     • 5 evaluation criteria

Test Runs: 15 total
  • Last 30 days: 15 runs
  • Success rate: 87%
  • Avg duration: 12.5s

File: .fluxloop/bundles/customer-support-suite.yaml
```

### `fluxloop bundles update`

Update an existing bundle.

**Usage:**

```bash
fluxloop bundles update \<name\> [options]
```

**Options:**

- `--add-persona <file>`: Add persona file
- `--add-input <file>`: Add input file
- `--add-scenario <pattern>`: Add scenario file(s)
- `--remove-persona \<name\>`: Remove persona
- `--remove-input <file>`: Remove input file
- `--remove-scenario \<name\>`: Remove scenario

**Examples:**

```bash
# Add scenario to bundle
fluxloop bundles update customer-support-suite \
  --add-scenario "scenarios/refund-request.yaml"

# Remove persona from bundle
fluxloop bundles update customer-support-suite \
  --remove-persona "VIP-customer"

# Add multiple inputs
fluxloop bundles update customer-support-suite \
  --add-input "inputs/new-issues.yaml"
```

### `fluxloop bundles delete`

Delete a bundle.

**Usage:**

```bash
fluxloop bundles delete \<name\> [options]
```

**Options:**

- `--force`: Skip confirmation prompt

**Examples:**

```bash
# Delete bundle (with confirmation)
fluxloop bundles delete old-suite

# Delete without confirmation
fluxloop bundles delete old-suite --force
```

### `fluxloop bundles export`

Export a bundle for sharing.

**Usage:**

```bash
fluxloop bundles export \<name\> [options]
```

**Options:**

- `--output <path>`: Output file path (default: \<name\>.bundle.tar.gz)
- `--format <format>`: Export format (tar.gz, zip, directory)

**Examples:**

```bash
# Export as tar.gz
fluxloop bundles export customer-support-suite

# Export as zip
fluxloop bundles export customer-support-suite \
  --format zip \
  --output support-tests.zip

# Export as directory
fluxloop bundles export customer-support-suite \
  --format directory \
  --output ./exported-bundle
```

### `fluxloop bundles import`

Import a bundle.

**Usage:**

```bash
fluxloop bundles import <file> [options]
```

**Options:**

- `--name \<name\>`: New bundle name (default: original name)

**Examples:**

```bash
# Import bundle
fluxloop bundles import customer-support-suite.bundle.tar.gz

# Import with new name
fluxloop bundles import support-tests.zip \
  --name "imported-support-suite"
```

## Bundle File Format

Bundles are defined in YAML format:

```yaml
# .fluxloop/bundles/customer-support-suite.yaml
name: customer-support-suite
description: Complete customer support test scenarios
version: 1.0.0
created: "2024-01-15T10:00:00Z"
updated: "2024-01-15T14:30:00Z"

personas:
  sources:
    - file: personas/auth-personas.yaml
      personas:
        - frustrated-customer
        - tech-savvy-user
        - elderly-customer

inputs:
  sources:
    - file: inputs/password-reset.yaml
      count: 10
    - file: inputs/account-issues.yaml
      count: 15
    - file: inputs/billing.yaml
      count: 8

scenarios:
  sources:
    - file: scenarios/password-reset.yaml
    - file: scenarios/account-creation.yaml
    - file: scenarios/order-tracking.yaml

configuration:
  parallel: true
  max_concurrency: 5
  timeout: 30000
  retry_failed: true
  retry_count: 2

metadata:
  tags:
    - customer-support
    - authentication
    - e-commerce
  owner: support-team
  last_run: "2024-01-15T14:30:00Z"
  success_rate: 0.87
```

## Best Practices

### 1. Organize by Feature

Create bundles for specific features:

```bash
# Authentication bundle
fluxloop bundles create \
  --name "auth-suite" \
  --scenarios "scenarios/auth-*.yaml"

# Billing bundle
fluxloop bundles create \
  --name "billing-suite" \
  --scenarios "scenarios/billing-*.yaml"

# E2E bundle
fluxloop bundles create \
  --name "e2e-suite" \
  --scenarios "scenarios/*.yaml"
```

### 2. Version Control

Keep bundles in version control:

```gitignore
# .gitignore

# Keep bundles
!.fluxloop/bundles/

# Ignore exported bundles
*.bundle.tar.gz
*.bundle.zip
```

### 3. Use Meaningful Names

```bash
✅ Good:
  • password-reset-complete-suite
  • onboarding-flow-tests
  • critical-path-scenarios

❌ Bad:
  • bundle1
  • test_suite
  • temp
```

### 4. Document Bundle Purpose

```yaml
name: critical-path-suite
description: |
  Critical path test scenarios that must pass before deployment.
  Includes:
    - User authentication
    - Order placement
    - Payment processing
    - Order tracking

  Run this suite:
    - Before every deployment
    - After major changes to auth or checkout
    - Daily in CI/CD

  Success criteria: 100% pass rate required
```

### 5. Optimize for CI/CD

```yaml
configuration:
  # Run tests in parallel for speed
  parallel: true
  max_concurrency: 10

  # Short timeout for CI
  timeout: 20000

  # Don't retry in CI (fail fast)
  retry_failed: false

  # Generate JUnit XML for CI
  output_format: junit
  output_file: test-results.xml
```

## Bundle Templates

### Smoke Test Bundle

Quick validation of core functionality:

```yaml
name: smoke-test-suite
description: Fast smoke tests for core functionality
personas:
  - typical-user
inputs:
  - file: inputs/happy-path.yaml
scenarios:
  - login
  - basic-operation
  - logout
configuration:
  parallel: true
  timeout: 10000
```

### Regression Test Bundle

Comprehensive test coverage:

```yaml
name: regression-suite
description: Full regression test suite
personas:
  sources:
    - file: personas/all-personas.yaml
inputs:
  sources:
    - file: inputs/**/*.yaml
scenarios:
  sources:
    - file: scenarios/**/*.yaml
configuration:
  parallel: true
  max_concurrency: 20
  timeout: 60000
  retry_failed: true
```

### Performance Test Bundle

Focus on performance metrics:

```yaml
name: performance-suite
description: Performance and load testing
scenarios:
  - file: scenarios/high-load.yaml
configuration:
  parallel: true
  max_concurrency: 100
  timeout: 5000
  metrics:
    - response_time
    - token_usage
    - cost_per_interaction
  thresholds:
    max_response_time: 3000
    max_cost: 0.05
```

## Troubleshooting

### Bundle Not Found

```
❌ Error: Bundle 'my-suite' not found

Available bundles:
  • customer-support-suite
  • authentication-suite

Run 'fluxloop bundles list' to see all bundles.
```

### Missing Components

```
❌ Error: Missing components in bundle

Bundle: customer-support-suite
Missing:
  • personas/auth-personas.yaml
  • scenarios/refund-request.yaml

Solution:
  • Ensure all referenced files exist
  • Update bundle to remove missing components
  • Or restore missing files
```

### Invalid Bundle Format

```
❌ Error: Invalid bundle file format

File: .fluxloop/bundles/my-suite.yaml
Line 10: 'scenarios' must be an array

Solution:
  • Check YAML syntax
  • Refer to bundle format documentation
```

## Related Commands

- [`fluxloop test`](./test): Run tests with bundles
- [`fluxloop personas`](./personas): Manage personas
- [`fluxloop inputs`](./inputs): Manage inputs
- [`fluxloop scenarios`](./scenarios): Manage scenarios

## See Also

- [Testing Workflows](../workflows/basic-workflow): End-to-end testing guide
- [CI/CD Integration](../workflows/ci-cd-integration): Using bundles in CI/CD
