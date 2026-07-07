"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useInfiniteQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Search, SlidersHorizontal, X, Loader2, Briefcase, Zap, Sparkles, Bell, Check } from "lucide-react";
import { subDays } from "date-fns";
import { useSession } from "next-auth/react";
import { internshipsApi, usersApi } from "@/lib/api";
import { InternshipCard } from "@/components/internships/InternshipCard";
import { FilterSidebar } from "@/components/internships/FilterSidebar";

import type { Filters } from "@/components/internships/FilterSidebar";
const DEFAULT_FILTERS: Filters = { category: "", source: "", remote: null, period: "all" };

function InternshipCardSkeleton() {
  return (
    <div className="bg-[#0a080f]/40 border border-white/5 rounded-2xl p-5 glass h-[260px] relative overflow-hidden shimmer-shimmer">
      <div className="flex items-start justify-between mb-4">
        <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/5" />
        <div className="w-20 h-5 rounded-full bg-white/5" />
      </div>
      <div className="h-4 w-24 bg-white/5 rounded mb-2" />
      <div className="h-6 w-48 bg-white/5 rounded mb-4" />
      <div className="h-4 w-32 bg-white/5 rounded mb-4" />
      <div className="mt-auto h-9 w-full bg-white/5 rounded-xl" />
    </div>
  );
}

