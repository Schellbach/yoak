"""Paul Graham decision heuristics — the agent's instincts."""

from __future__ import annotations

from pathlib import Path

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "system" / "pg_principles.md"


def load_prompt() -> str:
    return _PROMPT_PATH.read_text()


IDEA_FILTERS = [
    "well_not_field",
    "schlep_blindness",
    "unsexy_filter",
    "organic_vs_manufactured",
    "path_out",
]

ANTI_PATTERNS = [
    "sitcom_startup",
    "big_launch_fallacy",
    "premature_scaling",
    "partnership_fantasy",
    "strategizing_as_procrastination",
    "playing_house",
    "linear_thinking",
    "silent_retreat",
]


def get_relevant_heuristics(topic: str) -> str:
    """Return PG heuristics most relevant to a conversation topic."""
    topic_lower = topic.lower()

    sections = []

    if any(w in topic_lower for w in ("idea", "concept", "start", "build what", "problem")):
        sections.append(_section("Idea Evaluation"))

    if any(w in topic_lower for w in ("grow", "metric", "user", "traction", "rate")):
        sections.append(_section("Growth"))

    if any(w in topic_lower for w in ("launch", "ship", "scale", "manual", "early")):
        sections.append(_section("Execution"))

    if any(w in topic_lower for w in ("stuck", "quit", "demoralized", "failing", "lost")):
        sections.append(_section("Survival"))

    if any(w in topic_lower for w in ("hire", "team", "cofounder", "people", "culture")):
        sections.append(_section("People"))

    if not sections:
        sections.append(_section("Execution"))

    return "\n\n".join(sections)


def _section(name: str) -> str:
    """Extract a named section from the PG principles prompt."""
    full = load_prompt()
    marker = f"## {name}"
    start = full.find(marker)
    if start == -1:
        return ""
    next_h2 = full.find("\n## ", start + len(marker))
    if next_h2 == -1:
        return full[start:]
    return full[start:next_h2].strip()


_SURVIVAL_PROMPT = """## PG on Survival
- Most startups die because founders get demoralized and quit — not from insurmountable external obstacles.
- "Keep typing" — startups rarely die mid-keystroke.
- Demoralization is the true cause of death. The roller coaster is normal.
- If even a small core of users are ecstatic, you're on the right track.
- Stay in contact with peers/investors who expect progress — accountability is a forcing function.
- "Not hearing from a startup is a 100% accurate predictor of death."
"""


def get_survival_prompt() -> str:
    return _SURVIVAL_PROMPT
