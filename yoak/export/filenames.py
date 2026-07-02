"""Stable export paths and slug generation."""

from __future__ import annotations

import re
import unicodedata

from yoak.memory.canvas import LEAN_CANVAS_BLOCKS

BLOCK_ORDER = {block_id: index for index, (block_id, _) in enumerate(LEAN_CANVAS_BLOCKS, start=1)}


def slugify(text: str, *, max_len: int = 48) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if not slug:
        slug = "untitled"
    return slug[:max_len].rstrip("-")


def project_slug(name: str) -> str:
    return slugify(name, max_len=64) or "project"


def block_kebab(block_id: str) -> str:
    return block_id.replace("_", "-")


def hypothesis_export_id(db_id: str) -> str:
    return f"H-{db_id}"


def pivot_export_id(journal_id: str) -> str:
    return f"P-{journal_id}"


def hypothesis_filename(db_id: str, statement: str) -> str:
    return f"{hypothesis_export_id(db_id)}-{slugify(statement)}.md"


def pivot_filename(journal_id: str, title: str) -> str:
    return f"{pivot_export_id(journal_id)}-{slugify(title)}.md"


def block_filename(block_id: str, block_name: str) -> str:
    index = BLOCK_ORDER.get(block_id, 99)
    return f"{index:02d} {block_name}.md"


def block_wikilink(block_id: str, block_name: str) -> str:
    return f"[[canvas/{block_filename(block_id, block_name)}|{block_name}]]"


def hypothesis_wikilink(db_id: str, statement: str) -> str:
    return f"[[hypotheses/{hypothesis_filename(db_id, statement)}|{statement}]]"


def parse_export_id_from_frontmatter(frontmatter: dict) -> str | None:
    export_id = frontmatter.get("id")
    if isinstance(export_id, str) and export_id:
        return export_id
    return None
