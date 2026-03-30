"""Unified model provider abstraction over LiteLLM (cloud) and Ollama (local)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import AsyncIterator

import litellm

from yoak.core.config import Settings

litellm.drop_params = True


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class Chunk:
    """A single streaming chunk from the model."""

    delta: str
    finish_reason: str | None = None


@dataclass
class CompletionResult:
    content: str
    model: str
    usage: dict = field(default_factory=dict)


def _resolve_model(settings: Settings) -> tuple[str, dict]:
    """Return (model_string, extra_kwargs) based on config."""
    if settings.ollama.enabled:
        return f"ollama/{settings.ollama.model}", {
            "api_base": settings.ollama.base_url,
        }
    extra: dict = {}
    if settings.model.api_base:
        extra["api_base"] = settings.model.api_base
    return settings.model.model, extra


async def complete(
    messages: list[Message],
    settings: Settings,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> CompletionResult:
    model, extra = _resolve_model(settings)
    resp = await litellm.acompletion(
        model=model,
        messages=[{"role": m.role, "content": m.content} for m in messages],
        temperature=temperature or settings.model.temperature,
        max_tokens=max_tokens or settings.model.max_tokens,
        **extra,
    )
    choice = resp.choices[0]
    return CompletionResult(
        content=choice.message.content,
        model=resp.model or model,
        usage=dict(resp.usage) if resp.usage else {},
    )


async def stream(
    messages: list[Message],
    settings: Settings,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> AsyncIterator[Chunk]:
    model, extra = _resolve_model(settings)
    resp = await litellm.acompletion(
        model=model,
        messages=[{"role": m.role, "content": m.content} for m in messages],
        temperature=temperature or settings.model.temperature,
        max_tokens=max_tokens or settings.model.max_tokens,
        stream=True,
        **extra,
    )
    async for part in resp:
        delta = part.choices[0].delta
        content = delta.content or ""
        finish = part.choices[0].finish_reason
        if content or finish:
            yield Chunk(delta=content, finish_reason=finish)
