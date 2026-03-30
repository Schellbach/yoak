"""Extract structured memory updates from agent responses."""

from __future__ import annotations

import re
from dataclasses import dataclass

import aiosqlite

from yoak.memory.canvas import update_block
from yoak.memory.hypotheses import create_hypothesis
from yoak.memory.journal import add_entry

_CANVAS_RE = re.compile(r"\[CANVAS:(\w+)\]\s*(.+)")
_HYPOTHESIS_RE = re.compile(r"\[HYPOTHESIS:(\w+)\]\s*(.+)")
_LEARNING_RE = re.compile(r"\[LEARNING\]\s*(.+)")

VALID_BLOCKS = {
    "customer_segments",
    "value_propositions",
    "channels",
    "customer_relationships",
    "revenue_streams",
    "key_resources",
    "key_activities",
    "key_partners",
    "cost_structure",
}


@dataclass
class Extraction:
    canvas_updates: list[tuple[str, str]]
    hypotheses: list[tuple[str, str]]
    learnings: list[tuple[str, str]]
    clean_text: str


def parse_response(text: str) -> Extraction:
    """Parse structured tags from a response and return clean text + extracted items."""
    canvas_updates = []
    hypotheses = []
    learnings = []
    clean_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        m = _CANVAS_RE.match(stripped)
        if m and m.group(1) in VALID_BLOCKS:
            canvas_updates.append((m.group(1), m.group(2).strip()))
            continue

        m = _HYPOTHESIS_RE.match(stripped)
        if m and m.group(1) in VALID_BLOCKS:
            hypotheses.append((m.group(1), m.group(2).strip()))
            continue

        m = _LEARNING_RE.match(stripped)
        if m:
            learnings.append(_split_learning(m.group(1).strip()))
            continue

        clean_lines.append(line)

    clean_text = "\n".join(clean_lines).strip()

    return Extraction(
        canvas_updates=canvas_updates,
        hypotheses=hypotheses,
        learnings=learnings,
        clean_text=clean_text,
    )


def _split_learning(text: str) -> tuple[str, str]:
    """Split 'title | content' or use the text as both."""
    if "|" in text:
        parts = text.split("|", 1)
        return parts[0].strip(), parts[1].strip()
    return text[:60], text


async def apply_extractions(db: aiosqlite.Connection, extraction: Extraction) -> list[str]:
    """Write extracted items to the database. Returns a list of what was saved."""
    saved = []

    for block_id, content in extraction.canvas_updates:
        await update_block(db, block_id, content)
        saved.append(f"canvas:{block_id}")

    for block_id, statement in extraction.hypotheses:
        await create_hypothesis(db, block_id, statement)
        saved.append(f"hypothesis:{block_id}")

    for title, content in extraction.learnings:
        await add_entry(db, "learning", title, content)
        saved.append(f"learning:{title}")

    return saved
