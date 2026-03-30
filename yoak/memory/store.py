"""SQLite-backed persistence layer for Yoak memory."""

from __future__ import annotations

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS canvas_blocks (
    id TEXT PRIMARY KEY,
    block_name TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT PRIMARY KEY,
    canvas_block TEXT NOT NULL,
    statement TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'untested',
    confidence REAL NOT NULL DEFAULT 0.0,
    evidence TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id TEXT PRIMARY KEY,
    entry_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT 'Untitled',
    workflow TEXT,
    workflow_state TEXT,
    messages TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS project_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_CANVAS_SEED = [
    ("customer_segments", "Customer Segments", ""),
    ("value_propositions", "Value Propositions", ""),
    ("channels", "Channels", ""),
    ("customer_relationships", "Customer Relationships", ""),
    ("revenue_streams", "Revenue Streams", ""),
    ("key_resources", "Key Resources", ""),
    ("key_activities", "Key Activities", ""),
    ("key_partners", "Key Partners", ""),
    ("cost_structure", "Cost Structure", ""),
]


async def get_db(db_path: str) -> aiosqlite.Connection:
    db = await aiosqlite.connect(db_path)
    db.row_factory = aiosqlite.Row
    await db.executescript(_SCHEMA)
    for block_id, name, content in _CANVAS_SEED:
        await db.execute(
            "INSERT OR IGNORE INTO canvas_blocks (id, block_name, content) VALUES (?, ?, ?)",
            (block_id, name, content),
        )
    await db.execute(
        "INSERT OR IGNORE INTO project_state (key, value) VALUES (?, ?)",
        ("phase", "discovery"),
    )
    await db.commit()
    return db
