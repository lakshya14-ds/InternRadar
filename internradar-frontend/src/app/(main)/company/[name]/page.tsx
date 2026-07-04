"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { 
  Building2, Globe, Users, Briefcase, MapPin, Tag, ArrowLeft, 
  Loader2, Sparkles, TrendingUp, Calendar, ChevronRight 
} from "lucide-react";
import { motion } from "framer-motion";
import { 
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid 
} from "recharts";
import { companiesApi } from "@/lib/api";
import { InternshipCard } from "@/components/internships/InternshipCard";
import { cn } from "@/lib/utils";

export default function CompanyProfilePage() {
  const params = useParams();
  const router = useRouter();
  const companyName = decodeURIComponent(params.name as string);

  // Fetch company details
  const { data: details, isLoading, error } = useQuery({
    queryKey: ["company-details", companyName],
    queryFn: () => companiesApi.getCompanyDetails(companyName),
    enabled: !!companyName,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-32 text-muted-foreground bg-[#18181b]/40 border border-white/5 rounded-2xl glass animate-pulse max-w-4xl mx-auto">
        <Loader2 className="w-8 h-8 animate-spin mb-4 text-orange-400" />
        <p className="text-xs font-semibold">Gathering company intelligence profile...</p>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div className="text-center py-20 bg-card border border-border/50 rounded-2xl glass max-w-xl mx-auto mt-10">
        <Building2 className="w-12 h-12 mx-auto mb-4 opacity-20 text-orange-400" />
        <h3 className="text-white font-bold text-sm mb-2">Company Profile Not Found</h3>
        <p className="text-xs text-muted-foreground mb-6">We couldn't retrieve details for this organization.</p>
        <button onClick={() => router.back()} className="inline-flex items-center gap-1 bg-orange-600 hover:bg-orange-500 text-white px-4 py-2 rounded-xl text-xs font-semibold">
          <ArrowLeft className="w-3.5 h-3.5" /> Go Back
        </button>
      </div>
    );
  }

  const { brand, open_internships, hiring_activity, internship_history, skills_in_demand, locations } = details;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Back Button */}
      <button 
        onClick={() => router.back()} 
        className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-white transition-colors font-semibold"
      >
        <ArrowLeft className="w-4 h-4" /> Back to listings
      </button>

      {/* Hero Header Card */}
      <div className="relative overflow-hidden rounded-3xl border border-white/5 bg-gradient-to-br from-[#09090b]/80 to-[#18181b]/60 p-6 md:p-8 glass shadow-2xl">
        <div className="absolute top-0 right-0 w-[300px] h-[200px] bg-orange-500/5 rounded-full blur-3xl pointer-events-none -z-10" />
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start md:items-center gap-5">
            {/* Logo */}
            <div className="w-16 h-16 rounded-2xl bg-white border border-white/10 flex items-center justify-center p-2 shrink-0 shadow-inner overflow-hidden">
              <img 
                src={brand.logo} 
                alt={`${companyName} Logo`} 
                className="w-full h-full object-contain"
                onError={(e) => {
                  const parent = (e.target as HTMLElement).parentElement;
                  if (parent) {
                    parent.innerHTML = `<span class="text-2xl font-extrabold text-orange-400">${companyName[0].toUpperCase()}</span>`;
                    parent.className = "w-16 h-16 rounded-2xl bg-orange-500/10 flex items-center justify-center border border-orange-500/20 shadow-inner";
                  }
                }}
              />
            </div>
            
            <div className="space-y-1.5">
              <div className="flex items-center gap-3 flex-wrap">
                <h1 className="text-3xl font-extrabold text-white tracking-tight">{companyName}</h1>
                {details.company_type && (
                  <span className={cn(
                    "text-[10px] font-bold px-2.5 py-1 rounded-full border tracking-wide uppercase",
                    details.company_type === "mnc" && "bg-blue-500/10 text-blue-400 border-blue-500/20",
                    details.company_type === "startup" && "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
                    details.company_type === "enterprise" && "bg-purple-500/10 text-purple-400 border-purple-500/20",
                  )}>
                    {details.company_type === "startup" && details.funding_stage
                      ? `${details.company_type} · ${details.funding_stage}`
                      : details.company_type}
                  </span>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground font-semibold">
                <span className="flex items-center gap-1"><Briefcase className="w-3.5 h-3.5 text-orange-400/85" /> {brand.industry || "Technology"}</span>
                <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5 text-orange-400/85" /> {brand.company_size || "100-500 employees"}</span>
                {brand.website && (
                  <a
                    href={brand.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-orange-400 hover:text-orange-300 transition-colors"
                  >
                    <Globe className="w-3.5 h-3.5 shrink-0" /> Website
                  </a>
                )}
              </div>
            </div>
          </div>

          <div className="shrink-0 flex gap-3">
            <div className="bg-orange-500/10 border border-orange-500/20 rounded-2xl px-5 py-3 text-center min-w-[100px] glass">
              <div className="text-2xl font-black text-orange-400">{open_internships.length}</div>
              <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider">Active Roles</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        
        {/* Main Content (Overview, Timeline, Open Roles) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Overview */}
          <div className="bg-[#18181b]/30 border border-white/5 rounded-2xl p-6 glass">
            <h2 className="font-extrabold text-sm text-white uppercase tracking-wider mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-orange-400" />
              <span>Company Overview</span>
            </h2>
            <p className="text-xs text-muted-foreground leading-relaxed font-medium">
              {brand.description || `${companyName} is an innovative organization offering high-impact opportunities in their domain.`}
            </p>
          </div>

          {/* Hiring Activity Timeline Chart */}
          <div className="bg-[#18181b]/30 border border-white/5 rounded-2xl p-6 glass">
            <h2 className="font-extrabold text-sm text-white uppercase tracking-wider mb-5 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-orange-400" />
              <span>Hiring Activity History</span>
            </h2>
            {hiring_activity && hiring_activity.length > 0 ? (
              <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={hiring_activity} margin={{ top: 5, right: 10, left: -25, bottom: 5 }}>
                  <defs>
                    <linearGradient id="companyHiringColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                  <XAxis dataKey="month" tick={{ fontSize: 9, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 9, fill: "#9ca3af" }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      background: "rgba(9, 9, 11, 0.95)",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: "12px",
                      fontSize: "10px",
                      color: "#fff"
                    }}
                  />
                  <Area type="monotone" dataKey="postings" stroke="#f97316" strokeWidth={2} fillOpacity={1} fill="url(#companyHiringColor)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[180px] flex items-center justify-center text-muted-foreground text-xs">
                No historical hiring timeline details.
              </div>
            )}
          </div>

          {/* Open Internships Listings */}
          <div className="space-y-4">
            <h2 className="font-extrabold text-sm text-white uppercase tracking-wider mb-2 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-orange-400" />
              <span>Open Internship Listings ({open_internships.length})</span>
            </h2>
            
            {open_internships.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {open_internships.map((internship: any) => (
                  <InternshipCard key={internship.id || internship._id} internship={internship} compact />
                ))}
              </div>
            ) : (
              <div className="text-center py-16 bg-[#18181b]/20 border border-white/5 rounded-2xl glass">
                <Briefcase className="w-10 h-10 mx-auto mb-3 opacity-25 text-orange-400" />
                <p className="text-xs text-muted-foreground">No active openings right now. Check back later!</p>
              </div>
            )}
          </div>

        </div>

        {/* Sidebar details */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Top Locations */}
          <div className="bg-[#18181b]/30 border border-white/5 rounded-2xl p-6 glass">
            <h3 className="font-extrabold text-xs text-white uppercase tracking-wider mb-4 flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-orange-400" />
              <span>Hiring Locations</span>
            </h3>
            <div className="flex flex-wrap gap-2">
              {locations && locations.length > 0 ? (
                locations.map((loc: any) => (
                  <span 
                    key={loc.name}
                    className="text-[10px] font-bold px-2.5 py-1 rounded-lg bg-white/5 border border-white/5 text-gray-200"
                  >
                    {loc.name} ({loc.count})
                  </span>
                ))
              ) : (
                <span className="text-xs text-muted-foreground">India / Remote</span>
              )}
            </div>
          </div>

          {/* Demand Skills */}
          <div className="bg-[#18181b]/30 border border-white/5 rounded-2xl p-6 glass">
            <h3 className="font-extrabold text-xs text-white uppercase tracking-wider mb-4 flex items-center gap-1.5">
              <Tag className="w-4 h-4 text-orange-400" />
              <span>Skills in Demand</span>
            </h3>
            <div className="flex flex-wrap gap-2">
              {skills_in_demand && skills_in_demand.length > 0 ? (
                skills_in_demand.map((sk: any) => (
                  <span 
                    key={sk.name}
                    className="text-[10px] font-bold px-2.5 py-1 rounded-lg bg-orange-500/10 border border-orange-500/20 text-orange-300"
                  >
                    {sk.name} ({sk.count})
                  </span>
                ))
              ) : (
                <span className="text-xs text-muted-foreground">Standard tech stack</span>
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
