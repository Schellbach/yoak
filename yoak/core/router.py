"""Intent detection and workflow/skill dispatch."""

from __future__ import annotations

from yoak.philosophy.synthesis import detect_topic_intent
from yoak.skills import SKILL_REGISTRY, Skill
from yoak.workflows import WORKFLOW_REGISTRY, Workflow, create_workflow


def route_message(message: str) -> tuple[str, str]:
    """Return (route_type, route_name) for a user message.

    route_type is 'workflow', 'skill', or 'general'.
    """
    intent = detect_topic_intent(message)

    if intent in WORKFLOW_REGISTRY:
        return "workflow", intent
    if intent in SKILL_REGISTRY:
        return "skill", intent
    return "general", "general"


def get_workflow_or_skill(route_type: str, route_name: str) -> Workflow | Skill | None:
    if route_type == "workflow":
        return create_workflow(route_name)
    if route_type == "skill":
        return SKILL_REGISTRY.get(route_name)
    return None
