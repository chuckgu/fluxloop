---
sidebar_position: 2
---

# Artifacts Reference

Understanding FluxLoop experiment artifacts.

## Output Structure

```
results/exp_20241101_123456/
├── summary.json                # Aggregate statistics
├── trace_summary.jsonl         # Per-trace summaries
├── traces.jsonl                # Detailed traces
├── observations.jsonl          # Observation stream
└── per_trace_analysis/         # Human-readable timelines
    ├── trace_001.md
    ├── trace_002.md
    └── ...
```

## Artifact Types

### summary.json

Aggregate experiment statistics.

### trace_summary.jsonl

One JSON object per line, each representing a trace summary.

### traces.jsonl

Complete trace data with all observations.

### observations.jsonl

Raw observation stream.

## Coming Soon

Detailed artifact schema documentation is coming soon.

