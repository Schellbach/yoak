"""Main agent orchestrator — routes conversations through philosophy, memory, and workflows."""

from __future__ import annotations

import uuid
from typing import AsyncIterator

import aiosqlite

from yoak.core.config import Settings
from yoak.core.router import route_message
from yoak.memory.canvas import canvas_summary, get_canvas
from yoak.memory.journal import get_phase, get_recent_summary
from yoak.memory.store import get_db
from yoak.models.provider import Chunk, Message, complete, stream
from yoak.models.streaming import StreamAccumulator
from yoak.philosophy.synthesis import build_context_prompt, load_system_prompt
from yoak.skills import get_skill
from yoak.workflows import create_workflow
from yoak.workflows.base import Workflow


class Agent:
    """The Yoak cofounder agent."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._db: aiosqlite.Connection | None = None
        self._active_workflow: Workflow | None = None
        self._conversation_id: str = uuid.uuid4().hex[:12]
        self._messages: list[Message] = []

    async def _ensure_db(self) -> aiosqlite.Connection:
        if self._db is None:
            self._db = await get_db(self.settings.db_path)
        return self._db

    async def _build_system_messages(self, user_message: str) -> list[Message]:
        """Assemble the full system + context prompt."""
        db = await self._ensure_db()

        system_prompt = load_system_prompt()
        phase = await get_phase(db)
        blocks = await get_canvas(db)
        c_summary = canvas_summary(blocks)
        j_summary = await get_recent_summary(db)

        context = build_context_prompt(
            phase=phase,
            canvas_summary=c_summary,
            journal_summary=j_summary,
            user_message=user_message,
        )

        # Add workflow supplement if active
        workflow_supplement = ""
        if self._active_workflow and not self._active_workflow.is_complete:
            workflow_supplement = (
                f"\n\n---\n## Active Workflow: {self._active_workflow.progress}\n\n"
                + self._active_workflow.get_prompt_supplement()
            )

        # Add skill supplement if routed to one
        skill_supplement = ""
        if not self._active_workflow:
            route_type, route_name = route_message(user_message)
            if route_type == "skill":
                skill = get_skill(route_name)
                if skill:
                    skill_supplement = f"\n\n---\n## Skill: {skill.name}\n\n{skill.get_prompt()}"

        full_system = system_prompt + "\n\n---\n" + context + workflow_supplement + skill_supplement

        return [Message(role="system", content=full_system)]

    async def chat(self, user_message: str) -> str:
        """Send a message and get a complete response."""
        system_msgs = await self._build_system_messages(user_message)

        self._messages.append(Message(role="user", content=user_message))

        all_messages = system_msgs + self._messages

        result = await complete(all_messages, self.settings)

        self._messages.append(Message(role="assistant", content=result.content))
        return result.content

    async def chat_stream(self, user_message: str) -> AsyncIterator[Chunk]:
        """Send a message and stream the response."""
        system_msgs = await self._build_system_messages(user_message)

        self._messages.append(Message(role="user", content=user_message))

        all_messages = system_msgs + self._messages

        accumulator = StreamAccumulator()
        async for chunk in stream(all_messages, self.settings):
            accumulator.feed(chunk)
            yield chunk

        self._messages.append(Message(role="assistant", content=accumulator.text))

    def start_workflow(self, workflow_name: str) -> bool:
        """Start a named workflow."""
        wf = create_workflow(workflow_name)
        if wf:
            self._active_workflow = wf
            return True
        return False

    def advance_workflow(self) -> str | None:
        """Advance to the next step of the active workflow."""
        if self._active_workflow and not self._active_workflow.is_complete:
            self._active_workflow.advance()
            if self._active_workflow.is_complete:
                name = self._active_workflow.name
                self._active_workflow = None
                return f"Workflow '{name}' completed."
            return self._active_workflow.progress
        return None

    def cancel_workflow(self) -> None:
        self._active_workflow = None

    @property
    def active_workflow(self) -> dict | None:
        if self._active_workflow:
            return self._active_workflow.to_dict()
        return None

    @property
    def conversation_history(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self._messages]

    def reset_conversation(self) -> None:
        self._messages = []
        self._active_workflow = None
        self._conversation_id = uuid.uuid4().hex[:12]

    async def auto_route(self, user_message: str) -> str | None:
        """Detect intent and optionally start a workflow. Returns the workflow name if started."""
        if self._active_workflow:
            return None
        route_type, route_name = route_message(user_message)
        if route_type == "workflow":
            self.start_workflow(route_name)
            return route_name
        return None

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def get_db(self) -> aiosqlite.Connection:
        return await self._ensure_db()
