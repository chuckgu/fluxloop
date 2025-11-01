---
sidebar_position: 2
---

# generate Command

Generate input variations from base inputs using LLM or deterministic strategies.

## Usage

```bash
fluxloop generate inputs [OPTIONS]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--limit` | Number of inputs to generate | 50 |
| `--mode` | Generation mode: `llm` or `deterministic` | From config |
| `--output` | Output file path | `inputs/generated.yaml` |
| `--overwrite` | Overwrite existing file | `false` |

## Examples

### Basic Generation

Generate 50 inputs using LLM:

```bash
fluxloop generate inputs --limit 50
```

### Deterministic Mode

Generate inputs without LLM:

```bash
fluxloop generate inputs --mode deterministic --limit 100
```

### Custom Output

Save to custom location:

```bash
fluxloop generate inputs --output my-inputs.yaml --limit 30
```

### Overwrite Existing

Replace existing generated inputs:

```bash
fluxloop generate inputs --overwrite --limit 100
```

## How It Works

### 1. Reads Configuration

Loads personas and base inputs from `configs/input.yaml`:

```yaml
personas:
  - name: novice_user
    description: New to the system

base_inputs:
  - input: "How do I start?"
    persona: novice_user
```

### 2. Applies Generation Strategies

**LLM Mode:**
- Rephrase: Different wording, same meaning
- Verbose: Longer, more detailed versions
- Concise: Shorter, direct versions
- Error-prone: Typos, grammar mistakes

**Deterministic Mode:**
- Pattern-based transformations
- No LLM API calls required

### 3. Outputs Generated File

Creates `inputs/generated.yaml`:

```yaml
generated_inputs:
  - input: "What are the steps to get started?"
    source: "How do I start?"
    strategy: rephrase
    persona: novice_user
  
  - input: "how do i strt?"
    source: "How do I start?"
    strategy: error_prone
    persona: novice_user
```

## Configuration

Set LLM provider in `configs/input.yaml`:

```yaml
input_generation:
  mode: llm
  llm:
    provider: openai        # or anthropic
    model: gpt-4o-mini
    temperature: 0.7
  strategies:
    - rephrase
    - verbose
    - concise
    - error_prone
```

## API Key Setup

Before generating with LLM:

```bash
# Set API key
fluxloop config set-llm openai sk-your-key --model gpt-4o-mini

# Or add to .env
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

## Best Practices

1. **Start small**: Generate 10-20 inputs first to test
2. **Review outputs**: Check quality before generating large batches
3. **Mix strategies**: Use all strategies for diversity
4. **Version control**: Commit generated inputs for reproducibility

## Troubleshooting

### "No API key found"

Set your LLM provider API key:
```bash
fluxloop config set-llm openai sk-your-key
```

### "Generation failed"

Check your internet connection and API key validity.

### "File already exists"

Use `--overwrite` flag or delete existing file:
```bash
rm inputs/generated.yaml
fluxloop generate inputs
```

## Next Steps

- [Run Experiment](./run) - Run simulation with generated inputs
- [Input Configuration](../configuration/input-config) - Configure generation settings
