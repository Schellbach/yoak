import { useState, useEffect } from "react";
import {
  Search,
  CheckCircle,
  Megaphone,
  Building,
  AlertTriangle,
  Check,
  X,
  FlaskConical,
} from "lucide-react";
import { getPhase, getCanvas, getHypotheses, getJournal, getActiveWorkflow } from "@/api/client";

const PHASE_CONFIG = [
  { id: "discovery", label: "Discovery", icon: Search, description: "Testing problem-solution fit" },
  { id: "validation", label: "Validation", icon: CheckCircle, description: "Proving repeatable sales" },
  { id: "creation", label: "Creation", icon: Megaphone, description: "Driving demand at scale" },
  { id: "building", label: "Building", icon: Building, description: "Scaling the company" },
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

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <header className="border-b border-gray-800 px-6 py-3">
        <h1 className="text-lg font-semibold">Overview</h1>
      </header>

      <div className="p-6 space-y-6">
        {/* Phase tracker */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-400 mb-4">Customer Development Phase</h2>
          <div className="flex gap-2">
            {PHASE_CONFIG.map((p, i) => {
              const isActive = p.id === phase;
              const isPast = PHASE_CONFIG.findIndex((x) => x.id === phase) > i;
              const Icon = p.icon;
              return (
                <div
                  key={p.id}
                  className={`flex-1 rounded-lg border p-3 transition ${
                    isActive
                      ? "border-yoak-500 bg-yoak-950/40"
                      : isPast
                        ? "border-green-800 bg-green-950/20"
                        : "border-gray-800"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Icon size={16} className={isActive ? "text-yoak-400" : isPast ? "text-green-500" : "text-gray-600"} />
                    <span className={`text-sm font-medium ${isActive ? "text-yoak-300" : isPast ? "text-green-400" : "text-gray-500"}`}>
                      {p.label}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">{p.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {/* Hypothesis stats */}
          <div className="card">
            <h2 className="text-sm font-semibold text-gray-400 mb-3">Hypotheses</h2>
            <div className="text-3xl font-bold text-gray-100 mb-3">{total}</div>
            <div className="space-y-2">
              <StatBar label="Untested" count={hypothesisCounts.untested} total={total} color="bg-gray-500" />
              <StatBar label="Testing" count={hypothesisCounts.testing} total={total} color="bg-yellow-500" />
              <StatBar label="Validated" count={hypothesisCounts.validated} total={total} color="bg-green-500" />
              <StatBar label="Invalidated" count={hypothesisCounts.invalidated} total={total} color="bg-red-500" />
            </div>
          </div>

          {/* Active workflow */}
          <div className="card">
            <h2 className="text-sm font-semibold text-gray-400 mb-3">Active Workflow</h2>
            {activeWorkflow ? (
              <div>
                <p className="text-sm font-medium text-yoak-300">{activeWorkflow.name.replace(/_/g, " ")}</p>
                <p className="text-xs text-gray-500 mt-1">
                  Step {activeWorkflow.current_step + 1}/{activeWorkflow.total_steps}: {activeWorkflow.step_name}
                </p>
                <div className="mt-3 h-1.5 rounded-full bg-gray-800">
                  <div
                    className="h-1.5 rounded-full bg-yoak-500 transition-all"
                    style={{ width: `${((activeWorkflow.current_step + 1) / activeWorkflow.total_steps) * 100}%` }}
                  />
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-600">No active workflow. Start one from the chat.</p>
            )}
          </div>

          {/* Quick stats */}
          <div className="card">
            <h2 className="text-sm font-semibold text-gray-400 mb-3">Journal Entries</h2>
            <div className="text-3xl font-bold text-gray-100 mb-1">{journalCount}</div>
            <p className="text-xs text-gray-500">recent entries captured</p>
          </div>
        </div>

        {/* Recent journal */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-400 mb-3">Recent Activity</h2>
          {recentEntries.length === 0 ? (
            <p className="text-sm text-gray-600">No activity yet. Chat with Yoak to get started.</p>
          ) : (
            <div className="space-y-2">
              {recentEntries.map((e) => (
                <div key={e.id} className="flex items-baseline gap-3 text-sm">
                  <span className="text-xs text-gray-600 shrink-0">{e.created_at}</span>
                  <span className="text-xs font-medium text-gray-500 uppercase w-20">{e.entry_type}</span>
                  <span className="text-gray-300">{e.title}</span>
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
      <span className="w-20 text-gray-500">{label}</span>
      <div className="flex-1 h-1.5 rounded-full bg-gray-800">
        <div className={`h-1.5 rounded-full ${color} transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-6 text-right text-gray-500">{count}</span>
    </div>
  );
}
