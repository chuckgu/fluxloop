"""Utilities for generating input datasets."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Sequence

import yaml

from fluxloop.schemas import (
    ExperimentConfig,
    InputGenerationMode,
    PersonaConfig,
    VariationStrategy,
)

from .llm_generator import DEFAULT_STRATEGIES, LLMGenerationError, generate_llm_inputs

if TYPE_CHECKING:
    from .llm_generator import LLMClient


@dataclass
class GenerationSettings:
    """Options controlling input generation."""

    limit: Optional[int] = None
    dry_run: bool = False
    mode: Optional[InputGenerationMode] = None
    strategies: Optional[Sequence[VariationStrategy]] = None
    use_cache: bool = True
    llm_api_key_override: Optional[str] = None
    llm_client: Optional["LLMClient"] = None


@dataclass
class GeneratedInput:
    """Represents a single generated input entry."""

    input: str
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Container for generation output."""

    entries: List[GeneratedInput]
    metadata: Dict[str, object]

    def to_yaml(self) -> str:
        payload = {
            "generated_at": dt.datetime.utcnow().isoformat() + "Z",
            "metadata": self.metadata,
            "inputs": [
                {
                    "input": entry.input,
                    "metadata": entry.metadata,
                }
                for entry in self.entries
            ],
        }
        return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)

    def to_json(self) -> str:
        return json.dumps(
            {
                "generated_at": dt.datetime.utcnow().isoformat() + "Z",
                "metadata": self.metadata,
                "inputs": [
                    {
                        "input": entry.input,
                        "metadata": entry.metadata,
                    }
                    for entry in self.entries
                ],
            },
            indent=2,
        )


class GenerationError(Exception):
    """Raised when input generation cannot proceed."""


def generate_inputs(
    config: ExperimentConfig,
    settings: GenerationSettings,
) -> GenerationResult:
    """Generate deterministic input entries based on configuration."""
    if not config.base_inputs:
        raise GenerationError("base_inputs must be defined to generate inputs")

    mode = settings.mode or config.input_generation.mode

    if mode == InputGenerationMode.LLM:
        strategies: Sequence[VariationStrategy]
        if settings.strategies and len(settings.strategies) > 0:
            strategies = list(settings.strategies)
        elif config.variation_strategies:
            strategies = config.variation_strategies
        else:
            strategies = DEFAULT_STRATEGIES

        try:
            raw_entries = generate_llm_inputs(
                config=config,
                strategies=strategies,
                settings=settings,
            )
        except LLMGenerationError as exc:
            raise GenerationError(str(exc)) from exc

        entries = [
            GeneratedInput(input=item["input"], metadata=item.get("metadata", {}))
            for item in raw_entries
        ]

        metadata = {
            "config_name": config.name,
            "total_base_inputs": len(config.base_inputs),
            "total_personas": len(config.personas),
            "strategies": [strategy.value for strategy in strategies],
            "limit": settings.limit,
            "generation_mode": InputGenerationMode.LLM.value,
            "llm_provider": config.input_generation.llm.provider,
            "llm_model": config.input_generation.llm.model,
        }

        return GenerationResult(entries=entries, metadata=metadata)

    entries: List[GeneratedInput] = []

    for base_index, base_input in enumerate(config.base_inputs):
        base_text = base_input.get("input")
        if not base_text:
            continue

        personas: Iterable[Optional[PersonaConfig]]
        if config.personas:
            personas = config.personas
        else:
            personas = [None]

        for persona_index, persona in enumerate(personas):
            metadata = {
                "source": "base_inputs",
                "base_index": base_index,
            }
            metadata.update({k: v for k, v in base_input.items() if k != "input"})

            if persona:
                metadata["persona"] = persona.name
                metadata["persona_description"] = persona.description

            entry_text = base_text
            entries.append(
                GeneratedInput(
                    input=entry_text,
                    metadata=metadata,
                )
            )

            if settings.limit is not None and len(entries) >= settings.limit:
                break

        if settings.limit is not None and len(entries) >= settings.limit:
            break

    metadata = {
        "config_name": config.name,
        "total_base_inputs": len(config.base_inputs),
        "total_personas": len(config.personas),
        "strategies": [strategy.value for strategy in config.variation_strategies],
        "limit": settings.limit,
        "generation_mode": InputGenerationMode.DETERMINISTIC.value,
    }

    return GenerationResult(entries=entries, metadata=metadata)
