import { useState, useEffect } from "react";
import { Plus, BookOpen, GitBranch, Lightbulb, Flag, Users, FlaskConical } from "lucide-react";
import { getJournal, createJournalEntry } from "@/api/client";

const TYPE_CONFIG: Record<string, { icon: typeof BookOpen; color: string; label: string }> = {
  learning: { icon: Lightbulb, color: "text-yellow-400", label: "Learning" },
  pivot: { icon: GitBranch, color: "text-red-400", label: "Pivot" },
  decision: { icon: Flag, color: "text-blue-400", label: "Decision" },
  milestone: { icon: Flag, color: "text-green-400", label: "Milestone" },
  interview: { icon: Users, color: "text-purple-400", label: "Interview" },
  experiment: { icon: FlaskConical, color: "text-orange-400", label: "Experiment" },
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
      <header className="flex items-center justify-between border-b border-gray-800 px-6 py-3">
        <h1 className="text-lg font-semibold">Learning Journal</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-1 text-xs">
          <Plus size={14} /> New Entry
        </button>
      </header>

      <div className="flex gap-2 border-b border-gray-800 px-6 py-2">
        <button
          onClick={() => setFilter(null)}
          className={`btn-ghost text-xs ${!filter ? "text-yoak-400" : ""}`}
        >
          All
        </button>
        {Object.entries(TYPE_CONFIG).map(([key, { label }]) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`btn-ghost text-xs ${filter === key ? "text-yoak-400" : ""}`}
          >
            {label}
          </button>
        ))}
      </div>

      {showForm && (
        <div className="border-b border-gray-800 bg-gray-900/50 px-6 py-4 space-y-3">
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
            <button onClick={handleCreate} className="btn-primary text-xs">Save</button>
            <button onClick={() => setShowForm(false)} className="btn-ghost text-xs">Cancel</button>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-6 py-4">
        {entries.length === 0 ? (
          <p className="text-center text-gray-600 mt-8">No entries yet. Start capturing your learnings.</p>
        ) : (
          <div className="space-y-3">
            {entries.map((e) => {
              const cfg = TYPE_CONFIG[e.entry_type] || TYPE_CONFIG.learning;
              const Icon = cfg.icon;
              return (
                <div key={e.id} className="card flex gap-3">
                  <div className={`mt-0.5 ${cfg.color}`}>
                    <Icon size={18} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline gap-2">
                      <h3 className="font-medium text-sm">{e.title}</h3>
                      <span className="text-xs text-gray-600">{e.created_at}</span>
                    </div>
                    <p className="text-sm text-gray-400 mt-1 whitespace-pre-wrap">{e.content}</p>
                    {e.tags.length > 0 && (
                      <div className="flex gap-1 mt-2">
                        {e.tags.map((t: string) => (
                          <span key={t} className="rounded bg-gray-800 px-1.5 py-0.5 text-xs text-gray-500">{t}</span>
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
