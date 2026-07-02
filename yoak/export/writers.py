"""Markdown writers for Obsidian export."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from yoak.export.datetime_util import parse_date, parse_time
from yoak.export.filenames import (
    block_filename,
    block_kebab,
    block_wikilink,
    hypothesis_export_id,
    hypothesis_filename,
    hypothesis_wikilink,
    pivot_export_id,
    pivot_filename,
)
from yoak.export.frontmatter import dump_frontmatter
from yoak.memory.canvas import LEAN_CANVAS_BLOCKS, CanvasBlock
from yoak.memory.hypotheses import Hypothesis
from yoak.memory.journal import JournalEntry

STATUS_GROUPS = ("validated", "testing", "untested", "invalidated")


@dataclass
class ExportBundle:
    files: dict[str, str] = field(default_factory=dict)
    managed_ids: set[str] = field(default_factory=set)


def _evidence_summary(item: dict) -> str:
    verdict = "supports" if item.get("supports") else "contradicts"
    return f"**{item.get('source', 'Unknown')}** — {item.get('finding', '').strip()} ({verdict})"


def _history_lines(history: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    previous: str | None = None
    for row in history:
        status = row["status"]
        if status == previous:
            continue
        lines.append(f"- **{parse_date(row['changed_at'])}** — status set to **{status}**")
        previous = status
    return lines


def write_hypothesis_note(
    hypothesis: Hypothesis,
    *,
    block_name: str,
    history: list[dict[str, str]],
    exported: str,
) -> tuple[str, str]:
    export_id = hypothesis_export_id(hypothesis.id)
    rel_path = f"hypotheses/{hypothesis_filename(hypothesis.id, hypothesis.statement)}"

    frontmatter = {
        "yoak_managed": True,
        "id": export_id,
        "type": "hypothesis",
        "block": block_kebab(hypothesis.canvas_block),
        "status": hypothesis.status,
        "confidence": float(hypothesis.confidence),
        "created": parse_date(hypothesis.created_at),
        "updated": parse_date(hypothesis.updated_at),
        "exported": exported,
        "tags": ["yoak/hypothesis"],
    }

    body_lines = [
        f"# {hypothesis.statement}",
        "",
        f"Block: {block_wikilink(hypothesis.canvas_block, block_name)}",
        "",
        "## Evidence",
        "",
    ]
    if hypothesis.evidence:
        for item in hypothesis.evidence:
            body_lines.append(f"- {_evidence_summary(item)}")
    else:
        body_lines.append("_No evidence yet._")

    history_lines = _history_lines(history)
    if history_lines:
        body_lines.extend(["", "## History", ""])
        body_lines.extend(history_lines)

    content = dump_frontmatter(frontmatter) + "\n".join(body_lines) + "\n"
    return rel_path, content


def write_block_note(
    block: CanvasBlock,
    *,
    hypotheses: list[Hypothesis],
    exported: str,
) -> tuple[str, str]:
    rel_path = f"canvas/{block_filename(block.id, block.block_name)}"
    frontmatter = {
        "yoak_managed": True,
        "type": "lean-canvas-block",
        "block": block_kebab(block.id),
        "exported": exported,
        "tags": ["yoak/canvas"],
    }

    body_lines = [f"# {block.block_name}", ""]
    if block.content.strip():
        body_lines.append(block.content.strip())
    else:
        body_lines.append("_Empty._")
    body_lines.extend(["", "## Hypotheses", ""])

    grouped: dict[str, list[Hypothesis]] = {status: [] for status in STATUS_GROUPS}
    for hypothesis in sorted(hypotheses, key=lambda h: (h.statement.lower(), h.id)):
        grouped.setdefault(hypothesis.status, []).append(hypothesis)

    for status in STATUS_GROUPS:
        items = grouped.get(status) or []
        if not items:
            continue
        body_lines.append(f"### {status.capitalize()}")
        body_lines.append("")
        for item in items:
            body_lines.append(f"- {hypothesis_wikilink(item.id, item.statement)}")
        body_lines.append("")

    content = dump_frontmatter(frontmatter) + "\n".join(body_lines).rstrip() + "\n"
    return rel_path, content


def _journal_wikilinks(
    entry: JournalEntry,
    *,
    hypothesis_by_id: dict[str, Hypothesis],
) -> str:
    content = entry.content
    linked: set[str] = set()

    for tag in entry.tags:
        if tag.startswith("hypothesis:"):
            db_id = tag.split(":", 1)[1]
            if db_id in hypothesis_by_id:
                linked.add(db_id)

    for db_id in hypothesis_by_id:
        token = hypothesis_export_id(db_id)
        if token in content:
            linked.add(db_id)

    for db_id, hypothesis in hypothesis_by_id.items():
        if db_id in linked:
            continue
        if hypothesis.statement and hypothesis.statement in content:
            linked.add(db_id)

    appendix = ["", "**Related hypotheses:**"]
    for db_id in sorted(linked):
        hypothesis = hypothesis_by_id.get(db_id)
        if not hypothesis:
            continue
        appendix.append(f"- {hypothesis_wikilink(db_id, hypothesis.statement)}")
    if len(appendix) <= 2:
        return content
    return content.rstrip() + "\n" + "\n".join(appendix) + "\n"


def write_journal_day(
    date: str,
    entries: list[JournalEntry],
    *,
    hypothesis_by_id: dict[str, Hypothesis],
    exported: str,
) -> tuple[str, str]:
    rel_path = f"journal/{date}.md"
    frontmatter = {
        "yoak_managed": True,
        "type": "journal",
        "date": date,
        "exported": exported,
        "tags": ["yoak/journal"],
    }

    body_lines: list[str] = []
    for entry in sorted(entries, key=lambda e: (e.created_at, e.id)):
        body_lines.append(f"## {parse_time(entry.created_at)} — {entry.title}")
        body_lines.append("")
        body_lines.append(f"**Type:** {entry.entry_type}")
        if entry.tags:
            body_lines.append(f"**Tags:** {', '.join(entry.tags)}")
        body_lines.append("")
        body_lines.append(_journal_wikilinks(entry, hypothesis_by_id=hypothesis_by_id).rstrip())
        body_lines.append("")

    content = dump_frontmatter(frontmatter) + "\n".join(body_lines).rstrip() + "\n"
    return rel_path, content


def _pivot_triggered_ids(
    entry: JournalEntry,
    *,
    hypothesis_by_id: dict[str, Hypothesis],
) -> list[str]:
    linked: set[str] = set()
    for tag in entry.tags:
        if tag.startswith("hypothesis:"):
            db_id = tag.split(":", 1)[1]
            if db_id in hypothesis_by_id:
                linked.add(db_id)

    pivot_date = entry.created_at
    for db_id, hypothesis in hypothesis_by_id.items():
        if hypothesis.status != "invalidated":
            continue
        if hypothesis.updated_at <= pivot_date or parse_date(hypothesis.updated_at) <= parse_date(pivot_date):
            linked.add(db_id)

    for db_id in hypothesis_by_id:
        token = hypothesis_export_id(db_id)
        if token in entry.content or token in entry.title:
            linked.add(db_id)

    return sorted(linked)


def write_pivot_note(
    entry: JournalEntry,
    *,
    hypothesis_by_id: dict[str, Hypothesis],
    exported: str,
) -> tuple[str, str]:
    export_id = pivot_export_id(entry.id)
    rel_path = f"pivots/{pivot_filename(entry.id, entry.title)}"
    frontmatter = {
        "yoak_managed": True,
        "type": "pivot",
        "id": export_id,
        "date": parse_date(entry.created_at),
        "exported": exported,
        "tags": ["yoak/pivot"],
    }

    body_lines = [
        f"# {entry.title}",
        "",
        entry.content.strip() or "_No pivot details recorded._",
        "",
        "## Triggered by",
        "",
    ]
    triggered = _pivot_triggered_ids(entry, hypothesis_by_id=hypothesis_by_id)
    if triggered:
        for db_id in triggered:
            hypothesis = hypothesis_by_id.get(db_id)
            if not hypothesis:
                continue
            body_lines.append(f"- {hypothesis_wikilink(db_id, hypothesis.statement)}")
    else:
        body_lines.append("_No linked hypotheses._")

    content = dump_frontmatter(frontmatter) + "\n".join(body_lines) + "\n"
    return rel_path, content


def write_dashboard(
    *,
    project_name: str,
    blocks: list[CanvasBlock],
    hypotheses: list[Hypothesis],
    journal_dates: list[str],
    exported: str,
) -> tuple[str, str]:
    rel_path = "Dashboard.md"
    frontmatter = {
        "yoak_managed": True,
        "type": "dashboard",
        "project": project_name,
        "exported": exported,
        "tags": ["yoak/dashboard"],
    }

    counts = Counter(h.status for h in hypotheses)
    body_lines = [
        f"# {project_name} — Yoak Dashboard",
        "",
        "## Hypothesis status",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status in STATUS_GROUPS:
        body_lines.append(f"| {status.capitalize()} | {counts.get(status, 0)} |")
    body_lines.extend(["", "## Lean Canvas blocks", ""])
    for block_id, block_name in LEAN_CANVAS_BLOCKS:
        body_lines.append(f"- [[canvas/{block_filename(block_id, block_name)}|{block_name}]]")
    body_lines.extend(["", "## Recent journal", ""])
    if journal_dates:
        for day in journal_dates:
            body_lines.append(f"- [[journal/{day}|{day}]]")
    else:
        body_lines.append("_No journal entries yet._")

    body_lines.extend(
        [
            "",
            "> [!note] Requires the Dataview plugin",
            ">",
            "> ```dataview",
            "> TABLE status, confidence, block",
            "> FROM #yoak/hypothesis",
            "> SORT status ASC",
            "> ```",
            "",
            "> ```dataview",
            "> TABLE rows.file.link AS Hypothesis, confidence, block",
            "> FROM #yoak/hypothesis",
            "> GROUP BY status",
            "> ```",
            "",
        ]
    )

    content = dump_frontmatter(frontmatter) + "\n".join(body_lines)
    return rel_path, content


def block_health_color(hypotheses: list[Hypothesis]) -> str | None:
    if not hypotheses:
        return None
    counts = Counter(h.status for h in hypotheses)
    total = len(hypotheses)
    if counts.get("validated", 0) > total / 2:
        return "4"
    if counts.get("invalidated", 0) > total / 2:
        return "1"
    if counts.get("testing", 0) > 0:
        return "3"
    return None
