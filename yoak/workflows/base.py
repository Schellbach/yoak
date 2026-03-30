"""Base workflow class — state machine for multi-turn guided processes."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WorkflowStep:
    name: str
    prompt_supplement: str
    exit_criteria: list[str] = field(default_factory=list)


class Workflow:
    """A state machine guiding the agent through a multi-step process."""

    name: str = "base"
    description: str = ""
    steps: list[WorkflowStep] = []

    def __init__(self) -> None:
        self._current_step_index = 0
        self._state: dict[str, Any] = {}

    @property
    def current_step(self) -> WorkflowStep | None:
        if 0 <= self._current_step_index < len(self.steps):
            return self.steps[self._current_step_index]
        return None

    @property
    def is_complete(self) -> bool:
        return self._current_step_index >= len(self.steps)

    @property
    def progress(self) -> str:
        total = len(self.steps)
        current = min(self._current_step_index + 1, total)
        step = self.current_step
        step_name = step.name if step else "Complete"
        return f"[{self.name}] Step {current}/{total}: {step_name}"

    def advance(self) -> None:
        self._current_step_index += 1

    def reset(self) -> None:
        self._current_step_index = 0
        self._state = {}

    def get_prompt_supplement(self) -> str:
        step = self.current_step
        if step:
            return step.prompt_supplement
        return ""

    def set_state(self, key: str, value: Any) -> None:
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "current_step": self._current_step_index,
            "total_steps": len(self.steps),
            "step_name": self.current_step.name if self.current_step else None,
            "is_complete": self.is_complete,
            "state": self._state,
        }

    @classmethod
    def _load_prompt(cls, filename: str) -> str:
        path = Path(__file__).parent.parent / "prompts" / "workflows" / filename
        return path.read_text()
