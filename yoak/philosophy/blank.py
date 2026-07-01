"""Steve Blank Customer Development methodology — the agent's process."""

from __future__ import annotations

from pathlib import Path

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "system" / "blank_methodology.md"

PHASES = ("discovery", "validation", "creation", "building")

PHASE_DESCRIPTIONS = {
    "discovery": "Customer Discovery — transforming hypotheses into facts by getting out of the building",
    "validation": "Customer Validation — proving a repeatable sales process and Product/Market Fit",
    "creation": "Customer Creation — creating and driving end-user demand",
    "building": "Company Building — transitioning from search to execution at scale",
}

CANVAS_BLOCKS = [
    "problem",
    "solution",
    "unique_value_proposition",
    "unfair_advantage",
    "customer_segments",
    "cost_structure",
    "revenue_streams",
    "channels",
    "key_metrics",
]


def load_prompt() -> str:
    return _PROMPT_PATH.read_text()


def get_phase_guidance(phase: str) -> str:
    """Return methodology guidance for the current Customer Development phase."""
    full = load_prompt()

    phase_map = {
        "discovery": "### Phase 1: Customer Discovery",
        "validation": "### Phase 2: Customer Validation",
        "creation": "### Phase 3: Customer Creation",
        "building": "### Phase 4: Company Building",
    }

    marker = phase_map.get(phase, phase_map["discovery"])
    start = full.find(marker)
    if start == -1:
        return ""
    next_h3 = full.find("\n### Phase", start + len(marker))
    if next_h3 == -1:
        next_h2 = full.find("\n## ", start + len(marker))
        end = next_h2 if next_h2 != -1 else len(full)
    else:
        end = next_h3
    return full[start:end].strip()


def get_mvp_guidance() -> str:
    full = load_prompt()
    marker = "## MVP Types"
    start = full.find(marker)
    if start == -1:
        return ""
    next_h2 = full.find("\n## ", start + len(marker))
    end = next_h2 if next_h2 != -1 else len(full)
    return full[start:end].strip()


def get_pivot_guidance() -> str:
    full = load_prompt()
    marker = "## Pivot Types"
    start = full.find(marker)
    if start == -1:
        return ""
    next_h2 = full.find("\n## ", start + len(marker))
    end = next_h2 if next_h2 != -1 else len(full)
    return full[start:end].strip()


def get_pmf_guidance() -> str:
    full = load_prompt()
    marker = "## Product/Market Fit"
    start = full.find(marker)
    if start == -1:
        return ""
    return full[start:].strip()
