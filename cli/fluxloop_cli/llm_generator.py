"""LLM-backed input generation utilities."""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple

import httpx

from fluxloop.schemas import (
    ExperimentConfig,
    InputGenerationMode,
    LLMGeneratorConfig,
    PersonaConfig,
    VariationStrategy,
)

logger = logging.getLogger(__name__)


DEFAULT_STRATEGIES: Sequence[VariationStrategy] = (
    VariationStrategy.REPHRASE,
    VariationStrategy.VERBOSE,
    VariationStrategy.CONCISE,
)


class LLMGenerationError(RuntimeError):
    """Raised when LLM-backed generation fails."""


@dataclass
class LLMGenerationContext:
    """Context data passed into prompt templates."""

    base_input: Dict[str, Any]
    persona: Optional[PersonaConfig]
    strategy: VariationStrategy
    iteration: int


class LLMClient(Protocol):
    """Protocol describing asynchronous LLM client implementations."""

    async def generate(
        self,
        *,
        prompts: Sequence[Tuple[str, Dict[str, Any]]],
        config: ExperimentConfig,
        llm_config: LLMGeneratorConfig,
    ) -> List[Dict[str, Any]]:
        ...


def _ensure_llm_mode(config: ExperimentConfig) -> LLMGeneratorConfig:
    generation = config.input_generation
    if generation.mode != InputGenerationMode.LLM:
        raise LLMGenerationError(
            "LLM input generation requested but configuration mode is not set to 'llm'"
        )
    if not generation.llm.enabled:
        raise LLMGenerationError("LLM input generation is disabled in configuration")
    return generation.llm


def _hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


