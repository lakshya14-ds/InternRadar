"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, MapPin, ExternalLink, Bookmark, BookmarkCheck, Calendar, Building2, Tag, Globe } from "lucide-react";
import { motion } from "framer-motion";
import { useSession } from "next-auth/react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { internshipsApi, usersApi } from "@/lib/api";
import { cn, timeAgo, sourceLabel, categoryColor, getInternshipId } from "@/lib/utils";
import { useAppStore } from "@/store/useStore";
import { InternshipCard } from "@/components/internships/InternshipCard";

export default function InternshipDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data: session } = useSession();
  const { isBookmarked, toggleBookmark } = useAppStore();
  const queryClient = useQueryClient();

  const { data: internship, isLoading } = useQuery({
    queryKey: ["internship", id],
    queryFn: () => internshipsApi.getById(id),
    enabled: !!id,
  });

  const { data: related } = useQuery({
    queryKey: ["internships", "search", { category: internship?.category }],
    queryFn: () => internshipsApi.search({ category: internship?.category || "", limit: 6 }),
    enabled: !!internship?.category,
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

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-8 bg-muted rounded-xl w-1/3" />
        <div className="h-48 bg-card border border-border/50 rounded-xl" />
        <div className="h-64 bg-card border border-border/50 rounded-xl" />
      </div>
    );
  }

  if (!internship) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Internship not found</p>
        <button onClick={() => router.back()} className="mt-4 text-indigo-400 hover:text-indigo-300 text-sm">Go back</button>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl space-y-6">
      <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Internships
      </button>

      {/* Main Card */}
      <div className="bg-card border border-border/50 rounded-2xl p-6">
        <div className="flex items-start justify-between gap-4 mb-6">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/20 flex items-center justify-center text-xl font-bold text-indigo-400 shrink-0">
              {internship.company[0]?.toUpperCase()}
            </div>
            <div>
              <h1 className="text-xl font-bold mb-1">{internship.title}</h1>
              <p className="text-muted-foreground font-medium">{internship.company}</p>
            </div>
          </div>
          <button
            onClick={() => bookmarkMutation.mutate()}
            className={cn("p-2 rounded-lg border transition-all shrink-0", saved ? "bg-indigo-600/10 border-indigo-500/20 text-indigo-400" : "border-border/50 text-muted-foreground hover:text-foreground hover:bg-accent")}
          >
            {saved ? <BookmarkCheck className="w-5 h-5" /> : <Bookmark className="w-5 h-5" />}
          </button>
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { icon: MapPin, label: "Location", value: internship.location },
            { icon: Globe, label: "Remote", value: internship.remote ? "Yes" : "No" },
            { icon: Tag, label: "Category", value: internship.category || "Other" },
            { icon: Calendar, label: "Posted", value: timeAgo(internship.posted_at || internship.scraped_at) },
          ].map((meta) => (
            <div key={meta.label} className="flex items-start gap-2">
              <meta.icon className="w-4 h-4 text-muted-foreground mt-0.5 shrink-0" />
              <div>
                <p className="text-xs text-muted-foreground">{meta.label}</p>
                <p className="text-sm font-medium truncate">{meta.value}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          {internship.category && (
            <span className={cn("text-xs px-3 py-1 rounded-full border", categoryColor(internship.category))}>
              {internship.category}
            </span>
          )}
          <span className="text-xs px-3 py-1 rounded-full bg-white/5 border border-white/10 text-muted-foreground">
            via {sourceLabel(internship.source)}
          </span>
          {internship.skills.slice(0, 5).map((s) => (
            <span key={s} className="text-xs px-3 py-1 rounded-full bg-white/5 border border-white/10 text-muted-foreground">{s}</span>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <a href={internship.url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold transition-colors">
            Apply Now <ExternalLink className="w-4 h-4" />
          </a>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Building2 className="w-3.5 h-3.5" />
            <span>{internship.employment_type}</span>
          </div>
        </div>
      </div>

      {/* Description */}
      {internship.description && (
        <div className="bg-card border border-border/50 rounded-2xl p-6">
          <h2 className="font-semibold mb-4">About this Internship</h2>
          <div className="prose prose-sm prose-invert max-w-none">
            <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap text-sm">{internship.description}</p>
          </div>
        </div>
      )}

      {/* Related */}
      {related && related.filter((r) => getInternshipId(r) !== id).length > 0 && (
        <div>
          <h2 className="font-semibold mb-4">Related Internships</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {related.filter((r) => getInternshipId(r) !== id).slice(0, 3).map((r) => (
              <InternshipCard key={getInternshipId(r)} internship={r} compact />
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
