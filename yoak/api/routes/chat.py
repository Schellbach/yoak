"""Chat endpoints — REST and WebSocket."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from yoak.api.deps import get_agent
from yoak.core.agent import Agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    auto_route: bool = True


class ChatResponse(BaseModel):
    response: str
    workflow: dict | None = None
    workflow_event: str | None = None
    routed_to: str | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, agent: Agent = Depends(get_agent)):
    routed = None
    if req.auto_route:
        routed = await agent.auto_route(req.message)

    response = await agent.chat(req.message)
    return ChatResponse(
        response=response,
        workflow=agent.active_workflow,
        workflow_event=agent.last_workflow_event,
        routed_to=routed,
    )


@router.post("/chat/reset")
async def reset_chat_endpoint(agent: Agent = Depends(get_agent)):
    await agent.reset_chat()
    return {"status": "ok"}


@router.get("/chat/history")
async def chat_history(agent: Agent = Depends(get_agent)):
    return {"messages": agent.conversation_history}


@router.post("/chat/workflow/advance")
async def advance_workflow(agent: Agent = Depends(get_agent)):
    result = agent.advance_workflow()
    return {"status": result or "no active workflow", "workflow": agent.active_workflow}


@router.post("/chat/workflow/cancel")
async def cancel_workflow(agent: Agent = Depends(get_agent)):
    agent.cancel_workflow()
    return {"status": "cancelled"}


@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    await websocket.accept()
    agent: Agent = websocket.app.state.agent

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            message = payload.get("message", "")

            if payload.get("auto_route", True):
                routed = await agent.auto_route(message)
                if routed:
                    await websocket.send_json(
                        {"type": "workflow_started", "workflow": agent.active_workflow}
                    )

            async for chunk in agent.chat_stream(message):
                await websocket.send_json({"type": "chunk", "delta": chunk.delta})
                if chunk.finish_reason:
                    await websocket.send_json({
                        "type": "done",
                        "finish_reason": chunk.finish_reason,
                        "workflow": agent.active_workflow,
                        "workflow_event": agent.last_workflow_event,
                    })
    except WebSocketDisconnect:
        pass
