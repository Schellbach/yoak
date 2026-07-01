"""Extract structured memory updates from agent responses."""

from __future__ import annotations

import re
from dataclasses import dataclass

import aiosqlite

from yoak.memory.canvas import VALID_CANVAS_BLOCK_IDS, update_block
from yoak.memory.hypotheses import create_hypothesis
from yoak.memory.journal import add_entry

_CANVAS_RE = re.compile(r"\[CANVAS:\s*(\w+)\]\s*(.+?)(?=\[(?:CANVAS|HYPOTHESIS|LEARNING)|$)", re.IGNORECASE)
_HYPOTHESIS_RE = re.compile(
    r"\[HYPOTHESIS:\s*(\w+)\]\s*(.+?)(?=\[(?:CANVAS|HYPOTHESIS|LEARNING)|$)",
    re.IGNORECASE,
)
_LEARNING_RE = re.compile(r"\[LEARNING\]\s*(.+?)(?=\[(?:CANVAS|HYPOTHESIS|LEARNING)|$)", re.IGNORECASE)
_TAG_LINE = re.compile(
    r"^\s*#*\s*\**\[?(?:CANVAS|HYPOTHESIS|LEARNING)[^\n]*\]?",
    re.IGNORECASE,
)
_STRAY_TAG = re.compile(
    r"\*+\[?(?:CANVAS|HYPOTHESIS|LEARNING):\s*\w+\]?\s*[^\n]*|\[LEARNING\]\s*[^\n]*",
    re.IGNORECASE,
)

_ARTIFACT_HEADER = re.compile(
    r"^#{0,3}\s*(User|Assistant|Human|AI|System)\s*:?\s*",
    re.IGNORECASE,
)
_ARTIFACT_LABEL = re.compile(
    r"^(User|Assistant|Human|AI|System)\s*:\s*",
    re.IGNORECASE,
)

@dataclass
class Extraction:
    canvas_updates: list[tuple[str, str]]
    hypotheses: list[tuple[str, str]]
    learnings: list[tuple[str, str]]
    clean_text: str


def _normalize_tag_source(text: str) -> str:
    """Remove markdown noise so tags parse even when models wrap them."""
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        stripped = re.sub(r"^#+\s*", "", stripped)
        stripped = re.sub(r"^\*+|\*+$", "", stripped).strip()
        lines.append(stripped)
    return "\n".join(lines)


def _extract_tags(text: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
    canvas_updates: list[tuple[str, str]] = []
    hypotheses: list[tuple[str, str]] = []
    learnings: list[tuple[str, str]] = []

    for match in _CANVAS_RE.finditer(text):
        block_id = match.group(1).lower()
        if block_id in VALID_CANVAS_BLOCK_IDS:
            canvas_updates.append((block_id, match.group(2).strip().strip("*")))

    for match in _HYPOTHESIS_RE.finditer(text):
        block_id = match.group(1).lower()
        if block_id in VALID_CANVAS_BLOCK_IDS:
            hypotheses.append((block_id, match.group(2).strip().strip("*")))

    for match in _LEARNING_RE.finditer(text):
        learnings.append(_split_learning(match.group(1).strip().strip("*")))

    return canvas_updates, hypotheses, learnings


def sanitize_response_text(text: str) -> str:
    """Strip prompt-template leaks (### User:, role labels, echoed turns)."""
    for marker in ("### User:", "### Assistant:", "### Human:", "### System:"):
        if marker in text:
            text = text.split(marker, 1)[0]

    cleaned_lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if _ARTIFACT_HEADER.match(stripped) or _ARTIFACT_LABEL.match(stripped):
            break
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def _strip_tag_lines(text: str) -> str:
    clean_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        normalized = re.sub(r"^#+\s*", "", stripped)
        normalized = re.sub(r"^\*+|\*+$", "", normalized).strip()
        if _TAG_LINE.match(normalized):
            continue
        without_inline = _STRAY_TAG.sub("", line).strip()
        if without_inline:
            clean_lines.append(without_inline)
    return "\n".join(clean_lines).strip()


def parse_response(text: str) -> Extraction:
    """Parse structured tags from a response and return clean text + extracted items."""
    text = sanitize_response_text(text)
    tag_source = _normalize_tag_source(text)
    canvas_updates, hypotheses, learnings = _extract_tags(tag_source)
    clean_text = _strip_tag_lines(text)

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
