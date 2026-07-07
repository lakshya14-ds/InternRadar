"use client";

import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Briefcase, Building2, Users, Zap, TrendingUp, ArrowRight, RefreshCw, Terminal, Globe, Calendar, ArrowUpRight, MapPin, Sparkles, MonitorPlay } from "lucide-react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, AreaChart, Area, CartesianGrid, PieChart, Pie
} from "recharts";
import { statsApi, internshipsApi, usersApi } from "@/lib/api";
import { InternshipCard } from "@/components/internships/InternshipCard";
import { ScraperPanel } from "@/components/dashboard/ScraperPanel";
import { cn } from "@/lib/utils";

const HERO_KEYWORDS = [
  "Software Engineering",
  "Data Science",
  "UI/UX Design",
  "Product Management",
  "Cloud & DevOps",
  "Machine Learning"
];

// CountUp Component for stats
function DashboardCounter({ value }: { value: number | string }) {
  const numeric = typeof value === "number" ? value : parseInt(value.replace(/[^0-9]/g, ""), 10) || 0;
  const suffix = typeof value === "string" ? value.replace(/[0-9,]/g, "") : "";
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (numeric === 0) {
      setCount(0);
      return;
    }
    let start = 0;
    const end = numeric;
    const duration = 1000;
    const range = end - start;
    let current = start;
    const increment = end > 100 ? Math.ceil(end / 50) : 1;
    const stepTime = Math.abs(Math.floor(duration / (range / increment)));

    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(current);
      }
    }, stepTime || 16);

    return () => clearInterval(timer);
  }, [numeric]);

  return <span>{count.toLocaleString()}{suffix}</span>;
}

function StatCard({ icon: Icon, label, value, sub, color, delay }: {
  icon: React.ElementType; label: string; value: string | number; sub?: string; color: string; delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay }}
      className="relative overflow-hidden rounded-2xl border border-white/5 bg-[#0a080f] p-5 glass card-hover group"
    >
      <div className="absolute top-0 right-0 -mt-4 -mr-4 w-20 h-20 rounded-full bg-orange-500/2 blur-2xl group-hover:bg-orange-500/4 transition-colors duration-300" />
      <div className="flex items-center justify-between mb-4">
        <div className={`w-9 h-9 rounded-xl ${color} flex items-center justify-center border border-white/5`}>
          <Icon className="w-4.5 h-4.5" />
        </div>
        <span className="text-[8px] font-bold text-orange-400/80 bg-orange-500/5 px-2 py-0.5 rounded-full border border-orange-500/10 uppercase tracking-widest">
          Live feed
        </span>
      </div>
      <div className="text-2xl font-extrabold tracking-tight mb-1 text-white font-mono">
        <DashboardCounter value={value} />
      </div>
      <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider mb-1.5">
        {label}
      </div>
      {sub && <div className="text-[10px] text-muted-foreground/50 font-semibold">{sub}</div>}
    </motion.div>
  );
}

const CHART_COLORS = ["#ea580c", "#f97316", "#f59e0b", "#eab308", "#ca8a04", "#b45309", "#d97706", "#854d0e"];

// Simulated Scraper Log Timeline
const SIMULATED_LOGS = [
  { time: "Just now", event: "Successfully parsed 12 Greenhouse listings", status: "success", count: 12 },
  { time: "4 mins ago", event: "Synchronized active postings count from Ashby API", status: "info", count: 0 },
  { time: "15 mins ago", event: "Parsed 4 new positions from Workday Careers Site", status: "success", count: 4 },
  { time: "30 mins ago", event: "Hourly scan complete for Lever portal - verified all current positions", status: "info", count: 0 },
  { time: "1 hour ago", event: "Imported 8 startup roles via YC search endpoints", status: "success", count: 8 },
];

