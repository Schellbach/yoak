import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import { Check, ChevronDown, ChevronUp, Plus, X, AlertTriangle } from "lucide-react";
import {
  getCanvas,
  updateCanvasBlock,
  createHypothesis,
  updateHypothesis,
  deleteHypothesis,
} from "@/api/client";
import {
  LEAN_CANVAS_FIELDS,
  blocksFromApi,
  exportCSV,
  exportJSON,
  exportMarkdown,
  loadSnapshots,
  saveSnapshots,
  uid,
  emptyBlockMap,
  type BlockMap,
  type CanvasSnapshot,
} from "@/lib/leanCanvas";

const LIVE_ID = "__live__";

const STATUS_STYLES: Record<string, CSSProperties> = {
  untested: { borderColor: "var(--line)", color: "var(--muted)" },
  testing: { borderColor: "var(--gold)", color: "var(--gold)" },
  validated: { borderColor: "var(--moss)", color: "var(--moss)" },
  invalidated: { borderColor: "var(--rust)", color: "var(--rust)" },
};

type ApiBlock = {
  id: string;
  content: string;
  hypotheses: Array<{ id: string; statement: string; status: string }>;
};

export default function CanvasPage() {
  const [apiBlocks, setApiBlocks] = useState<ApiBlock[]>([]);
  const [snapshots, setSnapshots] = useState<CanvasSnapshot[]>(() => loadSnapshots().snapshots);
  const [activeId, setActiveId] = useState(LIVE_ID);
  const [compareMode, setCompareMode] = useState(false);
  const [compareA, setCompareA] = useState(LIVE_ID);
  const [compareB, setCompareB] = useState<string>("");
  const [exportOpen, setExportOpen] = useState(false);
  const [newModalOpen, setNewModalOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [expandedHyp, setExpandedHyp] = useState<Record<string, boolean>>({});
  const [addingHyp, setAddingHyp] = useState<string | null>(null);
  const [newHypothesis, setNewHypothesis] = useState("");
  const saveTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  const loadApi = useCallback(async () => {
    const res = await getCanvas();
    setApiBlocks(res.blocks);
  }, []);

  useEffect(() => {
    loadApi();
  }, [loadApi]);

  const liveBlocks = useMemo(() => blocksFromApi(apiBlocks), [apiBlocks]);

  const allVersions = useMemo(
    () => [{ id: LIVE_ID, name: "Current", blocks: liveBlocks, created: 0 }, ...snapshots],
    [liveBlocks, snapshots]
  );

  useEffect(() => {
    if (!compareB && snapshots[0]) setCompareB(snapshots[0].id);
  }, [compareB, snapshots]);

  const activeVersion = allVersions.find((v) => v.id === activeId) || allVersions[0];
  const activeBlocks = activeVersion.blocks;
  const isLive = activeId === LIVE_ID;

  const persistSnapshots = (next: CanvasSnapshot[]) => {
    setSnapshots(next);
    saveSnapshots({ snapshots: next });
  };

  const scheduleSave = (blockId: string, value: string) => {
    if (saveTimers.current[blockId]) clearTimeout(saveTimers.current[blockId]);
    saveTimers.current[blockId] = setTimeout(async () => {
      if (isLive) {
        await updateCanvasBlock(blockId, value);
        await loadApi();
      } else {
        persistSnapshots(
          snapshots.map((s) =>
            s.id === activeId ? { ...s, blocks: { ...s.blocks, [blockId]: value } } : s
          )
        );
      }
    }, 400);
  };

  const handleFieldChange = (blockId: string, value: string) => {
    if (isLive) {
      setApiBlocks((prev) =>
        prev.map((b) => (b.id === blockId ? { ...b, content: value } : b))
      );
    } else {
      persistSnapshots(
        snapshots.map((s) =>
          s.id === activeId ? { ...s, blocks: { ...s.blocks, [blockId]: value } } : s
        )
      );
    }
    scheduleSave(blockId, value);
  };

  const createSnapshot = (name: string, blocks: BlockMap) => {
    const snap: CanvasSnapshot = { id: uid(), name, created: Date.now(), blocks: { ...blocks } };
    persistSnapshots([...snapshots, snap]);
    setActiveId(snap.id);
    setNewModalOpen(false);
  };

  const duplicateSnapshot = () => {
    createSnapshot(`${activeVersion.name} copy`, activeBlocks);
  };

  const deleteSnapshot = (id: string) => {
    const next = snapshots.filter((s) => s.id !== id);
    persistSnapshots(next);
    if (activeId === id) setActiveId(LIVE_ID);
    if (compareA === id) setCompareA(LIVE_ID);
    if (compareB === id) setCompareB(next[0]?.id || LIVE_ID);
  };

  const applySnapshotToLive = async (blocks: BlockMap) => {
    for (const field of LEAN_CANVAS_FIELDS) {
      await updateCanvasBlock(field.id, blocks[field.id] || "");
    }
    await loadApi();
    setActiveId(LIVE_ID);
  };

  const handleAddHypothesis = async (blockId: string) => {
    if (!newHypothesis.trim() || !isLive) return;
    await createHypothesis({ canvas_block: blockId, statement: newHypothesis.trim() });
    setNewHypothesis("");
    setAddingHyp(null);
    loadApi();
  };

  const cycleStatus = async (id: string, status: string) => {
    const order = ["untested", "testing", "validated", "invalidated"];
    const next = order[(order.indexOf(status) + 1) % order.length];
    await updateHypothesis(id, { status: next });
    loadApi();
  };

  const getHypotheses = (blockId: string) =>
    apiBlocks.find((b) => b.id === blockId)?.hypotheses || [];

  const renderCell = (field: (typeof LEAN_CANVAS_FIELDS)[number], editable: boolean) => {
    const value = activeBlocks[field.id] || "";
    const hyps = getHypotheses(field.id);
    const hypOpen = expandedHyp[field.id];

    return (
      <div key={field.id} className={`lean-cell ${field.gridClass}`}>
        <div className="lean-cell-label">{field.label}</div>
        <textarea
          className="lean-cell-textarea"
          placeholder={field.placeholder}
          value={value}
          readOnly={!editable}
          onChange={(e) => editable && handleFieldChange(field.id, e.target.value)}
        />
        {isLive && hyps.length > 0 && (
          <div className="mt-2 border-t pt-2" style={{ borderColor: "var(--line)" }}>
            <button
              type="button"
              className="flex items-center gap-1 text-[10px] font-extrabold uppercase tracking-wide"
              style={{ color: "var(--muted)" }}
              onClick={() => setExpandedHyp((p) => ({ ...p, [field.id]: !p[field.id] }))}
            >
              {hypOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              {hyps.length} hypothesis{hyps.length === 1 ? "" : "es"}
            </button>
            {hypOpen && (
              <div className="mt-1.5 space-y-1">
                {hyps.map((h) => (
                  <div key={h.id} className="lean-hypothesis border" style={STATUS_STYLES[h.status]}>
                    <button type="button" onClick={() => cycleStatus(h.id, h.status)} title="Cycle status">
                      {h.status === "validated" ? <Check size={11} /> : <AlertTriangle size={11} />}
                    </button>
                    <span className="flex-1">{h.statement}</span>
                    <button type="button" onClick={() => deleteHypothesis(h.id).then(loadApi)} style={{ color: "var(--muted)" }}>
                      <X size={11} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        {isLive && addingHyp === field.id ? (
          <div className="mt-2 flex gap-1">
            <input
              value={newHypothesis}
              onChange={(e) => setNewHypothesis(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddHypothesis(field.id)}
              placeholder="Hypothesis..."
              className="input flex-1 text-xs"
              autoFocus
            />
            <button type="button" onClick={() => handleAddHypothesis(field.id)} className="btn-primary px-2 text-xs">+</button>
            <button type="button" onClick={() => { setAddingHyp(null); setNewHypothesis(""); }} className="btn-ghost px-2 text-xs">
              <X size={12} />
            </button>
          </div>
        ) : isLive ? (
          <button type="button" onClick={() => setAddingHyp(field.id)} className="btn-ghost mt-1 flex items-center gap-1 self-start text-[11px]">
            <Plus size={11} /> Add hypothesis
          </button>
        ) : null}
      </div>
    );
  };

  const renderCompare = () => {
    const a = allVersions.find((v) => v.id === compareA) || allVersions[0];
    const b = allVersions.find((v) => v.id === compareB) || allVersions[0];

    return (
      <div className="mx-auto max-w-[1000px] p-6">
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <select
            className="input text-sm"
            value={compareA}
            onChange={(e) => setCompareA(e.target.value)}
          >
            {allVersions.map((v) => (
              <option key={v.id} value={v.id}>{v.name}</option>
            ))}
          </select>
          <span className="text-xs font-extrabold" style={{ color: "var(--muted)" }}>vs</span>
          <select
            className="input text-sm"
            value={compareB}
            onChange={(e) => setCompareB(e.target.value)}
          >
            {allVersions.map((v) => (
              <option key={v.id} value={v.id}>{v.name}</option>
            ))}
          </select>
        </div>
        <table className="w-full overflow-hidden rounded-[var(--radius-md)] border text-sm" style={{ borderColor: "var(--line)" }}>
          <thead>
            <tr className="border-b text-left text-xs" style={{ borderColor: "var(--line)", background: "var(--surface-muted)", color: "var(--muted)" }}>
              <th className="w-36 px-4 py-2.5">Section</th>
              <th className="px-4 py-2.5" style={{ background: "var(--compare-a)" }}>{a.name}</th>
              <th className="px-4 py-2.5" style={{ background: "var(--compare-b)" }}>{b.name}</th>
            </tr>
          </thead>
          <tbody>
            {LEAN_CANVAS_FIELDS.map((field) => {
              const valA = a.blocks[field.id] || "";
              const valB = b.blocks[field.id] || "";
              const diff = valA !== valB;
              return (
                <tr key={field.id} className="border-b last:border-0" style={{ borderColor: "var(--line)" }}>
                  <td className="px-4 py-3 text-[11px] font-extrabold uppercase tracking-wide" style={{ background: "var(--surface-muted)", color: "var(--muted)" }}>
                    {field.label}
                    {diff && <span className="ml-2 inline-block h-1.5 w-1.5 rounded-full" style={{ background: "var(--gold-soft)" }} />}
                  </td>
                  <td className="whitespace-pre-wrap px-4 py-3 align-top" style={{ background: diff ? "var(--compare-a)" : "transparent", color: diff ? "var(--ink)" : "var(--muted)" }}>
                    {valA || <span className="italic">empty</span>}
                  </td>
                  <td className="whitespace-pre-wrap px-4 py-3 align-top" style={{ background: diff ? "var(--compare-b)" : "transparent", color: diff ? "var(--ink)" : "var(--muted)" }}>
                    {valB || <span className="italic">empty</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="flex h-full flex-col">
      <header className="page-header sticky top-0 z-10">
        <h1>Lean Canvas</h1>
        <div className="flex items-center gap-2">
          {!isLive && !compareMode && (
            <button type="button" className="btn-primary text-xs" onClick={() => applySnapshotToLive(activeBlocks)}>
              Apply to Current
            </button>
          )}
          <button
            type="button"
            className={`filter-chip ${compareMode ? "active" : ""}`}
            onClick={() => {
              if (!compareMode && snapshots.length < 1) {
                duplicateSnapshot();
              }
              setCompareMode(!compareMode);
            }}
          >
            Compare
          </button>
          <div className="relative">
            <button type="button" className="btn-ghost text-xs" onClick={() => setExportOpen(!exportOpen)}>
              Export
            </button>
            {exportOpen && (
              <div
                className="absolute right-0 top-full z-20 mt-1 min-w-[150px] rounded-[var(--radius-sm)] border py-1 shadow-lg"
                style={{ borderColor: "var(--line)", background: "var(--surface-elevated)" }}
              >
                {(
                  [
                    { label: "JSON", action: () => exportJSON(activeVersion.name, activeBlocks) },
                    { label: "Markdown", action: () => exportMarkdown(activeVersion.name, activeBlocks) },
                    { label: "CSV", action: () => exportCSV(activeVersion.name, activeBlocks) },
                  ] as const
                ).map(({ label, action }) => (
                  <button
                    key={label}
                    type="button"
                    className="block w-full px-4 py-2 text-left text-xs hover:opacity-80"
                    style={{ color: "var(--ink)" }}
                    onClick={() => { action(); setExportOpen(false); }}
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="flex flex-wrap items-center gap-2 border-b px-6 py-2" style={{ borderColor: "var(--line)", background: "var(--surface-muted)" }}>
        {allVersions.map((v) => (
          <button
            key={v.id}
            type="button"
            onClick={() => { setActiveId(v.id); setCompareMode(false); }}
            className={`filter-chip ${activeId === v.id && !compareMode ? "active" : ""}`}
          >
            {v.name}
            {v.id !== LIVE_ID && (
              <span
                role="button"
                className="ml-2"
                style={{ color: "var(--rust)" }}
                onClick={(e) => { e.stopPropagation(); deleteSnapshot(v.id); }}
              >
                ×
              </span>
            )}
          </button>
        ))}
        <button type="button" className="btn-ghost text-xs" onClick={() => { setNewName(`Model v${snapshots.length + 1}`); setNewModalOpen(true); }}>
          + New
        </button>
        <button type="button" className="btn-ghost text-xs" onClick={duplicateSnapshot}>
          Duplicate
        </button>
      </div>

      {compareMode ? renderCompare() : (
        <div className="flex-1 overflow-y-auto">
          <div className="lean-canvas-wrap">
            <div className="lean-canvas">
              {LEAN_CANVAS_FIELDS.map((field) => renderCell(field, true))}
            </div>
          </div>
        </div>
      )}

      {newModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "var(--backdrop)" }}>
          <div
            className="w-full max-w-md rounded-[var(--radius-lg)] border p-6 shadow-xl"
            style={{ borderColor: "var(--dialog-border)", background: "var(--surface-elevated)" }}
          >
            <h3 className="mb-4 font-serif text-base" style={{ color: "var(--ink)" }}>New Canvas</h3>
            <input
              className="input mb-4 w-full"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="e.g. SaaS Model v2"
              autoFocus
              onKeyDown={(e) => e.key === "Enter" && newName.trim() && createSnapshot(newName.trim(), emptyBlockMap())}
            />
            <div className="flex justify-end gap-2">
              <button type="button" className="btn-ghost" onClick={() => setNewModalOpen(false)}>Cancel</button>
              <button
                type="button"
                className="btn-primary"
                onClick={() => newName.trim() && createSnapshot(newName.trim(), emptyBlockMap())}
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
