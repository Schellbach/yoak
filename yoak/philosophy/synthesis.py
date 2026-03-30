"""Synthesis — combined meta-framework across all three philosophies."""

from __future__ import annotations

from pathlib import Path

from yoak.philosophy import blank, graham, jobs

_SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "system" / "cofounder.md"


def load_system_prompt() -> str:
    return _SYSTEM_PROMPT_PATH.read_text()


def build_context_prompt(
    *,
    phase: str,
    canvas_summary: str,
    journal_summary: str,
    user_message: str,
) -> str:
    """Build the full context block injected alongside the system prompt."""
    parts = [
        f"## Current Phase: {blank.PHASE_DESCRIPTIONS.get(phase, phase)}\n",
        canvas_summary,
        journal_summary,
        "---",
        "## Relevant Methodology\n",
        blank.get_phase_guidance(phase),
        "\n## Relevant Instincts\n",
        graham.get_relevant_heuristics(user_message),
        "\n## Relevant Design Principles\n",
        jobs.get_relevant_principles(user_message),
    ]
    return "\n\n".join(parts)


def detect_topic_intent(message: str) -> str:
    """Coarse intent detection to route to the right workflow or skill."""
    msg = message.lower()

    if any(w in msg for w in ("idea", "concept", "what if", "should i build", "startup idea")):
        return "idea_evaluation"
    if any(w in msg for w in ("interview", "talk to", "customer", "discovery", "problem")):
        return "customer_discovery"
    if any(w in msg for w in ("sell", "price", "revenue", "mvp", "validate", "validation")):
        return "customer_validation"
    if any(w in msg for w in ("pivot", "change direction", "not working", "give up")):
        return "pivot_decision"
    if any(w in msg for w in ("product market fit", "pmf", "retention", "churn", "growing")):
        return "pmf_assessment"
    if any(w in msg for w in ("design", "ux", "ui", "feature", "product review", "critique")):
        return "product_critique"
    if any(w in msg for w in ("market", "tam", "sam", "competitors", "landscape")):
        return "market_analysis"
    if any(w in msg for w in ("growth", "scale", "viral", "acquisition")):
        return "growth_strategy"
    if any(w in msg for w in ("economics", "cac", "ltv", "burn", "runway", "unit")):
        return "unit_economics"
    if any(w in msg for w in ("competition", "moat", "competitor", "differentiat")):
        return "competitive_intel"

    return "general"
