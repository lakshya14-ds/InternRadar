"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { 
  ArrowRight, Briefcase, Zap, Globe, Search, Bell, TrendingUp, 
  Star, Building2, MapPin, Loader2, Sparkles, ChevronRight, Award, Compass, ArrowUpRight, GraduationCap
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

// CountUp Component for premium statistical loading
function StatCounter({ valueStr }: { valueStr: string }) {
  const numeric = parseInt(valueStr.replace(/[^0-9]/g, ""), 10) || 0;
  const suffix = valueStr.replace(/[0-9,]/g, "");
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (numeric === 0) {
      setCount(0);
      return;
    }
    let start = 0;
    const end = numeric;
    const duration = 1200;
    const range = end - start;
    let current = start;
    const increment = end > 100 ? Math.ceil(end / 40) : 1;
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

export default function LandingPage() {
  const router = useRouter();
  const [navigatingTo, setNavigatingTo] = useState<string | null>(null);

  // Mouse Parallax for hero card backing
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const rotateX = useTransform(mouseY, [-300, 300], [10, -10]);
  const rotateY = useTransform(mouseX, [-300, 300], [-10, 10]);

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const centerX = rect.left + width / 2;
    const centerY = rect.top + height / 2;
    mouseX.set(e.clientX - centerX);
    mouseY.set(e.clientY - centerY);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

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
    { label: "Companies Tracked", value: stats?.total_companies ? `${stats.total_companies}+` : "380+", icon: Building2 },
    { label: "Active Internships", value: stats?.total_internships ? `${stats.total_internships}+` : "1,450+", icon: Briefcase },
    { label: "Added This Week", value: stats?.new_this_week ? `+${stats.new_this_week}` : "+180", icon: Sparkles },
  ];

  const MARQUEE_COMPANIES = [
    "Google", "Microsoft", "Stripe", "Amazon", "Nvidia", "Meta", 
    "Vercel", "Linear", "Databricks", "Netflix", "Atlassian", "Uber"
  ];

  const TESTIMONIALS = [
    {
      name: "Aryan Sen",
      role: "SWE Intern at Google",
      comment: "InternRadar's scraper logs let me find the Greenhouse listing as soon as it went live. Had my interview scheduled in 3 days!",
      logo: "Google"
    },
    {
      name: "Sanjana Roy",
      role: "Research Intern at Nvidia",
      comment: "The AI recommendation matched my computer vision portfolio perfectly. Centralized and simple interface.",
      logo: "Nvidia"
    },
    {
      name: "Tushar Dev",
      role: "Product Intern at Stripe",
      comment: "I used to check dozens of job boards manually. Finding verified official career portal direct links here is a game-changer.",
      logo: "Stripe"
    }
  ];

  const ROADMAP_STEPS = [
    {
      step: "01",
      title: "ATS Scrapers Scan Career Portals",
      desc: "Our auto-scrapers monitor Lever, Ashby, Greenhouse, and Workday links hour-by-hour.",
      glow: "shadow-orange-500/10 border-orange-500/20"
    },
    {
      step: "02",
      title: "AI Analysis & Filtering",
      desc: "Openings are parsed by technical domain, stipend rate, remote flags, and experience levels.",
      glow: "shadow-amber-500/10 border-amber-500/20"
    },
    {
      step: "03",
      title: "Instant Search Notifications",
      desc: "Save queries, setup notification rules, and get direct email alerts when matches are found.",
      glow: "shadow-yellow-500/10 border-yellow-500/20"
    }
  ];

  return (
    <div className="min-h-screen bg-[#040108] text-white overflow-x-hidden">
      {/* Floating abstract premium background meshes */}
      <div className="fixed inset-0 -z-50 pointer-events-none overflow-hidden">
        <div className="absolute top-[5%] left-[-10%] w-[600px] h-[600px] rounded-full bg-orange-600/5 blur-[130px] opacity-70 animate-pulse-slow" style={{ animationDuration: "12s" }} />
        <div className="absolute bottom-[10%] right-[-10%] w-[700px] h-[700px] rounded-full bg-amber-600/3 blur-[160px] opacity-60 animate-pulse-slow" style={{ animationDuration: "16s" }} />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:36px_36px]" />
      </div>

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#040108]/75 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg overflow-hidden flex items-center justify-center border border-orange-500/20 bg-orange-950/20 shadow-lg shadow-orange-500/10">
            <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <span className="font-bold text-sm tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-orange-200 via-amber-200 to-yellow-100">InternRadar</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleNav("/login")}
            disabled={navigatingTo !== null}
            className="text-xs text-muted-foreground hover:text-white transition-colors px-3 py-1.5 flex items-center gap-1.5 disabled:opacity-50"
          >
            {navigatingTo === "/login" && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            Sign in
          </button>
          <button
            onClick={() => handleNav("/signup")}
            disabled={navigatingTo !== null}
            className="text-xs bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white px-4 py-2 rounded-xl transition-all font-semibold flex items-center gap-1.5 disabled:opacity-50 shadow-lg shadow-orange-500/15"
          >
            {navigatingTo === "/signup" && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-36 pb-20 px-6 text-center max-w-7xl mx-auto" onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}>
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
          className="space-y-6"
        >
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-orange-500/20 bg-orange-500/5 text-orange-400 text-[10px] font-bold uppercase tracking-wider mb-2">
            <Zap className="w-3 h-3 text-orange-400" />
            <span>Automated ATS Scrapers & High-Impact Curation</span>
          </div>

          <h1 className="text-4xl md:text-7xl font-extrabold tracking-tight leading-tight text-white">
            Discover Quality Internships<br />
            <span className="gradient-text bg-gradient-to-r from-orange-400 via-amber-400 to-yellow-300 bg-clip-text text-transparent">Direct From Corporate Portals</span>
          </h1>

          <p className="text-sm md:text-base text-muted-foreground max-w-2xl mx-auto mb-8 leading-relaxed font-semibold">
            Aggregated hourly across 350+ MNC career sites, startups, and top tech boards. Filter by roles, stipends, and skills. Apply directly on official corporate links.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap pt-2">
            <button
              onClick={() => handleNav("/signup")}
              disabled={navigatingTo !== null}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white px-6 py-3.5 rounded-xl font-bold transition-all shadow-lg shadow-orange-500/20 disabled:opacity-50 text-xs"
            >
              {navigatingTo === "/signup" ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              Create Student Account
            </button>
            <button
              onClick={() => handleNav("/internships")}
              disabled={navigatingTo !== null}
              className="inline-flex items-center gap-2 border border-white/5 hover:border-white/10 text-white/95 hover:text-white px-6 py-3.5 rounded-xl font-bold transition-all bg-[#120f18]/30 glass disabled:opacity-50 text-xs hover:bg-[#120f18]/60"
            >
              {navigatingTo === "/internships" && <Loader2 className="w-4 h-4 animate-spin" />}
              Browse Opportunities
            </button>
          </div>
        </motion.div>
      </section>

      {/* Scrolling Marquee / Brand Carousel */}
      <section className="py-8 border-y border-white/5 bg-white/[0.01] overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 mb-4">
          <p className="text-[10px] text-center font-bold text-muted-foreground/40 uppercase tracking-widest">
            Aggregating Listings From Global Tech Hubs
          </p>
        </div>
        <div className="relative flex items-center justify-center">
          <div className="w-full overflow-hidden select-none relative">
            {/* Fade overlays */}
            <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-[#040108] to-transparent z-10 pointer-events-none" />
            <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-[#040108] to-transparent z-10 pointer-events-none" />
            
            <motion.div
              animate={{ x: [0, -1000] }}
              transition={{
                ease: "linear",
                duration: 25,
                repeat: Infinity,
              }}
              className="flex gap-16 whitespace-nowrap min-w-full w-max"
            >
              {[...MARQUEE_COMPANIES, ...MARQUEE_COMPANIES, ...MARQUEE_COMPANIES].map((comp, idx) => (
                <div key={idx} className="flex items-center gap-2 text-muted-foreground/60 hover:text-orange-400/90 transition-colors font-bold text-sm tracking-widest uppercase cursor-default">
                  <Building2 className="w-4 h-4 text-orange-500/40" />
                  {comp}
                </div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Counter Section */}
      <section className="py-12 px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {statsList.map((s, i) => (
            <motion.div 
              key={s.label} 
              initial={{ opacity: 0, y: 15 }} 
              whileInView={{ opacity: 1, y: 0 }} 
              viewport={{ once: true }} 
              transition={{ delay: 0.1 * i, duration: 0.4 }}
              className="glass border border-white/5 bg-[#120f18]/30 rounded-2xl p-6 text-center shadow-lg"
            >
              <div className="w-10 h-10 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mx-auto mb-3 text-orange-400">
                <s.icon className="w-5 h-5" />
              </div>
              <div className="text-3xl font-extrabold mb-1 tracking-tight text-white font-mono">
                <StatCounter valueStr={s.value} />
              </div>
              <div className="text-muted-foreground text-[10px] font-bold uppercase tracking-wider">{s.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How it Works / Recruitment Roadmap */}
      <section className="py-16 px-6 max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-300 text-xs font-semibold mb-2">
            <GraduationCap className="w-4 h-4 text-orange-400" /> Roadmap
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white">How InternRadar Accelerates Discovery</h2>
          <p className="text-muted-foreground text-xs font-semibold mt-1">Real-time pipeline automation for early-career students</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {ROADMAP_STEPS.map((step, idx) => (
            <div key={idx} className={cn("glass border bg-[#120f18]/30 rounded-2xl p-6 relative overflow-hidden group", step.glow)}>
              <div className="absolute top-0 right-0 text-7xl font-black text-white/[0.02] select-none -mt-4 mr-2">
                {step.step}
              </div>
              <div className="w-8 h-8 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-xs font-bold text-orange-400 mb-4">
                {step.step}
              </div>
              <h3 className="font-extrabold text-sm text-white mb-2">{step.title}</h3>
              <p className="text-muted-foreground text-xs leading-relaxed font-semibold">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Featured MNC Internships */}
      <section className="py-16 px-6 max-w-7xl mx-auto">
        <div className="flex justify-between items-end mb-8 border-b border-white/5 pb-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-bold tracking-wide uppercase mb-2">
              <Award className="w-3.5 h-3.5" /> High-Impact Roles
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Featured MNC Listings</h2>
            <p className="text-muted-foreground text-xs font-semibold mt-1">Genuine internships from global tech leaders (Google, Microsoft, Amazon, Databricks, Nvidia...)</p>
          </div>
          <Link href="/internships" className="hidden sm:inline-flex items-center gap-1 text-orange-400 hover:text-orange-300 text-xs font-bold transition-colors">
            View all MNCs <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mncInternships?.slice(0, 6).map((job) => (
            <InternshipCard key={getInternshipId(job)} internship={job} />
          )) || (
            [...Array(6)].map((_, i) => (
              <div key={i} className="h-60 bg-[#120f18]/30 border border-white/5 rounded-2xl animate-pulse glass" />
            ))
          )}
        </div>
      </section>

      {/* Startup & Top Companies Panel */}
      <section className="py-16 px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Top Hiring Companies Widget */}
          <div className="lg:col-span-1 glass bg-[#120f18]/30 border border-white/5 rounded-2xl p-6">
            <h3 className="font-extrabold text-sm text-white uppercase tracking-wider mb-4 flex items-center gap-2 border-b border-white/5 pb-3">
              <Building2 className="w-4 h-4 text-orange-400" />
              <span>Top Hiring Firms</span>
            </h3>
            <div className="space-y-2">
              {stats?.top_companies?.slice(0, 5).map((comp: any) => {
                const logoDomain = comp.company.toLowerCase().replace(/[^a-z0-9]/g, "") + ".com";
                return (
                  <Link 
                    key={comp.company} 
                    href={`/company/${encodeURIComponent(comp.company)}`}
                    className="flex items-center justify-between p-3 rounded-xl border border-white/5 hover:border-orange-500/20 bg-white/[0.01] hover:bg-orange-500/5 transition-all duration-200"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-7 h-7 rounded bg-white border border-white/10 flex items-center justify-center p-0.5 overflow-hidden shrink-0">
                        <img 
                          src={`https://logo.clearbit.com/${logoDomain}`}
                          alt="" 
                          className="w-full h-full object-contain"
                          onError={(e) => {
                            const parent = (e.target as HTMLElement).parentElement;
                            if (parent) {
                              parent.innerHTML = `<span class="text-[10px] font-bold text-orange-400">${comp.company[0]}</span>`;
                              parent.className = "w-7 h-7 rounded bg-orange-500/10 flex items-center justify-center shrink-0";
                            }
                          }}
                        />
                      </div>
                      <span className="text-xs font-bold text-white/95 truncate">{comp.company}</span>
                    </div>
                    <span className="text-[9px] font-bold bg-white/5 border border-white/10 px-2 py-0.5 rounded-full text-muted-foreground shrink-0">
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
            <div className="flex justify-between items-end mb-6 border-b border-white/5 pb-3">
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
                  <div key={i} className="h-44 bg-[#120f18]/30 border border-white/5 rounded-2xl animate-pulse glass" />
                ))
              )}
            </div>
          </div>

        </div>
      </section>

      {/* Animated Success Testimonials */}
      <section className="py-16 px-6 max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-2xl md:text-3xl font-extrabold text-white">Student Success Stories</h2>
          <p className="text-muted-foreground text-xs font-semibold mt-1">Discover how candidates landed top tech roles</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {TESTIMONIALS.map((t, idx) => (
            <div key={idx} className="glass border border-white/5 bg-[#120f18]/30 rounded-2xl p-6 flex flex-col justify-between hover:border-orange-500/20 transition-all duration-300">
              <div className="space-y-4">
                <div className="flex items-center gap-1 text-amber-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-3.5 h-3.5 fill-current" />
                  ))}
                </div>
                <p className="text-muted-foreground text-xs leading-relaxed font-semibold italic">
                  &quot;{t.comment}&quot;
                </p>
              </div>
              <div className="flex items-center justify-between border-t border-white/5 pt-4 mt-6">
                <div>
                  <h4 className="text-xs font-bold text-white">{t.name}</h4>
                  <p className="text-[10px] text-muted-foreground font-medium mt-0.5">{t.role}</p>
                </div>
                <span className="text-[10px] font-bold bg-orange-500/10 text-orange-400 border border-orange-500/10 px-2.5 py-0.5 rounded-full uppercase tracking-wider shrink-0">
                  {t.logo}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Box */}
      <section className="py-16 px-6 max-w-7xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }} 
          whileInView={{ opacity: 1, scale: 1 }} 
          viewport={{ once: true }}
          className="max-w-4xl mx-auto text-center glass bg-[#120f18]/15 rounded-3xl p-12 border border-orange-500/20 shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/5 rounded-full blur-2xl pointer-events-none" />
          <h2 className="text-3xl font-extrabold mb-4 text-white">Start Discovering Internships Today</h2>
          <p className="text-muted-foreground text-sm font-semibold mb-8 max-w-md mx-auto">
            Join thousands of college candidates using InternRadar to discover indexer updates.
          </p>
          <button
            onClick={() => handleNav("/signup")}
            disabled={navigatingTo !== null}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white px-8 py-3.5 rounded-xl font-bold transition-all shadow-lg shadow-orange-500/20 disabled:opacity-50 text-xs"
          >
            {navigatingTo === "/signup" ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
            Get Started For Free
          </button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6 text-center text-muted-foreground text-xs">
        <div className="flex items-center justify-center gap-2 mb-2">
          <img src="/logo.png" alt="Logo" className="w-5 h-5 object-cover" />
          <span className="font-semibold text-white">InternRadar</span>
        </div>
        <p>© 2026 InternRadar. Discover India&apos;s internship opportunities.</p>
      </footer>
    </div>
  );
}
