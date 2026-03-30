"""Workflow management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from yoak.api.deps import get_agent
from yoak.core.agent import Agent
from yoak.workflows import WORKFLOW_REGISTRY

router = APIRouter()


class WorkflowStart(BaseModel):
    name: str


@router.get("/workflows")
async def list_workflows():
    return {
        "workflows": [
            {"name": name, "description": cls.description}
            for name, cls in WORKFLOW_REGISTRY.items()
        ]
    }


@router.get("/workflows/active")
async def active_workflow(agent: Agent = Depends(get_agent)):
    return {"workflow": agent.active_workflow}


@router.post("/workflows/start")
async def start_workflow(body: WorkflowStart, agent: Agent = Depends(get_agent)):
    ok = agent.start_workflow(body.name)
    if not ok:
        return {"status": "error", "message": f"Unknown workflow: {body.name}"}
    return {"status": "ok", "workflow": agent.active_workflow}


@router.post("/workflows/advance")
async def advance(agent: Agent = Depends(get_agent)):
    result = agent.advance_workflow()
    return {"status": result or "no active workflow", "workflow": agent.active_workflow}


@router.post("/workflows/cancel")
async def cancel(agent: Agent = Depends(get_agent)):
    agent.cancel_workflow()
    return {"status": "cancelled"}
