"use client";

import Link from "next/link";
import { ExternalLink, MapPin, Bookmark, BookmarkCheck, Calendar } from "lucide-react";
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
    <motion.div whileHover={{ y: -2 }} className="bg-card border border-border/50 rounded-xl p-4 hover:border-indigo-500/30 transition-all hover:shadow-lg hover:shadow-indigo-500/5 flex flex-col h-full">
      <div className="flex items-start justify-between mb-3 gap-2">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/20 flex items-center justify-center text-sm font-bold text-indigo-400 shrink-0">
          {internship.company[0]?.toUpperCase()}
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {internship.remote && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/20">Remote</span>
          )}
          {session && (
            <button
              onClick={(e) => { e.preventDefault(); bookmarkMutation.mutate(); }}
              className={cn("p-1 rounded-md transition-colors", saved ? "text-indigo-400 hover:text-indigo-300" : "text-muted-foreground hover:text-foreground hover:bg-accent")}
            >
              {saved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
            </button>
          )}
        </div>
      </div>

      <Link href={`/internships/${id}`} className="flex-1 group">
        <div className="font-semibold text-sm mb-1 group-hover:text-indigo-400 transition-colors line-clamp-2">{internship.title}</div>
        <div className="text-muted-foreground text-xs mb-3">{internship.company}</div>

        {!compact && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {internship.category && (
              <span className={cn("text-xs px-2 py-0.5 rounded-full border", categoryColor(internship.category))}>
                {internship.category}
              </span>
            )}
            <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-muted-foreground border border-white/5">
              {sourceLabel(internship.source)}
            </span>
          </div>
        )}

        <div className="flex items-center justify-between text-xs text-muted-foreground mt-auto">
          <span className="flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            <span className="truncate max-w-[120px]">{internship.location}</span>
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {timeAgo(internship.posted_at || internship.scraped_at)}
          </span>
        </div>
      </Link>

      <div className="mt-3 pt-3 border-t border-border/50">
        <a
          href={internship.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-1.5 w-full py-1.5 rounded-lg text-xs font-medium bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/20 transition-colors"
        >
          Apply Now <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </motion.div>
  );
}
