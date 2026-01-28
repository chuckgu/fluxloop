---
sidebar_position: 4
---

# Team Collaboration

Collaborate with your team using FluxLoop Web Platform.

## Overview

FluxLoop enables teams to:
- Share test scenarios and bundles
- Collaborate on test results
- Track agent improvements over time
- Standardize evaluation criteria

## Setup

### 1. Create Team Project

Create a project on [FluxLoop Web Platform](https://app.fluxloop.ai):

```
1. Login to app.fluxloop.ai
2. Click "New Project"
3. Name: "my-agent-testing"
4. Invite team members
```

### 2. Authenticate CLI

Each team member authenticates:

```bash
fluxloop auth login
```

### 3. Link Local Project

Link your local project to the team project:

```bash
fluxloop projects select my-agent-testing
```

## Workflows

### Share Scenarios

**Create and share test scenarios:**

```bash
# Developer A creates scenario
fluxloop scenarios create edge-cases

# Add inputs locally
fluxloop inputs generate --persona power_user --count 50
fluxloop bundles create --name edge-cases

# Upload to platform
fluxloop sync upload --scenario edge-cases
```

**Teammate pulls and tests:**

```bash
# Developer B pulls scenario
fluxloop sync pull --scenario edge-cases

# Run tests
fluxloop test --scenario edge-cases
```

### Collaborative Testing

**Run tests and share results:**

```bash
# Run test
fluxloop test --scenario production-regression --no-skip-upload

# Results automatically uploaded
# Team can view at: https://results.fluxloop.ai/run/run_123
```

**Review results together:**
- View test results on Web Platform
- Add comments and discussions
- Compare with previous runs
- Track improvements

### Sync Test Data

**Bidirectional sync:**

```bash
# Pull latest from team
fluxloop sync pull

# Make local changes
fluxloop inputs generate --persona new_user --count 20

# Push changes
fluxloop sync upload --bundle-id latest

# Or use sync command
fluxloop sync
```

## Best Practices

### 1. Regular Syncs

Sync frequently to stay up-to-date:

```bash
# Daily sync routine
fluxloop sync pull
fluxloop sync pull
```

### 2. Meaningful Names

Use descriptive names for scenarios:

```bash
✅ fluxloop scenarios create "production-regression-v2"
✅ fluxloop scenarios create "auth-flow-edge-cases"

❌ fluxloop scenarios create "test1"
❌ fluxloop scenarios create "my-scenario"
```

### 3. Upload Results

Always upload test results (uploads are automatic by default):

```bash
fluxloop test --no-skip-upload
```

Benefits:
- Team visibility
- Historical tracking
- Automated evaluation

### 4. Document Scenarios

Add descriptions to scenarios:

```yaml
# scenarios/prod-regression/metadata.yaml
scenario_id: prod-regression-v2
name: "Production Regression Tests v2"
description: |
  Critical production paths that must pass before deployment.
  Covers authentication, user management, and billing flows.

owner: team@company.com
tags:
  - production
  - regression
  - critical
```

## Conflict Resolution

### Detect Conflicts

When pulling, FluxLoop detects conflicts:

```bash
$ fluxloop sync pull

[WARNING] Conflict detected in: scenarios/prod-tests
  Local version: Modified 2024-11-01 10:00
  Remote version: Modified 2024-11-01 11:00

Options:
  1. Keep local (your changes)
  2. Take remote (teammate's changes)
  3. Merge (combine both)
Choose (1/2/3):
```

### Resolve Conflicts

**Option 1: Keep Local**

```bash
fluxloop sync pull --keep-local
```

Your changes preserved, remote changes ignored.

**Option 2: Take Remote**

```bash
fluxloop sync pull --keep-remote
```

Remote changes accepted, local changes discarded.

**Option 3: Manual Merge**

```bash
# Pull and create merge file
fluxloop sync pull --create-merge

# Edit merge file
code scenarios/prod-tests/MERGE.yaml

# Complete merge
fluxloop scenarios merge-complete prod-tests
```

See [Conflict Resolution Guide](../guides/conflict-resolution) for details.

## Permissions

### Project Roles

FluxLoop projects have roles:

| Role | Can View | Can Edit | Can Delete | Can Manage Team |
|------|----------|----------|------------|-----------------|
| Viewer | ✅ | ❌ | ❌ | ❌ |
| Editor | ✅ | ✅ | ❌ | ❌ |
| Admin | ✅ | ✅ | ✅ | ✅ |

### Manage Team

Project admins can invite members:

```
1. Go to app.fluxloop.ai/projects/my-project/settings
2. Click "Team"
3. Click "Invite Member"
4. Enter email and select role
5. Send invitation
```

## CI/CD Integration

### Shared API Key

Create a team API key for CI:

```bash
# Admin creates API key
fluxloop apikeys create --name "ci-bot" --scope read-write

# Add to CI environment
export FLUXLOOP_API_KEY=flx_...
```

### Automated Testing

```yaml
# .github/workflows/test.yml
name: FluxLoop Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Authenticate
        env:
          FLUXLOOP_API_KEY: ${{ secrets.FLUXLOOP_API_KEY }}
        run: echo "Authenticated"

      - name: Pull Latest Scenarios
        run: fluxloop sync pull --yes

      - name: Run Tests
        run: fluxloop test --scenario production --yes --no-skip-upload

      - name: Check Results
        run: fluxloop results check --fail-on-regression
```

## Communication

### Result Notifications

Get notified on test results:

```
1. Go to app.fluxloop.ai/projects/my-project/settings
2. Click "Notifications"
3. Enable:
   - Slack integration
   - Email notifications
   - Webhook (custom)
```

### Comments

Add comments to test results:

```
1. View result on Web Platform
2. Click "Add Comment"
3. Tag teammates: @alice @bob
4. Discuss findings
```

## Workflow Examples

### Example 1: Pre-Deployment Testing

```bash
# 1. Pull production regression tests
fluxloop sync pull --scenario production

# 2. Run tests locally
fluxloop test --scenario production

# 3. Review results
fluxloop results show

# 4. If pass, upload results
fluxloop sync upload --scenario production

# 5. Team reviews on Web Platform
# 6. Approve deployment
```

### Example 2: Feature Development

```bash
# Developer A: Create feature tests
fluxloop scenarios create new-feature-tests
fluxloop inputs generate --topic "new feature" --count 30
fluxloop bundles create --name new-feature-tests
fluxloop sync upload --scenario new-feature-tests

# Developer B: Test feature
fluxloop sync pull --scenario new-feature-tests
fluxloop test --scenario new-feature-tests --no-skip-upload

# Team: Review results
# app.fluxloop.ai/run/run_123
```

### Example 3: Regression Detection

```bash
# Daily CI job
# 1. Pull latest scenarios
fluxloop sync pull --yes

# 2. Run all tests
fluxloop test --all-scenarios --no-skip-upload

# 3. Compare with baseline
fluxloop results compare --baseline last-week

# 4. Alert on regressions
fluxloop results check --fail-on-regression
```

## Troubleshooting

### Sync Issues

**Problem**: Sync fails

**Solution**: Check authentication

```bash
fluxloop auth status
fluxloop auth login
```

### Permission Errors

**Problem**: "Insufficient permissions"

**Solution**: Ask admin for appropriate role

```bash
$ fluxloop sync upload
[ERROR] Insufficient permissions
Contact project admin for Editor or Admin role
```

### Merge Conflicts

**Problem**: Unable to merge changes

**Solution**: Use force pull or manual merge

```bash
# Force pull (discard local)
fluxloop pull --force

# Or manual merge
fluxloop pull --create-merge
```

## Related

- [CI/CD Integration](./ci-cd-integration) - Automate testing
- [Sync Command](../commands/sync) - Synchronization
- [Projects Command](../commands/projects) - Manage projects

## Next Steps

- Set up team project on Web Platform
- Invite teammates
- Create shared scenarios
- Establish testing workflow
