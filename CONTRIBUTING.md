# Contributing to FluxLoop

Thank you for your interest in contributing! This guide explains how to propose changes and get them merged.

## Code of Conduct

Be respectful and constructive. We follow common-sense community guidelines. Harassment or discrimination is not tolerated.

## Ways to Contribute

- Report bugs and request features via [GitHub Issues](https://github.com/chuckgu/fluxloop/issues)
- Improve docs and examples
- Implement enhancements in SDK, CLI, or Collector
- Build integrations with popular frameworks

## Development Setup

1. Fork the repo and clone your fork
2. Create a virtual environment
3. Install packages in editable mode

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e packages/sdk -e packages/cli
```

## Branching and Commits

- Create a feature branch from `main` (e.g., `feat/short-title` or `fix/short-title`)
- Write clear, descriptive commit messages
- Keep changes focused and small when possible

## Testing & Linting

Run tests locally before opening a PR.

```bash
pytest -q
```

Fix lint errors if any are reported in CI.

## Pull Request Checklist

- The PR title clearly states intent
- Linked issue (if applicable)
- Includes tests or rationale for missing tests
- Updates docs if behavior changes

## Release Notes

If your change is user-facing, add a brief note to the appropriate release documentation or include it in the PR description.

## Questions?

Open an [issue](https://github.com/chuckgu/fluxloop/issues) and we’ll help.
