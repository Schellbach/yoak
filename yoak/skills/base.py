"""Base skill class."""

from __future__ import annotations

from pathlib import Path


class Skill:
    name: str = "base"
    description: str = ""
    prompt_file: str = ""

    def get_prompt(self) -> str:
        path = Path(__file__).parent.parent / "prompts" / "skills" / self.prompt_file
        return path.read_text()