export default function InternshipsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { data: session } = useSession();
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    ...DEFAULT_FILTERS,
    category: searchParams.get("category") || "",
  });
  const [quickFilter, setQuickFilter] = useState("all");

  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveName, setSaveName] = useState("");
  const [frequency, setFrequency] = useState("daily");
  const [isSavingSearch, setIsSavingSearch] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Synchronize URL search parameters with component state
  useEffect(() => {
    const categoryParam = searchParams.get("category") || "";
    const qParam = searchParams.get("q") || "";
    setFilters((prev) => {
      if (prev.category !== categoryParam) {
        return { ...prev, category: categoryParam };
      }
      return prev;
    });
    setQuery(qParam);
  }, [searchParams]);

  const searchArgs = useMemo(() => {
    const args: Record<string, string | boolean | undefined> = {};
    if (query) args.q = query;
    if (filters.category) args.category = filters.category;
    if (filters.source) args.source = filters.source;
    if (filters.remote !== null) args.remote = true;
    const period = filters.period;
    if (period === "24h") args.posted_after = subDays(new Date(), 1).toISOString();
    if (period === "7d") args.posted_after = subDays(new Date(), 7).toISOString();
    return args;
  }, [query, filters]);

  const hasSearch = Object.keys(searchArgs).length > 0;
  const PAGE_SIZE = 24;

  const {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["internships", "infinite", searchArgs],
    queryFn: ({ pageParam }) => {
      const page = pageParam as number;
      if (hasSearch) {
        return internshipsApi.search({ ...searchArgs, page, page_size: PAGE_SIZE });
      }
      return internshipsApi.list(page, PAGE_SIZE);
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) =>
      lastPage.results.length >= PAGE_SIZE ? allPages.length + 1 : undefined,
  });

  const internships = data?.pages.flatMap(p => p.results) ?? [];
  const totalOpportunities = data?.pages[0]?.total ?? 0;

  const filteredInternships = useMemo(() => {
    if (quickFilter === "all") return internships;
    if (quickFilter === "ats") {
      return internships.filter(item => ["greenhouse", "lever", "ashby", "workday", "smartrecruiters", "icims", "taleo", "successfactors", "jobvite", "bamboohr"].includes(item.source.toLowerCase()));
    }
    if (quickFilter === "startups") {
      return internships.filter(item => item.company_type === "startup" || ["yc", "wellfound", "simplify", "ripplematch", "handshake", "huzzle"].includes(item.source.toLowerCase()));
    }
    if (quickFilter === "iit_nit") {
      return internships.filter(item => ["iit_portal", "nit_portal"].includes(item.source.toLowerCase()) || item.tags?.some(t => ["iit", "nit"].includes(t.toLowerCase())));
    }
    if (quickFilter === "mncs") {
      return internships.filter(item => item.company_type === "mnc" || item.company_type === "enterprise");
    }
    if (quickFilter === "verified") {
      return internships.filter(item => ["greenhouse", "lever", "ashby", "workday", "smartrecruiters", "icims", "taleo", "successfactors", "jobvite", "bamboohr", "yc", "wellfound", "simplify", "ripplematch", "handshake", "huzzle"].includes(item.source.toLowerCase()));
    }
    return internships;
  }, [internships, quickFilter]);

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
    const url = new URL(window.location.href);
    url.searchParams.delete("q");
    url.searchParams.delete("category");
    router.push(url.pathname);
  };

  const hasActiveFilters = filters.category || filters.source || filters.remote !== null || filters.period !== "all";

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-300 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5 text-orange-400" /> Catalog Feed
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white mb-0.5">Explore Internships</h1>
          <p className="text-muted-foreground text-xs font-semibold">
            {filteredInternships.length > 0
              ? `${quickFilter === "all" ? totalOpportunities : filteredInternships.length} active opportunities found`
              : isLoading
                ? "Analyzing ATS career portal data..."
                : "No opportunities found"}
          </p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <form onSubmit={handleSearch} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-orange-500/60" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by role name, employer keyword, or tech stack..."
            className="w-full pl-11 pr-10 py-3 bg-[#0a080f]/60 border border-white/5 rounded-xl text-xs placeholder:text-muted-foreground/60 text-white focus:outline-none focus:border-orange-500/40 glass"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        <button
          type="submit"
          className="px-5 py-3 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-orange-500/20 transition-all focus:outline-none"
        >
          Search Database
        </button>
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={`px-3.5 py-3 rounded-xl text-xs font-bold border transition-all focus:outline-none ${
            hasActiveFilters || showFilters
              ? "bg-orange-600/10 border-orange-500/30 text-orange-400"
              : "bg-[#0a080f]/60 border-white/5 text-muted-foreground hover:text-white"
          }`}
        >
          <SlidersHorizontal className="w-4 h-4" />
        </button>
      </form>

      {/* Save Search Button / Form */}
      {session?.accessToken && (hasActiveFilters || query) && (
        <div className="bg-[#0a080f]/40 border border-white/5 rounded-2xl p-4 glass">
          {!showSaveDialog ? (
            <button
              type="button"
              onClick={() => {
                setShowSaveDialog(true);
                setSaveName(query ? `Alerts for "${query}"` : "My Custom Alert");
              }}
              className="inline-flex items-center gap-2 text-xs font-bold text-orange-400 hover:text-orange-300 transition-colors focus:outline-none"
            >
              <Bell className="w-4 h-4" /> Save this search query & configure email alerts
            </button>
          ) : (
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                if (!session?.accessToken || !saveName.trim()) return;
                setIsSavingSearch(true);
                try {
                  await usersApi.createSavedSearch(session.accessToken, {
                    name: saveName.trim(),
                    query_params: searchArgs,
                    frequency,
                  });
                  setSaveSuccess(true);
                  setTimeout(() => {
                    setSaveSuccess(false);
                    setShowSaveDialog(false);
                    setSaveName("");
                  }, 2000);
                } catch (err) {
                  console.error("Failed to save search", err);
                } finally {
                  setIsSavingSearch(false);
                }
              }}
              className="flex flex-col sm:flex-row items-end sm:items-center gap-3 w-full"
            >
              <div className="flex-1 w-full">
                <label className="block text-[9px] font-bold text-muted-foreground uppercase tracking-wider mb-1.5">Search Alert Title</label>
                <input
                  type="text"
                  required
                  value={saveName}
                  onChange={(e) => setSaveName(e.target.value)}
                  placeholder="e.g. Software engineering remote alerts"
                  className="w-full px-3.5 py-2.5 bg-[#050308]/60 border border-white/5 rounded-xl text-xs text-white focus:outline-none focus:border-orange-500/40"
                />
              </div>
              <div className="w-full sm:w-auto">
                <label className="block text-[9px] font-bold text-muted-foreground uppercase tracking-wider mb-1.5">Alert Frequency</label>
                <select
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value)}
                  className="w-full px-3 py-2.5 bg-[#050308]/60 border border-white/5 rounded-xl text-xs text-white focus:outline-none focus:border-orange-500/40"
                >
                  <option value="instant">Instant Notification</option>
                  <option value="daily">Daily Summary</option>
                  <option value="weekly">Weekly Digest</option>
                </select>
              </div>
              <div className="flex gap-2 w-full sm:w-auto shrink-0 justify-end mt-2 sm:mt-0">
                <button
                  type="button"
                  onClick={() => setShowSaveDialog(false)}
                  className="px-4 py-2.5 border border-white/5 text-muted-foreground hover:text-white rounded-xl text-xs font-semibold focus:outline-none"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSavingSearch || saveSuccess}
                  className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg focus:outline-none"
                >
                  {isSavingSearch ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : saveSuccess ? (
                    <Check className="w-3.5 h-3.5" />
                  ) : (
                    <Bell className="w-3.5 h-3.5" />
                  )}
                  {isSavingSearch ? "Saving..." : saveSuccess ? "Alert Configured!" : "Create Search Alert"}
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* Quick Filter Tabs */}
      <div className="flex gap-2 pb-2 overflow-x-auto custom-scrollbar flex-wrap">
        {[
          { id: "all", label: "All Opportunities" },
          { id: "ats", label: "Top ATS Openings" },
          { id: "startups", label: "Startup Roles" },
          { id: "iit_nit", label: "IITs / NITs Portal" },
          { id: "mncs", label: "Tech MNCs" },
          { id: "verified", label: "Verified Only" }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setQuickFilter(tab.id)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all focus:outline-none ${
              quickFilter === tab.id
                ? "bg-gradient-to-r from-orange-600 to-amber-600 text-white shadow-md shadow-orange-500/10"
                : "bg-[#0a080f]/60 border border-white/5 text-muted-foreground hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex flex-col lg:flex-row gap-6 items-start">
        {/* Filter Sidebar container */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, x: -15, width: 0 }}
              animate={{ opacity: 1, x: 0, width: 230 }}
              exit={{ opacity: 0, x: -15, width: 0 }}
              transition={{ duration: 0.22, ease: "easeOut" }}
              className="shrink-0 bg-[#0a080f]/40 border border-white/5 rounded-2xl p-5 glass w-full lg:w-[230px] sticky top-20 overflow-hidden"
            >
              <FilterSidebar filters={filters} onChange={setFilters} onReset={resetFilters} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Catalog */}
        <div className="flex-1 min-w-0 w-full">
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {[...Array(6)].map((_, i) => (
                <InternshipCardSkeleton key={i} />
              ))}
            </div>
          ) : !internships?.length ? (
            <div className="flex flex-col items-center justify-center py-20 text-muted-foreground bg-[#0a080f]/40 border border-white/5 rounded-2xl glass text-center">
              <Briefcase className="w-12 h-12 mb-4 opacity-20 text-orange-450 animate-pulse" />
              <h3 className="text-white font-bold text-sm mb-1">No Opportunities Found</h3>
              <p className="text-xs text-muted-foreground max-w-xs mb-6">
                We couldn&apos;t locate any listings matching your queries. Adjust filters to search broader scopes.
              </p>
              {(hasActiveFilters || query) && (
                <button
                  onClick={resetFilters}
                  className="bg-orange-600/10 border border-orange-500/20 text-orange-400 font-bold text-xs px-5 py-2.5 rounded-xl hover:bg-orange-500/20 transition-all focus:outline-none"
                >
                  Clear Filters & Search Query
                </button>
              )}
            </div>
          ) : (
            <>
              <motion.div layout className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                <AnimatePresence mode="popLayout">
                  {filteredInternships.map((internship, i) => (
                    <motion.div
                      key={internship._id || internship.external_id}
                      layout
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.25, delay: Math.min(0.015 * i, 0.2) }}
                    >
                      <InternshipCard internship={internship} />
                    </motion.div>
                  ))}
                </AnimatePresence>
              </motion.div>

              {hasNextPage && (
                <div className="flex justify-center mt-8">
                  <button
                    onClick={() => fetchNextPage()}
                    disabled={isFetchingNextPage}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-orange-500/20 transition-all disabled:opacity-60 disabled:cursor-not-allowed focus:outline-none"
                  >
                    {isFetchingNextPage ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" /> Loading more roles…
                      </>
                    ) : (
                      <>
                        <Briefcase className="w-4 h-4" /> Load More Opportunities
                      </>
                    )}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
