"""Learning journal endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from yoak.api.deps import get_agent
from yoak.core.agent import Agent
from yoak.memory.journal import add_entry, get_entry, get_phase, list_entries, set_phase

router = APIRouter()


class JournalCreate(BaseModel):
    entry_type: str
    title: str
    content: str
    tags: list[str] = []


class PhaseUpdate(BaseModel):
    phase: str


@router.get("/journal")
async def list_journal(
    entry_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    agent: Agent = Depends(get_agent),
):
    db = await agent.get_db()
    entries = await list_entries(db, entry_type=entry_type, limit=limit, offset=offset)
    return {"entries": [e.to_dict() for e in entries]}


@router.post("/journal")
async def create_entry(body: JournalCreate, agent: Agent = Depends(get_agent)):
    db = await agent.get_db()
    eid = await add_entry(db, body.entry_type, body.title, body.content, body.tags)
    return {"id": eid}


@router.get("/journal/{entry_id}")
async def get_journal_entry(entry_id: str, agent: Agent = Depends(get_agent)):
    db = await agent.get_db()
    e = await get_entry(db, entry_id)
    if not e:
        raise HTTPException(404, "Entry not found")
    return e.to_dict()


@router.get("/phase")
async def current_phase(agent: Agent = Depends(get_agent)):
    db = await agent.get_db()
    phase = await get_phase(db)
    return {"phase": phase}


@router.put("/phase")
async def update_phase(body: PhaseUpdate, agent: Agent = Depends(get_agent)):
    db = await agent.get_db()
    await set_phase(db, body.phase)
    return {"status": "ok", "phase": body.phase}
