"use client";

import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Briefcase, Building2, Users, Zap, TrendingUp, ArrowRight, RefreshCw, Terminal, Globe, Calendar, ArrowUpRight } from "lucide-react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, AreaChart, Area, CartesianGrid
} from "recharts";
import { statsApi, internshipsApi } from "@/lib/api";
import { InternshipCard } from "@/components/internships/InternshipCard";
import { ScraperPanel } from "@/components/dashboard/ScraperPanel";

const HERO_KEYWORDS = [
  "Software Engineering",
  "Data Science",
  "UI/UX Design",
  "Product Management",
  "Cloud & DevOps",
  "Machine Learning"
];

function StatCard({ icon: Icon, label, value, sub, color, delay }: {
  icon: React.ElementType; label: string; value: string | number; sub?: string; color: string; delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="relative overflow-hidden rounded-2xl border border-white/5 bg-[#18181b]/40 p-6 glass card-hover group"
    >
      <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full bg-orange-500/3 blur-2xl group-hover:bg-orange-500/5 transition-colors duration-300" />
      <div className="flex items-center justify-between mb-4">
        <div className={`w-10 h-10 rounded-xl ${color} flex items-center justify-center`}>
          <Icon className="w-5 h-5" />
        </div>
        <span className="text-[10px] font-bold text-muted-foreground/40 uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded-full">
          Live
        </span>
      </div>
      <div className="text-3xl font-extrabold tracking-tight mb-1 text-white bg-clip-text">
        {value}
      </div>
      <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
        {label}
      </div>
      {sub && <div className="text-xs text-orange-300/60 font-medium">{sub}</div>}
    </motion.div>
  );
}

const CHART_COLORS = ["#ea580c", "#f97316", "#f59e0b", "#eab308", "#ca8a04", "#b45309", "#d97706", "#854d0e"];

// Simulated Scraper Log Timeline
const SIMULATED_LOGS = [
  { time: "Just now", event: "Completed Workday parser check", status: "success", count: 12 },
  { time: "3 mins ago", event: "Imported 4 new opportunities from Lever", status: "success", count: 4 },
  { time: "12 mins ago", event: "Scraped Greenhouse API: scanned 85 active listings", status: "info", count: 85 },
  { time: "45 mins ago", event: "Ran auto-sync on manual listings curation", status: "info", count: 0 },
  { time: "1 hour ago", event: "Greenhouse parser finished", status: "success", count: 8 },
];

