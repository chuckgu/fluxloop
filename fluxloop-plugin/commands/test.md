# /fluxloop:test

Run the full FluxLoop test workflow (pull → run → upload)

## Run
```bash
fluxloop test
```

## Description
1. Pull criteria/inputs from Web
2. Run the test (turn recording)
3. Upload results to Web
4. Print summary + evaluation criteria

## Options
- `--skip-pull`: Skip pull
- `--skip-upload`: Skip upload
- `--smoke`: Smoke test only
- `--full`: Full test run
- `--quiet`: Minimal output (for hooks)
