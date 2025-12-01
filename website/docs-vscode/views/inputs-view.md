---
sidebar_position: 2
---

# Inputs View

The **Inputs** view lets you design experiment scenarios without leaving VS Code. It surfaces configuration, base input, generated variations, and recordings in a single tree.

## Layout

```
FluxLoop
└─ Inputs
   ├─ Configuration
   │   ├─ Open Configuration (configs/input.yaml)
   │   └─ Base Input
   │       └─ "How do I create an account?"
   ├─ Generate New Inputs…
   └─ Generated Inputs (inputs/generated.yaml)
       └─ rephrase • persona=novice_user • 2025-01-17
```

### Configuration

The **Configuration** folder provides quick access to input settings:

- **Open Configuration**: Opens `configs/input.yaml` for editing
- **Base Input**: Shows the primary seed input used for generation
  - Displays the first entry from `base_inputs[0]` in `configs/input.yaml`
  - Click to open the configuration file directly

### Base Input

The base input is the seed that drives input generation:
- Only the primary (first) base input is displayed in the tree
- This input is used as the foundation for all variation strategies
- Edit `configs/input.yaml` to modify or add more base inputs

### Generated Inputs
- Populated after running **Generate New Inputs…**
- Each node displays the strategy, persona, and timestamp
- Clicking a node opens `inputs/generated.yaml` at the corresponding entry
- Use **Refresh** icon to reload after editing the file manually

## Generate New Inputs

Use the **Generate New Inputs…** button in the tree (or `FluxLoop: Generate Inputs` command). The wizard collects:

1. **Generation Mode** (Deterministic / LLM)
2. **Base Input Confirmation** – Review the primary base input; edit configuration if needed
3. **Variation Strategies** – Select strategies (pre-checked based on `configs/input.yaml`)
   - Selected strategies are saved back to `variation_strategies` in `configs/input.yaml`
4. **Variation Limit** per base input
5. **Output Path** (defaults to `inputs/generated.yaml`)
6. **Overwrite/Append** + dry-run options
7. **LLM Provider, Model, API Key** (securely stored if you allow it)

Generated entries appear instantly under **Generated Inputs**.

## Context Menu Actions

Right-click on items to access common actions:

| Item | Actions |
|------|---------|
| Configuration | Open configuration |
| Base input | Open configuration / Copy content |
| Generated input | Open generated file / Remove entry |
| Tree header | Generate inputs / Refresh tree |

## Related Commands
- `FluxLoop: Generate Inputs`
- `FluxLoop: Open Input Configuration`

## See Also
- [Managing Inputs](../user-guide/managing-inputs.md)
- [Recording Mode](../user-guide/recording-mode.md)
