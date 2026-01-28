# fluxloop scenarios

Manage test scenarios on the Web Platform.

## Synopsis

```bash
fluxloop scenarios [command] [options]
```

## Description

The `scenarios` command allows you to manage cloud-based test scenarios. Scenarios are high-level test cases that include personas, inputs, and evaluation criteria.

## Commands

### `fluxloop scenarios list`

List all scenarios in the current Web Project.

**Usage:**

```bash
fluxloop scenarios list [options]
```

**Examples:**

```bash
# List scenarios for the current project
fluxloop scenarios list
```

---

### `fluxloop scenarios create`

Create a new test scenario on the Web Platform.

**Usage:**

```bash
fluxloop scenarios create [options]
```

**Options:**

- `--name <name>`: Scenario name (required)
- `--description <desc>`: Long description
- `--goal <text>`: One-sentence objective
- `--constraint <text>`: Repeatable constraint (e.g., "Response in Korean")
- `--success-criteria <text>`: Repeatable success criteria
- `--select/--no-select`: Automatically select the created scenario (default: true)

**Examples:**

```bash
# Create a simple scenario
fluxloop scenarios create --name "Basic Help" --goal "Verify agent can answer basic help questions"

# Create a complex scenario with constraints
fluxloop scenarios create --name "Product Search" \
  --constraint "Only search for available products" \
  --success-criteria "Agent must return at least 3 results"
```

---

### `fluxloop scenarios select`

Select a cloud scenario as the current working context.

**Usage:**

```bash
fluxloop scenarios select <scenario_id> [options]
```

**Options:**

- `--local-path <folder>`: Link to a local scenario folder in `.fluxloop/scenarios/`

**Examples:**

```bash
# Select a scenario by ID
fluxloop scenarios select sc_12345

# Select and link to a local folder
fluxloop scenarios select sc_12345 --local-path onboarding-tests
```

---

### `fluxloop scenarios show`

Display details of a specific scenario.

**Usage:**

```bash
fluxloop scenarios show --scenario <id>
```

---

### `fluxloop scenarios generate`

Generate a scenario definition from a user intent description using the Alignment Agent.

**Usage:**

```bash
fluxloop scenarios generate --intent "I want to test if the agent can handle refund requests according to company policy"
```

---

## Architecture: Local vs. Cloud

FluxLoop distinguishes between **Web Scenarios** and **Local Scenarios**:

1.  **Web Scenarios**: Centrally managed definitions on [app.fluxloop.ai](https://app.fluxloop.ai). They serve as the source of truth for teams.
2.  **Local Scenarios**: Folders in your project (usually `.fluxloop/scenarios/{name}/`) that contain local configuration, agent code, and results.

### The Connection Flow

```
1. fluxloop projects select <project_id>      # Link workspace to Web Project
2. fluxloop scenarios list                    # See available scenarios
3. fluxloop init scenario <name> --link <id>  # Link local folder to Web Scenario
4. fluxloop sync pull                         # Download data from Web to Local
5. fluxloop test                              # Run tests locally
6. fluxloop sync upload                       # Upload results back to Web
```

## Related Commands

- [`fluxloop init scenario`](./init) - Create the local folder structure
- [`fluxloop projects`](./projects) - Manage the parent project
- [`fluxloop sync pull`](./sync) - Download scenario data
