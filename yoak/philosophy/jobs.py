"""Steve Jobs product design philosophy — the agent's taste."""

from __future__ import annotations

from pathlib import Path

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "system" / "jobs_philosophy.md"


def load_prompt() -> str:
    return _PROMPT_PATH.read_text()


QUALITY_CHECKS = [
    "simplicity",
    "focus",
    "craft",
    "empathy",
    "experience_first",
]


def get_relevant_principles(topic: str) -> str:
    """Return Jobs principles most relevant to the conversation topic."""
    topic_lower = topic.lower()
    sections = []

    if any(w in topic_lower for w in ("design", "ui", "ux", "interface", "experience", "user")):
        sections.append(_section("Design is How It Works"))
        sections.append(_section("The Experience-First Test"))

    if any(w in topic_lower for w in ("feature", "scope", "roadmap", "priority", "focus")):
        sections.append(_section("Focus Means Saying No"))
        sections.append(_section("The Focus Test"))

    if any(w in topic_lower for w in ("quality", "craft", "detail", "polish", "bug")):
        sections.append(_section("Craft, Above All"))
        sections.append(_section("The Quality Test"))

    if any(w in topic_lower for w in ("simple", "complex", "strip", "minimal", "clean")):
        sections.append(_section("Simplicity is the Ultimate Sophistication"))
        sections.append(_section("The Simplicity Test"))

    if any(w in topic_lower for w in ("customer", "market", "user", "empathy")):
        sections.append(_section("Start with the Customer Experience"))
        sections.append(_section("The Empathy Check"))

    if any(w in topic_lower for w in ("vision", "conviction", "bold", "future")):
        sections.append(_section("On Vision"))

    if not sections:
        sections.append(_section("Core Principles"))

    return "\n\n".join(s for s in sections if s)


def _section(name: str) -> str:
    full = load_prompt()
    for prefix in ("### ", "## "):
        marker = f"{prefix}{name}"
        start = full.find(marker)
        if start != -1:
            next_h = full.find("\n#", start + len(marker))
            if next_h == -1:
                return full[start:]
            return full[start:next_h].strip()
    return ""


def get_product_critique_prompt() -> str:
    """Load the full product critique workflow prompt."""
    path = Path(__file__).parent.parent / "prompts" / "workflows" / "product_critique.md"
    return path.read_text()
