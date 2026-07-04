"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { 
  ArrowRight, Briefcase, Zap, Globe, Search, Bell, TrendingUp, 
  Star, Building2, MapPin, Loader2, Sparkles, ChevronRight, Award, Compass 
} from "lucide-react";
import { internshipsApi, statsApi } from "@/lib/api";
import { InternshipCard } from "@/components/internships/InternshipCard";
import { cn, getInternshipId } from "@/lib/utils";

const CATEGORY_COLORS: Record<string, string> = {
  "Software Engineering": "text-blue-400 bg-blue-500/10 border-blue-500/20",
  "Data Science": "text-purple-400 bg-purple-500/10 border-purple-500/20",
  "Research": "text-teal-400 bg-teal-500/10 border-teal-500/20",
  "Product": "text-green-400 bg-green-500/10 border-green-500/20",
  "Machine Learning": "text-pink-400 bg-pink-500/10 border-pink-500/20",
  "UI/UX": "text-orange-400 bg-orange-500/10 border-orange-500/20",
  "Cloud & DevOps": "text-sky-400 bg-sky-500/10 border-sky-500/20",
  "Cybersecurity": "text-red-400 bg-red-500/10 border-red-500/20",
};

export default function LandingPage() {
  const router = useRouter();
  const [navigatingTo, setNavigatingTo] = useState<string | null>(null);

  const handleNav = (href: string) => {
    setNavigatingTo(href);
    router.push(href);
  };

  // Queries
  const { data: stats } = useQuery({
    queryKey: ["stats"],
    queryFn: () => statsApi.get(),
  });

  const { data: mncInternships } = useQuery({
    queryKey: ["featured-mnc"],
    queryFn: () => internshipsApi.featuredMnc(6),
  });

  const { data: startupInternships } = useQuery({
    queryKey: ["startups"],
    queryFn: () => internshipsApi.startups(6),
  });

  const statsList = [
    { label: "Companies Tracked", value: stats?.total_companies ? `${stats.total_companies}+` : "350+", icon: Building2 },
    { label: "Active Internships", value: stats?.total_internships ? `${stats.total_internships}+` : "1,200+", icon: Briefcase },
    { label: "Added This Week", value: stats?.new_this_week ? `+${stats.new_this_week}` : "+150", icon: Sparkles },
  ];

  return (
    <div className="min-h-screen bg-[#090514] text-white overflow-x-hidden">
      {/* Premium background gradient overlays */}
      <div className="fixed inset-0 -z-50 pointer-events-none overflow-hidden">
        <div className="absolute top-[10%] left-[10%] w-[500px] h-[500px] rounded-full bg-orange-600/5 blur-[120px]" />
        <div className="absolute bottom-[20%] right-[10%] w-[600px] h-[600px] rounded-full bg-amber-600/5 blur-[150px]" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:32px_32px]" />
      </div>

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#090514]/80 backdrop-blur-xl">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg overflow-hidden flex items-center justify-center shadow-lg shadow-orange-500/20">
            <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <span className="font-bold text-lg tracking-tight">InternRadar</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleNav("/login")}
            disabled={navigatingTo !== null}
            className="text-sm text-muted-foreground hover:text-white transition-colors px-3 py-1.5 flex items-center gap-1.5 disabled:opacity-50"
          >
            {navigatingTo === "/login" && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            Sign in
          </button>
          <button
            onClick={() => handleNav("/signup")}
            disabled={navigatingTo !== null}
            className="text-sm bg-orange-600 hover:bg-orange-500 text-white px-4 py-1.5 rounded-lg transition-colors font-medium flex items-center gap-1.5 disabled:opacity-50"
          >
            {navigatingTo === "/signup" && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-20 px-6 text-center">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-orange-500/30 bg-orange-500/10 text-orange-400 text-xs font-semibold mb-6 animate-pulse">
            <Zap className="w-3.5 h-3.5" />
            <span>AI-Driven Feed Diversification & Structured Company Discovery</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
            Discover Quality Internships<br />
            <span className="gradient-text bg-gradient-to-r from-orange-500 via-amber-400 to-yellow-300 bg-clip-text text-transparent">Direct From Top Companies</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10 font-medium">
            Aggregated across 300+ MNCs, startups, and top recruitment boards. Search by skills, location, and role. Apply directly on employer pages.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <button
              onClick={() => handleNav("/signup")}
              disabled={navigatingTo !== null}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white px-6 py-3 rounded-xl font-bold transition-all hover:scale-105 shadow-lg shadow-orange-500/15 disabled:opacity-50"
            >
              {navigatingTo === "/signup" ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              Create Free Account
            </button>
            <button
              onClick={() => handleNav("/internships")}
              disabled={navigatingTo !== null}
              className="inline-flex items-center gap-2 border border-white/10 hover:border-white/20 text-white/80 hover:text-white px-6 py-3 rounded-xl font-bold transition-all bg-[#18181b]/30 glass disabled:opacity-50"
            >
              {navigatingTo === "/internships" && <Loader2 className="w-4 h-4 animate-spin" />}
              Browse Internships
            </button>
          </div>
        </motion.div>
      </section>

      {/* Stats Counter */}
      <section className="py-8 px-6">
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
          {statsList.map((s, i) => (
            <motion.div key={s.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 * i }}
              className="glass border border-white/5 bg-[#18181b]/40 rounded-2xl p-6 text-center shadow-lg"
            >
              <s.icon className="w-8 h-8 text-orange-400 mx-auto mb-3" />
              <div className="text-3xl font-extrabold mb-1 tracking-tight">{s.value}</div>
              <div className="text-muted-foreground text-xs font-semibold uppercase tracking-wider">{s.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Featured MNC Internships */}
      <section className="py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="flex justify-between items-end mb-8">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-bold tracking-wide uppercase mb-2">
                <Award className="w-3.5 h-3.5" /> High-Impact Roles
              </div>
              <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Featured MNC Opportunities</h2>
              <p className="text-muted-foreground text-xs font-semibold">Genuine internships from global tech leaders (Google, Microsoft, Amazon, Databricks, Nvidia...)</p>
            </div>
            <Link href="/internships" className="hidden sm:inline-flex items-center gap-1 text-orange-400 hover:text-orange-300 text-xs font-bold transition-colors">
              View all MNCs <ChevronRight className="w-4 h-4" />
            </Link>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mncInternships?.slice(0, 6).map((job) => (
              <InternshipCard key={getInternshipId(job)} internship={job} />
            )) || (
              [...Array(6)].map((_, i) => (
                <div key={i} className="h-60 bg-[#18181b]/40 border border-white/5 rounded-2xl animate-pulse glass" />
              ))
            )}
          </div>
        </div>
      </section>

      {/* Top Hiring Companies & Startup Row */}
      <section className="py-12 px-6 bg-white/[0.01] border-y border-white/5">
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Top Hiring Companies Widget */}
          <div className="lg:col-span-1 glass bg-[#18181b]/30 border border-white/5 rounded-2xl p-6">
            <h3 className="font-extrabold text-sm text-white uppercase tracking-wider mb-4 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-orange-400" />
              <span>Top Hiring Companies</span>
            </h3>
            <div className="space-y-3">
              {stats?.top_companies?.slice(0, 5).map((comp: any, idx: number) => {
                const logoDomain = comp.company.toLowerCase().replace(/[^a-z0-9]/g, "") + ".com";
                return (
                  <Link 
                    key={comp.company} 
                    href={`/company/${encodeURIComponent(comp.company)}`}
                    className="flex items-center justify-between p-3 rounded-xl border border-white/5 hover:border-orange-500/20 bg-white/[0.02] hover:bg-orange-500/5 transition-all duration-200"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-lg bg-white border border-white/10 flex items-center justify-center p-0.5 overflow-hidden">
                        <img 
                          src={`https://logo.clearbit.com/${logoDomain}`}
                          alt="" 
                          className="w-full h-full object-contain"
                          onError={(e) => {
                            const parent = (e.target as HTMLElement).parentElement;
                            if (parent) {
                              parent.innerHTML = `<span class="text-xs font-bold text-orange-400">${comp.company[0]}</span>`;
                              parent.className = "w-7 h-7 rounded-lg bg-orange-500/10 flex items-center justify-center";
                            }
                          }}
                        />
                      </div>
                      <span className="text-xs font-bold text-white/90">{comp.company}</span>
                    </div>
                    <span className="text-[10px] font-bold bg-white/5 border border-white/10 px-2 py-0.5 rounded-full text-muted-foreground">
                      {comp.count} openings
                    </span>
                  </Link>
                );
              }) || (
                [...Array(5)].map((_, i) => (
                  <div key={i} className="h-12 bg-white/5 rounded-xl animate-pulse" />
                ))
              )}
            </div>
          </div>

          {/* Startup Opportunities Section */}
          <div className="lg:col-span-2">
            <div className="flex justify-between items-end mb-6">
              <div>
                <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold tracking-wide uppercase mb-2">
                  <Compass className="w-3.5 h-3.5" /> High Growth Startups
                </div>
                <h2 className="text-xl font-extrabold text-white tracking-tight">Startup Opportunities</h2>
              </div>
              <Link href="/internships" className="text-orange-400 hover:text-orange-300 text-xs font-bold transition-colors">
                View all startups <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {startupInternships?.slice(0, 4).map((job) => (
                <InternshipCard key={getInternshipId(job)} internship={job} compact />
              )) || (
                [...Array(4)].map((_, i) => (
                  <div key={i} className="h-44 bg-[#18181b]/40 border border-white/5 rounded-2xl animate-pulse glass" />
                ))
              )}
            </div>
          </div>

        </div>
      </section>

      {/* Trending Categories Section */}
      <section className="py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-center mb-10">
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Trending Categories</h2>
            <p className="text-muted-foreground text-xs font-semibold">Explore opportunities grouped by popular industry verticals</p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(CATEGORY_COLORS).map(([cat, style]) => (
              <Link 
                key={cat} 
                href={`/internships?category=${encodeURIComponent(cat)}`}
                className="glass border border-white/5 bg-[#18181b]/30 p-5 rounded-2xl text-center hover:border-orange-500/30 hover:scale-105 transition-all duration-300 group flex flex-col items-center"
              >
                <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center mb-3 border", style)}>
                  <TrendingUp className="w-5 h-5" />
                </div>
                <div className="font-bold text-xs text-white/90 group-hover:text-orange-400 transition-colors">
                  {cat}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-6">
        <motion.div initial={{ opacity: 0, scale: 0.98 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center glass bg-[#18181b]/20 rounded-3xl p-12 border border-orange-500/20 shadow-2xl"
        >
          <h2 className="text-3xl font-extrabold mb-4">Start discovering internships today</h2>
          <p className="text-muted-foreground text-sm font-semibold mb-8">Join thousands of students who use InternRadar to find and track verified internships.</p>
          <button
            onClick={() => handleNav("/signup")}
            disabled={navigatingTo !== null}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white px-8 py-3 rounded-xl font-bold transition-all hover:scale-105 shadow-lg shadow-orange-500/15 disabled:opacity-50"
          >
            {navigatingTo === "/signup" ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
            Create Free Account
          </button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6 text-center text-muted-foreground text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <img src="/logo.png" alt="Logo" className="w-5 h-5 object-cover" />
          <span className="font-semibold text-white">InternRadar</span>
        </div>
        <p>© 2026 InternRadar. Discover India&apos;s internship opportunities.</p>
      </footer>
    </div>
  );
}
