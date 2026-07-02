"""YAML frontmatter serialization and parsing."""

from __future__ import annotations

from typing import Any

import yaml


def dump_frontmatter(fields: dict[str, Any]) -> str:
    body = yaml.dump(
        fields,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=1000,
    ).rstrip()
    return f"---\n{body}\n---\n"


def read_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    data = yaml.safe_load(parts[1]) or {}
    if not isinstance(data, dict):
        return None, text
    return data, parts[2].lstrip("\n")


def is_yoak_managed(path_text: str) -> bool:
    frontmatter, _ = read_frontmatter(path_text)
    return bool(frontmatter and frontmatter.get("yoak_managed") is True)
