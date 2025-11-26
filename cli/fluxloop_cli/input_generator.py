"""Utilities for generating input datasets."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

import yaml

from fluxloop.schemas import (
    ExperimentConfig,
    InputGenerationMode,
    VariationStrategy,
)

from .llm_generator import (
    DEFAULT_STRATEGIES,
    DEFAULT_USER_PROMPT_TEMPLATE,
    LLMGenerationError,
    generate_llm_inputs,
)

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
        timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        provider = self.metadata.get("llm_provider") or "unknown"
        model = self.metadata.get("llm_model") or "unknown"
        model_label = (
            f"{provider}/{model}"
            if provider not in ("", "unknown") and model not in ("", "unknown")
            else model if model not in ("", "unknown") else provider or "unknown"
        )

        strategies = self.metadata.get("strategies") or []
        stats = {
            "total_generated": len(self.entries),
            "base_inputs": self.metadata.get("total_base_inputs", 0),
            "personas": self.metadata.get("total_personas", 0),
            "strategies": len(strategies),
        }

        persona_summary: Dict[str, List[str]] = {}
        for entry in self.entries:
            persona_key = entry.metadata.get("persona") or "generic_user"
            if persona_key not in persona_summary:
                persona_summary[persona_key] = []

            strategy = entry.metadata.get("strategy")
            prefix = f"[{strategy}] " if strategy else ""
            persona_summary[persona_key].append(f"{prefix}{entry.input}")

        preferred_meta_order = [
            "strategy",
            "base_index",
            "persona",
            "persona_description",
            "prompt_hash",
        ]
        excluded_meta_keys = {"prompt", "model", "provider"}

        full_data: List[Dict[str, Any]] = []
        for entry in self.entries:
            row: Dict[str, Any] = {}
            row["input"] = entry.input
            metadata = entry.metadata or {}

            for key in preferred_meta_order:
                value = metadata.get(key)
                if value is not None:
                    row[key] = value

            for key, value in metadata.items():
                if key in preferred_meta_order or key in excluded_meta_keys:
                    continue
                if value is None:
                    continue
                row[key] = value

            full_data.append(row)

        generation_config = {
            "config_name": self.metadata.get("config_name"),
            "generation_mode": self.metadata.get("generation_mode"),
            "provider": provider,
            "model": model,
            "strategies": strategies,
            "limit": self.metadata.get("limit"),
            "prompt": self.metadata.get("llm_prompt_template"),
        }
        generation_config = {
            key: value for key, value in generation_config.items() if value is not None
        }

        lines: List[str] = [
            "# ===================================================================",
            f"# Generated User Inputs: {timestamp}",
            f"# Model: {model_label}",
            "# ===================================================================",
            "",
            yaml.safe_dump(
                {"stats": stats},
                sort_keys=False,
                allow_unicode=True,
            ).strip(),
            "",
        ]

        for persona_key, summary_items in persona_summary.items():
            header_label = persona_key.replace("_", " ").upper()
            lines.extend(
                [
                    "# -------------------------------------------------------------------",
                    f"# {header_label} ({len(summary_items)} inputs)",
                    "# -------------------------------------------------------------------",
                    "",
                    yaml.safe_dump(
                        {persona_key: summary_items},
                        sort_keys=False,
                        allow_unicode=True,
                    ).strip(),
                    "",
                ]
            )

        lines.extend(
            [
                "# ===================================================================",
                "# FULL DATA",
                "# ===================================================================",
                "",
                yaml.safe_dump(
                    {"inputs": full_data},
                    sort_keys=False,
                    allow_unicode=True,
                ).strip(),
                "",
                "# -------------------------------------------------------------------",
                "# COMMON METADATA (applies to all inputs above)",
                "# -------------------------------------------------------------------",
                "",
                yaml.safe_dump(
                    {"generation_config": generation_config},
                    sort_keys=False,
                    allow_unicode=True,
                ).strip(),
                "",
            ]
        )

        content = "\n".join(lines).rstrip()
        return content + "\n"

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
    base_inputs = config.base_inputs

    if not base_inputs:
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
            "total_base_inputs": len(base_inputs),
            "total_personas": len(config.personas or []),
            "strategies": [strategy.value for strategy in strategies],
            "limit": settings.limit,
            "generation_mode": InputGenerationMode.LLM.value,
            "llm_provider": config.input_generation.llm.provider,
            "llm_model": config.input_generation.llm.model,
            "llm_prompt_template": (
                config.input_generation.llm.user_prompt_template
                or DEFAULT_USER_PROMPT_TEMPLATE
            ),
        }

        return GenerationResult(entries=entries, metadata=metadata)

    raise GenerationError(
        "Only LLM-based generation is supported. Set input_generation.mode to 'llm'"
    )
