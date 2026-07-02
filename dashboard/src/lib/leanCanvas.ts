export const LEAN_CANVAS_FIELDS = [
  {
    id: "problem",
    label: "Problem",
    gridClass: "lean-cell-problem",
    placeholder: "Top 3 problems",
  },
  {
    id: "solution",
    label: "Solution",
    gridClass: "lean-cell-solution",
    placeholder: "Top 3 features",
  },
  {
    id: "key_metrics",
    label: "Key Metrics",
    gridClass: "lean-cell-keymetrics",
    placeholder: "Key activities you measure",
  },
  {
    id: "unique_value_proposition",
    label: "Unique Value Prop",
    gridClass: "lean-cell-uvp",
    placeholder: "Single, clear message",
  },
  {
    id: "unfair_advantage",
    label: "Unfair Advantage",
    gridClass: "lean-cell-unfair",
    placeholder: "Can't be easily copied",
  },
  {
    id: "channels",
    label: "Channels",
    gridClass: "lean-cell-channels",
    placeholder: "Path to customers",
  },
  {
    id: "customer_segments",
    label: "Customer Segments",
    gridClass: "lean-cell-customers",
    placeholder: "Target customers",
  },
  {
    id: "cost_structure",
    label: "Cost Structure",
    gridClass: "lean-cell-cost",
    placeholder: "Customer acquisition costs, hosting, etc.",
  },
  {
    id: "revenue_streams",
    label: "Revenue Streams",
    gridClass: "lean-cell-revenue",
    placeholder: "Revenue model, lifetime value, etc.",
  },
] as const;

export function blockLabel(blockId: string): string {
  return LEAN_CANVAS_FIELDS.find((f) => f.id === blockId)?.label ?? blockId.replace(/_/g, " ");
}

export type CanvasBlockId = (typeof LEAN_CANVAS_FIELDS)[number]["id"];

export type BlockMap = Record<string, string>;

export type CanvasSnapshot = {
  id: string;
  name: string;
  created: number;
  blocks: BlockMap;
};

export type SnapshotStore = {
  snapshots: CanvasSnapshot[];
};

const STORAGE_KEY = "yoak_canvas_snapshots";

export function uid(): string {
  return Math.random().toString(36).slice(2, 10);
}

export function emptyBlockMap(): BlockMap {
  return Object.fromEntries(LEAN_CANVAS_FIELDS.map((f) => [f.id, ""]));
}

export function blocksFromApi(apiBlocks: Array<{ id: string; content: string }>): BlockMap {
  const map = emptyBlockMap();
  for (const block of apiBlocks) {
    map[block.id] = block.content || "";
  }
  return map;
}

export function loadSnapshots(): SnapshotStore {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as SnapshotStore;
      if (parsed.snapshots?.length) return parsed;
    }
  } catch {
    /* ignore */
  }
  return { snapshots: [] };
}

export function saveSnapshots(store: SnapshotStore): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

export function exportJSON(name: string, blocks: BlockMap): void {
  const blob = new Blob([JSON.stringify({ name, blocks }, null, 2)], { type: "application/json" });
  downloadBlob(blob, `${slug(name)}.json`);
}

export function exportMarkdown(name: string, blocks: BlockMap): void {
  let md = `# Lean Canvas — ${name}\n\n`;
  for (const field of LEAN_CANVAS_FIELDS) {
    md += `## ${field.label}\n\n${blocks[field.id]?.trim() || "_empty_"}\n\n`;
  }
  const blob = new Blob([md], { type: "text/markdown" });
  downloadBlob(blob, `${slug(name)}.md`);
}

export function exportCSV(name: string, blocks: BlockMap): void {
  const rows = [["Section", "Content"]];
  for (const field of LEAN_CANVAS_FIELDS) {
    rows.push([field.label, blocks[field.id] || ""]);
  }
  const csv = rows.map((row) => row.map(escapeCsv).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  downloadBlob(blob, `${slug(name)}.csv`);
}

function slug(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") || "lean-canvas";
}

function escapeCsv(value: string): string {
  if (/[",\n]/.test(value)) return `"${value.replace(/"/g, '""')}"`;
  return value;
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
