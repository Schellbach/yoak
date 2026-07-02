import { useEffect, useState, type CSSProperties } from "react";
import { Plus, X, Check, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import {
  getHypotheses,
  createHypothesis,
  updateHypothesis,
  deleteHypothesis,
} from "@/api/client";
import { LEAN_CANVAS_FIELDS, blockLabel } from "@/lib/leanCanvas";

type Hypothesis = {
  id: string;
  canvas_block: string;
  statement: string;
  status: string;
  confidence: number;
  evidence: Array<{ source: string; finding: string; supports: boolean }>;
  created_at: string;
  updated_at: string;
};

const STATUS_FILTERS = [
  { id: null, label: "All" },
  { id: "untested", label: "Untested" },
  { id: "testing", label: "Testing" },
  { id: "validated", label: "Validated" },
  { id: "invalidated", label: "Invalidated" },
] as const;

const STATUS_STYLES: Record<string, CSSProperties> = {
  untested: { borderColor: "var(--line)", color: "var(--muted)" },
  testing: { borderColor: "var(--gold)", color: "var(--gold)" },
  validated: { borderColor: "var(--moss)", color: "var(--moss)" },
  invalidated: { borderColor: "var(--rust)", color: "var(--rust)" },
};

export default function HypothesesPage() {
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [blockFilter, setBlockFilter] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [form, setForm] = useState({ canvas_block: "problem", statement: "" });

  const load = async () => {
    const res = await getHypotheses(blockFilter ?? undefined, statusFilter ?? undefined);
    setHypotheses(res.hypotheses);
  };

  useEffect(() => {
    load();
  }, [statusFilter, blockFilter]);

  const cycleStatus = async (id: string, status: string) => {
    const order = ["untested", "testing", "validated", "invalidated"];
    const next = order[(order.indexOf(status) + 1) % order.length];
    await updateHypothesis(id, { status: next });
    load();
  };

  const handleCreate = async () => {
    if (!form.statement.trim()) return;
    await createHypothesis(form);
    setForm({ canvas_block: "problem", statement: "" });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    await deleteHypothesis(id);
    load();
  };

  return (
    <div className="flex h-full flex-col">
      <header className="page-header">
        <div>
          <h1>Hypotheses</h1>
          <p className="page-subhead mt-0.5">Testable beliefs linked to your Lean Canvas.</p>
        </div>
        <button
          type="button"
          onClick={() => setShowForm(!showForm)}
          className="btn-primary flex items-center gap-1 text-xs"
        >
          <Plus size={14} /> New Hypothesis
        </button>
      </header>

      <div className="flex flex-wrap items-center gap-2 border-b px-6 py-2" style={{ borderColor: "var(--line)" }}>
        {STATUS_FILTERS.map(({ id, label }) => (
          <button
            key={label}
            type="button"
            onClick={() => setStatusFilter(id)}
            className={`filter-chip ${statusFilter === id ? "active" : ""}`}
          >
            {label}
          </button>
        ))}
        <select
          value={blockFilter ?? ""}
          onChange={(e) => setBlockFilter(e.target.value || null)}
          className="input ml-auto text-xs"
        >
          <option value="">All blocks</option>
          {LEAN_CANVAS_FIELDS.map((f) => (
            <option key={f.id} value={f.id}>
              {f.label}
            </option>
          ))}
        </select>
      </div>

      {showForm && (
        <div
          className="space-y-3 border-b px-6 py-4"
          style={{ borderColor: "var(--line)", background: "var(--surface-muted)" }}
        >
          <div className="flex gap-3">
            <select
              value={form.canvas_block}
              onChange={(e) => setForm({ ...form, canvas_block: e.target.value })}
              className="input text-xs"
            >
              {LEAN_CANVAS_FIELDS.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.label}
                </option>
              ))}
            </select>
            <input
              value={form.statement}
              onChange={(e) => setForm({ ...form, statement: e.target.value })}
              placeholder="What do you believe that still needs testing?"
              className="input flex-1 text-sm"
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
          </div>
          <div className="flex gap-2">
            <button type="button" onClick={handleCreate} className="btn-primary text-xs">
              Save
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-ghost text-xs">
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-6 py-4">
        {hypotheses.length === 0 ? (
          <p className="mt-8 text-center" style={{ color: "var(--muted)" }}>
            No hypotheses yet. Add one here or let Yoak capture them from chat.
          </p>
        ) : (
          <div className="space-y-3">
            {hypotheses.map((h) => {
              const isOpen = expanded[h.id];
              const hasEvidence = h.evidence.length > 0;
              return (
                <div key={h.id} className="card">
                  <div className="flex items-start gap-3">
                    <button
                      type="button"
                      onClick={() => cycleStatus(h.id, h.status)}
                      className="lean-hypothesis mt-0.5 shrink-0 border px-2 py-1 text-[10px] font-extrabold uppercase tracking-wide"
                      style={STATUS_STYLES[h.status]}
                      title="Click to cycle status"
                    >
                      {h.status === "validated" ? <Check size={12} /> : <AlertTriangle size={12} />}
                      <span className="ml-1">{h.status}</span>
                    </button>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-baseline gap-2">
                        <span className="tag">{blockLabel(h.canvas_block)}</span>
                        <span className="text-xs" style={{ color: "var(--muted)" }}>
                          {Math.round(h.confidence * 100)}% confidence
                        </span>
                        <span className="text-xs" style={{ color: "var(--muted)" }}>
                          {h.updated_at}
                        </span>
                      </div>
                      <p className="mt-2 text-sm" style={{ color: "var(--ink)" }}>
                        {h.statement}
                      </p>
                      {hasEvidence && (
                        <button
                          type="button"
                          onClick={() => setExpanded((p) => ({ ...p, [h.id]: !p[h.id] }))}
                          className="mt-2 flex items-center gap-1 text-[10px] font-extrabold uppercase tracking-wide"
                          style={{ color: "var(--muted)" }}
                        >
                          {isOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                          {h.evidence.length} evidence {h.evidence.length === 1 ? "entry" : "entries"}
                        </button>
                      )}
                      {isOpen && hasEvidence && (
                        <div className="mt-2 space-y-2">
                          {h.evidence.map((ev, i) => (
                            <div
                              key={i}
                              className="rounded-[var(--radius-sm)] border px-3 py-2 text-xs"
                              style={{
                                borderColor: ev.supports ? "var(--moss)" : "var(--rust)",
                                color: "var(--muted)",
                              }}
                            >
                              <span className="font-semibold" style={{ color: "var(--ink)" }}>
                                {ev.source}
                              </span>
                              {" — "}
                              {ev.finding}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => handleDelete(h.id)}
                      className="btn-ghost shrink-0 px-2"
                      title="Delete hypothesis"
                    >
                      <X size={14} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
