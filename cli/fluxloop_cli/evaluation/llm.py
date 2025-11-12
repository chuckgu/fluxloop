"""
LLM-backed evaluators with sampling, caching, and rate limits.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console

from .config import EvaluationConfig, EvaluatorConfig

console = Console()


class SafeFormatDict(dict):
    """Format helper that ignores missing keys."""

    def __missing__(self, key: str) -> str:  # pragma: no cover - formatting fallback
        return "{" + key + "}"


def _deterministic_sample(trace_id: Optional[str], sample_rate: float) -> bool:
    if sample_rate >= 1.0:
        return True
    identifier = trace_id or ""
    seed = int(hashlib.sha256(identifier.encode("utf-8")).hexdigest(), 16)
    rng = random.Random(seed)
    return rng.random() < sample_rate


def _parse_first_number_1_10(text: str) -> Tuple[Optional[float], Optional[str]]:
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None, "No numeric score found in response"
    value = float(match.group(1))
    if not 0 <= value <= 10:
        return None, f"Score {value} outside expected range 0-10"
    reason_match = re.search(r"reason[:\-]\s*(.*)", text, re.IGNORECASE)
    reason = reason_match.group(1).strip() if reason_match else text.strip()
    return value, reason


def _normalize_score(raw_score: float, max_score: float) -> float:
    if max_score <= 0:
        max_score = 1.0
    normalized = raw_score / max_score
    return max(0.0, min(1.0, normalized))


@dataclass
class LLMResult:
    score: float
    reasons: List[str]
    metadata: Dict[str, Any]


@dataclass
class LLMEvaluationManager:
    config: EvaluationConfig
    output_dir: Path
    api_key: Optional[str]
    sample_rate: float
    max_calls: Optional[int]
    cache_path: Optional[Path]

    def __post_init__(self) -> None:
        self.calls_made = 0
        self._client = None
        self._client_error: Optional[str] = None
        self.cache: Dict[str, Dict[str, Any]] = {}
        if self.cache_path:
            try:
                if self.cache_path.exists():
                    for line in self.cache_path.read_text(encoding="utf-8").splitlines():
                        if not line.strip():
                            continue
                        record = json.loads(line)
                        self.cache[record["key"]] = record
            except Exception as exc:  # noqa: BLE001
                console.print(f"[yellow]Warning:[/yellow] Failed to load LLM cache: {exc}")
        if self.api_key:
            self._resolve_client()

    def _resolve_client(self) -> None:
        try:
            from openai import OpenAI  # type: ignore
        except ImportError:  # pragma: no cover - optional dependency
            self._client_error = (
                "openai package not installed. Install with `pip install fluxloop-cli[openai]`."
            )
            console.print(f"[yellow]Warning:[/yellow] {self._client_error}")
            return

        try:
            self._client = OpenAI(api_key=self.api_key)
        except Exception as exc:  # pragma: no cover - network/environment errors
            self._client_error = f"Failed to initialize OpenAI client: {exc}"
            console.print(f"[yellow]Warning:[/yellow] {self._client_error}")

    @classmethod
    def create(
        cls,
        options_api_key: Optional[str],
        options_sample_rate: Optional[float],
        options_max_calls: Optional[int],
        config: EvaluationConfig,
        output_dir: Path,
    ) -> "LLMEvaluationManager":
        sample_rate = options_sample_rate if options_sample_rate is not None else config.limits.sample_rate
        sample_rate = max(0.0, min(1.0, sample_rate))

        max_calls = options_max_calls if options_max_calls is not None else config.limits.max_llm_calls
        cache_setting = config.limits.cache
        cache_path = None
        if cache_setting:
            cache_path = Path(cache_setting)
            if not cache_path.is_absolute():
                cache_path = output_dir / cache_setting
            cache_path.parent.mkdir(parents=True, exist_ok=True)

        api_key = (
            options_api_key
            or os.getenv("FLUXLOOP_LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

        return cls(
            config=config,
            output_dir=output_dir,
            api_key=api_key,
            sample_rate=sample_rate,
            max_calls=max_calls,
            cache_path=cache_path,
        )

    def _cache_key(self, evaluator: EvaluatorConfig, prompt: str, trace: Dict[str, Any]) -> str:
        payload = json.dumps(
            {
                "evaluator": evaluator.name,
                "model": evaluator.model,
                "prompt": prompt,
                "trace_id": trace.get("trace_id"),
                "iteration": trace.get("iteration"),
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _load_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        return self.cache.get(key)

    def _save_to_cache(self, key: str, record: Dict[str, Any]) -> None:
        if key in self.cache:
            return
        self.cache[key] = record
        if self.cache_path:
            with self.cache_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _prepare_prompt(self, evaluator: EvaluatorConfig, trace: Dict[str, Any]) -> str:
        template = evaluator.prompt_template or ""
        context = SafeFormatDict(
            {
                "input": trace.get("input") or "",
                "output": trace.get("output") or "",
                "persona": trace.get("persona") or "",
                "iteration": trace.get("iteration"),
                "trace_id": trace.get("trace_id") or "",
            }
        )
        return template.format_map(context)

    def _invoke_model(self, evaluator: EvaluatorConfig, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        if not self._client:
            return None, self._client_error or "LLM client unavailable"

        if self.max_calls is not None and self.calls_made >= self.max_calls:
            return None, "LLM evaluation budget exhausted"

        try:
            response = self._client.responses.create(  # type: ignore[attr-defined]
                model=evaluator.model,
                input=prompt,
                max_output_tokens=512,
            )
            self.calls_made += 1
            output = response.output_text  # type: ignore[attr-defined]
            return str(output), None
        except AttributeError:
            # Fallback for older openai versions
            try:
                completion = self._client.chat.completions.create(  # type: ignore[attr-defined]
                    model=evaluator.model,
                    messages=[
                        {"role": "system", "content": "You are an expert evaluator."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=512,
                )
                self.calls_made += 1
                text = completion.choices[0].message.content  # type: ignore[index]
                return text, None
            except Exception as exc:  # noqa: BLE001
                return None, f"LLM call failed: {exc}"
        except Exception as exc:  # noqa: BLE001
            return None, f"LLM call failed: {exc}"

    def evaluate(self, trace: Dict[str, Any], evaluator: EvaluatorConfig) -> LLMResult:
        if not evaluator.model:
            return LLMResult(
                score=0.0,
                reasons=["LLM evaluator missing model configuration"],
                metadata={"type": "llm"},
            )

        if not evaluator.prompt_template:
            return LLMResult(
                score=0.0,
                reasons=["LLM evaluator missing prompt_template"],
                metadata={"type": "llm"},
            )

        sample_key = trace.get("trace_id") or f"{trace.get('iteration')}:{trace.get('persona')}:{trace.get('input')}"

        if not _deterministic_sample(sample_key, self.sample_rate):
            return LLMResult(
                score=0.0,
                reasons=["Skipped due to LLM sampling"],
                metadata={"type": "llm", "sampled": False},
            )

        prompt = self._prepare_prompt(evaluator, trace)
        cache_key = self._cache_key(evaluator, prompt, trace)
        cached = self._load_from_cache(cache_key)
        if cached:
            raw_score = cached.get("raw_score")
            reason_text = cached.get("reason")
            normalized = _normalize_score(float(raw_score), float(evaluator.max_score or 10))
            return LLMResult(
                score=normalized,
                reasons=[reason_text] if reason_text else [],
                metadata={
                    "type": "llm",
                    "cached": True,
                    "raw_score": raw_score,
                    "response": cached.get("response"),
                },
            )

        if not self.api_key:
            return LLMResult(
                score=0.0,
                reasons=["LLM API key not provided. Set --llm-api-key or FLUXLOOP_LLM_API_KEY."],
                metadata={"type": "llm"},
            )

        response_text, error = self._invoke_model(evaluator, prompt)
        if error or not response_text:
            reason = error or "No response from LLM"
            return LLMResult(
                score=0.0,
                reasons=[reason],
                metadata={"type": "llm"},
            )

        parser = evaluator.parser or "first_number_1_10"
        max_score = float(evaluator.max_score or 10)

        if parser == "first_number_1_10":
            raw_score, reason_text = _parse_first_number_1_10(response_text)
        else:
            raw_score, reason_text = None, f"Unknown parser '{parser}'"

        if raw_score is None:
            return LLMResult(
                score=0.0,
                reasons=[reason_text or "Failed to parse LLM response"],
                metadata={"type": "llm", "response": response_text},
            )

        normalized = _normalize_score(raw_score, max_score)
        record = {
            "key": cache_key,
            "raw_score": raw_score,
            "reason": reason_text,
            "response": response_text,
        }
        self._save_to_cache(cache_key, record)

        reasons = [reason_text] if reason_text else []

        return LLMResult(
            score=normalized,
            reasons=reasons,
            metadata={
                "type": "llm",
                "raw_score": raw_score,
                "max_score": max_score,
                "response": response_text,
            },
        )

