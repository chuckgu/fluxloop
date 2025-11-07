---
title: Subprocess (JSONL Protocol)
sidebar_position: 7
tags: [subprocess, jsonl, node, go, p0]
---

## Overview

- **When to Use**: Integrate agents in other languages (Node.js, Go, Rust, etc)
- **Difficulty**: ⭐⭐ Intermediate
- **Priority**: P0 (Production-Ready)
- **Dependencies**: Executable binary/script, JSONL protocol implementation

Execute local processes and exchange JSONL (JSON Lines) messages via STDIN/STDOUT. Use when integrating agents written in languages other than Python.

## Basic Configuration

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    protocol: jsonl
```

## Full Options

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]      # Command array
    cwd: .                              # Working directory
    env:                                # Environment variables (optional)
      NODE_ENV: production
      API_KEY: "${API_KEY}"             # Environment variable substitution
    protocol: jsonl                     # Currently only jsonl supported
    
    stream_output_path: "delta"         # Delta path within JSONL events
    ready_pattern: "^READY$"            # Optional: startup ready signal (regex)
    timeout: 120s                       # Overall execution timeout
    
    # Process management
    kill_signal: SIGTERM                # Termination signal (default)
    kill_timeout: 5s                    # Force kill wait time
    
  guards:
    max_duration: 180s
```

## JSONL Protocol Convention

### FluxLoop → Process (STDIN)

**Input Message**
```json
{"type": "input", "input": "User query here", "context": {"persona": "expert_user", "iteration": 1}}
```

### Process → FluxLoop (STDOUT)

**Streaming Delta** (optional)
```json
{"type": "delta", "delta": "First chunk"}
{"type": "delta", "delta": " second chunk"}
```

**Final Response**
```json
{"type": "final", "output": "Complete response text"}
```

**Error Reporting** (optional)
```json
{"type": "error", "error": "Something went wrong", "code": "INTERNAL_ERROR"}
```

### Ready Signal (Optional)

Process outputs to STDOUT after initialization:
```
READY
```

FluxLoop sends input message after detecting this line.

## Examples

### Example 1: Node.js Echo Agent

**agent.mjs**
```javascript
import readline from 'readline';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Ready signal
console.log('READY');

rl.on('line', (line) => {
  const msg = JSON.parse(line);
  
  if (msg.type === 'input') {
    const response = `Echo from Node.js: ${msg.input}`;
    console.log(JSON.stringify({ type: 'final', output: response }));
  }
});
```

**configs/simulation.yaml**
```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    protocol: jsonl
    ready_pattern: "^READY$"
```

**Execution**
```bash
fluxloop run experiment
```

### Example 2: Node.js Streaming Agent (OpenAI)

**streaming_agent.mjs**
```javascript
import OpenAI from 'openai';
import readline from 'readline';

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

console.log('READY');

rl.on('line', async (line) => {
  const msg = JSON.parse(line);
  
  if (msg.type === 'input') {
    const stream = await client.chat.completions.create({
      model: 'gpt-4',
      messages: [{ role: 'user', content: msg.input }],
      stream: true,
    });
    
    for await (const chunk of stream) {
      const delta = chunk.choices[0]?.delta?.content || '';
      if (delta) {
        console.log(JSON.stringify({ type: 'delta', delta }));
      }
    }
    
    console.log(JSON.stringify({ type: 'final', output: '[STREAM_END]' }));
  }
});
```

**configs/simulation.yaml**
```yaml
runner:
  process:
    command: ["node", "streaming_agent.mjs"]
    protocol: jsonl
    stream_output_path: "delta"
    ready_pattern: "^READY$"
    timeout: 120s
```

### Example 3: Go Agent

