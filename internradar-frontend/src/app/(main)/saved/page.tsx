"use client";

import { useSession } from "next-auth/react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Bookmark, Search, SlidersHorizontal, ArrowUpDown, Briefcase, Globe, Sparkles, FolderHeart } from "lucide-react";
import Link from "next/link";
import { useState, useMemo } from "react";
import { usersApi } from "@/lib/api";
import { InternshipCard } from "@/components/internships/InternshipCard";
import type { Internship } from "@/types";

export default function SavedPage() {
  const { data: session } = useSession();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [sortBy, setSortBy] = useState<"newest" | "company" | "title">("newest");

  const { data: saved, isLoading } = useQuery({
    queryKey: ["bookmarks", session?.accessToken],
    queryFn: () => usersApi.bookmarks(session!.accessToken!),
    enabled: !!session?.accessToken,
  });

  // Calculate live bookmark metrics
  const stats = useMemo(() => {
    if (!saved) return { total: 0, remote: 0, categories: {} as Record<string, number> };
    const remoteCount = saved.filter(item => item.remote).length;
    const catMap: Record<string, number> = {};
    saved.forEach(item => {
      const cat = item.category || "Other";
      catMap[cat] = (catMap[cat] || 0) + 1;
    });
    return {
      total: saved.length,
      remote: remoteCount,
      categories: catMap
    };
  }, [saved]);

  // Search, filter, and sort list
  const filteredAndSorted = useMemo(() => {
    if (!saved) return [];
    let items = [...saved];

    // Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      items = items.filter(
        item => item.title.toLowerCase().includes(q) || item.company.toLowerCase().includes(q)
      );
    }

    // Category filter
    if (selectedCategory !== "All") {
      items = items.filter(item => (item.category || "Other") === selectedCategory);
    }

    // Sorting logic
    if (sortBy === "company") {
      items.sort((a, b) => a.company.localeCompare(b.company));
    } else if (sortBy === "title") {
      items.sort((a, b) => a.title.localeCompare(b.title));
    } else {
      // Default to "newest" / recently saved (using array order as proxy, or posted date)
      items.reverse();
    }

    return items;
  }, [saved, searchQuery, selectedCategory, sortBy]);

  const categoriesList = useMemo(() => {
    if (!stats.categories) return [];
    return ["All", ...Object.keys(stats.categories)];
  }, [stats.categories]);

  if (!session) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-muted-foreground bg-[#18181b]/40 border border-white/5 rounded-2xl glass max-w-xl mx-auto mt-10">
        <div className="w-14 h-14 rounded-2xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mb-4 text-orange-400">
          <Bookmark className="w-6 h-6" />
        </div>
        <h2 className="text-white font-bold text-base mb-1">Access Saved Collections</h2>
        <p className="text-xs text-muted-foreground max-w-xs text-center mb-6">
          Sign in to save internship opportunities, create personalized collections, and receive custom notifications.
        </p>
        <Link
          href="/login"
          className="bg-orange-600 hover:bg-orange-500 text-white font-bold text-xs px-6 py-2.5 rounded-xl shadow-lg shadow-orange-500/20 transition-all"
        >
          Sign In Now
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-300 text-xs font-semibold mb-2">
            <FolderHeart className="w-3.5 h-3.5 text-orange-400" /> Saved Curation
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white mb-0.5">My Saved Internships</h1>
          <p className="text-muted-foreground text-xs font-semibold">
            Track and monitor the applications you have bookmarked
          </p>
        </div>
      </div>

      {/* Quick stats board */}
      {saved && saved.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-[#18181b]/40 border border-white/5 rounded-2xl p-5 glass flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-orange-400">
              <Bookmark className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Saved Positions</span>
              <p className="text-xl font-black text-white mt-0.5">{stats.total}</p>
            </div>
          </div>

          <div className="bg-[#18181b]/40 border border-white/5 rounded-2xl p-5 glass flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Remote Positions</span>
              <p className="text-xl font-black text-white mt-0.5">{stats.remote}</p>
            </div>
          </div>

          <div className="bg-[#18181b]/40 border border-white/5 rounded-2xl p-5 glass flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Primary Category</span>
              <p className="text-xs font-bold text-white mt-0.5 truncate max-w-[170px]">
                {Object.entries(stats.categories).sort((a, b) => b[1] - a[1])[0]?.[0] || "None"}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Filter and search toolbar */}
      {saved && saved.length > 0 && (
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-white/5 pb-5">
          {/* Left: category chips */}
          <div className="flex flex-wrap items-center gap-1.5">
            {categoriesList.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`text-[10px] font-bold px-3.5 py-1.5 rounded-full border transition-all uppercase tracking-wider ${
                  selectedCategory === cat
                    ? "bg-orange-600 border-transparent text-white shadow-lg shadow-orange-500/15"
                    : "bg-white/5 border-white/5 text-muted-foreground hover:text-white hover:bg-white/10"
                }`}
              >
                {cat} {cat !== "All" && `(${stats.categories[cat] || 0})`}
              </button>
            ))}
          </div>

          {/* Right: Search and Sort toolbar */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            {/* Search inputs */}
            <div className="relative w-full sm:w-60">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search saved items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-[#18181b]/60 border border-white/5 rounded-xl text-xs placeholder:text-muted-foreground text-white focus:outline-none focus:border-orange-500/40"
              />
            </div>

            {/* Sort selectors */}
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <div className="p-2 rounded-xl bg-white/5 border border-white/5 text-orange-400">
                <SlidersHorizontal className="w-3.5 h-3.5" />
              </div>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as "newest" | "company" | "title")}
                className="w-full sm:w-auto bg-[#18181b]/60 border border-white/5 rounded-xl px-3 py-2 text-xs text-muted-foreground hover:text-white focus:outline-none"
              >
                <option value="newest">Recently Saved</option>
                <option value="company">Company Name</option>
                <option value="title">Internship Title</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Main content lists */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-44 bg-card/40 border border-white/5 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : !saved?.length ? (
        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground bg-[#18181b]/40 border border-white/5 rounded-2xl glass text-center max-w-xl mx-auto">
          <Bookmark className="w-12 h-12 mb-4 opacity-20 text-orange-400 animate-pulse" />
          <h3 className="text-white font-bold text-sm mb-1">No Bookmarked Internships</h3>
          <p className="text-xs text-muted-foreground max-w-xs mb-6">
            Find roles that match your interests on our main directory and save them here.
          </p>
          <Link
            href="/internships"
            className="inline-flex items-center gap-1.5 bg-orange-600 hover:bg-orange-500 text-white font-bold text-xs px-5 py-2.5 rounded-xl shadow-lg shadow-orange-500/20 transition-all"
          >
            Explore Internships
          </Link>
        </div>
      ) : filteredAndSorted.length === 0 ? (
        <div className="text-center py-16 text-muted-foreground bg-[#18181b]/40 border border-white/5 rounded-2xl glass">
          <p className="text-xs mb-2">No bookmarks match your search or filter preferences.</p>
          <button
            onClick={() => {
              setSearchQuery("");
              setSelectedCategory("All");
            }}
            className="text-xs font-semibold text-orange-400 hover:underline"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <motion.div layout className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          <AnimatePresence mode="popLayout">
            {filteredAndSorted.map((internship, i) => (
              <motion.div
                key={internship._id || internship.external_id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3, delay: 0.03 * i }}
              >
                <InternshipCard internship={internship} />
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      )}
    </div>
  );
}
