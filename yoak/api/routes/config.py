"""Configuration management endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from yoak.core.config import load_settings, update_setting

router = APIRouter()


class SettingUpdate(BaseModel):
    key: str
    value: str | int | float | bool


@router.get("/config")
async def get_config():
    settings = load_settings()
    data = settings.model_dump(mode="json")
    return {"config": data}


@router.put("/config")
async def set_config(body: SettingUpdate):
    settings = update_setting(body.key, body.value)
    return {"status": "ok", "config": settings.model_dump(mode="json")}


@router.get("/config/models")
async def list_model_options():
    return {
        "cloud_providers": [
            {
                "provider": "anthropic",
                "models": ["anthropic/claude-sonnet-4-20250514", "anthropic/claude-opus-4-20250514"],
            },
            {"provider": "openai", "models": ["gpt-4o", "gpt-4o-mini", "o1-preview"]},
            {"provider": "google", "models": ["gemini/gemini-2.5-pro", "gemini/gemini-2.5-flash"]},
        ],
        "local": {
            "provider": "ollama",
            "models": ["llama3.1", "llama3.1:70b", "mistral", "codellama"],
        },
    }
