from __future__ import annotations

import json
from pathlib import Path

import pytest

from yoak.export.filenames import (
    hypothesis_export_id,
    hypothesis_filename,
    project_slug,
)
from yoak.export.frontmatter import dump_frontmatter, read_frontmatter
from yoak.export.runner import build_export_files, export_to_vault
from yoak.memory.canvas import update_block
from yoak.memory.hypotheses import create_hypothesis, delete_hypothesis, update_hypothesis
from yoak.memory.journal import add_entry
from yoak.memory.store import get_db

EXPORT_DATE = "2026-07-02"
PROJECT_NAME = "Mango Trees"
PROJECT_ID = "mango-trees"


@pytest.fixture
async def db(tmp_path):
    database = await get_db(str(tmp_path / "export.db"))
    yield database
    await database.close()


async def seed_export_db(db) -> dict[str, str]:
    await update_block(db, "problem", "Home growers lack reliable variety information.")
    await update_block(db, "customer_segments", "Backyard orchard owners with 3-10 trees.")

    h_untested = await create_hypothesis(
        db, "customer_segments", 'Owners say: "I don\'t know what [[variety]] I have."'
    )
    h_testing = await create_hypothesis(db, "problem", "Pain is severe enough to switch tools.")
    h_invalid = await create_hypothesis(db, "channels", "Facebook groups reach this segment.")

    await db.execute(
        "UPDATE hypotheses SET created_at = ?, updated_at = ? WHERE id = ?",
        ("2026-06-10 09:00:00", "2026-06-10 09:00:00", h_untested),
    )
    await db.execute(
        "UPDATE hypotheses SET created_at = ?, updated_at = ? WHERE id = ?",
        ("2026-06-11 10:00:00", "2026-06-18 11:00:00", h_testing),
    )
    await db.execute(
        "UPDATE hypotheses SET created_at = ?, updated_at = ? WHERE id = ?",
        ("2026-06-12 12:00:00", "2026-06-28 15:00:00", h_invalid),
    )
    await update_hypothesis(db, h_testing, status="testing")
    await update_hypothesis(db, h_invalid, status="invalidated")
    await db.commit()

    learning_id = await add_entry(
        db,
        "learning",
        "Interview notes",
        "Grower confirmed confusion about scion lineage.",
        tags=[f"hypothesis:{h_untested}"],
    )
    await db.execute(
        "UPDATE journal_entries SET created_at = ? WHERE id = ?",
        ("2026-06-20 14:30:00", learning_id),
    )
    await add_entry(
        db,
        "experiment",
        "Landing page test",
        "Posted in local orchard group.",
    )
    await db.execute(
        "UPDATE journal_entries SET created_at = ? WHERE id = (SELECT id FROM journal_entries WHERE title = ?)",
        ("2026-06-21 09:15:00", "Landing page test"),
    )
    pivot_id = await add_entry(
        db,
        "pivot",
        "Focus on premium pedigree trees",
        "Shift from all growers to premium-focused owners.",
        tags=[f"hypothesis:{h_invalid}"],
    )
    await db.execute(
        "UPDATE journal_entries SET created_at = ? WHERE id = ?",
        ("2026-06-29 16:00:00", pivot_id),
    )
    await db.commit()
    return {
        "untested": h_untested,
        "testing": h_testing,
        "invalidated": h_invalid,
        "pivot": pivot_id,
    }


def test_frontmatter_serializes_special_characters():
    fields = {
        "yoak_managed": True,
        "id": "H-abc123",
        "type": "hypothesis",
        "block": "customer-segments",
        "status": "testing",
        "confidence": 0.4,
        "created": "2026-06-12",
        "updated": "2026-06-28",
        "exported": EXPORT_DATE,
        "tags": ["yoak/hypothesis"],
        "title": 'Quote: " [[ ]] : test',
    }
    rendered = dump_frontmatter(fields)
    parsed, _ = read_frontmatter(rendered)
    assert parsed is not None
    assert parsed["title"] == 'Quote: " [[ ]] : test'
    assert rendered.startswith("---\n")


def test_filename_generation_is_id_stable():
    db_id = "abc123def456"
    statement = 'Owners say: "emoji 🥭" :: [[bad]]'
    first = hypothesis_filename(db_id, statement)
    second = hypothesis_filename(db_id, statement)
    assert first == second
    assert first.startswith(f"{hypothesis_export_id(db_id)}-")


def test_project_slug():
    assert project_slug("Mango Trees") == "mango-trees"


