import { useState, useEffect } from "react";
import { Plus, BookOpen, GitBranch, Lightbulb, Flag, Users, FlaskConical } from "lucide-react";
import { getJournal, createJournalEntry } from "@/api/client";

const TYPE_CONFIG: Record<string, { icon: typeof BookOpen; color: string; label: string }> = {
  learning: { icon: Lightbulb, color: "var(--gold)", label: "Learning" },
  pivot: { icon: GitBranch, color: "var(--rust)", label: "Pivot" },
  decision: { icon: Flag, color: "var(--moss)", label: "Decision" },
  milestone: { icon: Flag, color: "var(--mint)", label: "Milestone" },
  interview: { icon: Users, color: "var(--clay)", label: "Interview" },
  experiment: { icon: FlaskConical, color: "var(--gold-soft)", label: "Experiment" },
};

export default function JournalPage() {
  const [entries, setEntries] = useState<any[]>([]);
  const [filter, setFilter] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ entry_type: "learning", title: "", content: "" });

  const load = async () => {
    const res = await getJournal(filter ?? undefined);
    setEntries(res.entries);
  };

  useEffect(() => { load(); }, [filter]);

  const handleCreate = async () => {
    if (!form.title.trim() || !form.content.trim()) return;
    await createJournalEntry(form);
    setForm({ entry_type: "learning", title: "", content: "" });
    setShowForm(false);
    load();
  };

  return (
    <div className="flex h-full flex-col">
      <header className="page-header">
        <h1>Journal</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-1 text-xs">
          <Plus size={14} /> New Entry
        </button>
      </header>

      <div className="flex flex-wrap gap-2 border-b px-6 py-2" style={{ borderColor: "var(--line)" }}>
        <button type="button" onClick={() => setFilter(null)} className={`filter-chip ${!filter ? "active" : ""}`}>
          All
        </button>
        {Object.entries(TYPE_CONFIG).map(([key, { label }]) => (
          <button
            key={key}
            type="button"
            onClick={() => setFilter(key)}
            className={`filter-chip ${filter === key ? "active" : ""}`}
          >
            {label}
          </button>
        ))}
      </div>

      {showForm && (
        <div className="space-y-3 border-b px-6 py-4" style={{ borderColor: "var(--line)", background: "var(--surface-muted)" }}>
          <div className="flex gap-3">
            <select
              value={form.entry_type}
              onChange={(e) => setForm({ ...form, entry_type: e.target.value })}
              className="input text-xs"
            >
              {Object.entries(TYPE_CONFIG).map(([key, { label }]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Title"
              className="input flex-1 text-sm"
            />
          </div>
          <textarea
            value={form.content}
            onChange={(e) => setForm({ ...form, content: e.target.value })}
            placeholder="What did you learn?"
            className="input w-full text-sm"
            rows={3}
          />
          <div className="flex gap-2">
            <button type="button" onClick={handleCreate} className="btn-primary text-xs">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-ghost text-xs">Cancel</button>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-6 py-4">
        {entries.length === 0 ? (
          <p className="mt-8 text-center" style={{ color: "var(--muted)" }}>No entries yet. Start capturing your learnings.</p>
        ) : (
          <div className="space-y-3">
            {entries.map((e) => {
              const cfg = TYPE_CONFIG[e.entry_type] || TYPE_CONFIG.learning;
              const Icon = cfg.icon;
              return (
                <div
                  key={e.id}
                  className="card flex gap-3"
                  style={{ borderLeft: `3px solid ${cfg.color}` }}
                >
                  <div className="mt-0.5" style={{ color: cfg.color }}>
                    <Icon size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-baseline gap-2">
                      <h3 className="text-sm font-semibold" style={{ color: "var(--ink)" }}>{e.title}</h3>
                      <span className="text-xs" style={{ color: "var(--muted)" }}>{e.created_at}</span>
                    </div>
                    <p className="mt-1 whitespace-pre-wrap text-sm" style={{ color: "var(--muted)" }}>{e.content}</p>
                    {e.tags.length > 0 && (
                      <div className="mt-2 flex gap-1">
                        {e.tags.map((t: string) => (
                          <span key={t} className="tag">{t}</span>
                        ))}
                      </div>
                    )}
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
