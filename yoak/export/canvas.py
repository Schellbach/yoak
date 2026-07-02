"""JSON Canvas builder for Lean Canvas layout."""

from __future__ import annotations

import json

from yoak.export.filenames import block_filename
from yoak.export.writers import block_health_color
from yoak.memory.canvas import LEAN_CANVAS_BLOCKS, CanvasBlock
from yoak.memory.hypotheses import Hypothesis


def _file_node(
    node_id: str,
    file_path: str,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
    color: str | None,
) -> dict:
    node = {
        "id": node_id,
        "type": "file",
        "file": file_path,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
    }
    if color:
        node["color"] = color
    return node


def build_canvas_json(
    blocks: list[CanvasBlock],
    hypotheses_by_block: dict[str, list[Hypothesis]],
) -> str:
    block_by_id = {block.id: block for block in blocks}
    nodes: list[dict] = []

    layout = {
        "problem": (0, 0, 260, 520),
        "solution": (280, 0, 260, 250),
        "key_metrics": (280, 270, 260, 250),
        "unique_value_proposition": (560, 0, 260, 520),
        "unfair_advantage": (840, 0, 260, 250),
        "channels": (840, 270, 260, 250),
        "customer_segments": (1120, 0, 260, 520),
        "cost_structure": (0, 540, 690, 220),
        "revenue_streams": (710, 540, 670, 220),
    }

    for block_id, block_name in LEAN_CANVAS_BLOCKS:
        block = block_by_id.get(block_id)
        if not block:
            continue
        x, y, width, height = layout[block_id]
        hyps = hypotheses_by_block.get(block_id, [])
        color = block_health_color(hyps)
        rel = f"canvas/{block_filename(block_id, block_name)}"
        nodes.append(
            _file_node(
                f"block-{block_id}",
                rel,
                x=x,
                y=y,
                width=width,
                height=height,
                color=color,
            )
        )

    payload = {"nodes": nodes, "edges": []}
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
