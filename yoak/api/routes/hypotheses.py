"""Hypothesis management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from yoak.api.deps import get_agent
from yoak.core.agent import Agent
from yoak.memory.hypotheses import (
    add_evidence,
    create_hypothesis,
    delete_hypothesis,
    get_hypothesis,
    list_hypotheses,
    update_hypothesis,
)

router = APIRouter()


class HypothesisCreate(BaseModel):
    canvas_block: str
    statement: str
    status: str = "untested"
    confidence: float = 0.0


class HypothesisUpdate(BaseModel):
    status: str | None = None
    confidence: float | None = None
    statement: str | None = None


class EvidenceAdd(BaseModel):
    source: str
    finding: str
    supports: bool


@router.get("/hypotheses")
async def list_all(
    canvas_block: str | None = None,
    status: str | None = None,
    agent: Agent = Depends(get_agent),
):
    db = await agent.get_db()
    results = await list_hypotheses(db, canvas_block=canvas_block, status=status)
    return {"hypotheses": [h.to_dict() for h in results]}


@router.post("/hypotheses")
async def create(body: HypothesisCreate, agent: Agent = Depends(get_agent)):
    db = await agent.get_db()
    hid = await create_hypothesis(
        db, body.canvas_block, body.statement, body.status, body.confidence
    )
    return {"id": hid}


@router.get("/hypotheses/{hypothesis_id}")
async def get_one(hypothesis_id: str, agent: Agent = Depends(get_agent)):
    db = await agent.get_db()
    h = await get_hypothesis(db, hypothesis_id)
    if not h:
        raise HTTPException(404, "Hypothesis not found")
    return h.to_dict()


@router.patch("/hypotheses/{hypothesis_id}")
async def update(
    hypothesis_id: str, body: HypothesisUpdate, agent: Agent = Depends(get_agent)
):
    db = await agent.get_db()
    await update_hypothesis(
        db, hypothesis_id, status=body.status, confidence=body.confidence, statement=body.statement
    )
    return {"status": "ok"}


@router.post("/hypotheses/{hypothesis_id}/evidence")
async def add_evidence_entry(
    hypothesis_id: str, body: EvidenceAdd, agent: Agent = Depends(get_agent)
):
    db = await agent.get_db()
    await add_evidence(
        db,
        hypothesis_id,
        {"source": body.source, "finding": body.finding, "supports": body.supports},
    )
    return {"status": "ok"}


@router.delete("/hypotheses/{hypothesis_id}")
async def delete(hypothesis_id: str, agent: Agent = Depends(get_agent)):
    db = await agent.get_db()
    await delete_hypothesis(db, hypothesis_id)
    return {"status": "ok"}
