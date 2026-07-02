"""Yoak configuration management."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

YOAK_DIR = Path(os.environ.get("YOAK_DIR", Path.home() / ".yoak"))
CONFIG_PATH = YOAK_DIR / "config.yaml"
DB_PATH = YOAK_DIR / "yoak.db"


class ModelConfig(BaseModel):
    provider: str = "ollama"
    model: str = "ollama/llama3.1"
    temperature: float = 0.7
    max_tokens: int = 4096
    api_base: str | None = None


class OllamaConfig(BaseModel):
    enabled: bool = True
    base_url: str = "http://localhost:11434"
    model: str = "llama3.1"


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8420
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])


class ExportConfig(BaseModel):
    vault_path: str | None = None
    project_slug: str | None = None


class Settings(BaseSettings):
    model: ModelConfig = Field(default_factory=ModelConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)
    db_path: str = str(DB_PATH)
    project_name: str = "My Startup"

    model_config = {"env_prefix": "YOAK_", "env_nested_delimiter": "__"}


def ensure_yoak_dir() -> Path:
    YOAK_DIR.mkdir(parents=True, exist_ok=True)
    return YOAK_DIR


def load_settings() -> Settings:
    ensure_yoak_dir()
    if CONFIG_PATH.exists():
        raw = yaml.safe_load(CONFIG_PATH.read_text()) or {}
        return Settings(**raw)
    return Settings()


def save_settings(settings: Settings) -> None:
    ensure_yoak_dir()
    data = settings.model_dump(mode="json")
    CONFIG_PATH.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))


def update_setting(key_path: str, value: Any) -> Settings:
    """Update a nested setting by dot-separated path (e.g. 'model.temperature')."""
    settings = load_settings()
    data = settings.model_dump()
    keys = key_path.split(".")
    target = data
    for k in keys[:-1]:
        target = target[k]
    target[keys[-1]] = value
    new_settings = Settings(**data)
    save_settings(new_settings)
    return new_settings
