"use client";

import { useState, useMemo, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Search, SlidersHorizontal, X, Loader2, Briefcase } from "lucide-react";
import { subDays } from "date-fns";
import { internshipsApi } from "@/lib/api";
import { InternshipCard } from "@/components/internships/InternshipCard";
import { FilterSidebar } from "@/components/internships/FilterSidebar";

import type { Filters } from "@/components/internships/FilterSidebar";
const DEFAULT_FILTERS: Filters = { category: "", source: "", remote: null, period: "all" };

export default function InternshipsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    ...DEFAULT_FILTERS,
    category: searchParams.get("category") || "",
  });

  const searchArgs = useMemo(() => {
    const args: Record<string, string | boolean | undefined> = {};
    if (query) args.title = query;
    if (filters.category) args.category = filters.category;
    if (filters.source) args.source = filters.source;
    if (filters.remote !== null) args.remote = true;
    const period = filters.period;
    if (period === "24h") args.posted_after = subDays(new Date(), 1).toISOString();
    if (period === "7d") args.posted_after = subDays(new Date(), 7).toISOString();
    return args;
  }, [query, filters]);

  const hasSearch = Object.keys(searchArgs).length > 0;

  const { data: searchResults, isLoading: searching } = useQuery({
    queryKey: ["internships", "search", searchArgs],
    queryFn: () => internshipsApi.search(searchArgs),
    enabled: hasSearch,
  });

  const { data: all, isLoading: loadingAll } = useQuery({
    queryKey: ["internships", "list"],
    queryFn: () => internshipsApi.list(1, 100),
    enabled: !hasSearch,
  });

  const internships = hasSearch ? searchResults : all;
  const isLoading = hasSearch ? searching : loadingAll;

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    const url = new URL(window.location.href);
    if (query) url.searchParams.set("q", query);
    else url.searchParams.delete("q");
    router.push(url.pathname + url.search);
  }, [query, router]);

  const resetFilters = () => {
    setFilters(DEFAULT_FILTERS);
    setQuery("");
  };

  const hasActiveFilters = filters.category || filters.source || filters.remote !== null || filters.period !== "all";

  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-0.5">Internship Feed</h1>
        <p className="text-muted-foreground text-sm">
          {internships?.length !== undefined ? `${internships.length} opportunities found` : "Discovering opportunities..."}
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by role, company, keyword..."
            className="w-full pl-10 pr-4 py-2.5 bg-card border border-border/50 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
          />
          {query && (
            <button type="button" onClick={() => setQuery("")} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        <button type="submit" className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition-colors">
          Search
        </button>
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={`px-3 py-2.5 rounded-xl text-sm font-medium border transition-all ${hasActiveFilters ? "bg-indigo-600/10 border-indigo-500/30 text-indigo-400" : "bg-card border-border/50 text-muted-foreground hover:text-foreground"}`}
        >
          <SlidersHorizontal className="w-4 h-4" />
        </button>
      </form>

      <div className="flex gap-6">
        {/* Filter Sidebar */}
        <AnimatePresence>
          {showFilters && (
            <motion.div initial={{ opacity: 0, x: -20, width: 0 }} animate={{ opacity: 1, x: 0, width: 220 }} exit={{ opacity: 0, x: -20, width: 0 }}
              className="shrink-0 bg-card border border-border/50 rounded-xl p-4 h-fit sticky top-20 overflow-hidden">
              <FilterSidebar filters={filters} onChange={setFilters} onReset={resetFilters} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <div className="flex-1 min-w-0">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
              <Loader2 className="w-8 h-8 animate-spin mb-3 text-indigo-400" />
              <p className="text-sm">Loading internships...</p>
            </div>
          ) : !internships?.length ? (
            <div className="flex flex-col items-center justify-center py-20 text-muted-foreground bg-card border border-border/50 rounded-xl">
              <Briefcase className="w-12 h-12 mb-3 opacity-20" />
              <p className="font-medium mb-1">No internships found</p>
              <p className="text-sm">{hasActiveFilters || query ? "Try adjusting your filters" : "Database may still be connecting"}</p>
              {(hasActiveFilters || query) && (
                <button onClick={resetFilters} className="mt-3 text-sm text-indigo-400 hover:text-indigo-300">Clear filters</button>
              )}
            </div>
          ) : (
            <motion.div layout className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <AnimatePresence>
                {internships.map((internship, i) => (
                  <motion.div key={internship._id || internship.external_id}
                    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                    transition={{ delay: Math.min(0.02 * i, 0.3) }}>
                    <InternshipCard internship={internship} />
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