@pytest.mark.asyncio
async def test_export_is_idempotent(db, tmp_path):
    await seed_export_db(db)
    vault = tmp_path / "vault"
    first = await export_to_vault(
        db,
        vault,
        project_name=PROJECT_NAME,
        project_id=PROJECT_ID,
        exported=EXPORT_DATE,
        force=True,
    )
    second = await export_to_vault(
        db,
        vault,
        project_name=PROJECT_NAME,
        project_id=PROJECT_ID,
        exported=EXPORT_DATE,
        force=True,
    )
    assert first.output_dir == second.output_dir

    def tree_bytes(root: Path) -> dict[str, bytes]:
        payload: dict[str, bytes] = {}
        for path in sorted(root.rglob("*")):
            if path.is_file():
                payload[str(path.relative_to(root))] = path.read_bytes()
        return payload

    assert tree_bytes(first.output_dir) == tree_bytes(second.output_dir)


@pytest.mark.asyncio
async def test_overwrite_protection_skips_unmanaged_file(db, tmp_path):
    await seed_export_db(db)
    vault = tmp_path / "vault"
    output_dir = vault / "yoak" / PROJECT_ID
    output_dir.mkdir(parents=True)
    canvas_dir = output_dir / "canvas"
    canvas_dir.mkdir(parents=True)
    protected = canvas_dir / "01 Problem.md"
    protected.write_text("# My manual note\n", encoding="utf-8")

    result = await export_to_vault(
        db,
        vault,
        project_name=PROJECT_NAME,
        project_id=PROJECT_ID,
        exported=EXPORT_DATE,
        force=True,
    )
    assert protected.read_text(encoding="utf-8") == "# My manual note\n"
    assert "canvas/01 Problem.md" in result.files_skipped
    assert any("Skipped unmanaged" in warning for warning in result.warnings)


@pytest.mark.asyncio
async def test_stale_hypothesis_file_removed(db, tmp_path):
    ids = await seed_export_db(db)
    vault = tmp_path / "vault"
    await export_to_vault(
        db,
        vault,
        project_name=PROJECT_NAME,
        project_id=PROJECT_ID,
        exported=EXPORT_DATE,
        force=True,
    )
    stale_name = hypothesis_filename(ids["untested"], 'Owners say: "I don\'t know what [[variety]] I have."')
    stale_path = vault / "yoak" / PROJECT_ID / "hypotheses" / stale_name
    assert stale_path.exists()

    await delete_hypothesis(db, ids["untested"])
    result = await export_to_vault(
        db,
        vault,
        project_name=PROJECT_NAME,
        project_id=PROJECT_ID,
        exported=EXPORT_DATE,
        force=True,
    )
    assert not stale_path.exists()
    assert any(stale_name in deleted for deleted in result.files_deleted)


@pytest.mark.asyncio
async def test_canvas_output_has_nine_file_nodes(db, tmp_path):
    await seed_export_db(db)
    files, _, _, canvas_files = await build_export_files(
        db,
        project_name=PROJECT_NAME,
        project_id=PROJECT_ID,
        exported=EXPORT_DATE,
    )
    canvas_name = next(iter(canvas_files))
    payload = json.loads(files[canvas_name])
    file_nodes = [node for node in payload["nodes"] if node["type"] == "file"]
    assert len(file_nodes) == 9
    assert payload["edges"] == []


@pytest.mark.asyncio
async def test_integration_snapshot_tree(db, tmp_path):
    ids = await seed_export_db(db)
    vault = tmp_path / "vault"
    result = await export_to_vault(
        db,
        vault,
        project_name=PROJECT_NAME,
        project_id=PROJECT_ID,
        exported=EXPORT_DATE,
        force=True,
    )

    rel_paths = sorted(
        str(path.relative_to(result.output_dir))
        for path in result.output_dir.rglob("*")
        if path.is_file()
    )
    assert rel_paths[0] == "Dashboard.md"
    assert f"{PROJECT_ID}.canvas" in rel_paths
    assert len([p for p in rel_paths if p.startswith("canvas/")]) == 9
    assert len([p for p in rel_paths if p.startswith("hypotheses/")]) == 3
    assert len([p for p in rel_paths if p.startswith("journal/")]) == 2
    assert len([p for p in rel_paths if p.startswith("pivots/")]) == 1

    dashboard = (result.output_dir / "Dashboard.md").read_text(encoding="utf-8")
    assert "yoak_managed: true" in dashboard
    assert "## Hypothesis status" in dashboard

    hypothesis_path = result.output_dir / "hypotheses" / hypothesis_filename(
        ids["testing"], "Pain is severe enough to switch tools."
    )
    hypothesis_text = hypothesis_path.read_text(encoding="utf-8")
    assert "## History" in hypothesis_text
    assert "status set to **testing**" in hypothesis_text

    pivot_files = list((result.output_dir / "pivots").glob("*.md"))
    assert len(pivot_files) == 1
    assert "## Triggered by" in pivot_files[0].read_text(encoding="utf-8")

    canvas_payload = json.loads((result.output_dir / f"{PROJECT_ID}.canvas").read_text(encoding="utf-8"))
    assert len([n for n in canvas_payload["nodes"] if n["type"] == "file"]) == 9
