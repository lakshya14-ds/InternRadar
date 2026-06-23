"use client";

import Link from "next/link";
import { ExternalLink, MapPin, Bookmark, BookmarkCheck, Calendar, Sparkles } from "lucide-react";
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
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="relative flex flex-col h-full rounded-2xl border border-white/5 bg-[#18181b]/40 p-5 glass hover:border-orange-500/30 hover:shadow-2xl hover:shadow-orange-500/10 transition-all duration-300 group overflow-hidden"
    >
      {/* Background glow highlights */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/3 rounded-full blur-3xl pointer-events-none group-hover:bg-orange-500/5 transition-all duration-300 -z-10" />

      <div className="flex items-start justify-between mb-4 gap-2">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-orange-500/15 via-amber-500/10 to-yellow-500/5 border border-orange-500/20 flex items-center justify-center text-sm font-extrabold text-orange-300 group-hover:scale-105 transition-transform duration-200 shrink-0 shadow-inner">
          {internship.company[0]?.toUpperCase() || "I"}
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {internship.remote && (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 tracking-wide uppercase">
              Remote
            </span>
          )}
          {session && (
            <motion.button
              whileTap={{ scale: 0.85 }}
              onClick={(e) => {
                e.preventDefault();
                bookmarkMutation.mutate();
              }}
              className={cn(
                "p-1.5 rounded-lg border transition-all duration-200",
                saved
                  ? "bg-orange-500/10 border-orange-500/30 text-orange-300 hover:bg-orange-500/20"
                  : "bg-white/5 border-transparent text-muted-foreground hover:text-foreground hover:bg-white/10"
              )}
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

      <Link href={`/internships/${id}`} className="flex-1 flex flex-col group">
        <div className="font-bold text-sm text-white group-hover:text-orange-300 transition-colors duration-200 line-clamp-2 leading-snug mb-1">
          {internship.title}
        </div>
        <div className="text-muted-foreground text-xs font-semibold hover:text-white transition-colors mb-4 flex items-center gap-1.5">
          {internship.company}
          {internship.remote && <span className="w-1 h-1 rounded-full bg-orange-500/50" />}
        </div>

        {!compact && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {internship.category && (
              <span
                className={cn(
                  "text-[10px] font-bold px-2.5 py-0.5 rounded-full border tracking-wide uppercase",
                  categoryColor(internship.category)
                )}
              >
                {internship.category}
              </span>
            )}
            <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-white/5 text-muted-foreground border border-white/5 tracking-wide uppercase">
              {sourceLabel(internship.source)}
            </span>
          </div>
        )}

        <div className="flex items-center justify-between text-[11px] text-muted-foreground mt-auto pt-1 font-medium">
          <span className="flex items-center gap-1.5 max-w-[140px]">
            <MapPin className="w-3.5 h-3.5 text-orange-400/70" />
            <span className="truncate">{internship.location || "Worldwide"}</span>
          </span>
          <span className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-orange-400/70" />
            {timeAgo(internship.posted_at || internship.scraped_at)}
          </span>
        </div>
      </Link>

      <div className="mt-4 pt-4 border-t border-white/5">
        <a
          href={internship.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-1.5 w-full py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-orange-500/10 via-amber-500/10 to-transparent hover:from-orange-600 hover:to-orange-500 text-orange-300 hover:text-white border border-orange-500/20 hover:border-transparent transition-all duration-300 shadow-sm"
        >
          <span>Apply Now</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </motion.div>
  );
}
