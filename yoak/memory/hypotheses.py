"""Hypothesis lifecycle tracking: untested → testing → validated/invalidated."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

import aiosqlite


@dataclass
class Hypothesis:
    id: str
    canvas_block: str
    statement: str
    status: str
    confidence: float
    evidence: list[dict]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "canvas_block": self.canvas_block,
            "statement": self.statement,
            "status": self.status,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


async def create_hypothesis(
    db: aiosqlite.Connection,
    canvas_block: str,
    statement: str,
    status: str = "untested",
    confidence: float = 0.0,
) -> str:
    hid = uuid.uuid4().hex[:12]
    await db.execute(
        """INSERT INTO hypotheses (id, canvas_block, statement, status, confidence, evidence)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (hid, canvas_block, statement, status, confidence, "[]"),
    )
    await db.commit()
    return hid


async def update_hypothesis(
    db: aiosqlite.Connection,
    hypothesis_id: str,
    *,
    status: str | None = None,
    confidence: float | None = None,
    statement: str | None = None,
) -> None:
    parts, params = [], []
    if status is not None:
        parts.append("status = ?")
        params.append(status)
    if confidence is not None:
        parts.append("confidence = ?")
        params.append(confidence)
    if statement is not None:
        parts.append("statement = ?")
        params.append(statement)
    if not parts:
        return
    parts.append("updated_at = datetime('now')")
    params.append(hypothesis_id)
    await db.execute(
        f"UPDATE hypotheses SET {', '.join(parts)} WHERE id = ?",
        params,
    )
    await db.commit()


async def add_evidence(
    db: aiosqlite.Connection, hypothesis_id: str, evidence_entry: dict
) -> None:
    async with db.execute(
        "SELECT evidence FROM hypotheses WHERE id = ?", (hypothesis_id,)
    ) as cur:
        row = await cur.fetchone()
        if not row:
            return
    current = json.loads(row["evidence"])
    current.append(evidence_entry)
    await db.execute(
        "UPDATE hypotheses SET evidence = ?, updated_at = datetime('now') WHERE id = ?",
        (json.dumps(current), hypothesis_id),
    )
    await db.commit()


async def list_hypotheses(
    db: aiosqlite.Connection, *, canvas_block: str | None = None, status: str | None = None
) -> list[Hypothesis]:
    query = "SELECT * FROM hypotheses WHERE 1=1"
    params: list = []
    if canvas_block:
        query += " AND canvas_block = ?"
        params.append(canvas_block)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"
    results = []
    async with db.execute(query, params) as cur:
        async for row in cur:
            results.append(
                Hypothesis(
                    id=row["id"],
                    canvas_block=row["canvas_block"],
                    statement=row["statement"],
                    status=row["status"],
                    confidence=row["confidence"],
                    evidence=json.loads(row["evidence"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
    return results


async def get_hypothesis(db: aiosqlite.Connection, hypothesis_id: str) -> Hypothesis | None:
    async with db.execute(
        "SELECT * FROM hypotheses WHERE id = ?", (hypothesis_id,)
    ) as cur:
        row = await cur.fetchone()
        if not row:
            return None
        return Hypothesis(
            id=row["id"],
            canvas_block=row["canvas_block"],
            statement=row["statement"],
            status=row["status"],
            confidence=row["confidence"],
            evidence=json.loads(row["evidence"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


async def delete_hypothesis(db: aiosqlite.Connection, hypothesis_id: str) -> None:
    await db.execute("DELETE FROM hypotheses WHERE id = ?", (hypothesis_id,))
    await db.commit()
