# fluxloop sync

Synchronize data between local environment and the FluxLoop Web Platform.

## Synopsis

```bash
fluxloop sync [command] [options]
```

## Description

The `sync` command handles bidirectional data transfer between your local workspace and the cloud. It is used to pull test scenarios and bundles from the Web Platform, and to upload experiment results for visualization and analysis.

## Commands

### `fluxloop sync pull`

Download test data from the Web Platform to your local project.

**Usage:**

```bash
fluxloop sync pull [options]
```

**Options:**

- `--project-id <id>`: Web Project ID to pull from (defaults to current context)
- `--bundle-version-id <id>`: Specific bundle version ID to pull
- `--scenario <name>`: Local scenario name to sync into
- `--force`: Overwrite local changes without confirmation

**Examples:**

```bash
# Pull latest scenarios for the current project
fluxloop sync pull

# Pull a specific bundle version
fluxloop sync pull --bundle-version-id bv_12345

# Pull into a specific local scenario folder
fluxloop sync pull --scenario onboarding-tests
```

---

### `fluxloop sync upload`

Upload local test results to the FluxLoop Web Platform.

**Usage:**

```bash
fluxloop sync upload [options]
```

**Options:**

- `--experiment-dir <path>`: Directory containing the results to upload (defaults to latest)
- `--scenario <name>`: Scenario name associated with the results
- `--config <path>`: Path to config file to resolve output directory
- `--quiet`: Minimal output during upload

**Examples:**

```bash
# Upload the latest experiment results
fluxloop sync upload

# Upload results from a specific directory
fluxloop sync upload --experiment-dir results/exp_20250128_120000

# Upload results for a specific scenario
fluxloop sync upload --scenario onboarding-tests
```

---

### `fluxloop sync status`

Check the synchronization status between local and cloud.

**Usage:**

```bash
fluxloop sync status [options]
```

**Examples:**

```bash
# View sync status
fluxloop sync status
```

---

## How It Works

### Pulling Data
When you run `fluxloop sync pull`, the CLI:
1.  Authenticates with the Web Platform using your API key.
2.  Fetches scenario definitions, personas, and base inputs.
3.  Saves them into the `.fluxloop/scenarios/` directory (or current directory if no scenario specified).
4.  Updates the local `.state/` to track versions.

### Uploading Results
When you run `fluxloop sync upload`, the CLI:
1.  Packages the local `traces.jsonl`, `observations.jsonl`, and `summary.json` files.
2.  Uploads them to the Web Platform.
3.  Returns a URL to view the interactive dashboard on [results.fluxloop.ai](https://results.fluxloop.ai).

## Best Practices

### 1. Sync Before Testing
Always pull the latest scenarios before running a regression test to ensure you're using the most up-to-date test cases.

```bash
fluxloop sync pull
fluxloop test
```

### 2. Use Automatic Upload
The `fluxloop test` command can automatically upload results. This is recommended for most development workflows.

```bash
# Test and upload in one go
fluxloop test
```

### 3. CI/CD Integration
In CI/CD pipelines, use the `--bundle-version-id` flag to ensure you're testing against a fixed set of inputs.

```bash
# In GitHub Actions
fluxloop sync pull --bundle-version-id $BUNDLE_ID
fluxloop test --skip-upload  # Don't upload if you prefer manual review
fluxloop sync upload --experiment-dir results/latest/
```

## Related Commands

- [`fluxloop test`](./test) - Run tests locally
- [`fluxloop init scenario`](./init) - Initialize a local scenario folder
- [`fluxloop projects select`](./projects) - Link workspace to a Web Project