async def _request_openai(
    client: httpx.AsyncClient,
    *,
    config: LLMGeneratorConfig,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    endpoint = "https://api.openai.com/v1/responses"
    headers = {}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    try:
        response = await client.post(
            endpoint,
            headers=headers,
            timeout=config.request_timeout,
            json=payload,
        )
    except httpx.HTTPError as exc:
        raise LLMGenerationError(f"OpenAI request failed: {exc}") from exc

    if response.status_code >= 400:
        raise LLMGenerationError(
            f"OpenAI API error {response.status_code}: {response.text}"
        )

    return response.json()


async def _generate_variations_openai(
    *,
    client: httpx.AsyncClient,
    config: ExperimentConfig,
    llm_config: LLMGeneratorConfig,
    prompts: Sequence[Tuple[str, Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for prompt_text, metadata in prompts:
        payload = {
            "model": llm_config.model,
            "input": prompt_text,
            "temperature": llm_config.temperature,
            "top_p": llm_config.top_p,
            "frequency_penalty": llm_config.frequency_penalty,
            "presence_penalty": llm_config.presence_penalty,
            "max_output_tokens": llm_config.max_tokens,
        }

        if llm_config.system_prompt:
            payload["modalities"] = ["text"]
            payload["metadata"] = {"system_prompt": llm_config.system_prompt}

        response = await _request_openai(client, config=llm_config, payload=payload)

        text = None
        if "output" in response and isinstance(response["output"], list):
            candidates = response["output"]
            if candidates:
                text = candidates[0].get("content") or candidates[0].get("text")
        if not text and "choices" in response:
            choices = response["choices"]
            if choices:
                message = choices[0].get("message") or {}
                text = message.get("content")

        if not text:
            raise LLMGenerationError("OpenAI response did not contain content")

        results.append(
            {
                "input": text.strip(),
                "metadata": {
                    **metadata,
                    "model": llm_config.model,
                    "provider": llm_config.provider,
                    "prompt_hash": _hash_prompt(prompt_text),
                    "prompt": prompt_text,
                },
            }
        )

    return results


async def _generate_variations_mock(
    *,
    config: ExperimentConfig,
    llm_config: LLMGeneratorConfig,
    prompts: Sequence[Tuple[str, Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for prompt_text, metadata in prompts:
        persona = metadata.get("persona") or "generic"
        strategy = metadata.get("strategy", "unspecified")
        base_index = metadata.get("base_index")
        generated = f"[mock:{strategy}] persona={persona} base={base_index}"
        results.append(
            {
                "input": generated,
                "metadata": {
                    **metadata,
                    "model": llm_config.model,
                    "provider": "mock",
                    "prompt_hash": _hash_prompt(prompt_text),
                    "prompt": prompt_text,
                    "mock": True,
                },
            }
        )

    return results


def _format_prompt(
    config: ExperimentConfig,
    llm_config: LLMGeneratorConfig,
    context: LLMGenerationContext,
) -> Tuple[str, Dict[str, Any]]:
    template = llm_config.user_prompt_template or (
        "Generate a user input variation given the base input and persona.\n"
        "Base Input: {input}\n"
        "Strategy: {strategy}\n"
        "Persona: {persona}\n"
        "Provide a single realistic user message variant."
    )

    optional_persona = (
        context.persona.to_prompt() if context.persona else "Generic user"
    )
    strategy_prompt = llm_config.strategy_prompts.get(
        context.strategy.value,
        context.strategy.value,
    )

    prompt_text = template.format(
        input=context.base_input.get("input", ""),
        persona=optional_persona,
        strategy=strategy_prompt,
        metadata=json.dumps(context.base_input, ensure_ascii=False),
    )

    metadata = {
        "strategy": context.strategy.value,
        "base_index": context.iteration,
        "persona": context.persona.name if context.persona else None,
        "persona_description": context.persona.description if context.persona else None,
    }

    return prompt_text, metadata


async def _generate_with_client(
    *,
    config: ExperimentConfig,
    llm_config: LLMGeneratorConfig,
    prompts: Sequence[Tuple[str, Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    if llm_config.provider == "mock":
        return await _generate_variations_mock(
            config=config,
            llm_config=llm_config,
            prompts=prompts,
        )

    if llm_config.provider == "openai":
        async with httpx.AsyncClient() as client:
            return await _generate_variations_openai(
                client=client,
                config=config,
                llm_config=llm_config,
                prompts=prompts,
            )

    raise LLMGenerationError(f"Unsupported LLM provider: {llm_config.provider}")


def _collect_prompts(
    *,
    config: ExperimentConfig,
    strategies: Sequence[VariationStrategy],
    limit: Optional[int],
) -> List[Tuple[str, Dict[str, Any]]]:
    llm_config = _ensure_llm_mode(config)
    prompts: List[Tuple[str, Dict[str, Any]]] = []

    personas: Iterable[Optional[PersonaConfig]] = config.personas or [None]

    for index, base_input in enumerate(config.base_inputs):
        if not base_input.get("input"):
            continue
        for persona in personas:
            for strategy in strategies:
                context = LLMGenerationContext(
                    base_input=base_input,
                    persona=persona,
                    strategy=strategy,
                    iteration=index,
                )
                prompts.append(_format_prompt(config, llm_config, context))

                if limit is not None and len(prompts) >= limit:
                    return prompts

    return prompts


def generate_llm_inputs(
    *,
    config: ExperimentConfig,
    strategies: Sequence[VariationStrategy],
    settings,
) -> List[Dict[str, Any]]:
    """Generate inputs using an LLM provider."""

    llm_config = _ensure_llm_mode(config)

    if settings.llm_api_key_override:
        llm_config = llm_config.model_copy(update={"api_key": settings.llm_api_key_override})

    prompts = _collect_prompts(
        config=config,
        strategies=strategies,
        limit=settings.limit,
    )

    if not prompts:
        raise LLMGenerationError("No prompts generated from base inputs")

    async def _run_generation() -> List[Dict[str, Any]]:
        if settings.llm_client:
            result = settings.llm_client.generate(
                prompts=prompts,
                config=config,
                llm_config=llm_config,
            )
            if inspect.isawaitable(result):
                return await result
            return result

        return await _generate_with_client(
            config=config,
            llm_config=llm_config,
            prompts=prompts,
        )

    try:
        results = asyncio.run(_run_generation())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            raise LLMGenerationError(
                "LLM generation cannot run inside an active asyncio event loop"
            )
        results = loop.run_until_complete(_run_generation())

    return results


