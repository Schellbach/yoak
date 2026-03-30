const BASE = "/api";

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// Chat
export const postChat = (message: string) =>
  request<{ response: string; workflow: any; routed_to: string | null }>("/chat", {
    method: "POST",
    body: JSON.stringify({ message, auto_route: true }),
  });

export const resetChat = () => request("/chat/reset", { method: "POST" });
export const getChatHistory = () => request<{ messages: any[] }>("/chat/history");
export const advanceWorkflow = () => request<{ status: string; workflow: any }>("/chat/workflow/advance", { method: "POST" });
export const cancelWorkflow = () => request("/chat/workflow/cancel", { method: "POST" });

// Canvas
export const getCanvas = () => request<{ blocks: any[] }>("/canvas");
export const updateCanvasBlock = (id: string, content: string) =>
  request(`/canvas/${id}`, { method: "PUT", body: JSON.stringify({ content }) });

// Hypotheses
export const getHypotheses = (block?: string, status?: string) => {
  const params = new URLSearchParams();
  if (block) params.set("canvas_block", block);
  if (status) params.set("status", status);
  return request<{ hypotheses: any[] }>(`/hypotheses?${params}`);
};
export const createHypothesis = (data: { canvas_block: string; statement: string }) =>
  request<{ id: string }>("/hypotheses", { method: "POST", body: JSON.stringify(data) });
export const updateHypothesis = (id: string, data: any) =>
  request(`/hypotheses/${id}`, { method: "PATCH", body: JSON.stringify(data) });
export const deleteHypothesis = (id: string) =>
  request(`/hypotheses/${id}`, { method: "DELETE" });
export const addEvidence = (id: string, data: { source: string; finding: string; supports: boolean }) =>
  request(`/hypotheses/${id}/evidence`, { method: "POST", body: JSON.stringify(data) });

// Journal
export const getJournal = (type?: string, limit = 50) => {
  const params = new URLSearchParams({ limit: String(limit) });
  if (type) params.set("entry_type", type);
  return request<{ entries: any[] }>(`/journal?${params}`);
};
export const createJournalEntry = (data: { entry_type: string; title: string; content: string; tags?: string[] }) =>
  request<{ id: string }>("/journal", { method: "POST", body: JSON.stringify(data) });

// Phase
export const getPhase = () => request<{ phase: string }>("/phase");
export const setPhase = (phase: string) =>
  request("/phase", { method: "PUT", body: JSON.stringify({ phase }) });

// Workflows
export const getWorkflows = () => request<{ workflows: any[] }>("/workflows");
export const getActiveWorkflow = () => request<{ workflow: any }>("/workflows/active");
export const startWorkflow = (name: string) =>
  request("/workflows/start", { method: "POST", body: JSON.stringify({ name }) });

// Config
export const getConfig = () => request<{ config: any }>("/config");
export const setConfig = (key: string, value: any) =>
  request("/config", { method: "PUT", body: JSON.stringify({ key, value }) });

// WebSocket chat
export function connectChat(
  onChunk: (delta: string) => void,
  onDone: (workflow: any) => void,
  onWorkflowStarted?: (name: string) => void
): { send: (message: string) => void; close: () => void } {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "chunk") onChunk(data.delta);
    else if (data.type === "done") onDone(data.workflow);
    else if (data.type === "workflow_started") onWorkflowStarted?.(data.workflow);
  };

  return {
    send: (message: string) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ message, auto_route: true }));
      }
    },
    close: () => ws.close(),
  };
}
