"""Base workflow class — state machine for multi-turn guided processes."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

WORKFLOW_CONVERSATION_RULES = """
## Workflow conversation rules
- Read the full message history above. Do not re-summarize the entire idea each turn.
- Never repeat a phrase you already used (e.g. "that's great user research",
  "it sounds like you're building...").
- Every reply must include something with teeth: a concern, pushback, sharp opinion,
  or concrete test — not only "tell me more."
- Ask at most one specific question. Avoid open-ended "can you tell me more about X?"
- Never output role labels or template markers (### User:, User:, Assistant:, etc.).
  Plain conversational text only.
- Steps advance automatically when the founder gives a substantive answer.
  Match the current step goal; do not behave as if you are still on an earlier step.
"""


@dataclass
class WorkflowStep:
    name: str
    prompt_supplement: str
    exit_criteria: list[str] = field(default_factory=list)
    min_user_chars: int = 40
    max_turns: int = 2


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

    @property
    def turns_on_step(self) -> int:
        return int(self._state.get("turns_on_step", 0))

    def record_user_turn(self, message: str) -> None:
        self._state["turns_on_step"] = self.turns_on_step + 1
        self._state["last_user_len"] = len(message.strip())

    def should_auto_advance(self, message: str) -> bool:
        """True when the founder's reply satisfies this step — advance before the next model turn."""
        if self.is_complete or not self.current_step:
            return False
        # Final step is model-delivered (verdict, honest take); don't skip it on user input.
        if self._current_step_index >= len(self.steps) - 1:
            return False
        step = self.current_step
        msg_len = len(message.strip())
        if self.turns_on_step >= step.max_turns:
            return True
        if self.turns_on_step >= 1 and msg_len >= step.min_user_chars:
            return True
        return False

    def advance(self) -> None:
        self._current_step_index += 1
        self._state["turns_on_step"] = 0

    def complete_after_response(self) -> bool:
        """Call after the model responds on the final step."""
        if self.is_complete:
            return False
        if self._current_step_index == len(self.steps) - 1:
            self.advance()
            return True
        return False

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
