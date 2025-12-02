# FluxLoop Playground Simulation Guide

Follow this checklist before running **Prepare Simulation → Run Experiment** in the VS Code Playground. Each item links directly to the relevant section of the FluxLoop CLI / SDK docs.

---

## 1. Environment Prep
- Create a Python 3.11+ virtual environment and install `fluxloop`, `fluxloop-cli`, and `fluxloop-mcp` inside it. ([SDK ▸ Installation](https://docs.fluxloop.io/sdk/getting-started/installation))
- Ensure the same venv is active for the VS Code terminal, Playground, and CLI. Run `fluxloop doctor` (or System Console **Run Doctor**) until Python/CLI/SDK/MCP/Index all show ✅. ([CLI ▸ Basic Workflow](https://docs.fluxloop.io/cli/workflows/basic-workflow))

## 2. Runner & Decorators
- Verify the `runner` section in `configs/simulation.yaml` points to your actual entry point. Pattern-specific instructions live in [Runner Targets](https://docs.fluxloop.io/cli/configuration/runner-targets).
- Any Python function/class runner must be wrapped with the SDK decorators described in [SDK ▸ Decorators](https://docs.fluxloop.io/sdk/api/decorators). Make sure the module lives inside your `project.source_root` so VS Code can resolve it automatically.

## 3. Advanced Simulation Options
- If you use multi-turn conversations, double-check `multi_turn.enabled`, `max_turns`, and the `supervisor.*` fields. ([CLI ▸ Multi-Turn Workflow](https://docs.fluxloop.io/cli/workflows/multi-turn-workflow))
- To replay recorded traffic, run `fluxloop record enable`, capture JSONL files, and point `replay_args.recording_file` to the file. ([CLI ▸ Recording Workflow](https://docs.fluxloop.io/cli/workflows/recording-workflow))

## 4. Inputs & Experiments
- Keep `configs/input.yaml` up to date and run `fluxloop generate inputs` so `inputs/generated.yaml` is available.
- Clean up the `experiments/` folder occasionally so the Playground can surface recent runs quickly.

## 5. Prepare Simulation Tips
1. Always click **Prepare Simulation** first. The command automatically passes your `targetSourceRoot` to Flux Agent, so the default option usually requires only hitting Enter.
2. If you need to highlight different folders/files, choose them manually from the QuickPick dialog.
3. Seeing “Flux Agent cancelled by user” means no context was selected. Re-run the command and either pick folders or check the System Console (**Show Install Guide / Run Doctor**) to validate the environment.

## 6. Run Experiment & Evaluate
- Once preparation succeeds, run **Run Experiment**. If you rely on multi-turn, replay, or HTTP runners, double-check `configs/simulation.yaml` and `project.source_root` first.
- After the run completes, follow the standard CLI flow (`fluxloop parse`, `fluxloop evaluate`) to produce `evaluation_report/report.html`. ([CLI ▸ First Experiment](https://docs.fluxloop.io/cli/getting-started/first-experiment))

---

**Additional References**
- CLI docs: <https://docs.fluxloop.io/cli>
- SDK docs: <https://docs.fluxloop.io/sdk>
- VS Code System Console: **Show Install Guide · Select Environment · Run Doctor**