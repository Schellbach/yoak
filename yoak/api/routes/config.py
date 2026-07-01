"""Configuration management endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from yoak.core.config import load_settings, update_setting
from yoak.models.catalog import list_model_options

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
async def list_models():
    return list_model_options()
