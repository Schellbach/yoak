"""Orchestrate one-way export to an Obsidian vault."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import aiosqlite

from yoak.export.canvas import build_canvas_json
from yoak.export.filenames import parse_export_id_from_frontmatter
from yoak.export.frontmatter import is_yoak_managed, read_frontmatter
from yoak.export.writers import (
    write_block_note,
    write_dashboard,
    write_hypothesis_note,
    write_journal_day,
    write_pivot_note,
)
from yoak.memory.canvas import get_canvas
from yoak.memory.hypotheses import Hypothesis, list_hypotheses, list_status_history
from yoak.memory.journal import JournalEntry, list_entries


@dataclass
class ExportResult:
    output_dir: Path
    files_written: list[str] = field(default_factory=list)
    files_skipped: list[str] = field(default_factory=list)
    files_deleted: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


async def _list_all_journal_entries(db: aiosqlite.Connection) -> list[JournalEntry]:
    return await list_entries(db, limit=10_000, offset=0)


async def build_export_files(
    db: aiosqlite.Connection,
    *,
    project_name: str,
    project_id: str,
    exported: str,
) -> tuple[dict[str, str], set[str], set[str], set[str]]:
    blocks = await get_canvas(db)
    hypotheses = await list_hypotheses(db)
    hypotheses.sort(key=lambda item: (item.created_at, item.id))
    hypothesis_by_id = {item.id: item for item in hypotheses}
    hypotheses_by_block: dict[str, list[Hypothesis]] = defaultdict(list)
    for item in hypotheses:
        hypotheses_by_block[item.canvas_block].append(item)

    entries = await _list_all_journal_entries(db)
    non_pivot = [entry for entry in entries if entry.entry_type != "pivot"]
    pivots = [entry for entry in entries if entry.entry_type == "pivot"]
    pivots.sort(key=lambda item: (item.created_at, item.id))

    files: dict[str, str] = {}
    managed_ids: set[str] = set()
    journal_dates: set[str] = set()

    canvas_name = f"{project_id}.canvas"

    for block in blocks:
        rel, content = write_block_note(
            block,
            hypotheses=hypotheses_by_block.get(block.id, []),
            exported=exported,
        )
        files[rel] = content

    for hypothesis in hypotheses:
        block_name = next((b.block_name for b in blocks if b.id == hypothesis.canvas_block), hypothesis.canvas_block)
        history = await list_status_history(db, hypothesis.id)
        rel, content = write_hypothesis_note(
            hypothesis,
            block_name=block_name,
            history=history,
            exported=exported,
        )
        files[rel] = content
        managed_ids.add(f"H-{hypothesis.id}")

    journal_by_day: dict[str, list[JournalEntry]] = defaultdict(list)
    for entry in non_pivot:
        day = entry.created_at[:10]
        journal_by_day[day].append(entry)
        journal_dates.add(day)

    for day in sorted(journal_by_day):
        rel, content = write_journal_day(
            day,
            journal_by_day[day],
            hypothesis_by_id=hypothesis_by_id,
            exported=exported,
        )
        files[rel] = content

    for pivot in pivots:
        rel, content = write_pivot_note(
            pivot,
            hypothesis_by_id=hypothesis_by_id,
            exported=exported,
        )
        files[rel] = content
        managed_ids.add(f"P-{pivot.id}")

    recent_journal = sorted(journal_dates, reverse=True)[:5]
    dash_rel, dash_content = write_dashboard(
        project_name=project_name,
        blocks=blocks,
        hypotheses=hypotheses,
        journal_dates=recent_journal,
        exported=exported,
    )
    files[dash_rel] = dash_content
    files[canvas_name] = build_canvas_json(blocks, hypotheses_by_block)

    return files, managed_ids, journal_dates, {canvas_name}


async def export_to_vault(
    db: aiosqlite.Connection,
    vault_path: Path,
    *,
    project_name: str,
    project_id: str,
    exported: str,
    force: bool = False,
) -> ExportResult:
    output_dir = vault_path / "yoak" / project_id
    result = ExportResult(output_dir=output_dir)

    if output_dir.exists() and any(output_dir.rglob("*.md")) and not force:
        managed_present = False
        for path in output_dir.rglob("*.md"):
            try:
                if is_yoak_managed(path.read_text(encoding="utf-8")):
                    managed_present = True
                    break
            except OSError:
                continue
        if managed_present:
            raise FileExistsError(
                f"Export target already contains yoak-managed notes at {output_dir}. "
                "Re-run with --force to regenerate."
            )

    files, managed_ids, journal_dates, canvas_files = await build_export_files(
        db,
        project_name=project_name,
        project_id=project_id,
        exported=exported,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("canvas", "hypotheses", "journal", "pivots"):
        (output_dir / sub).mkdir(parents=True, exist_ok=True)

    for rel_path, content in sorted(files.items()):
        target = output_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if not is_yoak_managed(existing):
                result.files_skipped.append(rel_path)
                result.warnings.append(f"Skipped unmanaged file: {target}")
                continue
        target.write_text(content, encoding="utf-8", newline="\n")
        result.files_written.append(rel_path)

    _cleanup_stale_files(
        output_dir,
        managed_ids=managed_ids,
        journal_dates=journal_dates,
        canvas_files=canvas_files,
        result=result,
    )
    return result


def _cleanup_stale_files(
    output_dir: Path,
    *,
    managed_ids: set[str],
    journal_dates: set[str],
    canvas_files: set[str],
    result: ExportResult,
) -> None:
    for folder, prefix in (("hypotheses", "H-"), ("pivots", "P-")):
        directory = output_dir / folder
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if not is_yoak_managed(text):
                continue
            frontmatter, _ = read_frontmatter(text)
            export_id = parse_export_id_from_frontmatter(frontmatter or {})
            if export_id and export_id.startswith(prefix) and export_id not in managed_ids:
                path.unlink()
                result.files_deleted.append(str(path.relative_to(output_dir)))

    journal_dir = output_dir / "journal"
    if journal_dir.exists():
        for path in sorted(journal_dir.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if not is_yoak_managed(text):
                continue
            frontmatter, _ = read_frontmatter(text)
            day = (frontmatter or {}).get("date")
            if isinstance(day, str) and day not in journal_dates:
                path.unlink()
                result.files_deleted.append(str(path.relative_to(output_dir)))

    for path in sorted(output_dir.glob("*.canvas")):
        if path.name not in canvas_files:
            path.unlink()
            result.files_deleted.append(path.name)
