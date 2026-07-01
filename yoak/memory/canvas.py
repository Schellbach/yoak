"""Lean Canvas — 9 hypothesis blocks with persistent state."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import aiosqlite

LEAN_CANVAS_BLOCKS: list[tuple[str, str]] = [
    ("problem", "Problem"),
    ("solution", "Solution"),
    ("unique_value_proposition", "Unique Value Proposition"),
    ("unfair_advantage", "Unfair Advantage"),
    ("customer_segments", "Customer Segments"),
    ("cost_structure", "Cost Structure"),
    ("revenue_streams", "Revenue Streams"),
    ("channels", "Channels"),
    ("key_metrics", "Key Metrics"),
]

VALID_CANVAS_BLOCK_IDS = frozenset(block_id for block_id, _ in LEAN_CANVAS_BLOCKS)

_BLOCK_ORDER = {block_id: index for index, (block_id, _) in enumerate(LEAN_CANVAS_BLOCKS)}

_LEGACY_BLOCK_MAP = {
    "value_propositions": "unique_value_proposition",
    "customer_relationships": "channels",
    "key_partners": "unfair_advantage",
    "key_resources": "unfair_advantage",
    "key_activities": "solution",
}


@dataclass
class CanvasBlock:
    id: str
    block_name: str
    content: str
    updated_at: str
    hypotheses: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "block_name": self.block_name,
            "content": self.content,
            "updated_at": self.updated_at,
            "hypotheses": self.hypotheses,
        }


async def _merge_block_content(
    db: aiosqlite.Connection, source_id: str, target_id: str
) -> None:
    async with db.execute(
        "SELECT content FROM canvas_blocks WHERE id = ?", (source_id,)
    ) as cur:
        row = await cur.fetchone()
        if not row or not row["content"].strip():
            return
    source_content = row["content"].strip()
    async with db.execute(
        "SELECT content FROM canvas_blocks WHERE id = ?", (target_id,)
    ) as cur:
        target_row = await cur.fetchone()
    target_content = (target_row["content"] or "").strip() if target_row else ""
    merged = source_content if not target_content else f"{target_content}\n{source_content}"
    await db.execute(
        "UPDATE canvas_blocks SET content = ?, updated_at = datetime('now') WHERE id = ?",
        (merged, target_id),
    )


async def migrate_legacy_canvas(db: aiosqlite.Connection) -> None:
    """Migrate Business Model Canvas blocks to Lean Canvas."""
    for old_id, new_id in _LEGACY_BLOCK_MAP.items():
        await _merge_block_content(db, old_id, new_id)
        await db.execute(
            "UPDATE hypotheses SET canvas_block = ? WHERE canvas_block = ?",
            (new_id, old_id),
        )

    valid_ids = tuple(VALID_CANVAS_BLOCK_IDS)
    placeholders = ",".join("?" * len(valid_ids))
    await db.execute(
        f"DELETE FROM canvas_blocks WHERE id NOT IN ({placeholders})",
        valid_ids,
    )

    for block_id, name in LEAN_CANVAS_BLOCKS:
        await db.execute(
            "INSERT OR IGNORE INTO canvas_blocks (id, block_name, content) VALUES (?, ?, ?)",
            (block_id, name, ""),
        )
        await db.execute(
            "UPDATE canvas_blocks SET block_name = ? WHERE id = ?",
            (name, block_id),
        )
    await db.commit()


async def get_canvas(db: aiosqlite.Connection) -> list[CanvasBlock]:
    blocks = []
    async with db.execute("SELECT * FROM canvas_blocks ORDER BY rowid") as cur:
        async for row in cur:
            block = CanvasBlock(
                id=row["id"],
                block_name=row["block_name"],
                content=row["content"],
                updated_at=row["updated_at"],
            )
            async with db.execute(
                "SELECT * FROM hypotheses WHERE canvas_block = ? ORDER BY created_at",
                (row["id"],),
            ) as hcur:
                async for hrow in hcur:
                    block.hypotheses.append(
                        {
                            "id": hrow["id"],
                            "statement": hrow["statement"],
                            "status": hrow["status"],
                            "confidence": hrow["confidence"],
                            "evidence": json.loads(hrow["evidence"]),
                            "created_at": hrow["created_at"],
                            "updated_at": hrow["updated_at"],
                        }
                    )
            blocks.append(block)
    blocks.sort(key=lambda b: _BLOCK_ORDER.get(b.id, 999))
    return blocks


async def update_block(db: aiosqlite.Connection, block_id: str, content: str) -> None:
    await db.execute(
        "UPDATE canvas_blocks SET content = ?, updated_at = datetime('now') WHERE id = ?",
        (content, block_id),
    )
    await db.commit()


async def clear_canvas(db: aiosqlite.Connection) -> None:
    """Reset all canvas block content and remove attached hypotheses."""
    await db.execute("UPDATE canvas_blocks SET content = '', updated_at = datetime('now')")
    await db.execute("DELETE FROM hypotheses")
    await db.commit()


def canvas_summary(blocks: list[CanvasBlock]) -> str:
    """Render the canvas as a concise text summary for prompt injection."""
    lines = ["## Current Lean Canvas\n"]
    for b in blocks:
        lines.append(f"### {b.block_name}")
        if b.content:
            lines.append(b.content)
        if b.hypotheses:
            for h in b.hypotheses:
                status_icon = {
                    "untested": "?",
                    "testing": "~",
                    "validated": "+",
                    "invalidated": "x",
                }.get(h["status"], "?")
                lines.append(f"  [{status_icon}] {h['statement']} (confidence: {h['confidence']:.0%})")
        elif not b.content:
            lines.append("  (empty)")
        lines.append("")
    return "\n".join(lines)
