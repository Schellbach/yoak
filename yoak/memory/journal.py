"""Learning journal — timestamped append-only log of insights, pivots, and decisions."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

import aiosqlite

ENTRY_TYPES = ("learning", "pivot", "decision", "milestone", "interview", "experiment")


@dataclass
class JournalEntry:
    id: str
    entry_type: str
    title: str
    content: str
    tags: list[str]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "entry_type": self.entry_type,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
        }


async def add_entry(
    db: aiosqlite.Connection,
    entry_type: str,
    title: str,
    content: str,
    tags: list[str] | None = None,
) -> str:
    eid = uuid.uuid4().hex[:12]
    await db.execute(
        "INSERT INTO journal_entries (id, entry_type, title, content, tags) VALUES (?, ?, ?, ?, ?)",
        (eid, entry_type, title, content, json.dumps(tags or [])),
    )
    await db.commit()
    return eid


async def list_entries(
    db: aiosqlite.Connection,
    *,
    entry_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[JournalEntry]:
    query = "SELECT * FROM journal_entries WHERE 1=1"
    params: list = []
    if entry_type:
        query += " AND entry_type = ?"
        params.append(entry_type)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    results = []
    async with db.execute(query, params) as cur:
        async for row in cur:
            results.append(
                JournalEntry(
                    id=row["id"],
                    entry_type=row["entry_type"],
                    title=row["title"],
                    content=row["content"],
                    tags=json.loads(row["tags"]),
                    created_at=row["created_at"],
                )
            )
    return results


async def get_entry(db: aiosqlite.Connection, entry_id: str) -> JournalEntry | None:
    async with db.execute(
        "SELECT * FROM journal_entries WHERE id = ?", (entry_id,)
    ) as cur:
        row = await cur.fetchone()
        if not row:
            return None
        return JournalEntry(
            id=row["id"],
            entry_type=row["entry_type"],
            title=row["title"],
            content=row["content"],
            tags=json.loads(row["tags"]),
            created_at=row["created_at"],
        )


async def get_recent_summary(db: aiosqlite.Connection, limit: int = 10) -> str:
    """Render recent journal entries as text for prompt injection."""
    entries = await list_entries(db, limit=limit)
    if not entries:
        return "## Learning Journal\n\n(No entries yet.)\n"
    lines = ["## Recent Learning Journal Entries\n"]
    for e in entries:
        icon = {"learning": "L", "pivot": "P", "decision": "D", "milestone": "M",
                "interview": "I", "experiment": "E"}.get(e.entry_type, "?")
        lines.append(f"[{icon}] **{e.title}** ({e.created_at})")
        lines.append(f"    {e.content[:200]}")
        lines.append("")
    return "\n".join(lines)


async def get_phase(db: aiosqlite.Connection) -> str:
    async with db.execute(
        "SELECT value FROM project_state WHERE key = 'phase'"
    ) as cur:
        row = await cur.fetchone()
        return row["value"] if row else "discovery"


async def set_phase(db: aiosqlite.Connection, phase: str) -> None:
    await db.execute(
        "INSERT OR REPLACE INTO project_state (key, value, updated_at) VALUES ('phase', ?, datetime('now'))",
        (phase,),
    )
    await db.commit()
