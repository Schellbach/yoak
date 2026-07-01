"""Supported cloud and local model catalog (LiteLLM model strings)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class CloudProvider:
    id: str
    label: str
    env_var: str
    default_model: str
    models: tuple[str, ...]


# Order matters for auto-detect: first matching env var wins.
CLOUD_PROVIDERS: tuple[CloudProvider, ...] = (
    CloudProvider(
        "anthropic",
        "Anthropic (Claude)",
        "ANTHROPIC_API_KEY",
        "anthropic/claude-sonnet-4-20250514",
        (
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-opus-4-20250514",
            "anthropic/claude-3-5-haiku-20241022",
        ),
    ),
    CloudProvider(
        "openai",
        "OpenAI (GPT)",
        "OPENAI_API_KEY",
        "gpt-4o",
        ("gpt-4o", "gpt-4o-mini", "o1-preview", "o3-mini"),
    ),
    CloudProvider(
        "deepseek",
        "DeepSeek",
        "DEEPSEEK_API_KEY",
        "deepseek/deepseek-chat",
        ("deepseek/deepseek-chat", "deepseek/deepseek-reasoner"),
    ),
    CloudProvider(
        "google",
        "Google (Gemini)",
        "GEMINI_API_KEY",
        "gemini/gemini-2.5-pro",
        ("gemini/gemini-2.5-pro", "gemini/gemini-2.5-flash", "gemini/gemini-2.0-flash"),
    ),
    CloudProvider(
        "zhipuai",
        "Zhipu (GLM)",
        "ZHIPUAI_API_KEY",
        "zhipuai/glm-4-flash",
        ("zhipuai/glm-4-flash", "zhipuai/glm-4-plus", "zhipuai/glm-4-air", "zhipuai/glm-4-long"),
    ),
    CloudProvider(
        "mistral",
        "Mistral",
        "MISTRAL_API_KEY",
        "mistral/mistral-large-latest",
        ("mistral/mistral-large-latest", "mistral/mistral-small-latest", "mistral/open-mistral-nemo"),
    ),
)

OLLAMA_SUGGESTED_MODELS: tuple[str, ...] = (
    "llama3.1",
    "llama3.2",
    "deepseek-r1",
    "qwen2.5",
    "glm4",
    "mistral",
    "codellama",
)

# LiteLLM provider prefix -> API key env var (includes aliases).
PROVIDER_ENV_VARS: dict[str, str] = {}
for _p in CLOUD_PROVIDERS:
    PROVIDER_ENV_VARS[_p.id] = _p.env_var
PROVIDER_ENV_VARS["gemini"] = "GEMINI_API_KEY"


def provider_env_var(model: str) -> str | None:
    """Return the env var name required for a LiteLLM model string, if known."""
    prefix = model.split("/")[0] if "/" in model else model
    return PROVIDER_ENV_VARS.get(prefix)


def detect_api_key_in_env() -> tuple[str, str, str] | None:
    """First cloud provider with a key set. Returns (default_model, label, env_var)."""
    for provider in CLOUD_PROVIDERS:
        if os.environ.get(provider.env_var):
            return provider.default_model, provider.label, provider.env_var
    return None


def list_model_options() -> dict:
    """JSON-serializable catalog for API and dashboard."""
    return {
        "cloud_providers": [
            {
                "provider": p.id,
                "label": p.label,
                "env_var": p.env_var,
                "default_model": p.default_model,
                "models": list(p.models),
            }
            for p in CLOUD_PROVIDERS
        ],
        "local": {
            "provider": "ollama",
            "models": list(OLLAMA_SUGGESTED_MODELS),
        },
    }


def all_cloud_model_strings() -> list[str]:
    models: list[str] = []
    for p in CLOUD_PROVIDERS:
        models.extend(p.models)
    return models