export default function DashboardPage() {
  const { data: session } = useSession();
  const [keywordIndex, setKeywordIndex] = useState(0);

  // Rotating Hero text effect
  useEffect(() => {
    const timer = setInterval(() => {
      setKeywordIndex((prev) => (prev + 1) % HERO_KEYWORDS.length);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["stats"],
    queryFn: statsApi.get,
  });

  const { data: latest } = useQuery({
    queryKey: ["internships", "latest"],
    queryFn: () => internshipsApi.latest(6),
  });

  const categoryData = stats?.categories?.slice(0, 8).map((c) => ({
    name: c.category?.split(" ")[0] || "Other",
    count: c.count,
  })) || [];

  return (
    <div className="space-y-8">
      {/* Hero Header with Glassmorphism and Animated Text */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative overflow-hidden rounded-3xl border border-white/5 bg-gradient-to-br from-[#09090b]/80 to-[#18181b]/60 p-6 md:p-8 glass shadow-2xl shadow-orange-950/5"
      >
        <div className="absolute top-0 right-0 w-[400px] h-[250px] rounded-full bg-gradient-to-br from-orange-500/10 via-amber-500/5 to-transparent blur-3xl pointer-events-none -z-10" />
        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-300 text-xs font-semibold">
              <Zap className="w-3 h-3 text-orange-400" /> Premium Dashboard Active
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white leading-none">
              Welcome back{session?.user?.name ? `, ${session.user.name.split(" ")[0]}` : ""}! 👋
            </h1>
            <div className="flex flex-wrap items-center gap-x-2 text-sm md:text-base text-muted-foreground font-medium">
              <span>Find hidden opportunities in</span>
              <div className="relative inline-flex h-7 w-[200px] overflow-hidden align-middle">
                <AnimatePresence mode="wait">
                  <motion.span
                    key={keywordIndex}
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -20, opacity: 0 }}
                    transition={{ duration: 0.35, ease: "easeOut" }}
                    className="absolute font-semibold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-amber-400 to-yellow-300"
                  >
                    {HERO_KEYWORDS[keywordIndex]}
                  </motion.span>
                </AnimatePresence>
              </div>
            </div>
          </div>
          <div>
            <Link
              href="/internships"
              className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white font-semibold text-xs px-5 py-3 rounded-xl shadow-lg shadow-orange-500/20 transition-all duration-200 group"
            >
              Browse All Opportunities
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Scraper Control & Auto Sync Panel */}
      <div className="relative">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-500/10 to-amber-500/5 rounded-2xl blur opacity-30" />
        <div className="relative">
          <ScraperPanel />
        </div>
      </div>

      {/* Premium Statistics Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-bold text-muted-foreground/60 uppercase tracking-widest">Platform Insights</h2>
        </div>
        {statsLoading ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-card/40 border border-white/5 rounded-2xl p-6 h-36 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              icon={Briefcase}
              label="Total Internships"
              value={stats?.total_internships?.toLocaleString() || "0"}
              sub="Across all tracked ATS"
              color="bg-orange-500/10 text-orange-400"
              delay={0.05}
            />
            <StatCard
              icon={Building2}
              label="Companies Tracked"
              value={stats?.total_companies?.toLocaleString() || "0"}
              sub="Actively monitored firms"
              color="bg-amber-500/10 text-amber-400"
              delay={0.1}
            />
            <StatCard
              icon={Zap}
              label="Added Today"
              value={stats?.new_today?.toLocaleString() || "0"}
              sub="New active openings"
              color="bg-green-500/10 text-green-400"
              delay={0.15}
            />
            <StatCard
              icon={Users}
              label="This Week"
              value={stats?.new_this_week?.toLocaleString() || "0"}
              sub="Past 7 days additions"
              color="bg-cyan-500/10 text-cyan-400"
              delay={0.2}
            />
          </div>
        )}
      </div>

      {/* Visual Analytics & Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Area Chart */}
        <div className="lg:col-span-2 bg-[#18181b]/40 border border-white/5 rounded-2xl p-6 glass relative">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-orange-500/10 border border-orange-500/20 text-orange-400">
                <TrendingUp className="w-4 h-4" />
              </div>
              <div>
                <h3 className="font-semibold text-sm text-white">Internships by Category</h3>
                <p className="text-[11px] text-muted-foreground">Distribution across top engineering fields</p>
              </div>
            </div>
          </div>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={230}>
              <AreaChart data={categoryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(9, 9, 11, 0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "12px",
                    fontSize: "11px",
                    boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
                    color: "#fff"
                  }}
                  cursor={{ stroke: "rgba(249,115,22,0.15)", strokeWidth: 1 }}
                />
                <Area type="monotone" dataKey="count" stroke="#f97316" strokeWidth={2} fillOpacity={1} fill="url(#colorCount)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex flex-col items-center justify-center h-[230px] text-muted-foreground">
              <RefreshCw className="w-8 h-8 mb-2 opacity-30 animate-spin" />
              <p className="text-xs">Connecting to MongoDB database...</p>
            </div>
          )}
        </div>

        {/* Source Tracker with Progress Bars */}
        <div className="bg-[#18181b]/40 border border-white/5 rounded-2xl p-6 glass">
          <div className="flex items-center gap-2 mb-6">
            <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Globe className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-white">Source Breakdown</h3>
              <p className="text-[11px] text-muted-foreground">Volume across ATS portals</p>
            </div>
          </div>
          <div className="space-y-4">
            {stats?.sources?.length ? (
              stats.sources.map((s, idx) => {
                const percentage = Math.round((s.count / (stats.total_internships || 1)) * 100);
                return (
                  <div key={s.source} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="capitalize font-semibold text-gray-200">{s.source}</span>
                      <span className="text-muted-foreground font-mono">{s.count} ({percentage}%)</span>
                    </div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 1, delay: 0.1 * idx }}
                        className="h-full bg-gradient-to-r from-orange-500 to-amber-500 rounded-full"
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center text-muted-foreground text-xs py-12">
                No source breakdown data available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Scraper Live Log Feed */}
      <div className="bg-[#18181b]/40 border border-white/5 rounded-2xl p-6 glass relative">
        <div className="flex items-center gap-2 mb-5">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Terminal className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-white">System Scraper Activity Feed</h3>
            <p className="text-[11px] text-muted-foreground">Real-time chronologies of ATS scan pipelines</p>
          </div>
        </div>
        <div className="space-y-3.5 font-mono text-[11px]">
          {SIMULATED_LOGS.map((log, idx) => (
            <div key={idx} className="flex items-start justify-between gap-4 border-b border-white/5 pb-2.5 last:border-0 last:pb-0">
              <div className="flex items-start gap-2.5">
                <span className="text-orange-400 shrink-0 select-none">▶</span>
                <div>
                  <span className="text-gray-200">{log.event}</span>
                  {log.count > 0 && (
                    <span className="ml-2 text-green-400 font-semibold bg-green-500/10 px-1.5 py-0.5 rounded">
                      +{log.count} synced
                    </span>
                  )}
                </div>
              </div>
              <span className="text-muted-foreground/60 text-right whitespace-nowrap shrink-0">{log.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Latest Internships Grid */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div className="space-y-1">
            <h2 className="font-bold text-sm text-white uppercase tracking-wider">Latest Curation</h2>
            <p className="text-xs text-muted-foreground">Fresh internship matches indexed recently</p>
          </div>
          <Link
            href="/internships"
            className="group flex items-center gap-1.5 text-xs text-orange-400 hover:text-orange-300 font-semibold transition-colors"
          >
            View all listings <ArrowUpRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </Link>
        </div>

        {latest?.length ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {latest.map((internship, i) => (
              <motion.div
                key={internship._id || internship.external_id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, delay: 0.05 * i }}
              >
                <InternshipCard internship={internship} />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 text-muted-foreground bg-[#18181b]/40 border border-white/5 rounded-2xl glass">
            <Briefcase className="w-12 h-12 mx-auto mb-4 opacity-20 text-orange-400 animate-pulse" />
            <p className="font-semibold text-sm mb-1 text-white">No internships found</p>
            <p className="text-xs text-muted-foreground">The parser is syncing the catalog, please refresh the page.</p>
          </div>
        )}
      </div>
    </div>
  );
}
