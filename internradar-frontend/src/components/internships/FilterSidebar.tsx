"use client";

import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { CATEGORIES, SOURCES } from "@/types";

export interface Filters {
  category: string;
  source: string;
  remote: boolean | null;
  period: "all" | "24h" | "7d";
}

interface Props {
  filters: Filters;
  onChange: (f: Filters) => void;
  onReset: () => void;
}

const PERIODS = [
  { value: "all", label: "All Time" },
  { value: "24h", label: "Last 24 Hours" },
  { value: "7d", label: "Last 7 Days" },
];

export function FilterSidebar({ filters, onChange, onReset }: Props) {
  const set = (partial: Partial<Filters>) => onChange({ ...filters, ...partial });
  const hasActive = filters.category || filters.source || filters.remote !== null || filters.period !== "all";

  return (
    <aside className="w-full space-y-5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold">Filters</span>
        {hasActive && (
          <button onClick={onReset} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
            <X className="w-3 h-3" /> Reset
          </button>
        )}
      </div>

      {/* Remote */}
      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Type</p>
        <button
          onClick={() => set({ remote: filters.remote === true ? null : true })}
          className={cn("w-full text-left px-3 py-2 rounded-lg text-sm transition-all", filters.remote === true ? "bg-orange-600/10 text-orange-400 border border-orange-500/20" : "text-muted-foreground hover:bg-accent")}
        >
          Remote Only
        </button>
      </div>

      {/* Period */}
      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Date Posted</p>
        <div className="space-y-0.5">
          {PERIODS.map((p) => (
            <button key={p.value} onClick={() => set({ period: p.value as Filters["period"] })}
              className={cn("w-full text-left px-3 py-2 rounded-lg text-sm transition-all", filters.period === p.value ? "bg-orange-600/10 text-orange-400 border border-orange-500/20" : "text-muted-foreground hover:bg-accent")}>
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Categories */}
      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Category</p>
        <div className="space-y-0.5 max-h-64 overflow-y-auto">
          {CATEGORIES.map((cat) => (
            <button key={cat} onClick={() => set({ category: filters.category === cat ? "" : cat })}
              className={cn("w-full text-left px-3 py-1.5 rounded-lg text-xs transition-all", filters.category === cat ? "bg-orange-600/10 text-orange-400 border border-orange-500/20" : "text-muted-foreground hover:bg-accent hover:text-foreground")}>
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Sources */}
      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Source</p>
        <div className="space-y-0.5">
          {SOURCES.map((src) => (
            <button key={src} onClick={() => set({ source: filters.source === src ? "" : src })}
              className={cn("w-full text-left px-3 py-1.5 rounded-lg text-xs capitalize transition-all", filters.source === src ? "bg-orange-600/10 text-orange-400 border border-orange-500/20" : "text-muted-foreground hover:bg-accent hover:text-foreground")}>
              {src}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
