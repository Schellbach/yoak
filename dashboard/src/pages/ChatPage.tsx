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
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${e.message}` },
      ]);
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
      <header className="flex items-center justify-between border-b border-gray-800 px-6 py-3">
        <h1 className="text-lg font-semibold">Chat with Yoak</h1>
        <button onClick={handleReset} className="btn-ghost flex items-center gap-1">
          <RotateCcw size={14} /> Reset
        </button>
      </header>

      {workflow && (
        <div className="flex items-center gap-3 border-b border-gray-800 bg-yoak-950/30 px-6 py-2 text-sm">
          <span className="text-yoak-400 font-medium">
            {workflow.name.replace(/_/g, " ")}
          </span>
          <span className="text-gray-500">
            Step {workflow.current_step + 1}/{workflow.total_steps}: {workflow.step_name}
          </span>
          <div className="ml-auto flex gap-2">
            <button onClick={handleAdvance} className="btn-ghost flex items-center gap-1 text-xs">
              <ChevronRight size={12} /> Next Step
            </button>
            <button onClick={handleCancel} className="btn-ghost flex items-center gap-1 text-xs text-red-400">
              <X size={12} /> Cancel
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center text-gray-600">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-500 mb-2">Yoak</p>
              <p className="text-sm">Your AI cofounder is ready. Describe your startup idea, ask for advice, or start a workflow.</p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {["I have a startup idea", "Help me with customer discovery", "Review my product", "Am I default alive?"].map((q) => (
                  <button
                    key={q}
                    onClick={() => { setInput(q); }}
                    className="rounded-lg border border-gray-700 px-3 py-1.5 text-xs text-gray-400 hover:border-yoak-500 hover:text-yoak-300 transition"
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
              className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-yoak-600 text-white"
                  : "bg-gray-800 text-gray-200"
              }`}
            >
              <div className="prose whitespace-pre-wrap">{m.content}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-gray-800 px-4 py-3 text-sm text-gray-400">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="border-t border-gray-800 px-6 py-4">
        <form
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="flex gap-3"
        >
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
