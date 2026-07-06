"use client";

import * as React from "react";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import * as Dialog from "@radix-ui/react-dialog";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Briefcase, Bookmark, LayoutDashboard, Database, User, ArrowRight, CornerDownLeft } from "lucide-react";
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
    { label: "Go to Dashboard", href: "/dashboard", icon: LayoutDashboard, desc: "Overview & Scraper" },
    { label: "Browse Internships", href: "/internships", icon: Briefcase, desc: "Search and apply" },
    { label: "Saved Bookmarks", href: "/saved", icon: Bookmark, desc: "Your collections" },
    { label: "Profile & Preferences", href: "/profile", icon: User, desc: "Manage settings" },
  ];

  const trendingCategories = [
    { label: "Software Engineering", href: "/internships?category=Software+Engineering", icon: Briefcase, desc: "Quick Filter" },
    { label: "AI", href: "/internships?category=AI", icon: Briefcase, desc: "Quick Filter" },
    { label: "Data Science", href: "/internships?category=Data+Science", icon: Briefcase, desc: "Quick Filter" },
    { label: "UI/UX Design", href: "/internships?category=UI%2FUX", icon: Briefcase, desc: "Quick Filter" },
  ];

  return (
    <>
      {/* Visual indicator in layout */}
      <button
        onClick={() => setOpen(true)}
        className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-card/40 hover:bg-card/80 border border-white/5 hover:border-white/10 transition-all duration-200 text-xs text-muted-foreground select-none"
      >
        <Search className="w-3.5 h-3.5" />
        <span>Search...</span>
        <kbd className="pointer-events-none inline-flex h-4 select-none items-center gap-0.5 rounded border border-white/10 bg-white/5 px-1.5 font-mono text-[10px] font-medium text-muted-foreground ml-2">
          <span className="text-xs">⌘</span>K
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
                    className="fixed inset-0 z-50 bg-black/60 backdrop-blur-md"
                  />
                </Dialog.Overlay>

                <Dialog.Content asChild>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.97, y: -20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.97, y: -20 }}
                    transition={{ duration: 0.15, ease: "easeOut" }}
                    onKeyDown={handleKeyDown}
                    className="fixed left-[50%] top-[20%] translate-x-[-50%] z-50 w-full max-w-xl overflow-hidden rounded-xl border border-white/10 bg-[#09090b]/95 glass shadow-2xl focus:outline-none"
                  >
                    <Dialog.Title className="sr-only">Search Dialog</Dialog.Title>
                    <Dialog.Description className="sr-only">
                      Search internships, companies, and roles
                    </Dialog.Description>
                    <div className="flex items-center border-b border-white/5 px-4 py-3 bg-[#18181b]/40">
                      <Search className="w-4 h-4 mr-3 text-muted-foreground" />
                      <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search internships, companies, roles..."
                        className="flex-1 bg-transparent border-0 text-sm placeholder:text-muted-foreground focus:outline-none text-foreground"
                        autoFocus
                      />
                      <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-0.5 rounded border border-white/10 bg-white/5 px-1.5 font-mono text-[9px] font-medium text-muted-foreground">
                        ESC
                      </kbd>
                    </div>

                    <div ref={listRef} className="max-h-[350px] overflow-y-auto p-2">
                      {loading && (
                        <div className="flex items-center justify-center py-10 text-muted-foreground text-xs gap-2">
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ repeat: Infinity, ease: "linear", duration: 1 }}
                            className="w-3.5 h-3.5 border-2 border-orange-500 border-t-transparent rounded-full"
                          />
                          Searching Internships...
                        </div>
                      )}

                      {!loading && query && results.length === 0 && (
                        <div className="text-center py-10 text-muted-foreground text-xs">
                          No matching internships found for "{query}"
                        </div>
                      )}

                      {!loading && query && results.length > 0 && (
                        <div className="space-y-1">
                          <p className="text-[10px] font-semibold text-muted-foreground px-2 py-1 uppercase tracking-wider">
                            Opportunities
                          </p>
                          {results.map((item, idx) => {
                            const active = selectedIndex === idx;
                            return (
                              <button
                                key={item._id || item.id}
                                onClick={() => handleSelectResult(item)}
                                data-active={active}
                                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-left transition-all ${
                                  active
                                    ? "bg-orange-600/10 border-orange-500/20 text-orange-300"
                                    : "hover:bg-white/5 text-muted-foreground hover:text-foreground"
                                }`}
                              >
                                <div className="flex items-center gap-3">
                                  <div className="w-7 h-7 rounded bg-orange-500/10 flex items-center justify-center text-orange-400 font-bold text-xs">
                                    {item.company.charAt(0)}
                                  </div>
                                  <div>
                                    <p className="text-xs font-semibold text-foreground line-clamp-1">
                                      {item.title}
                                    </p>
                                    <p className="text-[10px] text-muted-foreground line-clamp-1">
                                      {item.company} &bull; {item.location}
                                    </p>
                                  </div>
                                </div>
                                {active && <CornerDownLeft className="w-3.5 h-3.5 text-orange-400 opacity-60" />}
                              </button>
                            );
                          })}
                        </div>
                      )}

                      {!query && (
                        <div className="space-y-4">
                          <div>
                            <p className="text-[10px] font-semibold text-muted-foreground px-2 py-1 uppercase tracking-wider">
                              Navigation & Actions
                            </p>
                            <div className="space-y-0.5">
                              {quickActions.map((action, idx) => {
                                const active = selectedIndex === idx;
                                return (
                                  <button
                                    key={action.href}
                                    onClick={() => handleNavigate(action.href)}
                                    data-active={active}
                                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-all ${
                                      active
                                        ? "bg-orange-600/10 border-orange-500/20 text-orange-300"
                                        : "hover:bg-white/5 text-muted-foreground hover:text-foreground"
                                    }`}
                                  >
                                    <div className="flex items-center gap-3">
                                      <action.icon className="w-4 h-4 text-orange-400" />
                                      <div>
                                        <p className="text-xs font-semibold">{action.label}</p>
                                        <p className="text-[10px] text-muted-foreground">{action.desc}</p>
                                      </div>
                                    </div>
                                    {active && <ArrowRight className="w-3.5 h-3.5 text-orange-400" />}
                                  </button>
                                );
                              })}
                            </div>
                          </div>

                          <div>
                            <p className="text-[10px] font-semibold text-muted-foreground px-2 py-1 uppercase tracking-wider">
                              Trending Quick Filters
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
                                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-all ${
                                      active
                                        ? "bg-orange-600/10 border-orange-500/20 text-orange-300"
                                        : "hover:bg-white/5 text-muted-foreground hover:text-foreground"
                                    }`}
                                  >
                                    <div className="flex items-center gap-3">
                                      <div className="w-2 h-2 rounded-full bg-amber-400" />
                                      <div>
                                        <p className="text-xs font-semibold">{cat.label}</p>
                                        <p className="text-[10px] text-muted-foreground">{cat.desc}</p>
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