**agent.go**
```go
package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "os"
)

type InputMessage struct {
    Type    string                 `json:"type"`
    Input   string                 `json:"input"`
    Context map[string]interface{} `json:"context"`
}

type OutputMessage struct {
    Type   string `json:"type"`
    Output string `json:"output"`
}

func main() {
    fmt.Println("READY")
    
    scanner := bufio.NewScanner(os.Stdin)
    for scanner.Scan() {
        var msg InputMessage
        if err := json.Unmarshal(scanner.Bytes(), &msg); err != nil {
            continue
        }
        
        if msg.Type == "input" {
            response := OutputMessage{
                Type:   "final",
                Output: "Response from Go: " + msg.Input,
            }
            data, _ := json.Marshal(response)
            fmt.Println(string(data))
        }
    }
}
```

**Build & Configure**
```bash
go build -o agent agent.go
```

**configs/simulation.yaml**
```yaml
runner:
  process:
    command: ["./agent"]
    protocol: jsonl
    ready_pattern: "^READY$"
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Process fails to start | Command path error | Use absolute path in `command` or adjust `cwd` |
| JSONL parsing failure | Invalid JSON format | Check STDERR logs, debug process |
| Timeout | Slow response or infinite wait | Increase `timeout`, verify `ready_pattern` |
| Ready signal not detected | Pattern mismatch | Test regex, disable STDOUT buffering |
| Missing output | STDOUT buffering | Node: `console.log`, Go: `fmt.Println` (auto-flush) |
| Zombie process | Termination failure | Adjust `kill_signal`/`kill_timeout` |

## Advanced Topics

### Environment Variable Isolation

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    env:
      NODE_ENV: production
      API_KEY: "${OPENAI_API_KEY}"      # Load from .env file
    # System environment variables inherited by default
```

### Error Handling

Process reports error:

```json
{"type": "error", "error": "API rate limit exceeded", "code": "RATE_LIMIT"}
```

FluxLoop records as experiment failure and proceeds to next input.

### Run Without Ready Signal

Simple processes can omit `ready_pattern`:

```yaml
runner:
  process:
    command: ["python", "simple_agent.py"]
    protocol: jsonl
    # ready_pattern omitted → send input immediately
```

Note: Processes with long initialization may lose first input.

### Multiple Input Processing (Reuse)

By default, FluxLoop spawns a new process per input. For reuse, implement multi-input handling:

```javascript
// Node.js reuse example
rl.on('line', async (line) => {
  const msg = JSON.parse(line);
  if (msg.type === 'input') {
    const output = await process_input(msg.input);
    console.log(JSON.stringify({ type: 'final', output }));
  }
});
```

Configure reuse mode (P1 roadmap):

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    protocol: jsonl
    reuse: true                         # Process reuse (P1 roadmap)
```

## Performance

- **Startup Overhead**: Process creation (~10-100ms). Accumulates in repeated experiments.
- **Parallel Execution**: Use `simulation.parallelism` for concurrent processes.
- **Memory**: Each process uses independent memory space.

## Security

- **Input Validation**: Processes should consider malicious input possibilities.
- **Sandboxing**: Recommend running in container environment (P2: Docker pattern).
- **Log Sensitive Info**: Ensure API keys not exposed in STDOUT/STDERR.

## Related Documentation

- HTTP REST (Coming soon) – remote service integration
- Container Docker (Coming soon) – isolated process execution
- Streaming Schema (Coming soon) – advanced delta path configuration
- Guards (Coming soon) – timeout/resource limits
- [Simulation Config](../simulation-config) – full configuration structure

## MCP Metadata

```json
{
  "pattern": "subprocess-jsonl",
  "tags": ["subprocess", "jsonl", "node", "go", "rust", "p0", "cross-language"],
  "examples": [
    "examples/node-agent/",
    "samples/go-jsonl.md",
    "samples/rust-stdio.md"
  ],
  "faq": [
    "How to debug JSONL parsing errors?",
    "Process reuse vs per-input spawn?",
    "Environment variable passing?",
    "Ready signal best practices?"
  ],
  "related_patterns": [
    "http-rest",
    "container-docker",
    "streaming-schema"
  ],
  "dependencies": [
    "Node.js/Go/Rust runtime",
    "JSONL protocol implementation"
  ]
}
```
