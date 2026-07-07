"use client";

import Link from "next/link";
import { ExternalLink, MapPin, Bookmark, BookmarkCheck, Calendar, Sparkles, Building2 } from "lucide-react";
import { motion } from "framer-motion";
import { useSession } from "next-auth/react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { cn, timeAgo, getInternshipId, sourceLabel, categoryColor } from "@/lib/utils";
import { usersApi } from "@/lib/api";
import { useAppStore } from "@/store/useStore";
import type { Internship } from "@/types";

interface Props {
  internship: Internship;
  compact?: boolean;
}

export function InternshipCard({ internship, compact }: Props) {
  const { data: session } = useSession();
  const { isBookmarked, toggleBookmark } = useAppStore();
  const queryClient = useQueryClient();
  const id = getInternshipId(internship);
  const saved = isBookmarked(id);

  const bookmarkMutation = useMutation({
    mutationFn: async () => {
      if (!session?.accessToken) return;
      if (saved) {
        await usersApi.removeBookmark(session.accessToken, id);
      } else {
        await usersApi.addBookmark(session.accessToken, id);
      }
      toggleBookmark(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
    },
  });

  return (
    <motion.div
      whileHover={{ y: -3, scale: 1.005 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className="relative flex flex-col h-full rounded-2xl border border-white/5 bg-[#0a080f]/45 p-5 glass hover:border-orange-500/20 hover:shadow-xl hover:shadow-orange-500/5 transition-all duration-300 group overflow-hidden"
    >
      {/* Background glow highlights */}
      <div className="absolute top-0 right-0 w-28 h-28 bg-orange-500/2 rounded-full blur-3xl pointer-events-none group-hover:bg-orange-500/4 transition-all duration-300 -z-10" />

      <div className="flex items-start justify-between mb-4 gap-2">
        {internship.company_logo ? (
          <div className="w-10 h-10 rounded-xl bg-white border border-white/10 flex items-center justify-center p-1 group-hover:scale-105 transition-transform duration-200 shrink-0 shadow-inner overflow-hidden">
            <img
              src={internship.company_logo}
              alt={`${internship.company} Logo`}
              className="w-full h-full object-contain"
              onError={(e) => {
                const parent = (e.target as HTMLElement).parentElement;
                if (parent) {
                  parent.innerHTML = `<span class="text-xs font-black text-orange-400">${internship.company[0]?.toUpperCase() || "I"}</span>`;
                  parent.className = "w-10 h-10 rounded-xl bg-orange-500/10 border border-orange-500/25 flex items-center justify-center shrink-0 shadow-inner";
                }
              }}
            />
          </div>
        ) : (
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-orange-500/15 via-amber-500/10 to-yellow-500/5 border border-orange-500/20 flex items-center justify-center text-xs font-black text-orange-400 group-hover:scale-105 transition-transform duration-200 shrink-0 shadow-inner animate-pulse-slow">
            {internship.company[0]?.toUpperCase() || "I"}
          </div>
        )}
        <div className="flex items-center gap-1.5 shrink-0">
          {internship.remote && (
            <span className="text-[8px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 tracking-wider uppercase">
              Remote
            </span>
          )}
          {(internship.quality_score ?? 0) >= 70 && (
            <span
              title={`Match quality score ${internship.quality_score}/100`}
              className="text-[8px] font-bold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/25 tracking-wider uppercase flex items-center gap-0.5"
            >
              <Sparkles className="w-2 h-2 text-amber-400" /> Premium Match
            </span>
          )}
          {session && (
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.preventDefault();
                bookmarkMutation.mutate();
              }}
              className={cn(
                "p-1.5 rounded-lg border transition-all duration-200 focus:outline-none",
                saved
                  ? "bg-orange-500/10 border-orange-500/30 text-orange-300 hover:bg-orange-500/20"
                  : "bg-white/5 border-transparent text-muted-foreground hover:text-foreground hover:bg-white/10"
              )}
              aria-label="Bookmark Internship"
            >
              {saved ? (
                <BookmarkCheck className="w-4 h-4 text-orange-400" />
              ) : (
                <Bookmark className="w-4 h-4" />
              )}
            </motion.button>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {/* Company Link */}
        <Link 
          href={`/company/${encodeURIComponent(internship.company)}`} 
          className="text-[10px] font-bold text-orange-400/90 hover:text-orange-300 transition-colors mb-1 inline-flex items-center gap-1 w-max relative z-10 uppercase tracking-wider"
        >
          <Building2 className="w-3 h-3 shrink-0 text-orange-500/70" />
          <span>{internship.company}</span>
        </Link>
        
        {/* Role Title Link */}
        <Link href={`/internships/${id}`} className="block group/title mb-2">
          <div className="font-extrabold text-xs md:text-sm text-white group-hover/title:text-orange-400 transition-colors duration-250 line-clamp-2 leading-snug">
            {internship.title}
          </div>
        </Link>

        <div className="flex flex-wrap items-center gap-x-2 gap-y-1 mb-4 text-[10px] font-bold uppercase tracking-wider">
          {(internship.stipend || internship.salary) && (
            <span className="text-amber-400">
              {internship.stipend || internship.salary}
            </span>
          )}
          {internship.duration && (
            <span className="text-muted-foreground/60 flex items-center gap-1">
              {(internship.stipend || internship.salary) && <span className="w-1 h-1 rounded-full bg-white/10" />}
              {internship.duration}
            </span>
          )}
        </div>

        {!compact && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {internship.category && (
              <span
                className={cn(
                  "text-[8px] font-bold px-2.5 py-0.5 rounded-full border tracking-wider uppercase",
                  categoryColor(internship.category)
                )}
              >
                {internship.category}
              </span>
            )}
            {internship.funding_stage && (
              <span className="text-[8px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/25 tracking-wider uppercase">
                {internship.funding_stage}
              </span>
            )}
            <span className="text-[8px] font-bold px-2.5 py-0.5 rounded-full bg-white/5 text-muted-foreground border border-white/5 tracking-wider uppercase">
              Via {sourceLabel(internship.source)}
            </span>
          </div>
        )}

        <div className="flex items-center justify-between text-[10px] text-muted-foreground/60 mt-auto pt-1 font-bold uppercase tracking-wider">
          <span className="flex items-center gap-1 max-w-[130px]">
            <MapPin className="w-3.5 h-3.5 text-orange-400/50 shrink-0" />
            <span className="truncate">{internship.location || "Worldwide"}</span>
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-orange-400/50 shrink-0" />
            {timeAgo(internship.posted_at || internship.scraped_at)}
          </span>
        </div>
      </div>

      {/* Redirect redirect URL untouched */}
      <div className="mt-4 pt-4 border-t border-white/5 relative z-10">
        <a
          href={internship.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-1.5 w-full py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-orange-500/5 via-amber-500/5 to-transparent hover:from-orange-600 hover:to-orange-500 text-orange-400 hover:text-white border border-orange-500/15 hover:border-transparent transition-all duration-300 shadow-sm focus:outline-none focus:ring-1 focus:ring-orange-500/40"
        >
          <span>Apply Now</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </motion.div>
  );
}
