import pytest

from yoak.memory.canvas import LEAN_CANVAS_BLOCKS, get_canvas, migrate_legacy_canvas
from yoak.memory.hypotheses import create_hypothesis, list_hypotheses
from yoak.memory.store import get_db


@pytest.mark.asyncio
async def test_migrate_legacy_bmc_to_lean_canvas(tmp_path):
    db = await get_db(str(tmp_path / "test.db"))

    await db.execute(
        "INSERT INTO canvas_blocks (id, block_name, content) VALUES (?, ?, ?)",
        ("value_propositions", "Value Propositions", "Better harvests through genetics"),
    )
    await db.execute(
        "UPDATE canvas_blocks SET content = ? WHERE id = ?",
        ("Backyard growers", "customer_segments"),
    )
    await db.commit()
    await create_hypothesis(db, "value_propositions", "Growers want genetic lineage data")

    await migrate_legacy_canvas(db)

    blocks = await get_canvas(db)
    block_ids = {b.id for b in blocks}
    assert block_ids == {block_id for block_id, _ in LEAN_CANVAS_BLOCKS}
    assert "value_propositions" not in block_ids

    uvp = next(b for b in blocks if b.id == "unique_value_proposition")
    assert "Better harvests through genetics" in uvp.content
    assert blocks[0].id == "problem"

    hypotheses = await list_hypotheses(db)
    assert len(hypotheses) == 1
    assert hypotheses[0].canvas_block == "unique_value_proposition"
    await db.close()
