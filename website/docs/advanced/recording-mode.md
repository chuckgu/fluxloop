---
sidebar_position: 2
---

# Recording Mode

Enable recording mode to capture function arguments for replay.

## Quick Start

```bash
# Enable recording
fluxloop record enable

# Run your application
python your_app.py

# Disable recording
fluxloop record disable

# Check status
fluxloop record status
```

## Configuration

Recording settings are stored in:
- `.env` - `FLUXLOOP_RECORD_ARGS=true`
- `configs/simulation.yaml` - `replay_args.enabled: true`

## Coming Soon

Detailed documentation is in progress. See [End-to-End Workflow](../guides/end-to-end-workflow) for examples.

