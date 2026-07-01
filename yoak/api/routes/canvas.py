"""Lean Canvas CRUD endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from yoak.api.deps import get_agent
from yoak.core.agent import Agent
from yoak.memory.canvas import get_canvas, update_block

router = APIRouter()


class BlockUpdate(BaseModel):
    content: str


@router.get("/canvas")
async def list_canvas(agent: Agent = Depends(get_agent)):
    db = await agent.get_db()
    blocks = await get_canvas(db)
    return {"blocks": [b.to_dict() for b in blocks]}


@router.put("/canvas/{block_id}")
async def update_canvas_block(
    block_id: str, body: BlockUpdate, agent: Agent = Depends(get_agent)
):
    db = await agent.get_db()
    await update_block(db, block_id, body.content)
    return {"status": "ok"}


@router.post("/canvas/reset")
async def reset_canvas(agent: Agent = Depends(get_agent)):
    await agent.reset_canvas()
    blocks = await get_canvas(await agent.get_db())
    return {"status": "ok", "blocks": [b.to_dict() for b in blocks]}
