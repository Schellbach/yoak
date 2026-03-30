"""Shared API dependencies."""

from __future__ import annotations

from fastapi import Request

from yoak.core.agent import Agent
from yoak.core.config import Settings


def get_agent(request: Request) -> Agent:
    return request.app.state.agent


def get_settings(request: Request) -> Settings:
    return request.app.state.settings
