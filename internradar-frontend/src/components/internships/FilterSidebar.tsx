"use client";

import { X, Check } from "lucide-react";
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
    <aside className="w-full space-y-6">
      <div className="flex items-center justify-between border-b border-white/5 pb-3">
        <span className="text-xs font-extrabold uppercase tracking-wider text-white">Curation Filters</span>
        {hasActive && (
          <button onClick={onReset} className="flex items-center gap-1 text-[10px] font-extrabold text-orange-400 hover:text-orange-300 uppercase tracking-wider transition-colors">
            <X className="w-3 h-3" /> Reset
          </button>
        )}
      </div>

      {/* Remote Toggle */}
      <div className="space-y-2">
        <p className="text-[9px] font-bold text-muted-foreground/50 uppercase tracking-widest">Work Arrangements</p>
        <button
          onClick={() => set({ remote: filters.remote === true ? null : true })}
          className={cn(
            "w-full text-left px-3 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-between border",
            filters.remote === true 
              ? "bg-orange-500/10 text-orange-400 border-orange-500/25" 
              : "text-muted-foreground border-transparent hover:bg-white/5 hover:text-white"
          )}
        >
          <span>Remote Placement Only</span>
          {filters.remote === true && <Check className="w-3.5 h-3.5 text-orange-400" />}
        </button>
      </div>

      {/* Date Posted */}
      <div className="space-y-2">
        <p className="text-[9px] font-bold text-muted-foreground/50 uppercase tracking-widest">Added Date Range</p>
        <div className="space-y-1">
          {PERIODS.map((p) => (
            <button 
              key={p.value} 
              onClick={() => set({ period: p.value as Filters["period"] })}
              className={cn(
                "w-full text-left px-3 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-between border", 
                filters.period === p.value 
                  ? "bg-orange-500/10 text-orange-400 border-orange-500/25" 
                  : "text-muted-foreground border-transparent hover:bg-white/5 hover:text-white"
              )}
            >
              <span>{p.label}</span>
              {filters.period === p.value && <Check className="w-3.5 h-3.5 text-orange-400" />}
            </button>
          ))}
        </div>
      </div>

      {/* Categories */}
      <div className="space-y-2">
        <p className="text-[9px] font-bold text-muted-foreground/50 uppercase tracking-widest">Technical Domain</p>
        <div className="space-y-0.5 max-h-56 overflow-y-auto pr-1 custom-scrollbar">
          {CATEGORIES.map((cat) => (
            <button 
              key={cat} 
              onClick={() => set({ category: filters.category === cat ? "" : cat })}
              className={cn(
                "w-full text-left px-3 py-2 rounded-xl text-[11px] font-semibold transition-all flex items-center justify-between border", 
                filters.category === cat 
                  ? "bg-orange-500/10 text-orange-400 border-orange-500/25" 
                  : "text-muted-foreground border-transparent hover:bg-white/[0.01] hover:text-white"
              )}
            >
              <span className="truncate">{cat}</span>
              {filters.category === cat && <Check className="w-3 h-3 text-orange-400 shrink-0 ml-1" />}
            </button>
          ))}
        </div>
      </div>

      {/* Sources */}
      <div className="space-y-2">
        <p className="text-[9px] font-bold text-muted-foreground/50 uppercase tracking-widest">Verification Source</p>
        <div className="space-y-0.5 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
          {SOURCES.map((src) => (
            <button 
              key={src} 
              onClick={() => set({ source: filters.source === src ? "" : src })}
              className={cn(
                "w-full text-left px-3 py-1.5 rounded-xl text-xs capitalize transition-all flex items-center justify-between border", 
                filters.source === src 
                  ? "bg-orange-500/10 text-orange-400 border-orange-500/25" 
                  : "text-muted-foreground border-transparent hover:bg-white/[0.01] hover:text-white"
              )}
            >
              <span className="truncate">{src}</span>
              {filters.source === src && <Check className="w-3 h-3 text-orange-400 shrink-0 ml-1" />}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
