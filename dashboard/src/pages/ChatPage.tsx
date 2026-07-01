import { useState, useRef, useEffect, useCallback } from "react";
import { Send, RotateCcw, ChevronRight, X } from "lucide-react";
import { postChat, resetChat, advanceWorkflow, cancelWorkflow } from "@/api/client";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [workflow, setWorkflow] = useState<any>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(scrollToBottom, [messages, scrollToBottom]);

  const handleSend = async () => {
    const msg = input.trim();
    if (!msg || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setLoading(true);
    try {
      const res = await postChat(msg);
      setMessages((prev) => [...prev, { role: "assistant", content: res.response }]);
      setWorkflow(res.workflow);
    } catch (e: any) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${e.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    await resetChat();
    setMessages([]);
    setWorkflow(null);
  };

  const handleAdvance = async () => {
    const res = await advanceWorkflow();
    setWorkflow(res.workflow);
  };

  const handleCancel = async () => {
    await cancelWorkflow();
    setWorkflow(null);
  };

  return (
    <div className="flex h-full flex-col">
      <header className="page-header">
        <h1>Chat</h1>
        <button onClick={handleReset} className="btn-ghost flex items-center gap-1 text-xs">
          <RotateCcw size={14} /> Reset
        </button>
      </header>

      {workflow && (
        <div
          className="flex items-center gap-3 border-b px-6 py-2 text-sm"
          style={{ borderColor: "var(--line)", background: "var(--chip-active-bg)" }}
        >
          <span className="font-extrabold capitalize" style={{ color: "var(--gold)" }}>
            {workflow.name.replace(/_/g, " ")}
          </span>
          <span style={{ color: "var(--muted)" }}>
            Step {workflow.current_step + 1}/{workflow.total_steps}: {workflow.step_name}
          </span>
          <div className="ml-auto flex gap-2">
            <button onClick={handleAdvance} className="btn-ghost flex items-center gap-1 text-xs">
              <ChevronRight size={12} /> Next Step
            </button>
            <button onClick={handleCancel} className="btn-ghost flex items-center gap-1 text-xs" style={{ color: "var(--rust)" }}>
              <X size={12} /> Cancel
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 space-y-4 overflow-y-auto px-6 py-4">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center">
            <div className="max-w-md text-center">
              <p className="mb-2 font-serif text-3xl tracking-tight" style={{ color: "var(--ink)" }}>Yoak</p>
              <p className="mb-4 text-sm font-semibold" style={{ color: "var(--muted)" }}>
                Your AI cofounder is ready. Describe your startup idea, ask for advice, or start a workflow.
              </p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {["I have a startup idea", "Help me with customer discovery", "Review my product", "Am I default alive?"].map((q) => (
                  <button
                    key={q}
                    type="button"
                    onClick={() => setInput(q)}
                    className="filter-chip"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className="max-w-[75%] rounded-[var(--radius-lg)] px-4 py-3 text-sm leading-relaxed"
              style={
                m.role === "user"
                  ? { background: "var(--ink)", color: "var(--paper)" }
                  : {
                      background: "var(--surface-elevated)",
                      color: "var(--ink)",
                      border: "1px solid var(--line)",
                      boxShadow: "0 10px 28px var(--card-shadow)",
                    }
              }
            >
              <div className="prose-brand whitespace-pre-wrap">{m.content}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div
              className="rounded-[var(--radius-lg)] px-4 py-3 text-sm"
              style={{ background: "var(--surface-muted)", color: "var(--muted)" }}
            >
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="border-t px-6 py-4" style={{ borderColor: "var(--line)", background: "var(--surface-muted)" }}>
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Talk to your cofounder..."
            className="input flex-1"
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()} className="btn-primary flex items-center gap-2">
            <Send size={16} /> Send
          </button>
        </form>
      </div>
    </div>
  );
}
