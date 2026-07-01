import { useState, useEffect } from "react";
import { Plus, Check, X, AlertTriangle } from "lucide-react";
import {
  getCanvas,
  createHypothesis,
  updateHypothesis,
  deleteHypothesis,
} from "@/api/client";

const BLOCK_LABELS: Record<string, string> = {
  problem: "Problem",
  solution: "Solution",
  unique_value_proposition: "Unique Value Proposition",
  unfair_advantage: "Unfair Advantage",
  customer_segments: "Customer Segments",
  cost_structure: "Cost Structure",
  revenue_streams: "Revenue Streams",
  channels: "Channels",
  key_metrics: "Key Metrics",
};

const LEAN_CANVAS_ROWS = [
  ["problem", "solution", "unique_value_proposition"],
  ["unfair_advantage", "channels", "customer_segments"],
  ["cost_structure", "revenue_streams", "key_metrics"],
];

const STATUS_STYLES: Record<string, string> = {
  untested: "border-gray-600 text-gray-400",
  testing: "border-yellow-600 text-yellow-400",
  validated: "border-green-600 text-green-400",
  invalidated: "border-red-600 text-red-400",
};

const STATUS_ICONS: Record<string, typeof Check> = {
  untested: AlertTriangle,
  testing: AlertTriangle,
  validated: Check,
  invalidated: X,
};

export default function CanvasPage() {
  const [blocks, setBlocks] = useState<any[]>([]);
  const [adding, setAdding] = useState<string | null>(null);
  const [newStatement, setNewStatement] = useState("");

  const load = async () => {
    const res = await getCanvas();
    setBlocks(res.blocks);
  };

  useEffect(() => { load(); }, []);

  const handleAddHypothesis = async (blockId: string) => {
    if (!newStatement.trim()) return;
    await createHypothesis({ canvas_block: blockId, statement: newStatement.trim() });
    setNewStatement("");
    setAdding(null);
    load();
  };

  const cycleStatus = async (h: any) => {
    const order = ["untested", "testing", "validated", "invalidated"];
    const next = order[(order.indexOf(h.status) + 1) % order.length];
    await updateHypothesis(h.id, { status: next });
    load();
  };

  const handleDelete = async (id: string) => {
    await deleteHypothesis(id);
    load();
  };

  const renderBlock = (blockId: string) => {
    const block = blocks.find((b) => b.id === blockId);
    if (!block) return null;
    return (
      <div key={blockId} className="card flex flex-col gap-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          {BLOCK_LABELS[blockId]}
        </h3>
        {block.content && (
          <p className="text-xs text-gray-400 whitespace-pre-wrap">{block.content}</p>
        )}
        <div className="flex-1 space-y-1.5">
          {block.hypotheses.map((h: any) => {
            const Icon = STATUS_ICONS[h.status] || AlertTriangle;
            return (
              <div
                key={h.id}
                className={`flex items-start gap-2 rounded-lg border px-2.5 py-1.5 text-xs ${STATUS_STYLES[h.status]}`}
              >
                <button onClick={() => cycleStatus(h)} title="Cycle status" className="mt-0.5 shrink-0">
                  <Icon size={12} />
                </button>
                <span className="flex-1">{h.statement}</span>
                <button onClick={() => handleDelete(h.id)} className="shrink-0 text-gray-600 hover:text-red-400">
                  <X size={12} />
                </button>
              </div>
            );
          })}
        </div>
        {adding === blockId ? (
          <div className="flex gap-1">
            <input
              value={newStatement}
              onChange={(e) => setNewStatement(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddHypothesis(blockId)}
              placeholder="Hypothesis..."
              className="input flex-1 text-xs"
              autoFocus
            />
            <button onClick={() => handleAddHypothesis(blockId)} className="btn-primary text-xs px-2">+</button>
            <button onClick={() => { setAdding(null); setNewStatement(""); }} className="btn-ghost text-xs px-2">
              <X size={12} />
            </button>
          </div>
        ) : (
          <button onClick={() => setAdding(blockId)} className="btn-ghost flex items-center gap-1 text-xs self-start">
            <Plus size={12} /> Add hypothesis
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-gray-800 px-6 py-3">
        <h1 className="text-lg font-semibold">Lean Canvas</h1>
        <p className="text-xs text-gray-500 mt-0.5">Click status icons to cycle: untested → testing → validated → invalidated</p>
      </header>
      <div className="flex-1 overflow-y-auto p-6 space-y-3">
        {LEAN_CANVAS_ROWS.map((row, i) => (
          <div key={i} className="grid grid-cols-3 gap-3">
            {row.map((id) => renderBlock(id))}
          </div>
        ))}
      </div>
    </div>
  );
}
