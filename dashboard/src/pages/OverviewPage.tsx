import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Search,
  CheckCircle,
  Megaphone,
  Building,
} from "lucide-react";
import { getPhase, getHypotheses, getJournal, getActiveWorkflow } from "@/api/client";

const PHASE_CONFIG = [
  { id: "discovery", label: "Discovery", icon: Search, description: "Testing problem-solution fit", accent: "var(--gold)" },
  { id: "validation", label: "Validation", icon: CheckCircle, description: "Proving repeatable sales", accent: "var(--moss)" },
  { id: "creation", label: "Creation", icon: Megaphone, description: "Driving demand at scale", accent: "var(--rust)" },
  { id: "building", label: "Building", icon: Building, description: "Scaling the company", accent: "var(--clay)" },
];

export default function OverviewPage() {
  const [phase, setPhase] = useState("discovery");
  const [hypothesisCounts, setHypothesisCounts] = useState({ untested: 0, testing: 0, validated: 0, invalidated: 0 });
  const [journalCount, setJournalCount] = useState(0);
  const [activeWorkflow, setActiveWorkflow] = useState<any>(null);
  const [recentEntries, setRecentEntries] = useState<any[]>([]);

  useEffect(() => {
    (async () => {
      const [phaseRes, hypoRes, journalRes, wfRes] = await Promise.all([
        getPhase(),
        getHypotheses(),
        getJournal(undefined, 5),
        getActiveWorkflow(),
      ]);
      setPhase(phaseRes.phase);
      setJournalCount(journalRes.entries.length);
      setRecentEntries(journalRes.entries);
      setActiveWorkflow(wfRes.workflow);

      const counts = { untested: 0, testing: 0, validated: 0, invalidated: 0 };
      for (const h of hypoRes.hypotheses) {
        counts[h.status as keyof typeof counts]++;
      }
      setHypothesisCounts(counts);
    })();
  }, []);

  const total = Object.values(hypothesisCounts).reduce((a, b) => a + b, 0);
  const currentPhaseIndex = PHASE_CONFIG.findIndex((x) => x.id === phase);

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <header className="page-header">
        <div>
          <h1>Overview</h1>
          <p className="page-subhead mt-0.5">Track phase, hypotheses, and workflow progress.</p>
        </div>
      </header>

      <div className="space-y-6 p-6">
        <div className="card card-accent-top pt-5">
          <h2 className="mb-4 font-serif text-base" style={{ color: "var(--muted)" }}>Customer Development Phase</h2>
          <div className="flex gap-2">
            {PHASE_CONFIG.map((p, i) => {
              const isActive = p.id === phase;
              const isPast = currentPhaseIndex > i;
              const Icon = p.icon;
              return (
                <div
                  key={p.id}
                  className="flex-1 rounded-[var(--radius-md)] border p-3 transition"
                  style={{
                    borderColor: isActive ? "var(--chip-active-border)" : "var(--line)",
                    background: isActive ? "var(--chip-active-bg)" : isPast ? "var(--tag-bg)" : "transparent",
                  }}
                >
                  <div className="mb-1 flex items-center gap-2">
                    <Icon size={16} style={{ color: isActive || isPast ? p.accent : "var(--muted)" }} />
                    <span className="text-sm font-semibold" style={{ color: isActive ? "var(--ink)" : "var(--muted)" }}>
                      {p.label}
                    </span>
                  </div>
                  <p className="text-xs" style={{ color: "var(--muted)" }}>{p.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <Link to="/hypotheses" className="card block transition hover:opacity-90">
            <h2 className="mb-3 font-serif text-sm" style={{ color: "var(--muted)" }}>Hypotheses</h2>
            <div className="mb-3 font-serif text-3xl" style={{ color: "var(--ink)" }}>{total}</div>
            <div className="space-y-2">
              <StatBar label="Untested" count={hypothesisCounts.untested} total={total} color="var(--clay)" />
              <StatBar label="Testing" count={hypothesisCounts.testing} total={total} color="var(--gold)" />
              <StatBar label="Validated" count={hypothesisCounts.validated} total={total} color="var(--moss)" />
              <StatBar label="Invalidated" count={hypothesisCounts.invalidated} total={total} color="var(--rust)" />
            </div>
            <p className="mt-3 text-xs" style={{ color: "var(--moss)" }}>View all →</p>
          </Link>

          <div className="card">
            <h2 className="mb-3 font-serif text-sm" style={{ color: "var(--muted)" }}>Active Workflow</h2>
            {activeWorkflow ? (
              <div>
                <p className="text-sm font-semibold capitalize" style={{ color: "var(--ink)" }}>
                  {activeWorkflow.name.replace(/_/g, " ")}
                </p>
                <p className="mt-1 text-xs" style={{ color: "var(--muted)" }}>
                  Step {activeWorkflow.current_step + 1}/{activeWorkflow.total_steps}: {activeWorkflow.step_name}
                </p>
                <div className="mt-3 h-1.5 rounded-full" style={{ background: "var(--line)" }}>
                  <div
                    className="h-1.5 rounded-full transition-all"
                    style={{
                      width: `${((activeWorkflow.current_step + 1) / activeWorkflow.total_steps) * 100}%`,
                      background: "linear-gradient(90deg, var(--gold), var(--mint))",
                    }}
                  />
                </div>
              </div>
            ) : (
              <p className="text-sm" style={{ color: "var(--muted)" }}>No active workflow. Start one from the chat.</p>
            )}
          </div>

          <div className="card">
            <h2 className="mb-3 font-serif text-sm" style={{ color: "var(--muted)" }}>Journal Entries</h2>
            <div className="mb-1 font-serif text-3xl" style={{ color: "var(--ink)" }}>{journalCount}</div>
            <p className="text-xs" style={{ color: "var(--muted)" }}>recent entries captured</p>
          </div>
        </div>

        <div className="card">
          <h2 className="mb-3 font-serif text-sm" style={{ color: "var(--muted)" }}>Recent Activity</h2>
          {recentEntries.length === 0 ? (
            <p className="text-sm" style={{ color: "var(--muted)" }}>No activity yet. Chat with Yoak to get started.</p>
          ) : (
            <div className="space-y-2">
              {recentEntries.map((e) => (
                <div key={e.id} className="flex items-baseline gap-3 text-sm">
                  <span className="shrink-0 text-xs" style={{ color: "var(--muted)" }}>{e.created_at}</span>
                  <span className="w-20 shrink-0 text-xs font-extrabold uppercase tracking-wide" style={{ color: "var(--moss)" }}>
                    {e.entry_type}
                  </span>
                  <span style={{ color: "var(--ink)" }}>{e.title}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatBar({ label, count, total, color }: { label: string; count: number; total: number; color: string }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-20" style={{ color: "var(--muted)" }}>{label}</span>
      <div className="h-1.5 flex-1 rounded-full" style={{ background: "var(--line)" }}>
        <div className="h-1.5 rounded-full transition-all" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="w-6 text-right" style={{ color: "var(--muted)" }}>{count}</span>
    </div>
  );
}
