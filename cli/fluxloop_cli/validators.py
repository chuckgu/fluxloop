"""Helper validators for CLI inputs."""

from __future__ import annotations

from typing import Iterable, List

import typer

from fluxloop.schemas import VariationStrategy


def parse_variation_strategies(values: Iterable[str]) -> List[VariationStrategy]:
    """Parse CLI-provided variation strategy names."""

    strategies: List[VariationStrategy] = []
    for value in values:
        normalized = value.strip().lower().replace("-", "_")
        if not normalized:
            continue

        try:
            strategies.append(VariationStrategy(normalized))
        except ValueError as exc:  # pragma: no cover - exercised via Typer
            allowed = ", ".join(strategy.value for strategy in VariationStrategy)
            raise typer.BadParameter(
                f"Unknown strategy '{value}'. Allowed values: {allowed}"
            ) from exc

    return strategies


