"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Briefcase, Zap, Globe, Search, Bell, TrendingUp, Star, Building2, MapPin } from "lucide-react";

const STATS = [
  { label: "Companies Tracked", value: "350+", icon: Building2 },
  { label: "Internships Collected", value: "12,000+", icon: Briefcase },
  { label: "Email Alerts Sent", value: "5,000+", icon: Bell },
];

const FEATURES = [
  { icon: Zap, title: "Real-Time ATS Aggregation", desc: "Connected to Greenhouse, Lever, Ashby, Workday and more — updated every 30 minutes." },
  { icon: Globe, title: "India-Focused", desc: "Only genuine internships located in India. No noise, no irrelevant listings." },
  { icon: Search, title: "Advanced Search & Filters", desc: "Filter by role, company, location, category, source, and posting date instantly." },
  { icon: Bell, title: "Email Alerts", desc: "Get notified the moment a new internship matches your preferences." },
  { icon: TrendingUp, title: "18 Categories", desc: "From Software Engineering to Research, ML, Product, and more — precisely categorized." },
  { icon: Star, title: "Save & Track", desc: "Bookmark internships, track applications, and never miss a deadline." },
];

const SAMPLE_JOBS = [
  { company: "Razorpay", title: "Software Engineering Intern", location: "Bangalore", category: "Software Engineering", source: "Lever" },
  { company: "Swiggy", title: "Data Science Intern", location: "Bangalore", category: "Data Science", source: "Greenhouse" },
  { company: "ISRO", title: "Research Internship", location: "Ahmedabad", category: "Research", source: "Manual" },
  { company: "Meesho", title: "Product Intern", location: "Bangalore", category: "Product", source: "Ashby" },
  { company: "DRDO", title: "Machine Learning Intern", location: "Delhi", category: "Machine Learning", source: "Manual" },
  { company: "Zepto", title: "UI/UX Design Intern", location: "Mumbai", category: "UI/UX", source: "Greenhouse" },
];

const CATEGORY_COLORS: Record<string, string> = {
  "Software Engineering": "text-blue-400 bg-blue-500/10",
  "Data Science": "text-purple-400 bg-purple-500/10",
  "Research": "text-teal-400 bg-teal-500/10",
  "Product": "text-green-400 bg-green-500/10",
  "Machine Learning": "text-pink-400 bg-pink-500/10",
  "UI/UX": "text-orange-400 bg-orange-500/10",
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#030712] text-white overflow-x-hidden">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#030712]/80 backdrop-blur-xl">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
            <Briefcase className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight">InternRadar</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login" className="text-sm text-muted-foreground hover:text-white transition-colors px-3 py-1.5">
            Sign in
          </Link>
          <Link href="/signup" className="text-sm bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-1.5 rounded-lg transition-colors font-medium">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-24 px-6 text-center">
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-600/10 rounded-full blur-3xl" />
          <div className="absolute top-40 left-1/4 w-[300px] h-[300px] bg-purple-600/10 rounded-full blur-3xl" />
        </div>
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-sm mb-6">
            <Zap className="w-3.5 h-3.5" />
            <span>Real-time internship aggregation from 350+ companies</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight">
            Discover Internship<br />
            <span className="gradient-text">Opportunities Before</span><br />
            Everyone Else
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            Track internships from startups, ATS platforms, research labs and top organizations — all in one place, updated every 30 minutes.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link href="/signup" className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-semibold transition-all hover:scale-105">
              Create Free Account <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/internships" className="inline-flex items-center gap-2 border border-white/10 hover:border-white/20 text-white/80 hover:text-white px-6 py-3 rounded-xl font-medium transition-all">
              Browse Internships
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
          {STATS.map((s, i) => (
            <motion.div key={s.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 * i }}
              className="glass rounded-2xl p-6 text-center">
              <s.icon className="w-8 h-8 text-indigo-400 mx-auto mb-3" />
              <div className="text-3xl font-bold mb-1">{s.value}</div>
              <div className="text-muted-foreground text-sm">{s.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Live Preview */}
      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-center mb-10">
            <h2 className="text-3xl font-bold mb-3">Live Internship Feed</h2>
            <p className="text-muted-foreground">Fresh opportunities updated every 30 minutes from top ATS platforms</p>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {SAMPLE_JOBS.map((job, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.05 * i }}
                className="glass rounded-xl p-4 hover:border-indigo-500/30 transition-all cursor-pointer card-hover">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center text-sm font-bold text-indigo-400">
                    {job.company[0]}
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${CATEGORY_COLORS[job.category] || "text-gray-400 bg-gray-500/10"}`}>
                    {job.category}
                  </span>
                </div>
                <div className="font-semibold text-sm mb-1">{job.title}</div>
                <div className="text-muted-foreground text-xs mb-2">{job.company}</div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>
                  <span className="text-indigo-400/70">{job.source}</span>
                </div>
              </motion.div>
            ))}
          </div>
          <div className="text-center mt-8">
            <Link href="/internships" className="inline-flex items-center gap-2 text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors">
              View all internships <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-6 bg-white/[0.02]">
        <div className="max-w-5xl mx-auto">
          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-3">Everything you need to land your internship</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">Built for students and fresh graduates looking for quality internship opportunities in India.</p>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f, i) => (
              <motion.div key={f.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.05 * i }}
                className="glass rounded-xl p-5">
                <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4">
                  <f.icon className="w-5 h-5 text-indigo-400" />
                </div>
                <div className="font-semibold mb-2">{f.title}</div>
                <div className="text-muted-foreground text-sm leading-relaxed">{f.desc}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-3">How It Works</h2>
            <p className="text-muted-foreground">From discovery to application in 3 simple steps.</p>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Create an Account", desc: "Sign up free and set your preferences — categories, locations, companies." },
              { step: "02", title: "Browse & Search", desc: "Explore thousands of internships filtered to your exact criteria in real-time." },
              { step: "03", title: "Get Notified", desc: "Receive email alerts when matching internships are posted. Never miss an opportunity." },
            ].map((s, i) => (
              <motion.div key={s.step} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 * i }}
                className="relative text-center">
                <div className="text-6xl font-black text-white/5 mb-4">{s.step}</div>
                <div className="font-semibold mb-2 -mt-6 relative z-10">{s.title}</div>
                <div className="text-muted-foreground text-sm relative z-10">{s.desc}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <motion.div initial={{ opacity: 0, scale: 0.98 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center glass rounded-3xl p-12 border border-indigo-500/20">
          <h2 className="text-3xl font-bold mb-4">Start discovering internships today</h2>
          <p className="text-muted-foreground mb-8">Join thousands of students who use InternRadar to find their perfect internship.</p>
          <Link href="/signup" className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-3 rounded-xl font-semibold transition-all hover:scale-105">
            Create Free Account <ArrowRight className="w-4 h-4" />
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6 text-center text-muted-foreground text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Briefcase className="w-4 h-4 text-indigo-400" />
          <span className="font-semibold text-white">InternRadar</span>
        </div>
        <p>© 2026 InternRadar. Discover India&apos;s internship opportunities.</p>
      </footer>
    </div>
  );
}
