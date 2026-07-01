"""Business Model Canvas — 9 hypothesis blocks with persistent state."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import aiosqlite


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
    lines = ["## Current Business Model Canvas\n"]
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