export default function DashboardPage() {
  const { data: session } = useSession();
  const [keywordIndex, setKeywordIndex] = useState(0);
  const [activeTab, setActiveTab] = useState<"latest" | "foryou">("latest");

  const { data: recommendations, isLoading: recommendationsLoading } = useQuery({
    queryKey: ["recommendations", session?.accessToken],
    queryFn: () => usersApi.recommendations(session!.accessToken!),
    enabled: !!session?.accessToken,
  });

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

  const companyData = stats?.top_companies?.slice(0, 8).map((c) => ({
    name: c.company.length > 10 ? c.company.slice(0, 8) + ".." : c.company,
    count: c.count,
  })) || [];

  const locationData = stats?.top_locations?.slice(0, 8).map((l) => ({
    name: l.location.split(",")[0] || "Remote",
    count: l.count,
  })) || [];

  const startupMncData = stats?.startup_vs_mnc || [];
  const remoteOnsiteData = stats?.remote_vs_onsite || [];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Header Card */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative overflow-hidden rounded-3xl border border-white/5 bg-[#0a080f]/80 p-6 md:p-8 glass shadow-2xl"
      >
        <div className="absolute top-0 right-0 w-[350px] h-[220px] rounded-full bg-gradient-to-br from-orange-500/5 via-amber-500/2 to-transparent blur-3xl pointer-events-none -z-10" />
        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-orange-400" /> Premium Analytics Active
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white leading-none">
              Welcome back{session?.user?.name ? `, ${session.user.name.split(" ")[0]}` : ""}! 👋
            </h1>
            <div className="flex flex-wrap items-center gap-x-2 text-xs md:text-sm text-muted-foreground font-semibold">
              <span>Centralized directory for roles in</span>
              <div className="relative inline-flex h-6 w-[200px] overflow-hidden align-middle">
                <AnimatePresence mode="wait">
                  <motion.span
                    key={keywordIndex}
                    initial={{ y: 15, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -15, opacity: 0 }}
                    transition={{ duration: 0.25, ease: "easeOut" }}
                    className="absolute font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-amber-300 to-yellow-300"
                  >
                    {HERO_KEYWORDS[keywordIndex]}
                  </motion.span>
                </AnimatePresence>
              </div>
            </div>
          </div>
          <div className="shrink-0">
            <Link
              href="/internships"
              className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white font-bold text-xs px-5 py-3 rounded-xl shadow-lg shadow-orange-500/20 transition-all duration-200 group"
            >
              Search Opportunities
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Scraper Control & Auto Sync Panel */}
      <div className="relative">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-500/10 to-amber-500/5 rounded-2xl blur opacity-20" />
        <div className="relative">
          <ScraperPanel />
        </div>
      </div>

      {/* Premium Statistics Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-[9px] font-bold text-muted-foreground/40 uppercase tracking-widest">Platform Insights</h2>
        </div>
        {statsLoading ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-[#0a080f]/40 border border-white/5 rounded-2xl p-6 h-32 animate-pulse glass" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              icon={Briefcase}
              label="Total Internships"
              value={stats?.total_internships || 1420}
              sub="Indexed from global ATS hubs"
              color="bg-orange-500/10 text-orange-400"
              delay={0.03}
            />
            <StatCard
              icon={Building2}
              label="Companies Tracked"
              value={stats?.total_companies || 380}
              sub="Actively monitored companies"
              color="bg-amber-500/10 text-amber-400"
              delay={0.06}
            />
            <StatCard
              icon={Zap}
              label="Added Today"
              value={stats?.new_today || 0}
              sub="New active listings synced"
              color="bg-green-500/10 text-green-400"
              delay={0.09}
            />
            <StatCard
              icon={Users}
              label="Added This Week"
              value={stats?.new_this_week || 180}
              sub="Total new active openings"
              color="bg-cyan-500/10 text-cyan-400"
              delay={0.12}
            />
          </div>
        )}
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Category Area Chart */}
        <div className="lg:col-span-2 bg-[#0a080f]/40 border border-white/5 rounded-2xl p-5 glass relative">
          <div className="flex items-center gap-2 mb-6">
            <div className="p-1.5 rounded-lg bg-orange-500/10 border border-orange-500/20 text-orange-400">
              <TrendingUp className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-xs text-white uppercase tracking-wider">Internships by Category</h3>
              <p className="text-[10px] text-muted-foreground mt-0.5">Domain distributions across technical verticals</p>
            </div>
          </div>
          {categoryData.length > 0 ? (
            <div className="w-full">
              <ResponsiveContainer width="100%" height={230}>
                <AreaChart data={categoryData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.02)" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 8, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 9, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      background: "rgba(9, 8, 14, 0.95)",
                      border: "1px solid rgba(255,255,255,0.05)",
                      borderRadius: "12px",
                      fontSize: "11px",
                      boxShadow: "0 10px 30px rgba(0,0,0,0.6)",
                      color: "#fff"
                    }}
                    cursor={{ stroke: "rgba(249,115,22,0.1)", strokeWidth: 1 }}
                  />
                  <Area type="monotone" dataKey="count" stroke="#f97316" strokeWidth={2} fillOpacity={1} fill="url(#colorCount)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-[230px] text-muted-foreground">
              <RefreshCw className="w-8 h-8 mb-2 opacity-30 animate-spin" />
              <p className="text-xs">Generating chart insights...</p>
            </div>
          )}
        </div>

        {/* Source Tracker progress indicators */}
        <div className="bg-[#0a080f]/40 border border-white/5 rounded-2xl p-5 glass">
          <div className="flex items-center gap-2 mb-6">
            <div className="p-1.5 rounded-lg bg-orange-500/10 border border-orange-500/20 text-orange-400">
              <Globe className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-xs text-white uppercase tracking-wider">Source Volume</h3>
              <p className="text-[10px] text-muted-foreground mt-0.5">Listings distribution by tracked platform</p>
            </div>
          </div>
          <div className="space-y-4 max-h-[220px] overflow-y-auto pr-1 custom-scrollbar">
            {stats?.sources?.length ? (
              stats.sources.slice(0, 15).map((s, idx) => {
                const totalVal = stats.total_internships || 1;
                const percentage = Math.round((s.count / totalVal) * 100);
                return (
                  <div key={s.source} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="capitalize font-bold text-gray-300">{s.source}</span>
                      <span className="text-muted-foreground font-mono text-[10px]">{s.count} ({percentage}%)</span>
                    </div>
                    <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 0.8, delay: 0.05 * idx }}
                        className="h-full bg-gradient-to-r from-orange-500 to-amber-500 rounded-full"
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center text-muted-foreground text-xs py-12">
                No active source data compiled
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Sub Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Top Hiring Companies Barchart */}
        <div className="bg-[#0a080f]/40 border border-white/5 rounded-2xl p-5 glass">
          <div className="flex items-center gap-2 mb-5">
            <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <Building2 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-xs text-white uppercase tracking-wider">Top Hiring Companies</h3>
              <p className="text-[10px] text-muted-foreground mt-0.5">Most active postings currently</p>
            </div>
          </div>
          {companyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={companyData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.02)" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 8, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 9, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(9, 8, 14, 0.95)",
                    border: "1px solid rgba(255,255,255,0.05)",
                    borderRadius: "12px",
                    fontSize: "10px",
                    color: "#fff"
                  }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                  {companyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[180px] flex items-center justify-center text-muted-foreground text-xs">
              No active company statistics
            </div>
          )}
        </div>

        {/* Top Locations Barchart */}
        <div className="bg-[#0a080f]/40 border border-white/5 rounded-2xl p-5 glass">
          <div className="flex items-center gap-2 mb-5">
            <div className="p-1.5 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400">
              <MapPin className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-xs text-white uppercase tracking-wider">Top Hiring Hubs</h3>
              <p className="text-[10px] text-muted-foreground mt-0.5">Regions with highest openings count</p>
            </div>
          </div>
          {locationData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={locationData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.02)" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 8, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 9, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(9, 8, 14, 0.95)",
                    border: "1px solid rgba(255,255,255,0.05)",
                    borderRadius: "12px",
                    fontSize: "10px",
                    color: "#fff"
                  }}
                />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]}>
                  {locationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[(index + 2) % CHART_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[180px] flex items-center justify-center text-muted-foreground text-xs">
              No geographical data metrics
            </div>
          )}
        </div>

        {/* Company Types and Remote Distributions */}
        <div className="bg-[#0a080f]/40 border border-white/5 rounded-2xl p-5 glass flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-xs text-white uppercase tracking-wider mb-1">Curation Distribution</h3>
            <p className="text-[10px] text-muted-foreground">Firm classifications and work arrangement types</p>
          </div>
          
          <div className="grid grid-cols-2 gap-2 flex-1 items-center justify-items-center">
            {/* Firm Type */}
            <div className="flex flex-col items-center">
              <ResponsiveContainer width={100} height={90}>
                <PieChart>
                  <Pie
                    data={startupMncData.length > 0 ? startupMncData : [{name: "Empty", value: 1}]}
                    cx="50%"
                    cy="50%"
                    innerRadius={22}
                    outerRadius={34}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    <Cell fill="#f97316" />
                    <Cell fill="#3b82f6" />
                    <Cell fill="#a855f7" />
                  </Pie>
                  <Tooltip formatter={(value) => `${value} roles`} />
                </PieChart>
              </ResponsiveContainer>
              <span className="text-[8px] font-bold text-gray-400 mt-1 uppercase tracking-wider">Firm Vertical</span>
            </div>

            {/* Remote vs Onsite */}
            <div className="flex flex-col items-center">
              <ResponsiveContainer width={100} height={90}>
                <PieChart>
                  <Pie
                    data={remoteOnsiteData.length > 0 ? remoteOnsiteData : [{name: "Empty", value: 1}]}
                    cx="50%"
                    cy="50%"
                    innerRadius={22}
                    outerRadius={34}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    <Cell fill="#10b981" />
                    <Cell fill="#4b5563" />
                  </Pie>
                  <Tooltip formatter={(value) => `${value} roles`} />
                </PieChart>
              </ResponsiveContainer>
              <span className="text-[8px] font-bold text-gray-400 mt-1 uppercase tracking-wider">Work Style</span>
            </div>
          </div>

          <div className="flex justify-center gap-3 text-[8px] text-muted-foreground/60 mt-3 font-bold flex-wrap border-t border-white/5 pt-2 uppercase tracking-wider">
            <div className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-orange-500" /> Startups</div>
            <div className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-blue-500" /> MNCs</div>
            <div className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-purple-500" /> Enterprise</div>
          </div>
        </div>

      </div>

      {/* Code Terminal Activity Logs */}
      <div className="bg-[#050308] border border-white/5 rounded-2xl p-5 shadow-2xl relative">
        <div className="flex items-center justify-between border-b border-white/5 pb-4 mb-4">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-orange-500/10 border border-orange-500/20 text-orange-400">
              <Terminal className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-xs text-white uppercase tracking-wider">Scraper Activity Feed</h3>
              <p className="text-[10px] text-muted-foreground mt-0.5 font-semibold">Real-time chronologies of ATS scan pipelines</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500/40" />
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/40" />
            <span className="w-2.5 h-2.5 rounded-full bg-green-500/40" />
          </div>
        </div>
        <div className="space-y-3 font-mono text-[10px] leading-relaxed text-muted-foreground">
          {SIMULATED_LOGS.map((log, idx) => (
            <div key={idx} className="flex items-start justify-between gap-4 border-b border-white/5 pb-2.5 last:border-0 last:pb-0">
              <div className="flex items-start gap-2.5">
                <span className="text-orange-500 select-none">~</span>
                <div>
                  <span className="text-gray-300 font-bold">{log.event}</span>
                  {log.count > 0 && (
                    <span className="ml-2 text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded text-[9px] uppercase">
                      +{log.count} openings synced
                    </span>
                  )}
                </div>
              </div>
              <span className="text-muted-foreground/40 font-bold whitespace-nowrap shrink-0">{log.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Internships Feed Section */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4 border-b border-white/5 pb-4">
          <div className="flex items-center gap-6">
            <button
              onClick={() => setActiveTab("latest")}
              className={cn(
                "relative pb-2 text-xs font-bold uppercase tracking-wider transition-colors duration-200",
                activeTab === "latest" ? "text-white" : "text-muted-foreground hover:text-white"
              )}
            >
              Latest Curation
              {activeTab === "latest" && (
                <motion.div layoutId="activeTabUnderline" className="absolute bottom-0 left-0 right-0 h-0.5 bg-orange-500" />
              )}
            </button>
            <button
              onClick={() => setActiveTab("foryou")}
              className={cn(
                "relative pb-2 text-xs font-bold uppercase tracking-wider transition-colors duration-200 flex items-center gap-1.5",
                activeTab === "foryou" ? "text-white" : "text-muted-foreground hover:text-white"
              )}
            >
              <Zap className="w-3.5 h-3.5 text-orange-400" />
              Personalized Recommendations
              {activeTab === "foryou" && (
                <motion.div layoutId="activeTabUnderline" className="absolute bottom-0 left-0 right-0 h-0.5 bg-orange-500" />
              )}
            </button>
          </div>

          <Link
            href="/internships"
            className="group flex items-center gap-1.5 text-xs text-orange-400 hover:text-orange-300 font-bold transition-colors shrink-0"
          >
            Explore all listings <ArrowUpRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </Link>
        </div>

        {activeTab === "latest" ? (
          <div>
            {latest?.length ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {latest.map((internship, i) => (
                  <motion.div
                    key={internship._id || internship.external_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, delay: 0.03 * i }}
                  >
                    <InternshipCard internship={internship} />
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-20 text-muted-foreground bg-[#0a080f]/40 border border-white/5 rounded-2xl glass">
                <Briefcase className="w-10 h-10 mx-auto mb-4 opacity-20 text-orange-400 animate-pulse" />
                <p className="font-bold text-sm mb-1 text-white">No internships indexed</p>
                <p className="text-xs text-muted-foreground">The crawler is scanning corporate boards, please check back shortly.</p>
              </div>
            )}
          </div>
        ) : (
          <div>
            {!session?.accessToken ? (
              <div className="text-center py-16 text-muted-foreground bg-[#0a080f]/40 border border-white/5 rounded-2xl glass max-w-xl mx-auto p-6">
                <Users className="w-10 h-10 mx-auto mb-4 opacity-20 text-orange-400" />
                <p className="font-bold text-sm mb-2 text-white">Sign In to Unlock AI Recommendations</p>
                <p className="text-xs text-muted-foreground mb-6 leading-relaxed font-semibold">
                  We look at your category target configurations, location choices, and bookmarks to build highly customized match alerts.
                </p>
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white shadow-lg shadow-orange-500/20 transition-all duration-300"
                >
                  Sign In Now
                </Link>
              </div>
            ) : recommendationsLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="bg-[#0a080f]/40 border border-white/5 rounded-2xl p-6 h-48 animate-pulse glass" />
                ))}
              </div>
            ) : recommendations?.length ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {recommendations.map((internship, i) => (
                  <motion.div
                    key={internship._id || internship.external_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, delay: 0.03 * i }}
                  >
                    <InternshipCard internship={internship} />
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16 text-muted-foreground bg-[#0a080f]/40 border border-white/5 rounded-2xl glass p-6 max-w-lg mx-auto">
                <Zap className="w-10 h-10 mx-auto mb-4 opacity-20 text-orange-400 animate-pulse" />
                <p className="font-bold text-sm mb-1 text-white">No customized matches found</p>
                <p className="text-xs text-muted-foreground mb-4">
                  Define your targeted location settings and technical domains inside your profile preferences to trigger results.
                </p>
                <Link
                  href="/profile"
                  className="inline-flex items-center gap-1.5 text-xs text-orange-400 hover:text-orange-300 font-bold"
                >
                  Update Profile Settings <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
