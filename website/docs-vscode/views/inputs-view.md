---
sidebar_position: 2
---

# Inputs View

The **Inputs** view lets you design experiment scenarios without leaving VS Code. It surfaces base inputs, generated variations, and recordings in a single tree.

## Layout

```
FluxLoop
└─ Inputs
   ├─ Base Inputs (configs/input.yaml)
   │   ├─ persona: novice_user
   │   └─ input: "How do I create an account?"
   ├─ Generated Inputs (inputs/generated.yaml)
   │   └─ rephrase • persona=novice_user • 2025-01-17
   └─ Recordings (recordings/*.jsonl)
       └─ args_recording.jsonl
```

### Base Inputs
- Mirrors the structure of `configs/input.yaml`
- Entries show persona name + snippet of the prompt
- Double-click opens `configs/input.yaml` and jumps to the entry
- Use the hover action **Edit configuration** to open the file in one click

### Generated Inputs
- Populated after running **Generate New Inputs…**
- Each node displays the strategy, persona, and timestamp
- Clicking a node opens `inputs/generated.yaml` at the corresponding entry
- Use **Refresh** icon to reload after editing the file manually

### Recordings
- Lists `.jsonl` files under `recordings/`
- Shows recording size and last modified time
- Clicking opens the JSONL file for inspection

## Generate New Inputs

Use the **Generate New Inputs…** button in the tree header (or `FluxLoop: Generate Inputs` command). The wizard collects:
- Generation mode (Deterministic / LLM)
- Variation strategies (rephrase, verbose, concise, error_prone, persona_mix, multilingual, etc.)
- Variation limit per base input
- Output path (defaults to `inputs/generated.yaml`)
- Overwrite/append + dry-run options
- LLM provider, model, API key (securely stored if you allow it)

Generated entries appear instantly under **Generated Inputs**.

## Context Menu Actions

Right-click on items to access common actions:

| Item | Actions |
|------|---------|
| Base input | Open configuration / Copy ID |
| Generated input | Open generated file / Remove entry |
| Recordings | Open file / Reveal in Explorer |
| Tree header | Generate inputs / Refresh tree |

## When to Use Recordings

Recording nodes remind you when argument capture is enabled. Use them to:
- Verify that new calls are being appended to `args_recording.jsonl`
- Manually inspect captured arguments before replay
- Delete outdated recordings (context menu → Delete)

## Related Commands
- `FluxLoop: Generate Inputs`
- `FluxLoop: Enable Recording Mode`
- `FluxLoop: Disable Recording Mode`
- `FluxLoop: Show Recording Status`

## See Also
- [Managing Inputs](../user-guide/managing-inputs.md)
- [Recording Mode](../user-guide/recording-mode.md)
