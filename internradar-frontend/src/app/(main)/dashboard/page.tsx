"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Briefcase, Building2, Users, Zap, TrendingUp, ArrowRight, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { statsApi, internshipsApi } from "@/lib/api";
import { InternshipCard } from "@/components/internships/InternshipCard";
import { ScraperPanel } from "@/components/dashboard/ScraperPanel";

function StatCard({ icon: Icon, label, value, sub, color }: {
  icon: React.ElementType; label: string; value: string | number; sub?: string; color: string;
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-border/50 rounded-xl p-5 card-hover">
      <div className={`w-10 h-10 rounded-lg ${color} flex items-center justify-center mb-4`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="text-2xl font-bold mb-0.5">{value}</div>
      <div className="text-sm font-medium mb-0.5">{label}</div>
      {sub && <div className="text-xs text-muted-foreground">{sub}</div>}
    </motion.div>
  );
}

const CHART_COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#84cc16"];

export default function DashboardPage() {
  const { data: session } = useSession();
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
    <div className="space-y-6">
      {/* Scraper Panel */}
      <ScraperPanel />

      {/* Welcome */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            Welcome back{session?.user?.name ? `, ${session.user.name.split(" ")[0]}` : ""}! 👋
          </h1>
          <p className="text-muted-foreground text-sm mt-0.5">Here&apos;s what&apos;s happening on InternRadar today.</p>
        </div>
        <Link href="/internships" className="hidden md:flex items-center gap-1.5 text-sm text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
          Browse all <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Stats */}
      {statsLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-card border border-border/50 rounded-xl p-5 animate-pulse h-28" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard icon={Briefcase} label="Total Internships" value={stats?.total_internships?.toLocaleString() || "0"}
            sub="Across all ATS platforms" color="bg-indigo-500/10 text-indigo-400" />
          <StatCard icon={Building2} label="Companies Tracked" value={stats?.total_companies?.toLocaleString() || "0"}
            sub="Active companies" color="bg-purple-500/10 text-purple-400" />
          <StatCard icon={Zap} label="New Today" value={stats?.new_today?.toLocaleString() || "0"}
            sub="Added in last 24h" color="bg-green-500/10 text-green-400" />
          <StatCard icon={Users} label="This Week" value={stats?.new_this_week?.toLocaleString() || "0"}
            sub="New this week" color="bg-orange-500/10 text-orange-400" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Chart */}
        <div className="lg:col-span-2 bg-card border border-border/50 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-indigo-400" />
            <h2 className="font-semibold text-sm">Internships by Category</h2>
          </div>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={categoryData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: "#1a1f2e", border: "1px solid #374151", borderRadius: "8px", fontSize: "12px" }}
                  cursor={{ fill: "rgba(99,102,241,0.05)" }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {categoryData.map((_, index) => (
                    <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex flex-col items-center justify-center h-[220px] text-muted-foreground">
              <RefreshCw className="w-8 h-8 mb-2 opacity-30" />
              <p className="text-sm">No data yet — database may be connecting</p>
            </div>
          )}
        </div>

        {/* Sources breakdown */}
        <div className="bg-card border border-border/50 rounded-xl p-5">
          <h2 className="font-semibold text-sm mb-4">Sources</h2>
          <div className="space-y-3">
            {stats?.sources?.length ? stats.sources.map((s) => (
              <div key={s.source} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                  <span className="text-sm capitalize">{s.source}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-500 rounded-full"
                      style={{ width: `${Math.min(100, (s.count / (stats.total_internships || 1)) * 100)}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground w-8 text-right">{s.count}</span>
                </div>
              </div>
            )) : (
              <div className="text-center text-muted-foreground text-sm py-8">No source data available</div>
            )}
          </div>
        </div>
      </div>

      {/* Latest Internships */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold">Latest Opportunities</h2>
          <Link href="/internships" className="text-sm text-indigo-400 hover:text-indigo-300 font-medium transition-colors flex items-center gap-1">
            View all <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
        {latest?.length ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {latest.map((internship, i) => (
              <motion.div key={internship._id || internship.external_id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                <InternshipCard internship={internship} />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 text-muted-foreground bg-card border border-border/50 rounded-xl">
            <Briefcase className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="font-medium mb-1">No internships yet</p>
            <p className="text-sm">Waiting for MongoDB connection to display data</p>
          </div>
        )}
      </div>
    </div>
  );
}
