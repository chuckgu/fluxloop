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
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)

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


async def _generate_one_variation_openai(
    client: httpx.AsyncClient,
    llm_config: LLMGeneratorConfig,
    prompt_text: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate a single input variation via OpenAI API."""
    messages: List[Dict[str, str]] = []
    if llm_config.system_prompt:
        messages.append({"role": "system", "content": llm_config.system_prompt})
    messages.append({"role": "user", "content": prompt_text})

    payload = {
        "model": llm_config.model,
        "messages": messages,
    }

    # Add GPT-5 specific controls if they exist on the config object
    # if hasattr(llm_config, "reasoning_effort") and llm_config.reasoning_effort:
    #     payload["reasoning"] = {"effort": llm_config.reasoning_effort}

    # if hasattr(llm_config, "text_verbosity") and llm_config.text_verbosity:
    #     payload["text"] = {"verbosity": llm_config.text_verbosity}

    response = await _request_openai(client, config=llm_config, payload=payload)

    text = None
    if "choices" in response:
        choices = response.get("choices", [])
        if choices:
            message = choices[0].get("message") or {}
            text = message.get("content")

    if text is None:
        error_details = json.dumps(response, indent=2)
        raise LLMGenerationError(
            f"OpenAI response did not contain content. Full response:\n{error_details}"
        )

    return {
        "input": text.strip(),
        "metadata": {
            **metadata,
            "model": llm_config.model,
            "provider": llm_config.provider,
            "prompt_hash": _hash_prompt(prompt_text),
            "prompt": prompt_text,
        },
    }


async def _request_openai(
    client: httpx.AsyncClient,
    *,
    config: LLMGeneratorConfig,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    endpoint = "https://api.openai.com/v1/chat/completions"
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
    progress: Progress,
    task_id: Any,
) -> List[Dict[str, Any]]:
    tasks = [
        _generate_one_variation_openai(client, llm_config, prompt_text, metadata)
        for prompt_text, metadata in prompts
    ]

    results: List[Dict[str, Any]] = []
    for future in asyncio.as_completed(tasks):
        try:
            result = await future
            results.append(result)
        except LLMGenerationError as exc:
            logger.warning(f"Failed to generate one variation: {exc}")
        except Exception as exc:
            logger.error(f"An unexpected error occurred during generation: {exc}")
        finally:
            progress.update(task_id, advance=1)

    return results


async def _generate_variations_mock(
    *,
    config: ExperimentConfig,
    llm_config: LLMGeneratorConfig,
    prompts: Sequence[Tuple[str, Dict[str, Any]]],
    progress: Progress,
    task_id: Any,
) -> List[Dict[str, Any]]:
    if llm_config.provider == "mock":
        results = await _generate_variations_mock(
            config=config,
            llm_config=llm_config,
            prompts=prompts,
        )
        progress.update(task_id, completed=len(prompts))
        return results

    if llm_config.provider == "openai":
        async with httpx.AsyncClient() as client:
            return await _generate_variations_openai(
                client=client,
                config=config,
                llm_config=llm_config,
                prompts=prompts,
                progress=progress,
                task_id=task_id,
            )

    raise LLMGenerationError(f"Unsupported LLM provider: {llm_config.provider}")


def _format_prompt(
    config: ExperimentConfig,
    llm_config: LLMGeneratorConfig,
    context: LLMGenerationContext,
) -> Tuple[str, Dict[str, Any]]:
    template = llm_config.user_prompt_template or (
        """You are an expert in creating high-quality datasets for testing AI agents.
Your task is to generate a single, realistic user message that a person would type into a support chat or search box. This message will be used as an input in an automated simulation to test an AI agent's performance.

**Instructions:**
1.  Read the Base Input, Strategy, and Persona details carefully.
2.  Generate a new user message that modifies the Base Input according to the given Strategy and reflects the Persona.
3.  **Keep the message concise and natural.** Even when the strategy is "verbose," it should still be a realistic user query, not a lengthy technical specification. A verbose user might ask multiple related questions in one message, but they would not write an essay.
4.  **Your output must ONLY be the generated user message text.** Do not include any prefixes, quotation marks, explanations, or formatting like bullet points. It should be a single block of text.

---
**Base Input:**
{input}

**Strategy to Apply (how the user words their request):**
{strategy}

**User Persona Profile:**
{persona}
---

Generated User Message:"""
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
    progress: Progress,
    task_id: Any,
) -> List[Dict[str, Any]]:
    if llm_config.provider == "mock":
        return await _generate_variations_mock(
            config=config,
            llm_config=llm_config,
            prompts=prompts,
            progress=progress,
            task_id=task_id,
        )

    if llm_config.provider == "openai":
        async with httpx.AsyncClient() as client:
            return await _generate_variations_openai(
                client=client,
                config=config,
                llm_config=llm_config,
                prompts=prompts,
                progress=progress,
                task_id=task_id,
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

    async def _run_generation(progress: Progress, task_id: Any) -> List[Dict[str, Any]]:
        if settings.llm_client:
            # Note: Custom clients do not support progress bars currently
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
            progress=progress,
            task_id=task_id,
        )

    console = Console()
    console.print(f"🧠 Generating [bold cyan]{len(prompts)}[/bold cyan] variations using LLM...")

    results: List[Dict[str, Any]] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TextColumn("({task.completed} of {task.total})"),
        console=console,
    ) as progress:
        generation_task = progress.add_task("[green]Generating...", total=len(prompts))
        try:
            results = asyncio.run(_run_generation(progress, generation_task))
        except RuntimeError:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                raise LLMGenerationError(
                    "LLM generation cannot run inside an active asyncio event loop"
                )

            results = loop.run_until_complete(_run_generation(progress, generation_task))

    if len(results) < len(prompts):
        console.print(
            f"[yellow]Warning:[/yellow] {len(prompts) - len(results)} variations failed to generate."
        )

    return results


