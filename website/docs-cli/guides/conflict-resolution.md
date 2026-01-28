---
sidebar_position: 5
---

# Conflict Resolution

Resolving conflicts when syncing data with FluxLoop Web Platform.

## Overview

Conflicts occur when:
- Local changes exist
- Remote changes were made by teammates
- Both versions modified simultaneously

FluxLoop detects and helps resolve conflicts automatically.

## Detecting Conflicts

### Pull Detection

```bash
$ fluxloop sync pull

[WARNING] Conflict detected in: scenarios/prod-tests
  Local version:  Modified 2024-11-01 10:00 by you
  Remote version: Modified 2024-11-01 11:00 by alice@company.com

Options:
  1. Keep local (discard remote)
  2. Take remote (discard local)
  3. Merge (combine both)
  4. Cancel (do nothing)

Choose (1/2/3/4):
```

### Conflict Types

#### Content Conflict

Both versions modified the same content:

```yaml
# Local
inputs:
  - text: "How do I start?"  # Your version

# Remote
inputs:
  - text: "How do I get started?"  # Teammate's version
```

#### Structural Conflict

Different structural changes:

```yaml
# Local: Added evaluation criteria
evaluation:
  criteria:
    - accuracy

# Remote: Added different criteria
evaluation:
  criteria:
    - helpfulness
```

## Resolution Strategies

### 1. Keep Local

Discard remote changes, keep yours:

```bash
fluxloop sync pull --keep-local

# Or interactively
Choose (1/2/3/4): 1
```

**When to use:**
- You're confident your changes are correct
- Remote changes are outdated
- Working on isolated feature

**Caution:**
- Teammate's work is lost
- May need to coordinate manually

### 2. Take Remote

Discard local changes, accept remote:

```bash
fluxloop sync pull --keep-remote

# Or interactively
Choose (1/2/3/4): 2
```

**When to use:**
- Remote version is authoritative
- Your local changes were experimental
- Want to sync with team

**Caution:**
- Your work is lost
- Save important changes first

### 3. Manual Merge

Combine both versions:

```bash
# Create merge file
fluxloop sync pull --create-merge

# Merge file created:
# scenarios/prod-tests/MERGE.yaml
```

Edit merge file:

```yaml
# MERGE.yaml
inputs:
  # Local version (yours)
  - text: "How do I start?"
    source: local
    author: you
    timestamp: "2024-11-01T10:00:00Z"

  # Remote version (teammate's)
  - text: "How do I get started?"
    source: remote
    author: alice@company.com
    timestamp: "2024-11-01T11:00:00Z"

# Choose one, or keep both:
  - text: "How do I start?"  # Keep this
  # - text: "How do I get started?"  # Comment out
```

Complete merge:

```bash
fluxloop scenarios merge-complete prod-tests
```

### 4. Three-Way Merge

Use common ancestor for intelligent merging:

```bash
fluxloop sync pull --merge-strategy three-way
```

FluxLoop finds common ancestor and merges changes:

```yaml
# Common ancestor
inputs:
  - text: "Start here"

# Your changes
inputs:
  - text: "Start here"
    context: "onboarding"  # Added

# Teammate's changes
inputs:
  - text: "Start here"
    persona: "novice_user"  # Added

# Merged result
inputs:
  - text: "Start here"
    context: "onboarding"    # From you
    persona: "novice_user"   # From teammate
```

## Preventing Conflicts

### 1. Frequent Pulls

Pull often to stay in sync:

```bash
# Start of day
fluxloop sync pull

# Before making changes
fluxloop sync pull
```

### 2. Push Regularly

Upload changes frequently:

```bash
# After making changes
fluxloop sync upload
```

### 3. Communicate

Coordinate with team:

```
Team chat:
"Working on prod-tests scenario today"
"Done with prod-tests, uploaded"
```

### 4. Use Branches

Work on separate scenarios:

```bash
# Alice works on auth scenarios
fluxloop scenarios create auth-tests

# Bob works on billing scenarios
fluxloop scenarios create billing-tests

# No conflicts!
```

## Advanced Resolution

### Diff View

Compare versions:

```bash
fluxloop diff scenarios prod-tests --local-remote
```

Output:

```diff
  inputs:
-   - text: "How do I start?"          # Local
+   - text: "How do I get started?"   # Remote
```

### Conflict Markers

Automatic conflict markers:

```yaml
inputs:
<<<<<<< LOCAL
  - text: "How do I start?"
=======
  - text: "How do I get started?"
>>>>>>> REMOTE
```

Edit and remove markers:

```yaml
inputs:
  - text: "How do I get started?"  # Chose remote version
```

### Partial Acceptance

Accept some changes, reject others:

```bash
# Review changes
fluxloop sync pull --review

# Accept specific changes
fluxloop accept scenarios/prod-tests/input_001
fluxloop accept scenarios/prod-tests/input_002

# Reject others
fluxloop reject scenarios/prod-tests/input_003
```

## Conflict Resolution Tools

### Interactive Mode

```bash
fluxloop sync pull --interactive
```

Shows diff and prompts for each conflict:

```
Conflict 1/5:

Local:
  - text: "How do I start?"

Remote:
  - text: "How do I get started?"

Keep (l)ocal, (r)emote, (e)dit, or (s)kip? [l/r/e/s]:
```

### Visual Diff

Launch visual diff tool:

```bash
fluxloop diff scenarios prod-tests --tool vscode
```

Opens VS Code with side-by-side comparison.

## Best Practices

### 1. Communicate Before Editing

```
✅ "I'm updating prod-tests scenario"
   "Go ahead!"
   [Make changes]
   [Upload]
   "Done!"

❌ [Silent editing]
   [Upload]
   "Oops, conflicts!"
```

### 2. Pull Before Push

```bash
# Always pull first
fluxloop sync pull

# Then upload
fluxloop sync upload
```

### 3. Small, Frequent Changes

```bash
✅ Small changes, uploaded frequently
❌ Large changes, uploaded rarely
```

### 4. Use Descriptive Commit Messages

```bash
fluxloop sync upload --message "Add edge cases for password reset"
```

### 5. Review Conflicts Carefully

```bash
# Don't blindly choose
❌ fluxloop pull --keep-local --yes

# Review first
✅ fluxloop pull --review
```

## Troubleshooting

### Can't Merge Automatically

**Problem**: Complex conflicts

**Solution**: Manual merge

```bash
fluxloop sync pull --create-merge
# Edit manually
fluxloop scenarios merge-complete
```

### Lost Changes

**Problem**: Accidentally discarded changes

**Solution**: Restore from backup

```bash
# FluxLoop keeps backups
fluxloop restore scenarios prod-tests --from backup_20241101_100000
```

### Merge Failed

**Problem**: Merge resulted in invalid scenario

**Solution**: Validate and fix

```bash
fluxloop scenarios validate prod-tests
# Fix errors
fluxloop scenarios validate prod-tests
```

## Related

- [Sync Command](../commands/sync) - Bidirectional sync
- [Sync Command](/cli/commands/sync) - Pull and upload data
- [Team Collaboration](../workflows/team-collaboration) - Workflow

## Next Steps

- Set up regular sync schedule
- Communicate with team about changes
- Practice conflict resolution in staging
- Establish team conventions
