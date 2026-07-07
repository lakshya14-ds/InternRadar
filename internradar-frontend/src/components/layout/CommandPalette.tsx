"use client";

import * as React from "react";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import * as Dialog from "@radix-ui/react-dialog";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Briefcase, Bookmark, LayoutDashboard, User, ArrowRight, CornerDownLeft, Command, Sparkles } from "lucide-react";
import { internshipsApi } from "@/lib/api";
import type { Internship } from "@/types";

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Internship[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const router = useRouter();
  const listRef = useRef<HTMLDivElement>(null);

  // Keyboard shortcut listener for Ctrl + K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Reactive search query fetching
  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }
    const delayDebounce = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await internshipsApi.search({ title: query, limit: 5 });
        setResults(data.results || []);
        setSelectedIndex(0);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }, 200);

    return () => clearTimeout(delayDebounce);
  }, [query]);

  const handleNavigate = (path: string) => {
    router.push(path);
    setOpen(false);
    setQuery("");
  };

  const handleSelectResult = (item: Internship) => {
    handleNavigate(`/internships/${item._id || item.id}`);
  };

  // Keyboard navigation within suggestions/results
  const handleKeyDown = (e: React.KeyboardEvent) => {
    const totalItems = query ? results.length : quickActions.length + trendingCategories.length;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % totalItems);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + totalItems) % totalItems);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (query && results[selectedIndex]) {
        handleSelectResult(results[selectedIndex]);
      } else if (!query) {
        const combined = [...quickActions, ...trendingCategories];
        const selected = combined[selectedIndex];
        if (selected) {
          handleNavigate(selected.href);
        }
      }
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  // Auto scroll into view for keyboard selection
  useEffect(() => {
    if (listRef.current) {
      const activeElement = listRef.current.querySelector("[data-active='true']");
      if (activeElement) {
        activeElement.scrollIntoView({ block: "nearest" });
      }
    }
  }, [selectedIndex]);

  const quickActions = [
    { label: "Go to Dashboard", href: "/dashboard", icon: LayoutDashboard, desc: "System Status & Insights" },
    { label: "Browse Internships", href: "/internships", icon: Briefcase, desc: "Search and filter roles" },
    { label: "Saved Bookmarks", href: "/saved", icon: Bookmark, desc: "Access your collections" },
    { label: "Profile Preferences", href: "/profile", icon: User, desc: "Notification settings" },
  ];

  const trendingCategories = [
    { label: "Software Engineering", href: "/internships?category=Software+Engineering", icon: Sparkles, desc: "Filter by Tech Roles" },
    { label: "AI & Deep Tech", href: "/internships?category=AI", icon: Sparkles, desc: "Filter by Artificial Intelligence" },
    { label: "Data Science", href: "/internships?category=Data+Science", icon: Sparkles, desc: "Filter by Analytics Roles" },
    { label: "UI/UX Design", href: "/internships?category=UI%2FUX", icon: Sparkles, desc: "Filter by Creative Design" },
  ];

  return (
    <>
      {/* Visual indicator in layout */}
      <button
        onClick={() => setOpen(true)}
        className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#120f18]/40 hover:bg-[#1c1826]/70 border border-white/5 hover:border-orange-500/20 hover:shadow-lg hover:shadow-orange-500/5 transition-all duration-300 text-xs text-muted-foreground select-none"
      >
        <Search className="w-3.5 h-3.5 text-orange-400/80" />
        <span>Search internship database...</span>
        <kbd className="pointer-events-none inline-flex h-4 select-none items-center gap-0.5 rounded border border-white/10 bg-white/5 px-1.5 font-mono text-[9px] font-medium text-muted-foreground ml-4">
          <span className="text-[10px]">⌘</span>K
        </kbd>
      </button>

      <Dialog.Root open={open} onOpenChange={setOpen}>
        <Dialog.Portal>
          <AnimatePresence>
            {open && (
              <>
                <Dialog.Overlay asChild>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm"
                  />
                </Dialog.Overlay>

                <Dialog.Content asChild>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.98, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.98, y: -10 }}
                    transition={{ duration: 0.18, ease: "easeOut" }}
                    onKeyDown={handleKeyDown}
                    className="fixed left-[50%] top-[15%] translate-x-[-50%] z-50 w-full max-w-lg overflow-hidden rounded-2xl border border-white/5 bg-[#0a080f] glass shadow-2xl focus:outline-none"
                  >
                    <Dialog.Title className="sr-only">Search Dialog</Dialog.Title>
                    <Dialog.Description className="sr-only">
                      Search internships, companies, and roles
                    </Dialog.Description>
                    <div className="flex items-center border-b border-white/5 px-4 py-3 bg-[#110e16]/50">
                      <Search className="w-4 h-4 mr-3 text-orange-400" />
                      <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search roles, tech stack, or hiring firms..."
                        className="flex-1 bg-transparent border-0 text-sm placeholder:text-muted-foreground/60 focus:outline-none text-foreground"
                        autoFocus
                      />
                      <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-0.5 rounded border border-white/10 bg-white/5 px-1.5 font-mono text-[9px] font-medium text-muted-foreground">
                        ESC
                      </kbd>
                    </div>

                    <div ref={listRef} className="max-h-[360px] overflow-y-auto p-2 hide-scrollbar">
                      {loading && (
                        <div className="flex items-center justify-center py-10 text-muted-foreground text-xs gap-2">
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ repeat: Infinity, ease: "linear", duration: 1 }}
                            className="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full"
                          />
                          <span>Searching listings...</span>
                        </div>
                      )}

                      {!loading && query && results.length === 0 && (
                        <div className="text-center py-10 text-muted-foreground text-xs">
                          No matching internships found for &quot;{query}&quot;
                        </div>
                      )}

                      {!loading && query && results.length > 0 && (
                        <div className="space-y-1">
                          <p className="text-[9px] font-bold text-muted-foreground/50 px-2 py-1.5 uppercase tracking-wider">
                            Opportunities
                          </p>
                          {results.map((item, idx) => {
                            const active = selectedIndex === idx;
                            return (
                              <button
                                key={item._id || item.id}
                                onClick={() => handleSelectResult(item)}
                                data-active={active}
                                className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-left transition-all ${
                                  active
                                    ? "bg-orange-500/10 border border-orange-500/20 text-orange-300"
                                    : "border border-transparent hover:bg-white/[0.02] text-muted-foreground hover:text-foreground"
                                }`}
                              >
                                <div className="flex items-center gap-3">
                                  <div className="w-8 h-8 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-orange-400 font-extrabold text-xs shrink-0">
                                    {item.company.charAt(0).toUpperCase()}
                                  </div>
                                  <div className="min-w-0">
                                    <p className="text-xs font-bold text-white truncate">
                                      {item.title}
                                    </p>
                                    <p className="text-[10px] text-muted-foreground truncate mt-0.5">
                                      {item.company} &bull; {item.location}
                                    </p>
                                  </div>
                                </div>
                                {active && <CornerDownLeft className="w-3.5 h-3.5 text-orange-400 shrink-0 opacity-80" />}
                              </button>
                            );
                          })}
                        </div>
                      )}

                      {!query && (
                        <div className="space-y-4">
                          <div>
                            <p className="text-[9px] font-bold text-muted-foreground/50 px-2 py-1.5 uppercase tracking-wider">
                              Quick Navigation
                            </p>
                            <div className="space-y-0.5">
                              {quickActions.map((action, idx) => {
                                const active = selectedIndex === idx;
                                return (
                                  <button
                                    key={action.href}
                                    onClick={() => handleNavigate(action.href)}
                                    data-active={active}
                                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left transition-all ${
                                      active
                                        ? "bg-orange-500/10 border border-orange-500/20 text-orange-300"
                                        : "border border-transparent hover:bg-white/[0.02] text-muted-foreground hover:text-foreground"
                                    }`}
                                  >
                                    <div className="flex items-center gap-3">
                                      <action.icon className="w-4 h-4 text-orange-400 shrink-0" />
                                      <div>
                                        <p className="text-xs font-bold text-gray-200">{action.label}</p>
                                        <p className="text-[10px] text-muted-foreground mt-0.5">{action.desc}</p>
                                      </div>
                                    </div>
                                    {active && <ArrowRight className="w-3.5 h-3.5 text-orange-400" />}
                                  </button>
                                );
                              })}
                            </div>
                          </div>

                          <div>
                            <p className="text-[9px] font-bold text-muted-foreground/50 px-2 py-1.5 uppercase tracking-wider">
                              Trending Filters
                            </p>
                            <div className="space-y-0.5">
                              {trendingCategories.map((cat, idx) => {
                                const relativeIdx = idx + quickActions.length;
                                const active = selectedIndex === relativeIdx;
                                return (
                                  <button
                                    key={cat.href}
                                    onClick={() => handleNavigate(cat.href)}
                                    data-active={active}
                                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-left transition-all ${
                                      active
                                        ? "bg-orange-500/10 border border-orange-500/20 text-orange-300"
                                        : "border border-transparent hover:bg-white/[0.02] text-muted-foreground hover:text-foreground"
                                    }`}
                                  >
                                    <div className="flex items-center gap-3">
                                      <cat.icon className="w-4 h-4 text-amber-500 shrink-0" />
                                      <div>
                                        <p className="text-xs font-bold text-gray-200">{cat.label}</p>
                                        <p className="text-[10px] text-muted-foreground mt-0.5">{cat.desc}</p>
                                      </div>
                                    </div>
                                    {active && <ArrowRight className="w-3.5 h-3.5 text-orange-400" />}
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                </Dialog.Content>
              </>
            )}
          </AnimatePresence>
        </Dialog.Portal>
      </Dialog.Root>
    </>
  );
}
