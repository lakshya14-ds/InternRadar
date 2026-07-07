"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, MapPin, ExternalLink, Bookmark, BookmarkCheck, Calendar, Building2, Globe, CheckCircle2, ChevronRight, Share2, DollarSign, Hourglass, Award, ShieldAlert, Sparkles, Share, ClipboardCheck } from "lucide-react";
import { motion } from "framer-motion";
import { useSession } from "next-auth/react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { internshipsApi, usersApi, companiesApi } from "@/lib/api";
import { cn, timeAgo, sourceLabel, categoryColor, getInternshipId } from "@/lib/utils";
import { useAppStore } from "@/store/useStore";
import { InternshipCard } from "@/components/internships/InternshipCard";
import Link from "next/link";

export default function InternshipDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data: session } = useSession();
  const { isBookmarked, toggleBookmark } = useAppStore();
  const queryClient = useQueryClient();
  const [scrollProgress, setScrollProgress] = useState(0);
  const [copiedLink, setCopiedLink] = useState(false);

  // Scroll Progress Tracker
  useEffect(() => {
    const handleScroll = () => {
      const totalScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (totalScroll > 0) {
        setScrollProgress(Number(((window.scrollY / totalScroll) * 100).toFixed(2)));
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const { data: internship, isLoading } = useQuery({
    queryKey: ["internship", id],
    queryFn: () => internshipsApi.getById(id),
    enabled: !!id,
  });

  const { data: enrichedCompany } = useQuery({
    queryKey: ["company-enrich", internship?.company],
    queryFn: () => companiesApi.enrich(internship!.company),
    enabled: !!internship?.company,
  });

  const { data: related } = useQuery({
    queryKey: ["internships", "recommendations", id],
    queryFn: () => internshipsApi.getRecommendations(id),
    enabled: !!id,
  });

  const saved = isBookmarked(id);
  const bookmarkMutation = useMutation({
    mutationFn: async () => {
      if (!session?.accessToken) { router.push("/login"); return; }
      if (saved) await usersApi.removeBookmark(session.accessToken, id);
      else await usersApi.addBookmark(session.accessToken, id);
      toggleBookmark(id);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bookmarks"] }),
  });

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: internship?.title,
        text: `Check out this internship at ${internship?.company}`,
        url: window.location.href,
      }).catch(console.error);
    } else {
      navigator.clipboard.writeText(window.location.href);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto animate-pulse">
        <div className="h-6 bg-white/5 rounded-xl w-32" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="h-44 bg-[#0a080f]/40 border border-white/5 rounded-2xl glass" />
            <div className="h-96 bg-[#0a080f]/40 border border-white/5 rounded-2xl glass" />
          </div>
          <div className="h-96 bg-[#0a080f]/40 border border-white/5 rounded-2xl glass" />
        </div>
      </div>
    );
  }

  if (!internship) {
    return (
      <div className="text-center py-20 bg-[#0a080f]/40 border border-white/5 rounded-2xl glass max-w-xl mx-auto mt-10">
        <p className="text-muted-foreground text-xs font-semibold mb-4">Internship opportunity not found or might have expired.</p>
        <button onClick={() => router.back()} className="inline-flex items-center gap-1.5 bg-orange-600 hover:bg-orange-500 text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all focus:outline-none">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to opportunities feed
        </button>
      </div>
    );
  }

  const relatedFiltered = related
    ? related.filter((r) => getInternshipId(r) !== id).slice(0, 3)
    : [];

  return (
    <div className="relative space-y-6 max-w-7xl mx-auto">
      {/* Scroll progress indicator */}
      <div className="fixed top-0 left-0 w-full h-0.5 z-50 pointer-events-none bg-orange-950/20">
        <motion.div
          className="h-full bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500"
          style={{ width: `${scrollProgress}%` }}
        />
      </div>

      {/* Top back navigation and quick action row */}
      <div className="flex items-center justify-between pb-2 border-b border-white/5">
        <button
          onClick={() => router.back()}
          className="group flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-muted-foreground hover:text-white transition-colors focus:outline-none"
        >
          <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          Back to Listings
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={handleShare}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#120f18]/45 border border-white/5 hover:border-orange-500/20 text-muted-foreground hover:text-white transition-all duration-200 focus:outline-none"
            title="Share Opportunity"
          >
            {copiedLink ? <ClipboardCheck className="w-3.5 h-3.5 text-emerald-400" /> : <Share2 className="w-3.5 h-3.5 text-orange-400" />}
            <span className="text-[10px] font-bold uppercase tracking-wider">{copiedLink ? "Copied!" : "Share Link"}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* LEFT COLUMN: Main internship content details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Header Card */}
          <div className="relative overflow-hidden rounded-3xl border border-white/5 bg-[#0a080f]/40 p-6 md:p-8 glass">
            <div className="absolute top-0 right-0 w-48 h-48 bg-orange-500/2 rounded-full blur-3xl pointer-events-none" />
            
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div className="flex items-start gap-4">
                {enrichedCompany?.logo ? (
                  <div className="w-16 h-16 rounded-2xl bg-white border border-white/10 flex items-center justify-center p-2 shrink-0 overflow-hidden shadow-inner">
                    <img
                      src={enrichedCompany.logo}
                      alt={`${internship.company} Logo`}
                      className="w-full h-full object-contain"
                    />
                  </div>
                ) : (
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-orange-600/15 via-amber-600/10 to-yellow-500/5 border border-orange-500/20 flex items-center justify-center text-2xl font-black text-orange-400 shrink-0">
                    {internship.company[0]?.toUpperCase()}
                  </div>
                )}
                <div className="space-y-1">
                  <h1 className="text-xl md:text-2xl font-black tracking-tight text-white leading-snug">
                    {internship.title}
                  </h1>
                  <p className="text-xs font-bold text-orange-400 flex items-center gap-2">
                    <span>{internship.company}</span>
                    <span className="w-1 h-1 rounded-full bg-white/20" />
                    <span className="text-muted-foreground">{internship.location}</span>
                  </p>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mt-6 border-t border-white/5 pt-4">
              {internship.category && (
                <span className={cn("text-[9px] font-bold px-3 py-1 rounded-full border tracking-wider uppercase", categoryColor(internship.category))}>
                  {internship.category}
                </span>
              )}
              <span className="text-[9px] font-bold px-3 py-1 rounded-full bg-white/5 border border-white/5 text-muted-foreground tracking-wider uppercase">
                {sourceLabel(internship.source)} Board Link
              </span>
              <span className="text-[9px] font-bold px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 tracking-wider uppercase">
                {internship.employment_type || "Internship"}
              </span>
            </div>
          </div>

          {/* Job Description Card */}
          {internship.description ? (
            <div className="bg-[#0a080f]/40 border border-white/5 rounded-3xl p-6 md:p-8 glass space-y-6">
              <h2 className="text-xs font-bold text-white uppercase tracking-wider border-b border-white/5 pb-3">
                Role Overview & Description
              </h2>
              <div className="text-muted-foreground text-xs md:text-sm leading-relaxed whitespace-pre-wrap font-sans space-y-4 font-semibold">
                {internship.description}
              </div>
            </div>
          ) : (
            <div className="text-center py-16 bg-[#0a080f]/40 border border-white/5 rounded-3xl glass text-muted-foreground text-xs font-semibold">
              Description details are not fully parsed. Click &quot;Apply Now&quot; to see original job post description on {internship.company}&apos;s career site.
            </div>
          )}

          {/* Company Enrichment Card */}
          {enrichedCompany && (
            <div className="bg-[#0a080f]/40 border border-white/5 rounded-3xl p-6 md:p-8 glass space-y-6">
              <div className="flex items-center gap-4 border-b border-white/5 pb-4">
                {enrichedCompany.logo && (
                  <div className="w-12 h-12 rounded-xl bg-white border border-white/10 flex items-center justify-center p-1.5 overflow-hidden shrink-0">
                    <img
                      src={enrichedCompany.logo}
                      alt={`${internship.company} Logo`}
                      className="w-full h-full object-contain"
                    />
                  </div>
                )}
                <div>
                  <h3 className="font-extrabold text-xs text-white uppercase tracking-wider">{internship.company}</h3>
                  <div className="flex flex-wrap gap-x-3 text-[10px] text-muted-foreground/60 mt-0.5 font-bold uppercase tracking-wider">
                    {enrichedCompany.industry && <span>{enrichedCompany.industry}</span>}
                    {enrichedCompany.company_size && (
                      <>
                        <span className="text-white/10">•</span>
                        <span>{enrichedCompany.company_size} Employees</span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {enrichedCompany.description && (
                <p className="text-muted-foreground text-xs leading-relaxed font-sans font-semibold">
                  {enrichedCompany.description}
                </p>
              )}

              {enrichedCompany.website && (
                <a
                  href={enrichedCompany.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-orange-400 hover:text-orange-400 font-bold transition-colors focus:outline-none"
                >
                  Visit Corporate Webpage <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Sticky summary card */}
        <div className="lg:col-span-1">
          <div className="sticky top-20 space-y-6">
            <div className="relative overflow-hidden rounded-3xl border border-white/5 bg-[#0a080f]/40 p-6 glass">
              <div className="absolute top-0 right-0 -mt-10 -mr-10 w-32 h-32 bg-amber-500/2 rounded-full blur-2xl" />
              
              <h3 className="text-[9px] font-bold text-muted-foreground/40 uppercase tracking-widest mb-4 border-b border-white/5 pb-3">Quick Metrics</h3>

              <div className="space-y-4 mb-6">
                {[
                  { icon: MapPin, label: "Workplace Type", value: internship.work_type || (internship.remote ? "Remote Placement" : "Onsite / In-Office") },
                  { icon: Globe, label: "Primary Location", value: internship.location || "Multiple Cities" },
                  { icon: DollarSign, label: "Curation Stipend", value: internship.stipend || internship.salary || "Not Specified" },
                  { icon: Hourglass, label: "Duration Scale", value: internship.duration || "Not Specified" },
                  { icon: Award, label: "Experience Required", value: internship.experience_level || "Not Specified" },
                  { icon: ShieldAlert, label: "Deadline", value: internship.application_deadline || "Open Enrollment" },
                  { icon: Calendar, label: "Published Date", value: timeAgo(internship.posted_at || internship.scraped_at) },
                  { icon: Building2, label: "Monitored Source", value: sourceLabel(internship.source) },
                ].map((item, idx) => (
                  <div key={idx} className="flex gap-3">
                    <div className="p-1.5 rounded-lg bg-[#120f18]/45 border border-white/5 text-orange-400 shrink-0 h-fit">
                      <item.icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-[9px] text-muted-foreground/50 uppercase tracking-widest font-bold">{item.label}</p>
                      <p className="text-xs font-bold text-white mt-0.5">{item.value}</p>
                    </div>
                  </div>
                ))}
              </div>

              {internship.benefits && internship.benefits.length > 0 && (
                <div className="mb-6 border-t border-white/5 pt-4">
                  <p className="text-[9px] text-muted-foreground/50 uppercase tracking-widest font-bold mb-3">Benefits & Perks</p>
                  <div className="flex flex-wrap gap-1.5">
                    {internship.benefits.map((benefit) => (
                      <span key={benefit} className="text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 uppercase tracking-wider">
                        {benefit}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {internship.skills && internship.skills.length > 0 && (
                <div className="mb-6 border-t border-white/5 pt-4">
                  <p className="text-[9px] text-muted-foreground/50 uppercase tracking-widest font-bold mb-3">Technical Skills Tracked</p>
                  <div className="flex flex-wrap gap-1.5">
                    {internship.skills.map((skill) => (
                      <span key={skill} className="text-[9px] font-bold px-2 py-0.5 rounded bg-orange-500/10 border border-orange-500/25 text-orange-400 uppercase tracking-wider">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Action CTAs */}
              <div className="space-y-3 pt-2">
                {/* Apply redirect untouched */}
                <a
                  href={internship.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full py-3 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-orange-500/20 transition-all duration-300 focus:outline-none"
                >
                  Apply Directly On Employer Page <ExternalLink className="w-4 h-4" />
                </a>

                {session && (
                  <button
                    onClick={() => bookmarkMutation.mutate()}
                    className={cn(
                      "flex items-center justify-center gap-2 w-full py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider border transition-all duration-200 focus:outline-none",
                      saved
                        ? "bg-orange-500/15 border-orange-500/30 text-orange-300 hover:bg-orange-500/20"
                        : "bg-white/5 border-white/5 text-muted-foreground hover:text-white hover:bg-white/10"
                    )}
                  >
                    {saved ? (
                      <>
                        <BookmarkCheck className="w-4 h-4 text-orange-400" /> Bookmarked Position
                      </>
                    ) : (
                      <>
                        <Bookmark className="w-4 h-4" /> Bookmark Opportunity
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-white/5 bg-[#120f18]/20 p-4 text-[10px] text-muted-foreground flex gap-2 font-semibold">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>We monitor applicant tracking links. All applies route directly to verified company listings.</span>
            </div>
          </div>
        </div>
      </div>

      {/* RELATED OPPORTUNITIES */}
      {relatedFiltered.length > 0 && (
        <div className="pt-8 border-t border-white/5">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-sm font-extrabold text-white uppercase tracking-wider">Similar Curation Matches</h2>
              <p className="text-[10px] text-muted-foreground mt-0.5">Recommendations based on technical matching metrics</p>
            </div>
            {internship.category && (
              <Link href={`/internships?category=${encodeURIComponent(internship.category)}`} className="text-xs font-bold text-orange-400 hover:text-orange-400 flex items-center gap-0.5">
                Browse category <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {relatedFiltered.map((r) => (
              <InternshipCard key={getInternshipId(r)} internship={r} compact />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
